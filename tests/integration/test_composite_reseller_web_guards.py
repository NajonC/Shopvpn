"""T050g: reseller web requests cannot discard composite type and spend credit."""
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_unsupported_surfaces import CUSTOM, FIXED, _panel_call, rweb
from tests.integration.test_composite_legacy_guards import as_row


def dump(db):
    with db._get_conn() as conn:
        return list(conn.iterdump())


def prepare(rweb, monkeypatch, representation, mode, source=None, discriminator=None):
    m = rweb.main
    m.adjust_reseller_credit(5001,50,reason="synthetic seed")
    cat = m.add_category("Synthetic supply")
    pid = m.add_product(cat,"SECRET-SELF-NAME" if source else "Safe supply",100000,duration_days=60,is_auto_provision=True,auto_provision_volume_gb=20,provision_server_id=1)
    m.grant_reseller_product_credit(5001,pid,2)
    if mode=="fixed":
        m.set_reseller_supply_model(5001,"fixed_product",pid)
    product = dict(m.get_product(pid))
    product.pop("service_kind",None)
    if discriminator is not None:
        product["service_kind"] = discriminator
    if source=="product":
        product["service_kind"] = "composite"
    original = m.get_product
    monkeypatch.setattr(m,"get_product",lambda key:as_row(product,representation) if key==pid else original(key))
    body = {"product_id":pid} if mode=="fixed" else {"volume_gb":10,"duration_days":30,"username":"syntheticself"}
    if discriminator is not None:
        body["service_kind"] = discriminator
    if source=="request":
        body["service_kind"] = "composite"
    return FIXED if mode=="fixed" else CUSTOM, body, pid


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("mode,source",[("fixed","product"),("fixed","request"),("custom","request")])
def test_composite_reseller_web_refused_before_effects(rweb,monkeypatch,caplog,representation,mode,source):
    url,body,_ = prepare(rweb,monkeypatch,representation,mode,source)
    before = [dump(db) for db in (rweb.main,rweb.tenant)]
    code,result = _panel_call(rweb.panel,"POST",url,json=body)
    assert code==403
    assert "composite" in result["detail"].lower()
    assert "SECRET-SELF" not in str(result)+caplog.text
    assert rweb.servers==[] and rweb.remote.calls==[] and rweb.remote.users=={}
    assert [dump(db) for db in (rweb.main,rweb.tenant)]==before


@pytest.mark.parametrize("representation",["dict","sqlite"])
@pytest.mark.parametrize("discriminator",[None,"legacy"])
@pytest.mark.parametrize("mode",["fixed","custom"])
def test_legacy_reseller_web_preserves_credit_and_service(rweb,monkeypatch,representation,discriminator,mode):
    url,body,pid = prepare(rweb,monkeypatch,representation,mode,discriminator=discriminator)
    code,result = _panel_call(rweb.panel,"POST",url,json=body)
    assert code==200
    volume,days = (20,60) if mode=="fixed" else (10,30)
    username = result["username"]
    assert result=={"username":username,"subscription_url":"https://sub.example.invalid/"+username,"volume_gb":volume,"duration_days":days}
    assert rweb.servers==[1]
    assert rweb.remote.calls==[("create_user",username,volume,days)]
    assert rweb.main.get_reseller_credit(5001)==(50 if mode=="fixed" else 40)
    assert rweb.main.get_reseller_product_credit(5001,pid)==(1 if mode=="fixed" else 2)
    with rweb.tenant._get_conn() as conn:
        rows = conn.execute("SELECT user_id,username,volume_gb,duration_days,subscription_url,source FROM custom_configs").fetchall()
    assert [tuple(r) for r in rows]==[(5001,username,volume,days,result["subscription_url"],"reseller")]
    with rweb.main._get_conn() as conn:
        actions = [r[0] for r in conn.execute("SELECT action FROM admin_logs")]
    assert actions==["reseller_self_"+mode]
