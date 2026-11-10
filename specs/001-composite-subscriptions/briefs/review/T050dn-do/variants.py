"""Scratch-only alias guards; no implementation copied to production."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py']
CREATE='''    if _review_blocked_invoice(db, {"kind": kind, "ref_id": ref_id}):
        raise ExtraGatewayError("composite_unsupported")
'''
PAY='''    if _review_blocked_invoice(db, invoice):
        return False
'''
def variants(payment):
    p=m.HELPER+payment
    p=change(p,'create_invoice_for',lambda s:once(s,'    spec(gateway)',CREATE+'    spec(gateway)'))
    p=change(p,'ref_still_payable',lambda s:once(s,'    kind = invoice["kind"]',PAY+'    kind = invoice["kind"]'))
    yield 'reference',p
    for name,b,a in [('order','marked(order) or marked(target) or marked(product)','marked(target) or marked(product)'),('target','marked(order) or marked(target) or marked(product)','marked(order) or marked(product)'),('product','marked(order) or marked(target) or marked(product)','marked(order) or marked(target)'),('ref','db.get_order(invoice["ref_id"])','db.get_order(invoice.get("id", 99999))'),('custom_domain','if custom else db.get_product(product_id)','if False else db.get_product(product_id)'),('stock_domain','if custom else db.get_product(product_id)','if True else db.get_product(product_id)'),('overstrict','return marked(order) or marked(target) or marked(product)','return True')]:
        altered=change(p,'_review_blocked_invoice',lambda s:once(s,b,a))
        yield name,altered
        yield 'pay_domain_'+name,altered
    for method,guard in [('create_invoice_for',CREATE),('ref_still_payable',PAY)]:
        yield method+'_omit',change(p,method,lambda s:once(s,guard,''))
    yield 'create_reason',change(p,'create_invoice_for',lambda s:once(s,'composite_unsupported','unsupported'))
    yield 'create_late',change(p,'create_invoice_for',lambda s:once(once(s,CREATE,''),'    order_number = _order_number(kind, ref_id)',CREATE+'    order_number = _order_number(kind, ref_id)'))
    yield 'pay_blanket',change(p,'ref_still_payable',lambda s:once(s,'    kind = invoice["kind"]','    return False\n    kind = invoice["kind"]'))
    yield 'create_wrong_amount',change(p,'create_invoice_for',lambda s:once(s,'    amount_toman = int(amount_toman)','    amount_toman = int(amount_toman) + 1'))
    yield 'create_no_reuse',change(p,'create_invoice_for',lambda s:once(s,'    if existing:','    if False:'))
