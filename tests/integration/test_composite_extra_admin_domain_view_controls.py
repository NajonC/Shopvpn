"""T050dh/di: upstream reference domains and independently pinned invoice views."""
import pytest
from tests.integration.test_composite_extra_cancel_alias_guards import alias, STATUSES
from tests.integration.test_composite_extra_admin_view_cancel_guards import catalog, prepare, invoke, dump, USER_ID, OWNER
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests._harness.legacy_bot import find_handler

STATUS={'new':'🟡 جدید','pending':'🟠 در انتظار','completed':'🟢 تکمیل‌شده','expired':'🔴 منقضی‌شده','cancelled':'🔴 لغوشده'}
META={'zarinpal':('🟡','زرین‌پال')}  # Unused: registered labels are checked by previous management tests.


def controls(c):
    return [(b.text,b.callback_data,b.url) for row in c.views[-1][2]['reply_markup'].inline_keyboard for b in row]


@pytest.mark.parametrize('entry',['view','cancel'])
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('kind',['wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',STATUSES)
def test_admin_reference_domains(catalog,monkeypatch,entry,key,kind,status):
    c=catalog;alias(c,monkeypatch,'global_renewal_target','composite','sqlite')
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET kind=?,gateway=?,status=? WHERE id=?',(kind,key,status,c.iid))
    before=dump(c.db);decoy=dict(c.db.get_extra_invoice(c.decoy));retained=[s for s in before if not s.startswith('INSERT INTO "extra_gateway_invoices"')]
    events=invoke(c,entry)
    assert len(events)==1 and events[0].text==(None if entry=='view' else '✅ فاکتور لغو و حذف شد.')
    assert len(c.views)==1 and c.views[0][0]==OWNER
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy
    if entry=='view':
        assert dump(c.db)==before and not c.effects
        assert ('👛 شارژ کیف پول' if kind=='wallet_topup' else '🏪 هزینه نمایندگی')+f': #{c.oid}' in c.views[0][1]
        assert f'👤 کاربر: {USER_ID}\n💰 مبلغ: 900 تومان' in c.views[0][1]
    else:
        assert c.db.get_extra_invoice(c.iid) is None
        assert [s for s in dump(c.db) if not s.startswith('INSERT INTO "extra_gateway_invoices"')]==retained
        assert [x[0] for x in c.effects]==['cancel_and_delete_extra_invoice','expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
    assert not c.trace and not c.remote and not c.invoice_trace


def expected_view(c,key,status):
    from extra_gateway_registry import GATEWAYS as registry
    inv=dict(c.db.get_extra_invoice(c.iid));meta=registry.get(key,{'icon':'💠','title':key})
    text=f"{meta['icon']} فاکتور {meta['title']} #{c.iid}\n🧾 سفارش: #{c.oid}\n👤 کاربر: {USER_ID}\n💰 مبلغ: 900 تومان\n"
    if key=='tgstars':text+=f"⭐ تعداد استارز: {inv['payable_amount']}\n"
    elif inv['payable_amount'] not in (None,0,900):text+=f"💳 مبلغ قابل پرداخت: {int(inv['payable_amount']):,} تومان\n"
    if inv['remote_id']:text+=f"🔖 شناسه درگاه: {inv['remote_id']}\n"
    text+=f"📌 وضعیت: {STATUS.get(status,status or '---')}\n🕐 ایجاد: {inv['created_at'] or '---'}"
    active=status in ['new','pending'];buttons=[]
    if active and inv['payment_url']:buttons.append(('🔗 باز کردن فاکتور',None,inv['payment_url']))
    if active:
        if key!='tgstars':buttons.append(('🔄 بررسی وضعیت',f'check_xgw_invoice:{c.iid}',None))
        buttons.append(('❌ لغو و حذف فاکتور',f'cancel_xgw_invoice:{c.iid}',None))
    buttons.append(('⬅️ بازگشت',f'adm_xgw_payments:{key}',None))
    return text,buttons


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('status',STATUSES)
def test_independent_view_status(catalog,monkeypatch,key,status):
    c=catalog;prepare(c,monkeypatch,'sqlite',key=key,status=status)
    text,buttons=expected_view(c,key,status);before=dump(c.db)
    events=invoke(c,'view')
    assert len(events)==1 and events[0].text is None
    assert c.views[0][1]==text and controls(c)==buttons
    assert dump(c.db)==before and not c.effects and not c.trace and not c.remote


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('variant',['no_url','no_remote','equal_payable','zero_payable','unknown_status','null_status','unknown_gateway','null_created'])
def test_view_field_boundaries(catalog,monkeypatch,key,variant):
    c=catalog;prepare(c,monkeypatch,'sqlite',key=key,status='pending')
    field,value={'no_url':('payment_url',None),'no_remote':('remote_id',None),'equal_payable':('payable_amount',900),'zero_payable':('payable_amount',0),'unknown_status':('status','synthetic_status'),'null_status':('status',None),'unknown_gateway':('gateway','synthetic_gateway'),'null_created':('created_at',None)}[variant]
    # These fields have nullable presentation semantics in existing schema.
    with c.db._get_conn() as conn:conn.execute(f'UPDATE extra_gateway_invoices SET {field}=? WHERE id=?',(value,c.iid))
    selected=dict(c.db.get_extra_invoice(c.iid));text,buttons=expected_view(c,selected['gateway'],selected['status']);before=dump(c.db)
    events=invoke(c,'view');assert len(events)==1 and events[0].text is None
    assert c.views[0][1]==text and controls(c)==buttons
    assert dump(c.db)==before and not c.effects and not c.trace and not c.remote


@pytest.mark.parametrize('entry',['view','cancel'])
@pytest.mark.parametrize('failure',['lookup','render'])
def test_admin_database_ui_failures(catalog,monkeypatch,entry,failure):
    c=catalog;prepare(c,monkeypatch,'sqlite');before=dump(c.db)
    if failure=='lookup':
        def fail(*a,**kw):raise RuntimeError('synthetic lookup')
        monkeypatch.setattr(c.db,'get_extra_invoice',fail)
    else:
        cb=find_handler(c.router,'callback_query','cb_'+entry+'_xgw_invoice')
        cells=dict(zip(cb.__code__.co_freevars,cb.__closure__))
        if entry=='cancel':
            show=cells['_show_invoices'].cell_contents
            cells=dict(zip(show.__code__.co_freevars,show.__closure__))
        async def fail(*a,**kw):raise RuntimeError('synthetic render')
        cells['replace_admin_view'].cell_contents=fail
    with pytest.raises(RuntimeError,match='synthetic '+failure):invoke(c,entry)
    if entry=='view' or failure=='lookup':assert dump(c.db)==before and not c.effects
    else:
        with c.db._get_conn() as conn:assert conn.execute('SELECT 1 FROM extra_gateway_invoices WHERE id=?',(c.iid,)).fetchone() is None
        assert [x[0] for x in c.effects]==['cancel_and_delete_extra_invoice','expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
    assert not c.views and not c.trace and not c.remote
