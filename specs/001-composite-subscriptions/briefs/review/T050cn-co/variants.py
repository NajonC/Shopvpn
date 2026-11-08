"""Topup compatibility reference is unchanged production, independently mutated."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050cd-ce/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
GATEWAY='topup-entry'
def variants(user,payment,database,fulfillment):
    yield 'reference',user,payment,database,fulfillment
    def u(name,func,b,a):return name,change(user,func,lambda s:once(s,b,a)),payment,database,fulfillment
    for name,b,a in [('available','if not egp.is_available(db, key, is_main_bot):','if False:'),('policy','if err:','if False:'),('amount','key, "wallet_topup", topup_id, amount, label','key, "wallet_topup", topup_id, amount+1, label'),('actor','tenant_id, call.from_user.id, key','tenant_id, call.from_user.id+1, key'),('reference_id','key, "wallet_topup", topup_id','key, "wallet_topup", topup_id+999'),('kind','key, "wallet_topup", topup_id','key, "order", topup_id'),('rollback','await asyncio.to_thread(db.reject_topup, topup_id)','pass'),('error_reply','f"⚠️ {e}"','"wrong"'),('label','f"شارژ کیف پول #{topup_id}"','"wrong"'),('new_amount','db.create_topup, call.from_user.id, amount','db.create_topup, call.from_user.id, amount+1'),('new_owner','db.create_topup, call.from_user.id, amount','db.create_topup, call.from_user.id+1, amount'),('overstrict','if not amount:','if True:'),('zero_boundary','if not amount:','if amount is None:')]:yield u(name,'make_topup_handler',b,a)
    # Rejecting a topup because of an unrelated composite order in FSM is wrong.
    anchor='            if not amount:'
    yield u('global_composite_ban','make_topup_handler',anchor,'            if data.get("order_id"):\n                await call.answer("composite_unsupported", show_alert=True)\n                return\n'+anchor)
    for name,b,a in [('stars_payload','egp.stars_payload(result["invoice_id"])','"xg:9999"'),('stars_amount','amount=stars','amount=stars+1'),('stars_currency','currency="XTR"','currency="USD"'),('stars_error','f"⚠️ ساخت فاکتور استارز ناموفق بود: {e.message}"','"wrong"'),('check_link',"result['invoice_id']","result['invoice_id']+999"),('pay_link','url=result["payment_url"]','url="https://wrong.example.invalid"'),('cube_exact','result["meta"].get("pay_amount_toman") or result["payable_amount"]','result["payable_amount"]'),('tetra_link','if gateway == "tetra98" and bot_url:','if False:'),('done_kind',"_DONE_TEXT.get(kind, _DONE_TEXT['order'])","_DONE_TEXT['order']")]:yield u(name,'present_invoice',b,a)
    for name,b,a in [('persist_amount','tg_id, amount_toman, payable','tg_id, amount_toman+1, payable'),('cube_fee','payable = cubepay_payable(db, amount_toman)','payable = amount_toman'),('star_round','math.ceil(int(amount_toman) / rate)','math.ceil(int(amount_toman) / rate)+1')]:
        yield name,user,change(payment,'stars_for_amount' if name=='star_round' else 'create_invoice_for',lambda s:once(s,b,a)),database,fulfillment
    yield 'reject_wrong_row',user,payment,change(database,'reject_topup',lambda s:once(s,'(datetime.utcnow().isoformat(), topup_id)','(datetime.utcnow().isoformat(), topup_id+999)')),fulfillment
    anchor='        with self._get_conn() as conn:'
    extra='''        with self._get_conn() as conn:
            existing = conn.execute("SELECT id FROM wallet_topups WHERE user_id=? AND amount=? AND status='pending' ORDER BY id DESC LIMIT 1", (user_tg_id, amount)).fetchone()
            if existing:
                return existing["id"]
'''
    yield 'repeated_request_reuse',user,payment,change(database,'create_topup',lambda s:once(s,anchor,extra+anchor)),fulfillment
