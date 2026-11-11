"""Actual policy/continuation mutations, independent clean source for each."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['handlers_user.py','extra_gateway_user.py']
def variants(user,gateway):
    yield 'reference',user,gateway
    for entry in ['_order_payment_method_error','_wallet_topup_method_error']:
        edits=[('equal',' < min_amt',' <= min_amt'),('skip_min','if min_amt and','if False and'),('wrong_key','db.get_payment_method_min_amount, method_key','db.get_payment_method_min_amount, "unknown"'),('wrong_min_text','{min_amt:,}','{min_amt+1:,}')]
        if entry=='_order_payment_method_error':
            edits += [('skip_product','elif product_id and not','elif False and not'),('skip_custom','if not (await asyncio.to_thread(db.custom_config_allows_payment_method','if False and not (await asyncio.to_thread(db.custom_config_allows_payment_method'),('wrong_product','db.product_allows_payment_method, product_id','db.product_allows_payment_method, product_id+999'),('overstrict','        return None','        return "unsupported"')]
        else:edits += [('skip_permission','if not (await asyncio.to_thread(db.wallet_topup_allows_payment_method','if False and not (await asyncio.to_thread(db.wallet_topup_allows_payment_method'),('overstrict','        return None','        return "unsupported"')]
        for name,b,a in edits:yield entry+name,change(user,entry,lambda s:once(s,b,a)),gateway
    for entry,call in [('make_order_handler','order_error(order, key)'),('make_topup_handler','topup_error(amount, key)')]:
        yield entry+'_bypass',user,change(gateway,entry,lambda s:once(s,'err = await '+call,'err = await '+call+' if key == "unknown" else None'))
