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
FUNC='custom_config_receive_username'
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
    reference=change(production,FUNC,lambda s:once(s,'        suffix = (message.text or "").strip()',GUARD+'        suffix = (message.text or "").strip()'))
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
        ('state','await state.set_state(CustomConfigFlow.waiting_volume)'),
        ('data','await state.update_data(custom_username="bad")'),
        ('clear','await state.clear()'),
        ('prompt','await message.answer("success")'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('provider','get_provider(db.get_panel_server(p["panel_server_id"]))'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('loose_name_bounds','[A-Za-z0-9_]{3,20}','[A-Za-z0-9_]{2,21}')
    yield mutate('strict_name_bounds','[A-Za-z0-9_]{3,20}','[A-Za-z0-9_]{4,19}')
    yield mutate('allow_space_unicode','[A-Za-z0-9_]{3,20}','.{3,20}')
    yield mutate('strict_whitespace','suffix = (message.text or "").strip()','suffix = (message.text or "")')
    yield mutate('omit_prefix','username = f"{prefix}-{suffix}" if prefix else suffix','username = suffix')
    yield mutate('wrong_separator','f"{prefix}-{suffix}"','f"{prefix}_{suffix}"')
    yield mutate('omit_collision','if (await asyncio.to_thread(db.is_custom_username_taken, username)):','if False:')
    yield mutate('wrong_collision_identity','db.is_custom_username_taken, username','db.is_custom_username_taken, "unused_fake_name"')
    yield mutate('wrong_saved_name','await state.update_data(custom_username=username)','await state.update_data(custom_username="wrong")',APPLY)
    yield mutate('wrong_state','await state.set_state(CustomConfigFlow.waiting_volume)','await state.set_state(CustomConfigFlow.waiting_username)',APPLY)
    yield mutate('wrong_price',"product['flat_price_per_gb']:,","product['flat_price_per_gb']+1:,",APPLY)
    yield mutate('wrong_min',"product['min_gb']","product['min_gb']+1",APPLY)
    yield mutate('wrong_max',"product['max_gb']","product['max_gb']-1",APPLY)
    yield mutate('wrong_duration',"product['duration_days']","product['duration_days']+1",APPLY)
    # cancel_kb appears in selected-product and global branches; mutate selected branch only.
    yield 'wrong_keyboard',change(reference,APPLY,lambda s:s.replace('reply_markup=kb.cancel_kb(),','reply_markup=kb.service_transfer_confirm_kb("x1",5103),',1))
    yield mutate('scan_sibling','        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None','        p = next((row for row in db.get_custom_config_products(True) if "service_kind" in row.keys() and row["service_kind"]=="composite"), db.get_custom_config_product(selected))')
