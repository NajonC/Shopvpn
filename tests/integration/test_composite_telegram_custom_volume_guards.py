"""T050ae: custom-volume continuation into user-selected duration."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,TelegramLog,find_handler,make_state
import handlers_user
from states import CustomConfigFlow


def data(c):
    return {'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1,'custom_username':'new_name'}


def invoke(c,text):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_volume);await state.set_data(data(c))
        log=TelegramLog();message=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),text=text)
        await find_handler(c.router,'message','custom_config_receive_volume')(message,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def choice(c,min_days=2,max_days=60):
    c.db.update_custom_config_product(c.alpha_id,duration_mode='user_choice',min_days=min_days,max_days=max_days)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_volume_refused(catalog,representation,caplog,monkeypatch):
    c=catalog;choice(c);c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    c.configure(overrides={c.alpha_id:'composite'},representation=representation)
    calls=[];monkeypatch.setattr(handlers_user,'get_provider',lambda row:calls.append(row))
    calc=c.db.calc_custom_config_product_price
    def price(*args):calls.append('price');return calc(*args)
    monkeypatch.setattr(c.db,'calc_custom_config_product_price',price)
    before=dump(c.db);events,state,stored=invoke(c,'10')
    assert len(events)==1 and events[0].kind=='message_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert state==CustomConfigFlow.waiting_volume.state and stored==data(c)
    assert dump(c.db)==before and calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('volume',[5,1000])
@pytest.mark.parametrize('limits',[(2,60),(None,None)])
def test_legacy_volume_exact(catalog,representation,kind,volume,limits):
    c=catalog;choice(c,*limits);c.configure(overrides={c.alpha_id:kind},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,f'  {volume}  ')
    assert dump(c.db)==before
    assert state==CustomConfigFlow.waiting_duration.state
    assert stored==data(c)|{'custom_volume_gb':volume,'custom_price':volume*100}
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==f'⏳ مدت اعتبار را به روز وارد کن (بین {limits[0] or 1} تا {limits[1] or 90} روز):'
    assert events[0].reply_markup is None


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['4','1001','-1','5.0','bad',''])
def test_legacy_invalid_volume_retained(catalog,representation,text):
    c=catalog;choice(c);c.configure(overrides={c.alpha_id:'legacy'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,text)
    assert dump(c.db)==before and state==CustomConfigFlow.waiting_volume.state and stored==data(c)
    assert len(events)==1
    assert events[0].text==('❌ حجم باید بین 5 تا 1000 گیگابایت باشد.' if text.isdigit() else '❌ لطفاً فقط عدد صحیح وارد کنید (به گیگابایت).')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_legacy_zero_price_clears(catalog,representation):
    c=catalog;choice(c);c.db.update_custom_config_product(c.alpha_id,flat_price_per_gb=0)
    c.configure(overrides={c.alpha_id:'legacy'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,'5')
    assert dump(c.db)==before and state is None and stored=={}
    assert len(events)==1 and events[0].text=='⚠️ قیمت‌گذاری برای این بخش هنوز تنظیم نشده. لطفاً با پشتیبانی تماس بگیرید.'


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_volume(catalog,representation):
    c=catalog;choice(c);c.configure(overrides={c.beta_id:'composite'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,'10')
    assert dump(c.db)==before and state==CustomConfigFlow.waiting_duration.state
    assert stored==data(c)|{'custom_volume_gb':10,'custom_price':1000}
    assert len(events)==1 and events[0].text=='⏳ مدت اعتبار را به روز وارد کن (بین 2 تا 60 روز):'
