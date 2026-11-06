"""T050l: unsupported composite trial catalog, claim and retained-link guards."""
import re
from types import SimpleNamespace

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import test_config_provision
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN, _call, mini
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_miniapp_retrieval_guards import dump

LINK = "https://sub.example.invalid/SECRET-TRIAL-LINK"
KINDS = ("status_plan", "status_custom", "status_stock", "claim_explicit", "claim_implicit", "claim_stock")
SOURCES = [(k, s) for k in KINDS for s in (("plan", "request") if k in ("claim_explicit", "claim_implicit") else ("request",) if k == "claim_stock" else ("plan",) if k == "status_plan" else ("custom",) if k == "status_custom" else ("stock",))]


def prepare(mini, monkeypatch, representation, kind, source=None, discriminator=None, unrelated=False):
    db = mini.main
    db.add_or_update_user(5101, "u5101", "U")
    sid = db.add_panel_server("Synthetic", "3xui", "https://panel.example.invalid", "fake-user", "fake-password")
    pid = None
    if kind in ("status_plan", "claim_explicit", "claim_implicit"):
        pid = db.create_test_config_plan("Safe trial", "tst", sid, 512, 12)
    other = db.create_test_config_plan("Other composite", "other", sid, 1024, 24) if unrelated else None
    if kind in ("status_custom", "status_stock"):
        assert db.try_reserve_test_slot(5101, mini.server.MAX_TEST_PER_USER)
        if kind == "status_custom": db.add_custom_config(5101, sid, "existing_trial", 0.5, 0.5, LINK, source="test")
        else:
            db.add_test_configs([LINK])
            assert db.take_unused_test_config(5101)["link"] == LINK
    elif kind == "claim_stock": db.add_test_configs([LINK])
    calls = []

    class Provider:
        async def create_user(self, username, volume_gb, duration_days):
            calls.append(("create", username, volume_gb, duration_days))
            return SimpleNamespace(subscription_url=LINK)

    def provider(server):
        calls.append(("factory", server["id"]))
        return Provider()

    monkeypatch.setattr(test_config_provision, "get_provider", provider)
    for name, category in (("get_test_config_plans", "plan"), ("get_test_custom_config_for_user", "custom"), ("get_assigned_test_config", "stock")):
        original = getattr(db, name)
        def wrap(*args, original=original, category=category, **kwargs):
            result = original(*args, **kwargs)
            def convert(row):
                if row is None: return None
                data = dict(row)
                data.pop("service_kind", None)
                if discriminator is not None: data["service_kind"] = discriminator
                if source == category or (category == "plan" and other is not None and data["id"] == other): data["service_kind"] = "composite"
                return as_row(data, representation)
            return [convert(r) for r in result] if isinstance(result, list) else convert(result)
        monkeypatch.setattr(db, name, wrap)
    body = {"plan_id": pid} if kind == "claim_explicit" else {}
    if discriminator is not None: body["service_kind"] = discriminator
    if source == "request": body["service_kind"] = "composite"
    path = "/api/test-config" + ("/claim" if kind.startswith("claim_") else "")
    return sid, pid, path, ({"json": body} if kind.startswith("claim_") else {}), calls


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("kind,source", SOURCES)
def test_composite_miniapp_trial_refused(mini, monkeypatch, caplog, representation, kind, source):
    _, _, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, source)
    before = dump(mini.main)
    code, result = _call(mini.server, "POST" if kind.startswith("claim_") else "GET", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 403 and "composite" in result["detail"].lower()
    assert dump(mini.main) == before and calls == [] and mini.subs == [] and mini.alerts == []
    assert "SECRET-TRIAL" not in str(result) + caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("kind,unrelated", [(k, False) for k in KINDS] + [("claim_explicit", True)])
def test_legacy_miniapp_trial_preserved(mini, monkeypatch, representation, discriminator, kind, unrelated):
    sid, pid, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, discriminator=discriminator, unrelated=unrelated)
    before = dump(mini.main)
    code, result = _call(mini.server, "POST" if kind.startswith("claim_") else "GET", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 200
    if kind.startswith("status_"):
        assert result == {"enabled": True, "used": kind != "status_plan", "available": 0, "link": None if kind == "status_plan" else LINK, "plans": [{"id": pid, "name": "Safe trial", "volume_mb": 512, "duration_hours": 12, "amount_label": "512 مگابایت / 12 ساعت"}] if kind == "status_plan" else []}
        expected = [re.sub(r'(INSERT INTO "sqlite_sequence" VALUES\(\'users\',)([0-9]+)(\);)', lambda m: m[1]+str(int(m[2])+1)+m[3], line) for line in before]
        assert expected != before and dump(mini.main) == expected and calls == []
    else:
        assert result == {"link": LINK} and mini.main.get_user(5101)["test_used"] == 1
        assert mini.main.get_wallet_credit(5101) == 0
        with mini.main._get_conn() as conn:
            assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
            records = conn.execute("SELECT user_id,username,volume_gb,duration_days,subscription_url,source,product_id FROM custom_configs").fetchall()
            assert conn.execute("SELECT COUNT(*) FROM custom_config_history").fetchone()[0] == (0 if kind == "claim_stock" else 1)
        if kind == "claim_stock":
            assert calls == [] and records == [] and mini.main.count_available_test_configs() == 0
            assert mini.main.get_assigned_test_config(5101)["link"] == LINK
        else:
            assert len(records) == 1
            user, username, volume, days, link, origin, product = records[0]
            assert (user, volume, days, link, origin, product) == (5101, 0.5, 0.5, LINK, "test", pid)
            assert re.fullmatch(r"tst[a-z0-9]{8}", username)
            assert calls == [("factory", sid), ("create", username, 0.5, 0.5)]
    assert mini.subs == [] and mini.alerts == []
