"""Admin view/cancel reference guards, independent caller and legacy mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py']
GUARD='''        order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice["kind"] == "order" else None
        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(admin):
    anchors={'cb_view_xgw_invoice':'        meta = registry.GATEWAYS.get(invoice["gateway"]','cb_cancel_xgw_invoice':'        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)'}
    ref=admin
    for entry,anchor in anchors.items():ref=change(ref,entry,lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref
    for entry in anchors:
        for name,b,a in [('order_alias','if blocked_order or blocked_product:','if blocked_product:'),('product_alias','if blocked_order or blocked_product:','if blocked_order:'),('ref_domain','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]'),('selected_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),('reason','composite_unsupported','unsupported'),('alert','"composite_unsupported", show_alert=True','"composite_unsupported", show_alert=False'),('overstrict','if blocked_order or blocked_product:','if order is not None:'),('remove_guard',GUARD,''),('authority','if not admin_only(call.from_user.id):','if False:'),('wrong_invoice','db.get_extra_invoice, invoice_id','db.get_extra_invoice, invoice_id+1'),('delete_before_guard',GUARD,'        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)\n'+GUARD)]:
            yield entry+'_'+name,change(ref,entry,lambda s:once(s,b,a))
    for name,b,a in [('active','invoice["status"] in ("new", "pending")','invoice["status"] == "new"'),('stars_controls','if invoice["gateway"] != "tgstars":','if True:'),('stars_amount','{invoice[\'payable_amount\']}','{invoice[\'amount_toman\']}'),('ordinary_amount','int(invoice[\'payable_amount\'])','int(invoice[\'amount_toman\'])'),('ref_display',"#{invoice['ref_id']}","#{invoice['id']}"),('back_gateway',"adm_xgw_payments:{invoice['gateway']}","adm_xgw_payments:wrong")]:
        yield 'view_'+name,change(ref,'cb_view_xgw_invoice',lambda s:once(s,b,a))
    for name,b,a in [('drop_delete','await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)','pass'),('wrong_delete','db.cancel_and_delete_extra_invoice, invoice_id','db.cancel_and_delete_extra_invoice, invoice["ref_id"]'),('wrong_refresh','_show_invoices(call, invoice["gateway"])','_show_invoices(call, "tgstars")')]:
        yield 'cancel_'+name,change(ref,'cb_cancel_xgw_invoice',lambda s:once(s,b,a))
