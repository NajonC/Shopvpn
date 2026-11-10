"""Direct Stars scratch reference and independently applied inline mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
def variants(payment):
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    anchor='    if not invoice or invoice["gateway"]'
    ref=change(m.HELPER+payment,'process_stars_payment',lambda s:once(s,anchor,guard+anchor))
    yield 'reference',ref
    for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('wrongref','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('domain','invoice["kind"] != "order"','False'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        yield name,change(ref,'_review_blocked_invoice',lambda s:once(s,b,a))
    for name,b,a in [('omit',guard,''),('reason','composite_unsupported','unsupported'),('owner','int(invoice["user_id"]) != int(user_id)','False'),('gateway','invoice["gateway"] != "tgstars"','False'),('currency','currency != "XTR"','False'),('amount','int(total_amount) != int(invoice["payable_amount"] or 0)','False'),('metadata','await asyncio.to_thread(db.merge_extra_invoice_meta, invoice_id, {"charge_id": charge_id})','pass'),('charge','{"charge_id": charge_id}','{"charge_id": "wrong"}'),('claim','if not await asyncio.to_thread(db.claim_extra_invoice, invoice_id):','if await asyncio.to_thread(db.claim_extra_invoice, invoice_id) and False:'),('deliver','return await deliver(db, bot, invoice, notify_admins_fn)','return "wrong"'),('notifier','deliver(db, bot, invoice, notify_admins_fn)','deliver(db, bot, invoice, None)'),('refresh','    invoice = await asyncio.to_thread(db.get_extra_invoice, invoice_id)\n    try:', '    try:'),('release','logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)','await asyncio.to_thread(db.release_extra_invoice, invoice_id)\n        logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)'),('warning','(شارژ {charge_id}). دستی بررسی کن.','(شارژ wrong). دستی بررسی کن.')]:
        # warning occurs in two branches; separate exact invalid-payload text instead.
        if name=='warning':
            b='payload نامعتبر از کاربر {user_id}';a='payload نامعتبر از کاربر 999'
        yield name,change(ref,'process_stars_payment',lambda s:once(s,b,a))
