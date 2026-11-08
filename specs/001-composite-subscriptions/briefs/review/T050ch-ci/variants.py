"""Independent admission, callback and inline settlement mutations."""
import ast
GATEWAY='extra'
def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)
def change(source,name,fn):
    ns=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name];assert len(ns)==1
    n=ns[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])
def variants(admin,payment):
    guard='''        order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice["kind"] == "order" else None
        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
    ack='        await call.answer("در حال بررسی وضعیت پرداخت...")'
    reference=change(admin,'cb_check_extra_gateway',lambda s:once(s,ack,guard+ack))
    yield 'reference',reference,payment
    def am(name,b,a):return name,change(reference,'cb_check_extra_gateway',lambda s:once(s,b,a)),payment
    yield am('omit_order','if blocked_order or blocked_product:','if blocked_product:')
    yield am('omit_product','if blocked_order or blocked_product:','if blocked_order:')
    yield am('wrong_order','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]')
    yield am('wrong_product','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999')
    yield am('reason','composite_unsupported','unsupported')
    yield am('early_ack',guard+ack,ack+'\n'+guard)
    yield am('early_process',guard+ack,'        await egp.process_invoice(db, bot, invoice)\n'+guard+ack)
    yield am('overstrict','if blocked_order or blocked_product:','if order is not None:')
    yield am('authority','if not invoice or invoice["user_id"] != call.from_user.id:','if not invoice:')
    yield am('wrong_invoice','db.get_extra_invoice, invoice_id','db.get_extra_invoice, invoice_id+1')
    def pm(name,func,b,a):return name,reference,change(payment,func,lambda s:once(s,b,a))
    yield pm('completed_fence','check_invoice','if invoice["status"] == "completed":','if False:')
    yield pm('expiry_fence','check_invoice','if invoice["status"] in ("expired", "cancelled"):','if False:')
    yield pm('failed_write','check_invoice','db.update_extra_invoice_status, invoice["id"], "expired"','db.update_extra_invoice_status, invoice["id"], "pending"')
    yield pm('pending_settles','check_invoice','if state != clients.PAID:','if False:')
    yield pm('ignore_claim_loss','check_invoice','return "verified_now" if claimed else "already_delivered"','return "verified_now"')
    yield pm('skip_release','process_invoice','await asyncio.to_thread(db.release_extra_invoice, invoice["id"])','pass')
    yield pm('wrong_delivery_ref','deliver','ref_id = int(invoice["ref_id"])','ref_id = int(invoice["ref_id"])+999')
    yield pm('skip_fulfillment','deliver','text = await abangateway_payment.finalize_paid_order(db, bot, ref_id, notify_admins_fn=notifier)','text = "wrong"')
