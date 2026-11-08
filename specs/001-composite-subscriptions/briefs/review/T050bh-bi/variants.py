"""Bounded pool-alias admission reference and independent helper/engine/SQL mutants."""
import ast
MODULES=['abangateway_payment.py','blupal_payment.py','noapay_payment.py']
READ='''    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    pool_target = db.get_config_by_id(order["renewal_target_id"]) if order["is_renewal"] and order["renewal_target_kind"] == "config" else None
    if pool_target is not None and pool_target["assigned_user_id"] != order["user_id"]:
        pool_target = None
    pool_product = db.get_product(pool_target["product_id"]) if pool_target is not None else None
'''
COND='order["is_renewal"] and order["renewal_target_kind"] == "config" and (composite(order) or composite(pool_target) or composite(pool_product))'
GUARD=READ+'    if '+COND+':\n        return "Unsupported composite legacy pool renewal"\n'
ENGINE_GUARD=READ+'    if '+COND+':\n        raise RenewalError("Unsupported composite legacy pool renewal")\n'
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
    ast.parse('async def check():\n'+s if s.startswith('    ') else s);return s

def variants(sources):
    anchor='    if order["status"] != "pending":'
    reference={**sources,**{m:replace(sources[m],anchor,GUARD+anchor) for m in MODULES}}
    reference['renewal_engine.py']=replace(sources['renewal_engine.py'],'    kind = order["renewal_target_kind"]',ENGINE_GUARD+'    kind = order["renewal_target_kind"]')
    yield 'reference',reference
    for m in MODULES:
        s=reference[m];start=s.index('    if order["is_renewal"]:\n');end=s.index('    if order["is_custom_config"]:\n',start);block=s[start:end]
        edits=[('omit_order','composite(order) or composite(pool_target) or composite(pool_product)','composite(pool_target) or composite(pool_product)'),('omit_target','composite(order) or composite(pool_target) or composite(pool_product)','composite(order) or composite(pool_product)'),('omit_product','composite(order) or composite(pool_target) or composite(pool_product)','composite(order) or composite(pool_target)'),('no_reason','Unsupported composite legacy pool renewal','Unavailable'),('early_claim','    def composite(row):','    db.claim_order(order_id)\n    def composite(row):'),('overstrict','composite(order) or composite(pool_target) or composite(pool_product)','True'),('omit_status',anchor,'    if False:'),('ignore_claim','if not db.claim_order(order_id):','if False:')]
        for name,a,b in edits:yield m+':'+name,{**reference,m:replace(s,a,b)}
        for name,a,b in [('omit_renewal','result_text = await execute_renewal(db, order)','result_text = "ignored"'),('omit_approval','        db.approve_renewal_order(order_id)\n',''),('recipient','bot.send_message(order["user_id"], result_text)','bot.send_message(9001, result_text)'),('omit_send','            await bot.send_message(order["user_id"], result_text)','            pass'),('omit_admin','        if notify_admins_fn:','        if False:'),('wrong_result','        return result_text','        return "wrong"'),('wrong_error','⛔️ تمدید ناموفق بود: {e}','wrong: {e}')]:
            yield m+':'+name,{**reference,m:replace(s,block,replace(block,a,b))}
        release='            db.release_order_claim(order_id)\n';assert block.count(release)==2
        yield m+':omit_release',{**reference,m:replace(s,block,block.replace(release,''))}
    s=reference['renewal_engine.py']
    for name,a,b in [('omit_order','composite(order) or composite(pool_target) or composite(pool_product)','composite(pool_target) or composite(pool_product)'),('omit_target','composite(order) or composite(pool_target) or composite(pool_product)','composite(order) or composite(pool_product)'),('omit_product','composite(order) or composite(pool_target) or composite(pool_product)','composite(order) or composite(pool_target)'),('wrong_days','db.extend_pool_config_expiry(target_id, order["user_id"], add_days)','db.extend_pool_config_expiry(target_id, order["user_id"], 1)'),('wrong_target','db.extend_pool_config_expiry(target_id, order["user_id"], add_days)','db.extend_pool_config_expiry(99999, order["user_id"], add_days)'),('wrong_owner','db.extend_pool_config_expiry(target_id, order["user_id"], add_days)','db.extend_pool_config_expiry(target_id, 9001, add_days)')]:
        yield 'renewal_engine.py:'+name,{**reference,'renewal_engine.py':replace(s,a,b)}
    s=reference['database.py'];start=s.index('    def extend_pool_config_expiry(');end=s.index('    def is_custom_username_taken',start);block=s[start:end]
    for name,a,b in [('discard_carryover','if current_dt > now:','if False:'),('expired_base','if current_dt > now:','if True:'),('no_persistence','(new_expires_at, config_id)','(row["expires_at"], config_id)'),('foreign_owner','WHERE id=? AND assigned_user_id=?','WHERE id=? AND ? IS NOT NULL')]:
        yield 'database.py:'+name,{**reference,'database.py':replace(s,block,replace(block,a,b))}
