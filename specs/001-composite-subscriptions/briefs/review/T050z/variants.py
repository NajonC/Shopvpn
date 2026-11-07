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
FUNC='cb_service_transfer_ask'
PRED='"service_kind" in cc.keys() and cc["service_kind"] == "composite"'
GUARD='''        cc = item["custom"]
        if "service_kind" in cc.keys() and cc["service_kind"] == "composite":
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
REFUSAL='            await call.answer("composite_unsupported", show_alert=True)'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        await state.set_state(ServiceTransferFlow.waiting_target_id)',''+GUARD+'        await state.set_state(ServiceTransferFlow.waiting_target_id)'))
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
        ('prompt','await call.message.answer("success")'),
        ('db','db.add_custom_config_history(cc["id"], "wrong", "wrong")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('omit_state','        await state.set_state(ServiceTransferFlow.waiting_target_id)\n','')
    yield mutate('wrong_target','await state.update_data(cb_id=cb_id)','await state.update_data(cb_id="wrong")')
    yield mutate('wrong_prompt','توجه: آن کاربر باید قبلاً بات را استارت کرده باشد.','wrong prompt')
    yield mutate('wrong_keyboard','kb.service_rename_cancel_kb(cb_id)','kb.service_transfer_confirm_kb(cb_id, 5102)')
    yield mutate('omit_feature_gate','!= "1":','== "impossible":')
    yield mutate('omit_test_gate','if _is_test_item(item):','if False:')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(call.from_user.id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
