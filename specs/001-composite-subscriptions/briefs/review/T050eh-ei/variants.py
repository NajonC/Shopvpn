"""Independent database admission reference; real SQL and tier grants unchanged."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050dd-de/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['database.py']
ENTRY='complete_reseller_request_gateway_payment'
ACTIVE='awaiting_payment'
GUARD='''            product = conn.execute("SELECT * FROM products WHERE id=?", (req["supply_product_id"],)).fetchone() if req is not None and req["supply_product_id"] else None
            def marked(row):
                return row is not None and "service_kind" in row.keys() and row["service_kind"] == "composite"
            if marked(req) or marked(product):
                raise ValueError("composite_unsupported")
'''
def variants(db):
    anchor='            if not req or req["status"] != "'+ACTIVE+'":'
    ref=change(db,ENTRY,lambda s:once(s,anchor,GUARD+anchor))
    yield 'reference',ref
    for name,b,a in [('request_alias','marked(req) or marked(product)','marked(product)'),('product_alias','marked(req) or marked(product)','marked(req)'),('overstrict','marked(req) or marked(product)','req is not None'),('omit_guard',GUARD,''),('reason','composite_unsupported','unsupported'),('wrong_product','conn.execute("SELECT * FROM products WHERE id=?", (req["supply_product_id"],)).fetchone()','conn.execute("SELECT * FROM products WHERE id=?", (req["supply_product_id"]+999,)).fetchone()'),('early_write',GUARD,'            conn.execute("UPDATE reseller_requests SET status=\'completed\' WHERE id=?", (request_id,))\n            conn.commit()\n'+GUARD),('status','next_status = "completed" if simple else "awaiting_bot_info"','next_status = "awaiting_bot_info"'),('tier','self.switch_agent_tier(req["user_id"], req["tier_code"])','self.switch_agent_tier(9002, req["tier_code"])'),('percent','percent = int(req["commission_percent"] or tier["commission_min"] or 10)','percent = 99'),('omit_enable','self.enable_inline_reseller(req["user_id"], percent)','pass'),('simple','tier["model"] in ("commission", "discount")','tier["model"] == "commission"'),('predicate',anchor,anchor.replace(ACTIVE,'pending_review')),('fallback','req["commission_percent"] or tier["commission_min"] or 10','req["commission_percent"] or 99'),('discount','int(req["discount_percent"]) if req["tier_code"] == "silver" and req["discount_percent"] is not None else None','None')]:
        def edit(s):
            if name=='discount':assert s.count(b)==2;return s.replace(b,a)
            return once(s,b,a)
        yield name,change(ref,ENTRY,edit)
    yield 'repeat',change(ref,ENTRY,lambda s:once(once(s,'req["status"] != "'+ACTIVE+'"','req["status"] not in ("'+ACTIVE+'", "completed")'),"AND status='"+ACTIVE+"'","AND status IN ('"+ACTIVE+"','completed')"))
