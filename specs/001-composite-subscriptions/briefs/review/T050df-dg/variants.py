"""Review-only global preflight; no housekeeping writes when composite is present."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py','database.py']
PREFLIGHT='''        with db._get_conn() as conn:
            candidates = conn.execute("SELECT * FROM extra_gateway_invoices ORDER BY id DESC").fetchall()
        blocked = any(_review_blocked_invoice(db, invoice) for invoice in candidates)
        if blocked:
            await call.answer("composite_unsupported", show_alert=True)
            invoices = [invoice for invoice in candidates if invoice["gateway"] == key][:50]
            invoices = [invoice for invoice in invoices if not _review_blocked_invoice(db, invoice)]
        else:
            invoices = await _load_invoices(key)
'''
def variants(admin,db):
    anchor='        invoices = await _load_invoices(key)\n'
    ref=change(m.HELPER+admin,'_show_invoices',lambda s:once(s,anchor,PREFLIGHT))
    yield 'reference',ref,db
    for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref_domain','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom_catalog','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock_catalog','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('kind_domain','invoice["kind"] != "order"','False'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        yield name,change(ref,'_review_blocked_invoice',lambda s:once(s,b,a)),db
    for name,b,a in [('omit',PREFLIGHT,anchor),('first50','ORDER BY id DESC"','ORDER BY id DESC LIMIT 50"'),('first200','ORDER BY id DESC"','ORDER BY id DESC LIMIT 200"'),('crossgateway','blocked = any(_review_blocked_invoice(db, invoice) for invoice in candidates)','blocked = any(_review_blocked_invoice(db, invoice) for invoice in candidates if invoice["gateway"] == key)'),('early','        with db._get_conn()','        await _load_invoices(key)\n        with db._get_conn()'),('filter','if not _review_blocked_invoice(db, invoice)','if True'),('drop_legacy','if not _review_blocked_invoice(db, invoice)','if False'),('reason','composite_unsupported','unsupported'),('alert','show_alert=True','show_alert=False'),('empty','if not invoices:','if False:')]:
        yield name,change(ref,'_show_invoices',lambda s:once(s,b,a)),db
