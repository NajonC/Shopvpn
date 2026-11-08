"""Bounded shared admission reference; real DIRECT/factory/SQL retained."""
import ast
MODULES=['abangateway_payment.py','blupal_payment.py','noapay_payment.py']
GUARD='''    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    catalog_product = db.get_product(order["product_id"]) if not order["is_renewal"] and not order["is_custom_config"] else None
    if catalog_product is not None and (composite(order) or composite(catalog_product)):
        return "Unsupported composite legacy DIRECT fulfillment"
'''
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b);ast.parse(s);return s

def variants(sources):
    anchor='    if order["status"] != "pending":'
    ref={**sources,**{m:replace(sources[m],anchor,GUARD+anchor) for m in MODULES}}
    yield 'reference',ref
    for m in MODULES:
        s=ref[m]
        edits=[('omit_order','composite(order) or composite(catalog_product)','composite(catalog_product)'),('omit_product','composite(order) or composite(catalog_product)','composite(order)'),('reason','Unsupported composite legacy DIRECT fulfillment','Unavailable'),('early_claim','    def composite(row):','    db.claim_order(order_id)\n    def composite(row):'),('overstrict','composite(order) or composite(catalog_product)','True'),('status',anchor,'    if False:'),('claim','if not db.claim_order(order_id):','if False:'),('quantity','quantity = order["quantity"] or 1','quantity = 1'),('owner','quantity, user_id=order["user_id"], order_id=order_id)','quantity, user_id=9001, order_id=order_id)'),('approval','            db.approve_order_auto(order_id)\n',''),('reward','reward_info = db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])','reward_info = None'),('amount','order["base_price"])','order["final_price"])'),('price','links, final_price=order["final_price"],','links, final_price=0,'),('admin','    if notify_admins_fn:\n        try:\n            await notify_admins_fn(bot, order_id)','    if False:\n        try:\n            await notify_admins_fn(bot, order_id)'),('recipient','                referrer_id,','                9001,'),('release','            except (ProvisionError, DirectProvisionError) as e:\n                db.release_order_claim(order_id)','            except (ProvisionError, DirectProvisionError) as e:\n                pass')]
        # owner anchor occurs in both provision branches: constrain to DIRECT call
        edits=[(n, 'await provision_direct(db, product, '+a if n=='owner' else a, 'await provision_direct(db, product, '+b if n=='owner' else b) for n,a,b in edits]
        for n,a,b in edits:yield m+':'+n,{**ref,m:replace(s,a,b)}
        start=s.index('        await deliver_config_to_user(\n',s.index('    else:\n        product ='));end=s.index('\n\n    reward_info',start)
        yield m+':delivery',{**ref,m:replace(s,s[start:end],'        pass')}
    s=ref['direct_panel_provision.py']
    for n,a,b in [('volume','volume_gb = product["auto_provision_volume_gb"]','volume_gb = 1'),('duration','duration_days = product["duration_days"] if product["duration_days"] is not None else 30','duration_days = 30'),('names','range(1, quantity + 1)','range(0, quantity)'),('persist','if user_id is not None:','if False:'),('source','source="direct_product"','source="custom_config"'),('rollback','                await provider.delete_user(item["username"])','                pass'),('retry','range(5)','range(1)'),('overstrict_zero','volume_gb < 0','volume_gb <= 0')]:
        yield 'direct_panel_provision.py:'+n,{**ref,'direct_panel_provision.py':replace(s,a,b)}
    s=ref['database.py'];start=s.index('    def add_custom_config(');end=s.index('    def get_custom_configs_for_user',start);block=s[start:end]
    for n,a,b in [('history','self.add_custom_config_history(new_id, "purchase", f"{volume_gb} گیگ / {duration_days} روز")','pass'),('linkage','(order_id, user_id, panel_server_id, username, volume_gb, duration_days, subscription_url,','(None, user_id, panel_server_id, username, volume_gb, duration_days, subscription_url,')]:
        assert block.count(a)==1
        yield 'database.py:'+n,{**ref,'database.py':replace(s,block,block.replace(a,b))}
