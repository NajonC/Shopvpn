"""T050aa: composite refusal before transfer recipient confirmation effects."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_user
from states import ServiceTransferFlow
from tests.integration.test_composite_telegram_autorenew_guards import controls, BUYER, FOREIGN
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, TelegramLog, find_handler, make_state, callback_rows

RECIPIENT=5103
PROMPT=(f'⚠️ آیا مطمئن هستید که این کانفیگ به کاربر با آی‌دی {RECIPIENT} منتقل شود؟\n'
        'این عملیات **غیرقابل بازگشت** است.')


@pytest.fixture
def transfer_control(controls):
    controls.db.add_or_update_user(RECIPIENT,'synthetic_recipient','Synthetic')
    return controls


def invoke(c,uid=BUYER,text='5103'):
    async def run():
        state=make_state(uid);await state.set_state(ServiceTransferFlow.waiting_target_id)
        await state.set_data({'sentinel':'keep','cb_id':f'x{c.target}'})
        log=TelegramLog();msg=FakeMessage(log,uid,from_user=FakeUser(uid),text=text)
        handler=find_handler(handlers_user.create_user_router(c.db),'message','service_transfer_receive')
        await handler(msg,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def assert_retained(c,state,data):
    assert state==ServiceTransferFlow.waiting_target_id.state
    assert data=={'sentinel':'keep','cb_id':f'x{c.target}'}


def assert_legacy(c,text='5103'):
    before=dump(c.db);events,state,data=invoke(c,text=text)
    assert dump(c.db)==before and c.calls==[]
    assert state is None and data=={}
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==PROMPT and events[0].parse_mode=='Markdown'
    assert callback_rows(events[0].reply_markup)==[[f'svc_transok:x{c.target}:{RECIPIENT}'],[f'mo_v:x{c.target}']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_transfer_receive_refused(transfer_control,representation,caplog):
    c=transfer_control;c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert_retained(c,state,data)
    assert dump(c.db)==before and c.calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('text',['5103','  005103  '])
def test_legacy_transfer_receive_exact(transfer_control,representation,kind,text):
    c=transfer_control;c.inject(c.target,kind,representation);assert_legacy(c,text)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_transfer_receive(transfer_control,representation):
    c=transfer_control;c.inject(c.sibling,'composite',representation);assert_legacy(c)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_transfer_receive_opaque(transfer_control,representation):
    c=transfer_control;c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c,FOREIGN)
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text=='این مورد دیگر یافت نشد.'
    assert state is None and data=={} and c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('text',['abc','','5101','99999'])
def test_legacy_transfer_receive_invalid(transfer_control,representation,text):
    c=transfer_control;c.inject(c.target,'legacy',representation);before=dump(c.db)
    events,state,data=invoke(c,text=text)
    expected={'abc':'❌ فقط آی‌دی عددی تلگرام را ارسال کنید.','':'❌ فقط آی‌دی عددی تلگرام را ارسال کنید.',
              '5101':'این کانفیگ همین الان مال شماست.','99999':'❌ این کاربر بات را استارت نکرده یا آی‌دی نادرست است.'}[text]
    assert len(events)==1 and events[0].kind=='message_answer' and events[0].text==expected
    assert_retained(c,state,data)
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('flag',['off','test'])
def test_legacy_transfer_receive_preserves_direct_flags(transfer_control,representation,flag):
    c=transfer_control;c.inject(c.target,'legacy',representation)
    if flag=='off': c.db.set_setting('svc_show_transfer','0')
    else:
        with c.db._get_conn() as conn:
            conn.execute("UPDATE custom_configs SET source='test' WHERE id=?",(c.target,))
    assert_legacy(c)
