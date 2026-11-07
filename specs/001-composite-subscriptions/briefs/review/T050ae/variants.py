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
    reference=change(production,FUNC,lambda s:once(s,'        data = await state.get_data()',GUARD+'        data = await state.get_data()'))
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
        ('state','await state.set_state(CustomConfigFlow.waiting_duration)'),
        ('data','await state.update_data(custom_username="bad")'),
        ('clear','await state.clear()'),
        ('prompt','await message.answer("success")'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('provider','get_provider(db.get_panel_server(p["panel_server_id"]))'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('lower_boundary',"volume_gb < product[\"min_gb\"]", "volume_gb <= product[\"min_gb\"]")
    yield mutate('upper_boundary',"volume_gb > product[\"max_gb\"]", "volume_gb >= product[\"max_gb\"]")
    yield mutate('omit_bounds','if volume_gb < product["min_gb"] or volume_gb > product["max_gb"]:','if False:')
    yield mutate('reject_valid_integer','if not text.isdigit():','if True:')
    yield mutate('omit_trim','text = (message.text or "").strip()','text = (message.text or "")')
    yield mutate('wrong_price','custom_price=price','custom_price=price+1')
    yield mutate('wrong_volume','custom_volume_gb=volume_gb','custom_volume_gb=volume_gb+1')
    yield mutate('reject_free','if price <= 0:','if price <= 500:')
    yield mutate('zero_price_passes','if price <= 0:','if price < 0:')
    yield mutate('omit_zero_clear','            await state.clear()','            await state.update_data(wrong="state")')
    yield mutate('wrong_duration_state','await state.set_state(CustomConfigFlow.waiting_duration)','await state.set_state(CustomConfigFlow.waiting_volume)')
    yield mutate('wrong_min_days','product["min_days"] or 1','product["min_days"] or 2')
    yield mutate('wrong_max_days','product["max_days"] or 90','product["max_days"] or 89')
    yield mutate('wrong_days_prompt','تا {max_days} روز','تا {max_days+1} روز')
    yield mutate('scan_sibling','        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None','        p = next((row for row in db.get_custom_config_products(True) if "service_kind" in row.keys() and row["service_kind"]=="composite"), db.get_custom_config_product(selected))')
