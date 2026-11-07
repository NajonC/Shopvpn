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
FUNC='service_transfer_receive'
PRED='"service_kind" in cc.keys() and cc["service_kind"] == "composite"'
GUARD='''        cc = item["custom"]
        if "service_kind" in cc.keys() and cc["service_kind"] == "composite":
            await message.answer("composite_unsupported")
            return
'''
REFUSAL='            await message.answer("composite_unsupported")'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        await state.clear()\n        await message.answer(',GUARD+'        await state.clear()\n        await message.answer('))
    yield 'reference',reference
    def mutate(name,before,after):
        return name,change(reference,FUNC,lambda s:once(s,before,after))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('wrong_kind',PRED,PRED.replace('"composite"','"other"'))
    yield mutate('reject_missing',PRED,'("service_kind" not in cc.keys() or cc["service_kind"] == "composite")')
    yield mutate('reject_legacy',PRED,'"service_kind" in cc.keys()')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('leak_reason','"composite_unsupported"','"composite_unsupported"+cc["subscription_url"]')
    for label,statement in [
        ('state','await state.set_state("wrong")'),
        ('data','await state.update_data(cb_id="bad")'),
        ('clear','await state.clear()'),
        ('prompt','await message.answer("success")'),
        ('db','db.add_custom_config_history(cc["id"], "wrong", "wrong")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('omit_clear','        await state.clear()\n        await message.answer(','        await message.answer(')
    yield mutate('wrong_recipient','kb.service_transfer_confirm_kb(cb_id, target_id)','kb.service_transfer_confirm_kb(cb_id, target_id+1)')
    yield mutate('wrong_service','kb.service_transfer_confirm_kb(cb_id, target_id)','kb.service_transfer_confirm_kb("x999", target_id)')
    yield mutate('wrong_prompt','این عملیات **غیرقابل بازگشت** است.','wrong prompt')
    yield mutate('wrong_parse_mode','parse_mode="Markdown"','parse_mode="HTML"')
    yield mutate('wrong_keyboard','kb.service_transfer_confirm_kb(cb_id, target_id)','kb.service_rename_cancel_kb(cb_id)')
    yield mutate('omit_self_check','if target_id == user_tg_id:','if False:')
    yield mutate('omit_registration_check','if not target_user:','if False:')
    yield mutate('wrong_invalid_reason','❌ فقط آی‌دی عددی تلگرام را ارسال کنید.','invalid')
    yield mutate('strict_whitespace','text = (message.text or "").strip()','text = (message.text or "")')
    for label,predicate in [('feature','db.get_setting("svc_show_transfer","1") != "1"'),('test','cc["source"] == "test"')]:
        yield mutate('overstrict_'+label,'        cc = item["custom"]','        cc = item["custom"]\n        if '+predicate+':\n            await message.answer("wrong restriction")\n            return')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(user_tg_id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
