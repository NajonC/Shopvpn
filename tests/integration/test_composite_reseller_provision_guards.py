"""T050e: composites never consume reseller credit or provision legacy children."""
import asyncio
import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import reseller_auto_provision as provision
from tests.characterization.test_unsupported_surfaces import rap
from tests.integration.test_composite_legacy_guards import as_row


def snapshot(db):
    with db._get_conn() as conn:
        return list(conn.iterdump())


def setup(rap, monkeypatch, representation, surface, source=None, discriminator="legacy"):
    m, t = rap.main, rap.tenant
    t.add_or_update_user(7001, "synthetic-buyer", "Synthetic Buyer")
    oid = t.create_order(7001, 1, 50000)
    m.adjust_reseller_credit(5001, 50, reason="synthetic seed")
    cat = m.add_category("Synthetic supply")
    pid = m.add_product(cat, "Safe supply", 50000, duration_days=60, is_auto_provision=True, auto_provision_volume_gb=10, provision_server_id=1)
    m.grant_reseller_product_credit(5001, pid, 2)
    order = dict(t.get_order(oid))
    data = ({"id":4,"name":"Safe test","name_prefix":"tst","volume_mb":512,"duration_hours":12} if surface=="test" else dict((m if surface=="fixed" else t).get_product(pid if surface=="fixed" else 1)))
    for row in (order, data):
        row.pop("service_kind", None)
        if discriminator is not None:
            row["service_kind"] = discriminator
    if source:
        (order if source=="order" else data)["service_kind"] = "composite"
        data["name"] = "SECRET-SUPPLY-NAME"
    monkeypatch.setattr(t, "get_order", lambda key: as_row(order, representation) if key==oid else None)
    if surface=="fixed":
        original = m.get_product
        monkeypatch.setattr(m, "get_product", lambda key: as_row(data, representation) if key==pid else original(key))
    async def invoke():
        if surface=="auto":
            return await provision.provision_auto_config(t, as_row(data, representation), 1, user_id=7001, order_id=oid)
        if surface=="test":
            return await provision.provision_test_config(t, as_row(data, representation), user_id=7001)
        return await provision.provision_reseller_fixed_product(m, 5001, pid, 1, username="fixedsynthetic")
    return invoke, pid, oid


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("surface,source", [("auto","product"),("auto","order"),("test","plan"),("fixed","product")])
def test_composite_reseller_provision_refused_before_effects(rap, monkeypatch, caplog, representation, surface, source):
    invoke, _, _ = setup(rap, monkeypatch, representation, surface, source)
    before = [snapshot(db) for db in (rap.main, rap.tenant)]
    with pytest.raises(provision.ProvisionError, match="(?i)composite") as error:
        asyncio.run(invoke())
    assert rap.servers == [] and rap.remote.calls == [] and rap.remote.users == {}
    assert [snapshot(db) for db in (rap.main, rap.tenant)] == before
    assert "SECRET-SUPPLY" not in str(error.value) + caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("surface", ["auto", "test", "fixed"])
def test_legacy_reseller_provision_preserves_credit_and_records(rap, monkeypatch, representation, discriminator, surface):
    invoke, pid, oid = setup(rap, monkeypatch, representation, surface, discriminator=discriminator)
    result = asyncio.run(invoke())
    item = result if surface=="test" else result[0]
    volume, days = (0.5, 0.5) if surface=="test" else (10, 60)
    assert item["volume_gb"] == volume and item["duration_days"] == days
    assert item["subscription_url"] == "https://sub.example.invalid/" + item["username"]
    assert rap.remote.calls == [("create_user", item["username"], volume, days)]
    assert rap.servers == [1]
    assert rap.main.get_reseller_credit(5001) == (50 if surface=="fixed" else 50-volume)
    assert rap.main.get_reseller_product_credit(5001,pid) == (1 if surface=="fixed" else 2)
    with rap.tenant._get_conn() as conn:
        records = conn.execute("SELECT user_id,username,source,order_id,product_id,volume_gb,duration_days FROM custom_configs").fetchall()
    assert len(records) == (0 if surface=="fixed" else 1)
    if records:
        assert tuple(records[0]) == (7001,item["username"],"test" if surface=="test" else "direct_product",None if surface=="test" else oid,4 if surface=="test" else None,volume,days)
