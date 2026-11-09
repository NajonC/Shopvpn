"""Review-only independent guards at direct deletion and admin entry boundaries."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cz-da/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py','database.py']
HELPER='''
def _review_blocked_invoice(db, invoice):
    if invoice is None or invoice["kind"] != "order":
        return False
    order = db.get_order(invoice["ref_id"])
    if order is None:
        return False
    def marked(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    target = None
    if order["is_renewal"] and order["renewal_target_id"]:
        target = (db.get_custom_config_by_id(order["renewal_target_id"]) if order["renewal_target_kind"] == "custom" else db.get_config_by_id(order["renewal_target_id"]))
    custom = bool(order["is_custom_config"]) or bool(order["is_renewal"] and order["renewal_target_kind"] == "custom")
    product_id = target["product_id"] if target is not None else order["custom_product_id"] if custom else order["product_id"]
    product = (db.get_custom_config_product(product_id) if custom else db.get_product(product_id)) if product_id else None
    return marked(order) or marked(target) or marked(product)

'''
CALL_GUARD='''        if _review_blocked_invoice(db, invoice):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
DIRECT_GUARD='''        invoice = self.get_extra_invoice(id_)
        if _review_blocked_invoice(self, invoice):
            raise ValueError("composite_unsupported")
'''
def variants(admin,db):
    ref=HELPER+admin;dref=HELPER+db
    for entry,anchor in [('cb_view_xgw_invoice','        meta = registry.GATEWAYS.get(invoice["gateway"]'),('cb_cancel_xgw_invoice','        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)')]:
        ref=change(ref,entry,lambda s:once(s,anchor,CALL_GUARD+anchor))
    dref=change(dref,'cancel_and_delete_extra_invoice',lambda s:once(s,'        with self._get_conn() as conn:',DIRECT_GUARD+'        with self._get_conn() as conn:'))
    yield 'reference',ref,dref
    for index,source in enumerate([ref,dref]):
        for name,b,a in [('order_alias','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target_alias','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product_alias','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref_domain','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('target_id','order["renewal_target_id"])','order["renewal_target_id"]+999)'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('ordinary_domain','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True'),('ref_kind','invoice["kind"] != "order"','False')]:
            if name=='ref_kind' and index==0:continue # callback other-kind controls remain open
            def edit(s):
                if name=='target_id':
                    assert s.count(b)==2;return s.replace(b,a)
                return once(s,b,a)
            altered=change(source,'_review_blocked_invoice',edit)
            yield ('callback_' if index==0 else 'direct_')+name,altered if index==0 else ref,altered if index==1 else dref
    for entry in ['cb_view_xgw_invoice','cb_cancel_xgw_invoice']:
        for name,b,a in [('omit',CALL_GUARD,''),('reason','composite_unsupported','unsupported'),('alert','"composite_unsupported", show_alert=True','"composite_unsupported", show_alert=False')]:
            yield entry+'_'+name,change(ref,entry,lambda s:once(s,b,a)),dref
    for name,b,a in [('omit',DIRECT_GUARD,''),('reason','composite_unsupported','unsupported'),('identity','WHERE id=?','WHERE ref_id=?'),('drop_delete','conn.execute("DELETE FROM extra_gateway_invoices WHERE id=?", (id_,))','pass'),('delete_early',DIRECT_GUARD,'        with self._get_conn() as conn:\n            conn.execute("DELETE FROM extra_gateway_invoices WHERE id=?", (id_,))\n'+DIRECT_GUARD)]:
        yield 'delete_'+name,ref,change(dref,'cancel_and_delete_extra_invoice',lambda s:once(s,b,a))
    yield 'callback_drop_refresh',change(ref,'cb_cancel_xgw_invoice',lambda s:once(s,'        await _show_invoices(call, invoice["gateway"])','        pass')),dref
    yield 'callback_refresh_before_delete',change(ref,'cb_cancel_xgw_invoice',lambda s:once(s,'        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)','        await _show_invoices(call, invoice["gateway"])\n        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)')),dref
    def swallow(s):
        lines=s.splitlines(keepends=True)
        return lines[0]+'        try:\n'+''.join('    '+line for line in lines[1:])+'        except RuntimeError:\n            return\n'
    yield 'callback_swallow_failure',change(ref,'cb_cancel_xgw_invoice',swallow),dref
