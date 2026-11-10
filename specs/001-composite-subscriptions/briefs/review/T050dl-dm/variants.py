"""Scratch-only alias-aware isolation, preserving independent legacy processing."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py','database.py']
EXCLUSION='''
def _review_exclusion(db):
    with db._get_conn() as conn:
        invoices = conn.execute("SELECT * FROM extra_gateway_invoices").fetchall()
    ids = [int(row["id"]) for row in invoices if _review_blocked_invoice(db, row)]
    return " AND id NOT IN (" + ",".join(map(str, ids)) + ")" if ids else ""

'''
GUARD='''                if _review_blocked_invoice(db, invoice):
                    try:
                        await bot.send_message(invoice["user_id"], "composite_unsupported")
                    except Exception:
                        pass
                    continue
'''
def variants(payment,db):
    p=m.HELPER+payment;d=m.HELPER+EXCLUSION+db
    p=change(p,'poll_loop',lambda s:once(s,'                result, text = await process_invoice(db, bot, invoice)',GUARD+'                result, text = await process_invoice(db, bot, invoice)'))
    for method,anchor in [('expire_stale_extra_invoices','AND created_at < ?'),('purge_old_extra_invoices','AND COALESCE(updated_at, created_at) < ?')]:
        d=change(d,method,lambda s:once(once(s,'        with self._get_conn() as conn:', '        exclusion = _review_exclusion(self)\n        with self._get_conn() as conn:'),anchor+'",',anchor+'" + exclusion,'))
    yield 'reference',p,d
    edits=[('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock_domain','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]
    for index,source in enumerate([p,d]):
        for name,b,a in edits:
            v=change(source,'_review_blocked_invoice',lambda s:once(s,b,a))
            yield ('poll_' if index==0 else 'sql_')+name,v if index==0 else p,d if index==0 else v
    yield 'sql_kind',p,change(d,'_review_blocked_invoice',lambda s:once(s,'invoice["kind"] != "order"','False'))
    for method in ['expire_stale_extra_invoices','purge_old_extra_invoices']:
        yield method+'_omit',p,change(d,method,lambda s:once(s,' + exclusion',''))
    for name,b,a in [('omit',GUARD,''),('reason','composite_unsupported','unsupported'),('recipient','bot.send_message(invoice["user_id"], "composite_unsupported")','bot.send_message(999, "composite_unsupported")'),('send_raises','                    except Exception:\n                        pass\n                    continue','                    except Exception:\n                        raise\n                    continue'),('stop_iteration','                    continue\n                result, text','                    break\n                result, text'),('cadence','now - seen < 12','now - seen <= 12')]:
        yield 'poll_'+name,change(p,'poll_loop',lambda s:once(s,b,a)),d
    for method in ['expire_stale_extra_invoices','purge_old_extra_invoices']:
        yield method+'_drop',p,change(d,method,lambda s:s.splitlines(keepends=True)[0]+'        return\n')
