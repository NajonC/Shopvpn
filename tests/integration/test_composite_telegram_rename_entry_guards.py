"""T050x: Telegram rename prompt refuses composite service before FSM/UI effects."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_autorenew_guards import controls, BUYER, FOREIGN
import handlers_user
from states import CustomConfigFlow, ServiceRenameFlow
from tests._harness.legacy_bot import FakeUser, FakeMessage, FakeCallbackQuery, TelegramLog, find_handler, make_state, callback_rows
from tests.integration.test_composite_ai_catalog_legacy import dump


def configure_label(c, mode):
    c.db.set_custom_config_prefix('shop' if mode!='none' else '')
    if mode=='matching': c.db.rename_custom_config(c.target,BUYER,'shop-alpha')


def invoke(c, uid=BUYER):
    async def run():
        state=make_state(uid)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({'sentinel':'keep'})
        log=TelegramLog();user=FakeUser(uid)
        msg=FakeMessage(log,uid,from_user=user)
        call=FakeCallbackQuery(log,user,f'svc_rename:x{c.target}',msg)
        fn=find_handler(handlers_user.create_user_router(c.db),'callback_query','cb_service_rename_ask')
        await fn(call,state)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


def exact_legacy(c, mode, events, state, data):
    label='shop-alpha' if mode=='matching' else 'alpha'
    body=('ادامه‌ی نام جدید (بعد از «shop-») را ارسال کنید.\nفقط حروف انگلیسی، عدد و آندرلاین، بین ۳ تا ۲۰ کاراکتر.' if mode=='matching' else 'نام جدید کانفیگ را ارسال کنید. فقط حروف انگلیسی، عدد و آندرلاین، بین ۳ تا ۲۰ کاراکتر.')
    assert [e.kind for e in events]==['callback_answer','message_answer']
    assert events[0].text is None and not events[0].show_alert
    assert events[1].text==f'✏️ نام فعلی: «{label}»\n\n'+body
    assert callback_rows(events[1].reply_markup)==[['cancel_flow']]
    assert state==ServiceRenameFlow.waiting_suffix.state
    assert data=={'sentinel':'keep','cb_id':f'x{c.target}'}
    assert c.calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('mode',['none','matching'])
def test_composite_rename_entry_refused(controls,representation,mode,caplog):
    c=controls;configure_label(c,mode);c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert state==CustomConfigFlow.waiting_product_select.state and data=={'sentinel':'keep'}
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('mode',['none','matching','nonmatching'])
def test_legacy_rename_entry_exact(controls,representation,kind,mode):
    c=controls;configure_label(c,mode);c.inject(c.target,kind,representation);before=dump(c.db)
    exact_legacy(c,mode,*invoke(c))
    assert dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_does_not_block_rename_entry(controls,representation):
    c=controls;c.inject(c.sibling,'composite',representation);before=dump(c.db)
    exact_legacy(c,'none',*invoke(c))
    assert dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_rename_entry_opaque(controls,representation):
    c=controls;c.inject(c.target,'composite',representation);before=dump(c.db)
    events,state,data=invoke(c,FOREIGN)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text=='این مورد یافت نشد.' and events[0].show_alert
    assert state==CustomConfigFlow.waiting_product_select.state and data=={'sentinel':'keep'}
    assert c.calls==[] and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('restriction',['off','test'])
def test_legacy_rename_entry_restrictions(controls,representation,restriction):
    c=controls;c.inject(c.target,'legacy',representation)
    if restriction=='off': c.db.set_setting('svc_show_rename','0')
    else:
        with c.db._get_conn() as conn: conn.execute("UPDATE custom_configs SET source='test' WHERE id=?",(c.target,))
    before=dump(c.db);events,state,data=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==('این قابلیت غیرفعال است.' if restriction=='off' else 'این قابلیت برای کانفیگ تست در دسترس نیست.')
    assert events[0].show_alert
    assert state==CustomConfigFlow.waiting_product_select.state and data=={'sentinel':'keep'}
    assert c.calls==[] and dump(c.db)==before
