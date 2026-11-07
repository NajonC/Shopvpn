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

FUNC='cb_pay_abangateway_custom_config'
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
    yield mutate('approved_allowed','if not order or order["status"] != "pending":','if not order:')
    yield mutate('ignore_method_error','if err:','if False:')
    yield mutate('wrong_actor','call.from_user.id, "order"','999, "order"')
    yield mutate('wrong_kind','call.from_user.id, "order"','call.from_user.id, "wallet_topup"')
    yield mutate('wrong_amount','order["final_price"],','order["final_price"]+1,')
    yield mutate('wrong_tenant','"miniapp_tenant_id", ""','"wrong_tenant", ""')
    yield mutate('wrong_order_name',"{order['custom_username']}","wrong")
    yield mutate('wrong_minimum_boundary','order["final_price"] < min_amt','order["final_price"] <= min_amt','_order_payment_method_error')
    yield mutate('wrong_error','await call.message.answer(f"⚠️ {e}")','await call.message.answer("wrong")')
    yield mutate('wrong_check_id',"{invoice_row['id']}","99999")
