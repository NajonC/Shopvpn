"""Reviewer-only custom receipt reference and independent rule mutations."""
import ast


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])

FUNC='receive_custom_config_receipt'
GUARD='''        p = (await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"])) if order is not None else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await message.answer("composite_unsupported")
            return
'''
REFUSAL='            await message.answer("composite_unsupported")'


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
        ('prompt','await message.answer("success")'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('details','await message.answer(db.get_setting("card_number"))'),
    ]:yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('approved_allowed','if not order or order["status"] != "pending":','if not order:')
    yield mutate('omit_receipt_save','(await asyncio.to_thread(db.set_order_receipt, order_id, file_id, receipt_type))','pass')
    yield mutate('wrong_receipt_type','file_id, receipt_type))','file_id, "wrong"))')
    yield mutate('wrong_notify_file','receipt_file_id=file_id, receipt_type=receipt_type','receipt_file_id="wrong", receipt_type=receipt_type')
    yield ('retain_success_fsm',change(reference,FUNC,lambda s: s[:s.rindex('        await state.clear()')]+s[s.rindex('        await state.clear()'):].replace('        await state.clear()','        pass',1)))
    yield mutate('wrong_success','✅ رسید شما برای بررسی ارسال شد.','success')
    yield mutate('omit_menu','reply_markup=kb.menu_for_user(db, message.from_user.id, is_main_bot)','reply_markup=None')
    yield mutate('receipt_before_refusal',REFUSAL,'            db.set_order_receipt(order_id, "synthetic-photo", "photo")\n'+REFUSAL)
    yield mutate('admin_before_refusal',REFUSAL,'            await _notify_admins_of_order(bot, order_id, receipt_file_id="synthetic-photo", receipt_type="photo")\n'+REFUSAL)
    yield mutate('wrong_photo_size','message.photo[-1].file_id','message.photo[0].file_id','_receipt_payload')
