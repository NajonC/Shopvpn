"""T050eb/ec: extra-gateway actual custom renewal and global NULL aliases."""
import asyncio
import importlib
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump
import panel_providers
import extra_gateway_payment as egp
from panel_providers.base import PanelError

GATEWAYS=['abangateway_payment','blupal_payment','noapay_payment']
RENEWED='✅ سرویس شما با موفقیت تمدید شد.'
PRIOR='✅ این سفارش قبلاً بررسی و تحویل داده شده است.'
LINK='https://subscription.example.invalid/renewal'


def setup(c,monkeypatch,gateway,representation,kind=None,marker='both',mode='full',scenario='success'):
    c.payment=importlib.import_module(gateway);c.trace=[]
    original_marker=marker
    marker={'global_order':'order','global_target':'target'}.get(marker,marker)
    c.target=c.db.add_custom_config(USER_ID,c.s1,'renew_name',10,30,LINK,expires_at='2030-01-01T00:00:00')
    c.sibling=c.db.add_custom_config(USER_ID,c.s2,'sibling',99,60,LINK,expires_at='2030-01-01T00:00:00')
    volume,days={'full':(20,30),'volume':(5,0),'time':(0,10)}[mode]
    c.oid=c.db.create_renewal_order(USER_ID,'custom',c.target,mode,volume,days,1000,wallet_used=100)
    get=c.db.get_order;owned=c.db.get_custom_config_owned
    def order(oid):
        row=get(oid)
        if row is None:return None
        d=dict(row)
        if oid==c.oid and marker in {'order','both'} and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    def target(cid,uid):
        row=owned(cid,uid)
        if row is None:return None
        d=dict(row)
        k=kind if cid==c.target and marker in {'target','both'} else 'composite' if cid==c.sibling else None
        if k is not None:d['service_kind']=k
        return as_row(d,representation)
    monkeypatch.setattr(c.db,'get_order',order);monkeypatch.setattr(c.db,'get_custom_config_owned',target)
    with c.db._get_conn() as conn:conn.execute('UPDATE custom_configs SET product_id=? WHERE id=?',(None if original_marker.startswith('global_') else c.alpha_id,c.target))
    c.configure(overrides={c.alpha_id:kind if marker=='product' else None,c.beta_id:'composite'},representation=representation)
    get_target=c.db.get_custom_config_by_id
    def marked_target(cid):
        row=get_target(cid)
        if row is None:return None
        d=dict(row)
        if cid==c.target and marker in {'target','both'} and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    monkeypatch.setattr(c.db,'get_custom_config_by_id',marked_target)
    for name in ['claim_order','release_order_claim','apply_custom_config_renewal','approve_renewal_order']:
        original=getattr(c.db,name)
        def wrap(*args,_name=name,_original=original,**kwargs):
            c.trace.append((_name,args,kwargs))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*args,**kwargs)
        monkeypatch.setattr(c.db,name,wrap)
    # These paths must never be reached by renewal dispatch.
    for name in ['reward_referrer_if_first_purchase','take_unused_configs','add_custom_config']:
        def forbidden(*args,_name=name,**kwargs):
            c.trace.append((_name,));raise AssertionError('unexpected purchase dispatch')
        monkeypatch.setattr(c.db,name,forbidden)
    class Provider:
        def __init__(self,server):
            c.trace.append(('factory',server['id']))
            if scenario=='factory':raise PanelError('synthetic failure')
        async def update_user(self,username,**kwargs):
            c.trace.append(('update',username,kwargs))
            if scenario in {'update','unexpected'}:raise (PanelError if scenario=='update' else RuntimeError)('synthetic failure')
        async def get_user_usage(self,username):
            c.trace.append(('usage',username))
            if scenario=='usage':raise PanelError('synthetic failure')
            return {'data_limit_bytes':26*1024**3}
    monkeypatch.setitem(panel_providers.PROVIDERS,'3xui',Provider)
    class Bot:
        async def send_message(self,uid,text):
            c.trace.append(('send',uid,text,c.db.get_order(c.oid)['status']))
            if scenario=='send':raise RuntimeError('synthetic failure')
    async def notify(bot,oid):
        c.trace.append(('admin',oid))
        if scenario=='admin':raise RuntimeError('synthetic failure')
    c.bot=Bot();c.notify=None if scenario=='no_admin' else notify
    c.db.create_extra_invoice('zarinpal','order',99999,USER_ID,1)
    iid=c.db.create_extra_invoice('zarinpal','order',c.oid,USER_ID,900)
    c.invoice=c.db.get_extra_invoice(iid)
    if scenario=='prior':c.db.approve_renewal_order(c.oid);c.trace.clear()
    if scenario=='lost_claim':
        c.db.claim_order(c.oid);c.trace.clear()
        def stale(oid):
            row=order(oid)
            if row is None:return None
            d=dict(row);d['status']='pending';return as_row(d,representation)
        monkeypatch.setattr(c.db,'get_order',stale)
    if scenario=='foreign':
        with c.db._get_conn() as conn:conn.execute('UPDATE custom_configs SET user_id=9001 WHERE id=?',(c.target,))


def invoke(c):
    # A real selected invoice, distinct from order id; deliver must not claim/release it.
    if not hasattr(c,'invoice'):
        c.db.create_extra_invoice('zarinpal','order',99999,USER_ID,1)
        iid=c.db.create_extra_invoice('zarinpal','order',c.oid,USER_ID,900)
        c.invoice=c.db.get_extra_invoice(iid)
    warnings=[]
    async def warning(db,bot,text):warnings.append((db,bot,text))
    prior=egp._notify_admins;egp._notify_admins=warning
    before=dict(c.db.get_extra_invoice(c.invoice['id']))
    try:
        text=asyncio.run(egp.deliver(c.db,c.bot,c.invoice,c.notify))
        if 'composite' in text.lower():assert not warnings
        elif text.startswith(('⛔️','⚠️')):
            title=egp.registry.GATEWAYS['zarinpal']['title']
            expected=(f'⚠️ پرداخت {title} برای سفارش #{c.oid} دریافت شد ولی سفارش پیدا نشد.' if c.oid==99999 else f'⚠️ پرداخت {title} برای سفارش #{c.oid} (کاربر {USER_ID}) تایید شد ولی تحویل خودکار ناموفق بود:\n{text}')
            assert warnings==[(c.db,c.bot,expected)]
        else:assert not warnings
        return text
    finally:
        egp._notify_admins=prior
        assert dict(c.db.get_extra_invoice(c.invoice['id']))==before
def names(c):return [e[0] for e in c.trace]
def state(c):
    with c.db._get_conn() as conn:
        return dict(conn.execute('SELECT * FROM custom_configs WHERE id=?',(c.target,)).fetchone()),conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]


@pytest.mark.parametrize('gateway',['abangateway_payment'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','target','product','global_order','global_target'])
@pytest.mark.parametrize('scenario',['success','prior','update','approve_renewal_order'])
def test_composite_renewal_refused_before_claim(catalog,monkeypatch,gateway,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario=scenario)
    before=dump(c.db)
    try:text=invoke(c)
    except RuntimeError as e:text=str(e)
    assert not c.trace and dump(c.db)==before
    assert 'composite' in text.lower()
    assert all(x not in text+caplog.text for x in [LINK,'renew_name','fake_pass_1'])


@pytest.mark.parametrize('gateway',['abangateway_payment'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['product','global_target'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('mode',['full','volume','time'])
def test_legacy_renewal_success_and_repeat(catalog,monkeypatch,gateway,representation,kind,mode,marker):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,marker=marker,mode=mode)
    with c.db._get_conn() as conn:sibling=dict(conn.execute('SELECT * FROM custom_configs WHERE id=?',(c.sibling,)).fetchone())
    wallet=c.db.get_wallet_credit(USER_ID)
    assert invoke(c)==RENEWED
    v,d={'full':(20,30),'volume':(5,0),'time':(0,10)}[mode]
    expected=['claim_order','factory','update']+(['usage'] if mode=='full' else [])+['apply_custom_config_renewal','approve_renewal_order','send','admin']
    assert names(c)==expected
    assert c.trace[0]==('claim_order',(c.oid,),{}) and c.trace[1]==('factory',c.s1)
    assert c.trace[2]==('update','renew_name',dict(add_volume_gb=v,add_days=d,reset_usage=mode=='full',preserve_remaining=mode=='full'))
    i=4 if mode=='full' else 3
    assert c.trace[i]==('apply_custom_config_renewal',(c.target,v,d),dict(full_reset=mode=='full',set_volume_gb=26 if mode=='full' else None))
    assert c.trace[-3:]==[('approve_renewal_order',(c.oid,),{}),('send',USER_ID,RENEWED,'approved'),('admin',c.oid)]
    row,status=state(c);assert status=='approved'
    assert (row['volume_gb'],row['duration_days'],row['expires_at'])=={'full':(26,60,'2030-01-31T00:00:00'),'volume':(15,30,'2030-01-01T00:00:00'),'time':(10,40,'2030-01-11T00:00:00')}[mode]
    assert (row['user_id'],row['panel_server_id'],row['username'],row['subscription_url'])==(USER_ID,c.s1,'renew_name',LINK)
    hist=c.db.get_custom_config_history(c.target)
    assert [(r['event_type'],r['detail']) for r in hist]==[('renewal',f'+{v} گیگ / +{d} روز'),('purchase','10 گیگ / 30 روز')]
    with c.db._get_conn() as conn:assert dict(conn.execute('SELECT * FROM custom_configs WHERE id=?',(c.sibling,)).fetchone())==sibling
    assert c.db.get_wallet_credit(USER_ID)==wallet and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
    before=dump(c.db);c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and dump(c.db)==before


@pytest.mark.parametrize('gateway',['abangateway_payment'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['product','global_target'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['factory','update','usage','unexpected','apply_custom_config_renewal','approve_renewal_order','send','admin','no_admin','prior','lost_claim','foreign','missing'])
def test_legacy_renewal_failure_boundaries(catalog,monkeypatch,gateway,representation,scenario,marker,kind):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,marker=marker,scenario=scenario)
    if scenario=='missing':
        c.oid=99999
        with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET ref_id=? WHERE id=?',(c.oid,c.invoice['id']))
        c.invoice=c.db.get_extra_invoice(c.invoice['id'])
    before_row=None if scenario=='missing' else state(c)[0]
    if scenario=='approve_renewal_order':
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
    else:
        text=invoke(c)
        if scenario in {'factory','update','usage'}:assert text=='⛔️ تمدید ناموفق بود: synthetic failure\nبا پشتیبانی تماس بگیرید.'
        elif scenario=='foreign':assert text=='⛔️ تمدید ناموفق بود: این سرویس دیگر یافت نشد (شاید قبلاً حذف شده).\nبا پشتیبانی تماس بگیرید.'
        elif scenario in {'unexpected','apply_custom_config_renewal'}:assert text=='⛔️ خطای غیرمنتظره‌ای در تمدید رخ داد. سفارش برای بررسی دوباره آزاد شد؛ با پشتیبانی تماس بگیرید.'
        else:assert text==('⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else RENEWED)
    prefixes={'factory':['claim_order','factory'],'update':['claim_order','factory','update'],'unexpected':['claim_order','factory','update'],'usage':['claim_order','factory','update','usage'],'apply_custom_config_renewal':['claim_order','factory','update','usage','apply_custom_config_renewal'],'foreign':['claim_order']}
    success=['claim_order','factory','update','usage','apply_custom_config_renewal','approve_renewal_order']
    expected=prefixes[scenario]+['release_order_claim'] if scenario in prefixes else [] if scenario in {'missing','prior'} else ['claim_order'] if scenario=='lost_claim' else success if scenario=='approve_renewal_order' else success+['send']+([] if scenario=='no_admin' else ['admin'])
    assert names(c)==expected
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
    if scenario!='missing':
        row,status=state(c)
        updated=scenario in {'approve_renewal_order','send','admin','no_admin'}
        assert status==('approved' if scenario in {'prior','send','admin','no_admin'} else 'processing' if scenario in {'lost_claim','approve_renewal_order'} else 'pending')
        if updated:
            assert (row['volume_gb'],row['duration_days'],row['expires_at'])==(26,60,'2030-01-31T00:00:00')
            assert len(c.db.get_custom_config_history(c.target))==2
        else:assert row==before_row and len(c.db.get_custom_config_history(c.target))==1
