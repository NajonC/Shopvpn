"""Scratch-only guards and independent status/identity/order mutations."""
import ast


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])

FUNC='cb_check_card_auto'
GUARD='''        order = (await asyncio.to_thread(db.get_order, invoice["ref_id"])) if invoice["kind"] == "order" else None
        product = (await asyncio.to_thread(db.get_custom_config_product, order["custom_product_id"])) if order is not None and order["custom_product_id"] else None
        blocked_order = order is not None and "service_kind" in order.keys() and order["service_kind"] == "composite"
        blocked_product = product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"
        if blocked_order or blocked_product:
            await call.answer("composite_unsupported", show_alert=True)
            return
'''
MAINTAIN='        await asyncio.to_thread(db.expire_stale_card_to_card_invoices)'


def variants(production):
    reference=change(production,FUNC,lambda s:once(s,MAINTAIN,GUARD+MAINTAIN))
    yield 'reference',reference
    def mutate(name,b,a):return name,change(reference,FUNC,lambda s:once(s,b,a))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('omit_order_guard','if blocked_order or blocked_product:','if blocked_product:')
    yield mutate('omit_product_guard','if blocked_order or blocked_product:','if blocked_order:')
    yield mutate('both_required','if blocked_order or blocked_product:','if blocked_order and blocked_product:')
    yield mutate('wrong_link','db.get_order, invoice["ref_id"]','db.get_order, invoice["id"]')
    yield mutate('no_reason','"composite_unsupported"','"unsupported"')
    yield mutate('early_expiry',GUARD+MAINTAIN,MAINTAIN+'\n'+GUARD)
    yield mutate('no_ownership','if not invoice or invoice["user_id"] != call.from_user.id:','if not invoice:')
    yield mutate('no_expiry',MAINTAIN,'        pass')
    yield mutate('no_refresh','        invoice = (await asyncio.to_thread(db.get_card_to_card_invoice, invoice_id))\n        if invoice["status"]','        if invoice["status"]')
    yield mutate('wrong_completed','if invoice["status"] == "completed":','if invoice["status"] == "wrong":')
    yield mutate('wrong_review','elif invoice["status"] == "manual_review":','elif invoice["status"] == "wrong":')
    yield mutate('legacy_overstrict','if blocked_order or blocked_product:','if order is not None:')
    yield mutate('sibling_overstrict','if blocked_order or blocked_product:','if blocked_order or blocked_product or any("service_kind" in p.keys() and p["service_kind"]=="composite" for p in db.get_custom_config_products()):')
