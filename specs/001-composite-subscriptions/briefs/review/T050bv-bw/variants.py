"""Bounded manual admission reference and independent actual callback mutations."""
import ast
GATEWAY='abangateway'
def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)
def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])
GUARD='''        def composite(row):
            return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
        target = await asyncio.to_thread(db.get_config_by_id, order["renewal_target_id"]) if order["is_renewal"] and order["renewal_target_id"] else None
        pid = target["product_id"] if target is not None else order["product_id"]
        product_guard = await asyncio.to_thread(db.get_product, pid) if pid else None
        if composite(order) or composite(target) or composite(product_guard):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(production,helper,db):
    anchor='        if order["status"] != "pending":'
    ref=change(production,'cb_order_approve',lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref,helper,db
    edits=[('omit_guard',GUARD,''),('omit_order','composite(order) or composite(target) or composite(product_guard)','composite(target) or composite(product_guard)'),('omit_product','composite(order) or composite(target) or composite(product_guard)','composite(order) or composite(target)'),('no_reason','composite_unsupported','unsupported'),('early_claim',GUARD,'        await asyncio.to_thread(db.claim_order, order_id)\n'+GUARD),('overstrict','if composite(order) or composite(target) or composite(product_guard):','if True:'),('authority','if not admin_only(call.from_user.id):','if False:'),('wrong_order','db.get_order, order_id','db.get_order, order_id+999'),('wrong_product','db.get_product, pid','db.get_product, pid+999'),('claim','if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:'),('quantity','quantity = order["quantity"] or 1','quantity = 1'),('stock_approve','db.approve_order, order_id,','db.approve_order, order_id+999,'),('auto_approve','db.approve_order_auto, order_id','db.approve_order_auto, order_id+999'),('delivery_price','final_price=order["final_price"]','final_price=0'),('reward_base','order["final_price"] or product["price"]))','product["price"]))'),('reward_skip','db.reward_referrer_if_first_purchase, order["user_id"]','db.reward_referrer_if_first_purchase, 99999'),('wrong_recipient','bot, order["user_id"], product["name"]','bot, 9001, product["name"]'),('direct_dispatch','if product["provision_server_id"]:','if False:'),('release_stock','            await asyncio.to_thread(db.release_order_claim, order_id)\n            await call.answer("⛔️ موجودی','            await call.answer("⛔️ موجودی'),('release_provision','                await asyncio.to_thread(db.release_order_claim, order_id)\n                await call.answer(f"⛔️ {e}','                await call.answer(f"⛔️ {e}'),('audit','db.log_admin_action,','db.get_order,')]
    yield 'repeat_fences',change(ref,'cb_order_approve',lambda s:once(once(s,anchor,'        if False:'),'if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:')),helper,db
    for name,b,a in edits:
        # repeated quantity/price/recipient/audit deliberately break all callback branches
        def edit(s):
            assert b in s,(name,b)
            return s.replace(b,a)
        if name=='audit':continue # wrong-signature mutations are not behavioral evidence
        yield name,change(ref,'cb_order_approve',edit),helper,db
