"""T050ez/fa: independent helper admission and real SQL latch/failure boundaries."""
import asyncio
import pytest
import stock_alerts
from tests.integration.test_composite_extra_stock_alerts import (
    catalog, setup as prior_setup, ADMINS, alert, latch_raw, dump,
)


def setup(c,mp,kind=None,representation='sqlite',stock=1,threshold='1',latched=0):
    prior_setup(c,mp,'zarinpal',representation,kind,'product',stock,threshold,latched)
    # This is direct alert invocation, before sale: consume none, set exact available count.
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM configs WHERE product_id=? AND id NOT IN (SELECT id FROM configs WHERE product_id=? ORDER BY id LIMIT ?)',(c.pid,c.pid,stock))
    c.calls=[]
    for method in ['count_available_configs','get_setting','check_low_stock_alert_state','list_admins']:
        fn=getattr(c.db,method)
        def call(*args,_fn=fn,_method=method,**kw):
            c.calls.append((_method,args));return _fn(*args,**kw)
        mp.setattr(c.db,method,call)


def invoke(c,pid=None):return asyncio.run(stock_alerts.check_and_notify_low_stock(c.bot.send_message,c.db,c.pid if pid is None else pid))


def frozen(c):
    with c.db._get_conn() as conn:
        tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result={}
        for table in tables:
            assert table.replace('_','').isalnum()
            rows=[dict(r) for r in conn.execute(f'SELECT * FROM "{table}" ORDER BY rowid')]
            if table=='products':
                for row in rows:
                    if row['id']==c.pid:row['low_stock_alert_sent']='<selected latch>'
            result[table]=rows
        return result


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('latched',[0,1])
@pytest.mark.parametrize('boundary',['low','above','invalid','count_fault','setting_fault'])
def test_composite_direct_before_preflight_and_reset(catalog,monkeypatch,caplog,representation,latched,boundary):
    c=catalog;setup(c,monkeypatch,'composite',representation,stock=2 if boundary=='above' else 1,threshold='invalid' if boundary=='invalid' else '1',latched=latched)
    if boundary.endswith('fault'):
        method='count_available_configs' if boundary=='count_fault' else 'get_setting'
        def fail(*a,**kw):c.calls.append(('forbidden_preflight',a));raise RuntimeError('synthetic preflight fault')
        monkeypatch.setattr(c.db,method,fail)
    state=dump(c.db)
    for _ in range(2):
        assert invoke(c) is None
        assert not c.calls and not c.messages and dump(c.db)==state,'missing T051 direct stock admission before preflight/reset'
    assert 'composite' in caplog.text.lower() and 'stock' in caplog.text.lower(),'missing T051 explicit direct stock refusal'
    assert 'Stock' not in caplog.text


@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('stock,threshold,initial,final,send',[(0,'0',0,1,True),(1,'1',0,1,True),(2,'1',1,0,False),(1,'1',1,1,False),(2,'',0,1,True),(0,'-1',1,0,False),(1,'bad',0,0,False)])
def test_direct_threshold_sql_and_repeat(catalog,monkeypatch,kind,representation,stock,threshold,initial,final,send):
    c=catalog;setup(c,monkeypatch,kind,representation,stock,threshold,initial);state=frozen(c)
    assert invoke(c) is None
    assert latch_raw(c)==final
    assert c.messages==([(u,alert(stock,int(threshold or 3))) for u in ADMINS] if send else [])
    assert frozen(c)==state
    c.messages.clear();assert invoke(c) is None and not c.messages and latch_raw(c)==final and frozen(c)==state


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('fault',['count','setting','state','product','admins','send_first','send_all','no_admins','missing_product'])
def test_direct_fault_ordering_and_missing_product(catalog,monkeypatch,representation,kind,fault,caplog):
    c=catalog;setup(c,monkeypatch,kind,representation);state=frozen(c)
    def fail(*a,**kw):raise RuntimeError('synthetic direct alert fault')
    method={'count':'count_available_configs','setting':'get_setting','state':'check_low_stock_alert_state','admins':'list_admins'}.get(fault)
    if method:monkeypatch.setattr(c.db,method,fail)
    if fault=='product':
        old=c.db.get_product;raised=[False]
        def read(pid):
            if latch_raw(c) and not raised[0]:
                raised[0]=True;raise RuntimeError('synthetic direct alert fault')
            return old(pid)
        monkeypatch.setattr(c.db,'get_product',read)
    if fault=='no_admins':monkeypatch.setattr(c.db,'list_admins',lambda:[])
    if fault.startswith('send'):
        async def send(uid,text):
            c.messages.append((uid,text))
            if uid in (ADMINS if fault=='send_all' else ADMINS[:1]):raise RuntimeError('synthetic direct alert fault')
        monkeypatch.setattr(c.bot,'send_message',send)
    pid=999999 if fault=='missing_product' else c.pid
    if fault in {'state','product','admins'}:
        with pytest.raises(RuntimeError,match='synthetic direct alert fault'):invoke(c,pid)
    else:
        try:assert invoke(c,pid) is None
        except RuntimeError as error:raise AssertionError('direct alert isolation violated') from error
    assert latch_raw(c)==int(fault not in {'count','setting','state','missing_product'})
    expected=[(u,alert(0 if fault=='missing_product' else 1,1,'نامشخص' if fault=='missing_product' else 'Stock')) for u in ADMINS] if fault in {'send_first','send_all','missing_product'} else []
    assert c.messages==expected and frozen(c)==state
    if fault.startswith('send'):assert 'ناموفق' in caplog.text
    if fault in {'send_first','send_all','no_admins','admins','product','missing_product'}:
        c.messages.clear();assert invoke(c,pid) is None
        assert c.messages==(expected if fault=='missing_product' else []) and frozen(c)==state


@pytest.mark.parametrize('kind',[None,'legacy'])
def test_direct_restock_reset_and_rearm(catalog,monkeypatch,kind):
    c=catalog;setup(c,monkeypatch,kind)
    assert invoke(c) is None and latch_raw(c)==1
    c.db.add_configs(c.pid,['https://subscription.example.invalid/direct-restock'])
    c.messages.clear();assert invoke(c) is None and latch_raw(c)==0 and not c.messages
    with c.db._get_conn() as conn:conn.execute('UPDATE configs SET is_used=1 WHERE product_id=?',(c.pid,))
    assert invoke(c) is None and latch_raw(c)==1 and c.messages==[(u,alert(0,1)) for u in ADMINS]
