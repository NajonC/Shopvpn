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
FUNC='cb_service_transfer_confirm'
PRED='"service_kind" in cc.keys() and cc["service_kind"] == "composite"'
GUARD='''        if "service_kind" in cc.keys() and cc["service_kind"] == "composite":
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
REFUSAL='            await call.answer("composite_unsupported", show_alert=True)'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,'        cc = item["custom"]\n','        cc = item["custom"]\n'+GUARD))
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
        ('transfer','db.transfer_custom_config(cc["id"],user_tg_id,target_id)'),
        ('history','db.add_custom_config_history(cc["id"],"wrong","wrong")'),
        ('prompt','await call.message.answer("success")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
        ('notification','await call.bot.send_message(target_id,"wrong")'),
        ('list','await _show_my_orders_list(call.message,user_tg_id,edit=True)'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('omit_transfer','ok = (await asyncio.to_thread(db.transfer_custom_config, cc["id"], user_tg_id, target_id))','ok = True')
    yield mutate('wrong_target','db.transfer_custom_config, cc["id"], user_tg_id, target_id','db.transfer_custom_config, cc["id"], user_tg_id, 5102')
    yield mutate('wrong_service','db.transfer_custom_config, cc["id"], user_tg_id, target_id','db.transfer_custom_config, cc["id"]+1, user_tg_id, target_id')
    yield mutate('wrong_owner','db.transfer_custom_config, cc["id"], user_tg_id, target_id','db.transfer_custom_config, cc["id"], 5102, target_id')
    yield mutate('wrong_history_type','cc["id"], "transfer",','cc["id"], "wrong",')
    yield mutate('wrong_history_detail','f"از {user_tg_id} به {target_id}"','"wrong detail"')
    yield mutate('sibling_history','db.add_custom_config_history, cc["id"],','db.add_custom_config_history, cc["id"]+1,')
    yield mutate('erase_history','        await call.answer("✅ کانفیگ منتقل شد.", show_alert=True)','        with db._get_conn() as conn:\n            conn.execute("DELETE FROM custom_config_history WHERE detail LIKE ?", ("synthetic%",))\n        await call.answer("✅ کانفیگ منتقل شد.", show_alert=True)')
    yield mutate('wrong_alert','✅ کانفیگ منتقل شد.','wrong alert')
    yield mutate('wrong_notification_target','                target_id,','                5102,')
    yield mutate('wrong_notification_label',"cc['display_name'] or cc['username']","cc['username']")
    yield 'omit_notification',change(reference,FUNC,lambda s:once(s,'        try:\n            await call.bot.send_message(', '        async def _discard_notification(*args, **kwargs):\n            return None\n        try:\n            await _discard_notification('))
    yield 'omit_list',change(reference,FUNC,lambda s: ''.join(s.rsplit('        await _show_my_orders_list(call.message, user_tg_id, edit=True)',1)))
    yield mutate('omit_feature_gate','!= "1":','== "impossible":')
    yield mutate('omit_test_gate','if _is_test_item(item):','if False:')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(user_tg_id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
