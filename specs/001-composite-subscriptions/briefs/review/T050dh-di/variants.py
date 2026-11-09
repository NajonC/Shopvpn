"""Production is compatibility reference; independently break admin view/domain rules."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_admin.py','database.py']
def variants(admin,db):
    yield 'reference',admin,db
    for status,label in [('new','🟡 جدید'),('pending','🟠 در انتظار'),('completed','🟢 تکمیل‌شده'),('expired','🔴 منقضی‌شده'),('cancelled','🔴 لغوشده')]:
        yield 'status_'+status,once(admin,label,'wrong'),db
    for name,b,a in [('amount',"invoice['amount_toman']:,","invoice['payable_amount']:,"),('reference',"invoice['ref_id']","invoice['id']"),('owner',"invoice['user_id']","invoice['id']"),('identity',"فاکتور {meta['title']} #{invoice['id']}","فاکتور {meta['title']} #{invoice['ref_id']}"),('payable_equal','int(invoice["payable_amount"]) != int(invoice["amount_toman"])','True'),('payable_zero','invoice["payable_amount"] and','True and'),('remote','if invoice["remote_id"]:','if True:'),('url','if invoice["payment_url"] and active:','if active:'),('inactive','active = invoice["status"] in ("new", "pending")','active = True'),('no_active','active = invoice["status"] in ("new", "pending")','active = False'),('stars_check','if invoice["gateway"] != "tgstars":','if True:'),('stars_amount','if invoice["gateway"] == "tgstars":','if False:'),('back',"adm_xgw_payments:{invoice['gateway']}","adm_xgw_payments:wrong"),('check',"check_xgw_invoice:{invoice['id']}","check_xgw_invoice:{invoice['ref_id']}"),('cancel',"cancel_xgw_invoice:{invoice['id']}","cancel_xgw_invoice:{invoice['ref_id']}"),('unknown_gateway','{"icon": "💠", "title": invoice["gateway"]}','{"icon": "X", "title": "wrong"}'),('unknown_status',"invoice['status'] or '---'","'wrong'"),('created',"invoice['created_at'] or '---'","'wrong'"),('drop_view','        await replace_admin_view(call, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))','        pass')]:
        yield 'view_'+name,change(admin,'cb_view_xgw_invoice',lambda s:once(s,b,a)),db
    for entry in ['cb_view_xgw_invoice','cb_cancel_xgw_invoice']:
        for kind in ['wallet_topup','reseller_request']:
            helper=m.HELPER.replace('invoice["kind"] != "order"',f'invoice["kind"] != "{kind}"')
            anchor='        meta = registry.GATEWAYS.get(invoice["gateway"]' if entry=='cb_view_xgw_invoice' else '        await asyncio.to_thread(db.cancel_and_delete_extra_invoice, invoice_id)'
            yield entry+'_'+kind+'_wrong_order_domain',change(helper+admin,entry,lambda s:once(s,anchor,m.CALL_GUARD+anchor)),db
        def swallow(s):
            lines=s.splitlines(keepends=True)
            return lines[0]+'        try:\n'+''.join('    '+line for line in lines[1:])+'        except RuntimeError:\n            return\n'
        yield entry+'_swallow_failure',change(admin,entry,swallow),db
