"""T050bh/bi: pool/config aliases at shared dispatch and actual renewal SQL."""
import asyncio
from datetime import datetime as RealDatetime
import pytest
import database
import renewal_engine
from tests.integration.test_composite_telegram_custom_selection_guards import catalog, USER_ID
from tests.integration.test_composite_gateway_stock_guards import setup as stock_setup, rows, names, GATEWAYS
from tests.integration.test_composite_gateway_renewal_guards import RENEWED, PRIOR
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump

class Clock(RealDatetime):
    @classmethod
    def utcnow(cls):return cls(2026,11,8,12,0,0)


def setup(c,monkeypatch,gateway,representation,kind=None,marker='all',mode='time',expiry='future',scenario='success'):
    monkeypatch.setattr(database,'datetime',Clock)
    stock_setup(c,monkeypatch,gateway,representation)
    c.target=rows(c)[0]['id'];c.sibling=rows(c)[1]['id']
    with c.db._get_conn() as conn:
        conn.execute('UPDATE configs SET is_used=1,assigned_user_id=?,expires_at=?,renewal_reminder_sent=1 WHERE id=?',(USER_ID,'2030-01-01T00:00:00' if expiry=='future' else '2020-01-01T00:00:00',c.target))
    volume,days={'time':(0,10),'full':(20,30),'volume':(5,0)}[mode]
    c.oid=c.db.create_renewal_order(USER_ID,'config',c.target,mode,volume,days,1000,wallet_used=100)
    for name,key,selected in [('get_order','order',c.oid),('get_config_by_id','target',c.target),('get_product','product',c.pid)]:
        original=getattr(c.db,name)
        def read(ident,_original=original,_key=key,_selected=selected):
            row=_original(ident)
            if row is None:return None
            d=dict(row)
            if ident==_selected and marker in {_key,'all'} and kind is not None:d['service_kind']=kind
            elif _key=='target' and ident==c.sibling:d['service_kind']='composite'
            return as_row(d,representation)
        monkeypatch.setattr(c.db,name,read)
    for name in ['extend_pool_config_expiry','approve_renewal_order']:
        original=getattr(c.db,name)
        def wrap(*args,_name=name,_original=original,**kwargs):
            c.trace.append((_name,args,kwargs))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*args,**kwargs)
        monkeypatch.setattr(c.db,name,wrap)
    class Bot:
        async def send_message(self,uid,text):
            c.trace.append(('send',uid,text,c.db.get_order(c.oid)['status']))
            if scenario=='send':raise RuntimeError('synthetic failure')
    async def notify(bot,oid):
        c.trace.append(('admin',oid))
        if scenario=='admin':raise RuntimeError('synthetic failure')
    c.bot=Bot();c.notify=None if scenario=='no_admin' else notify
    if scenario=='prior':c.db.approve_renewal_order(c.oid)
    if scenario=='lost_claim':
        c.db.claim_order(c.oid);get=c.db.get_order
        def stale(oid):
            row=get(oid)
            if row is None:return None
            d=dict(row);d['status']='pending';return as_row(d,representation)
        monkeypatch.setattr(c.db,'get_order',stale)
    if scenario=='foreign':
        with c.db._get_conn() as conn:conn.execute('UPDATE configs SET assigned_user_id=9001 WHERE id=?',(c.target,))
    if scenario=='missing_target':
        with c.db._get_conn() as conn:conn.execute('DELETE FROM configs WHERE id=?',(c.target,))
    c.trace.clear()


def invoke(c):return asyncio.run(c.payment.finalize_paid_order(c.db,c.bot,c.oid,c.notify))


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


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','target','product'])
def test_composite_pool_engine_refused_before_sql(catalog,monkeypatch,representation,marker):
    c=catalog;setup(c,monkeypatch,GATEWAYS[0],representation,'composite',marker)
    before=dump(c.db)
    with pytest.raises(renewal_engine.RenewalError,match='(?i)composite'):
        asyncio.run(renewal_engine.execute_renewal(c.db,c.db.get_order(c.oid)))
    assert not c.trace and dump(c.db)==before


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
        assert text==('⚠️ سفارش یافت نشد.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else '⛔️ تمدید ناموفق بود: این سرویس دیگر یافت نشد (شاید قبلاً حذف شده).\nبا پشتیبانی تماس بگیرید.' if scenario in {'foreign','missing_target'} else '⛔️ خطای غیرمنتظره‌ای در تمدید رخ داد. سفارش برای بررسی دوباره آزاد شد؛ با پشتیبانی تماس بگیرید.' if scenario=='extend_pool_config_expiry' else RENEWED)
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
