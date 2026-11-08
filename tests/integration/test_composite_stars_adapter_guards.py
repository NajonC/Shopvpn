"""T050cj/ck: Stars user adapters admission and real inline metadata/claim/stock effects."""
import asyncio
import json
from types import SimpleNamespace
from aiogram import Router
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import extra_gateway_user as user
from tests._harness.legacy_bot import FakeUser,FakeMessage,TelegramLog,find_handler
import pytest
from tests.integration.test_composite_extra_admin_guards import egp
from tests.integration.test_composite_gateway_stock_guards import catalog, setup as stock_setup, rows, dump, LINKS, USER_ID, REFERRER, SUCCESS
REPEAT='✅ این پرداخت قبلاً ثبت و تحویل داده شده است.'
SCENARIOS=['paid','prior','shortage','delivery','completed','expired','cancelled','claim_lost','foreign','amount','currency','missing','gateway']


def setup(c,mp,representation,kind=None,marker='order',scenario='paid'):
    stock_setup(c,mp,'abangateway_payment',representation,kind,marker,scenario if scenario in {'prior','shortage','delivery'} else 'success')
    c.decoy=c.db.create_extra_invoice('tgstars','order',99999,USER_ID,111,11,meta={'retained':'decoy'})
    c.iid=c.db.create_extra_invoice('zarinpal' if scenario=='gateway' else 'tgstars','order',c.oid,USER_ID,900,37,meta={'retained':'selected'})
    if scenario in {'completed','expired','cancelled'}:c.db.update_extra_invoice_status(c.iid,scenario)
    c.invoice_trace=[];c.raced=False
    for method in ['merge_extra_invoice_meta','claim_extra_invoice','release_extra_invoice']:
        original=getattr(c.db,method)
        def call(*args,_fn=original,_name=method,**kw):
            c.invoice_trace.append((_name,args))
            if scenario=='claim_lost' and _name=='claim_extra_invoice' and not c.raced:
                assert _fn(*args,**kw);c.raced=True
            return _fn(*args,**kw)
        mp.setattr(c.db,method,call)
    c.args=(99999 if scenario=='missing' else c.iid,USER_ID+1 if scenario=='foreign' else USER_ID,38 if scenario=='amount' else 37,'USD' if scenario=='currency' else 'XTR','synthetic-charge')


def invoke(c):
    async def run():
        router=Router();user.register_early(router,c.db,True)
        log=TelegramLog();message=FakeMessage(log,c.args[1],from_user=FakeUser(c.args[1]))
        message.successful_payment=SimpleNamespace(invoice_payload=f'xg:{c.args[0]}',total_amount=c.args[2],currency=c.args[3],telegram_payment_charge_id=c.args[4])
        await find_handler(router,'message','stars_successful_payment')(message,c.bot)
        assert len(log.events)==1
        return log.events[0].text
    return asyncio.run(run())



@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['paid','prior','completed','delivery'])
def test_composite_stars_adapter(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db);text=invoke(c)
    assert not c.invoice_trace and not c.trace and dump(c.db)==before
    assert 'composite' in text.lower() and 'synthetic-charge' not in text+caplog.text


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',SCENARIOS)
def test_legacy_stars_adapter(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    before=rows(c);selected=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy));text=invoke(c)
    invalid=scenario in {'foreign','amount','currency','missing','gateway'}
    expected='⚠️ پرداخت دریافت شد ولی فاکتور یافت نشد. با پشتیبانی تماس بگیرید.' if scenario in {'foreign','missing','gateway'} else '⚠️ مبلغ پرداخت‌شده با فاکتور نمی‌خواند. با پشتیبانی تماس بگیرید.' if scenario in {'amount','currency'} else SUCCESS if scenario=='paid' else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else '⚠️ پرداخت شما دریافت شد ولی تحویل با خطا مواجه شد. ادمین به‌زودی رسیدگی می‌کند.' if scenario=='delivery' else REPEAT
    assert text==expected and dict(c.db.get_extra_invoice(c.decoy))==decoy
    now=dict(c.db.get_extra_invoice(c.iid))
    if invalid:
        assert now==selected and not c.invoice_trace and rows(c)==before
        assert len(c.trace)==1 and c.trace[0][0:2]==('send',9001)
        assert 'synthetic-charge' in c.trace[0][2]
    else:
        assert c.invoice_trace==[('merge_extra_invoice_meta',(c.iid,{'charge_id':'synthetic-charge'})),('claim_extra_invoice',(c.iid,))]
        assert json.loads(now['meta'])=={'retained':'selected','charge_id':'synthetic-charge'}
        assert now['status']==(scenario if scenario in {'expired','cancelled'} else 'completed')
        for key in selected:
            if key not in {'status','meta','updated_at'}:assert now[key]==selected[key]
        if scenario in {'paid','delivery'}:
            assert c.db.get_order(c.oid)['status']=='approved'
            assert c.trace[:3]==[('claim_order',(c.oid,),{}),('take_unused_configs',(c.pid,USER_ID,2),{}),('approve_order',(c.oid,[r['id'] for r in before[:2]]),{})]
            assert ('delivery',USER_ID,'Stock',LINKS[:2],dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
            assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:2]) and rows(c)[2:]==before[2:]
            assert c.db.get_wallet_credit(REFERRER)==(130 if scenario=='paid' else 0)
            assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(scenario=='paid')
            if scenario=='delivery':assert c.trace[-1][0:2]==('send',9001)
        elif scenario=='shortage':
            assert c.db.get_order(c.oid)['status']=='pending' and rows(c)==before
            assert ('release_order_claim',(c.oid,),{}) in c.trace and c.trace[-1][0:2]==('send',9001)
        else:assert not c.trace and rows(c)==before
        # Repeat still writes metadata, but cannot allocate/reward again.
        saved=rows(c);order=dict(c.db.get_order(c.oid));ref=c.db.get_wallet_credit(REFERRER)
        c.trace.clear();c.invoice_trace.clear()
        assert invoke(c)==REPEAT and not c.trace and rows(c)==saved and dict(c.db.get_order(c.oid))==order and c.db.get_wallet_credit(REFERRER)==ref
        assert c.invoice_trace==[('merge_extra_invoice_meta',(c.iid,{'charge_id':'synthetic-charge'})),('claim_extra_invoice',(c.iid,))]
    assert c.db.get_wallet_credit(USER_ID)==0


INVALID='این فاکتور دیگر معتبر نیست. لطفاً دوباره از منو اقدام کن.'

def precheckout(c,payload=None):
    async def run():
        router=Router();user.register_early(router,c.db,True);answers=[]
        async def answer(**kw):answers.append(kw)
        q=SimpleNamespace(invoice_payload=payload or f'xg:{c.args[0]}',from_user=FakeUser(c.args[1]),total_amount=c.args[2],currency=c.args[3],answer=answer)
        await find_handler(router,'pre_checkout_query','stars_pre_checkout')(q)
        return answers
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
def test_composite_precheckout(catalog,monkeypatch,representation,marker):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker)
    before=dump(c.db);answers=precheckout(c)
    assert len(answers)==1 and answers[0]['ok'] is False
    assert 'composite' in answers[0]['error_message'].lower()
    assert dump(c.db)==before and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','prior','completed','expired','cancelled','foreign','amount','currency','missing','gateway','malformed','pending_invoice','cancelled_order','missing_order'])
def test_legacy_precheckout(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    if scenario=='pending_invoice':c.db.update_extra_invoice_status(c.iid,'pending')
    if scenario=='cancelled_order':
        with c.db._get_conn() as conn:conn.execute("UPDATE orders SET status='rejected' WHERE id=?",(c.oid,))
    if scenario=='missing_order':
        with c.db._get_conn() as conn:conn.execute("UPDATE extra_gateway_invoices SET ref_id=99999 WHERE id=?",(c.iid,))
    before=dump(c.db);answers=precheckout(c,'xg:bad' if scenario=='malformed' else None)
    assert answers==([{'ok':True}] if scenario in {'paid','pending_invoice'} else [{'ok':False,'error_message':INVALID}])
    assert dump(c.db)==before and not c.trace and not c.invoice_trace


@pytest.mark.parametrize('payload',['other:1','xg:bad',''])
def test_successful_payment_invalid_payload(catalog,monkeypatch,payload):
    c=catalog;setup(c,monkeypatch,'sqlite','composite');before=dump(c.db)
    async def run():
        router=Router();user.register_early(router,c.db,True);log=TelegramLog()
        message=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID))
        message.successful_payment=SimpleNamespace(invoice_payload=payload,total_amount=37,currency='XTR',telegram_payment_charge_id='synthetic-charge')
        await find_handler(router,'message','stars_successful_payment')(message,c.bot)
        assert not log.events
    asyncio.run(run())
    assert dump(c.db)==before and not c.trace and not c.invoice_trace


def test_secondary_bot_has_no_early_adapters():
    router=Router();user.register_early(router,None,False)
    assert all(not getattr(router,name).handlers for name in ['callback_query','pre_checkout_query','message'])
