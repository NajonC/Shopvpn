"""T050ex/ey: actual open selection and its real housekeeping/poll consumer."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, ALIASES
from tests.integration.test_composite_extra_admin_view_cancel_guards import catalog, dump
from tests.integration.test_composite_extra_user_guards import egp

NAMES=['stock_order','stock_product']+ALIASES


def prepare(c,mp,name,kind,representation):
    if name.startswith('stock_') and name in NAMES[:2]:
        from tests.integration.test_composite_extra_admin_view_cancel_guards import prepare as stock
        stock(c,mp,representation,kind,name.split('_')[1])
    else:alias(c,mp,name,kind,representation)
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET gateway='zarinpal',status='pending',created_at='2999-01-01',updated_at='2999-01-01' WHERE id IN (?,?)",(c.iid,c.decoy))
        # A later eligible row pins selection after filtering, rather than filtering LIMIT output.
    c.later=c.db.create_extra_invoice('zarinpal','wallet_topup',c.oid,61001,123,124)
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET created_at='2999-01-01' WHERE id=?",(c.later,))


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('limit',[1,2,-1])
def test_open_composite_admission(catalog,monkeypatch,caplog,name,representation,limit):
    c=catalog;prepare(c,monkeypatch,name,'composite',representation)
    state=dump(c.db)
    expected=[c.decoy,c.later]
    if limit>=0:expected=expected[:limit]
    for _ in range(2):
        found=c.db.list_open_extra_invoices(limit)
        assert [r['id'] for r in found]==expected,'missing T052 open composite isolation before limit'
        assert all(dict(r)==dict(c.db.get_extra_invoice(r['id'])) for r in found)
        assert dump(c.db)==state and not c.remote and not c.trace and not c.invoice_trace
    # A mixed batch must explicitly identify refusal without leaking invoice metadata.
    assert 'composite' in caplog.text.lower(),'missing T052 open composite refusal reason'
    assert 'synthetic-remote' not in caplog.text


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('domain',['order','wallet_topup','reseller_request'])
def test_open_legacy_and_reference_domains(catalog,monkeypatch,name,kind,domain):
    c=catalog;prepare(c,monkeypatch,name,kind if domain=='order' else 'composite','sqlite')
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET kind=? WHERE id=?',(domain,c.iid))
    state=dump(c.db)
    assert [r['id'] for r in c.db.list_open_extra_invoices(-1)]==[c.decoy,c.iid,c.later]
    assert dump(c.db)==state and not c.remote and not c.trace and not c.invoice_trace


def poll(c,mp,fault):
    trace=[];sent=[];tick=[0];times=[100,105,112]
    async def process(db,bot,row):
        trace.append((times[tick[0]],row['id']))
        if fault=='process' and row['id']==c.decoy and tick[0]==0:raise RuntimeError('synthetic process fault')
        return 'verified_now',str(row['id'])
    async def send(uid,text):
        sent.append((uid,text))
        if fault=='send':raise RuntimeError('synthetic send fault')
    async def sleep(n):
        assert n==17;tick[0]+=1
        if tick[0]==len(times):raise asyncio.CancelledError
    mp.setattr(egp,'process_invoice',process);mp.setattr(c.bot,'send_message',send)
    mp.setattr(egp.asyncio,'get_running_loop',lambda:SimpleNamespace(time=lambda:times[tick[0]]))
    mp.setattr(egp.asyncio,'sleep',sleep)
    with pytest.raises(asyncio.CancelledError):asyncio.run(egp.poll_loop(c.bot,c.db,17))
    return trace,sent


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('kind',['composite',None,'legacy'])
@pytest.mark.parametrize('fault',['none','send','process'])
def test_actual_open_housekeeping_poll(catalog,monkeypatch,name,kind,fault):
    c=catalog;prepare(c,monkeypatch,name,kind,'sqlite');state=dump(c.db)
    trace,sent=poll(c,monkeypatch,fault)
    ids=[c.decoy,c.later] if kind=='composite' else [c.decoy,c.iid,c.later]
    expected=[(t,i) for t in [100,112] for i in ids]
    if fault=='process':
        expected=[(100,c.decoy)]+[(105,i) for i in ids[1:]]+[(112,c.decoy)]
    assert trace==expected,'missing T052 real open poll composite isolation/continuation'
    rows={i:dict(c.db.get_extra_invoice(i)) for i in ids}
    assert sent==[(rows[i]['user_id'],str(i)) for t,i in expected if not(fault=='process' and t==100)]
    assert dump(c.db)==state and not c.remote and not c.trace and not c.invoice_trace
