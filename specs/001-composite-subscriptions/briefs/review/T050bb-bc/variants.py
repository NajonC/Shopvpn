"""Exact-match, isolated executable helper variants, never applied to production."""
import ast
GUARD='''    product_guard = db.get_custom_config_product(order["custom_product_id"]) if order["is_custom_config"] and order["custom_product_id"] else None
    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    if order["is_custom_config"] and (composite(order) or composite(product_guard)):
        return "Unsupported composite custom fulfillment"
'''
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    result=s.replace(a,b);ast.parse(result);return result

def variants(source):
    anchor='    if order["status"] != "pending":'
    ref=replace(source,anchor,GUARD+anchor)
    yield 'reference',ref
    edits=[
      ('omit_order','composite(order) or composite(product_guard)','composite(product_guard)'),
      ('omit_product','composite(order) or composite(product_guard)','composite(order)'),
      ('omit_both',GUARD,''),
      ('no_reason','Unsupported composite custom fulfillment','Unavailable'),
      ('early_claim','    product_guard =','    db.claim_order(order_id)\n    product_guard ='),
      ('wrong_product','db.get_custom_config_product(order["custom_product_id"])','db.get_custom_config_product(99999)'),
      ('overstrict_legacy','composite(order) or composite(product_guard)','True'),
      ('sibling_blocks','composite(order) or composite(product_guard)','composite(order) or composite(product_guard) or any(composite(p) for p in db.get_custom_config_products())'),
      ('omit_status',anchor,'    if False:'),
      ('ignore_claim','if not db.claim_order(order_id):','if False:'),
      ('wrong_server','db.get_panel_server(order["custom_panel_server_id"])','db.get_panel_server(99999)'),
      ('wrong_username','provider.create_user(order["custom_username"],','provider.create_user("wrong_name",'),
      ('wrong_volume','provider.create_user(order["custom_username"], order["custom_volume_gb"], duration_days)','provider.create_user(order["custom_username"], 11, duration_days)'),
      ('wrong_duration','duration_days = db.get_custom_config_settings()["duration_days"]','duration_days = order["custom_duration_days"]'),
      ('wrong_config_owner','order["user_id"], server["id"], result.username','6201, server["id"], result.username'),
      ('wrong_config_name','server["id"], result.username,','server["id"], "wrong_name",'),
      ('wrong_config_link','duration_days, result.subscription_url, order_id=order_id,','duration_days, "wrong_link", order_id=order_id,'),
      ('wrong_config_order','duration_days, result.subscription_url, order_id=order_id,','duration_days, result.subscription_url, order_id=None,'),
      ('omit_approve','        db.approve_custom_config_order(order_id)\n',''),
      ('wrong_delivery_price','[result.subscription_url], final_price=order["final_price"],','[result.subscription_url], final_price=order["base_price"],'),
      ('wrong_reward_amount','db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])','db.reward_referrer_if_first_purchase(order["user_id"], order["final_price"])'),
      ('omit_reward','reward_info = db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])','reward_info = None'),
      ('omit_admin','    if notify_admins_fn:\n        try:\n            await notify_admins_fn(bot, order_id)','    if False:\n        try:\n            await notify_admins_fn(bot, order_id)'),
      ('wrong_success','✅ پرداخت تایید شد و کانفیگ تحویل داده شد.','wrong success'),
      ('wrong_error','⛔️ خطا در ساخت کانفیگ روی پنل: {e}','⛔️ wrong error: {e}'),
    ]
    for n,a,b in edits:yield n,replace(ref,a,b)
    # These repeated statements are intentionally all removed; exact expected count checked.
    a='            db.release_order_claim(order_id)\n';assert ref.count(a)==6
    yield 'omit_release',ref.replace(a,'')
