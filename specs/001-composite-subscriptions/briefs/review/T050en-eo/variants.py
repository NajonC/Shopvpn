"""Scratch-only caller admission; independent dependent-effect mutations."""
import importlib.util
from pathlib import Path

def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/name/'variants.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('T050dd-de');old=load('T050bl-bm')
once,change=base.once,base.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py','blupal_payment.py','noapay_payment.py','direct_panel_provision.py','reseller_auto_provision.py','database.py']
def variants(*texts):
    sources=dict(zip(SOURCES,texts));payment=sources['extra_gateway_payment.py']
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    ref=change(base.HELPER+payment,'deliver',lambda s:once(s,'    kind = invoice["kind"]',guard+'    kind = invoice["kind"]'))
    baseline={**sources,'extra_gateway_payment.py':ref}
    yield ('reference',*(baseline[p] for p in SOURCES))
    edits=[('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('reference','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]
    for name,b,a in edits:
        altered={**baseline,'extra_gateway_payment.py':change(ref,'_review_blocked_invoice',lambda s:once(s,b,a))}
        yield ('caller_'+name,*(altered[p] for p in SOURCES))
    for name,b,a in [('omit',guard,''),('reason','composite_unsupported','unsupported'),('early_claim',guard,'    db.claim_order(int(invoice["ref_id"]))\n'+guard),('notifier','notify_admins_fn=notifier','notify_admins_fn=None'),('order_ref','finalize_paid_order(db, bot, ref_id,','finalize_paid_order(db, bot, 99999,'),('warning','تایید شد ولی تحویل خودکار ناموفق بود:', 'تایید شد ولی wrong:')]:
        altered={**baseline,'extra_gateway_payment.py':change(ref,'deliver',lambda s:once(s,b,a))}
        yield ('deliver_'+name,*(altered[p] for p in SOURCES))
    for name,mut in old.variants(sources):
        if name=='reference':continue
        if name.startswith(('blupal_payment.py:','noapay_payment.py:')):continue
        if name.split(':')[-1] in {'omit_order','omit_product','reason','early_claim','overstrict'}:continue
        altered={**baseline}
        for p in SOURCES[1:]:
            if mut[p]!=sources[p]:altered[p]=mut[p].replace(old.GUARD,'')
        yield ('dependent_'+name,*(altered[p] for p in SOURCES))
