"""T050en/eo: actual extra-gateway AUTO credit/mirror/persistence path."""
from pathlib import Path
import pytest
import database
from tests.integration.test_composite_extra_direct_fulfillment import (
    catalog, USER_ID, GATEWAYS, REFERRER, SUCCESS, PRIOR, LINK, dump, invoke, names,
    configs, setup as direct_setup,
)
import reseller_auto_provision as auto
OWNER=9001


@pytest.fixture
def auto_catalog(catalog):
    c=catalog;c.main=database.Database(str(Path(c.db.db_path).with_name('main.db')));c.main.init_db(OWNER)
    try:yield c
    finally:c.main.close()


def setup(c,mp,gateway,representation,kind=None,marker='both',scenario='success',quantity=2,days=17,model='volume_credit'):
    direct_setup(c,mp,gateway,representation,kind,marker,scenario,quantity,days,10)
    with c.db._get_conn() as conn:conn.execute('UPDATE products SET name=?,provision_server_id=NULL WHERE id=?',('Auto',c.pid))
    cat=c.main.add_category('Supply');pid=c.main.add_product(cat,'Supply',999)
    assert pid==c.pid
    c.main.add_or_update_user(OWNER,'owner','Owner');c.main.set_reseller_status(OWNER,True)
    c.main.add_panel_server('Unused','3xui','https://unused.example.invalid','fake','fake')
    c.remote=c.main.add_panel_server('Supply','3xui','https://supply.example.invalid','fake','fake')
    c.main.set_reseller_panel(OWNER,c.remote);c.main.set_reseller_supply_model(OWNER,model,pid)
    c.main.adjust_reseller_credit(OWNER,100);c.main.set_reseller_product_credit(OWNER,pid,10)
    mp.setattr(auto,'MAIN_DB_PATH',c.main.db_path)
    candidates=iter(['r1','r2','r3','r4','r5','r6'])
    mp.setattr(auto,'_random_username',lambda prefix:next(candidates))
    if scenario=='inactive':
        with c.main._get_conn() as conn:conn.execute('UPDATE panel_servers SET is_active=0 WHERE id=?',(c.remote,))
    if scenario=='shortage':
        if model=='fixed_product':c.main.set_reseller_product_credit(OWNER,pid,1)
        else:c.main.adjust_reseller_credit(OWNER,-99)
    if scenario=='disabled':c.main.set_reseller_status(OWNER,False)
    if scenario=='owner':
        with c.db._get_conn() as conn:conn.execute("DELETE FROM admins WHERE role='owner'")
    original=c.db.get_or_create_mirror_panel_server
    def mirror(server,_original=original):
        c.trace.append(('mirror',server['id']))
        if scenario=='mirror':raise RuntimeError('synthetic failure')
        return _original(server)
    mp.setattr(c.db,'get_or_create_mirror_panel_server',mirror)
    for method in ['consume_reseller_credit','consume_reseller_product_credit']:
        original=getattr(database.Database,method)
        def consume(db,*args,_original=original,_name=method,**kwargs):
            assert db.db_path==c.main.db_path
            c.trace.append((_name,args,kwargs))
            if scenario=='race':
                with db._get_conn() as conn:
                    if _name=='consume_reseller_credit':conn.execute('UPDATE users SET reseller_credit_gb=1 WHERE telegram_id=?',(OWNER,))
                    else:conn.execute('UPDATE reseller_product_credit SET qty_remaining=1 WHERE reseller_id=?',(OWNER,))
            return _original(db,*args,**kwargs)
        mp.setattr(database.Database,method,consume)
    c.model=model


def balance(c):return c.main.get_reseller_credit(OWNER),c.main.get_reseller_product_credit(OWNER,c.pid)


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','second','delivery','prior'])
def test_composite_auto_refused(auto_catalog,monkeypatch,gateway,representation,marker,scenario,caplog):
    c=auto_catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,scenario)
    before=(dump(c.db),dump(c.main))
    try:text=invoke(c)
    except RuntimeError as e:text=str(e)
    assert not c.trace and (dump(c.db),dump(c.main))==before
    assert 'composite' in text.lower()
    assert all(s not in text+caplog.text for s in [LINK,'fake_pass_1','chosen'])


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('representation,model',[('dict','volume_credit'),('sqlite','volume_credit'),('dict','fixed_product')])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('terms',[(0,0),(2,17),(2,None)])
def test_legacy_auto_success_repeat(auto_catalog,monkeypatch,gateway,representation,model,kind,terms):
    c=auto_catalog;qty,days=terms;setup(c,monkeypatch,gateway,representation,kind,quantity=qty,days=days,model=model)
    assert invoke(c)==SUCCESS
    q=qty or 1;duration=30 if days is None else days;users=['r'+str(i) for i in range(1,q+1)]
    consume='consume_reseller_product_credit' if model=='fixed_product' else 'consume_reseller_credit'
    assert names(c)==['claim_order','factory']+['create']*q+[consume,'mirror']+['add_custom_config']*q+['approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin']
    assert c.trace[1]==('factory',c.remote)
    assert [e for e in c.trace if e[0]=='create']==[('create',u,10,duration) for u in users]
    event=next(e for e in c.trace if e[0]==consume)
    assert event==((consume,(OWNER,c.pid,q),{}) if model=='fixed_product' else (consume,(OWNER,q*10),dict(reason=f'خرید خودکار مشتری - محصول «Auto» × {q}')))
    assert balance(c)==((100,10-q) if model=='fixed_product' else (100-q*10,10))
    rows=configs(c);assert len(rows)==q
    for row,u in zip(rows,users):
        mirror=c.db.get_panel_server(row['panel_server_id'])
        assert mirror['is_mirror']==1 and mirror['mirror_source_id']==c.remote and mirror['api_url']=='https://supply.example.invalid'
        assert row['panel_server_id']!=c.remote
        assert {k:row[k] for k in ['user_id','order_id','username','volume_gb','duration_days','subscription_url','source','product_id']}==dict(user_id=USER_ID,order_id=c.oid,username=u,volume_gb=10,duration_days=duration,subscription_url=LINK+u,source='direct_product',product_id=None)
        assert (row['expires_at'] is None)==(duration==0)
        h=c.db.get_custom_config_history(row['id']);assert len(h)==1 and h[0]['event_type']=='purchase' and h[0]['detail']==f'10 گیگ / {duration} روز'
    assert c.trace[-4]==('delivery',USER_ID,'Auto',[LINK+u for u in users],dict(final_price=900,order_id=c.oid,db=c.db),'approved')
    assert c.trace[-3]==('reward_referrer_if_first_purchase',(USER_ID,1000),{})
    assert c.trace[-2]==('send',REFERRER,'🤝 تبریک! یکی از زیرمجموعه‌های شما اولین خرید خود را انجام داد.\n💰 130 تومان به کیف پول شما اضافه شد.')
    assert c.trace[-1]==('admin',c.oid)
    assert c.db.get_wallet_credit(REFERRER)==130 and c.db.get_wallet_credit(USER_ID)==0
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==1
    if model=='volume_credit':
        logs=c.main.get_reseller_credit_log(OWNER);assert logs[0]['delta_gb']==-q*10 and logs[0]['reason']==f'خرید خودکار مشتری - محصول «Auto» × {q}'
    state=(dump(c.db),dump(c.main));c.trace.clear();assert invoke(c)==PRIOR
    assert not c.trace and (dump(c.db),dump(c.main))==state


@pytest.mark.parametrize('gateway',GATEWAYS)
@pytest.mark.parametrize('model',['volume_credit','fixed_product'])
@pytest.mark.parametrize('scenario',['owner','disabled','shortage','inactive','factory','create','second','rollback','collision','race','mirror','add_custom_config','approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin','prior','lost_claim','missing','sqlite_fixed'])
def test_legacy_auto_failures(auto_catalog,monkeypatch,gateway,model,scenario):
    c=auto_catalog;setup(c,monkeypatch,gateway,'sqlite' if scenario=='sqlite_fixed' else 'dict',scenario=scenario,model=model)
    if scenario=='missing':c.oid=99999
    raises={'factory','approve_order_auto','delivery','reward_referrer_if_first_purchase'}
    if scenario=='sqlite_fixed' and model=='fixed_product':
        with pytest.raises(AttributeError,match='has no attribute.*get'):invoke(c)
    elif scenario in raises:
        from panel_providers import PanelError
        with pytest.raises((RuntimeError,PanelError),match='synthetic failure'):invoke(c)
    else:
        text=invoke(c)
        if scenario in {'owner','disabled','shortage','inactive','create','second','rollback','race'}:assert text.startswith('⚠️ پرداخت تایید شد ولی ساخت خودکار کانفیگ ناموفق بود: ') and text.endswith('\nبا پشتیبانی تماس بگیرید.')
        else:assert text==('⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if scenario=='missing' else PRIOR if scenario in {'prior','lost_claim'} else SUCCESS)
    consume='consume_reseller_product_credit' if model=='fixed_product' else 'consume_reseller_credit'
    full=['claim_order','factory','create','create',consume,'mirror','add_custom_config','add_custom_config','approve_order_auto','delivery','reward_referrer_if_first_purchase','send','admin']
    expected=[] if scenario in {'prior','missing'} else ['claim_order'] if scenario=='lost_claim' or scenario=='sqlite_fixed' and model=='fixed_product' else ['claim_order','release_order_claim'] if scenario in {'owner','disabled','shortage','inactive'} else ['claim_order','factory'] if scenario=='factory' else ['claim_order','factory','create','release_order_claim'] if scenario=='create' else ['claim_order','factory','create','create','delete','release_order_claim'] if scenario in {'second','rollback'} else ['claim_order','factory','create','create',consume,'delete','delete','release_order_claim'] if scenario=='race' else full[:full.index(scenario)+1] if scenario in raises else full[:6]+full[8:] if scenario=='mirror' else full[:3]+['create']+full[3:] if scenario=='collision' else full
    assert names(c)==expected
    completed=scenario in {'mirror','add_custom_config','approve_order_auto','delivery','reward_referrer_if_first_purchase','collision','send','admin'} or scenario=='sqlite_fixed' and model=='volume_credit'
    assert len(configs(c))==(2 if completed and scenario not in {'mirror','add_custom_config'} else 0)
    if scenario in {'second','rollback'}:assert ('delete','r1') in c.trace
    if scenario=='race':assert [e[1] for e in c.trace if e[0]=='delete']==['r1','r2']
    if scenario=='collision':assert [e[1] for e in c.trace if e[0]=='create']==['r1','r2','r3']
    expected_balance=(100,8) if completed and model=='fixed_product' else (80,10) if completed else (100,1) if scenario in {'race','shortage'} and model=='fixed_product' else (1,10) if scenario in {'race','shortage'} else (100,10)
    assert balance(c)==expected_balance
    rewarded=completed and scenario not in {'approve_order_auto','delivery','reward_referrer_if_first_purchase'}
    assert c.db.get_wallet_credit(REFERRER)==(130 if rewarded else 0)
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(rewarded)
    if scenario!='missing':
        with c.db._get_conn() as conn:status=conn.execute('SELECT status FROM orders WHERE id=?',(c.oid,)).fetchone()[0]
        assert status==('pending' if scenario in {'owner','disabled','shortage','inactive','create','second','rollback','race'} else 'processing' if scenario in {'factory','lost_claim','approve_order_auto'} or scenario=='sqlite_fixed' and model=='fixed_product' else 'approved')
