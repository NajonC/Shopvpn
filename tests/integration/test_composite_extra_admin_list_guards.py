"""T050db/dc: list admission before housekeeping, real SQL and exact rows."""
import asyncio
import pytest
from tests.integration.test_composite_extra_admin_view_cancel_guards import prepare, catalog, OWNER, USER_ID, dump, admin, egp
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests._harness.legacy_bot import FakeUser, FakeMessage, FakeCallbackQuery, TelegramLog, find_handler


def invoke(c,key,uid=OWNER):
    async def run():
        log=TelegramLog();u=FakeUser(uid)
        call=FakeCallbackQuery(log,u,f'adm_xgw_payments:{key}',FakeMessage(log,uid,from_user=u))
        await find_handler(c.router,'callback_query','cb_xgw_payments')(call)
        return log.events
    return asyncio.run(run())


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status',['new','completed'])
def test_list_composite_admission(catalog,monkeypatch,key,representation,marker,status):
    c=catalog;prepare(c,monkeypatch,representation,'composite',marker,key,status)
    # Real housekeeping remains permissive: caller must refuse before invoking it.
    with c.db._get_conn() as conn:
        conn.execute("UPDATE extra_gateway_invoices SET created_at='2000-01-01 00:00:00',updated_at='2000-01-01T00:00:00' WHERE id=?",(c.iid,))
        conn.execute('UPDATE extra_gateway_invoices SET gateway=? WHERE id=?',(key,c.decoy))
    before=dump(c.db)
    for _ in range(2):
        events=invoke(c,key)
        assert any(e.show_alert and 'composite' in (e.text or '').lower() for e in events), 'missing T052 admin list composite refusal'
        assert not [x for x in c.effects if x[0]!='list_extra_invoices'] and dump(c.db)==before
        assert len(c.views)==_+1
        buttons=[b for row in c.views[-1][2]['reply_markup'].inline_keyboard for b in row]
        assert any(b.callback_data==f'view_xgw_invoice:{c.decoy}' for b in buttons)
        assert not any(b.callback_data and b.callback_data.endswith(':'+str(c.iid)) for b in buttons)
        assert not c.trace and not c.remote and not c.invoice_trace


STATUS={'new':'🟡 جدید','pending':'🟠 در انتظار','completed':'🟢 تکمیل‌شده','expired':'🔴 منقضی‌شده','cancelled':'🔴 لغوشده'}
@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('status',list(STATUS))
def test_list_legacy_rows(catalog,monkeypatch,key,kind,status):
    c=catalog;prepare(c,monkeypatch,'sqlite',kind,key=key,status=status)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET gateway=? WHERE id=?',(key,c.decoy))
    before=dump(c.db);events=invoke(c,key)
    assert len(events)==1 and events[0].text is None
    assert [x for x in c.effects if x[0]!='list_extra_invoices']==[('expire_stale_extra_invoices',(),{}),('purge_old_extra_invoices',(7,),{})]
    assert c.effects[-1]==('list_extra_invoices',(50,key),{})
    assert dump(c.db)==before and len(c.views)==1 and c.views[0][0]==OWNER
    meta=egp.registry.GATEWAYS[key];rows=c.views[0][2]['reply_markup'].inline_keyboard
    expected=[(f"{STATUS[status]} | {meta['icon']} {meta['title']} | 🧾 سفارش #{c.oid} | 900",f'view_xgw_invoice:{c.iid}')]
    if status in {'new','pending'}:
        if key!='tgstars':expected.append(('🔄',f'check_xgw_invoice:{c.iid}'))
        expected.append(('❌',f'cancel_xgw_invoice:{c.iid}'))
    assert [(b.text,b.callback_data) for b in rows[0]]==expected
    assert rows[1][0].callback_data==f'view_xgw_invoice:{c.decoy}'
    assert [(r[0].text,r[0].callback_data) for r in rows[-2:]]==[('🔄 بروزرسانی',f'adm_xgw_payments:{key}'),('⬅️ بازگشت','adm_cat:daily')]
    assert c.views[0][1]==f"{meta['icon']} پرداخت‌های {meta['title']}\n\nاین پرداخت‌ها به‌صورت خودکار تایید می‌شوند و در بخش سفارش‌ها/شارژهای دستی نمایش داده نمی‌شوند."


@pytest.mark.parametrize('scenario',['unauthorized','unknown','empty','expire_error','purge_error','list_error','render_error'])
def test_list_boundaries(catalog,monkeypatch,scenario):
    c=catalog;prepare(c,monkeypatch,'sqlite')
    if scenario=='empty':
        with c.db._get_conn() as conn:conn.execute('DELETE FROM extra_gateway_invoices')
    method={'expire_error':'expire_stale_extra_invoices','purge_error':'purge_old_extra_invoices','list_error':'list_extra_invoices'}.get(scenario)
    if method:
        def fail(*a,**kw):c.effects.append((method,a,kw));raise RuntimeError('synthetic '+scenario)
        monkeypatch.setattr(c.db,method,fail)
    if scenario=='render_error':
        async def fail(*a,**kw):raise RuntimeError('synthetic render_error')
        # Register captures replace_admin_view in closure; replace that exact cell.
        handler=find_handler(c.router,'callback_query','cb_xgw_payments')
        show=dict(zip(handler.__code__.co_freevars,handler.__closure__))['_show_invoices'].cell_contents
        dict(zip(show.__code__.co_freevars,show.__closure__))['replace_admin_view'].cell_contents=fail
    before=dump(c.db)
    if scenario.endswith('error'):
        with pytest.raises(RuntimeError,match='synthetic '+scenario):invoke(c,'zarinpal')
        assert not c.views
        names=[x[0] for x in c.effects]
        if names[0]=='list_extra_invoices' and len(names)>1:names=names[1:]
        expected=['expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
        if scenario=='list_error':assert names in [expected,['list_extra_invoices']]
        else:assert names==expected[:expected.index(method)+1] if method else names==expected
    else:
        events=invoke(c,'unknown' if scenario=='unknown' else 'zarinpal',USER_ID if scenario=='unauthorized' else OWNER)
        assert len(events)==1 and events[0].text==('درگاه نامعتبر.' if scenario=='unknown' else None)
        if scenario=='empty':
            assert len(c.views)==1 and 'هیچ پرداختی ثبت نشده است.' in c.views[0][1]
        else:assert not c.effects and not c.views
    assert dump(c.db)==before and not c.trace and not c.remote


@pytest.mark.parametrize('gateway',[None,'zarinpal','tgstars','unknown'])
@pytest.mark.parametrize('limit',[None,0,-1,1,50,200,201,999])
def test_real_sql_list_contract(catalog,monkeypatch,gateway,limit):
    c=catalog;prepare(c,monkeypatch,'sqlite')
    with c.db._get_conn() as conn:
        conn.execute('DELETE FROM extra_gateway_invoices')
    ids=[]
    for n in range(205):
        key='tgstars' if n%2 else 'zarinpal'
        iid=c.db.create_extra_invoice(key,['order','wallet_topup','reseller_request'][n%3],700+n,USER_ID,123+n,456+n)
        c.db.update_extra_invoice_status(iid,list(STATUS)[n%5]);ids.append((iid,key))
    before=dump(c.db);rows=c.db.list_extra_invoices(limit,gateway)
    bound=max(1,min(int(limit or 50),200))
    assert [r['id'] for r in rows]==[i for i,k in reversed(ids) if not gateway or k==gateway][:bound]
    assert dump(c.db)==before
