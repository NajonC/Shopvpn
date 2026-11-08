"""T050cv/cw: caller-local guard isolation plus real legacy stock settlement."""
import asyncio
import pytest
from tests.integration.test_composite_extra_user_guards import catalog, setup, egp, USER_ID, SUCCESS, REFERRER, LINKS, rows, dump
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS, invoices
from tests.integration.test_composite_legacy_guards import as_row


@pytest.mark.parametrize('entry',['process','deliver'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('boundary',['pending','approved','rejected'])
def test_composite_caller_local_admission(catalog,monkeypatch,entry,key,representation,marker,boundary):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker)
    with c.db._get_conn() as conn:
        conn.execute('UPDATE orders SET status=? WHERE id=?',(boundary,c.oid))
        conn.execute('UPDATE extra_gateway_invoices SET gateway=? WHERE id=?',(key,c.iid))
    row=as_row(dict(c.db.get_extra_invoice(c.iid)),representation);calls=[]
    # Deliberately permissive downstream seams: shared-helper protection cannot
    # masquerade as caller-local admission. Neither function under test is mocked.
    async def check(*args):calls.append(('check',args));return 'verified_now'
    async def delivered(*args,**kw):calls.append(('deliver',args,kw));return 'synthetic delivered'
    async def finalize(*args,**kw):calls.append(('finalize',args,kw));return 'synthetic delivered'
    if entry=='process':
        monkeypatch.setattr(egp,'check_invoice',check);monkeypatch.setattr(egp,'deliver',delivered)
    else:monkeypatch.setattr(egp.abangateway_payment,'finalize_paid_order',finalize)
    before=dump(c.db)
    def invoke():
        return asyncio.run(egp.process_invoice(c.db,c.bot,row)) if entry=='process' else asyncio.run(egp.deliver(c.db,c.bot,row))
    result=invoke();text=result[0] if entry=='process' else result
    assert 'composite' in text.lower(), 'missing T052 caller-local composite refusal'
    if entry=='process':assert result[1]=='' and text.startswith('error:')
    assert invoke()==result and not calls and not c.remote and not c.invoice_trace and not c.trace and dump(c.db)==before


def assert_fulfillment(c,before,scenario):
    if scenario in {'paid','delivery'}:
        assert c.db.get_order(c.oid)['status']=='approved'
        assert c.trace[:3]==[('claim_order',(c.oid,),{}),('take_unused_configs',(c.pid,USER_ID,2),{}),('approve_order',(c.oid,[r['id'] for r in before[:2]]),{})]
        assert ('delivery',USER_ID,'Stock',LINKS[:2],dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
        assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:2]) and rows(c)[2:]==before[2:]
        assert c.db.get_wallet_credit(REFERRER)==(130 if scenario=='paid' else 0)
        assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(scenario=='paid')
    elif scenario=='shortage':
        assert c.db.get_order(c.oid)['status']=='pending' and rows(c)==before
        assert c.trace[0]==('claim_order',(c.oid,),{}) and ('release_order_claim',(c.oid,),{}) in c.trace
    else:assert rows(c)==before
    assert c.db.get_wallet_credit(USER_ID)==0


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','prior','shortage','delivery','pending','failed','remote_error','completed','cancelled','expired','claim_lost'])
def test_direct_process_legacy_chain(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    row=as_row(dict(c.db.get_extra_invoice(c.iid)),representation);before=rows(c);decoy=dict(c.db.get_extra_invoice(c.decoy))
    result,text=asyncio.run(egp.process_invoice(c.db,c.bot,row,c.notify))
    expected='verified_now' if scenario in {'paid','prior','shortage'} else 'error:خطای غیرمنتظره در تحویل؛ دوباره بررسی می‌شود.' if scenario=='delivery' else 'not_paid_yet' if scenario=='pending' else 'error:synthetic outage' if scenario=='remote_error' else 'already_delivered' if scenario in {'completed','claim_lost'} else 'expired'
    assert result==expected
    assert text==(SUCCESS if scenario=='paid' else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else '')
    assert c.remote==([] if scenario in {'completed','cancelled','expired'} else [('zarinpal','synthetic-remote','synthetic-number',900)])
    status='completed' if scenario in {'paid','prior','shortage','completed','claim_lost'} else 'pending' if scenario=='delivery' else 'expired' if scenario=='failed' else scenario if scenario in {'expired','cancelled'} else 'new'
    assert c.db.get_extra_invoice(c.iid)['status']==status and dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert c.invoice_trace==([] if scenario in {'completed','cancelled','expired','pending','remote_error'} else [('update_extra_invoice_status',(c.iid,'expired'))] if scenario=='failed' else [('claim_extra_invoice',(c.iid,)),('release_extra_invoice',(c.iid,))] if scenario=='delivery' else [('claim_extra_invoice',(c.iid,))])
    assert_fulfillment(c,before,scenario)
    if scenario=='paid':assert ('admin',c.oid) in c.trace
    if status=='completed':
        saved=dump(c.db);c.trace.clear();c.invoice_trace.clear();count=len(c.remote)
        fresh=as_row(dict(c.db.get_extra_invoice(c.iid)),representation)
        assert asyncio.run(egp.process_invoice(c.db,c.bot,fresh,c.notify))==('already_delivered','')
        assert dump(c.db)==saved and not c.trace and not c.invoice_trace and len(c.remote)==count


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','prior','shortage','delivery','rejected','missing'])
@pytest.mark.parametrize('notifier',['explicit','registered'])
def test_direct_deliver_legacy_chain(catalog,monkeypatch,representation,kind,scenario,notifier):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    if scenario=='rejected':
        with c.db._get_conn() as conn:conn.execute("UPDATE orders SET status='rejected' WHERE id=?",(c.oid,))
    row=dict(c.db.get_extra_invoice(c.iid))
    if scenario=='missing':row['ref_id']=99999
    row=as_row(row,representation);before=rows(c);invoice_rows=invoices(c)
    egp.register_order_notifier(c.db,c.notify)
    try:
        if scenario=='delivery':
            with pytest.raises(RuntimeError,match='synthetic failure'):asyncio.run(egp.deliver(c.db,c.bot,row,c.notify if notifier=='explicit' else None))
        else:
            text=asyncio.run(egp.deliver(c.db,c.bot,row,c.notify if notifier=='explicit' else None))
            assert text==(SUCCESS if scenario=='paid' else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else '⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if scenario=='missing' else '⚠️ پرداخت شما دریافت شد ولی این سفارش دیگر فعال نیست. با پشتیبانی تماس بگیرید.')
        assert_fulfillment(c,before,scenario)
        assert invoices(c)==invoice_rows and not c.invoice_trace and not c.remote
        if scenario=='paid':assert ('admin',c.oid) in c.trace
        if scenario in {'paid','prior'}:
            saved=dump(c.db);c.trace.clear()
            assert asyncio.run(egp.deliver(c.db,c.bot,row,c.notify if notifier=='explicit' else None))=='✅ این سفارش قبلاً بررسی و تحویل داده شده است.'
            assert dump(c.db)==saved and not c.trace
    finally:egp._order_notifiers.pop(id(c.db),None)
