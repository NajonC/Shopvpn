"""T050at: shared automatic-card status uses the owned invoice's actual order."""
import asyncio
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_telegram_custom_card_auto_guards import prepare
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, FakeCallbackQuery, TelegramLog, find_handler

DONE = "✅ این پرداخت قبلاً تایید و تحویل داده شده است."
REVIEW = "⏳ مهلت این مبلغ تمام شده و برای بررسی دستی به ادمین ارسال شد."
PENDING = "⏳ هنوز پیامک بانک برای این مبلغ دریافت نشده. کمی صبر کن."


def setup(c, representation, marker=None, status="pending", stale=False):
    prepare(c, representation, 'composite' if marker=='order' else 'legacy', 'composite' if marker=='product' else 'legacy')
    card=c.db.list_card_to_card_cards()[0]['id']
    # Deliberately make invoice identity different from order identity.
    c.other=c.db.create_card_to_card_invoice(card,'wallet',987,USER_ID,200,201,'2000-01-01')
    c.iid=c.db.create_card_to_card_invoice(card,'order',c.oid,USER_ID,900,901,'2000-01-01' if stale else '2999-01-01')
    with c.db._get_conn() as conn:
        conn.execute('UPDATE card_to_card_invoices SET status=? WHERE id=?',(status,c.iid))
    c.maintenance=[]
    original=c.db.expire_stale_card_to_card_invoices
    def maintain():
        c.maintenance.append(True)
        return original()
    c.db.expire_stale_card_to_card_invoices=maintain


def invoke(c, data=None, uid=USER_ID):
    async def run():
        log=TelegramLog();user=FakeUser(uid);msg=FakeMessage(log,uid,from_user=user)
        call=FakeCallbackQuery(log,user,data or f'check_c2c:{c.iid}',msg)
        await find_handler(c.router,'callback_query','cb_check_card_auto')(call)
        return log.events
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status,stale',[('pending',False),('pending',True),('completed',False),('manual_review',False)])
def test_composite_card_status_refused(catalog,representation,marker,status,stale,caplog):
    c=catalog;setup(c,representation,marker,status,stale)
    before=dump(c.db);events=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert 'composite' in (events[0].text or '').lower()
    assert events[0].show_alert
    assert not c.maintenance and dump(c.db)==before
    assert 'FAKE-CARD-NUMBER' not in str(events)+caplog.text and 'newname' not in str(events)+caplog.text


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('status,stale,expected',[('pending',False,PENDING),('pending',True,REVIEW),('completed',True,DONE),('manual_review',True,REVIEW)])
def test_legacy_card_status_and_global_expiry(catalog,representation,kind,status,stale,expected):
    c=catalog;setup(c,representation,None,status,stale)
    # Missing and explicit discriminators remain compatible; unrelated composite ignored.
    c.configure(overrides={c.alpha_id:kind,c.beta_id:'composite'},representation=representation)
    order_before=dict(c.db.get_order(c.oid));wallet=c.db.get_wallet_credit(USER_ID)
    selected_before=dict(c.db.get_card_to_card_invoice(c.iid));other_before=dict(c.db.get_card_to_card_invoice(c.other))
    events=invoke(c)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].text==expected and events[0].show_alert
    assert c.maintenance==[True]
    assert dict(c.db.get_order(c.oid))==order_before and c.db.get_wallet_credit(USER_ID)==wallet
    selected=dict(c.db.get_card_to_card_invoice(c.iid));other=dict(c.db.get_card_to_card_invoice(c.other))
    new_status='manual_review' if status=='pending' and stale else status
    assert selected['status']==new_status and other['status']=='manual_review'
    for key in selected_before:
        if key not in {'status','updated_at'}:assert selected[key]==selected_before[key]
    for key in other_before:
        if key not in {'status','updated_at'}:assert other[key]==other_before[key]
    if new_status==status:assert selected==selected_before
    else:assert selected['updated_at']!=selected_before['updated_at']
    assert other['updated_at']!=other_before['updated_at']
    before=dump(c.db);again=invoke(c)
    assert again[0].text==expected and dump(c.db)==before and c.maintenance==[True,True]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['malformed','missing','foreign'])
def test_card_status_opaque_refusals(catalog,representation,failure):
    c=catalog;setup(c,representation,'order',stale=True)
    before=dump(c.db)
    data='check_c2c:invalid' if failure=='malformed' else 'check_c2c:999999' if failure=='missing' else None
    events=invoke(c,data,USER_ID+1 if failure=='foreign' else USER_ID)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert
    assert events[0].text==('داده نامعتبر.' if failure=='malformed' else 'فاکتور یافت نشد.')
    assert not c.maintenance and dump(c.db)==before
