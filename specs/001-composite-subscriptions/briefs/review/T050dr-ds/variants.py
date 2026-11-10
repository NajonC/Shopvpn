"""Scratch-only local guards; independent resolver copies per nested entry."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_user.py']
def variants(user):
    p=user;guards={}
    for entry,method,anchor,guard in [('label','_order_label','        keys = order.keys()', '        if _review_label(db, {"kind":"order", "ref_id":order_id}):\n            raise egp.ExtraGatewayError("composite_unsupported")\n'),('handler','make_order_handler','            if not egp.is_available(db, key, is_main_bot):','            if _review_handler(db, {"kind":"order", "ref_id":order_id}):\n                await call.answer("composite_unsupported", show_alert=True)\n                return\n')]:
        p=m.HELPER.replace('_review_blocked_invoice','_review_'+entry)+p
        p=change(p,method,lambda s:once(s,anchor,guard+anchor));guards[entry]=(method,guard)
    yield 'reference',p
    for entry,(method,guard) in guards.items():
        for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref','db.get_order(invoice["ref_id"])','db.get_order(invoice["ref_id"]+999)'),('custom','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
            yield entry+'_'+name,change(p,'_review_'+entry,lambda s:once(s,b,a))
        yield entry+'_omit',change(p,method,lambda s:once(s,guard,''))
        yield entry+'_reason',change(p,method,lambda s:once(s,'composite_unsupported','unsupported'))
    for name,b,a in [('renewal_label','f"تمدید سرویس #{order_id}"','f"تمدید سرویس #{order_id+1}"'),('custom_label',"{order['custom_username']}","wrong")]:yield 'label_'+name,change(p,'_order_label',lambda s:once(s,b,a))
    for name,b,a in [('amount','order_id, order["final_price"], label','order_id, order["final_price"]+1, label'),('ref_arg','key, "order", order_id','key, "order", order_id+1'),('actor','tenant_id, call.from_user.id, key','tenant_id, call.from_user.id+1, key'),('presentation','await present_invoice(call.message, bot, key, result, "order", label, order["final_price"])','pass')]:yield 'handler_'+name,change(p,'make_order_handler',lambda s:once(s,b,a))
