"""Bounded executable poll/SQL reference; independent rule mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050ct-cu/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py','database.py']
GUARD=m.GUARD.replace('return "error:composite_unsupported"','await bot.send_message(invoice["user_id"], "composite_unsupported")\n            continue')
GUARD='\n'.join('            '+line if line else line for line in GUARD.splitlines())+'\n'
FILTER=" AND NOT EXISTS (SELECT 1 FROM orders o LEFT JOIN products p ON p.id=o.product_id WHERE extra_gateway_invoices.kind='order' AND o.id=extra_gateway_invoices.ref_id AND (o.service_kind='composite' OR p.service_kind='composite'))"
def variants(payment,db):
    # Inject the caller guard after cadence tracking and before permissive process seam.
    anchor='                result, text = await process_invoice(db, bot, invoice)'
    payment=change(payment,'poll_loop',lambda s:once(s,anchor,GUARD+anchor))
    for method,anchor in [('expire_stale_extra_invoices','AND created_at < ?'),('purge_old_extra_invoices','AND COALESCE(updated_at, created_at) < ?')]:
        db=change(db,method,lambda s:once(s,anchor,anchor+FILTER))
    yield 'reference',payment,db
    for name,b,a in [('order_alias','if blocked_order or blocked_product:','if blocked_product:'),('product_alias','if blocked_order or blocked_product:','if blocked_order:'),('ref_domain','db.get_order, int(invoice["ref_id"])','db.get_order, int(invoice["id"])'),('product_identity','db.get_product, order["product_id"]','db.get_product, order["product_id"]+999'),('reason','composite_unsupported','unsupported'),('overstrict','if blocked_order or blocked_product:','if order is not None:'),('remove_guard',GUARD,''),('recipient','bot.send_message(invoice["user_id"], "composite_unsupported")','bot.send_message(999, "composite_unsupported")'),('cadence','now - seen < 12','now - seen <= 12'),('batch_limit','db.list_open_extra_invoices, 100','db.list_open_extra_invoices, 50'),('housekeeping_frequency','tick % 8 == 1','tick % 8 == 0'),('purge_age','db.purge_old_extra_invoices, 7','db.purge_old_extra_invoices, 1'),('interval','asyncio.sleep(interval)','asyncio.sleep(15)'),('legacy_recipient','bot.send_message(invoice["user_id"], text)','bot.send_message(999, text)'),('unpaid_notification','if result == "verified_now" and text:','if text:'),('drop_send','await bot.send_message(invoice["user_id"], text)','pass')]:
        yield name,change(payment,'poll_loop',lambda s:once(s,b,a)),db
    for method in ['expire_stale_extra_invoices','purge_old_extra_invoices']:
        for name,b,a in [('remove_filter',FILTER,''),('order_alias',"o.service_kind='composite' OR p.service_kind='composite'","p.service_kind='composite'"),('product_alias',"o.service_kind='composite' OR p.service_kind='composite'","o.service_kind='composite'"),('overstrict',"(o.service_kind='composite' OR p.service_kind='composite')","1=1"),('reference_domain','extra_gateway_invoices.ref_id','extra_gateway_invoices.id'),('kind_domain',"extra_gateway_invoices.kind='order'","1=1")]:
            yield method+'_'+name,payment,change(db,method,lambda s:once(s,b,a))
