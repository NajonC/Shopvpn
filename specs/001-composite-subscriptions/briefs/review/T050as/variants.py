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
    def guard(s):
        return once(s,'        text = (message.text or "").strip()',GUARD+'        text = (message.text or "").strip()')
    reference=change(change(production,FUNC,guard),'custom_config_receive_duration',guard)
    yield 'reference',reference
    def mutate(name,before,after,func='_custom_config_finalize_order'):
        return name,change(reference,func,lambda s:once(s,before,after))
    for func in [FUNC,'custom_config_receive_duration']:
        yield mutate(func+'_omit_guard',GUARD,'',func)
        yield mutate(func+'_reject_missing',PRED,'p is not None and ("service_kind" not in p.keys() or p["service_kind"]=="composite")',func)
        yield mutate(func+'_reject_legacy',PRED,'p is not None and "service_kind" in p.keys()',func)
        yield mutate(func+'_no_reason','"composite_unsupported"','"unsupported"',func)
        yield mutate(func+'_early_debit',REFUSAL,'            db.add_wallet_credit(message.from_user.id,-1)\n'+REFUSAL,func)
        yield mutate(func+'_early_provider',REFUSAL,'            try:\n                get_provider(db.get_panel_server(p["panel_server_id"]))\n            except Exception:\n                pass\n'+REFUSAL,func)
    for label,b,a in [
        ('wrong_price','price = data.get("custom_price")','price = data.get("custom_price")+1'),
        ('wrong_volume','volume_gb = data.get("custom_volume_gb")','volume_gb = data.get("custom_volume_gb")+1'),
        ('wrong_user','message.from_user.id, volume_gb, username','9001, volume_gb, username'),
        ('omit_debit','db.add_wallet_credit, message.from_user.id, -wallet_used','db.add_wallet_credit, message.from_user.id, 0'),
        ('double_debit','db.add_wallet_credit, message.from_user.id, -wallet_used','db.add_wallet_credit, message.from_user.id, -2*wallet_used'),
        ('wrong_product','custom_product_id=product_id','custom_product_id=None'),
        ('wrong_days','provider.create_user(username, volume_gb, duration_days)','provider.create_user(username, volume_gb, duration_days+1)'),
        ('wrong_config_name','server["id"], result.username, volume_gb','server["id"], username, volume_gb'),
        ('wrong_config_product','order_id=order_id, product_id=product_id','order_id=order_id, product_id=None'),
        ('omit_approve','(await asyncio.to_thread(db.approve_custom_config_order, order_id))','pass'),
        ('omit_outer_reject','(await asyncio.to_thread(db.reject_order, order_id))\n            await state.clear()','pass\n            await state.clear()'),
        ('force_outer_refund','(await asyncio.to_thread(db.reject_order, order_id))\n            await state.clear()','db.add_wallet_credit(message.from_user.id,wallet_used)\n            (await asyncio.to_thread(db.reject_order, order_id))\n            await state.clear()'),
        ('omit_delivery','[result.subscription_url], final_price=0','[], final_price=0'),
        ('omit_notify','await _notify_admins_of_order(message.bot, order_id)','pass'),
        ('omit_outer_reason','"⛔️ خطای غیرمنتظره‌ای در پردازش سفارش رخ داد.\\n"','"wrong failure"'),
    ]:yield mutate(label,b,a)
