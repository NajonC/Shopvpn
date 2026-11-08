"""Independent gateway and renewal-engine mutants, scratch only."""
import ast
MODULES=['abangateway_payment.py','blupal_payment.py','noapay_payment.py']
GUARD='''    def composite(row):
        return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
    target_guard = db.get_custom_config_owned(order["renewal_target_id"], order["user_id"]) if order["is_renewal"] and order["renewal_target_kind"] == "custom" else None
    if order["is_renewal"] and (composite(order) or composite(target_guard)):
        return "Unsupported composite single-panel renewal"
'''
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b);ast.parse("async def check():\n"+s if s.startswith("    ") else s);return s

def variants(sources):
    anchor='    if order["status"] != "pending":'
    reference={m:replace(sources[m],anchor,GUARD+anchor) for m in MODULES}
    reference['renewal_engine.py']=sources['renewal_engine.py']
    yield 'reference',reference
    for m in MODULES:
        s=reference[m]
        # Restrict ambiguous repeated success branches to the first renewal block.
        start=s.index('    if order["is_renewal"]:\n');end=s.index('    if order["is_custom_config"]:\n',start)
        block=s[start:end]
        edits=[('omit_order','composite(order) or composite(target_guard)','composite(target_guard)'),('omit_target','composite(order) or composite(target_guard)','composite(order)'),('omit_both',GUARD,''),('no_reason','Unsupported composite single-panel renewal','Unavailable'),('early_claim','    def composite(row):','    db.claim_order(order_id)\n    def composite(row):'),('wrong_target','db.get_custom_config_owned(order["renewal_target_id"], order["user_id"])','db.get_custom_config_owned(99999, order["user_id"])'),('overstrict','composite(order) or composite(target_guard)','True'),('omit_status',anchor,'    if False:'),('ignore_claim','if not db.claim_order(order_id):','if False:')]
        for name,a,b in edits:yield m+':'+name,{**reference,m:replace(s,a,b)}
        block_edits=[('omit_renewal','result_text = await execute_renewal(db, order)','result_text = "ignored"'),('omit_approval','        db.approve_renewal_order(order_id)\n',''),('wrong_order','db.approve_renewal_order(order_id)','db.approve_renewal_order(99999)'),('wrong_recipient','bot.send_message(order["user_id"], result_text)','bot.send_message(9001, result_text)'),('wrong_result','        return result_text','        return "wrong"'),('omit_admin','        if notify_admins_fn:','        if False:'),('omit_send','            await bot.send_message(order["user_id"], result_text)','            pass'),('wrong_error','⛔️ تمدید ناموفق بود: {e}','wrong: {e}'),('propagate_unexpected','        except Exception:\n            logger.exception','        except KeyError:\n            logger.exception')]
        for name,a,b in block_edits:yield m+':'+name,{**reference,m:replace(s,block,replace(block,a,b))}
        a='            db.release_order_claim(order_id)\n';assert block.count(a)==2
        yield m+':omit_release',{**reference,m:replace(s,block,block.replace(a,''))}
    eng=reference['renewal_engine.py']
    for name,a,b in [
        ('wrong_volume','add_volume_gb=add_volume','add_volume_gb=1'),('wrong_days','add_days=add_days','add_days=1'),('no_preserve','preserve_remaining=(mode == "full")','preserve_remaining=False'),('no_reset','reset_usage=(mode == "full")','reset_usage=False'),('wrong_name','cc["username"], add_volume_gb','"wrong_name", add_volume_gb'),('no_readback','if mode == "full" and add_volume:','if False:'),('wrong_local_volume','set_volume_gb=set_volume_gb','set_volume_gb=1'),('omit_local','        db.apply_custom_config_renewal(\n            cc["id"], add_volume, add_days, full_reset=(mode == "full"), set_volume_gb=set_volume_gb,\n        )','        pass')]:
        yield 'renewal_engine.py:'+name,{**reference,'renewal_engine.py':replace(eng,a,b)}
