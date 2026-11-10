"""Independent source guards at three registered adapters; scratch only."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_user.py']
def variants(user):
    p=user;guards={}
    for entry,method,anchor,setup,reply in [
        ('pre','stars_pre_checkout','        ok = bool(', '', 'await query.answer(ok=False, error_message="composite_unsupported")'),
        ('success','stars_successful_payment','        notifier = egp._order_notifiers.get(id(db))', '        invoice = await asyncio.to_thread(db.get_extra_invoice, invoice_id)\n', 'await message.answer("composite_unsupported")'),
        ('check','cb_check_extra_gateway','        await call.answer("در حال بررسی وضعیت پرداخت...")', '', 'await call.answer("composite_unsupported", show_alert=True)')]:
        p=m.HELPER.replace('_review_blocked_invoice','_review_'+entry)+p
        guard=setup+f'        if _review_{entry}(db, invoice):\n            {reply}\n            return\n'
        p=change(p,method,lambda s:once(s,anchor,guard+anchor));guards[entry]=(method,guard)
    yield 'reference',p
    for entry,(method,guard) in guards.items():
        for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
            yield entry+'_'+name,change(p,'_review_'+entry,lambda s:once(s,b,a))
        yield entry+'_omit',change(p,method,lambda s:once(s,guard,''))
        yield entry+'_reason',change(p,method,lambda s:once(s,'composite_unsupported','unsupported'))
    for entry,method,b,a in [('pre','stars_pre_checkout','await egp.ref_still_payable(db, invoice)','True'),('success','stars_successful_payment','payment.total_amount, payment.currency','payment.total_amount+1, payment.currency'),('success','stars_successful_payment','payment.telegram_payment_charge_id, notifier','payment.telegram_payment_charge_id, None'),('check','cb_check_extra_gateway','egp.process_invoice(db, bot, invoice,','egp.process_invoice(db, bot, {**dict(invoice), "ref_id":invoice["id"]},'),('check','cb_check_extra_gateway','await call.message.answer(text)','await call.message.answer("wrong")')]:yield entry+'_args_'+str(len(b)),change(p,method,lambda s:once(s,b,a))
