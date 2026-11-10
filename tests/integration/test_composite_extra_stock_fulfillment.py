"""T050ep/eq: real extra deliver -> shared STOCK -> allocation, alert, reward SQL."""
from datetime import datetime
import pytest
from tests.integration.test_composite_gateway_stock_guards import (
    catalog, USER_ID, REFERRER, SUCCESS, PRIOR, LINKS, dump, names, rows,
    setup as stock_setup,
)
from tests.integration.test_composite_extra_direct_fulfillment import invoke
GATEWAYS=['zarinpal','tgstars']

def setup(c,mp,gateway,representation,kind=None,marker='both',scenario='success',quantity=2):
    stock_setup(c,mp,'abangateway_payment',representation,kind,marker,scenario,quantity)
    c.gateway=gateway
    c.db.create_extra_invoice(gateway,'order',99998,USER_ID,1)
    iid=c.db.create_extra_invoice(gateway,'order',c.oid,USER_ID,900)
    c.invoice=c.db.get_extra_invoice(iid)

@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','shortage','delivery','prior'])
def test_composite_stock_refused_before_claim(catalog,monkeypatch,gateway,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario)
    before=dump(c.db)
    try:text=invoke(c)
    except RuntimeError as e:text=str(e)
    assert not c.trace and dump(c.db)==before
    assert 'composite' in text.lower()
    assert all(s not in text+caplog.text for s in [LINKS[0],'fake_pass_1'])


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('quantity',[0,2])
def test_legacy_stock_success_repeat(catalog,monkeypatch,gateway,representation,kind,quantity):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,quantity=quantity)
    before=rows(c);wallet=c.db.get_wallet_credit(USER_ID);ref=c.db.get_wallet_credit(REFERRER)
    assert invoke(c)==SUCCESS
    qty=quantity or 1
    assert names(c)==['claim_order','take_unused_configs','approve_order','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase','send','admin']
    assert c.trace[:3]==[('claim_order',(c.oid,),{}),('take_unused_configs',(c.pid,USER_ID,qty),{}),('approve_order',(c.oid,[r['id'] for r in before[:qty]]),{})]
    assert c.trace[3]==('check_low_stock_alert_state',(c.pid,6-qty,1),{})
    assert c.trace[4]==('delivery',USER_ID,'Stock',LINKS[:qty],dict(final_price=900,order_id=c.oid,db=c.db),'approved')
    assert c.trace[5]==('reward_referrer_if_first_purchase',(USER_ID,1000),{})
    assert c.trace[6]==('send',REFERRER,'🤝 تبریک! یکی از زیرمجموعه‌های شما اولین خرید خود را انجام داد.\n💰 130 تومان به کیف پول شما اضافه شد.')
    assert c.trace[7]==('admin',c.oid)
    after=rows(c)
    for r in after[:qty]:
        assert (r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid)
        assert (datetime.fromisoformat(r['expires_at'])-datetime.fromisoformat(r['assigned_at'])).days==17
    assert after[qty:]==before[qty:]
    assert c.db.get_order(c.oid)['config_id']==before[0]['id']
    assert c.db.get_wallet_credit(REFERRER)==ref+130 and c.db.get_wallet_credit(USER_ID)==wallet
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==1
    state=dump(c.db);c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and dump(c.db)==state


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('scenario',['shortage','take_unused_configs','approve_order','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase','send','admin','prior','lost_claim','missing'])
def test_legacy_stock_failure_boundaries(catalog,monkeypatch,gateway,representation,scenario):
    c=catalog;setup(c,monkeypatch,gateway,representation,scenario=scenario)
    before=rows(c);ref=c.db.get_wallet_credit(REFERRER)
    if scenario=='missing':c.oid=99999
    errors=['take_unused_configs','approve_order','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase']
    if scenario in errors:
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    else:
        assert invoke(c)==('⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else SUCCESS)
    full=['claim_order','take_unused_configs','approve_order','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase','send','admin']
    expected=[] if scenario in {'prior','missing'} else ['claim_order'] if scenario=='lost_claim' else ['claim_order','take_unused_configs','release_order_claim'] if scenario=='shortage' else full[:full.index(scenario)+1] if scenario in errors else full
    assert names(c)==expected
    allocated=scenario in {'approve_order','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase','send','admin'}
    if allocated:assert all(r['is_used']==1 and r['assigned_user_id']==USER_ID for r in rows(c)[:2])
    else:assert rows(c)==before
    assert c.db.get_wallet_credit(REFERRER)==ref+(130 if scenario in {'send','admin'} else 0)
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(scenario in {'send','admin'})
    if scenario!='missing':
        with c.db._get_conn() as conn:status=conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]
        assert status==('approved' if scenario in {'prior','check_low_stock_alert_state','delivery','reward_referrer_if_first_purchase','send','admin'} else 'pending' if scenario=='shortage' else 'processing')
