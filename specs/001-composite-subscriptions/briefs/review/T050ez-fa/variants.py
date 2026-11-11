"""Independent direct helper reference; mutations only in scratch."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['stock_alerts.py','database.py']
GUARD='''    product = db.get_product(product_id)
    if product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite":
        logger.warning("Composite product refused by legacy stock alert")
        return
'''
def variants(stock,db):
    ref=change(stock,'check_and_notify_low_stock',lambda s:once(s,'    try:\n        stock =',GUARD+'    try:\n        stock ='))
    yield 'reference',ref,db
    for name,b,a in [
      ('omit',GUARD,''),
      ('reason','Composite product refused by legacy stock alert','unsupported'),
      ('leak','logger.warning("Composite product refused by legacy stock alert")','logger.warning("Composite stock refused %s", product["name"])'),
      ('overstrict','product["service_kind"] == "composite"','True'),
      ('absent','"service_kind" in product.keys() and product["service_kind"] == "composite"','("service_kind" not in product.keys() or product["service_kind"] == "composite")'),
      ('count','count_available_configs(product_id)','count_available_configs(product_id+999)'),
      ('fallback','or 3','or 1'),
      ('negative','int(db.get_setting("low_stock_threshold", "3") or 3)','max(0,int(db.get_setting("low_stock_threshold", "3") or 3))'),
      ('swallow','except Exception:\n        return','except Exception:\n        raise'),
      ('skip_state','if not should_alert:','if True:'),
      ('name','product["name"] if product else "نامشخص"','"wrong"'),
      ('missing_name','"نامشخص"','"wrong"'),
      ('recipient','send_fn(admin_id, text)','send_fn(admin_id+999, text)'),
      ('text','آستانه‌ی هشدار: {threshold}','آستانه‌ی هشدار: 999'),
      ('first_only','for admin_id in db.list_admins():','for admin_id in db.list_admins()[:1]:'),
      ('send_raise','logger.warning("ارسال','raise RuntimeError("synthetic direct alert fault"); logger.warning("ارسال'),
      ('stop_failure','logger.warning("ارسال','return; logger.warning("ارسال'),
    ]:yield name,change(ref,'check_and_notify_low_stock',lambda s:once(s,b,a)),db
    yield 'late_guard',change(ref,'check_and_notify_low_stock',lambda s:once(once(s,GUARD,''),'    should_alert =',GUARD+'    should_alert =')),db
    for name,b,a in [
      ('equality','stock <= threshold','stock < threshold'),
      ('reset_equality','stock > threshold','stock >= threshold'),
      ('repeat','stock <= threshold and not already_sent','stock <= threshold'),
      ('latch','SET low_stock_alert_sent=1','SET low_stock_alert_sent=0'),
      ('reset','SET low_stock_alert_sent=0','SET low_stock_alert_sent=1'),
      ('wrong_product','WHERE id=?','WHERE id=?+999'),
      ('missing_row','already_sent = bool(row["low_stock_alert_sent"]) if row else False','already_sent = bool(row["low_stock_alert_sent"]) if row else True'),
    ]:
        def edit(s,b=b,a=a):
            assert b in s
            return s.replace(b,a)
        yield name,ref,change(db,'check_low_stock_alert_state',edit)
