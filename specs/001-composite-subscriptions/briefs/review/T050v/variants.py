"""Reviewer-only scratch transformations: custom-plan UI guards, no production edits."""
import ast


def once(s, before, after):
    assert s.count(before) == 1, (before, s.count(before))
    return s.replace(before, after)


def change(source, name, fn):
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.AsyncFunctionDef) and n.name == name]
    assert len(nodes) == 1
    n = nodes[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1]) + fn(''.join(lines[n.lineno-1:n.end_lineno])) + ''.join(lines[n.end_lineno:])


PRED = '"service_kind" in p.keys() and p["service_kind"] == "composite"'
DISC = '''        visible = await asyncio.to_thread(db.get_custom_config_products, True)
        if any("service_kind" in p.keys() and p["service_kind"] == "composite" for p in visible):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
PICK = '''        p = product
        if "service_kind" in p.keys() and p["service_kind"] == "composite":
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
START = 'cb_custom_config_start'
SELECT = 'cb_custom_config_pick_product'
REFUSAL = '            await call.answer("composite_unsupported", show_alert=True)'


def variants(production):
    reference = change(production, START, lambda s: once(s, '        try:', DISC+'        try:'))
    reference = change(reference, SELECT, lambda s: once(s, '        await call.answer()\n        try:', PICK+'        await call.answer()\n        try:'))
    yield 'reference', reference
    def mutate(name, func, before, after):
        return name, change(reference, func, lambda s: once(s,before,after))
    for label,func,guard in [('discovery',START,DISC),('pick',SELECT,PICK)]:
        yield mutate(label+'_omit_guard',func,guard,'')
        yield mutate(label+'_wrong_kind',func,PRED,PRED.replace('"composite"','"other"'))
        yield mutate(label+'_reject_missing',func,PRED,'("service_kind" not in p.keys() or p["service_kind"] == "composite")')
        yield mutate(label+'_reject_legacy',func,PRED,'"service_kind" in p.keys()')
        yield mutate(label+'_no_reason',func,'"composite_unsupported"','"unsupported"')
        yield mutate(label+'_delete_before_refusal',func,REFUSAL,'            await call.message.delete()\n'+REFUSAL)
        yield mutate(label+'_state_before_refusal',func,REFUSAL,'            await state.set_state(CustomConfigFlow.waiting_username)\n'+REFUSAL)
        yield mutate(label+'_data_before_refusal',func,REFUSAL,'            await state.update_data(product_id=999)\n'+REFUSAL)
        yield mutate(label+'_write_before_refusal',func,REFUSAL,'            db.set_setting("bad_guard_write", "1")\n'+REFUSAL)
        yield mutate(label+'_prompt_before_refusal',func,REFUSAL,'            await call.message.answer("نام کاربری")\n'+REFUSAL)
        yield mutate(label+'_callback_before_refusal',func,REFUSAL,'            await call.answer("success")\n'+REFUSAL)
    yield mutate('discovery_scan_inactive',START,'db.get_custom_config_products, True','db.get_custom_config_products, False')
    yield mutate('pick_scan_siblings',SELECT,'p = product','p = next((row for row in db.get_custom_config_products(True) if "service_kind" in row.keys() and row["service_kind"] == "composite"), product)')
    yield mutate('pick_unavailable_alert',SELECT,'این پلن دیگر در دسترس نیست.','wrong unavailable')
    # Deletion is inside an existing try/except: removing it must preserve valid syntax.
    for label,func in [('discovery',START),('pick',SELECT)]:
        yield mutate(label+'_omit_delete',func,'            await call.message.delete()','            pass')
    for label,before,after in [
        ('wrong_product','product_id=product["id"]','product_id=999'),
        ('wrong_server','panel_server_id=server["id"]','panel_server_id=999'),
        ('clear_sentinel','await state.update_data(product_id=','await state.set_data(product_id='),
    ]:
        if label == 'clear_sentinel':
            yield mutate(label,'_custom_config_select_product','        await state.update_data(product_id=', '        await state.clear()\n        await state.update_data(product_id=')
        else:
            yield mutate(label,'_custom_config_select_product',before,after)
    yield mutate('wrong_username_state','_custom_config_ask_username','CustomConfigFlow.waiting_username','CustomConfigFlow.waiting_volume')
    yield mutate('wrong_username_text','_custom_config_ask_username','لطفاً یک نام کاربری دلخواه','wrong text')
    yield ('wrong_username_keyboard', change(reference,'_custom_config_ask_username',lambda s:s.replace('reply_markup=kb.custom_config_username_kb(),','reply_markup=kb.custom_config_product_select_kb([]),')))
    yield mutate('wrong_catalog_state','custom_config_start','await state.set_state(CustomConfigFlow.waiting_product_select)','await state.set_state(CustomConfigFlow.waiting_volume)')
    yield mutate('wrong_catalog_text','custom_config_start','لطفاً یکی از پلن‌های زیر را انتخاب کن:','wrong catalog')
    yield mutate('wrong_catalog_keyboard','custom_config_start','reply_markup=kb.custom_config_product_select_kb(products)','reply_markup=kb.custom_config_username_kb()')
