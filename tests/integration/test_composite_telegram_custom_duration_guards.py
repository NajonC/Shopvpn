"""T050af: duration submission must refuse composite before financial effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,TelegramLog,find_handler,make_state,callback_rows
import handlers_user
from states import CustomConfigFlow


def data(c):
    return {'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1,'custom_username':'newname','custom_volume_gb':10,'custom_price':1000}


def invoke(c,text):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_duration);await state.set_data(data(c))
        log=TelegramLog();message=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),text=text)
        await find_handler(c.router,'message','custom_config_receive_duration')(message,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def prepare(c,limits=(2,60),wallet=100,methods=None):
    c.db.update_custom_config_product(c.alpha_id,duration_mode='user_choice',min_days=limits[0],max_days=limits[1],payment_methods=methods)
    c.db.add_wallet_credit(USER_ID,wallet)
    c.db.set_setting('card_to_card_enabled','1')
    c.debits=[]
    original=c.db.add_wallet_credit
    def debit(user,delta):
        c.debits.append((user,delta))
        return original(user,delta)
    c.db.add_wallet_credit=debit


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_duration_refused(catalog,representation,caplog,monkeypatch):
    c=catalog;prepare(c);c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    c.configure(overrides={c.alpha_id:'composite'},representation=representation)
    calls=[];monkeypatch.setattr(handlers_user,'get_provider',lambda row:calls.append(row))
    before=dump(c.db);events,state,stored=invoke(c,'30')
    assert len(events)==1 and events[0].kind=='message_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert state==CustomConfigFlow.waiting_duration.state and stored==data(c)
    assert dump(c.db)==before and calls==[] and c.debits==[]


def check_order(c,days,wallet=100,methods=None):
    events,state,stored=invoke(c,f'  {days}  ')
    orders=c.db.get_user_orders(USER_ID)
    assert len(orders)==1
    order=orders[0];used=wallet if methods is None else 0
    assert {k:order[k] for k in ['user_id','product_id','status','base_price','wallet_used','final_price','quantity','is_custom_config','custom_volume_gb','custom_username','custom_panel_server_id','custom_product_id','custom_duration_days','tier_discount_amount']}==dict(user_id=USER_ID,product_id=0,status='pending',base_price=1000,wallet_used=used,final_price=1000-used,quantity=1,is_custom_config=1,custom_volume_gb=10,custom_username='newname',custom_panel_server_id=c.s1,custom_product_id=c.alpha_id,custom_duration_days=days,tier_discount_amount=0)
    assert c.db.get_wallet_credit(USER_ID)==wallet-used
    assert c.debits==([(USER_ID,-used)] if used else [])
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)|{'order_id':order['id']}
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==('🛠 نام کاربری: newname\n📶 حجم: 10 گیگابایت\n'+f'⏳ مدت: {days} روز\n\n'+(f'👛 استفاده از کیف پول: {used:,} تومان\n' if used else '')+f'💰 مبلغ نهایی قابل پرداخت: {1000-used:,} تومان\n\nلطفاً روش پرداخت را انتخاب کنید:')
    assert callback_rows(events[0].reply_markup)==[['pay_card2card'],['cancel_flow']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('limits,days',[((2,60),2),((2,60),60),((None,None),1),((None,None),90)])
def test_legacy_duration_exact(catalog,representation,kind,limits,days):
    c=catalog;prepare(c,limits);c.configure(overrides={c.alpha_id:kind},representation=representation);check_order(c,days)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['1','61','-1','2.0','bad',''])
def test_legacy_invalid_duration_retained(catalog,representation,text):
    c=catalog;prepare(c);c.configure(overrides={c.alpha_id:'legacy'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,text)
    assert dump(c.db)==before and state==CustomConfigFlow.waiting_duration.state and stored==data(c)
    assert len(events)==1 and events[0].text=='❌ مدت باید بین 2 تا 60 روز باشد.'


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_duration(catalog,representation):
    c=catalog;prepare(c);c.configure(overrides={c.beta_id:'composite'},representation=representation);check_order(c,30)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_card_only_preserves_wallet(catalog,representation):
    c=catalog;prepare(c,methods='["card"]');c.configure(overrides={c.alpha_id:'legacy'},representation=representation);check_order(c,30,methods='["card"]')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_missing_duration_product_clears(catalog,representation):
    c=catalog;prepare(c);c.db.delete_custom_config_product(c.alpha_id);c.configure(overrides={},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,'30')
    assert dump(c.db)==before and state is None and stored=={}
    assert len(events)==1 and events[0].text=='⛔️ این پلن دیگر در دسترس نیست. لطفاً دوباره از منو شروع کنید.'
