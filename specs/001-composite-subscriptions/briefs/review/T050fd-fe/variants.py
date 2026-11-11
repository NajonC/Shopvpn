"""Minimal unsupported-AI execution guard; independent real caller mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['handlers_user.py','stock_alerts.py','database.py']
GUARD='''        if product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite":
            await message.answer("composite_unsupported")
            return
'''
def variants(user,stock,db):
    ref=change(user,'_ai_finalize_wallet_purchase',lambda s:once(s,'        if not product or not product["is_active"]:',GUARD+'        if not product or not product["is_active"]:'))
    yield 'reference',ref,stock,db
    for name,b,a in [('omit',GUARD,''),('overstrict','product["service_kind"] == "composite"','True'),('absent','"service_kind" in product.keys() and product["service_kind"] == "composite"','("service_kind" not in product.keys() or product["service_kind"] == "composite")'),('reason','composite_unsupported','unsupported'),('leak','await message.answer("composite_unsupported")','await message.answer("composite_unsupported "+product["name"])')]:
        yield 'ai_guard_'+name,change(ref,'_ai_finalize_wallet_purchase',lambda s:once(s,b,a)),stock,db
    for entry in ['_buy_start','_ai_finalize_wallet_purchase']:
        alert='await check_and_notify_low_stock(bot.send_message, db, product_id)'
        for name,b,a in [('skip_alert',alert,'pass'),('wrong_alert_product',alert,'await check_and_notify_low_stock(bot.send_message, db, product_id+999)'),('skip_approval','db.approve_order, order_id, [r["id"] for r in results]','db.get_order, order_id'),('wrong_reward_base','order["base_price"]','0'),('skip_delivery','await deliver_config_to_user(','await _review_no_delivery('),('wrong_quantity','db.take_unused_configs, product_id,','db.take_unused_configs, product_id+999,')]:
            # A no-op delivery function is supplied only as a mutant, never as reference.
            edited=change(ref,entry,lambda s:once(s,b,a))
            if name=='skip_delivery':edited='async def _review_no_delivery(*args,**kwargs): pass\n'+edited
            yield entry+'_'+name,edited,stock,db
        def early(s):
            # Removing approval simulates alert-side failures before approval; exact approved/debit checks detect it.
            return once(s,'db.approve_order, order_id, [r["id"] for r in results]','db.get_order, order_id')
        # Debit amount is separately pinned in both caller contracts.
        b='-wallet_used' if entry=='_buy_start' else '-total_price'
        yield entry+'_credit_instead_debit',change(ref,entry,lambda s:once(s,b,b[1:])),stock,db
    for name,b,a in [('no_preflight_isolation','except Exception:\n        return','except Exception:\n        raise'),('stop_send_failure','logger.warning("ارسال','return; logger.warning("ارسال')]:
        yield name,ref,change(stock,'check_and_notify_low_stock',lambda s:once(s,b,a)),db
    for name,b,a in [('equality','stock <= threshold','stock < threshold'),('repeat','stock <= threshold and not already_sent','stock <= threshold'),('latch','SET low_stock_alert_sent=1','SET low_stock_alert_sent=0'),('reset','SET low_stock_alert_sent=0','SET low_stock_alert_sent=1')]:
        yield name,ref,stock,change(db,'check_low_stock_alert_state',lambda s:once(s,b,a))
