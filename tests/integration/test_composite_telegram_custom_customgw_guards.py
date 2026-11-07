"""T050am: selected custom order/product refusal before customgw invoice side effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare,data
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,FakeCallbackQuery,TelegramLog,find_handler,make_state
from states import CustomConfigFlow
import custom_gateway_payment as payment
import payment_engine as client
import re

URL='https://payment.example.invalid/synthetic-invoice'


def setup(c,monkeypatch,representation,kind=None,marker='both',wallet=100):
    prepare(c,representation,kind if marker in {'both','order'} else None,kind if marker in {'both','product'} else None,wallet=wallet)
    c.db.set_setting('miniapp_tenant_id','synthetic-tenant')
    c.gid=c.db.create_custom_gateway('synthetic','Synthetic Gateway',{
        'amount_currency':'rial','amount_multiplier':2,
        'credentials':{'key':'synthetic-key'},
        'create_request':{'url':'https://payment.example.invalid/create','headers':{'X-Key':'{key}'},
          'body':{k:'{'+k+'}' for k in ['amount','amount_toman','order_id','currency','description','tenant_id','callback_url','webhook_url','customer_user_id','customer_phone']}},
        'create_response':{'invoice_url_path':'url','txn_id_path':'ref'}},enabled=True)
    monkeypatch.setattr(payment,'API_BASE_URL','https://shop.example.invalid')
    c.no_url=False
    c.remote=[];c.remote_error=False;c.helper_calls=[]
    original=payment.create_invoice_for
    async def recorded(*args,**kwargs):
        c.helper_calls.append((args[1:],kwargs))
        return await original(*args,**kwargs)
    monkeypatch.setattr(payment,'create_invoice_for',recorded)
    async def create(method,url,headers,body_type,body):
        c.remote.append((method,url,headers,body_type,body))
        if c.remote_error:raise client.PaymentEngineError('synthetic outage')
        return {'ref':'synthetic-remote-ref','url':None if c.no_url else URL}
    monkeypatch.setattr(client,'_http_request',create)


def invoke(c):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_receipt);await state.set_data(data(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID))
        call=FakeCallbackQuery(log,FakeUser(USER_ID),f'pay_customgw:{c.gid}',msg)
        await find_handler(c.router,'callback_query','cb_pay_customgw_custom_config')(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
def test_composite_custom_customgw_refused(catalog,monkeypatch,representation,marker,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker)
    before=dump(c.db);events,state,stored=invoke(c)
    assert c.helper_calls==[] and c.remote==[] and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert len(events)==1 and 'composite' in (events[0].text or '').lower()
    assert all(value not in str(events)+caplog.text for value in ['newname',URL,'synthetic-key'])


def check_success(c,wallet):
    before_order=dict(c.db.get_order(c.oid));events,state,stored=invoke(c)
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert dict(c.db.get_order(c.oid))==before_order
    assert len(c.helper_calls)==1
    assert c.helper_calls[0]==(('synthetic-tenant',USER_ID,'synthetic','order',c.oid,1000-wallet),{'order_name':f'کانفیگ شخصی #{c.oid} - newname'})
    assert len(c.remote)==1
    method,url,headers,body_type,kw=c.remote[0]
    assert (method,url,headers,body_type)==('POST','https://payment.example.invalid/create',{'X-Key':'synthetic-key'},'json')
    row=c.db.get_pending_custom_gateway_invoice_for_ref(c.gid,'order',c.oid)
    assert row is not None and row['user_id']==USER_ID and row['amount_toman']==1000-wallet
    assert row['gateway_ref']=='synthetic-remote-ref' and row['invoice_url']==(None if c.no_url else URL)
    assert re.fullmatch(f'order-synthetic-tenant-{c.oid}-[0-9]+-[0-9a-f]{{12}}',row['txn_id'])
    assert re.fullmatch(f'{c.oid}-[0-9]+',kw['order_id']) and len(kw['order_id'])<=20
    assert kw=={'amount':str((1000-wallet)*20),'amount_toman':str(1000-wallet),'order_id':kw['order_id'],'currency':'IRR','description':f'کانفیگ شخصی #{c.oid} - newname','tenant_id':'synthetic-tenant','callback_url':f"https://shop.example.invalid/api/pay/custom/synthetic/return?b=synthetic-tenant&txn={row['txn_id']}",'webhook_url':'https://shop.example.invalid/api/webhooks/custom/synthetic?b=synthetic-tenant','customer_user_id':str(USER_ID),'customer_phone':''}
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text=='در حال ساخت فاکتور...'
    if c.no_url:
        assert events[1].text=='💠 فاکتور «Synthetic Gateway» ساخته شد ولی این درگاه لینک پرداخت برنگرداند.\nپس از انجام پرداخت، کانفیگ به‌محض تایید درگاه به‌صورت خودکار ساخته می‌شود.'
        assert events[1].reply_markup is None
    else:
        assert events[1].text=='💠 فاکتور پرداخت «Synthetic Gateway» ساخته شد. روی دکمه‌ی زیر بزن و پرداخت رو تکمیل کن.\nبه‌محض تایید پرداخت توسط درگاه، کانفیگ شما به‌صورت خودکار ساخته می‌شود.'
        assert len(events[1].reply_markup.inline_keyboard)==1 and events[1].reply_markup.inline_keyboard[0][0].url==URL
    before=dump(c.db);again,st,stored2=invoke(c)
    assert dump(c.db)==before and len(c.remote)==1 and again[1].text==events[1].text
    assert st==state and stored2==stored


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('wallet',[0,100])
def test_legacy_custom_customgw_exact(catalog,monkeypatch,representation,kind,wallet):
    c=catalog;setup(c,monkeypatch,representation,kind,wallet=wallet);check_success(c,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_customgw(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation)
    c.configure(overrides={c.beta_id:'composite'},representation=representation);check_success(c,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['approved','restricted','minimum','missing','disabled','no_gateway'])
def test_legacy_customgw_refusals(catalog,monkeypatch,representation,failure):
    c=catalog;setup(c,monkeypatch,representation,'legacy')
    expected='سفارش معتبر یافت نشد.'
    if failure=='approved':c.db.approve_custom_config_order(c.oid)
    elif failure=='restricted':
        c.db.update_custom_config_product(c.alpha_id,payment_methods='["wallet"]');expected='⛔️ این روش پرداخت برای ساخت کانفیگ شخصی مجاز نیست.'
    elif failure=='minimum':
        c.db.update_custom_gateway(c.gid,min_amount=901);expected='⛔️ حداقل مبلغ قابل پرداخت با این روش 901 تومان است.'
    elif failure=='missing':c.oid=99999
    elif failure=='disabled':c.db.update_custom_gateway(c.gid,enabled=False);expected='این درگاه در دسترس نیست.'
    elif failure=='no_gateway':c.gid=99999;expected='این درگاه در دسترس نیست.'
    before=dump(c.db);events,state,stored=invoke(c)
    assert c.helper_calls==[] and c.remote==[] and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].text==expected and events[0].show_alert


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_customgw_minimum_boundary(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation,'legacy');c.db.update_custom_gateway(c.gid,min_amount=900);check_success(c,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_customgw_gateway_error(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation);c.remote_error=True
    before=dump(c.db);events,state,stored=invoke(c)
    assert len(c.remote)==1 and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text=='در حال ساخت فاکتور...' and events[1].text=='⚠️ synthetic outage'


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_customgw_without_url(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation);c.no_url=True;check_success(c,100)
