"""T050fh/fi: independent web admin STOCK alert caller via signed ASGI requests."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_order_approval import shop, remote, site, web_approve, BUYER, OWNER, configs, admin_logs
from tests._harness.legacy_web import load_admin_panel
from tests.integration.test_composite_admin_stock_alerts import setup, warnings, latch, delivered, REFERRER
from tests.integration.test_composite_ai_catalog_legacy import dump


def prepare(c,mp,s,representation,kind=None,marker='product',remaining=1,threshold='1',latched=0):
    setup(c,mp,representation,kind,marker,remaining,threshold,latched)
    c.log=s.log


def invoke(c):
    async def run():
        loop=asyncio.get_running_loop();tasks=[]
        def factory(loop,coro,context=None):
            task=asyncio.Task(coro,loop=loop,context=context);tasks.append(task);return task
        old=loop.get_task_factory();loop.set_task_factory(factory)
        try:
            response=await web_approve(c.oid,drain=False)
            results=await asyncio.gather(*tasks,return_exceptions=True)
            c.background_errors=[r for r in results if isinstance(r,BaseException)]
            return response
        finally:loop.set_task_factory(old)
    response=asyncio.run(run())
    assert dict(c.db.get_product(2))==c.other_before
    return response


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('remaining,threshold,initial,final,send',[(0,'0',0,1,True),(1,'1',0,1,True),(2,'1',1,0,False),(1,'1',1,1,False),(3,'',0,1,True)])
def test_web_admin_stock_alert_threshold_and_repeat(site,shop,monkeypatch,representation,kind,remaining,threshold,initial,final,send):
    c=shop;prepare(c,monkeypatch,site,representation,kind,remaining=remaining,threshold=threshold,latched=initial)
    response=invoke(c)
    assert response.status_code==200 and response.json()=={'ok':True} and not c.background_errors
    assert [n for n,a in c.trace]==['claim_order','take_unused_configs','approve_order','log_admin_action','check_low_stock_alert_state','reward_referrer_if_first_purchase']
    order=c.db.get_order(c.oid)
    assert (order['status'],order['user_id'],order['quantity'],order['final_price'],order['wallet_used'])==('approved',BUYER,2,180000,0)
    allocated=[r for r in configs(c) if r[1]]
    assert len(allocated)==2 and all(r[2:]==(BUYER,c.oid) for r in allocated)
    assert c.db.count_available_configs(1)==remaining and latch(c)==final
    assert c.db.get_wallet_credit(BUYER)==777 and c.db.get_wallet_credit(REFERRER)==23400
    assert c.db.get_user(BUYER)['referral_first_purchase_rewarded']==1
    assert [e.chat_id for e in warnings(c)]==([OWNER,9002] if send else [])
    if send:
        text='⚠️ هشدار اتمام موجودی\n\n'+f'📦 محصول «Stock 30d» فقط {remaining} کانفیگ آزاد باقی مانده (آستانه‌ی هشدار: {int(threshold or 3)}).\nلطفاً هرچه زودتر کانفیگ جدید به انبار اضافه کنید.'
        assert all(e.text==text for e in warnings(c))
    assert delivered(c)==['🔗 لینک اشتراک شما (برای کپی):\n`vless://admin-1`','🔗 لینک اشتراک شما (برای کپی):\n`vless://admin-2`']
    assert len(admin_logs(c))==1 and admin_logs(c)[0]==(1,'order_approve','سفارش #1 | کاربر 1001 | محصول «Stock 30d» (پنل وب - owner)','order','1')
    assert all(e.chat_id in {BUYER,OWNER,9002} for e in c.log.events)
    state=dump(c.db);c.trace.clear();c.log.events.clear();response=invoke(c)
    assert response.status_code==400 and response.json()=={'detail':'سفارش یافت نشد یا قبلاً بررسی شده.'}
    assert not c.trace and dump(c.db)==state and not c.log.events


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['product','order'])
@pytest.mark.parametrize('remaining,latched',[(0,0),(2,1)])
def test_composite_web_admin_stock_refuses_before_alert_and_claim(site,shop,monkeypatch,representation,marker,remaining,latched):
    c=shop;prepare(c,monkeypatch,site,representation,'composite',marker,remaining=remaining,latched=latched)
    before=dump(c.db)
    for _ in range(2):
        response=invoke(c)
        assert not c.trace and dump(c.db)==before and not c.log.events,'missing T052 web admin STOCK admission before claim/alert'
        assert response.status_code==400 and 'composite' in response.text.lower(),'missing T052 explicit web admin STOCK refusal'
        assert 'Stock 30d' not in response.text and 'vless://' not in response.text


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('fault',['count','threshold','state','product','admins','send_first','send_all','reward','delivery','log','notify'])
def test_web_admin_stock_alert_fault_boundaries(site,shop,monkeypatch,representation,fault):
    c=shop;prepare(c,monkeypatch,site,representation)
    web=load_admin_panel()
    def fail(*a,**kw):raise RuntimeError('synthetic web admin stock fault')
    method={'count':'count_available_configs','state':'check_low_stock_alert_state','admins':'list_admins','reward':'reward_referrer_if_first_purchase','log':'log_admin_action'}.get(fault)
    if method:monkeypatch.setattr(c.db,method,fail)
    if fault=='threshold':
        old=c.db.get_setting
        def setting(key,*a):return fail() if key=='low_stock_threshold' else old(key,*a)
        monkeypatch.setattr(c.db,'get_setting',setting)
    if fault=='product':
        old=c.db.get_product
        def product(pid):return fail() if pid==1 and latch(c) else old(pid)
        monkeypatch.setattr(c.db,'get_product',product)
    # External alert transport exceptions are isolated; delivery transport exceptions run in a background task.
    if fault in {'send_first','send_all','delivery','notify'}:
        original=site.api.send_message
        async def send(token,uid,text,*a,**kw):
            result=await original(token,uid,text,*a,**kw)
            alert='هشدار اتمام موجودی' in text
            if (fault=='send_all' and alert) or (fault=='send_first' and alert and uid==OWNER) or (fault=='notify' and uid==BUYER and text=='✅ خرید شما تایید شد!') or (fault=='delivery' and uid==BUYER and 'لینک اشتراک شما' in text):raise RuntimeError('synthetic web admin stock fault')
            return result
        monkeypatch.setattr(web,'tg_send',send)
        from admin_panel import config_delivery_web
        monkeypatch.setattr(config_delivery_web,'tg_send',send)
    fatal=fault in {'state','product','admins','reward','log'}
    # Both tasks run after the HTTP operation; observe their exceptions without changing scheduling/production.
    response=invoke(c)
    assert response.status_code==(500 if fatal else 200)
    if not fatal:assert response.json()=={'ok':True}
    assert len(c.background_errors)==int(fault in {'notify','delivery'})
    assert all(type(e) is RuntimeError and str(e)=='synthetic web admin stock fault' for e in c.background_errors)
    assert c.db.get_order(c.oid)['status']=='approved'
    assert len([r for r in configs(c) if r[1] and r[2:]==(BUYER,c.oid)])==2
    assert latch(c)==int(fault not in {'count','threshold','state','log'})
    assert c.db.get_wallet_credit(BUYER)==777 and c.db.get_wallet_credit(REFERRER)==(0 if fatal else 23400)
    assert len(delivered(c))==(0 if fatal else 1 if fault=='delivery' else 2)
    assert [e.chat_id for e in warnings(c)]==([OWNER,9002] if fault in {'send_first','send_all','reward','delivery','notify'} else [])
    assert len(admin_logs(c))==int(fault!='log')
    state=dump(c.db);c.trace.clear();c.log.events.clear();response=invoke(c)
    assert response.status_code==400 and not c.trace and dump(c.db)==state and not c.log.events
