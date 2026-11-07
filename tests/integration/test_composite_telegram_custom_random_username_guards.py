"""T050ad: selected composite refusal before random username continuation."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()

import handlers_user
from states import CustomConfigFlow
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, FakeCallbackQuery, TelegramLog, find_handler, make_state, callback_rows


def invoke(c):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_username)
        await state.set_data({'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1})
        log=TelegramLog();msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID))
        call=FakeCallbackQuery(log,FakeUser(USER_ID),'custom_config_random_username',msg)
        await find_handler(c.router,'callback_query','cb_custom_config_random_username')(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_random_username_refused(catalog,representation,caplog,monkeypatch):
    c=catalog;c.db.update_custom_config_product(c.alpha_id,name='SECRET-COMPOSITE')
    c.configure(overrides={c.alpha_id:'composite'},representation=representation)
    effects=[]
    monkeypatch.setattr(handlers_user.random,'choices',lambda *a,**kw: effects.append('random') or list('abcdefgh'))
    monkeypatch.setattr(handlers_user,'get_provider',lambda row:effects.append('provider'))
    before=dump(c.db);events,state,stored=invoke(c)
    assert len(events)==1 and events[0].kind in {'callback_answer','message_answer'}
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert state==CustomConfigFlow.waiting_username.state
    assert stored=={'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1}
    assert dump(c.db)==before and effects==[]


def check_legacy(c,monkeypatch,prefix,collisions):
    c.db.set_custom_config_prefix(prefix)
    names=['u'+str(i)*8 for i in range(10)]
    for name in names[:collisions]:
        c.db.add_custom_config(USER_ID,c.s1,(prefix+'-' if prefix else '')+name,10,30,'')
    calls=[]
    def choices(alphabet,k):
        assert alphabet=='abcdefghijklmnopqrstuvwxyz0123456789' and k==8
        calls.append(len(calls));return list(str(calls[-1])*8)
    monkeypatch.setattr(handlers_user.random,'choices',choices)
    before=dump(c.db);events,state,stored=invoke(c)
    attempts=min(collisions+1,10);username=(prefix+'-' if prefix else '')+names[attempts-1]
    assert len(calls)==attempts
    assert dump(c.db)==before
    assert state==CustomConfigFlow.waiting_volume.state
    assert stored=={'sentinel':'keep','product_id':c.alpha_id,'panel_server_id':c.s1,'custom_username':username}
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text is None
    assert events[1].text==(f'✅ نام کاربری: {username}\n\n💰 قیمت: 100 تومان/گیگ\n\n'
                            '📶 حالا حجم مورد نظر خود را به گیگابایت وارد کنید.\n'
                            'حداقل: 5 گیگ — حداکثر: 1000 گیگ\n⏳ مدت اعتبار: 30 روز (ثابت)')
    assert callback_rows(events[1].reply_markup)==[['cancel_flow']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('prefix',['','shop'])
@pytest.mark.parametrize('collisions',[0,1,9,10])
def test_legacy_random_username_exact(catalog,monkeypatch,representation,kind,prefix,collisions):
    c=catalog;c.configure(overrides={c.alpha_id:kind},representation=representation)
    check_legacy(c,monkeypatch,prefix,collisions)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_random_username(catalog,monkeypatch,representation):
    c=catalog;c.configure(overrides={c.beta_id:'composite'},representation=representation)
    check_legacy(c,monkeypatch,'',0)
