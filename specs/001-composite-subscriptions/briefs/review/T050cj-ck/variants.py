"""Fresh adapter-boundary and downstream contract mutations for batch15."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
once,change=m.once,m.change
GATEWAY='adapters'
def variants(user,payment,database,fulfillment):
    lookup='''        order = await asyncio.to_thread(db.get_order, invoice["ref_id"]) if invoice and invoice["kind"] == "order" else None
        product = await asyncio.to_thread(db.get_product, order["product_id"]) if order is not None and order["product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
'''
    pg=lookup+'''        if blocked_order or blocked_product:
            await query.answer(ok=False, error_message="composite_unsupported")
            return
'''
    sg='        invoice = await asyncio.to_thread(db.get_extra_invoice, invoice_id)\n'+lookup+'''        if blocked_order or blocked_product:
            await message.answer("composite_unsupported")
            return
'''
    ack='        ok = bool('
    notif='        notifier = egp._order_notifiers.get(id(db))'
    ref=change(user,'stars_pre_checkout',lambda s:once(s,ack,pg+ack))
    ref=change(ref,'stars_successful_payment',lambda s:once(s,notif,sg+notif))
    yield 'reference',ref,payment,database,fulfillment
    def um(name,func,b,a):return name,change(ref,func,lambda s:once(s,b,a)),payment,database,fulfillment
    for func in ['stars_pre_checkout','stars_successful_payment']:
        tag='pre' if func=='stars_pre_checkout' else 'success'
        yield um(tag+'_order_alias',func,'if blocked_order or blocked_product:','if blocked_product:')
        yield um(tag+'_product_alias',func,'if blocked_order or blocked_product:','if blocked_order:')
        yield um(tag+'_order_link',func,'db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]')
        yield um(tag+'_product_link',func,'db.get_product, order["product_id"]','db.get_product, order["product_id"]+999')
        yield um(tag+'_reason',func,'composite_unsupported','unsupported')
        yield um(tag+'_overstrict',func,'if blocked_order or blocked_product:','if order is not None:')
    yield um('pre_gateway','stars_pre_checkout','invoice["gateway"] == "tgstars"','True')
    yield um('pre_status','stars_pre_checkout','invoice["status"] in ("new", "pending")','True')
    yield um('pre_owner','stars_pre_checkout','int(invoice["user_id"]) == query.from_user.id','True')
    yield um('pre_currency','stars_pre_checkout','query.currency == "XTR"','True')
    yield um('pre_amount','stars_pre_checkout','int(query.total_amount) == int(invoice["payable_amount"] or 0)','True')
    yield um('pre_ref_payable','stars_pre_checkout','await egp.ref_still_payable(db, invoice)','True')
    yield um('success_early_effects','stars_successful_payment',sg+notif,'        await egp.process_stars_payment(db, bot, invoice_id, message.from_user.id, payment.total_amount, payment.currency, payment.telegram_payment_charge_id)\n'+sg+notif)
    yield um('success_charge','stars_successful_payment','payment.telegram_payment_charge_id, notifier','"wrong", notifier')
    yield um('success_amount','stars_successful_payment','payment.total_amount, payment.currency','payment.total_amount+1, payment.currency')
    yield um('success_invoice','stars_successful_payment','db, bot, invoice_id, message.from_user.id','db, bot, invoice_id+1, message.from_user.id')
    yield um('success_reply','stars_successful_payment','await message.answer(text)','await message.answer("wrong")')
    def pm(name,func,b,a):return name,ref,change(payment,func,lambda s:once(s,b,a)),database,fulfillment
    yield pm('success_owner','process_stars_payment','int(invoice["user_id"]) != int(user_id)','False')
    yield pm('success_gateway','process_stars_payment','invoice["gateway"] != "tgstars"','False')
    yield pm('success_amount_validation','process_stars_payment','int(total_amount) != int(invoice["payable_amount"] or 0)','False')
    yield pm('success_currency','process_stars_payment','currency != "XTR"','False')
    yield pm('metadata','process_stars_payment','await asyncio.to_thread(db.merge_extra_invoice_meta, invoice_id, {"charge_id": charge_id})','pass')
    yield pm('claim_loss','process_stars_payment','if not await asyncio.to_thread(db.claim_extra_invoice, invoice_id):','if await asyncio.to_thread(db.claim_extra_invoice, invoice_id) and False:')
    yield pm('fulfill','process_stars_payment','return await deliver(db, bot, invoice, notify_admins_fn)','return "wrong"')
    yield pm('exception_release','process_stars_payment','logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)','await asyncio.to_thread(db.release_extra_invoice, invoice_id)\n        logger.exception("خطای غیرمنتظره در تحویل فاکتور استارز %s", invoice_id)')
    yield 'sql_claim',ref,payment,change(database,'claim_extra_invoice',lambda s:once(s,"WHERE id=? AND status IN ('new','pending')","WHERE id=?")),fulfillment
    for name,b,a in [('quantity','quantity = order["quantity"] or 1','quantity = 1'),('price','links, final_price=order["final_price"]','links, final_price=order["final_price"]+1'),('reward','order["base_price"]','order["base_price"]+100')]:
        yield name,ref,payment,database,change(fulfillment,'finalize_paid_order',lambda s:once(s,b,a))
