"""T050bv/bw: manual stock/direct callback, real fulfillment and SQLite."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_admin
from tests._harness.legacy_bot import FakeCallbackQuery, FakeUser, FakeMessage, TelegramLog, RecordingBot, find_handler
from tests.integration.test_composite_gateway_auto_guards import catalog, auto_catalog, balance
from tests.integration.test_composite_gateway_stock_guards import setup as stock_setup, rows, dump, LINKS, USER_ID, REFERRER
from tests.integration.test_composite_gateway_direct_guards import setup as direct_setup, configs, LINK
from tests.integration.test_composite_gateway_auto_guards import setup as auto_setup
from tests.integration.test_composite_gateway_pool_renewal_guards import setup as renewal_setup
OWNER=9001
ALREADY='این سفارش قبلاً بررسی شده است.'


def setup(c,mp,representation,branch,kind=None,marker='both',scenario='success',quantity=2):
    import reseller_auto_provision
    mp.setattr(reseller_auto_provision,'MAIN_DB_PATH',c.main.db_path)
    local={'stock':'shortage','direct':'second','auto':'second','renewal':'foreign'}[branch] if scenario=='failure' else scenario
    if branch=='renewal':renewal_setup(c,mp,'abangateway_payment',representation,kind,marker,scenario=local)
    else:{'stock':stock_setup,'direct':direct_setup,'auto':auto_setup}[branch](c,mp,'abangateway_payment',representation,kind,marker,scenario=local,quantity=quantity)
    c.branch=branch
    async def delivery(bot,uid,title,links,**kw):
        c.trace.append(('delivery',uid,title,links,kw,c.db.get_order(c.oid)['status']))
        if scenario=='delivery':raise RuntimeError('synthetic failure')
    mp.setattr(handlers_admin,'deliver_config_to_user',delivery)
    c.router=handlers_admin.create_admin_router(c.db,is_main_bot=True)
    c.trace.clear()


def invoke(c,uid=OWNER,data=None):
    async def run():
        log=TelegramLog();user=FakeUser(uid)
        call=FakeCallbackQuery(log,user,data or f'order_approve:{c.oid}',FakeMessage(log,uid,from_user=user))
        await find_handler(c.router,'callback_query','cb_order_approve')(call,RecordingBot(log))
        return log.events
    return asyncio.run(run())


def refused(c,mp,representation,branch,marker,scenario,caplog):
    setup(c,mp,representation,branch,'composite',marker,scenario)
    before=(dump(c.db),dump(c.main));events=invoke(c)
    assert not c.trace and (dump(c.db),dump(c.main))==before
    assert len(events)==1 and events[0].kind=='callback_answer' and events[0].show_alert and 'composite' in (events[0].text or '').lower()
    assert all(s not in str(events)+caplog.text for s in [LINK,LINKS[0],'fake_pass_1'])


def legacy(c,mp,representation,branch,kind,scenario,quantity=2):
    setup(c,mp,representation,branch,kind,scenario=scenario,quantity=quantity)
    stock=rows(c);credit=balance(c);before=(dump(c.db),dump(c.main))
    events=invoke(c);answers=[e for e in events if e.kind=='callback_answer']
    assert len(answers)==1
    if scenario in {'prior','lost_claim'}:
        assert answers[0].text==ALREADY and (dump(c.db),dump(c.main))==before
        assert [e[0] for e in c.trace]==([] if scenario=='prior' else ['claim_order'])
        return
    assert c.trace[0]==('claim_order',(c.oid,),{})
    if scenario=='failure':
        assert answers[0].show_alert and answers[0].text.startswith('⛔️')
        assert c.db.get_order(c.oid)['status']=='pending' and c.trace[-1]==('release_order_claim',(c.oid,),{})
        assert rows(c)==stock and not configs(c) and balance(c)==credit
        assert c.db.get_wallet_credit(REFERRER)==0 and c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==0
        if branch in {'direct','auto'}:assert ('delete','chosen_1' if branch=='direct' else 'r1') in c.trace
        return
    assert c.db.get_order(c.oid)['status']=='approved' and not answers[0].show_alert
    assert answers[0].text=={'stock':'سفارش تایید و کانفیگ برای کاربر ارسال شد.','direct':'سفارش تایید و کانفیگ به‌صورت خودکار ساخته شد.','auto':'سفارش تایید و کانفیگ به‌صورت خودکار ساخته شد.','renewal':'سفارش تایید و سرویس تمدید شد.'}[branch]
    q=quantity or 1
    if branch=='renewal':
        assert rows(c)[0]['expires_at']=='2030-01-11T00:00:00' and rows(c)[1:]==stock[1:]
        assert ('extend_pool_config_expiry',(c.target,USER_ID,10),{}) in c.trace
    else:
        links=LINKS[:q] if branch=='stock' else [LINK+u for u in (['chosen'] if q==1 else ['chosen_1','chosen_2'])] if branch=='direct' else [LINK+'r'+str(i) for i in range(1,q+1)]
        assert ('delivery',USER_ID,branch.title(),links,dict(final_price=900,order_id=c.oid,db=c.db),'approved') in c.trace
        if branch=='stock':
            assert all((r['is_used'],r['assigned_user_id'],r['order_id'])==(1,USER_ID,c.oid) for r in rows(c)[:q]) and rows(c)[q:]==stock[q:]
            assert ('reward_referrer_if_first_purchase',(USER_ID,900),{}) in c.trace
        else:
            entries=configs(c);assert len(entries)==q
            for row,url in zip(entries,links):
                assert row['user_id']==USER_ID and row['order_id']==c.oid and row['volume_gb']==10 and row['duration_days']==17 and row['subscription_url']==url
                assert len(c.db.get_custom_config_history(row['id']))==1
            assert [e for e in c.trace if e[0]=='create']==[('create',url.removeprefix(LINK),10,17) for url in links]
        if branch=='auto':
            assert balance(c)==(credit[0]-q*10,credit[1])
            for row in configs(c):assert c.db.get_panel_server(row['panel_server_id'])['is_mirror']==1
    assert c.db.get_wallet_credit(REFERRER)==(117 if branch=='stock' else 0)
    assert c.db.get_user(USER_ID)['referral_first_purchase_rewarded']==int(branch=='stock')
    assert c.db.get_wallet_credit(USER_ID)==0
    with c.db._get_conn() as conn:
        logs=conn.execute('SELECT action FROM admin_logs').fetchall()
    assert [r[0] for r in logs]==['renewal_approve' if branch=='renewal' else 'order_approve']
    state=(dump(c.db),dump(c.main));c.trace.clear()
    assert [e.text for e in invoke(c) if e.kind=='callback_answer']==[ALREADY]
    assert not c.trace and (dump(c.db),dump(c.main))==state


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',['stock','direct'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('scenario',['success','failure','prior'])
def test_composite_manual_catalog(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog):
    refused(auto_catalog,monkeypatch,representation,branch,marker,scenario,caplog)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',['stock','direct'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('scenario',['success','failure','prior','lost_claim','delivery'])
@pytest.mark.parametrize('quantity',[0,2])
def test_legacy_manual_catalog(auto_catalog,monkeypatch,representation,branch,kind,scenario,quantity):
    if scenario=='failure' and quantity==0:quantity=2
    legacy(auto_catalog,monkeypatch,representation,branch,kind,scenario,quantity)

@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('branch',['stock','direct'])
@pytest.mark.parametrize('failure',['unauthorized','malformed','missing'])
def test_manual_catalog_opaque(auto_catalog,monkeypatch,representation,branch,failure):
    opaque(auto_catalog,monkeypatch,representation,branch,failure)


def opaque(c,mp,representation,branch,failure):
    setup(c,mp,representation,branch,'composite','order')
    before=(dump(c.db),dump(c.main))
    events=invoke(c,USER_ID if failure=='unauthorized' else OWNER, 'order_approve:bad' if failure=='malformed' else 'order_approve:99999' if failure=='missing' else None)
    assert len(events)==1 and events[0].kind=='callback_answer'
    assert events[0].text==(None if failure=='unauthorized' else '❌ درخواست نامعتبر است.' if failure=='malformed' else 'سفارش یافت نشد.')
    assert not c.trace and (dump(c.db),dump(c.main))==before
