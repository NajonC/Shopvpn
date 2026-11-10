"""Independent caller-local alias guards, only in isolated scratch execution."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
def variants(payment):
    p=payment;guards={}
    for entry,method,anchor in [('check','check_invoice','    if invoice["status"] == "completed":'),('process','process_invoice','    result = await check_invoice(db, invoice)'),('deliver','deliver','    kind = invoice["kind"]')]:
        helper='_review_'+entry
        p=m.HELPER.replace('_review_blocked_invoice',helper)+p
        result='"error:composite_unsupported", ""' if entry=='process' else '"error:composite_unsupported"' if entry=='check' else '"composite_unsupported"'
        guard=f'    if {helper}(db, invoice):\n        return {result}\n'
        guards[entry]=(method,guard)
        p=change(p,method,lambda s:once(s,anchor,guard+anchor))
    yield 'reference',p
    for entry,(method,guard) in guards.items():
        for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock_domain','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
            yield entry+'_'+name,change(p,'_review_'+entry,lambda s:once(s,b,a))
        yield entry+'_omit',change(p,method,lambda s:once(s,guard,''))
        yield entry+'_reason',change(p,method,lambda s:once(s,'composite_unsupported','unsupported'))
    yield 'check_skip_claim',change(p,'check_invoice',lambda s:once(s,'    claimed = await asyncio.to_thread(db.claim_extra_invoice, invoice["id"])','    claimed = True'))
    yield 'process_wrong_ref',change(p,'process_invoice',lambda s:once(s,'    result = await check_invoice(db, invoice)','    result = await check_invoice(db, {**dict(invoice), "ref_id": invoice["id"]})'))
    yield 'process_drop_deliver',change(p,'process_invoice',lambda s:once(s,'        text = await deliver(db, bot, invoice, notify_admins_fn)','        text = "alias delivered"'))
    yield 'deliver_wrong_ref',change(p,'deliver',lambda s:once(s,'    ref_id = int(invoice["ref_id"])','    ref_id = int(invoice["id"])'))
    yield 'deliver_only_pending',change(p,'deliver',lambda s:once(s,'("pending", "approved")','("pending",)'))
    yield 'deliver_destination',change(p,'_notify_admins',lambda s:once(s,'bot.send_message(admin_id, text)','bot.send_message(999, text)'))
