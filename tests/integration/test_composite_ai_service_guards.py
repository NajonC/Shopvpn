"""T050f: AI service shortcut dispatch tests (tasks T050 / T053).

Refuse composite records in nine read-only AI service shortcut tool routes before
returning an actionable success, while preserving current legacy shortcut responses.
"""
from __future__ import annotations

import asyncio

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()

import ai_support
import panel_providers
import sub_info
from tests.characterization.test_legacy_renewal_reminders import (
    BUYER,
    OTHER_USER,
    shop,
)
from tests.integration.test_composite_legacy_guards import as_row

NINE_TOOLS = [
    "set_service_auto_renew",
    "get_service_history",
    "request_service_qr",
    "request_individual_configs",
    "request_toggle_service_enabled",
    "request_rename_service",
    "request_regenerate_service_access",
    "request_transfer_service",
    "request_delete_service",
]

TOOL_ARGS_EXTRA = {
    "set_service_auto_renew": {"enabled": True},
    "get_service_history": {},
    "request_service_qr": {},
    "request_individual_configs": {},
    "request_toggle_service_enabled": {"enabled": True},
    "request_rename_service": {"new_name": "changed_name"},
    "request_regenerate_service_access": {},
    "request_transfer_service": {"target_telegram_id": OTHER_USER},
    "request_delete_service": {},
}


def _build_tool_args(tool_name: str, service_id: str) -> dict:
    args = {"service_id": service_id}
    args.update(TOOL_ARGS_EXTRA[tool_name])
    return args


def _expected_legacy_response(tool_name: str, service_id: str, shop) -> dict:
    if tool_name == "set_service_auto_renew":
        return {"ok": True, "service_id": service_id, "enabled": True}
    if tool_name == "get_service_history":
        rows = shop.db.get_custom_config_history(shop.cc)
        return {
            "ok": True,
            "events": [
                {"type": r["event_type"], "detail": r["detail"] or "", "at": r["created_at"]}
                for r in rows
            ],
        }
    if tool_name == "request_service_qr":
        return {"ok": True, "service_id": service_id}
    if tool_name == "request_individual_configs":
        return {"ok": True, "service_id": service_id}
    if tool_name == "request_toggle_service_enabled":
        return {"ok": True, "service_id": service_id, "enabled": True}
    if tool_name == "request_rename_service":
        return {"ok": True, "service_id": service_id, "new_name": "changed_name"}
    if tool_name == "request_regenerate_service_access":
        return {"ok": True, "service_id": service_id}
    if tool_name == "request_transfer_service":
        return {"ok": True, "service_id": service_id, "target_telegram_id": OTHER_USER}
    if tool_name == "request_delete_service":
        return {"ok": True, "service_id": service_id}
    raise ValueError(f"Unexpected tool: {tool_name}")


@pytest.fixture
def mock_external_calls(monkeypatch):
    provider_calls = []
    fetch_calls = []

    def fake_get_provider(*args, **kwargs):
        provider_calls.append((args, kwargs))
        return object()

    async def fake_fetch_sub_info(*args, **kwargs):
        fetch_calls.append((args, kwargs))
        return {"ok": True, "upload": 0, "download": 0, "total": 10 * 1024**3, "expire": None}

    monkeypatch.setattr(ai_support, "get_provider", fake_get_provider)
    monkeypatch.setattr(panel_providers, "get_provider", fake_get_provider)
    monkeypatch.setattr(ai_support, "fetch_sub_info", fake_fetch_sub_info)
    monkeypatch.setattr(sub_info, "fetch_sub_info", fake_fetch_sub_info)

    return provider_calls, fetch_calls


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("tool_name", NINE_TOOLS)
def test_composite_ai_service_shortcut_refused(
    shop, mock_external_calls, monkeypatch, representation, tool_name
):
    provider_calls, fetch_calls = mock_external_calls
    service_id = f"x{shop.cc}"
    args = _build_tool_args(tool_name, service_id)

    orig_get = shop.db.get_custom_config_owned
    real_record = dict(orig_get(shop.cc, BUYER))
    injected_data = dict(real_record)
    injected_data["service_kind"] = "composite"
    injected_row = as_row(injected_data, representation)

    def patched_get_custom_config_owned(custom_config_id, user_tg_id):
        if custom_config_id == shop.cc and user_tg_id == BUYER:
            return injected_row
        return orig_get(custom_config_id, user_tg_id)

    monkeypatch.setattr(shop.db, "get_custom_config_owned", patched_get_custom_config_owned)

    with shop.db._get_conn() as conn:
        before_sql = list(conn.iterdump())

    res = asyncio.run(ai_support._run_tool(shop.db, BUYER, tool_name, args))

    assert res == {"ok": False, "reason": "composite_unsupported"}
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before_sql
    assert provider_calls == []
    assert fetch_calls == []


@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("tool_name", NINE_TOOLS)
def test_legacy_ai_service_shortcut_preserved(
    shop, mock_external_calls, monkeypatch, representation, discriminator, tool_name
):
    provider_calls, fetch_calls = mock_external_calls
    service_id = f"x{shop.cc}"
    args = _build_tool_args(tool_name, service_id)

    orig_get = shop.db.get_custom_config_owned
    real_record = dict(orig_get(shop.cc, BUYER))
    injected_data = dict(real_record)
    injected_data.pop("service_kind", None)
    if discriminator is not None:
        injected_data["service_kind"] = discriminator
    injected_row = as_row(injected_data, representation)

    def patched_get_custom_config_owned(custom_config_id, user_tg_id):
        if custom_config_id == shop.cc and user_tg_id == BUYER:
            return injected_row
        return orig_get(custom_config_id, user_tg_id)

    monkeypatch.setattr(shop.db, "get_custom_config_owned", patched_get_custom_config_owned)

    with shop.db._get_conn() as conn:
        before_sql = list(conn.iterdump())

    res = asyncio.run(ai_support._run_tool(shop.db, BUYER, tool_name, args))

    expected = _expected_legacy_response(tool_name, service_id, shop)
    if tool_name == "get_service_history":
        assert expected["events"] and expected["events"][0]["type"] == "purchase"
    assert res == expected
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before_sql
    assert provider_calls == []
    assert fetch_calls == []
