"""Manual custom renewal admission plus independent callback/engine mutations."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('custom_mutations',Path(__file__).parents[1]/'T050bz-ca/variants.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
change=base.change;once=base.once;GATEWAY='unused'
GUARD='''        def composite(row):
            return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
        target_guard = await asyncio.to_thread(db.get_custom_config_owned, order["renewal_target_id"], order["user_id"]) if order["is_renewal"] and order["renewal_target_kind"] == "custom" else None
        pid = target_guard["product_id"] if target_guard is not None else None
        product_guard = await asyncio.to_thread(db.get_custom_config_product, pid) if pid else None
        if composite(order) or composite(target_guard) or composite(product_guard):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(production,engine,db):
    anchor='        if order["status"] != "pending":'
    ref=change(production,'cb_order_approve',lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref,engine,db
    edits=[('omit_guard',GUARD,''),('omit_order','composite(order) or composite(target_guard) or composite(product_guard)','composite(target_guard) or composite(product_guard)'),('omit_target','composite(order) or composite(target_guard) or composite(product_guard)','composite(order) or composite(product_guard)'),('omit_product','composite(order) or composite(target_guard) or composite(product_guard)','composite(order) or composite(target_guard)'),('wrong_target','db.get_custom_config_owned, order["renewal_target_id"], order["user_id"]','db.get_custom_config_owned, 99999, order["user_id"]'),('wrong_product','db.get_custom_config_product, pid','db.get_custom_config_product, 99999'),('reason','composite_unsupported','unsupported'),('early_claim',GUARD,'        await asyncio.to_thread(db.claim_order, order_id)\n'+GUARD),('overstrict','if composite(order) or composite(target_guard) or composite(product_guard):','if True:'),('claim','if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:'),('approval','db.approve_renewal_order, order_id','db.approve_renewal_order, 99999'),('release','                await asyncio.to_thread(db.release_order_claim, order_id)\n',''),('skip_renewal','result_text = await execute_renewal(db, order)','result_text = "wrong"'),('recipient','bot.send_message(order["user_id"], result_text)','bot.send_message(9001, result_text)'),('audit','db.log_admin_action,','lambda *a: None,'),('illicit_reward','            (await asyncio.to_thread(db.approve_renewal_order, order_id))','            (await asyncio.to_thread(db.approve_renewal_order, order_id))\n            await asyncio.to_thread(db.reward_referrer_if_first_purchase, order["user_id"],900)')]
    yield 'repeat_fences',change(ref,'cb_order_approve',lambda s:once(once(s,anchor,'        if False:'),'if not (await asyncio.to_thread(db.claim_order, order_id)):','if False:')),engine,db
    for name,b,a in edits:
        def edit(s):assert b in s,(name,b);return s.replace(b,a)
        yield name,change(ref,'cb_order_approve',edit),engine,db
    for name,b,a in [
        ('ownership','db.get_custom_config_owned(target_id, order["user_id"])','db.get_custom_config_by_id(target_id)'),
        ('volume','add_volume_gb=add_volume','add_volume_gb=1'),
        ('days','add_days=add_days','add_days=1'),
        ('name','cc["username"], add_volume_gb','"wrong", add_volume_gb'),
        ('preserve','preserve_remaining=(mode == "full")','preserve_remaining=False'),
        ('reset','reset_usage=(mode == "full")','reset_usage=False'),
        ('readback','if mode == "full" and add_volume:','if False:'),
        ('local_volume','set_volume_gb=set_volume_gb','set_volume_gb=1'),
        ('local_days','cc["id"], add_volume, add_days','cc["id"], add_volume, 0'),
    ]:
        yield name,ref,once(engine,b,a),db
