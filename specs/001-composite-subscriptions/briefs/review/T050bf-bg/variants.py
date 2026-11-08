"""Stock admission reference, independent guards and stock/reward mutants."""
import ast
MODULES=['abangateway_payment.py','blupal_payment.py','noapay_payment.py']
GUARD='''    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    catalog_product = db.get_product(order["product_id"]) if not order["is_renewal"] and not order["is_custom_config"] else None
    if catalog_product is not None and (composite(order) or composite(catalog_product)):
        return "Unsupported composite legacy stock fulfillment"
'''
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b);ast.parse(s);return s

def variants(sources):
    anchor='    if order["status"] != "pending":'
    reference={**sources,**{m:replace(sources[m],anchor,GUARD+anchor) for m in MODULES}}
    yield 'reference',reference
    for m in MODULES:
        s=reference[m]
        edits=[('omit_order','composite(order) or composite(catalog_product)','composite(catalog_product)'),('omit_product','composite(order) or composite(catalog_product)','composite(order)'),('no_reason','Unsupported composite legacy stock fulfillment','Unavailable'),('early_claim','    def composite(row):','    db.claim_order(order_id)\n    def composite(row):'),('overstrict','composite(order) or composite(catalog_product)','True'),('omit_status',anchor,'    if False:'),('ignore_claim','if not db.claim_order(order_id):','if False:'),('quantity','quantity = order["quantity"] or 1','quantity = 1'),('wrong_user','db.take_unused_configs(order["product_id"], order["user_id"], quantity)','db.take_unused_configs(order["product_id"], 9001, quantity)'),('wrong_product','db.take_unused_configs(order["product_id"], order["user_id"], quantity)','db.take_unused_configs(99999, order["user_id"], quantity)'),('omit_approval','            db.approve_order(order_id, [r["id"] for r in results])\n',''),('omit_alert','            await check_and_notify_low_stock(bot.send_message, db, order["product_id"])\n',''),('omit_reward','reward_info = db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])','reward_info = None'),('reward_amount','order["base_price"])','order["final_price"])'),('omit_admin','    if notify_admins_fn:\n        try:\n            await notify_admins_fn(bot, order_id)','    if False:\n        try:\n            await notify_admins_fn(bot, order_id)'),('recipient','                referrer_id,','                9001,'),('price','links, final_price=order["final_price"],','links, final_price=0,'),('no_release','            if not results:\n                db.release_order_claim(order_id)','            if not results:\n                pass')]
        for name,a,b in edits:yield m+':'+name,{**reference,m:replace(s,a,b)}
        start=s.index('        await deliver_config_to_user(\n',s.index('    else:\n        product ='))
        end=s.index('\n\n    reward_info',start)
        yield m+':omit_delivery',{**reference,m:replace(s,s[start:end],'        pass')}
    d=reference['database.py']
    start=d.index('    def take_unused_configs(');end=d.index('    def admin_take_random_config',start);block=d[start:end]
    for name,a,b in [('no_assign','assigned_user_id=?,','assigned_user_id=NULL,'),('wrong_duration','timedelta(days=duration_days)','timedelta(days=1)'),('reverse_fifo','ORDER BY id LIMIT ?','ORDER BY id DESC LIMIT ?')]:
        # Keep SQL parameter arity valid for assignment mutant.
        if name=='no_assign':continue
        yield 'database.py:'+name,{**reference,'database.py':replace(d,block,block.replace(a,b))}
    start=d.index('    def approve_order(');end=d.index('    def approve_order_auto',start);block=d[start:end]
    yield 'database.py:no_linkage',{**reference,'database.py':replace(d,block,block.replace('[(order_id, cid) for cid in config_ids]','[(None, cid) for cid in config_ids]'))}
