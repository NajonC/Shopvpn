"""Scratch custom-order callback guard and adapter rule mutations."""
import ast


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])

FUNC='cb_check_blupal'
GUARD='''        order = (await asyncio.to_thread(db.get_order, invoice_row["ref_id"])) if invoice_row["kind"] == "order" else None
        custom = order is not None and order["is_custom_config"]
        product = (await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"])) if custom and order["custom_product_id"] else None
        blocked_order = custom and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
ACK='        await call.answer("در حال بررسی وضعیت پرداخت...")'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,ACK,GUARD+ACK))
    yield 'reference',reference
    def mutate(name,b,a):return name,change(reference,FUNC,lambda s:once(s,b,a))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('omit_order_guard','if blocked_order or blocked_product:','if blocked_product:')
    yield mutate('omit_product_guard','if blocked_order or blocked_product:','if blocked_order:')
    yield mutate('both_required','if blocked_order or blocked_product:','if blocked_order and blocked_product:')
    yield mutate('wrong_ref','db.get_order, invoice_row["ref_id"]','db.get_order, invoice_row["id"]')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('early_ack',GUARD+ACK,ACK+'\n'+GUARD)
    yield mutate('early_verify',GUARD+ACK,'        await blupal_payment.try_verify_and_finalize(db, invoice_row)\n'+GUARD+ACK)
    yield mutate('no_ownership','if not invoice_row or invoice_row["user_id"] != call.from_user.id:','if not invoice_row:')
    yield mutate('wrong_lookup','db.get_blupal_invoice, invoice_db_id','db.get_blupal_invoice, invoice_db_id+1')
    yield mutate('wrong_helper_input','try_verify_and_finalize(db, invoice_row)','try_verify_and_finalize(db, db.get_blupal_invoice(invoice_db_id-1))')
    yield mutate('wrong_pending','if result == "not_paid_yet":','if result == "already_delivered":')
    yield mutate('wrong_expired','if result in ("expired", "cancelled"):','if result in ("expired",):')
    yield mutate('no_finalizer','text = await blupal_payment.finalize_paid_order(','text = "wrong" if True else await blupal_payment.finalize_paid_order(')
    yield mutate('wrong_finalizer_ref','db, bot, invoice_row["ref_id"], notify_admins_fn','db, bot, invoice_row["ref_id"]+999, notify_admins_fn')
    yield mutate('wrong_topup_ref','finalize_paid_topup(db, invoice_row["ref_id"])','finalize_paid_topup(db, invoice_row["ref_id"]+999)')
    yield mutate('legacy_overstrict','if blocked_order or blocked_product:','if custom:')
    yield mutate('sibling_overstrict','if blocked_order or blocked_product:','if blocked_order or blocked_product or any("service_kind" in p.keys() and p["service_kind"]=="composite" for p in db.get_custom_config_products()):')


def payment_variants(production):
    def mutate(name,b,a):return name,change(production,'try_verify_and_finalize',lambda s:once(s,b,a))
    yield mutate('ignore_lost_invoice_claim','if not db.claim_blupal_invoice(invoice_id):','if False:')
    yield mutate('claim_wrong_invoice','db.claim_blupal_invoice(invoice_id)','db.claim_blupal_invoice("synthetic-decoy")')
    yield mutate('skip_completed_shortcut','if invoice_row["status"] == "completed":','if False:')
    yield mutate('force_paid_for_pending','if remote_status != "paid":','if False:')
    yield mutate('omit_remote_error_reason','return f"error:{e}"','return "error:wrong"')
