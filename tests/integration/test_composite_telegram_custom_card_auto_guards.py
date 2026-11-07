"""T050ah: refuse composite custom order/product before automatic-card reservation."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,FakeCallbackQuery,TelegramLog,find_handler,make_state
from states import CustomConfigFlow


def prepare(c,representation,order_kind=None,product_kind=None,days=30,wallet=100):
    c.db.create_card_to_card_card("FAKE-CARD-NUMBER", "Synthetic Holder", "Synthetic Bank")
    c.db.set_setting("card_to_card_auto_timeout_minutes", "23")
    c.db.set_setting('card_to_card_auto_enabled','1')
    c.db.set_setting('card_number','FAKE-CARD-NUMBER')
    c.db.set_setting('card_holder','Synthetic Holder')
    c.db.set_setting('card_msg_autodelete_seconds','0')
    c.oid=c.db.create_custom_config_order(USER_ID,10,'newname',c.s1,1000,wallet_used=wallet,custom_product_id=c.alpha_id,custom_duration_days=days)
    c.configure(overrides={c.alpha_id:product_kind},representation=representation)
    original=c.db.get_order
    def get_order(oid):
        row=original(oid)
        if row is None:return None
        result=dict(row)
        if oid==c.oid and order_kind is not None:result['service_kind']=order_kind
        return as_row(result,representation)
    c.db.get_order=get_order


def data(c):return {'sentinel':'keep','order_id':c.oid}


def invoke(c):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_receipt);await state.set_data(data(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID))
        call=FakeCallbackQuery(log,FakeUser(USER_ID),'pay_card_auto',msg)
        await find_handler(c.router,'callback_query','cb_pay_card_auto_custom_config')(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
def test_composite_custom_card_entry_refused(catalog,representation,marker,caplog):
    c=catalog;prepare(c,representation,order_kind='composite' if marker=='order' else None,product_kind='composite' if marker=='product' else None)
    before=dump(c.db);events,state,stored=invoke(c)
    assert len(events)==1 and events[0].kind in {'callback_answer','message_answer'}
    assert 'composite' in (events[0].text or '').lower()
    assert 'FAKE-CARD-NUMBER' not in str(events)+caplog.text and 'newname' not in str(events)+caplog.text
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert dump(c.db)==before


def check_details(c,days,wallet):
    before_order=dict(c.db.get_order(c.oid))
    events,state,stored=invoke(c)
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert dict(c.db.get_order(c.oid))==before_order
    invoice=c.db.get_pending_card_to_card_invoice_for_ref('order',c.oid)
    assert invoice is not None
    assert invoice['user_id']==USER_ID and invoice['base_amount_toman']==1000-wallet
    amount=invoice['amount_toman']
    assert 100<=amount-(1000-wallet)<=999 and invoice['status']=='pending'
    assert [e.kind for e in events]==['callback_answer','message_answer'] and events[0].text is None
    assert events[1].text==('🛠 نام کاربری: newname\n📶 حجم: 10 گیگابایت\n'+f'⏳ مدت: {days} روز\n'+(f'👛 استفاده از کیف پول: {wallet:,} تومان\n' if wallet else '')+'💳 شماره کارت: `FAKE-CARD-NUMBER`\n👤 به نام: Synthetic Holder\n🏦 بانک: Synthetic Bank\n'+f'\n⚠️ لطفاً دقیقاً یکی از این دو مبلغ رو (بسته به واحد اپ بانکت) واریز کن:\n💰 تومان: `{amount}` ({amount:,} تومان)\n💰 ریال: `{amount*10}` ({amount*10:,} ریال)\n\n'+'✅ به‌محض دریافت پیامک بانک، پرداخت به‌صورت خودکار تایید و تحویل داده می‌شود (بدون نیاز به ارسال رسید).\n⏳ اعتبار این مبلغ فقط 23 دقیقه است؛ بعد از آن باید دوباره اقدام کنید.')
    assert events[1].reply_markup.inline_keyboard[0][0].callback_data==f"check_c2c:{invoice['id']}"
    # Re-entry preserves reserved amount, invoice, card rotation and all SQL/FSM state.
    before=dump(c.db); again,st,stored2=invoke(c)
    assert dump(c.db)==before and again[1].text==events[1].text
    assert st==state and stored2==stored


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('days',[17,None])
@pytest.mark.parametrize('wallet',[0,100])
def test_legacy_custom_card_entry_exact(catalog,representation,kind,days,wallet):
    c=catalog;prepare(c,representation,kind,kind,days,wallet)
    if days is None:c.db.set_setting('custom_config_duration_days','45')
    check_details(c,days or 45,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_custom_card(catalog,representation):
    c=catalog;prepare(c,representation)
    c.configure(overrides={c.beta_id:'composite'},representation=representation)
    check_details(c,30,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['disabled','approved','restricted','minimum','missing'])
def test_legacy_card_entry_refusals(catalog,representation,failure):
    c=catalog;prepare(c,representation,'legacy','legacy')
    expected='سفارش معتبر یافت نشد.'
    if failure=='disabled':
        c.db.set_setting('card_to_card_auto_enabled','0');expected='این روش پرداخت در حال حاضر غیرفعال است.'
    elif failure=='approved':c.db.approve_custom_config_order(c.oid)
    elif failure=='restricted':
        c.db.update_custom_config_product(c.alpha_id,payment_methods='["wallet"]');expected='⛔️ این روش پرداخت برای ساخت کانفیگ شخصی مجاز نیست.'
    elif failure=='minimum':
        c.db.set_setting('min_amount_card_auto','901');expected='⛔️ حداقل مبلغ قابل پرداخت با این روش 901 تومان است.'
    elif failure=='missing':c.oid=99999
    before=dump(c.db);events,state,stored=invoke(c)
    assert dump(c.db)==before and state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].text==expected and events[0].show_alert


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_card_minimum_boundary_allowed(catalog,representation):
    c=catalog;prepare(c,representation,'legacy','legacy');c.db.set_setting('min_amount_card_auto','900');check_details(c,30,100)

@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_card_auto_reservation_error(catalog,representation):
    c=catalog;prepare(c,representation)
    for card in c.db.list_card_to_card_cards():c.db.delete_card_to_card_card(card['id'])
    before=dump(c.db);events,state,stored=invoke(c)
    assert dump(c.db)==before and stored==data(c) and state==CustomConfigFlow.waiting_receipt.state
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text is None and events[1].text=='⚠️ هیچ شماره کارتی برای دریافت وجه تعریف نشده است.'
