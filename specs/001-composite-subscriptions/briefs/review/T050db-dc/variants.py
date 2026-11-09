"""Bounded list caller reference: inspect rows before housekeeping, refuse per row."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cz-da/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py','database.py']
PREFLIGHT='''        candidates = await asyncio.to_thread(db.list_extra_invoices, 50, key)
        allowed = []
        blocked = False
        for invoice in candidates:
            order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice["kind"] == "order" else None
            product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
            blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
            blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
            if blocked_order or blocked_product:
                blocked = True
            else:
                allowed.append(invoice)
        if blocked:
            await call.answer("composite_unsupported", show_alert=True)
            invoices = allowed
        else:
            invoices = await _load_invoices(key)
'''
def variants(admin,db):
    anchor='        invoices = await _load_invoices(key)\n'
    ref=change(admin,'_show_invoices',lambda s:once(s,anchor,PREFLIGHT))
    # For wholly legacy lists preserve the exact original housekeeping/list call order.
    yield 'reference',ref,db
    for name,b,a in [('omit',PREFLIGHT,anchor),('order_alias','if blocked_order or blocked_product:','if blocked_product:'),('product_alias','if blocked_order or blocked_product:','if blocked_order:'),('ref_domain','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]'),('selected_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),('reason','composite_unsupported','unsupported'),('alert','show_alert=True','show_alert=False'),('overstrict','if blocked_order or blocked_product:','if order is not None:'),('drop_legacy','allowed.append(invoice)','pass'),('show_blocked','invoices = allowed','invoices = candidates'),('early_housekeeping','        candidates =','        await _load_invoices(key)\n        candidates =')]:
        yield name,change(ref,'_show_invoices',lambda s:once(s,b,a)),db
    for name,b,a in [('status','🟠 در انتظار','wrong'),('stars','if inv["gateway"] != "tgstars":','if True:'),('amount',"inv['amount_toman']","inv['payable_amount']"),('reference',"inv['ref_id']","inv['id']"),('inactive','if inv["status"] in ("new", "pending"):','if True:'),('back','adm_cat:daily','adm_cat:finance')]:
        yield 'keyboard_'+name,once(ref,b,a) if name=='status' else change(ref,'invoices_kb',lambda s:once(s,b,a)),db
    for name,b,a in [('limit_upper','200','201'),('limit_lower','max(1,','max(2,'),('default','limit or 50','limit or 1'),('gateway','WHERE gateway=?','WHERE gateway!=?'),('order_filtered','ORDER BY id DESC','ORDER BY id ASC'),('order_all','ORDER BY id DESC LIMIT ?", (limit,)','ORDER BY id ASC LIMIT ?", (limit,)')]:
        if name=='order_filtered':
            yield 'sql_'+name,ref,change(db,'list_extra_invoices',lambda s:s.replace(b,a,1))
        else:yield 'sql_'+name,ref,change(db,'list_extra_invoices',lambda s:once(s,b,a))
    for name,b,a in [('drop_expiry','await asyncio.to_thread(db.expire_stale_extra_invoices)','pass'),('drop_purge','await asyncio.to_thread(db.purge_old_extra_invoices, 7)','pass'),('purge_age','db.purge_old_extra_invoices, 7','db.purge_old_extra_invoices, 1'),('limit','db.list_extra_invoices, 50, gateway','db.list_extra_invoices, 1, gateway')]:
        yield 'loader_'+name,change(ref,'_load_invoices',lambda s:once(s,b,a)),db
    for name,b,a in [('authority','if not admin_only(call.from_user.id):','if False:'),('unknown','if key not in registry.GATEWAYS:','if True:')]:
        yield 'callback_'+name,change(ref,'cb_xgw_payments',lambda s:once(s,b,a)),db
