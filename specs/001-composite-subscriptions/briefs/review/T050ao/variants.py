"""Reviewer-only scratch transformations: custom-plan UI guards, no production edits."""
import ast


def once(s, before, after):
    assert s.count(before) == 1, (before, s.count(before))
    return s.replace(before, after)


def change(source, name, fn):
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef)) and n.name == name]
    assert len(nodes) == 1
    n = nodes[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1]) + fn(''.join(lines[n.lineno-1:n.end_lineno])) + ''.join(lines[n.end_lineno:])
FUNC='custom_config_receive_volume'
APPLY='_custom_config_apply_username'
PRED='p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite"'
GUARD='''        selected = (await state.get_data()).get("product_id")
        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None
        if p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite":
            await message.answer("composite_unsupported")
            return
'''
REFUSAL='            await message.answer("composite_unsupported")'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        text = (message.text or "").strip()',GUARD+'        text = (message.text or "").strip()'))
    yield 'reference',reference
    def mutate(name,before,after,func=FUNC):
        return name,change(reference,func,lambda s:once(s,before,after))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('wrong_kind',PRED,PRED.replace('"composite"','"other"'))
    yield mutate('reject_missing',PRED,'p is not None and ("service_kind" not in p.keys() or p["service_kind"] == "composite")')
    yield mutate('reject_legacy',PRED,'p is not None and "service_kind" in p.keys()')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('leak_reason','"composite_unsupported"','"composite_unsupported"+p["name"]')
    for label,statement in [
        ('state','await state.set_state(CustomConfigFlow.waiting_receipt)'),
        ('data','await state.update_data(custom_username="bad")'),
        ('clear','await state.clear()'),
        ('prompt','await message.answer("success")'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('provider','get_provider(db.get_panel_server(p["panel_server_id"]))'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('lower_boundary','volume_gb < product["min_gb"]','volume_gb <= product["min_gb"]')
    yield mutate('upper_boundary','volume_gb > product["max_gb"]','volume_gb >= product["max_gb"]')
    yield mutate('omit_trim','text = (message.text or "").strip()','text = (message.text or "")')
    yield mutate('wrong_final_days','_custom_config_finalize_order(message, state, duration_days)','_custom_config_finalize_order(message, state, duration_days+1)')
    yield mutate('global_duration','["duration_days"]\n        await _custom_config_finalize_order','["min_gb"]\n        await _custom_config_finalize_order')
    for label,b,a in [
        ('wrong_price','price = data.get("custom_price")','price = data.get("custom_price")+1'),
        ('wrong_volume','volume_gb = data.get("custom_volume_gb")','volume_gb = data.get("custom_volume_gb")+1'),
        ('wrong_user','message.from_user.id, volume_gb, username','9001, volume_gb, username'),
        ('wrong_username','username = data.get("custom_username")','username = "wrong"'),
        ('omit_debit','db.add_wallet_credit, message.from_user.id, -wallet_used','db.add_wallet_credit, message.from_user.id, 0'),
        ('double_debit','db.add_wallet_credit, message.from_user.id, -wallet_used','db.add_wallet_credit, message.from_user.id, -2*wallet_used'),
        ('wrong_wallet_order','base_price=price, wallet_used=wallet_used','base_price=price, wallet_used=0'),
        ('wrong_product','custom_product_id=product_id','custom_product_id=None'),
        ('wrong_state','await state.set_state(CustomConfigFlow.waiting_receipt)','await state.set_state(CustomConfigFlow.waiting_duration)'),
        ('omit_order_id','await state.update_data(order_id=order_id, custom_volume_gb=volume_gb)','await state.update_data(custom_volume_gb=volume_gb)'),
        ('ignore_wallet_restriction','wallet_allowed = allowed_methods is None or "wallet" in allowed_methods','wallet_allowed = True'),
    ]:
        yield mutate(label,b,a,'_custom_config_finalize_order')
    yield mutate('scan_sibling','        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None','        p = next((row for row in db.get_custom_config_products(True) if "service_kind" in row.keys() and row["service_kind"]=="composite"), db.get_custom_config_product(selected))')
    yield mutate('omit_global_low_limit','volume_gb < settings["min_gb"]','False')
    yield mutate('omit_global_high_limit','volume_gb > settings["max_gb"]','False')
    yield mutate('omit_product_low_limit','volume_gb < product["min_gb"]','False')
    yield mutate('omit_product_high_limit','volume_gb > product["max_gb"]','False')
    yield mutate('skip_server_guard','if not server or not server["is_active"]:','if not server:','_custom_config_finalize_order')
    yield mutate('skip_payment_guard','if not (await asyncio.to_thread(db.has_any_payable_method, remaining_amount, allowed_methods)):','if False:','_custom_config_finalize_order')
    yield mutate('no_unavailable_refund','(await asyncio.to_thread(db.reject_order, order_id))\n                await state.clear()','pass\n                await state.clear()','_custom_config_finalize_order')
    yield mutate('price_before_refusal',REFUSAL,'            db.calc_custom_config_product_price(selected, 10)\n'+REFUSAL)
    yield mutate('double_unavailable_refund','(await asyncio.to_thread(db.reject_order, order_id))\n                await state.clear()','db.add_wallet_credit(message.from_user.id, wallet_used)\n                (await asyncio.to_thread(db.reject_order, order_id))\n                await state.clear()','_custom_config_finalize_order')
