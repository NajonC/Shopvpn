"""T050dl/dm: direct alias isolation and poll refusal notification failures."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES, STATUSES
from tests.integration.test_composite_extra_admin_view_cancel_guards import catalog, dump, USER_ID
from tests.integration.test_composite_extra_user_guards import egp

METHODS=['expire_stale_extra_invoices','purge_old_extra_invoices']


def old(c,status,kind='order'):
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET status=?,kind=?,created_at='2000-01-01',updated_at='2000-01-01' WHERE id=?",(status,kind,c.iid))
        conn.execute("UPDATE extra_gateway_invoices SET status=?,created_at='2000-01-01',updated_at='2000-01-01' WHERE id=?",(status,c.decoy))


def run_housekeeping(c,method):
    return getattr(c.db,method)(*([7] if method=='purge_old_extra_invoices' else []))


def changed(row,method,status,before):
    if method=='expire_stale_extra_invoices' and status in {'new','pending'}:
        assert row is not None and row['status']=='expired' and row['updated_at']!='2000-01-01'
    elif method=='purge_old_extra_invoices' and status in {'completed','expired','cancelled'}:assert row is None
    else:assert dict(row)==before


@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('status',STATUSES)
def test_housekeeping_composite_alias(catalog,monkeypatch,method,representation,name,status):
    c=catalog;alias(c,monkeypatch,name,'composite',representation);old(c,status)
    before=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy));state=dump(c.db)
    for _ in range(2):
        run_housekeeping(c,method)
        assert dict(c.db.get_extra_invoice(c.iid) or {})==before,'missing T052 direct housekeeping alias isolation'
    changed(c.db.get_extra_invoice(c.decoy),method,status,decoy)
    assert [x for x in dump(c.db) if not x.startswith('INSERT INTO "extra_gateway_invoices"')]==[x for x in state if not x.startswith('INSERT INTO "extra_gateway_invoices"')]
    assert not c.remote and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('name',ALIASES)
@pytest.mark.parametrize('status',STATUSES)
def test_housekeeping_legacy_alias(catalog,monkeypatch,method,kind,name,status):
    c=catalog;alias(c,monkeypatch,name,kind,'sqlite');old(c,status)
    before=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy));state=dump(c.db)
    run_housekeeping(c,method)
    changed(c.db.get_extra_invoice(c.iid),method,status,before);changed(c.db.get_extra_invoice(c.decoy),method,status,decoy)
    assert [x for x in dump(c.db) if not x.startswith('INSERT INTO "extra_gateway_invoices"')]==[x for x in state if not x.startswith('INSERT INTO "extra_gateway_invoices"')]


@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('kind',['wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',STATUSES)
def test_housekeeping_other_kind_alias_collision(catalog,monkeypatch,method,kind,status):
    c=catalog;alias(c,monkeypatch,'global_renewal_target','composite','sqlite');old(c,status,kind)
    before=dict(c.db.get_extra_invoice(c.iid));run_housekeeping(c,method)
    changed(c.db.get_extra_invoice(c.iid),method,status,before)


def poll(c,mp,send_failure=False,failure=None):
    selected=dict(c.db.get_extra_invoice(c.iid));other=dict(c.db.get_extra_invoice(c.decoy),user_id=USER_ID+77)
    index=[0];trace=[];messages=[];times=[100,105,112,113]
    def listing(limit):
        trace.append(('list',limit))
        if failure=='list' and index[0]==0:raise RuntimeError('list outage')
        return [selected,other]
    async def process(db,bot,row):
        trace.append(('process',row['id']));trace.append(('process_at',(times[index[0]],row['id'])))
        if failure=='process' and row['id']==c.iid and index[0]==0:raise RuntimeError('process outage')
        return 'verified_now','legacy-delivered'
    async def send(uid,text):
        messages.append((uid,text));trace.append(('send_at',(times[index[0]],uid,text)))
        if send_failure and 'composite' in text.lower():raise RuntimeError('refusal notification blocked')
    async def sleep(interval):
        trace.append(('sleep',interval));index[0]+=1
        if index[0]==len(times):raise asyncio.CancelledError
    mp.setattr(c.db,'list_open_extra_invoices',listing);mp.setattr(egp,'process_invoice',process);mp.setattr(c.bot,'send_message',send)
    mp.setattr(egp.asyncio,'get_running_loop',lambda:SimpleNamespace(time=lambda:times[index[0]]));mp.setattr(egp.asyncio,'sleep',sleep)
    for method in METHODS:
        fn=getattr(c.db,method)
        def wrap(*args,_method=method,_fn=fn):
            trace.append((_method,args))
            if failure==_method and index[0]==0:raise RuntimeError('housekeeping outage')
            return _fn(*args)
        mp.setattr(c.db,method,wrap)
    with pytest.raises(asyncio.CancelledError):asyncio.run(egp.poll_loop(c.bot,c.db,17))
    return trace,messages


@pytest.mark.parametrize('send_failure',[False,True])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
def test_poll_composite_alias_notification_continuation(catalog,monkeypatch,send_failure,representation,name):
    c=catalog;alias(c,monkeypatch,name,'composite',representation);before=dump(c.db)
    trace,messages=poll(c,monkeypatch,send_failure)
    assert [x for x in trace if x[0]=='process']==[('process',c.decoy)]*2,'missing T052 poll alias refusal/continuation'
    assert [x[1] for x in trace if x[0]=='process_at']==[(100,c.decoy),(112,c.decoy)]
    assert [x[1][0] for x in trace if x[0]=='send_at']==[100,100,112,112]
    assert len(messages)==4 and all(uid==USER_ID and 'composite' in text.lower() for uid,text in messages[::2])
    assert messages[1::2]==[(USER_ID+77,'legacy-delivered')]*2
    assert [x for x in trace if x[0]=='sleep']==[('sleep',17)]*4
    assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('send_failure',[False,True])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('name',ALIASES)
def test_poll_legacy_alias_continuation(catalog,monkeypatch,send_failure,kind,name):
    c=catalog;alias(c,monkeypatch,name,kind,'sqlite');before=dump(c.db)
    trace,messages=poll(c,monkeypatch,send_failure)
    assert [x for x in trace if x[0]=='process']==[('process',c.iid),('process',c.decoy)]*2
    assert [x[1] for x in trace if x[0]=='process_at']==[(t,i) for t in [100,112] for i in [c.iid,c.decoy]]
    assert messages==[(USER_ID,'legacy-delivered'),(USER_ID+77,'legacy-delivered')]*2
    assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('failure',METHODS+['list','process'])
def test_poll_outer_failure_continuation(catalog,monkeypatch,failure):
    c=catalog;alias(c,monkeypatch,'global_renewal_target',None,'sqlite');before=dump(c.db)
    trace,messages=poll(c,monkeypatch,failure=failure)
    ids=[x[1] for x in trace if x[0]=='process']
    assert ids==([c.iid,c.decoy,c.iid] if failure=='process' else [c.iid,c.decoy])
    assert messages==([(USER_ID+77,'legacy-delivered'),(USER_ID,'legacy-delivered')] if failure=='process' else [(USER_ID,'legacy-delivered'),(USER_ID+77,'legacy-delivered')])
    assert [x for x in trace if x[0]=='sleep']==[('sleep',17)]*4
    assert dump(c.db)==before
