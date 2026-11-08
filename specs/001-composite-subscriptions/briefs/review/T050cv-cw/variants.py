"""Independent process/deliver caller guards, no helper-closure assumptions."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050ct-cu/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
def guard(entry):return m.GUARD.replace('return "error:composite_unsupported"','return ("error:composite_unsupported", "")' if entry=='process_invoice' else 'return "⛔️ composite_unsupported"')
def variants(payment):
    ref=payment
    for entry,anchor in [('process_invoice','    result = await check_invoice(db, invoice)'),('deliver','    kind = invoice["kind"]')]:ref=change(ref,entry,lambda s:once(s,anchor,guard(entry)+anchor))
    yield 'reference',ref
    for entry in ['process_invoice','deliver']:
        for name,b,a in [
            ('order_alias','if blocked_order or blocked_product:','if blocked_product:'),
            ('product_alias','if blocked_order or blocked_product:','if blocked_order:'),
            ('reference_domain','db.get_order, int(invoice["ref_id"])','db.get_order, int(invoice["id"])'),
            ('selected_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),
            ('reason','composite_unsupported','unsupported'),
            ('overstrict','if blocked_order or blocked_product:','if order is not None:'),
            ('remove_guard',guard(entry),''),
            ('claim_before_guard',guard(entry),'    await asyncio.to_thread(db.claim_extra_invoice, invoice["id"])\n'+guard(entry)),
            ('credit_before_guard',guard(entry),'    await asyncio.to_thread(db.add_wallet_credit, invoice["user_id"], 1)\n'+guard(entry)),
        ]:yield entry+'_'+name,change(ref,entry,lambda s:once(s,b,a))
    for name,b,a in [
        ('unpaid_delivery','if result != "verified_now":','if False:'),
        ('drop_delivery','text = await deliver(db, bot, invoice, notify_admins_fn)','text = ""'),
        ('release_wrong_invoice','db.release_extra_invoice, invoice["id"]','db.release_extra_invoice, invoice["ref_id"]'),
        ('omit_release','await asyncio.to_thread(db.release_extra_invoice, invoice["id"])','pass'),
        ('result_text','return result, text','return result, ""'),
    ]:yield name,change(ref,'process_invoice',lambda s:once(s,b,a))
    for name,b,a in [
        ('delivery_reference','ref_id = int(invoice["ref_id"])','ref_id = int(invoice["id"])'),
        ('approved_rejected','("pending", "approved")','("pending", "rejected")'),
        ('registered_notifier','notify_admins_fn or _order_notifiers.get(id(db))','notify_admins_fn'),
        ('notifier_forwarding','notify_admins_fn=notifier','notify_admins_fn=None'),
        ('drop_finalizer','text = await abangateway_payment.finalize_paid_order(db, bot, ref_id, notify_admins_fn=notifier)','text = "synthetic omitted"'),
    ]:yield name,change(ref,'deliver',lambda s:once(s,b,a))
