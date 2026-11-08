"""T050br/bs: upstream catalog status, actual dispatch/provision/SQLite."""
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_admin
import abangateway_client
import blupal_client
from tests.integration.test_composite_gateway_auto_guards import catalog, auto_catalog, balance
from tests.integration.test_composite_gateway_stock_guards import setup as stock_setup, rows, LINKS, REFERRER, USER_ID, dump
from tests.integration.test_composite_gateway_direct_guards import setup as direct_setup, configs, LINK
from tests.integration.test_composite_gateway_auto_guards import setup as auto_setup
from tests.integration.test_composite_gateway_pool_renewal_guards import setup as renewal_setup, RENEWED
from tests.integration.test_composite_admin_abangateway_status_guards import invoke, DONE, SUCCESS, OWNER
BRANCHES=['stock','direct','auto','renewal']


def setup(c,mp,gateway,representation,branch,kind=None,marker='both',scenario='paid'):
    import reseller_auto_provision
    mp.setattr(reseller_auto_provision,'MAIN_DB_PATH',c.main.db_path)
    local='shortage' if branch=='stock' else 'second' if branch in {'direct','auto'} else 'foreign'
    local=local if scenario=='fulfillment_failure' else 'prior' if scenario=='prior' else 'success'
    if branch=='renewal':renewal_setup(c,mp,gateway+'_payment',representation,kind,marker,scenario=local)
    else:{'stock':stock_setup,'direct':direct_setup,'auto':auto_setup}[branch](c,mp,gateway+'_payment',representation,kind,marker,scenario=local)
    c.gateway=gateway;c.remote=[];c.verifications=[]
    c.db.set_setting(gateway+'_api_key','synthetic-key')
    create=getattr(c.db,'create_'+gateway+'_invoice')
    c.decoy=create('synthetic-decoy','order',99999,USER_ID,999,9990)
    c.iid=create('synthetic-selected','order',c.oid,USER_ID,900,9000)
    if scenario=='completed':getattr(c.db,'update_'+gateway+'_invoice_status')('synthetic-selected','completed')
    client=abangateway_client if gateway=='abangateway' else blupal_client
    async def get(key,invoice):
        c.remote.append((key,invoice))
        if scenario=='remote_error':raise client.AbanGatewayError('synthetic outage') if gateway=='abangateway' else client.BluPalError('synthetic outage')
        status='paid' if scenario in {'paid','prior','fulfillment_failure','claim_lost'} else scenario
        return {'status':({'cancelled':'CANCELED'}.get(status,status.upper()) if gateway=='blupal' else status)}
    async def verify(key,invoice):c.verifications.append((key,invoice))
    mp.setattr(client,'get_invoice',get)
    if gateway=='abangateway':mp.setattr(client,'verify_invoice',verify)
    if scenario=='claim_lost':
        original=c.db.claim_blupal_invoice
        def compete(invoice):
            assert original(invoice)
            return original(invoice)
        mp.setattr(c.db,'claim_blupal_invoice',compete)
    c.admin_router=handlers_admin.create_admin_router(c.db,is_main_bot=True)
    c.trace.clear()


def composite(c,mp,gateway,representation,branch,marker,scenario,caplog):
    setup(c,mp,gateway,representation,branch,'composite',marker,scenario)
    before=(dump(c.db),dump(c.main));events=invoke(c)
    assert not c.remote and not c.verifications and not c.trace and (dump(c.db),dump(c.main))==before
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert and 'composite' in (events[0].text or '').lower()
    assert all(secret not in str(events)+caplog.text for secret in ['synthetic-key','synthetic-selected','fake_pass_1',LINK])


def legacy(c,mp,gateway,representation,branch,kind,scenario):
    setup(c,mp,gateway,representation,branch,kind,scenario=scenario)
    before=(dump(c.db),dump(c.main));stock=rows(c);credit=balance(c);decoy=dict(getattr(c.db,'get_'+gateway+'_invoice')(c.decoy))
    events=invoke(c)
    answers=[e for e in events if e.kind=='message_answer']
    assert len(answers)==1 and events[0].kind=='callback_answer' and events[0].text=='در حال بررسی...' and not events[0].show_alert
    success=scenario=='paid';failure=scenario=='fulfillment_failure'
    expected=DONE if scenario in {'completed','claim_lost'} else '✅ این سفارش قبلاً بررسی و تحویل داده شده است.' if scenario=='prior' else '❌ اعتبار این فاکتور تمام شده یا لغو شده است.' if scenario in {'expired','cancelled'} else '⚠️ خطا در بررسی وضعیت: synthetic outage' if scenario=='remote_error' else '⏳ هنوز واریزی برای این فاکتور تایید نشده.' if scenario=='pending' else RENEWED if branch=='renewal' and success else SUCCESS
    if failure:
        assert answers[0].text.startswith('⚠️ پرداخت تایید شد ولی '+('موجودی' if branch=='stock' else 'ساخت خودکار') if branch!='renewal' else '⛔️ تمدید ناموفق بود:')
    else:assert answers[0].text==expected
    assert c.remote==([] if scenario=='completed' else [('synthetic-key','synthetic-selected')])
    assert c.verifications==([('synthetic-key','synthetic-selected')] if gateway=='abangateway' and scenario in {'paid','prior','fulfillment_failure'} else [])
    selected=getattr(c.db,'get_'+gateway+'_invoice')(c.iid)
    assert selected['status']==('completed' if scenario in {'paid','prior','fulfillment_failure','completed','claim_lost'} else scenario if scenario in {'expired','cancelled'} else 'new')
    assert dict(getattr(c.db,'get_'+gateway+'_invoice')(c.decoy))==decoy
    if success:
        assert c.db.get_order(c.oid)['status']=='approved'
        assert c.trace[0]==('claim_order',(c.oid,),{})
        assert not any(e[0]=='admin' for e in c.trace)
        if branch=='renewal':
            assert rows(c)[0]['expires_at']=='2030-01-11T00:00:00' and rows(c)[1:]==stock[1:]
            assert c.db.get_wallet_credit(REFERRER)==0 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
            assert ('extend_pool_config_expiry',(c.target,USER_ID,10),{}) in c.trace
        else:
            links=LINKS[:2] if branch=='stock' else [LINK+u for u in (['chosen_1','chosen_2'] if branch=='direct' else ['r1','r2'])]
            assert ('delivery',USER_ID,branch.title(),links,dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
            assert ('reward_referrer_if_first_purchase',(USER_ID,1000),{}) in c.trace
            assert c.db.get_wallet_credit(REFERRER)==130 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==1
            if branch=='stock':
                assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:2]) and rows(c)[2:]==stock[2:]
            else:
                entries=configs(c);assert len(entries)==2
                for row,url in zip(entries,links):
                    assert row['user_id']==USER_ID and row['order_id']==c.oid and row['volume_gb']==10 and row['duration_days']==17 and row['subscription_url']==url
                    assert len(c.db.get_custom_config_history(row['id']))==1
            if branch=='auto':assert balance(c)==(credit[0]-20,credit[1])
        assert c.db.get_wallet_credit(USER_ID)==0
    elif failure:
        assert c.db.get_order(c.oid)['status']=='pending' and c.trace[-1]==('release_order_claim',(c.oid,),{})
        assert rows(c)==stock and configs(c)==[] and balance(c)==credit
        assert c.db.get_wallet_credit(REFERRER)==0 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
        if branch in {'direct','auto'}:assert ('delete','chosen_1' if branch=='direct' else 'r1') in c.trace
    else:
        assert not c.trace and balance(c)==credit and rows(c)==stock
    if selected['status']=='completed':
        state=(dump(c.db),dump(c.main));counts=(len(c.remote),len(c.verifications));c.trace.clear()
        assert invoke(c)[1].text==DONE and (dump(c.db),dump(c.main))==state and not c.trace and counts==(len(c.remote),len(c.verifications))


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['pending','expired','paid','completed'])
def test_composite_aban_catalog(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog):
    composite(auto_catalog,monkeypatch,'abangateway',representation,branch,marker,scenario,caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['paid','prior','fulfillment_failure','pending','expired','cancelled','remote_error','completed'])
def test_legacy_aban_catalog(auto_catalog,monkeypatch,representation,branch,kind,scenario):
    legacy(auto_catalog,monkeypatch,'abangateway',representation,branch,kind,scenario)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',BRANCHES)
@pytest.mark.parametrize('failure',['unauthorized','malformed','missing'])
def test_aban_catalog_opaque(auto_catalog,monkeypatch,representation,branch,failure):
    opaque(auto_catalog,monkeypatch,'abangateway',representation,branch,failure)


def opaque(c,mp,gateway,representation,branch,failure):
    setup(c,mp,gateway,representation,branch,'composite','order')
    before=(dump(c.db),dump(c.main))
    events=invoke(c,USER_ID if failure=='unauthorized' else OWNER,f'check_{gateway}_invoice:'+('bad' if failure=='malformed' else '99999') if failure!='unauthorized' else None)
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].text==(None if failure=='unauthorized' else '❌ درخواست نامعتبر است.' if failure=='malformed' else 'فاکتور یافت نشد.')
    assert not c.remote and not c.verifications and not c.trace and (dump(c.db),dump(c.main))==before
