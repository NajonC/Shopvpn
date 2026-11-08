"""Independent admin callback and actual verifier mutations."""
import ast
SOURCE='handlers_admin.py'
GATEWAY='abangateway'
def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)
def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])
def variants(production,helper):
    g=GATEWAY;func='cb_check_'+g+'_invoice';ack='        await call.answer("در حال بررسی...")'
    guard='''        order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice["kind"] == "order" else None
        product = await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"]) if order is not None and order["is_custom_config"] and order["custom_product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
    reference=change(production,func,lambda s:once(s,ack,guard+ack))
    yield 'reference',reference,helper
    def mutate(name,b,a):return name,change(reference,func,lambda s:once(s,b,a)),helper
    yield mutate('omit_guard',guard,'')
    yield mutate('omit_order','if blocked_order or blocked_product:','if blocked_product:')
    yield mutate('omit_product','if blocked_order or blocked_product:','if blocked_order:')
    yield mutate('both_required','if blocked_order or blocked_product:','if blocked_order and blocked_product:')
    yield mutate('wrong_order_ref','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]')
    yield mutate('wrong_product_ref','db.get_custom_config_product, order["custom_product_id"]','db.get_custom_config_product, order["custom_product_id"]+999')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('early_ack',guard+ack,ack+'\n'+guard)
    yield mutate('early_verify',guard+ack,'        await '+g+'_payment.try_verify_and_finalize(db, invoice)\n'+guard+ack)
    yield mutate('legacy_overstrict','if blocked_order or blocked_product:','if order is not None:')
    yield mutate('topup_overstrict','if blocked_order or blocked_product:','if True:')
    yield mutate('no_authority','if not admin_only(call.from_user.id):','if False:')
    yield mutate('wrong_invoice','db.get_'+g+'_invoice, invoice_id','db.get_'+g+'_invoice, invoice_id+1')
    yield mutate('no_order_finalizer','text = await '+g+'_payment.finalize_paid_order(','text = "wrong" if True else await '+g+'_payment.finalize_paid_order(')
    yield mutate('wrong_finalizer_ref','finalize_paid_order(db, bot, invoice["ref_id"])','finalize_paid_order(db, bot, invoice["ref_id"]+999)')
    yield mutate('wrong_topup_ref','finalize_paid_topup(db, invoice["ref_id"])','finalize_paid_topup(db, invoice["ref_id"]+999)')
    yield mutate('wrong_pending','elif result == "not_paid_yet":','elif result == "never":')
    yield mutate('wrong_cancel','elif result in ("expired", "cancelled"):','elif result in ("expired",):')
    def hm(name,func,b,a):return name,reference,change(helper,func,lambda s:once(s,b,a))
    yield hm('no_completed_fence','try_verify_and_finalize','if invoice_row["status"] == "completed":','if False:')
    yield hm('wrong_remote_ref','try_verify_and_finalize','invoice_id = invoice_row["invoice_id"]','invoice_id = "wrong"')
    yield hm('no_status_write','try_verify_and_finalize','db.update_'+g+'_invoice_status(invoice_id, remote_status)','None')
    if g=='abangateway':
        yield hm('no_verify','try_verify_and_finalize','await abangateway_client.verify_invoice(api_key, invoice_id)','None')
        yield hm('no_complete','try_verify_and_finalize','db.update_abangateway_invoice_status(invoice_id, "completed")\n    return "verified_now"','None\n    return "verified_now"')
    else:
        yield hm('ignore_claim_loss','try_verify_and_finalize','if not db.claim_blupal_invoice(invoice_id):','if db.claim_blupal_invoice(invoice_id) and False:')
    yield hm('no_approve_topup','finalize_paid_topup','if not db.approve_topup(topup_id):','if False:')
