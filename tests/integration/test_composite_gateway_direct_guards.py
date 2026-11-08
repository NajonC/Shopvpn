"""T050bj/bk: shared DIRECT dispatch with real provision/factory/local SQL."""
from types import SimpleNamespace
import pytest
import direct_panel_provision as direct
import panel_providers
from tests.integration.test_composite_gateway_stock_guards import (
    catalog, USER_ID, GATEWAYS, REFERRER, SUCCESS, PRIOR, dump, invoke, names,
    setup as stock_setup,
)
LINK='https://subscription.example.invalid/direct/'


def setup(c,mp,gateway,representation,kind=None,marker='both',scenario='success',quantity=2,days=17,volume=10):
    stock_setup(c,mp,gateway,representation,kind,marker,scenario,quantity)
    with c.db._get_conn() as conn:
        conn.execute('UPDATE products SET name=?,is_auto_provision=1,provision_server_id=?,auto_provision_volume_gb=?,duration_days=? WHERE id=?',('Direct',c.s1,volume,days,c.pid))
        conn.execute('UPDATE orders SET config_name=? WHERE id=?',('chosen',c.oid))
        if scenario=='inactive':conn.execute('UPDATE panel_servers SET is_active=0 WHERE id=?',(c.s1,))
    for name in ['add_custom_config','approve_order_auto']:
        original=getattr(c.db,name)
        def wrap(*a,_name=name,_original=original,**kw):
            c.trace.append((_name,a,kw))
            if scenario==_name:raise RuntimeError('synthetic failure')
            return _original(*a,**kw)
        mp.setattr(c.db,name,wrap)
    class Provider:
        def __init__(self,server):
            c.trace.append(('factory',server['id']))
            if scenario=='factory':raise panel_providers.PanelError('synthetic failure')
        async def create_user(self,username,vol,duration):
            c.trace.append(('create',username,vol,duration))
            count=sum(e[0]=='create' for e in c.trace)
            if scenario=='create' or scenario in {'second','rollback'} and count==2:
                raise panel_providers.PanelError('synthetic failure')
            if scenario=='collision' and count==1:raise panel_providers.PanelUsernameTakenError('synthetic collision')
            return SimpleNamespace(username=username,subscription_url=LINK+username)
        async def delete_user(self,username):
            c.trace.append(('delete',username))
            if scenario=='rollback':raise panel_providers.PanelError('synthetic delete failure')
    mp.setitem(panel_providers.PROVIDERS,'3xui',Provider)
    mp.setattr(direct.random,'choices',lambda alphabet,k:['z']*k)


def configs(c):return sorted([dict(r) for r in c.db.get_custom_configs_for_user(USER_ID)],key=lambda r:r['id'])


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','second','delivery','prior'])
def test_composite_direct_refused(catalog,monkeypatch,gateway,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario)
    before=dump(c.db)
    try:text=invoke(c)
    except RuntimeError as e:text=str(e)
    assert not c.trace and dump(c.db)==before
    assert 'composite' in text.lower()
    assert all(s not in text+caplog.text for s in [LINK,'fake_pass_1','chosen'])


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('terms',[(0,0,0),(2,17,10),(2,None,10)])
def test_legacy_direct_success_repeat(catalog,monkeypatch,gateway,representation,kind,terms):
    c=catalog;qty,days,vol=terms;setup(c,monkeypatch,gateway,representation,kind,quantity=qty,days=days,volume=vol)
    assert invoke(c)==SUCCESS
    q=qty or 1;duration=30 if days is None else days
    users=['chosen'] if q==1 else ['chosen_1','chosen_2']
    assert names(c)==['claim_order','factory']+['create']*q+['add_custom_config']*q+['approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin']
    assert c.trace[0]==('claim_order',(c.oid,),{}) and c.trace[1]==('factory',c.s1)
    assert [e for e in c.trace if e[0]=='create']==[('create',u,vol,duration) for u in users]
    rows=configs(c);assert len(rows)==q
    for row,u in zip(rows,users):
        assert {k:row[k] for k in ['user_id','order_id','panel_server_id','username','volume_gb','duration_days','subscription_url','source','product_id']}==dict(user_id=USER_ID,order_id=c.oid,panel_server_id=c.s1,username=u,volume_gb=vol,duration_days=duration,subscription_url=LINK+u,source='direct_product',product_id=None)
        assert (row['expires_at'] is None)==(duration==0)
        h=c.db.get_custom_config_history(row['id']);assert len(h)==1 and h[0]['event_type']=='purchase' and h[0]['detail']==f'{vol} گیگ / {duration} روز'
    assert c.trace[-4]==('delivery',USER_ID,'Direct',[LINK+u for u in users],dict(final_price=900,order_id=c.oid,db=c.db),'approved')
    assert c.trace[-3]==('reward_referrer_if_first_purchase',(USER_ID,1000),{})
    assert c.trace[-2]==('send',REFERRER,'🤝 تبریک! یکی از زیرمجموعه‌های شما اولین خرید خود را انجام داد.\n💰 130 تومان به کیف پول شما اضافه شد.')
    assert c.trace[-1]==('admin',c.oid)
    assert c.db.get_wallet_credit(REFERRER)==130 and c.db.get_wallet_credit(USER_ID)==0
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==1
    state=dump(c.db);c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and dump(c.db)==state


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('scenario',['inactive','factory','create','second','rollback','collision','add_custom_config','approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin','prior','lost_claim','missing'])
def test_legacy_direct_failures(catalog,monkeypatch,gateway,representation,scenario):
    c=catalog;setup(c,monkeypatch,gateway,representation,scenario=scenario)
    if scenario=='missing':c.oid=99999
    raises={'factory','approve_order_auto','delivery','reward_referrer_if_first_purchase'}
    if scenario in raises:
        with pytest.raises((RuntimeError,panel_providers.PanelError),match='synthetic failure'):invoke(c)
    else:
        text=invoke(c)
        if scenario in {'inactive','factory','create','second','rollback'}:
            assert text.startswith('⚠️ پرداخت تایید شد ولی ساخت خودکار کانفیگ ناموفق بود: ') and text.endswith('\nبا پشتیبانی تماس بگیرید.')
        else:assert text==('⚠️ سفارش یافت نشد.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else SUCCESS)
    full=['claim_order','factory','create','create','add_custom_config','add_custom_config','approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin']
    expected=[] if scenario in {'prior','missing'} else ['claim_order'] if scenario=='lost_claim' else ['claim_order','release_order_claim'] if scenario=='inactive' else ['claim_order','factory'] if scenario=='factory' else ['claim_order','factory','create','release_order_claim'] if scenario=='create' else ['claim_order','factory','create','create','delete','release_order_claim'] if scenario in {'second','rollback'} else full[:full.index(scenario)+1] if scenario in raises else full[:3]+['create']+full[3:] if scenario=='collision' else full
    assert names(c)==expected
    persisted=scenario in (raises-{'factory'})|{'collision','send','admin'}
    assert len(configs(c))==(2 if persisted else 0)
    if scenario in {'second','rollback'}:assert ('delete','chosen_1') in c.trace
    if scenario=='collision':assert [e[1] for e in c.trace if e[0]=='create']==['chosen_1','chosen_1_zzz','chosen_2']
    rewarded=scenario in {'collision','add_custom_config','send','admin'}
    assert c.db.get_wallet_credit(REFERRER)==(130 if rewarded else 0)
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(rewarded)
    if scenario!='missing':
        with c.db._get_conn() as conn:status=conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]
        assert status==('pending' if scenario in {'inactive','create','second','rollback'} else 'processing' if scenario in {'factory','lost_claim','approve_order_auto'} else 'approved')
