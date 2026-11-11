"""T050ev/ew: actual notification registry and admin warning fanout."""
import asyncio
import pytest
from tests.integration.test_composite_extra_stock_alerts import (
    catalog, setup as alert_setup, ADMINS, egp, USER_ID, REFERRER, SUCCESS, PRIOR, dump, rows,
)


def setup(c,mp,gateway,representation,kind=None,marker='both'):
    alert_setup(c,mp,gateway,representation,kind,marker,stock=2,threshold='0')
    mp.setattr(egp,'_order_notifiers',{})
    c.notifications=[]
    def callback(label,fail=False):
        async def notify(bot,oid):
            assert bot is c.bot and oid==c.oid
            c.notifications.append((label,bot,oid,c.db.get_order(oid)['status'],c.db.get_wallet_credit(REFERRER)))
            if fail:raise RuntimeError('synthetic notifier fault')
        return notify
    c.callback=callback


def invoke(c,notifier=None):return asyncio.run(egp.deliver(c.db,c.bot,c.invoice,notifier))

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('selection',['explicit','registered','both','replacement','other_db','none','failure'])
def test_registry_selection_and_repeat(catalog,monkeypatch,gateway,representation,kind,selection):
    c=catalog;setup(c,monkeypatch,gateway,representation,kind)
    explicit=c.callback('explicit');stored=c.callback('stored');foreign=object()
    egp.register_order_notifier(foreign,c.callback('foreign'))
    if selection in {'registered','both','replacement','failure'}:egp.register_order_notifier(c.db,stored)
    if selection=='replacement':egp.register_order_notifier(c.db,c.callback('replacement'))
    if selection=='failure':egp.register_order_notifier(c.db,c.callback('failure',True))
    assert egp._order_notifiers.get(id(foreign)) is not None
    invoice=dict(c.invoice)
    try:result=invoke(c,explicit if selection in {'explicit','both'} else None)
    except RuntimeError as error:raise AssertionError('notifier failure isolation violated') from error
    assert result==SUCCESS
    label='explicit' if selection in {'explicit','both'} else 'stored' if selection=='registered' else selection
    assert c.notifications==([] if selection in {'none','other_db'} else [(label,c.bot,c.oid,'approved',130)])
    assert c.db.get_order(c.oid)['status']=='approved' and c.db.get_wallet_credit(REFERRER)==130
    assert c.db.get_wallet_credit(USER_ID)==0 and c.messages[-1][0]==REFERRER
    assert sum(r['is_used'] for r in rows(c))==2
    assert dict(c.db.get_extra_invoice(invoice['id']))==invoice
    state=dump(c.db);c.trace.clear();c.messages.clear();c.notifications.clear()
    assert invoke(c,explicit if selection in {'explicit','both'} else None)==PRIOR
    assert dump(c.db)==state and not c.trace and not c.messages and not c.notifications

@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('boundary',['pending','rejected','processing','shortage'])
def test_composite_warning_and_registry_refused(catalog,monkeypatch,gateway,representation,marker,boundary):
    c=catalog;setup(c,monkeypatch,gateway,representation,'composite',marker)
    egp.register_order_notifier(c.db,c.callback('stored'))
    with c.db._get_conn() as conn:
        if boundary=='shortage':conn.execute('DELETE FROM configs WHERE product_id=?',(c.pid,))
        elif boundary!='pending':conn.execute('UPDATE orders SET status=? WHERE id=?',(boundary,c.oid))
    state=dump(c.db)
    assert 'composite' in invoke(c,c.callback('explicit')).lower()
    assert dump(c.db)==state and not c.trace and not c.messages and not c.notifications


@pytest.mark.parametrize('gateway',['zarinpal','tgstars'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('boundary',['missing','rejected','processing','shortage'])
@pytest.mark.parametrize('fault',['none','send_first','send_all','no_admins','list_admins'])
def test_actual_admin_warnings(catalog,monkeypatch,tmp_path,gateway,representation,boundary,fault):
    c=catalog;setup(c,monkeypatch,gateway,representation)
    # Separate synthetic tenant has a different recipient and must never receive warnings.
    foreign=type(c.db)(str(tmp_path/'foreign-notification.db'));foreign.init_db(81999)
    egp.register_order_notifier(foreign,c.callback('foreign'))
    egp.register_order_notifier(c.db,c.callback('stored'))
    if boundary=='missing':
        c.oid=99999
        with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET ref_id=? WHERE id=?',(c.oid,c.invoice['id']))
        c.invoice=c.db.get_extra_invoice(c.invoice['id'])
    elif boundary=='shortage':
        with c.db._get_conn() as conn:conn.execute('DELETE FROM configs WHERE product_id=?',(c.pid,))
    else:
        with c.db._get_conn() as conn:conn.execute('UPDATE orders SET status=? WHERE id=?',(boundary,c.oid))
    if fault=='no_admins':
        with c.db._get_conn() as conn:conn.execute('DELETE FROM admins')
    if fault=='list_admins':
        def fail():raise RuntimeError('synthetic admins fault')
        monkeypatch.setattr(c.db,'list_admins',fail)
    async def send(uid,text):
        c.messages.append((uid,text))
        if uid in (ADMINS if fault=='send_all' else ADMINS[:1] if fault=='send_first' else []):raise RuntimeError('synthetic send fault')
    monkeypatch.setattr(c.bot,'send_message',send)
    text=('⚠️ پرداخت شما دریافت شد ولی سفارش یافت نشد. با پشتیبانی تماس بگیرید.' if boundary=='missing' else '⚠️ پرداخت تایید شد ولی موجودی هم‌زمان تمام شده؛ ادمین به‌زودی دستی رسیدگی می‌کند.' if boundary=='shortage' else '⚠️ پرداخت شما دریافت شد ولی این سفارش دیگر فعال نیست. با پشتیبانی تماس بگیرید.')
    title=egp.registry.GATEWAYS[gateway]['title']
    warning=(f'⚠️ پرداخت {title} برای سفارش #{c.oid} دریافت شد ولی سفارش پیدا نشد.' if boundary=='missing' else f'⚠️ پرداخت {title} برای سفارش #{c.oid} (کاربر {USER_ID}) تایید شد ولی تحویل خودکار ناموفق بود:\n{text}' if boundary=='shortage' else f'⚠️ پرداخت {title} برای سفارش #{c.oid} (کاربر {USER_ID}) دریافت شد ولی وضعیت سفارش «{boundary}» است. لطفاً دستی رسیدگی کنید.')
    state=warning_state(c);other=dump(foreign);invoice=dict(c.invoice)
    for _ in range(2):
        c.messages.clear();c.trace.clear()
        if fault=='list_admins':
            with pytest.raises(RuntimeError,match='synthetic admins fault'):invoke(c)
        else:
            try:result=invoke(c)
            except RuntimeError as error:raise AssertionError('admin send isolation violated') from error
            assert result==text
        assert c.messages==([] if fault in {'no_admins','list_admins'} else [(uid,warning) for uid in ADMINS])
        if boundary=='shortage':assert c.db.get_order(c.oid)['updated_at'] is not None
        assert not c.notifications and dump(foreign)==other
        assert [e[0] for e in c.trace]==(['claim_order','take_unused_configs','release_order_claim'] if boundary=='shortage' else [])
        assert warning_state(c)==state and dict(c.db.get_extra_invoice(invoice['id']))==invoice


def warning_state(c):
    # A shortage claim/release deliberately refreshes only the selected order's
    # updated_at. Preserve and compare every other field of every table.
    with c.db._get_conn() as conn:
        tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result={}
        for table in tables:
            assert table.replace('_','').isalnum()
            data=[dict(r) for r in conn.execute(f'SELECT * FROM "{table}" ORDER BY rowid')]
            if table=='orders':
                for row in data:
                    if row['id']==c.oid:
                        if row['status']=='pending':
                            row['updated_at']='<claim-release timestamp>'
            result[table]=data
        return result
