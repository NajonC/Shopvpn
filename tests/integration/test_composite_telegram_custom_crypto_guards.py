"""T050ai: selected custom order/product refusal before crypto invoice side effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare,data
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,FakeCallbackQuery,TelegramLog,find_handler,make_state
from states import CustomConfigFlow
import crypto_payment as payment
import plisio_client as client

URL='https://payment.example.invalid/synthetic-invoice'


def setup(c,monkeypatch,representation,kind=None,marker='both',wallet=100):
    prepare(c,representation,kind if marker in {'both','order'} else None,kind if marker in {'both','product'} else None,wallet=wallet)
    c.db.set_setting('plisio_api_key','synthetic-key')
    c.db.set_setting('crypto_payment_enabled','1')
    c.db.set_setting('miniapp_tenant_id','synthetic-tenant')
    c.db.set_setting('usd_to_toman_rate','100')
    monkeypatch.setattr(payment,'API_BASE_URL','https://shop.example.invalid',raising=False)
    c.remote=[];c.remote_error=False;c.helper_calls=[]
    original=payment.create_invoice_for
    async def recorded(*args,**kwargs):
        c.helper_calls.append((args[1:],kwargs))
        return await original(*args,**kwargs)
    monkeypatch.setattr(payment,'create_invoice_for',recorded)
    async def create(**kw):
        c.remote.append(kw)
        if c.remote_error:raise client.PlisioError('synthetic outage')
        return {'invoice_url':URL,'txn_id':'synthetic-remote-id'}
    monkeypatch.setattr(client,'create_invoice',create)


def invoke(c):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_receipt);await state.set_data(data(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID))
        call=FakeCallbackQuery(log,FakeUser(USER_ID),'pay_crypto',msg)
        await find_handler(c.router,'callback_query','cb_pay_crypto_custom_config')(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
def test_composite_custom_crypto_refused(catalog,monkeypatch,representation,marker,caplog):
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
    assert c.helper_calls[0]==(('synthetic-tenant',USER_ID,'order',c.oid,1000-wallet),{'order_name':f'کانفیگ شخصی #{c.oid} - newname'})
    assert len(c.remote)==1
    kw=c.remote[0]
    assert set(kw)=={'api_key','order_number','order_name','source_amount_usd','callback_url','expire_min','allowed_psys_cids'}
    assert kw['api_key']=='synthetic-key' and kw['source_amount_usd']==(1000-wallet)/100
    assert kw['order_number'].startswith(f'order-synthetic-tenant-{c.oid}-')
    assert kw['order_name']==f'کانفیگ شخصی #{c.oid} - newname'
    assert kw['callback_url']=='https://shop.example.invalid/api/webhooks/plisio?b=synthetic-tenant&json=true'
    assert kw['expire_min']==80 and kw['allowed_psys_cids']==''
    row=c.db.get_pending_crypto_invoice_for_ref('order',c.oid)
    assert row is not None and row['user_id']==USER_ID and row['amount_toman']==1000-wallet
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text=='در حال ساخت فاکتور...'
    assert events[1].text=='🪙 فاکتور پرداخت ساخته شد. روی دکمه\u200cی زیر بزن، ارز و مبلغ رو انتخاب کن و پرداخت رو تکمیل کن.\n⏳ اعتبار این فاکتور فقط ۸۰ دقیقه است.\nبه\u200cمحض تایید تراکنش روی بلاک\u200cچین، کانفیگ شما به\u200cصورت خودکار ساخته می\u200cشود.'
    assert events[1].reply_markup.inline_keyboard[0][0].url==URL
    assert len(events[1].reply_markup.inline_keyboard)==1
    before=dump(c.db);again,st,stored2=invoke(c)
    assert dump(c.db)==before and len(c.remote)==1 and again[1].text==events[1].text
    assert st==state and stored2==stored


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('wallet',[0,100])
def test_legacy_custom_crypto_exact(catalog,monkeypatch,representation,kind,wallet):
    c=catalog;setup(c,monkeypatch,representation,kind,wallet=wallet);check_success(c,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_crypto(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation)
    c.configure(overrides={c.beta_id:'composite'},representation=representation);check_success(c,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['approved','restricted','minimum','missing'])
def test_legacy_crypto_refusals(catalog,monkeypatch,representation,failure):
    c=catalog;setup(c,monkeypatch,representation,'legacy')
    expected='سفارش معتبر یافت نشد.'
    if failure=='approved':c.db.approve_custom_config_order(c.oid)
    elif failure=='restricted':
        c.db.update_custom_config_product(c.alpha_id,payment_methods='["wallet"]');expected='⛔️ این روش پرداخت برای ساخت کانفیگ شخصی مجاز نیست.'
    elif failure=='minimum':
        c.db.set_setting('min_amount_crypto','901');expected='⛔️ حداقل مبلغ قابل پرداخت با این روش 901 تومان است.'
    elif failure=='missing':c.oid=99999
    before=dump(c.db);events,state,stored=invoke(c)
    assert c.helper_calls==[] and c.remote==[] and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].text==expected and events[0].show_alert


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_crypto_minimum_boundary(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation,'legacy');c.db.set_setting('min_amount_crypto','900');check_success(c,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_crypto_gateway_error(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation);c.remote_error=True
    before=dump(c.db);events,state,stored=invoke(c)
    assert len(c.remote)==1 and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text=='در حال ساخت فاکتور...' and events[1].text=='⚠️ خطا از درگاه پرداخت: synthetic outage'
