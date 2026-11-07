"""T050ac: selected composite refusal before custom username continuation effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, TelegramLog, find_handler, make_state, callback_rows
import handlers_user
from states import CustomConfigFlow


def data(c):
    return {'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1}


def invoke(c,text='new_name'):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_username)
        await state.set_data(data(c))
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),text=text)
        handler=find_handler(c.router,'message','custom_config_receive_username')
        await handler(msg,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def assert_retained(c,state,stored):
    assert state==CustomConfigFlow.waiting_username.state and stored==data(c)


def assert_legacy(c,text='new_name',prefix=''):
    before=dump(c.db);events,state,stored=invoke(c,text)
    username=(prefix+'-' if prefix else '')+text.strip()
    assert dump(c.db)==before
    assert state==CustomConfigFlow.waiting_volume.state
    assert stored==data(c)|{'custom_username':username}
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==(f'✅ نام کاربری: {username}\n\n💰 قیمت: 100 تومان/گیگ\n\n'
                            '📶 حالا حجم مورد نظر خود را به گیگابایت وارد کنید.\n'
                            'حداقل: 5 گیگ — حداکثر: 1000 گیگ\n⏳ مدت اعتبار: 30 روز (ثابت)')
    assert callback_rows(events[0].reply_markup)==[['cancel_flow']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_custom_username_refused(catalog,representation,caplog,monkeypatch):
    c=catalog;c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    c.configure(overrides={c.alpha_id:'composite'},representation=representation)
    calls=[];monkeypatch.setattr(handlers_user,'get_provider',lambda row:calls.append(row))
    before=dump(c.db);events,state,stored=invoke(c)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert_retained(c,state,stored)
    assert dump(c.db)==before and calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('prefix',['','shop'])
@pytest.mark.parametrize('text',['abc','a'*20,'  new_name  '])
def test_legacy_custom_username_exact(catalog,representation,kind,prefix,text):
    c=catalog;c.db.set_custom_config_prefix(prefix)
    c.configure(overrides={c.alpha_id:kind},representation=representation)
    assert_legacy(c,text,prefix)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_custom_username(catalog,representation):
    c=catalog;c.configure(overrides={c.beta_id:'composite'},representation=representation);assert_legacy(c)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['aa','a'*21,'bad name','نام'])
def test_legacy_custom_username_invalid(catalog,representation,text):
    c=catalog;c.configure(overrides={c.alpha_id:'legacy'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,text)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text=='❌ نام کاربری نامعتبر است. فقط حروف انگلیسی، عدد و آندرلاین، بین ۳ تا ۲۰ کاراکتر.'
    assert_retained(c,state,stored);assert dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('prefix',['','shop'])
def test_legacy_custom_username_taken(catalog,representation,prefix):
    c=catalog;c.db.set_custom_config_prefix(prefix)
    c.db.add_custom_config(USER_ID,c.s1,(prefix+'-' if prefix else '')+'alpha',10,30,'')
    c.configure(overrides={c.alpha_id:'legacy'},representation=representation)
    before=dump(c.db);events,state,stored=invoke(c,'alpha')
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text=='❌ این نام کاربری قبلاً استفاده شده. لطفاً نام دیگری انتخاب کنید.'
    assert_retained(c,state,stored);assert dump(c.db)==before
