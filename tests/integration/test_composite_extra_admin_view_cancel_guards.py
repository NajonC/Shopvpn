"""T050cz/da: actual admin view/cancel callers, isolated selected references."""
import asyncio
import pytest
from aiogram import Router
from tests.integration.test_composite_extra_admin_guards import catalog, setup, admin, egp, OWNER, USER_ID, dump
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests.integration.test_composite_legacy_guards import as_row
from tests._harness.legacy_bot import FakeUser, FakeMessage, FakeCallbackQuery, TelegramLog, find_handler


def prepare(c,mp,representation,kind=None,marker='order',key='zarinpal',status='new'):
    setup(c,mp,representation,kind,marker)
    with c.db._get_conn() as conn:
        conn.execute('UPDATE extra_gateway_invoices SET gateway=?,status=?,payable_amount=990,payment_url=?,created_at=?,updated_at=? WHERE id=?',(key,status,'https://payments.invalid/synthetic','2026-01-01 00:00:00','2026-01-01T00:00:00',c.iid))
        # Keep selected invoices recent during list housekeeping; view timestamps
        # remain deterministic through a getter projection only in view tests.
        conn.execute("UPDATE extra_gateway_invoices SET created_at=datetime('now'),updated_at=datetime('now') WHERE id=?",(c.iid,))
    original=c.db.get_extra_invoice
    def getter(iid):
        row=original(iid)
        return as_row(dict(row),representation) if row is not None else None
    mp.setattr(c.db,'get_extra_invoice',getter)
    c.views=[];c.effects=[];c.router=Router()
    async def replace(call,text,**kw):c.views.append((call.from_user.id,text,kw))
    async def unused(*args,**kw):raise AssertionError('unexpected settings UI')
    def ident(data,prefix):
        try:return int(data.split(':')[1])
        except (ValueError,IndexError):return None
    admin.register(c.router,c.db,True,lambda uid:uid==OWNER,lambda uid:uid==OWNER,unused,replace,unused,ident)
    for name in ['cancel_and_delete_extra_invoice','expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']:
        fn=getattr(c.db,name)
        def wrap(*args,_name=name,_fn=fn,**kw):c.effects.append((_name,args,kw));return _fn(*args,**kw)
        mp.setattr(c.db,name,wrap)


def invoke(c,entry,uid=OWNER,suffix=None):
    async def run():
        log=TelegramLog();user=FakeUser(uid);name='view' if entry=='view' else 'cancel'
        call=FakeCallbackQuery(log,user,f'{name}_xgw_invoice:{c.iid if suffix is None else suffix}',FakeMessage(log,uid,from_user=user))
        await find_handler(c.router,'callback_query',f'cb_{name}_xgw_invoice')(call)
        return log.events
    return asyncio.run(run())


@pytest.mark.parametrize('entry',['view','cancel'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status',['new','pending','completed'])
def test_composite_admin_view_cancel(catalog,monkeypatch,entry,key,representation,marker,status):
    c=catalog;prepare(c,monkeypatch,representation,'composite',marker,key,status)
    before=dump(c.db)
    for _ in range(2):
        events=invoke(c,entry)
        assert len(events)==1 and events[0].show_alert and 'composite' in (events[0].text or '').lower(), 'missing T052 admin composite refusal'
        assert not c.views and not c.effects and not c.trace and not c.invoice_trace and not c.remote and dump(c.db)==before


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('status',['new','pending','completed','expired','cancelled'])
def test_legacy_admin_invoice_view(catalog,monkeypatch,representation,kind,key,status):
    c=catalog;prepare(c,monkeypatch,representation,kind,key=key,status=status)
    invoice=dict(c.db.get_extra_invoice(c.iid));before=dump(c.db)
    for _ in range(2):
        events=invoke(c,'view');assert len(events)==1 and events[0].text is None
    assert len(c.views)==2 and c.views[0]==c.views[1] and c.views[0][0]==OWNER
    meta=egp.registry.GATEWAYS[key]
    text=f"{meta['icon']} فاکتور {meta['title']} #{c.iid}\n🧾 سفارش: #{c.oid}\n👤 کاربر: {USER_ID}\n💰 مبلغ: 900 تومان\n"
    text+= '⭐ تعداد استارز: 990\n' if key=='tgstars' else '💳 مبلغ قابل پرداخت: 990 تومان\n'
    text+=f"🔖 شناسه درگاه: synthetic-remote\n📌 وضعیت: {admin._STATUS_TEXT[status]}\n🕐 ایجاد: {invoice['created_at']}"
    assert c.views[0][1]==text
    buttons=[b for row in c.views[0][2]['reply_markup'].inline_keyboard for b in row]
    expected=([('🔗 باز کردن فاکتور',None,'https://payments.invalid/synthetic')]+([] if key=='tgstars' else [('🔄 بررسی وضعیت',f'check_xgw_invoice:{c.iid}',None)])+[('❌ لغو و حذف فاکتور',f'cancel_xgw_invoice:{c.iid}',None)]) if status in {'new','pending'} else []
    expected+=[('⬅️ بازگشت',f'adm_xgw_payments:{key}',None)]
    assert [(b.text,b.callback_data,b.url) for b in buttons]==expected
    assert dump(c.db)==before and not c.effects and not c.trace and not c.remote


@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('status',['new','pending','completed','expired','cancelled'])
def test_legacy_admin_invoice_cancel(catalog,monkeypatch,representation,kind,key,status):
    c=catalog;prepare(c,monkeypatch,representation,kind,key=key,status=status)
    decoy=dict(c.db.get_extra_invoice(c.decoy))
    retained=[line for line in dump(c.db) if not line.startswith('INSERT INTO "extra_gateway_invoices"')]
    events=invoke(c,'cancel')
    assert len(events)==1 and events[0].text=='✅ فاکتور لغو و حذف شد.'
    assert c.db.get_extra_invoice(c.iid) is None and dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert [line for line in dump(c.db) if not line.startswith('INSERT INTO "extra_gateway_invoices"')]==retained
    assert c.effects==[('cancel_and_delete_extra_invoice',(c.iid,),{}),('expire_stale_extra_invoices',(),{}),('purge_old_extra_invoices',(7,),{}),('list_extra_invoices',(50,key),{})]
    assert len(c.views)==1 and c.views[0][0]==OWNER and egp.registry.GATEWAYS[key]['title'] in c.views[0][1]
    assert 'هیچ پرداختی ثبت نشده است.' in c.views[0][1] if key!='zarinpal' else 'به‌صورت خودکار تایید می‌شوند' in c.views[0][1]
    before=dump(c.db);c.effects.clear();c.views.clear()
    events=invoke(c,'cancel')
    assert len(events)==1 and events[0].show_alert and events[0].text=='فاکتور یافت نشد یا قبلاً حذف شده.'
    assert not c.effects and not c.views and dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('entry',['view','cancel'])
@pytest.mark.parametrize('scenario',['unauthorized','malformed','missing'])
def test_admin_view_cancel_opaque(catalog,monkeypatch,entry,scenario):
    c=catalog;prepare(c,monkeypatch,'sqlite','composite')
    before=dump(c.db)
    events=invoke(c,entry,USER_ID if scenario=='unauthorized' else OWNER,'bad' if scenario=='malformed' else 99999 if scenario=='missing' else None)
    assert len(events)==1 and events[0].text==(None if scenario=='unauthorized' else 'فاکتور یافت نشد.' if entry=='view' else 'فاکتور یافت نشد یا قبلاً حذف شده.')
    assert not c.effects and not c.views and not c.trace and not c.remote and dump(c.db)==before
