"""New caller and real renewal-engine mutations, each from the same scratch baseline."""
import importlib.util
from pathlib import Path
def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/name/'variants.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('T050dd-de');old=load('T050bd-be')
once,change=base.once,base.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py','blupal_payment.py','noapay_payment.py','renewal_engine.py']
def variants(payment,aban,blue,noa,engine):
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    ref=change(base.HELPER+payment,'deliver',lambda s:once(s,'    kind = invoice["kind"]',guard+'    kind = invoice["kind"]'))
    yield 'reference',ref,aban,blue,noa,engine
    for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('reference','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        yield 'caller_'+name,change(ref,'_review_blocked_invoice',lambda s:once(s,b,a)),aban,blue,noa,engine
    for name,b,a in [('omit',guard,''),('reason','composite_unsupported','unsupported'),('notifier','notify_admins_fn=notifier','notify_admins_fn=None'),('order_ref','finalize_paid_order(db, bot, ref_id,','finalize_paid_order(db, bot, 99999,'),('warning','تایید شد ولی تحویل خودکار ناموفق بود:', 'تایید شد ولی wrong:')]:
        yield 'deliver_'+name,change(ref,'deliver',lambda s:once(s,b,a)),aban,blue,noa,engine
    sources=dict(zip(SOURCES[1:],[aban,blue,noa,engine]))
    for name,altered in old.variants(sources):
        if not name.startswith(('abangateway_payment.py:','renewal_engine.py:')):continue
        if name.split(':')[-1] in {'omit_order','omit_target','omit_both','no_reason','early_claim','wrong_target','overstrict'}:continue
        yield 'dependent_'+name,ref,altered['abangateway_payment.py'].replace(old.GUARD,''),blue,noa,altered['renewal_engine.py']
