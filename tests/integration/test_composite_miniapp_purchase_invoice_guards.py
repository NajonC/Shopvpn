"""T050h: Mini App catalog checkout and every order-invoice adapter refuse composites."""
import pytest
import re
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import extra_gateway_payment
import extra_gateway_registry
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN, L1, L2, _call, _shop, mini
from tests.integration.test_composite_legacy_guards import as_row

INVOICES = ["crypto","abangateway","blupal","noapay","custom:synthetic","card_auto"] + ["extra:"+k for k in extra_gateway_registry.GATEWAY_ORDER]
WRAPPERS = {k:"_create_"+k+"_invoice_for" for k in ("crypto","abangateway","blupal","noapay")}
WRAPPERS.update(custom="_create_custom_gateway_invoice_for",extra="_create_extra_gateway_invoice",card_auto="_create_card_to_card_invoice_for")


def prepare(mini,monkeypatch,representation,kind,source=None,discriminator=None):
    db = mini.main
    db.add_or_update_user(5101,"u5101","U")
    db.add_wallet_credit(5101,30000)
    pid = _shop(db,"SECRET-MINI-PRODUCT" if source else "Safe Mini plan",100000,[L1,L2])
    oid = db.create_order(5101,pid,100000) if kind!="purchase" else None
    product = dict(db.get_product(pid))
    order = dict(db.get_order(oid)) if oid else None
    for row in (product,order):
        if row is not None:
            row.pop("service_kind",None)
            if discriminator is not None:row["service_kind"]=discriminator
    if source in ("product","order"):(product if source=="product" else order)["service_kind"]="composite"
    original_product,original_order = db.get_product,db.get_order
    monkeypatch.setattr(db,"get_product",lambda key:as_row(product,representation) if key==pid else original_product(key))
    if order:monkeypatch.setattr(db,"get_order",lambda key:as_row(order,representation) if key==oid else original_order(key))
    calls = []
    for key,name in WRAPPERS.items():
        def make(key):
            if key=="card_auto":
                def sync(*args,**kwargs):
                    calls.append((key,args,kwargs));return {"synthetic_invoice":key}
                return sync
            async def invoke(*args,**kwargs):
                calls.append((key,args,kwargs));return {"synthetic_invoice":key}
            return invoke
        monkeypatch.setattr(mini.server,name,make(key))
    monkeypatch.setattr(extra_gateway_payment,"API_BASE_URL","https://mini.example.invalid")
    for gateway in extra_gateway_registry.GATEWAY_ORDER:
        db.set_setting(extra_gateway_registry.enable_setting(gateway),"1")
        for field in extra_gateway_registry.GATEWAYS[gateway]["fields"]:
            if field["required"]:db.set_setting(field["setting"],"1" if field["numeric"] else "synthetic-not-a-key")
    body = {"product_id":pid}
    if discriminator is not None:body["service_kind"]=discriminator
    if source=="request":body["service_kind"]="composite"
    path = "/api/orders" if kind=="purchase" else (f"/api/orders/{oid}/extra-invoice/{kind.split(':')[1]}" if kind.startswith("extra:") else f"/api/orders/{oid}/custom-invoice/synthetic" if kind.startswith("custom:") else f"/api/orders/{oid}/card-auto-invoice" if kind=="card_auto" else f"/api/orders/{oid}/{kind}-invoice")
    return pid,oid,path,body,calls


def dump(db):
    with db._get_conn() as conn:return list(conn.iterdump())


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("kind,source",[("purchase",s) for s in ("product","request")]+[(k,s) for k in INVOICES for s in ("product","order")])
def test_composite_miniapp_purchase_invoice_refused(mini,monkeypatch,caplog,representation,kind,source):
    _,_,path,body,calls = prepare(mini,monkeypatch,representation,kind,source)
    before = dump(mini.main)
    code,result = _call(mini.server,"POST",path,token=MAIN_TOKEN,tg_id=5101,**({"json":body} if kind=="purchase" else {}))
    assert code==403 and "composite" in result["detail"].lower()
    assert calls==[] and mini.alerts==[] and mini.subs==[]
    assert dump(mini.main)==before
    assert "SECRET-MINI" not in str(result)+caplog.text


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("discriminator",[None,"legacy"])
@pytest.mark.parametrize("kind",["purchase",*INVOICES])
def test_legacy_miniapp_purchase_invoice_preserved(mini,monkeypatch,representation,discriminator,kind):
    pid,oid,path,body,calls = prepare(mini,monkeypatch,representation,kind,discriminator=discriminator)
    before = dump(mini.main)
    code,result = _call(mini.server,"POST",path,token=MAIN_TOKEN,tg_id=5101,**({"json":body} if kind=="purchase" else {}))
    assert code==200
    if kind=="purchase":
        assert result["status"]=="pending_payment" and result["order_id"]==1 and result["final_price"]==70000
        assert mini.main.get_wallet_credit(5101)==0 and mini.main.count_available_configs(pid)==2
        with mini.main._get_conn() as conn:
            assert tuple(conn.execute("SELECT user_id,product_id,status,wallet_used,final_price FROM orders").fetchone())==(5101,pid,"pending",30000,70000)
        assert calls==[]
    else:
        key = kind.split(':')[0]
        assert result=={"synthetic_invoice":key} and len(calls)==1 and calls[0][0]==key
        args = calls[0][1]
        assert (args[1:5] if key=="card_auto" else args[4:7] if key in ("extra","custom") else args[3:6])==(("order",oid,5101,100000) if key=="card_auto" else ("order",oid,100000))
        if key in ("extra","custom"):assert args[3]==kind.split(':')[1]
        expected = [re.sub(r'(INSERT INTO "sqlite_sequence" VALUES\(\'users\',)([0-9]+)(\);)', lambda m:m[1]+str(int(m[2])+1)+m[3],line) for line in before]
        assert expected!=before  # real legacy auth UPSERT advances this sequence exactly once
        assert dump(mini.main)==expected
    assert mini.alerts==[] and mini.subs==[]
