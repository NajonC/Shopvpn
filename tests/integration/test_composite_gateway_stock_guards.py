"""T050bf/bg: shared stock fulfillment admission and real allocation/reward SQL."""
import asyncio
import importlib
from datetime import datetime
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests.integration.test_composite_abangateway_fulfillment_guards import SUCCESS, PRIOR, REFERRER
GATEWAYS=['abangateway_payment','blupal_payment','noapay_payment']
LINKS=[f'https://subscription.example.invalid/stock-{n}' for n in range(6)]


def setup(c,monkeypatch,gateway,representation,kind=None,marker='both',scenario='success',quantity=2):
    c.payment=importlib.import_module(gateway);c.trace=[]
    cat=c.db.add_category('Synthetic')
    c.pid=c.db.add_product(cat,'Stock',1000,duration_days=17)
    c.other=c.db.add_product(cat,'Other',9900)
    c.db.add_configs(c.pid,LINKS[:1] if scenario=='shortage' else LINKS)
    c.db.add_configs(c.other,['https://subscription.example.invalid/other'])
    c.oid=c.db.create_order(USER_ID,c.pid,1000,wallet_used=100,quantity=quantity)
    c.db.add_or_update_user(REFERRER,'referrer','Referrer');c.db.set_setting('referral_percent','13')
    with c.db._get_conn() as conn:conn.execute('UPDATE users SET referred_by=? WHERE telegram_id=?',(REFERRER,USER_ID))
    c.db.set_setting('low_stock_threshold','1')
    for name,key in [('get_order','order'),('get_product','product')]:
        original=getattr(c.db,name)
        def read(ident,_original=original,_key=key):
            row=_original(ident)
            if row is None:return None
            d=dict(row);selected=ident==(c.oid if _key=='order' else c.pid)
            value=kind if selected and marker in {_key,'both'} else 'composite' if _key=='product' and ident==c.other else None
            if value is not None:d['service_kind']=value
            return as_row(d,representation)
        monkeypatch.setattr(c.db,name,read)
    for name in ['claim_order','release_order_claim','take_unused_configs','approve_order','check_low_stock_alert_state','reward_referrer_if_first_purchase']:
        original=getattr(c.db,name)
        def wrap(*args,_name=name,_original=original,**kwargs):
            c.trace.append((_name,args,kwargs))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*args,**kwargs)
        monkeypatch.setattr(c.db,name,wrap)
    async def delivery(bot,uid,title,links,**kwargs):
        c.trace.append(('delivery',uid,title,links,kwargs,c.db.get_order(c.oid)['status']))
        if scenario=='delivery':raise RuntimeError('synthetic failure')
    monkeypatch.setattr(c.payment,'deliver_config_to_user',delivery)
    class Bot:
        async def send_message(self,uid,text):
            c.trace.append(('send',uid,text))
            if scenario=='send':raise RuntimeError('synthetic failure')
    async def notify(bot,oid):
        c.trace.append(('admin',oid))
        if scenario=='admin':raise RuntimeError('synthetic failure')
    c.bot=Bot();c.notify=notify
    if scenario=='prior':c.db.approve_order(c.oid,[rows(c)[0]['id']]);c.trace.clear()
    if scenario=='lost_claim':
        c.db.claim_order(c.oid);c.trace.clear();get=c.db.get_order
        def stale(oid):
            row=get(oid)
            if row is None:return None
            d=dict(row);d['status']='pending';return as_row(d,representation)
        monkeypatch.setattr(c.db,'get_order',stale)


def rows(c):
    with c.db._get_conn() as conn:return [dict(r) for r in conn.execute('SELECT * FROM configs WHERE product_id=? ORDER BY id',(c.pid,))]
def invoke(c):return asyncio.run(c.payment.finalize_paid_order(c.db,c.bot,c.oid,c.notify))
def names(c):return [e[0] for e in c.trace]


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
        assert invoke(c)==('⚠️ سفارش یافت نشد.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if scenario=='shortage' else SUCCESS)
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
