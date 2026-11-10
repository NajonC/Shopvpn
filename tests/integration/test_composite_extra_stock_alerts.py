"""T050et/eu: actual extra STOCK threshold/latch and notification faults."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import extra_gateway_payment as egp
from tests.integration.test_composite_extra_stock_fulfillment import setup as stock_setup
from tests.integration.test_composite_gateway_stock_guards import catalog, USER_ID, REFERRER, SUCCESS, PRIOR, dump, rows

ADMINS=[81001,81002]

def setup(c,mp,gateway,representation,kind=None,marker='both',stock=1,threshold='1',latched=0):
    stock_setup(c,mp,gateway,representation,kind,marker,quantity=2)
    # Two decoys guarantee invoice ID != order ID, even if fixture IDs change.
    c.db.create_extra_invoice(gateway,'order',99997,USER_ID,1)
    iid=c.db.create_extra_invoice(gateway,'order',c.oid,USER_ID,900)
    c.invoice=c.db.get_extra_invoice(iid)
    assert iid!=c.oid
    c.db.set_setting('low_stock_threshold',threshold)
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM configs WHERE product_id=? AND id NOT IN (SELECT id FROM configs WHERE product_id=? ORDER BY id LIMIT ?)',(c.pid,c.pid,stock+2))
        conn.execute('UPDATE products SET low_stock_alert_sent=? WHERE id=?',(latched,c.pid))
    with c.db._get_conn() as conn:conn.execute('DELETE FROM admins')
    for uid in ADMINS:c.db.add_admin(uid)
    c.messages=[]
    async def send(uid,text):c.messages.append((uid,text))
    mp.setattr(c.bot,'send_message',send)


def invoke(c):return asyncio.run(egp.deliver(c.db,c.bot,c.invoice,c.notify))

def latch(c):return c.db.get_product(c.pid)['low_stock_alert_sent']

def alert(stock,threshold,name='Stock'):
    return ('⚠️ هشدار اتمام موجودی\n\n'+f'📦 محصول «{name}» فقط {stock} کانفیگ آزاد باقی مانده '+f'(آستانه‌ی هشدار: {threshold}).\n'+'لطفاً هرچه زودتر کانفیگ جدید به انبار اضافه کنید.')

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('latched',[0,1])
def test_composite_alert_refused(catalog,monkeypatch,gateway,representation,marker,latched):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker,latched=latched)
    before=dump(c.db)
    assert 'composite' in invoke(c).lower()
    assert dump(c.db)==before and not c.trace and not c.messages

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('stock,threshold,latched,expected',[(0,'1',0,1),(1,'1',0,1),(2,'1',0,0),(1,'1',1,1),(2,'1',1,0),(3,'',0,1),(3,'0',0,0)])
def test_stock_threshold_and_repeat(catalog,monkeypatch,gateway,representation,kind,stock,threshold,latched,expected):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind,stock=stock,threshold=threshold,latched=latched)
    assert invoke(c)==SUCCESS
    limit=int(threshold or 3)
    sends=[(u,alert(stock,limit)) for u in ADMINS] if stock<=limit and not latched else []
    assert c.messages[:len(sends)]==sends
    assert len(c.messages)==len(sends)+1 and c.messages[-1][0]==REFERRER
    assert latch(c)==expected and c.db.count_available_configs(c.pid)==stock
    assert all(r['is_used'] and r['order_id']==c.oid for r in rows(c)[:2])
    assert c.db.get_wallet_credit(REFERRER)==130 and c.db.get_order(c.oid)['status']=='approved'
    assert [e[0] for e in c.trace][-3:]==['delivery','reward_referrer_if_first_purchase','admin']
    state=dump(c.db);c.messages.clear();c.trace.clear()
    assert invoke(c)==PRIOR and dump(c.db)==state and not c.messages and not c.trace

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('fault',['count','threshold','state','product','admins','send_first','send_all','no_admins'])
def test_stock_alert_fault_isolation(catalog,monkeypatch,gateway,representation,fault,caplog):
    c=catalog;setup(c,monkeypatch,gateway,representation)
    def fail(*a,**kw):raise RuntimeError('synthetic alert fault')
    if fault=='count':monkeypatch.setattr(c.db,'count_available_configs',fail)
    if fault=='threshold':c.db.set_setting('low_stock_threshold','invalid')
    if fault=='state':monkeypatch.setattr(c.db,'check_low_stock_alert_state',fail)
    if fault=='product':
        original=c.db.get_product
        c.product_fault_raised=False
        def read(pid):
            if latch_raw(c) and not c.product_fault_raised:
                c.product_fault_raised=True
                raise RuntimeError('synthetic alert fault')
            return original(pid)
        monkeypatch.setattr(c.db,'get_product',read)
    if fault=='admins':monkeypatch.setattr(c.db,'list_admins',fail)
    if fault=='no_admins':monkeypatch.setattr(c.db,'list_admins',lambda:[])
    if fault.startswith('send'):
        async def send(uid,text):
            c.messages.append((uid,text))
            if uid in (ADMINS if fault=='send_all' else ADMINS[:1]):raise RuntimeError('synthetic alert fault')
        monkeypatch.setattr(c.bot,'send_message',send)
    raises=fault in {'state','product','admins'}
    if raises:
        with pytest.raises(RuntimeError,match='synthetic alert fault'):invoke(c)
    else:
        try:result=invoke(c)
        except RuntimeError as error:raise AssertionError('alert isolation violated') from error
        assert result==SUCCESS
    assert c.db.get_order(c.oid)['status']=='approved' and sum(r['is_used'] for r in rows(c))==2
    assert latch_raw(c)==int(fault not in {'count','threshold','state'})
    assert c.db.get_wallet_credit(REFERRER)==(0 if raises else 130)
    assert ('delivery' in [e[0] for e in c.trace])== (not raises)
    warnings=[e for e in c.messages if e[0] in ADMINS]
    assert warnings==([(u,alert(1,1)) for u in ADMINS] if fault.startswith('send') else [])
    if fault.startswith('send'):assert 'ناموفق' in caplog.text
    state=dump(c.db);c.messages.clear();c.trace.clear()
    assert invoke(c)==PRIOR and dump(c.db)==state and not c.trace and not c.messages


def latch_raw(c):
    with c.db._get_conn() as conn:return conn.execute('SELECT low_stock_alert_sent FROM products WHERE id=?',(c.pid,)).fetchone()[0]

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
def test_restock_rearms_next_sale(catalog,monkeypatch,gateway):
    c=catalog;setup(c,monkeypatch,gateway,'dict')
    assert invoke(c)==SUCCESS and latch(c)==1
    c.db.add_configs(c.pid,['https://subscription.example.invalid/refill1','https://subscription.example.invalid/refill2'])
    c.oid=c.db.create_order(USER_ID,c.pid,1000,quantity=1)
    iid=c.db.create_extra_invoice(gateway,'order',c.oid,USER_ID,1000);c.invoice=c.db.get_extra_invoice(iid)
    c.messages.clear();assert invoke(c)==SUCCESS and latch(c)==0 and not c.messages
    c.oid=c.db.create_order(USER_ID,c.pid,1000,quantity=1)
    iid=c.db.create_extra_invoice(gateway,'order',c.oid,USER_ID,1000);c.invoice=c.db.get_extra_invoice(iid)
    assert invoke(c)==SUCCESS and latch(c)==1 and c.messages==[(u,alert(1,1)) for u in ADMINS]
