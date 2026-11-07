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
PRED='"service_kind" in cc.keys() and cc["service_kind"] == "composite"'
GUARD='''        if "service_kind" in cc.keys() and cc["service_kind"] == "composite":
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
REFUSAL='            await call.answer("composite_unsupported", show_alert=True)'
FUNC='cb_service_rename_ask'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        cc = item["custom"]\n','        cc = item["custom"]\n'+GUARD))
    yield 'reference',reference
    def mutate(name,before,after,func=FUNC):
        return name,change(reference,func,lambda s:once(s,before,after))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('wrong_kind',PRED,PRED.replace('"composite"','"other"'))
    yield mutate('reject_missing',PRED,'("service_kind" not in cc.keys() or cc["service_kind"] == "composite")')
    yield mutate('reject_legacy',PRED,'"service_kind" in cc.keys()')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    for label,statement in [
        ('fsm','await state.set_state(ServiceRenameFlow.waiting_suffix)'),
        ('data','await state.update_data(cb_id=cb_id)'),
        ('db','db.set_setting("bad_guard", "1")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
        ('prompt','await call.message.answer("success")'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('leak_in_refusal','"composite_unsupported"','"composite_unsupported"+cc["subscription_url"]')
    yield mutate('wrong_state','await state.set_state(ServiceRenameFlow.waiting_suffix)','await state.set_state(CustomConfigFlow.waiting_volume)')
    yield mutate('wrong_target','await state.update_data(cb_id=cb_id)','await state.update_data(cb_id="x999")')
    yield mutate('clear_sentinel','await state.update_data(cb_id=cb_id)','await state.clear()\n        await state.update_data(cb_id=cb_id)')
    yield mutate('wrong_display','current_label = cc["display_name"] or cc["username"]','current_label = cc["username"]')
    yield mutate('wrong_prefix','if prefix and current_label.startswith(prefix + "-"):','if prefix:')
    yield mutate('wrong_suffix_text','ادامه‌ی نام جدید','wrong suffix')
    yield mutate('wrong_plain_text','نام جدید کانفیگ را ارسال کنید.','wrong plain')
    yield mutate('wrong_keyboard','kb.service_rename_cancel_kb(cb_id)','kb.custom_config_username_kb()')
    yield mutate('omit_feature_check','if (await asyncio.to_thread(db.get_setting, "svc_show_rename", "1")) != "1":','if False:')
    yield mutate('omit_test_check','if _is_test_item(item):','if False:')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(call.from_user.id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
