"""Scratch-only admin check admission and source result/authority mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py']
def variants(admin):
    anchor='        await call.answer("در حال بررسی...")'
    guard=m.CALL_GUARD
    ref=change(m.HELPER+admin,'cb_check_xgw_invoice',lambda s:once(s,anchor,guard+anchor))
    yield 'reference',ref
    for name,b,a in [
        ('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),
        ('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),
        ('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),
        ('wrongref','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),
        ('custom','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),
        ('stock','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),
        ('domain','invoice["kind"] != "order"','False'),
        ('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        yield name,change(ref,'_review_blocked_invoice',lambda s:once(s,b,a))
    for name,b,a in [('omit',guard,''),('reason','composite_unsupported','unsupported'),('alert','"composite_unsupported", show_alert=True','"composite_unsupported", show_alert=False'),('authority','if not admin_only(call.from_user.id):','if False:'),('selected','egp.process_invoice(db, bot, invoice)','egp.process_invoice(db, bot, {**dict(invoice), "ref_id":invoice["id"]})'),('verified','await call.message.answer(text or','await call.message.answer("wrong" or'),('notpaid','⏳ هنوز پرداختی برای این فاکتور تایید نشده.','wrong'),('already','✅ این پرداخت قبلاً تایید و تحویل داده شده است.','wrong'),('expired','❌ اعتبار این فاکتور تمام شده یا لغو شده است.','wrong'),('error','{result[6:]}','wrong'),('fallback','✅ پرداخت تایید و تحویل داده شد.','wrong')]:
        yield name,change(ref,'cb_check_xgw_invoice',lambda s:once(s,b,a))
