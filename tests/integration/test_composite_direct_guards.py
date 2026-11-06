"""T050c: direct provisioning guards against composite orders and products."""
import asyncio

import pytest

import direct_panel_provision
from direct_panel_provision import ProvisionError
from tests.characterization.test_direct_provision import BUYER, _order, _rows, shop
from tests.integration.test_composite_legacy_guards import as_row


@pytest.mark.parametrize("quantity", [1, 2])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("source", ["order", "product"])
def test_composite_direct_refused_before_provision(shop, monkeypatch, caplog, quantity, representation, source):
    shop.db.add_or_update_user(BUYER, "synthetic-buyer", "Synthetic Buyer")
    order_id = _order(shop, config_name="ali", quantity=quantity)

    order = dict(shop.db.get_order(order_id))
    product = dict(shop.db.get_product(shop.product_id))

    order["service_kind"] = "legacy"
    product["service_kind"] = "legacy"
    if source == "order":
        order["service_kind"] = "composite"
    elif source == "product":
        product["service_kind"] = "composite"

    product["name"] = "SECRET-DIRECT-NAME"

    monkeypatch.setattr(shop.db, "get_order", lambda key: as_row(order, representation) if key == order_id else None)
    product_row = as_row(product, representation)

    with shop.db._get_conn() as conn:
        before = list(conn.iterdump())

    with pytest.raises(ProvisionError, match="(?i)composite") as exc_info:
        asyncio.run(
            direct_panel_provision.provision_direct(
                shop.db, product_row, quantity=quantity, user_id=BUYER, order_id=order_id
            )
        )

    assert shop.panel.servers == []
    assert shop.panel.calls == []
    assert shop.panel.users == {}
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before
    assert "SECRET-DIRECT" not in str(exc_info.value)
    assert "SECRET-DIRECT" not in caplog.text


@pytest.mark.parametrize("quantity", [1, 2])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_direct_still_builds_and_persists(shop, monkeypatch, quantity, representation, discriminator):
    shop.db.add_or_update_user(BUYER, "synthetic-buyer", "Synthetic Buyer")
    order_id = _order(shop, config_name="ali", quantity=quantity)

    order = dict(shop.db.get_order(order_id))
    product = dict(shop.db.get_product(shop.product_id))

    for row in (order, product):
        row.pop("service_kind", None)
        if discriminator is not None:
            row["service_kind"] = discriminator

    monkeypatch.setattr(shop.db, "get_order", lambda key: as_row(order, representation) if key == order_id else None)
    product_row = as_row(product, representation)

    result = asyncio.run(
        direct_panel_provision.provision_direct(
            shop.db, product_row, quantity=quantity, user_id=BUYER, order_id=order_id
        )
    )

    expected_names = ["ali"] if quantity == 1 else ["ali_1", "ali_2"]
    assert len(result) == quantity
    assert [item["username"] for item in result] == expected_names
    assert [item["subscription_url"] for item in result] == [
        f"https://sub.example.invalid/sub/{name}" for name in expected_names
    ]
    assert all(item["volume_gb"] == 50 and item["duration_days"] == 30 for item in result)

    assert shop.panel.servers == [shop.server_id]
    assert shop.panel.calls == [("create_user", name, 50, 30) for name in expected_names]
    assert shop.panel.users == {name: (50, 30) for name in expected_names}

    rows = _rows(shop.db_path)
    assert len(rows) == quantity
    for row, name in zip(rows, expected_names):
        assert row[1] == name
        assert row[2] == BUYER
        assert row[3] == order_id
        assert row[4] == shop.server_id
        assert row[5] == 50
        assert row[6] == 30
        assert row[7] == f"https://sub.example.invalid/sub/{name}"
        assert row[8] == "direct_product"
        assert row[9] == "active"
