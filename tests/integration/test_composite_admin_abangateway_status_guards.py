"""T050bn/bo: admin invoice continuation, real verifier/fulfillment/SQL."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests._harness.legacy_bot import FakeMessage, FakeUser, FakeCallbackQuery, TelegramLog, RecordingBot, find_handler
import handlers_admin
import abangateway_payment
import blupal_payment
import abangateway_client
import blupal_client

OWNER=9001
DONE='✅ این پرداخت قبلاً تایید و تحویل داده شده است.'
PRIOR='✅ این سفارش قبلاً بررسی و تحویل داده شده است.'
SUCCESS='✅ پرداخت تایید شد و کانفیگ تحویل داده شد.'


def setup(c, monkeypatch, gateway, representation, kind=None, marker='both', scenario='pending'):
    prepare(c, representation, kind if marker in {'order','both'} else None, kind if marker in {'product','both'} else None)
    c.configure(overrides={c.alpha_id:kind if marker in {'product','both'} else None,c.beta_id:'composite'},representation=representation)
    c.gateway=gateway;c.remote=[];c.verifications=[];c.provisions=[];c.deliveries=[];c.claims=[]
    c.payment={'abangateway':abangateway_payment,'blupal':blupal_payment}[gateway]
    c.client={'abangateway':abangateway_client,'blupal':blupal_client}[gateway]
    c.db.set_setting(gateway+'_api_key','synthetic-key')
    create=getattr(c.db,'create_'+gateway+'_invoice')
    c.other=create('synthetic-decoy','wallet_topup',987,USER_ID,200,2000)
    c.iid=create('synthetic-selected','order',c.oid,USER_ID,900,9000)
    if scenario=='completed':getattr(c.db,'update_'+gateway+'_invoice_status')('synthetic-selected','completed')
    if scenario=='paid_prior':c.db.approve_custom_config_order(c.oid)
    if scenario=='paid_missing_server':
        with c.db._get_conn() as conn:conn.execute('UPDATE orders SET custom_panel_server_id=99999 WHERE id=?',(c.oid,))
    if scenario=='no_key':
        c.db.set_setting(gateway+'_api_key','');monkeypatch.setattr(c.payment,gateway.upper()+'_API_KEY','')
    async def get(key, invoice):
        c.remote.append((key,invoice))
        if scenario=='remote_error':raise (abangateway_client.AbanGatewayError if gateway=='abangateway' else blupal_client.BluPalError)('synthetic outage')
        status='paid' if scenario.startswith('paid_') or scenario in {'already_verified','verify_error','claim_lost'} else scenario
        if gateway=='blupal':status={'cancelled':'CANCELED'}.get(status,status.upper())
        return {'status':status}
    async def verify(key,invoice):
        c.verifications.append((key,invoice))
        if scenario=='already_verified':raise abangateway_client.AbanGatewayAlreadyVerified('synthetic already')
        if scenario=='verify_error':raise abangateway_client.AbanGatewayError('synthetic verify outage')
    monkeypatch.setattr(c.client,'get_invoice',get)
    if gateway=='abangateway':monkeypatch.setattr(c.client,'verify_invoice',verify)
    elif scenario=='claim_lost':
        # Deterministic competing claim through the real SQL method.
        original=c.db.claim_blupal_invoice
        def claim(invoice):
            assert original(invoice)
            return original(invoice)
        monkeypatch.setattr(c.db,'claim_blupal_invoice',claim)
    claim=c.db.claim_order
    def order_claim(oid):c.claims.append(oid);return claim(oid)
    monkeypatch.setattr(c.db,'claim_order',order_claim)
    async def provision(username,volume,days):
        c.provisions.append((username,volume,days))
        if scenario=='paid_provider_error':raise RuntimeError('synthetic panel failure')
        return SimpleNamespace(username=username,subscription_url='https://synthetic.invalid/sub')
    monkeypatch.setattr(c.payment,'get_provider',lambda server:SimpleNamespace(create_user=provision))
    async def deliver(bot,uid,name,links,**kw):c.deliveries.append((uid,name,links,kw))
    monkeypatch.setattr(c.payment,'deliver_config_to_user',deliver)
    c.admin_router=handlers_admin.create_admin_router(c.db,is_main_bot=True)


def invoke(c,uid=OWNER,data=None):
    async def run():
        log=TelegramLog();user=FakeUser(uid);call=FakeCallbackQuery(log,user,data or f'check_{c.gateway}_invoice:{c.iid}',FakeMessage(log,uid,from_user=user))
        await find_handler(c.admin_router,'callback_query','cb_check_'+c.gateway+'_invoice')(call,RecordingBot(log))
        return log.events
    return asyncio.run(run())


def composite(catalog,monkeypatch,representation,marker,scenario,gateway,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario)
    before=dump(c.db);events=invoke(c)
    assert c.remote==[] and c.verifications==[] and c.claims==[] and c.provisions==[] and c.deliveries==[] and dump(c.db)==before
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert
    assert 'composite' in (events[0].text or '').lower()
    assert all(s not in str(events)+caplog.text for s in ['synthetic-key','synthetic-selected','newname'])


def legacy(catalog,monkeypatch,representation,kind,scenario,gateway):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,scenario=scenario)
    old=dict(c.db.get_order(c.oid));other=dict(getattr(c.db,'get_'+gateway+'_invoice')(c.other));wallet=c.db.get_wallet_credit(USER_ID)
    events=invoke(c)
    expected=SUCCESS if scenario=='paid_success' else PRIOR if scenario=='paid_prior' else '⛔️ سرور مربوط به کانفیگ شخصی یافت نشد؛ با پشتیبانی تماس بگیرید.' if scenario=='paid_missing_server' else '⛔️ خطا در ساخت کانفیگ روی پنل: synthetic panel failure\nبا پشتیبانی تماس بگیرید.' if scenario=='paid_provider_error' else DONE if scenario in {'completed','already_verified','claim_lost'} else '❌ اعتبار این فاکتور تمام شده یا لغو شده است.' if scenario in {'expired','cancelled'} else '⚠️ خطا در بررسی وضعیت: synthetic outage' if scenario=='remote_error' else '⚠️ خطا در بررسی وضعیت: synthetic verify outage' if scenario=='verify_error' else '⚠️ خطا در بررسی وضعیت: کلید API '+('آبان گیت وی' if gateway=='abangateway' else 'بلوپال')+' تنظیم نشده است.' if scenario=='no_key' else '⏳ هنوز واریزی برای این فاکتور تایید نشده.'
    assert [e.kind for e in events]==['callback_answer','message_answer'] and events[0].text=='در حال بررسی...' and not events[0].show_alert and events[1].text==expected
    assert c.remote==([] if scenario in {'completed','no_key'} else [('synthetic-key','synthetic-selected')])
    assert c.verifications==([('synthetic-key','synthetic-selected')] if gateway=='abangateway' and (scenario.startswith('paid_') or scenario in {'already_verified','verify_error'}) else [])
    assert c.claims==([c.oid] if scenario in {'paid_success','paid_missing_server','paid_provider_error'} else [])
    assert c.provisions==([('newname',10,30)] if scenario in {'paid_success','paid_provider_error'} else [])
    after=dict(c.db.get_order(c.oid))
    assert after['status']==('approved' if scenario in {'paid_success','paid_prior'} else 'pending')
    for k in old:
        if k not in {'status','updated_at'}:assert after[k]==old[k]
    if scenario=='paid_success':
        assert c.deliveries==[(USER_ID,'کانفیگ شخصی',['https://synthetic.invalid/sub'],{'final_price':900,'order_id':c.oid,'db':c.db})]
        with c.db._get_conn() as conn:
            rows=conn.execute('SELECT * FROM custom_configs WHERE order_id=?',(c.oid,)).fetchall()
        assert len(rows)==1 and rows[0]['username']=='newname' and rows[0]['volume_gb']==10 and rows[0]['duration_days']==30 and rows[0]['subscription_url']=='https://synthetic.invalid/sub'
    else:assert c.deliveries==[]
    assert c.db.get_wallet_credit(USER_ID)==wallet and dict(getattr(c.db,'get_'+gateway+'_invoice')(c.other))==other
    status='completed' if scenario.startswith('paid_') or scenario in {'completed','already_verified','claim_lost'} else scenario if scenario in {'expired','cancelled'} else 'pending' if scenario=='partially_paid' and gateway=='abangateway' else 'new'
    assert getattr(c.db,'get_'+gateway+'_invoice')(c.iid)['status']==status
    if status=='completed':
        before=dump(c.db);counts=(len(c.remote),len(c.verifications),len(c.claims),len(c.provisions),len(c.deliveries))
        assert invoke(c)[1].text==DONE and dump(c.db)==before
        assert counts==(len(c.remote),len(c.verifications),len(c.claims),len(c.provisions),len(c.deliveries))


def opaque(catalog,monkeypatch,representation,failure,gateway):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite')
    before=dump(c.db);data=f'check_{gateway}_invoice:invalid' if failure=='malformed' else f'check_{gateway}_invoice:99999' if failure=='missing' else None
    events=invoke(c,USER_ID if failure=='unauthorized' else OWNER,data)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==(None if failure=='unauthorized' else '❌ درخواست نامعتبر است.' if failure=='malformed' else 'فاکتور یافت نشد.') and events[0].show_alert==(failure!='unauthorized')
    assert not c.remote and not c.verifications and not c.claims and dump(c.db)==before


def topup(catalog,monkeypatch,representation,gateway):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',scenario='paid_success')
    tid=c.db.create_topup(USER_ID,321)
    c.iid=getattr(c.db,'create_'+gateway+'_invoice')('synthetic-topup','wallet_topup',tid,USER_ID,321,3210)
    old=dict(c.db.get_order(c.oid));wallet=c.db.get_wallet_credit(USER_ID)
    events=invoke(c)
    assert events[1].text=='✅ پرداخت تایید شد و 321 تومان به کیف پول کاربر اضافه شد.' and events[0].text=='در حال بررسی...'
    assert c.db.get_wallet_credit(USER_ID)==wallet+321 and c.db.get_topup(tid)['status']=='approved'
    assert dict(c.db.get_order(c.oid))==old and not c.claims and not c.provisions and not c.deliveries
    assert c.remote==[('synthetic-key','synthetic-topup')]
    assert c.verifications==([('synthetic-key','synthetic-topup')] if gateway=='abangateway' else [])
    before=dump(c.db);assert invoke(c)[1].text==DONE and dump(c.db)==before and len(c.remote)==1


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['pending','expired','paid_success','completed'])
def test_composite_admin_aban_refused(catalog,monkeypatch,representation,marker,scenario,caplog):
    composite(catalog,monkeypatch,representation,marker,scenario,'abangateway',caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['pending','partially_paid','expired','cancelled','completed','remote_error','already_verified','verify_error','no_key','paid_prior','paid_missing_server','paid_provider_error','paid_success'])
def test_legacy_admin_aban_exact(catalog,monkeypatch,representation,kind,scenario):
    legacy(catalog,monkeypatch,representation,kind,scenario,'abangateway')

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('failure',['malformed','missing','unauthorized'])
def test_admin_aban_opaque(catalog,monkeypatch,representation,failure):opaque(catalog,monkeypatch,representation,failure,'abangateway')

@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_admin_aban_topup(catalog,monkeypatch,representation):topup(catalog,monkeypatch,representation,'abangateway')
