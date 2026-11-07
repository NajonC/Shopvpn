"""T050ap: full-wallet custom checkout, real SQL/factory/delivery, external fakes only."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_telegram_custom_fixed_checkout_guards import prepare as fixed_prepare, data as fixed_data
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, TelegramLog, RecordingBot, make_state, find_handler
from states import CustomConfigFlow
import panel_providers
from panel_providers import PanelUserResult

LINK='https://subscription.example.invalid/fake-wallet-link'


def prepare(c,monkeypatch,representation,kind=None,path='fixed',wallet=1500):
    fixed_prepare(c,representation,kind,wallet=wallet,global_mode=path=='global')
    c.path=path;c.provider_calls=[]
    if path=='choice':c.db.update_custom_config_product(c.alpha_id,duration_mode='user_choice',min_days=2,max_days=60)
    c.db.set_setting('deliver_individual_configs_enabled','0')
    class Provider:
        def __init__(self,row):c.provider_calls.append(('factory',row['id'],row['panel_type']))
        async def create_user(self,username,volume,days):
            c.provider_calls.append(('create',username,volume,days))
            return PanelUserResult('panel_name',LINK)
    monkeypatch.setitem(panel_providers.PROVIDERS,'3xui',Provider)


def initial(c):
    data=fixed_data(c)
    if c.path=='choice':data.update(custom_volume_gb=10,custom_price=1000)
    return data


def invoke(c):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_duration if c.path=='choice' else CustomConfigFlow.waiting_volume);await state.set_data(initial(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),text=' 30 ' if c.path=='choice' else ' 10 ');msg.bot=RecordingBot(log)
        await find_handler(c.router,'message','custom_config_receive_duration' if c.path=='choice' else 'custom_config_receive_volume')(msg,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('path',['fixed','choice'])
def test_composite_full_wallet_refused(catalog,monkeypatch,representation,path,caplog):
    c=catalog;prepare(c,monkeypatch,representation,'composite',path)
    c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    before=dump(c.db);events,state,data=invoke(c)
    assert c.provider_calls==[] and c.debits==[] and dump(c.db)==before
    assert state==(CustomConfigFlow.waiting_duration if path=='choice' else CustomConfigFlow.waiting_volume).state and data==initial(c)
    assert len(events)==1 and 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text and LINK not in str(events)+caplog.text


def check_success(c,wallet):
    events,state,data=invoke(c)
    days={'fixed':17,'choice':30,'global':45}[c.path];pid=None if c.path=='global' else c.alpha_id
    assert c.provider_calls==[('factory',c.s1,'3xui'),('create','newname',10,days)]
    assert c.debits==[(USER_ID,-1000)] and c.db.get_wallet_credit(USER_ID)==wallet-1000
    orders=c.db.get_user_orders(USER_ID);assert len(orders)==1;o=orders[0]
    assert {k:o[k] for k in ['user_id','status','base_price','wallet_used','final_price','custom_product_id','custom_duration_days','custom_volume_gb','custom_username','custom_panel_server_id']}==dict(user_id=USER_ID,status='approved',base_price=1000,wallet_used=1000,final_price=0,custom_product_id=pid,custom_duration_days=days,custom_volume_gb=10,custom_username='newname',custom_panel_server_id=c.s1)
    configs=c.db.get_custom_configs_for_user(USER_ID);assert len(configs)==1;config=configs[0]
    assert {k:config[k] for k in ['user_id','panel_server_id','username','volume_gb','duration_days','subscription_url','order_id','product_id','source']}==dict(user_id=USER_ID,panel_server_id=c.s1,username='panel_name',volume_gb=10,duration_days=days,subscription_url=LINK,order_id=o['id'],product_id=pid,source='custom_config')
    history=c.db.get_custom_config_history(config['id']);assert len(history)==1 and history[0]['event_type']=='purchase' and history[0]['detail']==f'10 گیگ / {days} روز'
    assert state is None and data=={}
    assert events[0].text=='✅ مبلغ سفارش شما به‌طور کامل از کیف پول پوشش داده شد.\nکانفیگ شما در پیام بعدی ارسال می‌شود 👇'
    assert [(e.kind,e.chat_id) for e in events]==[('message_answer',USER_ID),('send_photo',USER_ID),('send_message',USER_ID),('send_message',USER_ID),('send_message',9001)]
    assert events[2].text==f'🔗 لینک اشتراک شما (برای کپی):\n`{LINK}`' and events[2].parse_mode=='Markdown'
    assert f'#{o["id"]}' in events[1].text and 'کانفیگ شخصی' in events[1].text
    assert '1,000' in events[-1].text and str(USER_ID) in events[-1].text and events[-1].reply_markup is None
    assert 'به‌طور خودکار تایید' in events[-1].text
    stored=c.db.get_order(o['id'])
    assert stored['admin_chat_id']==9001 and stored['admin_message_id']==events[-1].message_id



@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('path',['fixed','choice','global'])
@pytest.mark.parametrize('wallet',[1000,1500])
def test_legacy_full_wallet_success(catalog,monkeypatch,representation,kind,path,wallet):
    c=catalog;prepare(c,monkeypatch,representation,kind,path,wallet);check_success(c,wallet)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('path',['fixed','choice'])
def test_unrelated_composite_allows_wallet(catalog,monkeypatch,representation,path):
    c=catalog;prepare(c,monkeypatch,representation,None,path)
    c.configure(overrides={c.beta_id:'composite'},representation=representation);check_success(c,1500)
