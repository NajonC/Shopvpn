"""Wallet reference is unchanged production: no service entitlement in this domain."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py','abangateway_payment.py','database.py']
def variants(payment,aban,db):
    yield 'reference',payment,aban,db
    for name,b,a in [('ref','finalize_paid_topup(db, ref_id)','finalize_paid_topup(db, invoice["id"])'),('domain','if kind == "wallet_topup":','if False:'),('overstrict','    if kind == "wallet_topup":','    if kind == "wallet_topup":\n        return "composite_unsupported"')]:
        yield name,change(payment,'deliver',lambda s:once(s,b,a)),aban,db
    for name,b,a in [('missing','⚠️ درخواست شارژ یافت نشد.','missing'),('repeat','✅ این درخواست شارژ قبلاً بررسی شده است.','repeat'),('amount',"{topup['amount']:,}","{topup['amount']+1:,}"),('skip_approval','if not db.approve_topup(topup_id):','if False:'),('lookup','db.get_topup(topup_id)','db.get_topup(topup_id+1)')]:
        yield name,payment,change(aban,'finalize_paid_topup',lambda s:once(s,b,a)),db
    for name,b,a in [('status',"AND status='pending'","AND status IN ('pending','approved')"),('processing',"AND status='pending'","AND status IN ('pending','processing')"),('beneficiary','topup["user_id"], topup["amount"]','9002, topup["amount"]'),('credit','topup["user_id"], topup["amount"]','topup["user_id"], topup["amount"]+1'),('omit_credit','        self.add_wallet_credit(topup["user_id"], topup["amount"])','        pass'),('credit_before_status','        with self._get_conn() as conn:','        self.add_wallet_credit(topup["user_id"], topup["amount"])\n        with self._get_conn() as conn:')]:
        yield name,payment,aban,change(db,'approve_topup',lambda s:once(s,b,a))
