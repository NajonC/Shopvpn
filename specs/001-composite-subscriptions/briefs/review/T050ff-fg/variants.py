"""Minimal selected ordinary admin guard; real inline STOCK effects remain intact."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['handlers_admin.py','stock_alerts.py','database.py']
GUARD='''        product_guard = await asyncio.to_thread(db.get_product, order["product_id"])
        def marked(row):
            return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
        if marked(order) or marked(product_guard):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(admin,stock,db):
    ref=change(admin,'cb_order_approve',lambda s:once(s,'        if not (await asyncio.to_thread(db.claim_order, order_id)):',GUARD+'        if not (await asyncio.to_thread(db.claim_order, order_id)):'))
    yield 'reference',ref,stock,db
    for name,b,a in [('omit',GUARD,''),('order','marked(order) or marked(product_guard)','marked(product_guard)'),('product','marked(order) or marked(product_guard)','marked(order)'),('overstrict','if marked(order) or marked(product_guard):','if True:'),('absent','"service_kind" in row.keys() and row["service_kind"] == "composite"','("service_kind" not in row.keys() or row["service_kind"] == "composite")'),('reason','composite_unsupported','unsupported'),('leak','"composite_unsupported", show_alert=True','"composite_unsupported "+product_guard["name"], show_alert=True')]:
        yield 'guard_'+name,change(ref,'cb_order_approve',lambda s:once(s,b,a)),stock,db
    alert='await check_and_notify_low_stock(bot.send_message, db, order["product_id"])'
    for name,b,a in [('skip_alert',alert,'pass'),('wrong_alert',alert,'await check_and_notify_low_stock(bot.send_message, db, order["product_id"]+999)'),('skip_approval','db.approve_order, order_id, [r["id"] for r in results]','db.get_order, order_id'),('reward_base','order["final_price"] or product["price"]','1'),('skip_delivery','await deliver_config_to_user(','await _review_no_delivery('),('quantity','order["quantity"] or 1','1'),('owner','db.take_unused_configs, order["product_id"], order["user_id"], quantity','db.take_unused_configs, order["product_id"], 1002, quantity'),('skip_log','db.log_admin_action,','db.get_order,')]:
        if name=='skip_log':continue # argument signature would be invalid, not a behavioral mutant
        edited=change(ref,'cb_order_approve',lambda s:(a.join(s.rsplit(b,1)) if name=='skip_delivery' else s.replace(b,a) if name=='quantity' else once(s,b,a)))
        if name=='skip_delivery':edited='async def _review_no_delivery(*args,**kwargs): pass\n'+edited
        yield name,edited,stock,db
    for name,b,a in [('preflight','except Exception:\n        return','except Exception:\n        raise'),('send_isolation','logger.warning("ارسال','return; logger.warning("ارسال')]:
        yield name,ref,change(stock,'check_and_notify_low_stock',lambda s:once(s,b,a)),db
    for name,b,a in [('equality','stock <= threshold','stock < threshold'),('repeat_latch','stock <= threshold and not already_sent','stock <= threshold'),('latch','SET low_stock_alert_sent=1','SET low_stock_alert_sent=0'),('reset','SET low_stock_alert_sent=0','SET low_stock_alert_sent=1')]:
        yield name,ref,stock,change(db,'check_low_stock_alert_state',lambda s:once(s,b,a))
