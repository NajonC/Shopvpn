"""T050ao: fixed-duration volume checkout guards and legacy pending/compensation paths."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
import handlers_user
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests.integration.test_composite_telegram_custom_duration_guards import prepare as prepare_duration
from tests._harness.legacy_bot import FakeMessage,FakeUser,TelegramLog,find_handler,make_state,callback_rows
from states import CustomConfigFlow


def prepare(c,representation,kind=None,wallet=100,methods=None,global_mode=False):
    prepare_duration(c,wallet=wallet,methods=methods)
    c.db.update_custom_config_product(c.alpha_id,duration_mode='fixed',duration_days=17)
    c.configure(overrides={c.alpha_id:kind},representation=representation)
    c.global_mode=global_mode
    if global_mode:
        c.db.set_setting('custom_config_duration_days','45')
        for t in c.db.get_pricing_tiers():c.db.delete_pricing_tier(t['id'])
        c.db.add_pricing_tier(5,1000,100)


def data(c):
    d={'sentinel':'keep','panel_server_id':c.s1,'custom_username':'newname'}
    if not c.global_mode:d['product_id']=c.alpha_id
    return d


def invoke(c,text='10'):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_volume);await state.set_data(data(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),text=text)
        await find_handler(c.router,'message','custom_config_receive_volume')(msg,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_fixed_checkout_refused(catalog,monkeypatch,representation,caplog):
    c=catalog;prepare(c,representation,'composite');c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    c.effects=[]
    for name in ['calc_custom_config_product_price','create_custom_config_order']:
        original=getattr(c.db,name)
        def capture(*args,_name=name,_original=original,**kw):c.effects.append(_name);return _original(*args,**kw)
        monkeypatch.setattr(c.db,name,capture)
    monkeypatch.setattr(handlers_user,'get_provider',lambda row:c.effects.append('provider'))
    before=dump(c.db);events,state,stored=invoke(c)
    assert c.effects==[] and c.debits==[] and dump(c.db)==before
    assert state==CustomConfigFlow.waiting_volume.state and stored==data(c)
    assert len(events)==1 and events[0].kind=='message_answer' and 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text and 'newname' not in str(events)+caplog.text


def check_order(c,volume,wallet,methods=None):
    events,state,stored=invoke(c,f'  {volume}  ')
    orders=c.db.get_user_orders(USER_ID);assert len(orders)==1
    row=orders[0];price=volume*100;used=wallet if methods is None else 0;days=45 if c.global_mode else 17
    assert {k:row[k] for k in ['user_id','product_id','status','base_price','wallet_used','final_price','quantity','is_custom_config','custom_volume_gb','custom_username','custom_panel_server_id','custom_product_id','custom_duration_days','tier_discount_amount']}==dict(user_id=USER_ID,product_id=0,status='pending',base_price=price,wallet_used=used,final_price=price-used,quantity=1,is_custom_config=1,custom_volume_gb=volume,custom_username='newname',custom_panel_server_id=c.s1,custom_product_id=None if c.global_mode else c.alpha_id,custom_duration_days=days,tier_discount_amount=0)
    assert c.db.get_wallet_credit(USER_ID)==wallet-used and c.debits==([(USER_ID,-used)] if used else [])
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)|{'custom_volume_gb':volume,'custom_price':price,'order_id':row['id']}
    assert len(events)==1 and events[0].kind=='message_answer' and events[0].parse_mode=='Markdown'
    assert events[0].text==('🛠 نام کاربری: newname\n'+f'📶 حجم: {volume} گیگابایت\n⏳ مدت: {days} روز\n\n'+(f'👛 استفاده از کیف پول: {used:,} تومان\n' if used else '')+f'💰 مبلغ نهایی قابل پرداخت: {price-used:,} تومان\n\nلطفاً روش پرداخت را انتخاب کنید:')
    assert callback_rows(events[0].reply_markup)==[['pay_card2card'],['cancel_flow']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('volume',[5,1000])
@pytest.mark.parametrize('wallet',[0,100])
def test_legacy_fixed_checkout_exact(catalog,representation,kind,volume,wallet):
    c=catalog;prepare(c,representation,kind,wallet);check_order(c,volume,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('wallet',[0,100])
def test_legacy_global_checkout_fallback(catalog,representation,wallet):
    c=catalog;prepare(c,representation,wallet=wallet,global_mode=True);check_order(c,10,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_fixed_card_only(catalog,representation):
    c=catalog;prepare(c,representation,'legacy',methods='["card"]');check_order(c,10,100,methods='["card"]')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_fixed_checkout(catalog,representation):
    c=catalog;prepare(c,representation);c.configure(overrides={c.beta_id:'composite'},representation=representation);check_order(c,10,100)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('global_mode',[False,True])
@pytest.mark.parametrize('text',['4','1001','bad'])
def test_legacy_fixed_invalid_volume(catalog,representation,global_mode,text):
    c=catalog;prepare(c,representation,global_mode=global_mode)
    before=dump(c.db);events,state,stored=invoke(c,text)
    assert dump(c.db)==before and c.debits==[] and state==CustomConfigFlow.waiting_volume.state and stored==data(c)
    assert len(events)==1 and events[0].text==('❌ حجم باید بین 5 تا 1000 گیگابایت باشد.' if text.isdigit() else '❌ لطفاً فقط عدد صحیح وارد کنید (به گیگابایت).')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_unavailable_server_fixed_checkout(catalog,representation):
    c=catalog;prepare(c,representation);c.db.update_panel_server(c.s1,is_active=0)
    before=dump(c.db);events,state,stored=invoke(c)
    assert dump(c.db)==before and c.debits==[] and state is None and stored=={}
    assert len(events)==1 and events[0].text=='⛔️ سرور این بخش دیگر در دسترس نیست. لطفاً دوباره از منو شروع کنید.'


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('wallet',[0,100])
def test_unavailable_payment_fixed_checkout_compensates(catalog,representation,wallet):
    c=catalog;prepare(c,representation,wallet=wallet);c.db.set_setting('card_to_card_enabled','0')
    events,state,stored=invoke(c)
    orders=c.db.get_user_orders(USER_ID);assert len(orders)==1
    row=orders[0]
    assert (row['status'],row['base_price'],row['wallet_used'],row['final_price'],row['custom_duration_days'])==('rejected',1000,wallet,1000-wallet,17)
    assert c.db.get_wallet_credit(USER_ID)==wallet and c.debits==([(USER_ID,-wallet),(USER_ID,wallet)] if wallet else [])
    assert state is None and stored=={}
    assert len(events)==1 and events[0].text=='⛔️ در حال حاضر هیچ روش پرداخت فعالی برای این مبلغ در دسترس نیست.'+('\nمبلغ کسرشده از کیف پول شما بازگردانده شد.' if wallet else '')
