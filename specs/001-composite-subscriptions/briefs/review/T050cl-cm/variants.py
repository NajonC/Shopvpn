"""Independent bounded admission reference and new order-entry mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
GATEWAY='order-entry'
def variants(user,payment,database,fulfillment):
    anchor='            if not egp.is_available(db, key, is_main_bot):'
    guard='''            product = await asyncio.to_thread(db.get_product, order["product_id"]) if order["product_id"] else None
            blocked_order = "service_kind" in order.keys() and order["service_kind"] == "composite"
            blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
            if blocked_order or blocked_product:
                await call.answer("composite_unsupported", show_alert=True)
                return
'''
    ref=change(user,'make_order_handler',lambda s:once(s,anchor,guard+anchor))
    yield 'reference',ref,payment,database,fulfillment
    def u(name,func,b,a):return name,change(ref,func,lambda s:once(s,b,a)),payment,database,fulfillment
    for name,b,a in [('order_alias','if blocked_order or blocked_product:','if blocked_product:'),('product_alias','if blocked_order or blocked_product:','if blocked_order:'),('product_link','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),('reason','composite_unsupported','unsupported'),('overstrict','if blocked_order or blocked_product:','if order is not None:'),('status','order["status"] != "pending"','False'),('available','if not egp.is_available(db, key, is_main_bot):','if False:'),('policy','if err:','if False:'),('amount','order_id, order["final_price"], label','order_id, order["final_price"]+1, label'),('actor','tenant_id, call.from_user.id, key','tenant_id, call.from_user.id+1, key'),('reference_id','key, "order", order_id','key, "order", order_id+999'),('error_reply','f"⚠️ {e}"','"wrong"')]:
        yield u(name,'make_order_handler',b,a)
    yield u('label','_order_label',"product['name'] if product else ''","'wrong'")
    for name,b,a in [('stars_payload','egp.stars_payload(result["invoice_id"])','"xg:9999"'),('stars_amount','amount=stars','amount=stars+1'),('stars_currency','currency="XTR"','currency="USD"'),('check_link',"result['invoice_id']","result['invoice_id']+999"),('pay_link','url=result["payment_url"]','url="https://wrong.example.invalid"'),('cube_exact','result["meta"].get("pay_amount_toman") or result["payable_amount"]','result["payable_amount"]'),('tetra_link','if gateway == "tetra98" and bot_url:','if False:')]:yield u(name,'present_invoice',b,a)
    for name,b,a in [('kind','db.create_extra_invoice, gateway, kind, ref_id','db.create_extra_invoice, gateway, "wallet_topup", ref_id'),('persist_amount','tg_id, amount_toman, payable','tg_id, amount_toman+1, payable'),('cube_fee','payable = cubepay_payable(db, amount_toman)','payable = amount_toman'),('remote_label','db.get_setting("zarinpal_merchant_id", "").strip(), amount_toman','db.get_setting("zarinpal_merchant_id", "").strip(), amount_toman+1')]:
        yield name,ref,change(payment,'create_invoice_for',lambda s:once(s,b,a)),database,fulfillment
    broken=change(payment,'create_invoice_for',lambda s:once(once(s,'if existing:','if False:'),'order_number = _order_number(kind, ref_id)','order_number = _order_number(kind, ref_id) + ("x" if existing else "")'))
    yield 'repeat',ref,broken,database,fulfillment
