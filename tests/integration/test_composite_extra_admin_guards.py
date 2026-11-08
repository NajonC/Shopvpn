"""T050cd/ce: actual extra-gateway admin/check/process/stock linkage."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from aiogram import Router
import extra_gateway_admin as admin
import extra_gateway_payment as egp
from tests._harness.legacy_bot import FakeUser, FakeMessage, FakeCallbackQuery, TelegramLog, RecordingBot, find_handler
from tests.integration.test_composite_gateway_stock_guards import catalog, setup as stock_setup, rows, dump, LINKS, USER_ID, REFERRER, SUCCESS
OWNER=9001
DONE='✅ این پرداخت قبلاً تایید و تحویل داده شده است.'
SCENARIOS=['paid','prior','shortage','delivery','pending','failed','remote_error','completed','cancelled','expired','claim_lost']


def setup(c,mp,representation,kind=None,marker='order',scenario='paid'):
    stock_setup(c,mp,'abangateway_payment',representation,kind,marker,scenario if scenario in {'prior','shortage','delivery'} else 'success')
    # Deliberately different invoice id and order id: wrong linkage must fail.
    c.decoy=c.db.create_extra_invoice('zarinpal','order',99999,USER_ID,111,111)
    c.iid=c.db.create_extra_invoice('zarinpal','order',c.oid,USER_ID,900,900,remote_id='synthetic-remote',order_number='synthetic-number')
    c.remote=[];c.invoice_trace=[]
    for method in ['claim_extra_invoice','release_extra_invoice','update_extra_invoice_status']:
        original=getattr(c.db,method)
        def call(*args,_name=method,_fn=original,**kw):
            c.invoice_trace.append((_name,args))
            if scenario=='claim_lost' and _name=='claim_extra_invoice':assert _fn(*args,**kw)
            return _fn(*args,**kw)
        mp.setattr(c.db,method,call)
    if scenario in {'completed','expired','cancelled'}:c.db.update_extra_invoice_status(c.iid,scenario)
    c.invoice_trace.clear()
    async def remote(db,invoice):
        c.remote.append((invoice['gateway'],invoice['remote_id'],invoice['order_number'],invoice['payable_amount']))
        if scenario=='remote_error':raise egp.clients.GatewayError('synthetic outage')
        return scenario if scenario in {'pending','failed'} else egp.clients.PAID
    mp.setattr(egp,'_remote_state',remote)
    c.router=Router()
    async def unused(*args,**kw):raise AssertionError('unexpected admin UI')
    def ident(data,prefix):
        try:return int(data.split(':')[1])
        except (ValueError,IndexError):return None
    admin.register(c.router,c.db,True,lambda uid:uid==OWNER,lambda uid:uid==OWNER,unused,unused,unused,ident)


def invoke(c,uid=OWNER,data=None):
    async def run():
        log=TelegramLog();user=FakeUser(uid)
        call=FakeCallbackQuery(log,user,data or f'check_xgw_invoice:{c.iid}',FakeMessage(log,uid,from_user=user))
        await find_handler(c.router,'callback_query','cb_check_xgw_invoice')(call,c.bot)
        return log.events
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['paid','pending','completed','delivery','prior'])
def test_composite_extra_admin(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db);events=invoke(c)
    assert not c.remote and not c.invoice_trace and not c.trace and dump(c.db)==before
    assert len(events)==1 and events[0].show_alert and 'composite' in (events[0].text or '').lower()
    assert 'synthetic-remote' not in str(events)+caplog.text


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',SCENARIOS)
def test_legacy_extra_admin(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    before=rows(c);decoy=dict(c.db.get_extra_invoice(c.decoy));events=invoke(c)
    assert len(events)==2 and events[0].text=='در حال بررسی...' and not events[0].show_alert
    expected=SUCCESS if scenario=='paid' else DONE if scenario in {'completed','claim_lost'} else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else '⚠️ خطا در بررسی وضعیت: خطای غیرمنتظره در تحویل؛ دوباره بررسی می‌شود.' if scenario=='delivery' else '⏳ هنوز پرداختی برای این فاکتور تایید نشده.' if scenario=='pending' else '⚠️ خطا در بررسی وضعیت: synthetic outage' if scenario=='remote_error' else '❌ اعتبار این فاکتور تمام شده یا لغو شده است.'
    assert events[1].text==expected
    assert c.remote==([] if scenario in {'completed','expired','cancelled'} else [('zarinpal','synthetic-remote','synthetic-number',900)])
    status='completed' if scenario in {'paid','prior','shortage','completed','claim_lost'} else 'pending' if scenario=='delivery' else 'expired' if scenario=='failed' else scenario if scenario in {'expired','cancelled'} else 'new'
    assert c.db.get_extra_invoice(c.iid)['status']==status and dict(c.db.get_extra_invoice(c.decoy))==decoy
    if scenario in {'paid','delivery'}:
        assert c.db.get_order(c.oid)['status']=='approved'
        assert c.trace[:3]==[('claim_order',(c.oid,),{}),('take_unused_configs',(c.pid,USER_ID,2),{}),('approve_order',(c.oid,[r['id'] for r in before[:2]]),{})]
        assert ('delivery',USER_ID,'Stock',LINKS[:2],dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
        assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:2]) and rows(c)[2:]==before[2:]
        assert c.db.get_wallet_credit(REFERRER)==(130 if scenario=='paid' else 0)
        assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(scenario=='paid')
        if scenario=='delivery':assert c.invoice_trace[-1]==('release_extra_invoice',(c.iid,))
    elif scenario=='shortage':
        assert c.db.get_order(c.oid)['status']=='pending' and rows(c)==before
        assert c.trace[0]==('claim_order',(c.oid,),{}) and ('release_order_claim',(c.oid,),{}) in c.trace
    else:assert not c.trace and rows(c)==before
    assert c.db.get_wallet_credit(USER_ID)==0
    if status=='completed':
        state=dump(c.db);c.trace.clear();c.invoice_trace.clear();count=len(c.remote)
        assert invoke(c)[1].text==DONE and dump(c.db)==state and not c.trace and not c.invoice_trace and len(c.remote)==count


@pytest.mark.parametrize('scenario',['unauthorized','malformed','missing'])
def test_extra_admin_opaque(catalog,monkeypatch,scenario):
    c=catalog;setup(c,monkeypatch,'sqlite','composite')
    before=dump(c.db)
    events=invoke(c,USER_ID if scenario=='unauthorized' else OWNER,'check_xgw_invoice:bad' if scenario=='malformed' else 'check_xgw_invoice:99999' if scenario=='missing' else None)
    assert len(events)==1 and events[0].text==(None if scenario=='unauthorized' else 'فاکتور یافت نشد.')
    assert not c.trace and not c.remote and not c.invoice_trace and dump(c.db)==before
