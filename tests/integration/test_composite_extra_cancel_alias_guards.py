"""T050dd/de: direct cancellation and independent admin alias admission."""
import pytest
from tests.integration.test_composite_extra_admin_view_cancel_guards import prepare, invoke, catalog, dump, USER_ID
from tests.integration.test_composite_extra_order_entry_guards import GATEWAYS
from tests.integration.test_composite_legacy_guards import as_row

ALIASES=['custom_order','custom_product','global_custom_order','renewal_order','renewal_target','renewal_product','global_renewal_target','stock_renewal_target','stock_renewal_product']
STATUSES=['new','pending','completed','expired','cancelled']


def alias(c,mp,name,kind,representation):
    prepare(c,mp,representation,kind,'order' if name.endswith('order') else 'unused')
    # Keep invoice id, selected order ref, and an unrelated valid order distinct.
    c.db.create_order(USER_ID,c.pid,777)
    if name.startswith('stock_'):
        with c.db._get_conn() as conn:target=conn.execute('SELECT id FROM configs WHERE product_id=? LIMIT 1',(c.pid,)).fetchone()[0]
        c.oid=c.db.create_renewal_order(USER_ID,'stock',target,'full',10,30,1000)
        getter='get_config_by_id';product_getter='get_product';product_id=c.pid
    else:
        product_id=None if name.startswith('global_') else c.alpha_id
        target=c.db.add_custom_config(USER_ID,c.s1,'synthetic-alias',10,30,'',product_id=product_id)
        if 'renewal' in name:
            c.oid=c.db.create_renewal_order(USER_ID,'custom',target,'full',10,30,1000)
        else:c.oid=c.db.create_custom_config_order(USER_ID,10,'synthetic-new',c.s1,1000,custom_product_id=product_id,custom_duration_days=30)
        getter='get_custom_config_by_id';product_getter='get_custom_config_product'
    original=c.db.get_order
    def order(oid):
        row=original(oid)
        if row is None:return None
        d=dict(row);d.pop('service_kind',None)
        if oid==c.oid and name.endswith('order') and kind is not None:d['service_kind']=kind
        return as_row(d,representation)
    mp.setattr(c.db,'get_order',order)
    if name.endswith('target') or name.endswith('product'):
        method=getter if name.endswith('target') else product_getter;ident=target if name.endswith('target') else product_id;old=getattr(c.db,method)
        def read(i):
            row=old(i)
            if row is None:return None
            d=dict(row);d.pop('service_kind',None)
            if i==ident and kind is not None:d['service_kind']=kind
            return as_row(d,representation)
        mp.setattr(c.db,method,read)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET ref_id=? WHERE id=?',(c.oid,c.iid))


def refuse_direct(c):
    before=dump(c.db)
    for _ in range(2):
        with pytest.raises(ValueError,match='(?i)composite'):c.db.cancel_and_delete_extra_invoice(c.iid)
        assert dump(c.db)==before and not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('key',GATEWAYS)
@pytest.mark.parametrize('marker',['order','product'])
@pytest.mark.parametrize('status',STATUSES)
def test_direct_cancel_stock(catalog,monkeypatch,key,marker,status):
    c=catalog;prepare(c,monkeypatch,'sqlite','composite',marker,key,status);refuse_direct(c)


@pytest.mark.parametrize('entry',['direct','view','cancel'])
@pytest.mark.parametrize('representation',['dict','sqlite'])
@pytest.mark.parametrize('name',ALIASES)
def test_composite_cancel_aliases(catalog,monkeypatch,entry,representation,name):
    c=catalog;alias(c,monkeypatch,name,'composite',representation)
    if entry=='direct':refuse_direct(c);return
    # Permissive dependent deletion cannot conceal absent callback admission.
    monkeypatch.setattr(c.db,'cancel_and_delete_extra_invoice',lambda iid:c.effects.append(('unguarded_delete',iid)))
    before=dump(c.db)
    for _ in range(2):
        events=invoke(c,entry)
        assert len(events)==1 and events[0].show_alert and 'composite' in (events[0].text or '').lower(), 'missing T052 admin alias refusal'
        assert not c.views and not c.effects and dump(c.db)==before and not c.trace and not c.remote


@pytest.mark.parametrize('kind',[None,'legacy'])
@pytest.mark.parametrize('entry',['direct','view','cancel'])
@pytest.mark.parametrize('name',ALIASES)
def test_legacy_cancel_aliases(catalog,monkeypatch,kind,entry,name):
    c=catalog;alias(c,monkeypatch,name,kind,'sqlite')
    before=dump(c.db);selected=dict(c.db.get_extra_invoice(c.iid));decoy=dict(c.db.get_extra_invoice(c.decoy))
    retained=[x for x in before if not x.startswith('INSERT INTO "extra_gateway_invoices"')]
    if entry=='direct':assert c.db.cancel_and_delete_extra_invoice(c.iid) is None
    else:
        events=invoke(c,entry);assert len(events)==1 and events[0].text==(None if entry=='view' else '✅ فاکتور لغو و حذف شد.')
        assert len(c.views)==1
        if entry=='view':assert f'#{c.oid}' in c.views[0][1] and '900' in c.views[0][1]
    assert dict(c.db.get_extra_invoice(c.decoy))==decoy
    if entry=='view':assert dump(c.db)==before and dict(c.db.get_extra_invoice(c.iid))==selected
    else:
        assert c.db.get_extra_invoice(c.iid) is None
        assert [x for x in dump(c.db) if not x.startswith('INSERT INTO "extra_gateway_invoices"')]==retained
        if entry=='direct':assert c.db.cancel_and_delete_extra_invoice(c.iid) is None
    assert not c.trace and not c.remote and not c.invoice_trace


@pytest.mark.parametrize('kind',['order','wallet_topup','reseller_request'])
@pytest.mark.parametrize('status',STATUSES)
def test_direct_cancel_reference_domains(catalog,monkeypatch,kind,status):
    c=catalog;prepare(c,monkeypatch,'sqlite','composite' if kind!='order' else 'legacy',key='tgstars',status=status)
    with c.db._get_conn() as conn:conn.execute('UPDATE extra_gateway_invoices SET kind=? WHERE id=?',(kind,c.iid))
    before=dump(c.db);retained=[x for x in before if not x.startswith('INSERT INTO "extra_gateway_invoices"')]
    decoy=dict(c.db.get_extra_invoice(c.decoy));assert c.db.cancel_and_delete_extra_invoice(c.iid) is None
    assert c.db.get_extra_invoice(c.iid) is None and dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert [x for x in dump(c.db) if not x.startswith('INSERT INTO "extra_gateway_invoices"')]==retained


@pytest.mark.parametrize('failure',['delete','expiry','purge','list','render'])
def test_cancel_failure_ordering(catalog,monkeypatch,failure):
    c=catalog;prepare(c,monkeypatch,'sqlite')
    method={'delete':'cancel_and_delete_extra_invoice','expiry':'expire_stale_extra_invoices','purge':'purge_old_extra_invoices','list':'list_extra_invoices'}.get(failure)
    if method:
        def fail(*a,**kw):c.effects.append((method,a,kw));raise RuntimeError('synthetic '+failure)
        monkeypatch.setattr(c.db,method,fail)
    else:
        # Reuse captured closure to fail only the external Telegram renderer.
        from tests._harness.legacy_bot import find_handler
        cb=find_handler(c.router,'callback_query','cb_cancel_xgw_invoice')
        show=dict(zip(cb.__code__.co_freevars,cb.__closure__))['_show_invoices'].cell_contents
        async def fail(*a,**kw):raise RuntimeError('synthetic render')
        dict(zip(show.__code__.co_freevars,show.__closure__))['replace_admin_view'].cell_contents=fail
    decoy=dict(c.db.get_extra_invoice(c.decoy));before=dump(c.db)
    with pytest.raises(RuntimeError,match='synthetic '+failure):invoke(c,'cancel')
    expected=['cancel_and_delete_extra_invoice','expire_stale_extra_invoices','purge_old_extra_invoices','list_extra_invoices']
    assert [x[0] for x in c.effects]==(expected[:expected.index(method)+1] if method else expected)
    assert (c.db.get_extra_invoice(c.iid) is not None)==(failure=='delete')
    if failure=='delete':assert dump(c.db)==before
    else:assert dict(c.db.get_extra_invoice(c.decoy))==decoy
    assert not c.views and not c.remote and not c.trace
