"""T050ff/fg: actual Telegram admin STOCK alert success and failure boundaries."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_order_approval import shop, remote, approve, BUYER, OWNER, configs, admin_logs
from tests._harness.legacy_bot import TelegramLog, RecordingBot
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump

REFERRER=1002

def setup(c,mp,representation,kind=None,marker='product',remaining=1,threshold='1',latched=0):
    c.pid=1
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM configs WHERE product_id=1')
    c.db.add_configs(1,[f'vless://admin-{i}' for i in range(1,remaining+3)])
    c.oid=c.db.create_order(BUYER,1,180000,quantity=2)
    c.db.add_or_update_user(REFERRER,'ref','Ref');c.db.set_referred_by(BUYER,REFERRER)
    c.db.set_setting('referral_percent','13');c.db.set_setting('low_stock_threshold',threshold)
    c.db.set_setting('deliver_individual_configs_enabled','0');c.db.add_admin(9002)
    c.db.add_wallet_credit(BUYER,777)
    with c.db._get_conn() as conn:conn.execute('UPDATE products SET low_stock_alert_sent=? WHERE id=1',(latched,))
    for method,selected in [('get_product',1),('get_order',c.oid)]:
        old=getattr(c.db,method)
        def read(id_,_old=old,_method=method,_selected=selected):
            row=_old(id_)
            if row is None:return None
            d=dict(row)
            if kind is not None and id_==_selected and marker==('product' if _method=='get_product' else 'order'):d['service_kind']=kind
            return as_row(d,representation)
        mp.setattr(c.db,method,read)
    c.other_before=dict(c.db.get_product(2));c.trace=[];c.log=TelegramLog()
    for name in ['claim_order','take_unused_configs','approve_order','log_admin_action','check_low_stock_alert_state','reward_referrer_if_first_purchase']:
        old=getattr(c.db,name)
        def wrapped(*a,_old=old,_name=name,**kw):c.trace.append((_name,a));return _old(*a,**kw)
        mp.setattr(c.db,name,wrapped)


def invoke(c,blocked=()):
    result=asyncio.run(approve(c,c.log,RecordingBot(c.log,blocked_chat_ids=blocked)))
    assert dict(c.db.get_product(2))==c.other_before
    return result


def warnings(c):return [e for e in c.log.events if e.text and 'هشدار اتمام موجودی' in e.text]
def latch(c):
    with c.db._get_conn() as conn:return conn.execute('SELECT low_stock_alert_sent FROM products WHERE id=1').fetchone()[0]
def delivered(c):return [e.text for e in c.log.events if e.text and 'لینک اشتراک شما (برای کپی)' in e.text]


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('remaining,threshold,initial,final,send',[(0,'0',0,1,True),(1,'1',0,1,True),(2,'1',1,0,False),(1,'1',1,1,False),(3,'',0,1,True)])
def test_admin_stock_alert_threshold_and_repeat(shop,monkeypatch,representation,kind,remaining,threshold,initial,final,send):
    c=shop;setup(c,monkeypatch,representation,kind,remaining=remaining,threshold=threshold,latched=initial)
    invoke(c)
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
    assert len(admin_logs(c))==1
    state=dump(c.db);c.trace.clear();c.log.events.clear();invoke(c)
    assert not c.trace and dump(c.db)==state and not warnings(c) and not delivered(c)
    assert [e.text for e in c.log.events]==['این سفارش قبلاً بررسی شده است.']


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['product','order'])
@pytest.mark.parametrize('remaining,latched',[(0,0),(2,1)])
def test_composite_admin_stock_refuses_before_alert_and_claim(shop,monkeypatch,representation,marker,remaining,latched):
    c=shop;setup(c,monkeypatch,representation,'composite',marker,remaining=remaining,latched=latched)
    before=dump(c.db)
    for _ in range(2):
        invoke(c)
        assert not c.trace and dump(c.db)==before,'missing T052 admin STOCK admission before claim/alert'
    assert any('composite' in (e.text or '').lower() for e in c.log.events),'missing T052 explicit admin STOCK refusal'
    assert not any('Stock 30d' in (e.text or '') or 'vless://' in (e.text or '') for e in c.log.events)


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('fault',['count','threshold','state','product','admins','send_first','send_all','reward','delivery','log'])
def test_admin_stock_alert_fault_boundaries(shop,monkeypatch,representation,fault):
    c=shop;setup(c,monkeypatch,representation)
    def fail(*a,**kw):raise RuntimeError('synthetic admin stock fault')
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
    blocked={OWNER} if fault=='send_first' else {OWNER,9002} if fault=='send_all' else {BUYER} if fault=='delivery' else set()
    fatal=fault in {'state','product','admins','reward','log'}
    if fatal:
        with pytest.raises(RuntimeError,match='synthetic admin stock fault'):invoke(c,blocked)
    else:
        try:invoke(c,blocked)
        except RuntimeError as error:raise AssertionError('caller isolation violated') from error
    assert c.db.get_order(c.oid)['status']=='approved'
    assert len([r for r in configs(c) if r[1] and r[2:]==(BUYER,c.oid)])==2
    assert latch(c)==int(fault not in {'count','threshold','state','log'})
    assert c.db.get_wallet_credit(BUYER)==777
    assert c.db.get_wallet_credit(REFERRER)==(0 if fatal else 23400)
    assert bool(delivered(c))==(not fatal and fault!='delivery')
    assert [e.chat_id for e in warnings(c)]==([OWNER,9002] if fault in {'send_first','send_all','reward','delivery'} else [])
    assert len(admin_logs(c))==int(fault!='log')
    state=dump(c.db);c.trace.clear();c.log.events.clear();invoke(c)
    assert not c.trace and dump(c.db)==state and not warnings(c) and not delivered(c)
