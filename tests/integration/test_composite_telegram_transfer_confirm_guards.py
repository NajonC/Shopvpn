"""T050ab: composite refusal before transfer ownership/history/Telegram effects."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_user
from tests.integration.test_composite_telegram_autorenew_guards import controls, BUYER, FOREIGN, other_tables
from tests.integration.test_composite_telegram_transfer_receive_guards import transfer_control, RECIPIENT
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeCallbackQuery, FakeMessage, FakeUser, TelegramLog, RecordingBot, find_handler, callback_rows

MISSING='این مورد یافت نشد (شاید قبلاً حذف/منتقل شده).'
LIST='📦 سفارش‌ها و کانفیگ‌های شما\n\nیکی از موارد زیر را برای مشاهده‌ی جزئیات انتخاب کنید:'


@pytest.fixture
def confirm_control(transfer_control):
    c=transfer_control
    c.db.add_custom_config_history(c.target,"purchase","synthetic target history")
    c.db.add_custom_config_history(c.sibling,"purchase","synthetic sibling history")
    return c


def invoke(c,uid=BUYER,blocked=False):
    log=TelegramLog();user=FakeUser(uid);msg=FakeMessage(log,uid,from_user=user)
    call=FakeCallbackQuery(log,user,f'svc_transok:x{c.target}:{RECIPIENT}',msg)
    call.bot=RecordingBot(log,blocked_chat_ids=[RECIPIENT] if blocked else [])
    handler=find_handler(handlers_user.create_user_router(c.db),'callback_query','cb_service_transfer_confirm')
    asyncio.run(handler(call))
    return log.events


def assert_legacy(c,blocked=False):
    before=dict(c.db.get_custom_config_owned(c.target,BUYER));sibling=dict(c.db.get_custom_config_owned(c.sibling,BUYER))
    other=other_tables(c.db);history=[dict(r) for r in c.db.get_custom_config_history(c.target)]
    sibling_history=[dict(r) for r in c.db.get_custom_config_history(c.sibling)]
    events=invoke(c,blocked=blocked)
    assert c.db.get_custom_config_owned(c.target,BUYER) is None
    transferred=c.db.get_custom_config_owned(c.target,RECIPIENT)
    assert transferred is not None
    assert dict(transferred)==before|{'user_id':RECIPIENT}
    assert dict(c.db.get_custom_config_owned(c.sibling,BUYER))==sibling
    assert other_tables(c.db)==other and c.calls==[]
    current=[dict(r) for r in c.db.get_custom_config_history(c.target)]
    assert len(current)==len(history)+1 and current[1:]==history
    assert current[0]['custom_config_id']==c.target and current[0]['event_type']=='transfer'
    assert current[0]['detail']==f'از {BUYER} به {RECIPIENT}'
    assert [dict(r) for r in c.db.get_custom_config_history(c.sibling)]==sibling_history
    assert [e.kind for e in events]==['callback_answer','send_message','edit_text']
    assert events[0].text=='✅ کانفیگ منتقل شد.' and events[0].show_alert
    label=before['display_name'] or before['username']
    assert events[1].chat_id==RECIPIENT and events[1].delivered== (not blocked)
    assert events[1].text==(f'📦 یک کانفیگ («{label}») از طرف کاربر دیگری به حساب شما منتقل شد.\n'
                            'برای مشاهده، حساب کاربری ← سرویس‌ها و سفارش‌های من را ببینید.')
    assert events[2].text==LIST
    assert callback_rows(events[2].reply_markup)==[[f'mo_v:x{c.sibling}'],['acct:hub']]
    # Replayed confirmation from the old owner must not repeat history or notification.
    snapshot=dump(c.db);events=invoke(c,blocked=blocked)
    assert dump(c.db)==snapshot and c.calls==[]
    assert [e.kind for e in events]==['callback_answer','edit_text']
    assert events[0].text==MISSING and events[0].show_alert
    assert events[1].text==LIST
    assert callback_rows(events[1].reply_markup)==[[f'mo_v:x{c.sibling}'],['acct:hub']]


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_transfer_confirm_refused(confirm_control,representation,caplog):
    c=confirm_control;c.inject(c.target,'composite',representation);before=dump(c.db)
    events=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert 'SECRET-COMPOSITE' not in str(events)+caplog.text
    assert dump(c.db)==before and c.calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('blocked',[False,True])
@pytest.mark.parametrize('display',[False,True])
def test_legacy_transfer_confirm_exact(confirm_control,representation,kind,blocked,display):
    c=confirm_control
    if display: c.db.rename_custom_config(c.target,BUYER,'Local Label')
    c.inject(c.target,kind,representation);assert_legacy(c,blocked)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_transfer_confirm(confirm_control,representation):
    c=confirm_control;c.inject(c.sibling,'composite',representation);assert_legacy(c)


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_foreign_transfer_confirm_opaque(confirm_control,representation):
    c=confirm_control;c.inject(c.target,'composite',representation);before=dump(c.db)
    events=invoke(c,FOREIGN)
    assert [e.kind for e in events]==['callback_answer','edit_text']
    assert events[0].text==MISSING and events[0].show_alert
    assert events[1].text=='شما تاکنون سفارشی ثبت نکرده‌اید.'
    assert dump(c.db)==before and c.calls==[]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('restriction',['off','test'])
def test_transfer_confirm_restrictions(confirm_control,representation,restriction):
    c=confirm_control;c.inject(c.target,'legacy',representation)
    if restriction=='off': c.db.set_setting('svc_show_transfer','0')
    else:
        with c.db._get_conn() as conn:
            conn.execute("UPDATE custom_configs SET source='test' WHERE id=?",(c.target,))
    before=dump(c.db);events=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==('این قابلیت غیرفعال است.' if restriction=='off' else 'این قابلیت برای کانفیگ تست در دسترس نیست.')
    assert events[0].show_alert and c.calls==[] and dump(c.db)==before
