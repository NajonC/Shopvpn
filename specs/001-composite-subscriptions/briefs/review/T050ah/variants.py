"""Reviewer-only custom manual card-entry reference and independent rule mutations."""
import ast


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])

FUNC='cb_pay_card_auto_custom_config'
GUARD='''        p = (await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"])) if order is not None else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
REFUSAL='            await call.answer("composite_unsupported", show_alert=True)'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        if not order or order["status"] != "pending":',GUARD+'        if not order or order["status"] != "pending":'))
    yield 'reference',reference
    def mutate(name,b,a,func=FUNC):return name,change(reference,func,lambda s:once(s,b,a))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('omit_order_guard','if blocked_order or blocked_product:','if blocked_product:')
    yield mutate('omit_product_guard','if blocked_order or blocked_product:','if blocked_order:')
    yield mutate('require_both_markers','if blocked_order or blocked_product:','if blocked_order and blocked_product:')
    yield mutate('wrong_order_kind','order["service_kind"] == "composite"','order["service_kind"] == "other"')
    yield mutate('wrong_product_kind','p["service_kind"] == "composite"','p["service_kind"] == "other"')
    yield mutate('reject_missing_marker','blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"','blocked_order = order is not None and ("service_kind" not in order.keys() or order["service_kind"] == "composite")')
    yield mutate('reject_legacy_marker','blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"','blocked_order = order is not None and "service_kind" in order.keys()')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('leak_name','"composite_unsupported"','"composite_unsupported"+order["custom_username"]')
    for label,statement in [
        ('state','await state.set_state(CustomConfigFlow.waiting_duration)'),
        ('data','await state.update_data(order_id=99999)'),
        ('clear','await state.clear()'),
        ('prompt','await call.message.answer("success")'),
        ('ack','await call.answer()'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('details','await call.message.answer(db.get_setting("card_number"))'),
    ]:yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('disabled_allowed','if (await asyncio.to_thread(db.get_setting, "card_to_card_auto_enabled", "0")) != "1":','if False:')
    yield mutate('approved_allowed','if not order or order["status"] != "pending":','if not order:')
    yield mutate('ignore_method_error','if err:','if False:')
    yield mutate('wrong_duration','duration_days = order["custom_duration_days"]','duration_days = 30')
    yield mutate('wrong_global_duration','duration_days = (await asyncio.to_thread(db.get_custom_config_settings))["duration_days"]','duration_days = 30')
    yield mutate('wrong_username',"escape_md(order['custom_username'])","'wrong'")
    yield mutate('wrong_volume',"order['custom_volume_gb']","order['custom_volume_gb']+1")
    yield mutate('wrong_wallet',"order['wallet_used']:,","order['wallet_used']+1:,")
    yield mutate('wrong_final_price','call.from_user.id, order["final_price"]','call.from_user.id, order["final_price"]+1')
    yield mutate('wrong_actor','call.from_user.id, order["final_price"]','999, order["final_price"]')
    yield mutate('wrong_rial','amount_rial = invoice.get("amount_rial") or invoice["amount_toman"] * 10','amount_rial = invoice["amount_toman"] * 100','_send_card_auto_details')
    yield mutate('wrong_timeout','"card_to_card_auto_timeout_minutes", "15"','"wrong_timeout", "15"','_send_card_auto_details')
    yield mutate('wrong_check',"invoice['invoice_id']",'999','_send_card_auto_details')
    yield mutate('wrong_minimum_boundary','order["final_price"] < min_amt','order["final_price"] <= min_amt','_order_payment_method_error')
    yield mutate('early_reservation',REFUSAL,'            await _send_card_auto_details(call.message, [], "order", order_id, call.from_user.id, order["final_price"])\n'+REFUSAL)
    yield mutate('wrong_kind','intro_lines, "order", order_id','intro_lines, "wallet", order_id')
    yield mutate('lose_reentry_reservation','        try:\n            invoice = await asyncio.to_thread(','        with db._get_conn() as conn:\n            conn.execute("DELETE FROM card_to_card_invoices")\n        try:\n            invoice = await asyncio.to_thread(','_send_card_auto_details')
    yield mutate('wrong_error_text','await target.answer(f"⚠️ {e}")','await target.answer("wrong")','_send_card_auto_details')
