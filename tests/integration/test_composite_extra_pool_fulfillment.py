"""T050er/es: actual extra deliver -> pool renewal engine -> expiry SQL."""
import pytest
from tests.integration.test_composite_gateway_pool_renewal_guards import (
    catalog, USER_ID, RENEWED, PRIOR, rows, names, dump, setup as pool_setup,
)
from tests.integration.test_composite_extra_direct_fulfillment import invoke
GATEWAYS=['zarinpal','tgstars']

def setup(c,mp,gateway,representation,kind=None,marker='all',mode='time',expiry='future',scenario='success'):
    pool_setup(c,mp,'abangateway_payment',representation,kind,marker,mode,expiry,scenario)
    c.gateway=gateway
    c.db.create_extra_invoice(gateway,'order',99998,USER_ID,1)
    c.db.create_extra_invoice(gateway,'order',99997,USER_ID,1)
    iid=c.db.create_extra_invoice(gateway,'order',c.oid,USER_ID,900)
    assert iid != c.oid
    c.invoice=c.db.get_extra_invoice(iid)

@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','target','product'])
@pytest.mark.parametrize('scenario',['success','prior','approve_renewal_order'])
def test_composite_pool_refused_before_claim(catalog,monkeypatch,gateway,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario=scenario)
    before=dump(c.db)
    try:text=invoke(c)
    except RuntimeError as e:text=str(e)
    assert not c.trace and dump(c.db)==before
    assert 'composite' in text.lower()
    assert all(s not in text+caplog.text for s in ['https://subscription.example.invalid/stock-0','fake_pass_1'])



@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('mode',['time','full','volume'])
@pytest.mark.parametrize('expiry',['future','expired'])
def test_legacy_pool_success_repeat(catalog,monkeypatch,gateway,representation,kind,mode,expiry):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,mode=mode,expiry=expiry)
    before=rows(c);wallet=c.db.get_wallet_credit(USER_ID)
    assert invoke(c)==RENEWED
    days={'time':10,'full':30,'volume':0}[mode]
    assert c.trace==[('claim_order',(c.oid,),{}),('extend_pool_config_expiry',(c.target,USER_ID,days),{}),('approve_renewal_order',(c.oid,),{}),('send',USER_ID,RENEWED,'approved'),('admin',c.oid)]
    after=rows(c);expected=dict(before[0]);expected['expires_at']=('2030-01-'+('11' if days==10 else '31' if days==30 else '01')+'T00:00:00' if expiry=='future' else {10:'2026-11-18T12:00:00',30:'2026-12-08T12:00:00',0:'2026-11-08T12:00:00'}[days])
    assert after==[expected,*before[1:]]
    assert c.db.get_order(c.oid)['status']=='approved'
    assert c.db.get_wallet_credit(USER_ID)==wallet and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
    before_sql=dump(c.db);c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and dump(c.db)==before_sql


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('scenario',['extend_pool_config_expiry','approve_renewal_order','send','admin','no_admin','prior','lost_claim','foreign','missing_target','missing'])
def test_legacy_pool_failure_boundaries(catalog,monkeypatch,gateway,representation,scenario):
    c=catalog;setup(c,monkeypatch,gateway,representation,scenario=scenario)
    before=rows(c)
    if scenario=='missing':c.oid=99999
    if scenario=='approve_renewal_order':
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    else:
        text=invoke(c)
        assert text==('⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else '⛔️ تمدید ناموفق بود: این سرویس دیگر یافت نشد (شاید قبلاً حذف شده).\nبا پشتیبانی تماس بگیرید.' if scenario in {'foreign','missing_target'} else '⛔️ خطای غیرمنتظره‌ای در تمدید رخ داد. سفارش برای بررسی دوباره آزاد شد؛ با پشتیبانی تماس بگیرید.' if scenario=='extend_pool_config_expiry' else RENEWED)
    full=['claim_order','extend_pool_config_expiry','approve_renewal_order','send','admin']
    expected=[] if scenario in {'prior','missing'} else ['claim_order'] if scenario=='lost_claim' else full[:2]+['release_order_claim'] if scenario in {'foreign','missing_target','extend_pool_config_expiry'} else full[:3] if scenario=='approve_renewal_order' else full[:4] if scenario=='no_admin' else full
    assert names(c)==expected
    updated=scenario in {'approve_renewal_order','send','admin','no_admin'}
    if updated:
        expected=dict(before[0]);expected['expires_at']='2030-01-11T00:00:00'
        assert rows(c)==[expected,*before[1:]]
    else:assert rows(c)==before
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
    if scenario!='missing':
        with c.db._get_conn() as conn:status=conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]
        assert status==('approved' if scenario in {'prior','send','admin','no_admin'} else 'processing' if scenario in {'lost_claim','approve_renewal_order'} else 'pending')
