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
FUNC='cb_service_autorenew_toggle'


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
        ('flag','db.set_custom_config_auto_renew(cc["id"], user_tg_id, True)'),
        ('history','db.add_custom_config_history(cc["id"], "bad", "bad")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
        ('fetch','await fetch_sub_info(cc["subscription_url"])'),
        ('leak','await call.message.answer(cc["subscription_url"])'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('leak_in_refusal','"composite_unsupported"','"composite_unsupported" + cc["subscription_url"]')
    yield mutate('wrong_toggle','new_val = not ((cc["auto_renew"] if "auto_renew" in cc.keys() else 0) == 1)','new_val = True')
    yield mutate('wrong_target','db.set_custom_config_auto_renew, cc["id"], user_tg_id, new_val','db.set_custom_config_auto_renew, cc["id"]+1, user_tg_id, new_val')
    yield mutate('wrong_history_type','"auto_renew_toggle"','"wrong_history"')
    yield mutate('wrong_history_detail','"فعال شد" if new_val else "غیرفعال شد"','"wrong_detail"')
    yield mutate('omit_card','        await _refresh_service_card(call.message, user_tg_id, cb_id)\n','')
    yield mutate('wrong_on_alert','✅ تمدید خودکار فعال شد. هر بار نزدیک انقضا، از کیف پول کسر و تمدید می‌شود.','wrong ON')
    yield mutate('wrong_off_alert','✅ تمدید خودکار غیرفعال شد.','wrong OFF')
    yield mutate('omit_provider_read','fresh = await provider.get_user(cc["username"])','fresh = type("Fresh", (), {"subscription_url": ""})()', '_my_orders_item_text')
    yield mutate('omit_feature_check','if (await asyncio.to_thread(db.get_setting, "svc_show_auto_renew", "1")) != "1":','if False:')
    yield mutate('omit_test_check','if _is_test_item(item):','if False:')
    yield mutate('omit_duration_check','if (cc["duration_days"] or 0) <= 0:','if False:')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(user_tg_id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
