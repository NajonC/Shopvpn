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
            await message.answer("composite_unsupported")
            return
'''
REFUSAL='            await message.answer("composite_unsupported")'
FUNC='service_rename_receive'


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
        ('fsm','await state.clear()'),
        ('data','await state.update_data(cb_id="x999")'),
        ('local','db.rename_custom_config(cc["id"], user_tg_id, "bad")'),
        ('history','db.add_custom_config_history(cc["id"], "bad", "bad")'),
        ('provider','get_provider(db.get_panel_server(cc["panel_server_id"]))'),
        ('rename','try:\n                await get_provider(db.get_panel_server(cc["panel_server_id"])).rename_user(cc["username"], "bad")\n            except PanelError:\n                pass'),
        ('prompt','await message.answer("success")'),
    ]:
        yield mutate(label+'_before_refusal',REFUSAL,'            '+statement+'\n'+REFUSAL)
    yield mutate('leak_in_refusal','"composite_unsupported"','"composite_unsupported"+cc["subscription_url"]')
    yield mutate('wrong_prefix','prefix and current_label.startswith(prefix + "-")','prefix')
    yield mutate('wrong_display','current_label = cc["display_name"] or cc["username"]','current_label = cc["username"]')
    yield mutate('loose_name_bounds','[A-Za-z0-9_]{3,20}','[A-Za-z0-9_]{2,21}')
    yield mutate('strict_name_bounds','[A-Za-z0-9_]{3,20}','[A-Za-z0-9_]{4,19}')
    yield mutate('omit_same_name_check','if new_label == current_label:','if False:')
    yield mutate('omit_taken_name_check','if (await asyncio.to_thread(db.is_custom_username_taken, new_label)):','if False:')
    yield mutate('omit_remote_rename','                await provider.rename_user(cc["username"], new_label)\n','')
    yield mutate('wrong_remote_identity','provider.rename_user(cc["username"], new_label)','provider.rename_user("wrong", new_label)')
    yield mutate('lose_confirmed_username','panel_username = new_label','panel_username = None')
    yield mutate('rename_unconfirmed_username','panel_username = None','panel_username = "wrong"')
    yield mutate('wrong_local_target','db.rename_custom_config, cc["id"], user_tg_id, new_label','db.rename_custom_config, cc["id"]+1, user_tg_id, new_label')
    yield mutate('wrong_history_type','cc["id"], "rename",','cc["id"], "wrong",')
    yield mutate('wrong_history_detail','f"{old_label} ← {new_label} {note}"','"wrong detail"')
    yield mutate('extra_sibling_history','        await state.clear()\n        await _refresh_service_card','        db.add_custom_config_history(cc["id"]+1, "wrong", "wrong")\n        await state.clear()\n        await _refresh_service_card')
    yield mutate('wrong_panel_note','(روی خودِ پنل هم اعمال شد)','wrong panel note')
    yield mutate('wrong_fallback_note','(فقط نام نمایشی داخل بات تغییر کرد؛ لینک/کانفیگ فعلی روی پنل بدون تغییر کار می‌کند)','wrong fallback note')
    yield mutate('omit_state_clear','        await state.clear()\n        await _refresh_service_card','        await _refresh_service_card')
    yield mutate('wrong_card_message','✅ نام کانفیگ به','wrong card prefix')
    yield mutate('scan_sibling','        cc = item["custom"]','        cc = next((r for r in db.get_custom_configs_for_user(user_tg_id) if "service_kind" in r.keys() and r["service_kind"]=="composite"), item["custom"])')
    yield 'wrong_requester',change(reference,'_my_orders_items',lambda s:s.replace('db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)'))
