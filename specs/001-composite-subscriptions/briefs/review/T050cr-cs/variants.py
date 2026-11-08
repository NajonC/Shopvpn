"""Direct payable boolean reference and independent alias/status/kind mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior_tools',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
def variants(payment):
    guard='''        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            return False
'''
    anchor='        return bool(order and order["status"] == "pending")'
    ref=change(payment,'ref_still_payable',lambda s:once(s,anchor,guard+anchor))
    yield 'reference',ref
    for name,b,a in [
        ('order_alias','if blocked_order or blocked_product:','if blocked_product:'),
        ('product_alias','if blocked_order or blocked_product:','if blocked_order:'),
        ('product_link','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),
        ('overstrict','if blocked_order or blocked_product:','if order is not None:'),
        ('order_status','order["status"] == "pending"','order["status"] != "pending"'),
        ('approved_order','order["status"] == "pending"','order["status"] in ("pending", "approved")'),
        ('missing_order','return bool(order and order["status"] == "pending")','return order is None or order["status"] == "pending"'),
        ('topup_status','topup["status"] == "pending"','topup["status"] != "pending"'),
        ('approved_topup','topup["status"] == "pending"','topup["status"] in ("pending", "approved")'),
        ('missing_topup','return bool(topup and topup["status"] == "pending")','return topup is None or topup["status"] == "pending"'),
        ('topup_reference','db.get_topup, ref_id','db.get_topup, 1'),
        ('reference_domain','ref_id = int(invoice["ref_id"])','ref_id = int(invoice["id"])'),
        ('kind_dispatch','if kind == "wallet_topup":','if False:'),
        ('reseller_default','    return True','    return False'),
        ('invoice_status','    kind = invoice["kind"]','    if invoice["status"] != "new":\n        return False\n    kind = invoice["kind"]'),
        ('global_composite_ban','    kind = invoice["kind"]','    if any("service_kind" in r.keys() and r["service_kind"] == "composite" for r in [db.get_order(1), db.get_product(1)] if r is not None):\n        return False\n    kind = invoice["kind"]'),
    ]:yield name,change(ref,'ref_still_payable',lambda s:once(s,b,a))
    yield 'claim_side_effect',change(ref,'ref_still_payable',lambda s:once(s,'    kind = invoice["kind"]','    await asyncio.to_thread(db.claim_extra_invoice, invoice["id"])\n    kind = invoice["kind"]'))
    yield 'wallet_side_effect',change(ref,'ref_still_payable',lambda s:once(s,'    kind = invoice["kind"]','    await asyncio.to_thread(db.add_wallet_credit, invoice["user_id"], 1)\n    kind = invoice["kind"]'))
