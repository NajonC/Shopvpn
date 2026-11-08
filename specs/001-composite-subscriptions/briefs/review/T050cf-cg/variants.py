"""Direct Stars admission, identity, money, claim ordering and real SQL mutants."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('b14_prior_variants',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
once,change=m.once,m.change
GATEWAY='stars'
def variants(payment,database,fulfillment):
    guard='''    order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice["kind"] == "order" else None
    product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
    blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
    blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
    if blocked_order or blocked_product:
        return "composite_unsupported"
'''
    merge='    await asyncio.to_thread(db.merge_extra_invoice_meta, invoice_id, {"charge_id": charge_id})'
    ref=change(payment,'process_stars_payment',lambda s:once(s,merge,guard+merge))
    yield 'reference',ref,database,fulfillment
    def pm(name,b,a):return name,change(ref,'process_stars_payment',lambda s:once(s,b,a)),database,fulfillment
    yield pm('order_alias','if blocked_order or blocked_product:','if blocked_product:')
    yield pm('product_alias','if blocked_order or blocked_product:','if blocked_order:')
    yield pm('wrong_order','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]')
    yield pm('wrong_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999')
    yield pm('reason','composite_unsupported','unsupported')
    yield pm('early_metadata',guard+merge,merge+'\n'+guard)
    yield pm('early_claim',guard+merge,'    await asyncio.to_thread(db.claim_extra_invoice, invoice_id)\n'+guard+merge)
    yield pm('overstrict','if blocked_order or blocked_product:','if order is not None:')
    yield pm('owner','int(invoice["user_id"]) != int(user_id)','False')
    yield pm('gateway','invoice["gateway"] != "tgstars"','False')
    yield pm('amount','int(total_amount) != int(invoice["payable_amount"] or 0)','False')
    yield pm('currency','currency != "XTR"','False')
    yield pm('metadata',merge,'    pass')
    yield pm('wrong_charge','{"charge_id": charge_id}','{"charge_id": "wrong"}')
    yield pm('ignore_claim','if not await asyncio.to_thread(db.claim_extra_invoice, invoice_id):','if await asyncio.to_thread(db.claim_extra_invoice, invoice_id) and False:')
    yield pm('metadata_after_claim',merge+'\n    if not await asyncio.to_thread(db.claim_extra_invoice, invoice_id):\n        return "✅ این پرداخت قبلاً ثبت و تحویل داده شده است."', '    if not await asyncio.to_thread(db.claim_extra_invoice, invoice_id):\n        return "✅ این پرداخت قبلاً ثبت و تحویل داده شده است."\n'+merge)
    yield pm('wrong_delivery','return await deliver(db, bot, invoice, notify_admins_fn)','return "wrong"')
    yield pm('release_failure','logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)','await asyncio.to_thread(db.release_extra_invoice, invoice_id)\n        logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)')
    yield 'claim_unconditional',ref,change(database,'claim_extra_invoice',lambda s:once(s,"WHERE id=? AND status IN ('new','pending')","WHERE id=?")),fulfillment
    def fm(name,b,a):return name,ref,database,change(fulfillment,'finalize_paid_order',lambda s:once(s,b,a))
    yield fm('quantity','quantity = order["quantity"] or 1','quantity = 1')
    yield fm('price','links, final_price=order["final_price"]','links, final_price=order["final_price"]+1')
    yield fm('reward','order["base_price"]','order["base_price"]+100')
