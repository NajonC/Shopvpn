"""Scratch-only admission plus actual dependent purchase mutations."""
import importlib.util
from pathlib import Path
def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/name/'variants.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('T050dd-de');old=load('T050ax-ay')
once,change=base.once,base.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py']
def variants(payment,aban):
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    ref=change(base.HELPER+payment,'deliver',lambda s:once(s,'    kind = invoice["kind"]',guard+'    kind = invoice["kind"]'))
    yield 'reference',ref,aban
    for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('reference','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        yield 'caller_'+name,change(ref,'_review_blocked_invoice',lambda s:once(s,b,a)),aban
    for name,b,a in [('omit',guard,''),('reason','composite_unsupported','unsupported'),('notifier','notify_admins_fn=notifier','notify_admins_fn=None'),('order_ref','finalize_paid_order(db, bot, ref_id,','finalize_paid_order(db, bot, 99999,'),('warning','تایید شد ولی تحویل خودکار ناموفق بود:', 'تایید شد ولی wrong:')]:
        yield 'deliver_'+name,change(ref,'deliver',lambda s:once(s,b,a)),aban
    for name,altered in old.variants(aban):
        if name in {'reference','omit_order','omit_product','omit_both','no_reason','early_claim','wrong_product','overstrict_legacy','sibling_blocks'}:continue
        yield 'dependent_'+name,ref,altered.replace(old.GUARD,'')
