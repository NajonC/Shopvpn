"""Actual notifier registry/fanout variants, bounded deliver reference only."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050et-eu/variants.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
once,change=p.once,p.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py']
def variants(extra,shared):
    guard='    if _review_blocked_invoice(db, invoice):\n        return "composite_unsupported"\n'
    ref=change(p.p.base.HELPER+extra,'deliver',lambda s:once(s,'    kind = invoice["kind"]',guard+'    kind = invoice["kind"]'))
    yield 'reference',ref,shared
    edits=[
      ('_review_blocked_invoice','order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),
      ('_review_blocked_invoice','product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),
      ('_review_blocked_invoice','ref_domain','db.get_order(invoice["ref_id"])','db.get_order(invoice["id"])'),
      ('_review_blocked_invoice','overstrict','return marked(order) or marked(target) or marked(product)','return True'),
      ('deliver','omit_guard',guard,''),
      ('deliver','no_reason','composite_unsupported','unsupported'),
      ('register_order_notifier','omit_registration','_order_notifiers[id(db)] = fn','pass'),
      ('register_order_notifier','wrong_key','_order_notifiers[id(db)] = fn','_order_notifiers[0] = fn'),
      ('register_order_notifier','no_replace','_order_notifiers[id(db)] = fn','_order_notifiers.setdefault(id(db), fn)'),
      ('deliver','omit_explicit','notify_admins_fn or _order_notifiers.get(id(db))','_order_notifiers.get(id(db))'),
      ('deliver','omit_registry','notify_admins_fn or _order_notifiers.get(id(db))','notify_admins_fn'),
      ('deliver','precedence','notify_admins_fn or _order_notifiers.get(id(db))','_order_notifiers.get(id(db)) or notify_admins_fn'),
      ('deliver','foreign_registry','_order_notifiers.get(id(db))','next(iter(_order_notifiers.values()),None)'),
      ('deliver','drop_notifier','notify_admins_fn=notifier','notify_admins_fn=None'),
      ('_notify_admins','recipient','bot.send_message(admin_id, text)','bot.send_message(admin_id+999, text)'),
      ('_notify_admins','text','bot.send_message(admin_id, text)','bot.send_message(admin_id, "wrong")'),
      ('_notify_admins','no_send','await bot.send_message(admin_id, text)','pass'),
      ('_notify_admins','only_first','await asyncio.to_thread(db.list_admins)','(await asyncio.to_thread(db.list_admins))[:1]'),
      ('_notify_admins','send_propagates','except Exception:\n            pass','except Exception:\n            raise'),
      ('_notify_admins','stop_after_failure','except Exception:\n            pass','except Exception:\n            return'),
      ('deliver','warning_id','سفارش #{ref_id}','سفارش #{invoice["id"]}'),
      ('deliver','gateway_title','title = registry.GATEWAYS[invoice["gateway"]]["title"]','title = "wrong"'),
      ('deliver','warning_user',"(کاربر {invoice['user_id']}) دریافت شد","(کاربر 999) دریافت شد"),
      ('deliver','warning_status',"«{order['status']}»","«wrong»"),
      ('deliver','warning_detail','ناموفق بود:\\n{text}','ناموفق بود:'),
      ('deliver','warning_prefix','if text.startswith(("⛔️", "⚠️")):','if False:'),
    ]
    for fn,name,b,a in edits:
        if name=='warning_id':
            def edit(s):
                assert s.count(b)==3;return s.replace(b,a)
        else:
            def edit(s,b=b,a=a):return once(s,b,a)
        yield name,change(ref,fn,edit),shared
    block='''    if notify_admins_fn:
        try:
            await notify_admins_fn(bot, order_id)
        except Exception:
            pass'''
    for name,b,a in [('notifier_id','notify_admins_fn(bot, order_id)','notify_admins_fn(bot, 99999)'),('notifier_propagates','except Exception:\n            pass','except Exception:\n            raise'),('notifier_omit','await notify_admins_fn(bot, order_id)','pass')]:
        yield name,ref,change(shared,'finalize_paid_order',lambda s:once(s,block,once(block,b,a)))
    early='    reward_info = db.reward_referrer_if_first_purchase(order["user_id"], order["base_price"])'
    yield 'notifier_before_reward',ref,change(shared,'finalize_paid_order',lambda s:once(s,early,block+'\n'+early).replace(block+'\n    return', '    return'))
