"""Bounded admission reference; independent actual callback mutations."""
import ast
GATEWAY='abangateway'
def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b));return s.replace(b,a)
def change(source,name,fn):
    n,=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])
GUARD='''        def composite(row):
            return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
        product_guard = await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"]) if order["custom_product_id"] else None
        if composite(order) or composite(product_guard):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(production,helper,db):
    anchor='        if order["status"] != "pending":'
    ref=change(production,'cb_order_approve',lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref,helper,db
    edits=[('omit_guard',GUARD,''),('omit_order','composite(order) or composite(product_guard)','composite(product_guard)'),('omit_product','composite(order) or composite(product_guard)','composite(order)'),('wrong_product','db.get_custom_config_product, order["custom_product_id"]','db.get_custom_config_product, 99999'),('reason','composite_unsupported','unsupported'),('early_claim',GUARD,'        await asyncio.to_thread(db.claim_order, order_id)\n'+GUARD),('overstrict','if composite(order) or composite(product_guard):','if True:'),('claim','if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:'),('approval','db.approve_custom_config_order, order_id','db.approve_custom_config_order, 99999'),('price','final_price=order["final_price"]','final_price=0'),('recipient','bot, order["user_id"], "کانفیگ شخصی"','bot, 9001, "کانفیگ شخصی"'),('duration','duration_days = order["custom_duration_days"]','duration_days = None'),('fallback','db.get_custom_config_settings))["duration_days"]','db.get_custom_config_settings))["duration_days"] + 1'),('volume','volume_gb=order["custom_volume_gb"]','volume_gb=1'),('name','username=order["custom_username"]','username="wrong"'),('product_link','product_id=order["custom_product_id"]','product_id=None'),('audit','db.log_admin_action,','lambda *a: None,'),('illicit_reward','            (await asyncio.to_thread(db.approve_custom_config_order, order_id))','            (await asyncio.to_thread(db.approve_custom_config_order, order_id))\n            await asyncio.to_thread(db.reward_referrer_if_first_purchase, order["user_id"],900)'),('release','                await asyncio.to_thread(db.release_order_claim, order_id)\n','')]
    yield 'repeat_fences',change(ref,'cb_order_approve',lambda s:once(once(s,anchor,'        if False:'),'if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:')),helper,db
    for name,b,a in edits:
        def edit(s):assert b in s,(name,b);return s.replace(b,a)
        yield name,change(ref,'cb_order_approve',edit),helper,db
