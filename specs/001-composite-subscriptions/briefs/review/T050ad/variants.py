"""Reviewer-only selected-product random-username reference and independent mutations."""
import ast


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])

FUNC='cb_custom_config_random_username'
APPLY='_custom_config_apply_username'
PRED='p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite"'
GUARD='''        selected = (await state.get_data()).get("product_id")
        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None
        if p is not None and "service_kind" in p.keys() and p["service_kind"] == "composite":
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
REFUSAL='            await call.answer("composite_unsupported", show_alert=True)'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        prefix = (await asyncio.to_thread(db.get_custom_config_prefix))',GUARD+'        prefix = (await asyncio.to_thread(db.get_custom_config_prefix))'))
    yield 'reference',reference
    def mutate(name,b,a,func=FUNC):
        return name,change(reference,func,lambda s:once(s,b,a))
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
        ('prompt','await call.message.answer("success")'),
        ('ack','await call.answer()'),
        ('db','db.set_setting("wrong_guard_write","1")'),
        ('provider','get_provider(db.get_panel_server(p["panel_server_id"]))'),
        ('random','random.choices("abc",k=8)'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('omit_prefix','candidate = f"{prefix}-{suffix}" if prefix else suffix','candidate = suffix')
    yield mutate('wrong_separator','f"{prefix}-{suffix}"','f"{prefix}_{suffix}"')
    yield mutate('wrong_suffix_length','k=8','k=7')
    yield mutate('wrong_alphabet','abcdefghijklmnopqrstuvwxyz0123456789','abcdefghijklmnopqrstuvwxyz')
    yield mutate('wrong_leading_u','suffix = "u"','suffix = "x"')
    yield mutate('early_retry_limit','range(10)','range(9)')
    yield mutate('extra_retry','range(10)','range(11)')
    yield mutate('omit_collision','if not (await asyncio.to_thread(db.is_custom_username_taken, candidate)):','if True:')
    yield mutate('wrong_collision_identity','db.is_custom_username_taken, candidate','db.is_custom_username_taken, "unused_fake_name"')
    yield mutate('wrong_saved_name','await state.update_data(custom_username=username)','await state.update_data(custom_username="wrong")',APPLY)
    yield mutate('wrong_state','await state.set_state(CustomConfigFlow.waiting_volume)','await state.set_state(CustomConfigFlow.waiting_username)',APPLY)
    yield mutate('wrong_price',"product['flat_price_per_gb']:,","product['flat_price_per_gb']+1:,",APPLY)
    yield mutate('wrong_min',"product['min_gb']","product['min_gb']+1",APPLY)
    yield mutate('wrong_max',"product['max_gb']","product['max_gb']-1",APPLY)
    yield mutate('wrong_duration',"product['duration_days']","product['duration_days']+1",APPLY)
    yield 'wrong_keyboard',change(reference,APPLY,lambda s:s.replace('reply_markup=kb.cancel_kb(),','reply_markup=kb.service_transfer_confirm_kb("x1",5103),',1))
    yield mutate('scan_sibling','        p = (await asyncio.to_thread(db.get_custom_config_product, selected)) if selected else None','        p = next((row for row in db.get_custom_config_products(True) if "service_kind" in row.keys() and row["service_kind"]=="composite"), db.get_custom_config_product(selected))')
