"""T050fd/fe: independent actual ordinary/AI STOCK purchase alert callers."""
import asyncio
from types import SimpleNamespace
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_user
from tests.characterization.test_buy_start import shop, stock_product, BUYER, REFERRER, rows, press_buy
from tests._harness.legacy_bot import FakeMessage, FakeUser, RecordingBot, TelegramLog, make_state, find_handler
from tests.integration.test_composite_telegram_payment_policies import closure
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump


def setup(c,mp,representation,kind=None,remaining=1,threshold='1',latched=0,quantity=1):
    c.pid=stock_product(c,links=quantity+remaining);c.quantity=quantity
    c.db.add_wallet_credit(BUYER,1000000);c.db.set_referred_by(BUYER,REFERRER)
    c.db.set_setting('referral_percent','13');c.db.set_setting('low_stock_threshold',threshold)
    c.db.set_setting('deliver_individual_configs_enabled','0')
    c.db.add_admin(9002)
    with c.db._get_conn() as conn:conn.execute('UPDATE products SET low_stock_alert_sent=? WHERE id=?',(latched,c.pid))
    get=c.db.get_product
    def read(pid):
        row=get(pid)
        if row is None:return None
        d=dict(row)
        if pid==c.pid and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    mp.setattr(c.db,'get_product',read)
    c.other=stock_product(c,links=2);c.other_before=dict(c.db.get_product(c.other));c.other_configs=rows(c,'SELECT * FROM configs WHERE product_id=?',(c.other,))
    c.log=TelegramLog();c.trace=[]
    for name in ['take_unused_configs','approve_order','check_low_stock_alert_state','reward_referrer_if_first_purchase']:
        original=getattr(c.db,name)
        def wrapped(*a,_name=name,_original=original,**kw):
            c.trace.append((_name,a));return _original(*a,**kw)
        mp.setattr(c.db,name,wrapped)
    c.ai=closure(find_handler(c.router,'message','ai_chat_receive'),'_ai_finalize_wallet_purchase')


def invoke(c,flow,blocked=()):
    async def run():
        bot=RecordingBot(c.log,blocked_chat_ids=blocked)
        msg=FakeMessage(c.log,BUYER,from_user=FakeUser(BUYER,'ali','Ali'))
        if flow=='ai':await c.ai(msg,bot,c.pid,c.quantity)
        else:
            from tests._harness.legacy_bot import FakeCallbackQuery
            call=FakeCallbackQuery(c.log,FakeUser(BUYER,'ali','Ali'),f'buy_start:{c.pid}:{c.quantity}',msg)
            await find_handler(c.router,'callback_query','cb_buy_start')(call,make_state(BUYER),bot)
    asyncio.run(run())
    assert dict(c.db.get_product(c.other))==c.other_before and rows(c,'SELECT * FROM configs WHERE product_id=?',(c.other,))==c.other_configs


def warnings(c):return [e for e in c.log.events if e.text and 'هشدار اتمام موجودی' in e.text]
def latch(c):return c.db.get_product(c.pid)['low_stock_alert_sent']
def used(c):return rows(c,'SELECT id,is_used,assigned_user_id,order_id FROM configs WHERE product_id=? ORDER BY id',(c.pid,))


@pytest.mark.parametrize('flow',['ordinary','ai'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('remaining,threshold,latched,expected',[(0,'0',0,1),(1,'1',0,1),(2,'1',1,0),(1,'1',1,1),(3,'',0,1)])
def test_inline_stock_threshold_success(shop,monkeypatch,flow,representation,kind,remaining,threshold,latched,expected):
    c=shop;setup(c,monkeypatch,representation,kind,remaining,threshold,latched,quantity=2)
    invoke(c,flow)
    order=c.db.get_order(1)
    assert (order['status'],order['user_id'],order['quantity'],order['wallet_used'],order['final_price'])==('approved',BUYER,2,200000,0)
    assert c.db.get_wallet_credit(BUYER)==800000 and c.db.get_wallet_credit(REFERRER)==26000
    assert used(c)[:2]==[(1,1,BUYER,1),(2,1,BUYER,1)]
    assert all(r[1:]==(0,None,None) for r in used(c)[2:])
    assert latch(c)==expected and c.db.count_available_configs(c.pid)==remaining
    alert=warnings(c);should=remaining<=int(threshold or 3) and not latched
    assert [e.chat_id for e in alert]==([9001,9002] if should else [])
    if should:assert all(e.text==('⚠️ هشدار اتمام موجودی\n\n'+f'📦 محصول «Stock 30d» فقط {remaining} کانفیگ آزاد باقی مانده (آستانه‌ی هشدار: {int(threshold or 3)}).\nلطفاً هرچه زودتر کانفیگ جدید به انبار اضافه کنید.') for e in alert)
    assert [n for n,_ in c.trace]==['take_unused_configs','approve_order','check_low_stock_alert_state','reward_referrer_if_first_purchase']
    links=[e.text for e in c.log.events if e.text and 'لینک اشتراک شما (برای کپی)' in e.text]
    assert links==['🔗 لینک اشتراک شما (برای کپی):\n`vless://stock-1`','🔗 لینک اشتراک شما (برای کپی):\n`vless://stock-2`']
    assert sum(e.kind=='send_photo' and e.chat_id==BUYER for e in c.log.events)==2
    assert c.db.get_user(BUYER)['referral_first_purchase_rewarded']==1


@pytest.mark.parametrize('flow',['ordinary','ai'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('fault',['count','threshold','state','product','admins','send_first','send_all','delivery','reward'])
def test_inline_stock_fault_ordering(shop,monkeypatch,flow,representation,fault):
    c=shop;setup(c,monkeypatch,representation)
    def fail(*a,**kw):raise RuntimeError('synthetic inline alert fault')
    if fault=='count':
        count=c.db.count_available_configs
        def read(pid):
            if c.db.get_order(1) is not None and c.db.get_order(1)['status']=='approved':return fail()
            return count(pid)
        monkeypatch.setattr(c.db,'count_available_configs',read)
    if fault=='threshold':c.db.set_setting('low_stock_threshold','invalid')
    if fault=='state':monkeypatch.setattr(c.db,'check_low_stock_alert_state',fail)
    if fault=='product':
        original=c.db.get_product
        def read(pid):
            with c.db._get_conn() as conn:sent=conn.execute('SELECT low_stock_alert_sent FROM products WHERE id=?',(c.pid,)).fetchone()[0]
            if pid==c.pid and sent:return fail()
            return original(pid)
        monkeypatch.setattr(c.db,'get_product',read)
    if fault=='admins':
        listing=c.db.list_admins
        def read():
            if latch(c):return fail()
            return listing()
        monkeypatch.setattr(c.db,'list_admins',read)
    if fault=='reward':monkeypatch.setattr(c.db,'reward_referrer_if_first_purchase',fail)
    blocked=(9001,) if fault=='send_first' else (9001,9002) if fault=='send_all' else (BUYER,) if fault=='delivery' else ()
    try:invoke(c,flow,blocked)
    except RuntimeError as error:raise AssertionError('inline outer handler must catch alert failure') from error
    assert c.db.get_order(1)['status']=='approved' and used(c)[0]==(1,1,BUYER,1)
    assert c.db.get_wallet_credit(BUYER)==900000
    with c.db._get_conn() as conn:sent=conn.execute('SELECT low_stock_alert_sent FROM products WHERE id=?',(c.pid,)).fetchone()[0]
    assert sent==int(fault not in {'count','threshold','state'})
    stops=fault in {'state','product','admins','reward'}
    assert c.db.get_wallet_credit(REFERRER)==(0 if stops else 13000)
    delivered=[e for e in c.log.events if e.kind=='send_photo' and e.chat_id==BUYER]
    assert bool(delivered)==(not stops)
    if fault=='delivery':assert delivered and not delivered[0].delivered
    if stops or fault=='delivery':assert any(e.text and 'بازگردانده' in e.text or e.text and 'برگشت' in e.text for e in c.log.events)
    else:assert sum(e.kind=='send_photo' and e.delivered for e in c.log.events)==1
    if fault.startswith('send'):
        assert [e.chat_id for e in warnings(c)]==[9001,9002]
        assert [e.delivered for e in warnings(c)]==([False,True] if fault=='send_first' else [False,False])
    # Rejection after approval cannot undo allocation or debit; no repair inferred.
    before=dump(c.db);assert c.db.reject_order(1) is False and dump(c.db)==before


@pytest.mark.parametrize('flow',['ordinary','ai'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
def test_inline_repeat_is_fresh_purchase_not_recovery(shop,monkeypatch,flow,representation):
    c=shop;setup(c,monkeypatch,representation,remaining=4,threshold='4')
    invoke(c,flow);assert len(warnings(c))==2
    invoke(c,flow)
    assert len(warnings(c))==2 and latch(c)==1
    assert [c.db.get_order(i)['status'] for i in [1,2]]==['approved','approved']
    assert used(c)[:2]==[(1,1,BUYER,1),(2,1,BUYER,2)]
    assert c.db.get_wallet_credit(BUYER)==800000 and c.db.get_wallet_credit(REFERRER)==13000
    assert sum(e.kind=='send_photo' for e in c.log.events)==2


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('latched',[0,1])
@pytest.mark.parametrize('remaining',[0,2])
def test_composite_ai_actual_execution_refuses_before_money(shop,monkeypatch,representation,latched,remaining):
    c=shop;setup(c,monkeypatch,representation,'composite',remaining=remaining,latched=latched)
    with c.db._get_conn() as conn:conn.execute('UPDATE products SET name=? WHERE id=?',('SECRET-COMPOSITE',c.pid))
    before=dump(c.db)
    for _ in range(2):invoke(c,'ai')
    assert dump(c.db)==before and c.trace==[], 'missing T053 AI execution composite admission before money/allocation/alert'
    assert len(c.log.events)==2 and all('composite' in (e.text or '').lower() for e in c.log.events), 'missing T053 explicit composite refusal'

    assert 'SECRET-COMPOSITE' not in str(c.log.events) and 'vless://' not in str(c.log.events)
