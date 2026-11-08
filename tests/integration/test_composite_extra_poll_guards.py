"""T050cx/cy: independent poll admission and real SQL housekeeping isolation."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_extra_user_guards import catalog, setup, egp, USER_ID, dump
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests.integration.test_composite_legacy_guards import as_row


@pytest.fixture(autouse=True)
def discriminator_columns(catalog):
    # Additive future discriminator schema, synthetic database only.
    with catalog.db._get_conn() as conn:
        conn.execute("ALTER TABLE orders ADD COLUMN service_kind TEXT")
        conn.execute("ALTER TABLE products ADD COLUMN service_kind TEXT")


def run_poll(c,mp,batches,times,results=None,fail_send=False):
    trace=[];messages=[];index=[0]
    async def process(db,bot,invoice):
        trace.append(('process',invoice['id']))
        value=(results or {}).get(invoice['id'],('verified_now','delivered'))
        if isinstance(value,Exception):raise value
        return value
    async def send(uid,text):
        messages.append((uid,text))
        if fail_send:raise RuntimeError('blocked Telegram')
    def listing(limit):trace.append(('list',limit));return batches[index[0]]
    async def sleep(interval):
        trace.append(('sleep',interval));index[0]+=1
        if index[0]>=len(batches):raise asyncio.CancelledError
    clock=SimpleNamespace(time=lambda:times[index[0]])
    mp.setattr(c.db,'list_open_extra_invoices',listing)
    mp.setattr(egp,'process_invoice',process)
    mp.setattr(c.bot,'send_message',send)
    mp.setattr(egp.asyncio,'get_running_loop',lambda:clock)
    mp.setattr(egp.asyncio,'sleep',sleep)
    for method in ['expire_stale_extra_invoices','purge_old_extra_invoices']:
        original=getattr(c.db,method)
        def wrapped(*args,_method=method,_fn=original):trace.append((_method,args));return _fn(*args)
        mp.setattr(c.db,method,wrapped)
    with pytest.raises(asyncio.CancelledError):asyncio.run(egp.poll_loop(c.bot,c.db,17))
    return trace,messages


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
def test_poll_caller_admission(catalog,monkeypatch,key,representation,marker):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker)
    row=dict(c.db.get_extra_invoice(c.iid));row['gateway']=key;row=as_row(row,representation)
    before=dump(c.db)
    trace,messages=run_poll(c,monkeypatch,[[row],[row]],[100,105])
    assert not [x for x in trace if x[0]=='process'], 'missing T052 poll caller-local composite refusal'
    assert len(messages)==1 and messages[0][0]==USER_ID and 'composite' in messages[0][1].lower()
    assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','empty','pending','error','send_failure','process_failure'])
def test_poll_legacy_cadence_and_continuation(catalog,monkeypatch,kind,scenario):
    c=catalog;setup(c,monkeypatch,'sqlite',kind)
    row=dict(c.db.get_extra_invoice(c.iid));other=dict(row,id=c.decoy,user_id=USER_ID+1)
    result=('verified_now','delivered') if scenario in {'paid','send_failure'} else ('verified_now','') if scenario=='empty' else ('not_paid_yet','ignored') if scenario=='pending' else ('error:outage','')
    results={c.iid:RuntimeError('processor failure') if scenario=='process_failure' else result,c.decoy:('verified_now','second')}
    before=dump(c.db)
    trace,messages=run_poll(c,monkeypatch,[[row,other]]*9,[100,105,112,113,124,125,136,137,148],results,scenario=='send_failure')
    assert [x for x in trace if x[0]=='list']==[('list',100)]*9
    assert [x for x in trace if x[0]=='sleep']==[('sleep',17)]*9
    assert [x for x in trace if x[0]=='expire_stale_extra_invoices']==[('expire_stale_extra_invoices',())]*2
    assert [x for x in trace if x[0]=='purge_old_extra_invoices']==[('purge_old_extra_invoices',(7,))]*2
    assert [x for x in trace if x[0]=='process']==([('process',x) for x in [c.iid,c.decoy,c.iid,c.iid,c.decoy,c.iid,c.decoy,c.iid]] if scenario=='process_failure' else [('process',c.iid),('process',c.decoy)]*5)
    expected=[(USER_ID+1,'second')]*3 if scenario=='process_failure' else sum((([(USER_ID,'delivered')] if scenario in {'paid','send_failure'} else [])+[(USER_ID+1,'second')] for _ in range(5)),[])
    assert messages==expected and dump(c.db)==before


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status',['new','pending','completed','expired','cancelled'])
def test_housekeeping_preserves_composite_references(catalog,monkeypatch,key,marker,status):
    c=catalog;setup(c,monkeypatch,'sqlite','composite',marker)
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET gateway=?,status=?,created_at='2000-01-01 00:00:00',updated_at='2000-01-01T00:00:00' WHERE id=?",(key,status,c.iid))
        conn.execute("UPDATE extra_gateway_invoices SET status=?,created_at='2000-01-01 00:00:00',updated_at='2000-01-01T00:00:00' WHERE id=?",(status,c.decoy))
    with c.db._get_conn() as conn:
        conn.execute('UPDATE '+('orders' if marker=='order' else 'products')+" SET service_kind='composite' WHERE id=?",(c.oid if marker=='order' else c.pid,))
    before=dict(c.db.get_extra_invoice(c.iid))
    c.db.expire_stale_extra_invoices();c.db.purge_old_extra_invoices(7)
    assert dict(c.db.get_extra_invoice(c.iid) or {})==before, 'missing T052 housekeeping composite isolation'
    legacy=c.db.get_extra_invoice(c.decoy)
    assert (legacy is not None and legacy['status']=='expired') if status in {'new','pending'} else legacy is None


@pytest.mark.parametrize('kind',['wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',['new','completed'])
def test_housekeeping_other_reference_domains(catalog,monkeypatch,kind,status):
    c=catalog;setup(c,monkeypatch,'sqlite','composite')
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET kind=?,status=?,created_at='2000-01-01 00:00:00',updated_at='2000-01-01T00:00:00' WHERE id=?",(kind,status,c.iid))
    with c.db._get_conn() as conn:conn.execute("UPDATE orders SET service_kind='composite' WHERE id=?",(c.oid,))
    c.db.expire_stale_extra_invoices();c.db.purge_old_extra_invoices(7)
    row=c.db.get_extra_invoice(c.iid)
    assert (row is not None and row['status']=='expired') if status=='new' else row is None


@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('status',['new','pending','completed','expired','cancelled'])
def test_housekeeping_selected_legacy_order(catalog,monkeypatch,kind,key,status):
    c=catalog;setup(c,monkeypatch,'sqlite',kind)
    with c.db._get_conn() as conn:
        for table,ident in [('orders',c.oid),('products',c.pid)]:
            conn.execute('UPDATE '+table+' SET service_kind=? WHERE id=?',(kind,ident))
        conn.execute("UPDATE extra_gateway_invoices SET gateway=?,status=?,created_at='2000-01-01 00:00:00',updated_at='2000-01-01T00:00:00' WHERE id=?",(key,status,c.iid))
    c.db.expire_stale_extra_invoices();c.db.purge_old_extra_invoices(7)
    row=c.db.get_extra_invoice(c.iid)
    assert (row is not None and row['status']=='expired') if status in {'new','pending'} else row is None
