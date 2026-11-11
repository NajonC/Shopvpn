"""Scratch-only bounded open-selection guard and independently applied mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['database.py','extra_gateway_payment.py']
SELECT='''    def list_open_extra_invoices(self, limit: int = 100):
        limit = int(limit)
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM extra_gateway_invoices WHERE status IN ('new','pending') AND gateway != 'tgstars' ORDER BY id").fetchall()
        allowed = []
        for row in rows:
            if _review_blocked_invoice(self, row):
                import logging
                logging.getLogger(__name__).warning("composite_unsupported")
                continue
            allowed.append(row)
        return allowed if limit < 0 else allowed[:limit]

'''
def variants(db,payment):
    ref=change(p.HELPER+db,'list_open_extra_invoices',lambda s:SELECT)
    yield 'reference',ref,payment
    for fn,name,b,a in [
      ('_review_blocked_invoice','order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),
      ('_review_blocked_invoice','target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),
      ('_review_blocked_invoice','product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),
      ('_review_blocked_invoice','ref_identity','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),
      ('_review_blocked_invoice','custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),
      ('_review_blocked_invoice','stock_domain','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),
      ('_review_blocked_invoice','kind','invoice["kind"] != "order"','False'),
      ('_review_blocked_invoice','overstrict','return marked(order) or marked(target) or marked(product)','return True'),
      ('list_open_extra_invoices','omit_guard','if _review_blocked_invoice(self, row):','if False:'),
      ('list_open_extra_invoices','reason','composite_unsupported','unsupported'),
      ('list_open_extra_invoices','no_reason','logging.getLogger(__name__).warning("composite_unsupported")','pass'),
      ('list_open_extra_invoices','limit_first','for row in rows:','for row in (rows if limit < 0 else rows[:limit]):'),
      ('list_open_extra_invoices','stop_batch','                continue','                break'),
    ]:yield name,change(ref,fn,lambda s:once(s,b,a)),payment
    for name,b,a in [
      ('poll_skip_next','for invoice in await asyncio.to_thread(db.list_open_extra_invoices, 100):','for invoice in (await asyncio.to_thread(db.list_open_extra_invoices, 100))[:1]:'),
      ('poll_boundary','now - seen < 12','now - seen <= 12'),
      ('poll_cache_late','                last_checked[invoice["id"]] = now\n                result, text = await process_invoice(db, bot, invoice)','                result, text = await process_invoice(db, bot, invoice)\n                last_checked[invoice["id"]] = now'),
      ('poll_send_aborts','                    except Exception:\n                        pass','                    except Exception:\n                        raise'),
    ]:yield name,ref,change(payment,'poll_loop',lambda s:once(s,b,a))
