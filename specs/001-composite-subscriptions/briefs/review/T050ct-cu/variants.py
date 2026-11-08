"""Bounded direct check guard, real remote dispatch; independent mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
GUARD='''    if invoice["kind"] == "order":
        order = await asyncio.to_thread(db.get_order, int(invoice["ref_id"]))
        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            return "error:composite_unsupported"
'''
def variants(payment):
    anchor='    if invoice["status"] == "completed":'
    ref=change(payment,'check_invoice',lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref
    for name,b,a in [
        ('order_alias','if blocked_order or blocked_product:','if blocked_product:'),
        ('product_alias','if blocked_order or blocked_product:','if blocked_order:'),
        ('selected_order','db.get_order, int(invoice["ref_id"])','db.get_order, int(invoice["id"])'),
        ('selected_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),
        ('explicit_reason','error:composite_unsupported','error:unsupported'),
        ('overstrict','if blocked_order or blocked_product:','if order is not None:'),
        ('late_terminal_guard',GUARD+anchor,anchor),
        ('terminal_completed','return "already_delivered"','return "not_paid_yet"'),
        ('terminal_cancelled','("expired", "cancelled")','("expired",)'),
        ('stars_unpaid','if invoice["gateway"] == "tgstars":\n        return "not_paid_yet"','if invoice["gateway"] == "tgstars":\n        return "verified_now"'),
        ('failed_expiry','invoice["id"], "expired"','invoice["id"], "pending"'),
        ('pending_claim','if state != clients.PAID:','if False:'),
        ('claim_identity','db.claim_extra_invoice, invoice["id"]','db.claim_extra_invoice, invoice["ref_id"]'),
        ('lost_claim','"verified_now" if claimed else "already_delivered"','"verified_now"'),
        ('gateway_error','return f"error:{e}"','return "not_paid_yet"'),
    ]:
        if name=='late_terminal_guard':
            # Retain guard after terminal return: deterministic ordering violation.
            yield name,change(ref,'check_invoice',lambda s:once(once(s,GUARD,''),'    try:',GUARD+'    try:'))
        else:yield name,change(ref,'check_invoice',lambda s:once(s,b,a))
    for name,b,a in [
        ('remote_amount','amount = int(invoice["amount_toman"])','amount = int(invoice["amount_toman"])+1'),
        ('remote_identity','remote_id = invoice["remote_id"]','remote_id = "wrong"'),
        ('cube_units','payable * 10','payable'),
        ('now_payment_id','meta.get("payment_id")','meta.get("wrong")'),
        ('now_price','meta.get("price_usd") or 0','0'),
    ]:yield name,change(ref,'_remote_state',lambda s:once(s,b,a))
    yield 'claim_before_guard',change(ref,'check_invoice',lambda s:once(s,GUARD,'    await asyncio.to_thread(db.claim_extra_invoice, invoice["id"])\n'+GUARD))
    yield 'wallet_side_effect',change(ref,'check_invoice',lambda s:once(s,GUARD,'    await asyncio.to_thread(db.add_wallet_credit, invoice["user_id"], 1)\n'+GUARD))
