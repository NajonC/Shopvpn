"""T050aw: real Noapay status continuation with synthetic remote boundary."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog,USER_ID
import noapay_payment as payment
import noapay_client as client
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage,FakeUser,FakeCallbackQuery,TelegramLog,find_handler

CHECK='در حال بررسی وضعیت پرداخت...'
PENDING='⏳ هنوز واریزی برای این فاکتور تایید نشده. کمی صبر کن و دوباره بررسی کن.'
EXPIRED='❌ اعتبار این فاکتور تمام شده یا رد شده. لطفاً دوباره از منو اقدام کن.'
DONE='✅ این پرداخت قبلاً تایید و تحویل داده شده است.'
PRIOR='✅ این سفارش قبلاً بررسی و تحویل داده شده است.'


def setup(c,monkeypatch,representation,kind=None,marker='both',scenario='pending'):
    prepare(c,representation,kind if marker in {'order','both'} else None,kind if marker in {'product','both'} else None)
    c.db.set_setting('noapay_api_key','synthetic-key')
    c.remote=[];c.verifications=[];c.claims=[]
    create=c.db.create_noapay_invoice
    c.other=create('synthetic-decoy','wallet_topup',987,USER_ID,200,2000)
    c.iid=create('synthetic-selected','order',c.oid,USER_ID,900,9000)
    c.scenario=scenario
    if scenario=='completed':c.db.update_noapay_invoice_status('synthetic-selected','completed')
    if scenario=='verified_prior':c.db.approve_custom_config_order(c.oid)
    if scenario!='verified_prior':
        with c.db._get_conn() as conn:conn.execute('UPDATE orders SET custom_panel_server_id=? WHERE id=?',(99999,c.oid))
    async def get(key,invoice):
        c.remote.append((key,invoice))
        if scenario=='remote_error':raise client.NoapayError('synthetic outage')
        return {'status': 'completed' if scenario.startswith('verified_') else scenario}
    monkeypatch.setattr(client,'get_invoice',get)
    original=c.db.claim_order
    def claim(oid):
        c.claims.append(oid);return original(oid)
    c.db.claim_order=claim


def invoke(c,data=None,uid=USER_ID):
    async def run():
        log=TelegramLog();u=FakeUser(uid);msg=FakeMessage(log,uid,from_user=u)
        call=FakeCallbackQuery(log,u,data or f'check_noapay:{c.iid}',msg)
        await find_handler(c.router,'callback_query','cb_check_noapay')(call,SimpleNamespace())
        return log.events
    return asyncio.run(run())


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['pending','expired','verified_prior'])
def test_composite_custom_status_refused(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db);events=invoke(c)
    assert c.remote==[] and c.verifications==[] and c.claims==[] and dump(c.db)==before
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert
    assert 'composite' in (events[0].text or '').lower()
    assert all(v not in str(events)+caplog.text for v in ['synthetic-key','synthetic-selected','newname'])


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['pending','opened','paid','confirmed','expired','rejected','completed','remote_error','verified_prior','verified_missing_server'])
def test_legacy_status_exact(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    c.configure(overrides={c.alpha_id:kind,c.beta_id:'composite'},representation=representation)
    before=dict(c.db.get_order(c.oid));other=dict(c.db.get_noapay_invoice(c.other));selected=dict(c.db.get_noapay_invoice(c.iid));wallet=c.db.get_wallet_credit(USER_ID)
    events=invoke(c)
    expected=EXPIRED if scenario in {'expired','rejected'} else DONE if scenario=='completed' else '⚠️ خطا در بررسی وضعیت: synthetic outage' if scenario=='remote_error' else PRIOR if scenario=='verified_prior' else '⛔️ سرور مربوط به کانفیگ شخصی یافت نشد؛ با پشتیبانی تماس بگیرید.' if scenario=='verified_missing_server' else PENDING
    assert [e.kind for e in events]==['callback_answer','message_answer'] and events[0].text==CHECK and not events[0].show_alert and events[1].text==expected
    assert c.remote==([] if scenario=='completed' else [('synthetic-key','synthetic-selected')])
    assert c.verifications==[]
    assert c.claims==([c.oid] if scenario=='verified_missing_server' else [])
    after=dict(c.db.get_order(c.oid))
    for key in before:
        if key!='updated_at':assert after[key]==before[key]
    assert c.db.get_wallet_credit(USER_ID)==wallet and dict(c.db.get_noapay_invoice(c.other))==other
    now=dict(c.db.get_noapay_invoice(c.iid))
    expected_status='completed' if scenario.startswith('verified_') else scenario if scenario in {'pending','opened','paid','confirmed','expired','rejected','completed'} else 'new'
    assert now['status']==expected_status
    for key in selected:
        if key not in {'status','updated_at'}:assert now[key]==selected[key]
    if expected_status=='completed':
        before_repeat=dump(c.db);counts=(len(c.remote),len(c.verifications),len(c.claims))
        again=invoke(c)
        assert again[1].text==DONE and dump(c.db)==before_repeat and counts==(len(c.remote),len(c.verifications),len(c.claims))


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['malformed','missing','foreign'])
def test_status_opaque_refusals(catalog,monkeypatch,representation,failure):
    c=catalog;setup(c,monkeypatch,representation,'composite')
    before=dump(c.db);data='check_noapay:invalid' if failure=='malformed' else 'check_noapay:99999' if failure=='missing' else None
    events=invoke(c,data,USER_ID+1 if failure=='foreign' else USER_ID)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert and events[0].text==('داده نامعتبر.' if failure=='malformed' else 'فاکتور یافت نشد.')
    assert not c.remote and not c.verifications and not c.claims and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_wallet_topup_status_retains_exact_credit(catalog,monkeypatch,representation):
    c=catalog;setup(c,monkeypatch,representation,'composite',scenario='verified_prior')
    topup=c.db.create_topup(USER_ID,321)
    c.iid=c.db.create_noapay_invoice('synthetic-topup','wallet_topup',topup,USER_ID,321,3210)
    before_order=dict(c.db.get_order(c.oid));before_wallet=c.db.get_wallet_credit(USER_ID)
    events=invoke(c)
    assert [e.kind for e in events]==['callback_answer','message_answer'] and events[0].text==CHECK
    assert events[1].text=='✅ پرداخت تایید شد و 321 تومان به کیف پول کاربر اضافه شد.'
    assert c.remote==[('synthetic-key','synthetic-topup')] and c.verifications==[]
    assert c.db.get_topup(topup)['status']=='approved' and c.db.get_wallet_credit(USER_ID)==before_wallet+321
    assert dict(c.db.get_order(c.oid))==before_order and not c.claims
    before=dump(c.db);again=invoke(c)
    assert again[1].text==DONE and dump(c.db)==before
    assert c.remote==[('synthetic-key','synthetic-topup')] and c.verifications==[]
