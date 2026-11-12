"""Minimal selected web admin guard plus independent real caller mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['admin_panel/server.py','stock_alerts.py','database.py']
GUARD='''    product_guard = await asyncio.to_thread(db.get_product, order["product_id"])
    def marked(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    if marked(order) or marked(product_guard):
        raise HTTPException(400,"composite_unsupported")
'''
def variants(web,stock,db):
    ref=change(web,'api_approve_order',lambda s:once(s,'    if not (await asyncio.to_thread(db.claim_order, order_id)):',GUARD+'    if not (await asyncio.to_thread(db.claim_order, order_id)):'))
    yield 'reference',ref,stock,db
    for name,b,a in [('omit',GUARD,''),('order','marked(order) or marked(product_guard)','marked(product_guard)'),('product','marked(order) or marked(product_guard)','marked(order)'),('overstrict','if marked(order) or marked(product_guard):','if True:'),('absent','"service_kind" in row.keys() and row["service_kind"] == "composite"','("service_kind" not in row.keys() or row["service_kind"] == "composite")'),('reason','composite_unsupported','unsupported'),('leak','"composite_unsupported"','"composite_unsupported "+product_guard["name"]')]:
        yield 'guard_'+name,change(ref,'api_approve_order',lambda s:once(s,b,a)),stock,db
    yield 'late_after_claim',change(ref,'api_approve_order',lambda s:once(once(s,GUARD,''),'    if order["is_renewal"]:',GUARD+'    if order["is_renewal"]:')),stock,db
    alert='await check_and_notify_low_stock(lambda aid, text: tg_send(_bot_token(), aid, text), db, order["product_id"])'
    for name,b,a in [('skip_alert',alert,'pass'),('wrong_alert',alert,'await check_and_notify_low_stock(lambda aid, text: tg_send(_bot_token(), aid, text), db, order["product_id"]+999)'),('skip_approval','db.approve_order, order_id, [r["id"] for r in results]','db.get_order, order_id'),('reward_base','order["final_price"] or (product["price"] if product else 0)','1'),('skip_delivery','asyncio.create_task(deliver_config_to_user_web(','asyncio.create_task(asyncio.sleep(0)) #'),('quantity','order["quantity"] or 1','1'),('owner','db.take_unused_configs, order["product_id"], order["user_id"], quantity','db.take_unused_configs, order["product_id"], 1002, quantity')]:
        def edit(s):
            if name=='skip_delivery':
                start=s.rindex('    asyncio.create_task(deliver_config_to_user_web(');end=s.index('    return {"ok": True}',start)
                return s[:start]+'    asyncio.create_task(asyncio.sleep(0))\n'+s[end:]
            return once(s,b,a)
        yield name,change(ref,'api_approve_order',edit),stock,db
    def omitlog(s):
        start=s.rindex('    (await asyncio.to_thread(db.log_admin_action,');end=s.index('    await check_and_notify_low_stock',start)
        return s[:start]+'    pass\n'+s[end:]
    yield 'omit_stock_log',change(ref,'api_approve_order',omitlog),stock,db
    def omitnotify(s):
        b='await notify_user(order["user_id"], "✅ خرید شما تایید شد!")';return 'pass'.join(s.rsplit(b,1))
    yield 'skip_notify',change(ref,'api_approve_order',omitnotify),stock,db
    for name,b,a in [('preflight','except Exception:\n        return','except Exception:\n        raise'),('send_isolation','logger.warning("ارسال','return; logger.warning("ارسال'),('wrong_recipient','await send_fn(admin_id, text)','await send_fn(1001, text)')]:
        yield name,ref,change(stock,'check_and_notify_low_stock',lambda s:once(s,b,a)),db
    for name,b,a in [('equality','stock <= threshold','stock < threshold'),('repeat_latch','stock <= threshold and not already_sent','stock <= threshold'),('latch','SET low_stock_alert_sent=1','SET low_stock_alert_sent=0'),('reset','SET low_stock_alert_sent=0','SET low_stock_alert_sent=1')]:
        yield name,ref,stock,change(db,'check_low_stock_alert_state',lambda s:once(s,b,a))
