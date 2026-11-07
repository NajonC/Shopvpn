"""T050an: custom receipt refuses composites before persistence/admin delivery."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare,data
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,FakeFile,RecordingBot,TelegramLog,find_handler,make_state,callback_rows
from states import CustomConfigFlow


def invoke(c,kind='photo',blocked=False):
    async def run():
        state=make_state(USER_ID);await state.set_state(CustomConfigFlow.waiting_receipt);await state.set_data(data(c))
        log=TelegramLog();bot=RecordingBot(log,blocked_chat_ids=[9001] if blocked else [])
        c.files=[]
        for name in ['send_photo','send_document']:
            original=getattr(bot,name)
            async def capture(chat_id,file_id,_name=name,_original=original,**kwargs):
                row=c.db.get_order(c.oid)
                c.files.append((_name,chat_id,file_id,row['receipt_file_id'],row['receipt_type']))
                return await _original(chat_id,file_id,**kwargs)
            setattr(bot,name,capture)
        msg=FakeMessage(log,USER_ID,from_user=FakeUser(USER_ID),photo=[FakeFile('small'),FakeFile('synthetic-photo')] if kind in {'photo','both'} else None,document=FakeFile('synthetic-document') if kind in {'document','both'} else None)
        await find_handler(c.router,'message','receive_custom_config_receipt')(msg,state,bot)
        return log.events,await state.get_state(),await state.get_data()
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('kind',['photo','document'])
def test_composite_custom_receipt_refused(catalog,representation,marker,kind,caplog):
    c=catalog;prepare(c,representation,'composite' if marker=='order' else None,'composite' if marker=='product' else None)
    before=dump(c.db);events,state,stored=invoke(c,kind)
    assert dump(c.db)==before and c.files==[]
    assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    assert len(events)==1 and 'composite' in (events[0].text or '').lower()
    assert all(v not in str(events)+caplog.text for v in ['newname','synthetic-photo','synthetic-document','FAKE-CARD-NUMBER'])


def check_success(c,kind,blocked=False):
    before=dict(c.db.get_order(c.oid));events,state,stored=invoke(c,kind,blocked)
    typ='photo' if kind in {'photo','both'} else 'document';file_id='synthetic-'+typ
    assert c.files==[('send_'+typ,9001,file_id,file_id,typ)]
    assert state is None and stored=={}
    row=dict(c.db.get_order(c.oid))
    assert (row['receipt_file_id'],row['receipt_type'],row['status'],row['final_price'])==(file_id,typ,'pending',900)
    changed={k for k in row if row[k]!=before[k]}
    assert changed <= {'receipt_file_id','receipt_type','admin_chat_id','admin_message_id'}
    assert [e.kind for e in events]==['send_'+typ,'message_answer']
    admin=events[0]
    assert admin.chat_id==9001 and admin.delivered== (not blocked)
    assert admin.text==f'🧾 سفارش کانفیگ شخصی #{c.oid}\n👤 کاربر: Test (@testuser)\n🆔 آیدی عددی: {USER_ID}\n🛠 نام کاربری: newname\n📶 حجم: 10 گیگابایت\n💰 قیمت پایه: 1,000 تومان\n👛 استفاده از کیف پول: 100 تومان\n💵 مبلغ قابل پرداخت: 900 تومان'
    assert callback_rows(admin.reply_markup)==[[f'order_approve:{c.oid}',f'order_reject:{c.oid}']]
    if not blocked:assert (row['admin_chat_id'],row['admin_message_id'])==(9001,admin.message_id)
    else:assert row['admin_chat_id']==before['admin_chat_id'] and row['admin_message_id']==before['admin_message_id']
    assert events[1].chat_id==USER_ID and events[1].text=='✅ رسید شما برای بررسی ارسال شد. پس از تایید ادمین، کانفیگ شخصی شما ساخته و ارسال خواهد شد.'
    assert events[1].reply_markup is not None


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',['photo','document','both'])
@pytest.mark.parametrize('marker',[None,'legacy'])
def test_legacy_custom_receipt_exact(catalog,representation,kind,marker):
    c=catalog;prepare(c,representation,marker,marker);check_success(c,kind)
    # A fresh FSM entry may overwrite the receipt and notify again: legacy behavior.
    check_success(c,'document')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_composite_sibling_allows_custom_receipt(catalog,representation):
    c=catalog;prepare(c,representation);c.configure(overrides={c.beta_id:'composite'},representation=representation);check_success(c,'photo')


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_blocked_admin_custom_receipt(catalog,representation):
    c=catalog;prepare(c,representation);check_success(c,'document',True)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['missing','approved','no_file'])
def test_legacy_custom_receipt_refusals(catalog,representation,failure):
    c=catalog;prepare(c,representation)
    if failure=='missing':c.oid=99999
    elif failure=='approved':c.db.approve_custom_config_order(c.oid)
    before=dump(c.db);events,state,stored=invoke(c,'none' if failure=='no_file' else 'photo')
    assert dump(c.db)==before and c.files==[]
    assert len(events)==1 and events[0].kind=='message_answer'
    assert events[0].text==('لطفاً عکس یا فایل رسید پرداخت را ارسال کنید.' if failure=='no_file' else 'سفارش معتبر یافت نشد. لطفاً دوباره از منو شروع کنید.')
    if failure=='no_file':assert state==CustomConfigFlow.waiting_receipt.state and stored==data(c)
    else:assert state is None and stored=={}
