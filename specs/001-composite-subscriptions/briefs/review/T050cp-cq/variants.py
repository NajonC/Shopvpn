"""Bounded direct-creation reference; no production modifications."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('tools_prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
def variants(payment):
    guard='''    if kind == "order":
        order = await asyncio.to_thread(db.get_order, ref_id)
        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            raise ExtraGatewayError("composite_unsupported")
'''
    anchor='    existing = await asyncio.to_thread(db.get_pending_extra_invoice_for_ref, gateway, kind, ref_id)'
    ref=change(payment,'create_invoice_for',lambda s:once(s,anchor,guard+anchor))
    yield 'reference',ref
    for name,b,a in [
        ('order_alias','if blocked_order or blocked_product:','if blocked_product:'),
        ('product_alias','if blocked_order or blocked_product:','if blocked_order:'),
        ('selected_reference','db.get_order, ref_id','db.get_order, ref_id+999'),
        ('selected_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),
        ('reason','composite_unsupported','unsupported'),
        ('overstrict','if blocked_order or blocked_product:','if order is not None:'),
        ('late_guard',guard+anchor,anchor+'\n'+guard),
        ('availability','if not is_available(db, gateway):','if False:'),
        ('actor','gateway, kind, ref_id, tg_id, amount_toman','gateway, kind, ref_id, tg_id+1, amount_toman'),
        ('invoice_reference','gateway, kind, ref_id, tg_id, amount_toman','gateway, kind, ref_id+999, tg_id, amount_toman'),
        ('kind','db.create_extra_invoice, gateway, kind,','db.create_extra_invoice, gateway, "wallet_topup",'),
        ('amount','tg_id, amount_toman, payable,','tg_id, amount_toman+1, payable,'),
        ('payable','tg_id, amount_toman, payable,','tg_id, amount_toman, payable+1,'),
        ('metadata','created["payment_url"], created["meta"]','created["payment_url"], {}'),
        ('remote_id','created["remote_id"], order_number','None, order_number'),
        ('remote_amount','zarinpal_merchant_id", "").strip(), amount_toman,','zarinpal_merchant_id", "").strip(), amount_toman+1,'),
        ('remote_label','db.get_setting("zarinpal_merchant_id", "").strip(), amount_toman,\n                callback_url(tenant_id, gateway), order_name','db.get_setting("zarinpal_merchant_id", "").strip(), amount_toman,\n                callback_url(tenant_id, gateway), "wrong"'),
        ('cube_fee','payable = cubepay_payable(db, amount_toman)','payable = amount_toman'),
        ('stars_rate','payable = await stars_for_amount(db, amount_toman)','payable = 900'),
    ]:yield name,change(ref,'create_invoice_for',lambda s:once(s,b,a))
    yield 'repeat',change(ref,'create_invoice_for',lambda s:once(once(s,'if existing:','if False:'),'order_number = _order_number(kind, ref_id)','order_number = _order_number(kind, ref_id) + ("x" if existing else "")'))
