"""Caller admission reference only; settlement and tier effects remain actual SQL."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py','database.py']
HELPER='''
def _review_blocked_reseller(db, invoice):
    if invoice['kind'] != 'reseller_request':
        return False
    req = db.get_reseller_request(int(invoice['ref_id']))
    if req is None:
        return False
    product = db.get_product(req['supply_product_id']) if req['supply_product_id'] else None
    def marked(row):
        return row is not None and 'service_kind' in row.keys() and row['service_kind'] == 'composite'
    return marked(req) or marked(product)

'''
GUARD='    if _review_blocked_reseller(db, invoice):\n        return "composite_unsupported"\n'
def variants(payment,db):
    ref=HELPER+payment
    for entry,anchor in [('deliver','    kind = invoice["kind"]'),('_finalize_reseller','    request_id = int(invoice["ref_id"])')]:
        ref=change(ref,entry,lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref,db
    for name,b,a in [('request_alias','marked(req) or marked(product)','marked(product)'),('product_alias','marked(req) or marked(product)','marked(req)'),('ref_domain',"int(invoice['ref_id'])","int(invoice['id'])"),('overstrict','return marked(req) or marked(product)','return True')]:
        yield name,change(ref,'_review_blocked_reseller',lambda s:once(s,b,a)),db
    altered=ref
    for entry in ['deliver','_finalize_reseller']:altered=change(altered,entry,lambda s:once(s,GUARD,''))
    yield 'omit_both',altered,db
    yield 'reason',ref.replace('composite_unsupported','unsupported'),db
    yield 'caller_early_effect',change(ref,'deliver',lambda s:once(s,GUARD,'    if _review_blocked_reseller(db, invoice):\n        db.complete_reseller_request_gateway_payment(int(invoice["ref_id"]))\n        return "composite_unsupported"\n')),db
    for name,b,a in [('lookup','request_id = int(invoice["ref_id"])','request_id = int(invoice["id"])'),('prior','✅ این پرداخت قبلاً ثبت شده است.','prior'),('missing','⚠️ درخواست نمایندگی یافت نشد.','missing'),('commission',"{req['commission_percent'] or tier['commission_min'] or 10}","{99}"),('recipient','req["user_id"],','9002,'),('markup','callback_data=f"resreq_continue:{request_id}"','callback_data=f"resreq_continue:{request_id+1}"'),('omit_send','await bot.send_message(','await _notify_admins(')]:
        # omit_send remains syntactically valid but invokes forbidden notifier with real arguments.
        if name=='omit_send':continue
        yield name,change(ref,'_finalize_reseller',lambda s:once(s,b,a)),db
    for name,b,a in [('predicate','req["status"] != "awaiting_payment"','req["status"] != "pending_review"'),('status','next_status = "completed" if simple else "awaiting_bot_info"','next_status = "awaiting_bot_info"'),('tier','self.switch_agent_tier(req["user_id"], req["tier_code"])','self.switch_agent_tier(9002, req["tier_code"])'),('percent','percent = int(req["commission_percent"] or tier["commission_min"] or 10)','percent = 99'),('omit_enable','self.enable_inline_reseller(req["user_id"], percent)','pass'),('discount','int(req["discount_percent"]) if req["tier_code"] == "silver" and req["discount_percent"] is not None else None','None')]:
        def edit(s):
            if name=='discount':assert s.count(b)==2;return s.replace(b,a)
            return once(s,b,a)
        yield name,ref,change(db,'complete_reseller_request_gateway_payment',edit)
    yield 'sql_repeat',ref,change(db,'complete_reseller_request_gateway_payment',lambda s:once(once(s,'req["status"] != "awaiting_payment"','req["status"] not in ("awaiting_payment", "completed")'),"AND status='awaiting_payment'","AND status IN ('awaiting_payment','completed')"))
    yield 'omit_send',change('async def _review_noop(*a,**kw): pass\n'+ref,'_finalize_reseller',lambda s:once(s,'await bot.send_message(','await _review_noop(')),db
    yield 'send_text',change(ref,'_finalize_reseller',lambda s:once(s,'حالا توکن بات نمایندگی خودتان را','حالا wrong را')),db
