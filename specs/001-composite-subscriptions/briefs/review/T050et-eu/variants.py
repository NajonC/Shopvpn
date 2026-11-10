"""Reference guards and independent actual STOCK alert/latch mutants."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050ep-eq/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py','database.py','stock_alerts.py']
def variants(*texts):
    original=dict(zip(SOURCES,texts));ref=dict(original)
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    ref[SOURCES[0]]=change(p.base.HELPER+ref[SOURCES[0]],'deliver',lambda s:once(s,'    kind = invoice["kind"]',guard+'    kind = invoice["kind"]'))
    yield 'reference',*(ref[n] for n in SOURCES)
    edits=[
      (SOURCES[0],'_review_blocked_invoice','order_guard','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),
      (SOURCES[0],'_review_blocked_invoice','product_guard','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),
      (SOURCES[0],'_review_blocked_invoice','ref_domain','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),
      (SOURCES[0],'_review_blocked_invoice','overstrict','return marked(order) or marked(target) or marked(product)','return True'),
      (SOURCES[0],'deliver','omit',guard,''),
      ('database.py','check_low_stock_alert_state','boundary','stock <= threshold','stock < threshold'),
      ('database.py','check_low_stock_alert_state','dedup','stock <= threshold and not already_sent','stock <= threshold'),
      ('database.py','check_low_stock_alert_state','save_latch','SET low_stock_alert_sent=1','SET low_stock_alert_sent=0'),
      ('database.py','check_low_stock_alert_state','reset','stock > threshold and already_sent','False'),
      ('database.py','check_low_stock_alert_state','reset_boundary','stock > threshold and already_sent','stock >= threshold and already_sent'),
      ('database.py','check_low_stock_alert_state','wrong_product','SET low_stock_alert_sent=1 WHERE id=?", (product_id,))','SET low_stock_alert_sent=1 WHERE id=?", (product_id+999,))'),
      ('stock_alerts.py','check_and_notify_low_stock','count','count_available_configs(product_id)','count_available_configs(product_id+999)'),
      ('stock_alerts.py','check_and_notify_low_stock','fallback','or 3','or 1'),
      ('stock_alerts.py','check_and_notify_low_stock','threshold','int(db.get_setting("low_stock_threshold", "3") or 3)','1'),
      ('stock_alerts.py','check_and_notify_low_stock','no_alert','if not should_alert:','if True:'),
      ('stock_alerts.py','check_and_notify_low_stock','name','product["name"] if product else "نامشخص"','"wrong"'),
      ('stock_alerts.py','check_and_notify_low_stock','text','آستانه‌ی هشدار: {threshold}','آستانه‌ی هشدار: 999'),
      ('stock_alerts.py','check_and_notify_low_stock','recipient','send_fn(admin_id, text)','send_fn(admin_id+999, text)'),
      ('stock_alerts.py','check_and_notify_low_stock','omit_send','await send_fn(admin_id, text)','pass'),
      ('stock_alerts.py','check_and_notify_low_stock','isolation','logger.warning(', 'raise RuntimeError("synthetic alert fault"); logger.warning('),
      ('stock_alerts.py','check_and_notify_low_stock','return_after_failure','logger.warning(', 'return; logger.warning('),
      ('stock_alerts.py','check_and_notify_low_stock','preflight_swallow','except Exception:\n        return','except Exception:\n        raise'),
      ('abangateway_payment.py','finalize_paid_order','omit_alert','await check_and_notify_low_stock(bot.send_message, db, order["product_id"])','pass'),
    ]
    for file,fn,name,b,a in edits:
        mutated=dict(ref);mutated[file]=change(ref[file],fn,lambda s:once(s,b,a))
        yield name,*(mutated[n] for n in SOURCES)
