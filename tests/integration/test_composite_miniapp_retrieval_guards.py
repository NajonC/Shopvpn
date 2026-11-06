"""T050i: Mini App retrieval refuses composite metadata before auth writes or exports."""
from datetime import datetime,timedelta,timezone
import re
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN,_call,_shop,mini
from tests.integration.test_composite_legacy_guards import as_row

LINK="https://sub.example.invalid/SECRET-GET-LINK"
SOURCES={"orders":["order","product"],"customs":["custom"],"sub_pool":["order","product"],"sub_custom":["custom"],"expiring_pool":["order","product","row"],"expiring_custom":["custom","row"],"invoice_status":["order","product"],"history":["custom"]}


def prepare(mini,monkeypatch,representation,kind,source=None,discriminator=None):
    db=mini.main
    db.add_or_update_user(5101,"u5101","U")
    pid=_shop(db,"SECRET-GET-PRODUCT" if source else "Safe retrieval",100000,[LINK])
    cc=oid=None;invoice=None
    expires=(datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(days=2)).isoformat()
    if kind in ("customs","sub_custom","expiring_custom","history"):
        sid=db.add_panel_server("Synthetic","3xui","https://panel.example.invalid","synthetic-user","synthetic-pass")
        cc=db.add_custom_config(5101,sid,"cust1",10,30,LINK,expires_at=expires)
    elif kind=="invoice_status":
        oid=db.create_order(5101,pid,100000)
        db.create_card_to_card_card("0000111122223333","Synthetic Holder","Synthetic Bank")
        code,invoice=_call(mini.server,"POST",f"/api/orders/{oid}/card-auto-invoice",token=MAIN_TOKEN,tg_id=5101)
        assert code==200 and 100100<=invoice["amount_toman"]<=100999
    else:
        db.add_wallet_credit(5101,100000)
        code,result=_call(mini.server,"POST","/api/orders",token=MAIN_TOKEN,tg_id=5101,json={"product_id":pid})
        assert code==200 and result["status"]=="approved"
        oid=result["order_id"]
        with db._get_conn() as conn:conn.execute("UPDATE configs SET expires_at=? WHERE product_id=?",(expires,pid))
    mini.alerts.clear();mini.subs.clear()
    product=dict(db.get_product(pid));orders=[dict(r) for r in db.get_user_orders(5101)];customs=[dict(r) for r in db.get_custom_configs_for_user(5101)];expiring=[dict(r) for r in db.get_expiring_configs_for_user(5101)]
    for row in [product,*orders,*customs,*expiring]:
        row.pop("service_kind",None)
        if discriminator is not None:row["service_kind"]=discriminator
    if source:
        ({"product":[product],"order":orders,"custom":customs,"row":expiring}[source])[0]["service_kind"]="composite"
    getters={name:getattr(db,name) for name in ("get_product","get_user_orders","get_order","get_custom_configs_for_user","get_custom_config_owned","get_expiring_configs_for_user")}
    monkeypatch.setattr(db,"get_product",lambda key:as_row(product,representation) if key==pid else getters["get_product"](key))
    monkeypatch.setattr(db,"get_user_orders",lambda user:[as_row(r,representation) for r in orders] if user==5101 else getters["get_user_orders"](user))
    monkeypatch.setattr(db,"get_order",lambda key:as_row(orders[0],representation) if oid and key==oid else getters["get_order"](key))
    monkeypatch.setattr(db,"get_custom_configs_for_user",lambda user:[as_row(r,representation) for r in customs] if user==5101 else getters["get_custom_configs_for_user"](user))
    monkeypatch.setattr(db,"get_custom_config_owned",lambda key,user:as_row(customs[0],representation) if cc and key==cc and user==5101 else getters["get_custom_config_owned"](key,user))
    monkeypatch.setattr(db,"get_expiring_configs_for_user",lambda user,*args:[as_row(r,representation) for r in expiring] if user==5101 else getters["get_expiring_configs_for_user"](user,*args))
    url={"orders":"/api/orders","customs":"/api/custom-configs","sub_pool":"/api/sub-info","sub_custom":"/api/sub-info","expiring_pool":"/api/expiring","expiring_custom":"/api/expiring","invoice_status":f"/api/card-auto-invoice/{invoice['invoice_id'] if invoice else 0}/status","history":f"/api/custom-configs/{cc}/history"}[kind]
    return url,({"link":LINK} if kind.startswith("sub_") else {}),oid,cc,invoice,expires


def dump(db):
    with db._get_conn() as conn:return list(conn.iterdump())


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("kind,source",[(k,s) for k,values in SOURCES.items() for s in values])
def test_composite_miniapp_retrieval_refused(mini,monkeypatch,caplog,representation,kind,source):
    url,params,*_=prepare(mini,monkeypatch,representation,kind,source)
    before=dump(mini.main)
    code,result=_call(mini.server,"GET",url,token=MAIN_TOKEN,tg_id=5101,params=params)
    assert code==403 and "composite" in result["detail"].lower()
    assert mini.subs==[] and mini.alerts==[] and dump(mini.main)==before
    assert "SECRET-GET" not in str(result)+caplog.text


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("discriminator",[None,"legacy"])
@pytest.mark.parametrize("kind",list(SOURCES))
def test_legacy_miniapp_retrieval_preserved(mini,monkeypatch,representation,discriminator,kind):
    url,params,oid,cc,invoice,expires=prepare(mini,monkeypatch,representation,kind,discriminator=discriminator)
    before=dump(mini.main)
    code,result=_call(mini.server,"GET",url,token=MAIN_TOKEN,tg_id=5101,params=params)
    assert code==200
    if kind=="orders":assert len(result)==1 and result[0]["id"]==oid and result[0]["link"]==LINK and result[0]["links"]==[LINK]
    elif kind=="customs":assert len(result)==1 and result[0]["id"]==cc and result[0]["subscription_url"]==LINK and result[0]["volume_gb"]==10
    elif kind.startswith("sub_"):assert result=={"ok":False,"marker":"synthetic"}
    elif kind.startswith("expiring_"):assert len(result)==1 and result[0]["link"]==LINK and result[0]["expires_at"]==expires
    elif kind=="history":assert result and result[0]["event_type"]=="purchase"
    else:assert result=={"status":"pending","amount_toman":invoice["amount_toman"]}
    assert mini.subs==([LINK] if kind.startswith(("sub_","expiring_")) else []) and mini.alerts==[]
    expected=[re.sub(r'(INSERT INTO "sqlite_sequence" VALUES\(\'users\',)([0-9]+)(\);)',lambda m:m[1]+str(int(m[2])+1)+m[3],line) for line in before]
    assert expected!=before and dump(mini.main)==expected


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("kind",["sub_pool","expiring_pool"])
def test_requested_legacy_service_not_blocked_by_unrelated_composite(mini,monkeypatch,representation,kind):
    url,params,_,_,_,expires=prepare(mini,monkeypatch,representation,kind)
    db=mini.main
    sid=db.add_panel_server("Unrelated","3xui","https://other.example.invalid","synthetic-user","synthetic-pass")
    cc=db.add_custom_config(5101,sid,"other_service",10,30,"https://sub.example.invalid/unrelated-composite",expires_at="2030-01-01T00:00:00")
    record=dict(db.get_custom_config_owned(cc,5101),service_kind="composite")
    original=db.get_custom_configs_for_user
    monkeypatch.setattr(db,"get_custom_configs_for_user",lambda user:[as_row(record,representation)] if user==5101 else original(user))
    before=dump(db)
    code,result=_call(mini.server,"GET",url,token=MAIN_TOKEN,tg_id=5101,params=params)
    assert code==200
    assert result=={"ok":False,"marker":"synthetic"} if kind=="sub_pool" else len(result)==1 and result[0]["link"]==LINK and result[0]["expires_at"]==expires
    assert mini.subs==[LINK] and mini.alerts==[]
    expected=[re.sub(r'(INSERT INTO "sqlite_sequence" VALUES\(\'users\',)([0-9]+)(\);)',lambda m:m[1]+str(int(m[2])+1)+m[3],line) for line in before]
    assert expected!=before and dump(db)==expected
