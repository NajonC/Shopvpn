"""Bounded shared admission reference; real AUTO/factory/SQL retained."""
import ast
MODULES=['abangateway_payment.py','blupal_payment.py','noapay_payment.py']
GUARD='''    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    catalog_product = db.get_product(order["product_id"]) if not order["is_renewal"] and not order["is_custom_config"] else None
    if catalog_product is not None and (composite(order) or composite(catalog_product)):
        return "Unsupported composite legacy AUTO fulfillment"
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
        edits=[('omit_order','composite(order) or composite(catalog_product)','composite(catalog_product)'),('omit_product','composite(order) or composite(catalog_product)','composite(order)'),('reason','Unsupported composite legacy AUTO fulfillment','Unavailable'),('early_claim','    def composite(row):','    db.claim_order(order_id)\n    def composite(row):'),('overstrict','composite(order) or composite(catalog_product)','True'),('status',anchor,'    if False:'),('claim','if not db.claim_order(order_id):','if False:'),('quantity','quantity = order["quantity"] or 1','quantity = 1'),('owner','quantity, user_id=order["user_id"], order_id=order_id)','quantity, user_id=9001, order_id=order_id)'),('approval','            db.approve_order_auto(order_id)\n',''),('reward','reward_info = db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])','reward_info = None'),('amount','order["base_price"])','order["final_price"])'),('price','links, final_price=order["final_price"],','links, final_price=0,'),('admin','    if notify_admins_fn:\n        try:\n            await notify_admins_fn(bot, order_id)','    if False:\n        try:\n            await notify_admins_fn(bot, order_id)'),('recipient','                referrer_id,','                9001,'),('release','            except (ProvisionError, DirectProvisionError) as e:\n                db.release_order_claim(order_id)','            except (ProvisionError, DirectProvisionError) as e:\n                pass')]
        # owner anchor occurs in both provision branches: constrain to AUTO call
        edits=[(n, 'await provision_auto_config(db, product, '+a if n=='owner' else a, 'await provision_auto_config(db, product, '+b if n=='owner' else b) for n,a,b in edits]
        for n,a,b in edits:yield m+':'+n,{**ref,m:replace(s,a,b)}
        start=s.index('        await deliver_config_to_user(\n',s.index('    else:\n        product ='));end=s.index('\n\n    reward_info',start)
        yield m+':delivery',{**ref,m:replace(s,s[start:end],'        pass')}
    s=ref['reseller_auto_provision.py']
    start=s.index('async def provision_auto_config(');end=s.index('async def provision_test_config',start);block=s[start:end]
    edits=[('volume','volume_gb = product["auto_provision_volume_gb"]','volume_gb = 1'),('duration','duration_days = product["duration_days"] if product["duration_days"] is not None else 30','duration_days = 30'),('total','total_volume_gb = volume_gb * quantity','total_volume_gb = volume_gb'),('rollback','                await provider.delete_user(item["username"])','                pass'),('retry','range(5)','range(1)'),('mirror','local_panel_id = local_db.get_or_create_mirror_panel_server(server)','local_panel_id = server["id"]'),('persist','if user_id is not None:','if False:'),('source','order_id=order_id, source=source,','order_id=order_id, source="custom_config",'),('fixed_amount','consume_reseller_product_credit(owner_id, fixed_product_id, quantity)','consume_reseller_product_credit(owner_id, fixed_product_id, 1)'),('volume_amount','            owner_id, total_volume_gb,','            owner_id, 1,'),('omit_consume_fixed','if not main_db.consume_reseller_product_credit(','if False and not main_db.consume_reseller_product_credit('),('omit_consume_volume','if not main_db.consume_reseller_credit(','if False and not main_db.consume_reseller_credit('),('overstrict_unlimited','duration_days = product["duration_days"] if product["duration_days"] is not None else 30','duration_days = product["duration_days"] or 30')]
    for n,a,b in edits:
        assert block.count(a)==1,(n,block.count(a))
        yield 'reseller_auto_provision.py:'+n,{**ref,'reseller_auto_provision.py':replace(s,block,block.replace(a,b))}
    s=ref['database.py']
    groups=[('add_custom_config','get_custom_configs_for_user',[('history','self.add_custom_config_history(new_id, "purchase", f"{volume_gb} گیگ / {duration_days} روز")','pass'),('linkage','(order_id, user_id, panel_server_id, username, volume_gb, duration_days, subscription_url,','(None, user_id, panel_server_id, username, volume_gb, duration_days, subscription_url,')]),('consume_reseller_credit','get_reseller_credit_log',[('credit_race','WHERE telegram_id=? AND reseller_credit_gb >= ?','WHERE telegram_id=? AND ? >= 0'),('credit_log','(user_tg_id, -amount_gb, reason, admin_id)','(user_tg_id, 0, reason, admin_id)')]),('consume_reseller_product_credit','get_resellers',[('fixed_race','AND qty_remaining >= ?','AND ? >= 0')])]
    for begin,end,edits in groups:
        start=s.index('    def '+begin+'(');stop=s.index('    def '+end+'(',start);block=s[start:stop]
        for n,a,b in edits:
            assert block.count(a)==1,(n,block.count(a))
            yield 'database.py:'+n,{**ref,'database.py':replace(s,block,block.replace(a,b))}
