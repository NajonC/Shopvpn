"""T050bz/ca: actual manual custom approval and SQL; external panel only faked."""
from types import SimpleNamespace
import pytest
from tests.integration.test_composite_abangateway_fulfillment_guards import catalog, setup as shared_setup, configs, LINK, REFERRER, USER_ID, dump
from tests.integration.test_composite_manual_catalog_guards import invoke, ALREADY
import handlers_admin
import panel_providers


def setup(c,mp,representation,kind=None,marker='both',scenario='success',days=17):
    shared_setup(c,mp,representation,kind,marker,scenario)
    with c.db._get_conn() as conn:
        conn.execute('UPDATE orders SET custom_duration_days=? WHERE id=?',(days,c.oid))
        if scenario=='inactive':conn.execute('UPDATE panel_servers SET is_active=0 WHERE id=?',(c.s1,))
    class Provider:
        def __init__(self,server):c.trace.append(('factory',server['id']))
        async def create_user(self,username,volume_gb,duration_days):
            c.trace.append(('create',username,volume_gb,duration_days))
            if scenario in {'taken','panel'}:raise (panel_providers.PanelUsernameTakenError if scenario=='taken' else panel_providers.PanelError)('synthetic failure')
            return SimpleNamespace(username='created_name',subscription_url=LINK)
    mp.setitem(panel_providers.PROVIDERS,'3xui',Provider)
    for name in ['log_admin_action']:
        original=getattr(c.db,name)
        def wrap(*a,_name=name,_original=original,**kw):
            c.trace.append((_name,a,kw));return _original(*a,**kw)
        mp.setattr(c.db,name,wrap)
    async def delivery(bot,uid,title,links,**kw):
        c.trace.append(('delivery',uid,title,links,kw,c.db.get_order(c.oid)['status']))
        if scenario=='delivery':raise RuntimeError('synthetic failure')
    mp.setattr(handlers_admin,'deliver_config_to_user',delivery)
    c.router=handlers_admin.create_admin_router(c.db,is_main_bot=True);c.trace.clear()


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','panel','prior'])
def test_composite_manual_custom(catalog,monkeypatch,representation,marker,scenario,caplog):
    c=catalog;setup(c,monkeypatch,representation,'composite',marker,scenario)
    before=dump(c.db);events=invoke(c)
    assert not c.trace and dump(c.db)==before
    assert len(events)==1 and events[0].show_alert and 'composite' in (events[0].text or '').lower()
    assert all(x not in str(events)+caplog.text for x in [LINK,'newname','fake_pass_1'])


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('days',[17,None])
@pytest.mark.parametrize('scenario',['success','inactive','taken','panel','prior','lost_claim','delivery','add_custom_config'])
def test_legacy_manual_custom(catalog,monkeypatch,representation,kind,days,scenario):
    c=catalog;setup(c,monkeypatch,representation,kind,scenario=scenario,days=days)
    before=dump(c.db)
    if scenario=='add_custom_config':
        with pytest.raises(RuntimeError,match='synthetic failure'):invoke(c)
        assert c.db.get_order(c.oid)['status']=='approved' and not configs(c)
        assert [e[0] for e in c.trace]==['claim_order','factory','create','approve_custom_config_order','add_custom_config']
        return
    events=invoke(c);answers=[e for e in events if e.kind=='callback_answer'];assert len(answers)==1
    if scenario in {'prior','lost_claim'}:
        assert answers[0].text==ALREADY and dump(c.db)==before
        assert [e[0] for e in c.trace]==([] if scenario=='prior' else ['claim_order'])
        return
    if scenario in {'inactive','taken','panel'}:
        assert answers[0].show_alert and answers[0].text.startswith('⛔️')
        assert c.db.get_order(c.oid)['status']==('processing' if scenario=='inactive' else 'pending')
        assert [e[0] for e in c.trace]==(['claim_order'] if scenario=='inactive' else ['claim_order','factory','create','release_order_claim'])
        assert not configs(c)
        return
    assert c.db.get_order(c.oid)['status']=='approved' and answers[0].text=='سفارش تایید و کانفیگ شخصی روی پنل ساخته شد.'
    duration=45 if days is None else days
    assert [e[0] for e in c.trace]==['claim_order','factory','create','approve_custom_config_order','add_custom_config','log_admin_action','delivery']
    assert c.trace[:3]==[('claim_order',(c.oid,),{}),('factory',c.s1),('create','newname',10,duration)]
    assert c.trace[-1]==('delivery',USER_ID,'کانفیگ شخصی',[LINK],dict(final_price=900,order_id=c.oid,db=c.db),'approved')
    entries=configs(c);assert len(entries)==1;r=entries[0]
    assert {k:r[k] for k in ['user_id','panel_server_id','username','volume_gb','duration_days','order_id','product_id','subscription_url','source']}==dict(user_id=USER_ID,panel_server_id=c.s1,username='created_name',volume_gb=10,duration_days=duration,order_id=c.oid,product_id=c.alpha_id,subscription_url=LINK,source='custom_config')
    h=c.db.get_custom_config_history(r['id']);assert len(h)==1 and (h[0]['event_type'],h[0]['detail'])==('purchase',f'10 گیگ / {duration} روز')
    with c.db._get_conn() as conn:assert [r[0] for r in conn.execute('SELECT action FROM admin_logs')]==['custom_config_approve']
    assert c.db.get_wallet_credit(REFERRER)==0 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0 and c.db.get_wallet_credit(USER_ID)==0
    state=dump(c.db);c.trace.clear();assert [e.text for e in invoke(c) if e.kind=='callback_answer']==[ALREADY]
    assert not c.trace and dump(c.db)==state
