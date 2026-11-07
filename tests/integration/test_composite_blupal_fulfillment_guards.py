"""T050az/ba: actual custom fulfillment, SQL and factory; synthetic remote/delivery."""
import asyncio
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_telegram_custom_card_entry_guards import prepare
from tests.integration.test_composite_ai_catalog_legacy import dump
import blupal_payment as payment
import panel_providers

SUCCESS='✅ پرداخت تایید شد و کانفیگ تحویل داده شد.'
PRIOR='✅ این سفارش قبلاً بررسی و تحویل داده شده است.'
LINK='https://subscription.example.invalid/synthetic'
REFERRER=6201


def setup(c, monkeypatch, representation, kind=None, marker='both', scenario='success'):
    prepare(c,representation,kind if marker in {'order','both'} else None,kind if marker in {'product','both'} else None,days=17)
    c.configure(overrides={c.alpha_id:kind if marker in {'product','both'} else None,c.beta_id:'composite'},representation=representation)
    c.db.set_setting('custom_config_duration_days','45')
    c.db.add_or_update_user(REFERRER,'synthetic_referrer','Referrer')
    c.db.set_setting('referral_percent','13')
    with c.db._get_conn() as conn:
        conn.execute('UPDATE users SET referred_by=? WHERE telegram_id=?',(REFERRER,USER_ID))
    c.trace=[]
    for name in ['claim_order','release_order_claim','add_custom_config','approve_custom_config_order','reward_referrer_if_first_purchase']:
        original=getattr(c.db,name)
        def wrap(*args,_name=name,_original=original,**kwargs):
            c.trace.append((_name,args,kwargs))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*args,**kwargs)
        monkeypatch.setattr(c.db,name,wrap)
    class Provider:
        def __init__(self,server):
            c.trace.append(('factory',server['id']))
            if scenario=='factory':raise RuntimeError('synthetic failure')
        async def create_user(self,username,volume,days):
            c.trace.append(('create',username,volume,days))
            if scenario=='create':raise RuntimeError('synthetic failure')
            return SimpleNamespace(username='created_name',subscription_url=LINK)
    monkeypatch.setitem(panel_providers.PROVIDERS,'3xui',Provider)
    async def delivery(bot,uid,title,links,**kwargs):
        c.trace.append(('delivery',uid,title,links,kwargs, c.db.get_order(c.oid)['status']))
        if scenario=='delivery':raise RuntimeError('synthetic failure')
    monkeypatch.setattr(payment,'deliver_config_to_user',delivery)
    class Bot:
        async def send_message(self,uid,text):
            c.trace.append(('send',uid,text))
            if scenario=='send':raise RuntimeError('synthetic failure')
    async def notify(bot,oid):
        c.trace.append(('admin',oid))
        if scenario=='admin':raise RuntimeError('synthetic failure')
    c.bot=Bot();c.notify=notify
    if scenario=='missing_server':
        with c.db._get_conn() as conn:conn.execute('UPDATE orders SET custom_panel_server_id=99999 WHERE id=?',(c.oid,))
    if scenario=='prior':c.db.approve_custom_config_order(c.oid);c.trace.clear()
    if scenario=='lost_claim':
        c.db.claim_order(c.oid);c.trace.clear()
        # stale pending read with real conditional claim losing to existing processing row
        get=c.db.get_order
        def stale(oid):
            row=get(oid)
            if row is None:return None
            row=dict(row);row['status']='pending';return row
        monkeypatch.setattr(c.db,'get_order',stale)


def invoke(c):return asyncio.run(payment.finalize_paid_order(c.db,c.bot,c.oid,c.notify))
def names(c):return [x[0] for x in c.trace]
def configs(c):return [dict(r) for r in c.db.get_custom_configs_for_user(USER_ID)]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','factory','create','delivery','prior'])
def test_composite_custom_refused_before_effects(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db)
    try:text=invoke(c)
    except RuntimeError as exc:text=str(exc)
    assert c.trace==[] and dump(c.db)==before
    assert isinstance(text,str) and 'composite' in text.lower()
    assert all(s not in text+caplog.text for s in ['newname',LINK,'fake_pass_1'])


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['success','send','admin'])
def test_legacy_success_reward_and_repeat(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    before_wallet=c.db.get_wallet_credit(REFERRER);buyer_wallet=c.db.get_wallet_credit(USER_ID)
    assert invoke(c)==SUCCESS
    assert names(c)==['claim_order','factory','create','add_custom_config','approve_custom_config_order','delivery','reward_referrer_if_first_purchase','send','admin']
    assert c.trace[0]==('claim_order',(c.oid,),{}) and c.trace[1]==('factory',c.s1)
    # Legacy helper uses global duration, even if selected order saved 17 days.
    assert c.trace[2]==('create','newname',10,45)
    rows=configs(c);assert len(rows)==1
    row=rows[0]
    assert {k:row[k] for k in ['order_id','user_id','panel_server_id','username','volume_gb','duration_days','subscription_url','source','product_id']}==dict(order_id=c.oid,user_id=USER_ID,panel_server_id=c.s1,username='created_name',volume_gb=10,duration_days=45,subscription_url=LINK,source='custom_config',product_id=None)
    history=c.db.get_custom_config_history(row['id']);assert len(history)==1 and history[0]['event_type']=='purchase' and history[0]['detail']=='10 گیگ / 45 روز'
    assert c.trace[5]==('delivery',USER_ID,'کانفیگ شخصی',[LINK],dict(final_price=900,order_id=c.oid,db=c.db),'approved')
    assert c.trace[6]==('reward_referrer_if_first_purchase',(USER_ID,1000),{})
    assert c.trace[7]==('send',REFERRER,'🤝 تبریک! یکی از زیرمجموعه‌های شما اولین خرید خود را انجام داد.\n💰 130 تومان به کیف پول شما اضافه شد.')
    assert c.trace[8]==('admin',c.oid)
    assert c.db.get_wallet_credit(REFERRER)==before_wallet+130 and c.db.get_wallet_credit(USER_ID)==buyer_wallet
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==1
    before=dump(c.db);c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['missing_server','factory','create','add_custom_config','approve_custom_config_order','delivery','prior','lost_claim','missing'])
def test_legacy_failure_boundaries(catalog,monkeypatch,representation,kind,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario)
    if scenario=='missing':c.oid=99999
    wallet=c.db.get_wallet_credit(REFERRER)
    if scenario in {'add_custom_config','approve_custom_config_order','delivery'}:
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    else:
        text=invoke(c)
        assert text==('⚠️ سفارش یافت نشد.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else '⛔️ سرور مربوط به کانفیگ شخصی یافت نشد؛ با پشتیبانی تماس بگیرید.' if scenario=='missing_server' else '⛔️ خطا در ساخت کانفیگ روی پنل: synthetic failure\nبا پشتیبانی تماس بگیرید.')
    expected={'missing':[], 'prior':[], 'lost_claim':['claim_order'],'missing_server':['claim_order','release_order_claim'],'factory':['claim_order','factory','release_order_claim'],'create':['claim_order','factory','create','release_order_claim'],'add_custom_config':['claim_order','factory','create','add_custom_config'],'approve_custom_config_order':['claim_order','factory','create','add_custom_config','approve_custom_config_order'],'delivery':['claim_order','factory','create','add_custom_config','approve_custom_config_order','delivery']}[scenario]
    assert names(c)==expected
    assert c.db.get_wallet_credit(REFERRER)==wallet and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
    assert len(configs(c))==(1 if scenario in {'approve_custom_config_order','delivery'} else 0)
    if scenario!='missing':
        # Existing post-persistence failures are characterized, not repaired here.
        with c.db._get_conn() as conn:status=conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]
        assert status==('approved' if scenario in {'prior','delivery'} else 'processing' if scenario in {'lost_claim','add_custom_config','approve_custom_config_order'} else 'pending')
