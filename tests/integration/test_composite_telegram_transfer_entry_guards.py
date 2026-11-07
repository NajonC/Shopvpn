"""T050z: refuse unsupported composite transfer before recipient-entry effects."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_user
from states import ServiceTransferFlow
from tests.integration.test_composite_telegram_autorenew_guards import controls, BUYER, FOREIGN
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeCallbackQuery, FakeMessage, FakeUser, TelegramLog, find_handler, make_state, callback_rows

PROMPT = ('👤 آی‌دی عددی تلگرام کاربری که می‌خواهید این کانفیگ به او منتقل شود را ارسال کنید.\n'
          'توجه: آن کاربر باید قبلاً بات را استارت کرده باشد.')


def invoke(c, uid=BUYER):
    async def run():
        state=make_state(uid)
        await state.set_state('sentinel-state')
        await state.set_data({'sentinel':'keep','cb_id':'x999'})
        log=TelegramLog();user=FakeUser(uid);msg=FakeMessage(log,uid,from_user=user)
        call=FakeCallbackQuery(log,user,f'svc_transfer:x{c.target}',msg)
        handler=find_handler(handlers_user.create_user_router(c.db),'callback_query','cb_service_transfer_ask')
        await handler(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def assert_unchanged(c,before,state,data):
    assert state=='sentinel-state'
    assert data=={'sentinel':'keep','cb_id':'x999'}
    assert dump(c.db)==before and c.calls==[]


def assert_legacy(c):
    before=dump(c.db);events,state,data=invoke(c)
    assert dump(c.db)==before and c.calls==[]
    assert state==ServiceTransferFlow.waiting_target_id.state
    assert data=={'sentinel':'keep','cb_id':f'x{c.target}'}
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert not events[0].text and not events[0].show_alert
    assert events[1].text==PROMPT
    assert callback_rows(events[1].reply_markup)==[['cancel_flow']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_transfer_entry_refused(controls,representation,caplog):
    c=controls;c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert_unchanged(c,before,state,data)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
def test_legacy_transfer_entry_exact(controls,representation,kind):
    c=controls;c.inject(c.target,kind,representation);assert_legacy(c)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_transfer_entry(controls,representation):
    c=controls;c.inject(c.sibling,'composite',representation);assert_legacy(c)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_transfer_entry_opaque(controls,representation):
    c=controls;c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c,FOREIGN)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text=='این مورد یافت نشد.' and events[0].show_alert
    assert_unchanged(c,before,state,data)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('restriction',['off','test'])
def test_transfer_entry_restrictions(controls,representation,restriction):
    c=controls;c.inject(c.target,'legacy',representation)
    if restriction=='off': c.db.set_setting('svc_show_transfer','0')
    else:
        with c.db._get_conn() as conn:
            conn.execute("UPDATE custom_configs SET source='test' WHERE id=?",(c.target,))
    before=dump(c.db);events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==('این قابلیت غیرفعال است.' if restriction=='off' else 'این قابلیت برای کانفیگ تست در دسترس نیست.')
    assert events[0].show_alert
    assert_unchanged(c,before,state,data)
