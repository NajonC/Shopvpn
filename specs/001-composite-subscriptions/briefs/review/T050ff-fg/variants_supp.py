"""Minimal selected ordinary admin guard; real inline STOCK effects remain intact."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['handlers_admin.py','stock_alerts.py','database.py']
GUARD='''        product_guard = await asyncio.to_thread(db.get_product, order["product_id"])
        def marked(row):
            return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
        if marked(order) or marked(product_guard):
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
def variants(admin,stock,db):
    ref=change(admin,'cb_order_approve',lambda s:once(s,'        if not (await asyncio.to_thread(db.claim_order, order_id)):',GUARD+'        if not (await asyncio.to_thread(db.claim_order, order_id)):'))
    yield 'reference',ref,stock,db
    # Late guard still gives a generic reason but has already durably claimed the order.
    late=change(ref,'cb_order_approve',lambda s:once(once(s,GUARD,''),'        # ===== سفارش تمدید سرویس از حساب کاربری =====',GUARD+'        # ===== سفارش تمدید سرویس از حساب کاربری ====='))
    yield 'late_after_claim',late,stock,db
    edited=change(ref,'cb_order_approve',lambda s:a.join(s.rsplit(b,1))) if False else ref
    b='(await asyncio.to_thread(db.log_admin_action, '
    # Suppress only the STOCK branch log while preserving a valid async call signature.
    def omitlog(s):
        start=s.rindex(b);end=s.index('        await check_and_notify_low_stock',start)
        return s[:start]+'pass\n'+s[end:]
    yield 'omit_stock_log',change(ref,'cb_order_approve',omitlog),stock,db
    yield 'wrong_admin_recipient',ref,change(stock,'check_and_notify_low_stock',lambda s:once(s,'await send_fn(admin_id, text)','await send_fn(1001, text)')),db
