"""T050r: AI server-country discovery guard tests (tasks T050 / T053).

Refuse composite country/custom-plan discovery through unsupported AI shortcuts,
while preserving legacy country and plan grouping and visibility.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()

import ai_support
import database
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests.integration.test_composite_legacy_guards import as_row


@pytest.fixture
def countries(tmp_path, monkeypatch):
    db = database.Database(str(tmp_path / "country_guard.db"))
    db.init_db(9001)

    server_a = db.add_panel_server(
        "Country A",
        "3xui",
        "https://panel.example.invalid",
        "fake-user",
        "fake-password",
    )
    server_b = db.add_panel_server(
        "Country B",
        "3xui",
        "https://panel.example.invalid",
        "fake-user",
        "fake-password",
    )
    db.update_panel_server(server_a, used_for_custom_config=1)
    db.update_panel_server(server_b, used_for_custom_config=1)

    alpha = db.create_custom_config_product(
        "Alpha", server_a, min_gb=5, max_gb=50
    )
    beta = db.create_custom_config_product(
        "Beta", server_a, min_gb=10, max_gb=100
    )
    gamma = db.create_custom_config_product(
        "Gamma", server_b, min_gb=2, max_gb=20
    )

    original_get_custom_products = db.get_custom_config_products

    def inject(selected_id, kind, representation):
        def custom_products(active_only=False):
            rows = original_get_custom_products(active_only=active_only)
            out = []
            for row in rows:
                data = dict(row)
                data.pop("service_kind", None)
                if selected_id is not None and row["id"] == selected_id and kind is not None:
                    data["service_kind"] = kind
                    if kind == "composite":
                        data["name"] = "COMPOSITE-COUNTRY-PLAN"
                out.append(as_row(data, representation))
            return out

        monkeypatch.setattr(db, "get_custom_config_products", custom_products)

    try:
        yield SimpleNamespace(
            db=db,
            server_a=server_a,
            server_b=server_b,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            inject=inject,
        )
    finally:
        db.close()


def call(db):
    return asyncio.run(ai_support._run_tool(db, 5101, "get_server_countries", {}))


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("target", ["alpha", "gamma"])
def test_composite_ai_country_discovery_refused(countries, representation, target):
    c = countries
    selected_id = c.alpha if target == "alpha" else c.gamma
    c.inject(selected_id, "composite", representation)
    before = dump(c.db)

    result = call(c.db)

    assert isinstance(result, dict)
    assert result.get("ok") is False
    reason = result.get("reason")
    assert reason and "composite" in str(reason).lower()
    assert "countries" not in result
    assert "plans" not in result
    assert dump(c.db) == before


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("kind", [None, "legacy"])
def test_legacy_ai_country_discovery_exact(countries, representation, kind):
    c = countries
    c.inject(c.alpha, kind, representation)
    before = dump(c.db)

    result = call(c.db)

    expected = {
        "countries": [
            {
                "name": "Country A",
                "plans": [
                    {"product_name": "Alpha", "min_gb": 5, "max_gb": 50},
                    {"product_name": "Beta", "min_gb": 10, "max_gb": 100},
                ],
            },
            {
                "name": "Country B",
                "plans": [
                    {"product_name": "Gamma", "min_gb": 2, "max_gb": 20},
                ],
            },
        ]
    }
    assert result == expected
    assert dump(c.db) == before


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize(
    "isolation_mode",
    ["inactive_product", "inactive_server", "server_not_custom", "mirrored_server"],
)
def test_isolated_composite_ai_country_discovery(countries, representation, isolation_mode):
    c = countries
    if isolation_mode == "inactive_product":
        c.db.update_custom_config_product(c.gamma, is_active=0)
        expected = {
            "countries": [
                {
                    "name": "Country A",
                    "plans": [
                        {"product_name": "Alpha", "min_gb": 5, "max_gb": 50},
                        {"product_name": "Beta", "min_gb": 10, "max_gb": 100},
                    ],
                },
                {
                    "name": "Country B",
                    "plans": [],
                },
            ]
        }
    elif isolation_mode == "inactive_server":
        c.db.update_panel_server(c.server_b, is_active=0)
        expected = {
            "countries": [
                {
                    "name": "Country A",
                    "plans": [
                        {"product_name": "Alpha", "min_gb": 5, "max_gb": 50},
                        {"product_name": "Beta", "min_gb": 10, "max_gb": 100},
                    ],
                },
            ]
        }
    elif isolation_mode == "server_not_custom":
        c.db.update_panel_server(c.server_b, used_for_custom_config=0)
        expected = {
            "countries": [
                {
                    "name": "Country A",
                    "plans": [
                        {"product_name": "Alpha", "min_gb": 5, "max_gb": 50},
                        {"product_name": "Beta", "min_gb": 10, "max_gb": 100},
                    ],
                },
            ]
        }
    elif isolation_mode == "mirrored_server":
        with c.db._get_conn() as conn:
            conn.execute("UPDATE panel_servers SET is_mirror=1 WHERE id=?", (c.server_b,))
        expected = {
            "countries": [
                {
                    "name": "Country A",
                    "plans": [
                        {"product_name": "Alpha", "min_gb": 5, "max_gb": 50},
                        {"product_name": "Beta", "min_gb": 10, "max_gb": 100},
                    ],
                },
            ]
        }
    else:
        raise ValueError(f"Unknown isolation_mode: {isolation_mode}")

    c.inject(c.gamma, "composite", representation)
    before = dump(c.db)

    result = call(c.db)

    assert result == expected
    assert dump(c.db) == before


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_empty_catalog_control_with_composite(countries, representation):
    c = countries
    c.db.update_panel_server(c.server_a, used_for_custom_config=0)
    c.db.update_panel_server(c.server_b, used_for_custom_config=0)
    c.inject(c.gamma, "composite", representation)
    before = dump(c.db)

    result = call(c.db)

    expected = {
        "countries": [],
        "note": "در حال حاضر سروری برای ساخت کانفیگ شخصی تعریف نشده.",
    }
    assert result == expected
    assert dump(c.db) == before
