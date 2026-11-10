"""T050dj/dk: independent cache cardinality and real SQL open-selection controls."""
import pytest
from tests.integration.test_composite_extra_poll_guards import catalog, setup, run_poll, dump


@pytest.mark.parametrize('size',[1999,2000,2001])
@pytest.mark.parametrize('outcome',['paid','pending','send_failure','process_failure'])
def test_poll_cache_cardinality(catalog,monkeypatch,size,outcome):
    c=catalog;setup(c,monkeypatch,'sqlite',None)
    base=dict(c.db.get_extra_invoice(c.iid));before=dump(c.db)
    # Unique ID domain, never coincident with a real order. No fulfillment is claimed.
    batch=[dict(base,id=10000+i,user_id=40000+i) for i in range(size)]
    results={r['id']:('verified_now','ok') if outcome in {'paid','send_failure'} else ('not_paid_yet','') for r in batch}
    if outcome=='process_failure':results[batch[-1]['id']]=RuntimeError('last processor fails')
    trace,messages=run_poll(c,monkeypatch,[batch,batch],[100,101],results,outcome=='send_failure')
    # Cache clearing occurs only after a fully completed iteration, strictly above 2000.
    repetitions=2 if size>2000 and outcome!='process_failure' else 1
    assert [x[1] for x in trace if x[0]=='process']==[r['id'] for r in batch]*repetitions
    expected=[(r['user_id'],'ok') for r in batch]*repetitions if outcome in {'paid','send_failure'} else []
    assert messages==expected
    assert [x for x in trace if x[0]=='sleep']==[('sleep',17)]*2
    assert dump(c.db)==before and not c.remote and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('limit',[None,0,1,2,99,100,101,200,201,999,-1,'3'])
def test_list_open_real_sql(catalog,monkeypatch,limit):
    c=catalog;setup(c,monkeypatch,'sqlite',None)
    before=dump(c.db)
    gateways=['zarinpal','idpay','zibal','nextpay','payping','nowpayments','tgstars','synthetic-unknown',None]
    statuses=['new','pending','completed','expired','cancelled','unknown',None]
    kinds=['order','wallet_topup','reseller_request']
    inserted=[]
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM extra_gateway_invoices')
        # Explicit reverse insertion IDs pin ascending ID rather than insertion or descending order.
        for i in range(440,0,-1):
            gateway=gateways[i%len(gateways)];status=statuses[(i//len(gateways))%len(statuses)];kind=kinds[i%3]
            # Gateway is NOT NULL in the schema. NULL status is legal.
            if gateway is None:gateway='tgstars'
            conn.execute('INSERT INTO extra_gateway_invoices (id,gateway,kind,ref_id,user_id,amount_toman,payable_amount,status) VALUES (?,?,?,?,?,?,?,?)',(10000+i,gateway,kind,70000+i,80000+i,900,901,status))
            inserted.append((10000+i,gateway,status,kind))
    frozen=dump(c.db)
    expected=sorted(x[0] for x in inserted if x[1]!='tgstars' and x[2] in {'new','pending'})
    value=100 if limit is None else int(limit)
    if value>=0:expected=expected[:value]
    rows=c.db.list_open_extra_invoices() if limit is None else c.db.list_open_extra_invoices(limit)
    assert [r['id'] for r in rows]==expected
    assert all(r['amount_toman']==900 and r['payable_amount']==901 and r['ref_id']==r['id']+60000 and r['user_id']==r['id']+70000 for r in rows)
    assert dump(c.db)==frozen and not c.trace and not c.remote and not c.invoice_trace
    assert [x for x in frozen if not x.startswith('INSERT INTO "extra_gateway_invoices"') and not x.startswith("INSERT INTO \"sqlite_sequence\" VALUES('extra_gateway_invoices'")]==[x for x in before if not x.startswith('INSERT INTO "extra_gateway_invoices"') and not x.startswith("INSERT INTO \"sqlite_sequence\" VALUES('extra_gateway_invoices'")]


@pytest.mark.parametrize('limit',[None,'bad'])
def test_list_open_invalid_limit_propagates(catalog,monkeypatch,limit):
    c=catalog;setup(c,monkeypatch,'sqlite',None);before=dump(c.db)
    with pytest.raises((TypeError,ValueError)):c.db.list_open_extra_invoices(limit)
    assert dump(c.db)==before
