"""T050b: reject composite candidates in legacy reminder and connection alert jobs before effects."""
import asyncio

import pytest

import connect_alerts
import renewal_reminders
from tests._harness.legacy_bot import RecordingBot, TelegramLog
from tests.characterization.test_legacy_renewal_reminders import (
    BUYER, CUST_1, DAY, GIB, MIB, POOL_1, POOL_2, codes, expire_in, flag,
    pool_config, shop, subs, usage,
)
from tests.integration.test_composite_legacy_guards import as_row

JOB_CONFIG = {
    "expiry": {
        "pool_selector": "get_configs_due_for_renewal_reminder",
        "custom_selector": "get_custom_configs_due_for_renewal_reminder",
        "marker": "renewal",
        "zero_result": 0,
        "legacy_result": 1,
        "run": lambda bot, db: renewal_reminders.check_and_send_renewal_reminders(bot, db),
    },
    "volume": {
        "pool_selector": "get_configs_due_for_volume_reminder",
        "custom_selector": "get_custom_configs_due_for_volume_reminder",
        "marker": "volume",
        "zero_result": 0,
        "legacy_result": 1,
        "run": lambda bot, db: renewal_reminders.check_and_send_volume_reminders(bot, db),
    },
    "connection": {
        "pool_selector": "get_configs_due_for_connect_check",
        "custom_selector": "get_custom_configs_due_for_connect_check",
        "marker": "connect",
        "zero_result": (0, 0),
        "legacy_result": (1, 0),
        "run": lambda bot, db: connect_alerts.check_and_send_connect_alerts(bot, db),
    },
}


@pytest.mark.parametrize("job", ["expiry", "volume", "connection"])
@pytest.mark.parametrize("source", ["pool", "custom"])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("assigned_user_id", [BUYER, None])
def test_composite_reminder_candidate_refused(
    shop, subs, monkeypatch, caplog, job, source, representation, assigned_user_id
):
    pool_config(shop, POOL_1)
    shop.db.set_setting("connect_alert_enabled", "1")

    cfg = JOB_CONFIG[job]
    selector = cfg["pool_selector"] if source == "pool" else cfg["custom_selector"]
    other_selector = cfg["custom_selector"] if source == "pool" else cfg["pool_selector"]

    row = dict(getattr(shop.db, selector)()[0])
    row["service_kind"] = "composite"
    row["assigned_user_id"] = assigned_user_id
    row["product_name"] = "SECRET-REMINDER-NAME"
    row["link"] = "https://sub.example.invalid/SECRET-REMINDER-NAME"

    subs.info[row["link"]] = usage(8 * GIB, expire=expire_in(3 * DAY + 3600))

    monkeypatch.setattr(shop.db, other_selector, lambda: [])
    monkeypatch.setattr(shop.db, selector, lambda: [as_row(row, representation)])

    with shop.db._get_conn() as conn:
        before = list(conn.iterdump())

    log = TelegramLog()
    result = asyncio.run(cfg["run"](RecordingBot(log), shop.db))

    assert result == cfg["zero_result"]
    assert subs.fetched == []
    assert log.events == []
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before

    messages = [r.getMessage().lower() for r in caplog.records if r.levelname == "WARNING"]
    assert any("composite" in m and cfg["marker"] in m for m in messages)
    assert "SECRET-REMINDER-NAME" not in caplog.text


@pytest.mark.parametrize("job", ["expiry", "volume", "connection"])
@pytest.mark.parametrize("source", ["pool", "custom"])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_reminder_candidate_still_processed(
    shop, subs, monkeypatch, job, source, representation, discriminator
):
    pool_config(shop, POOL_1)
    shop.db.set_setting("connect_alert_enabled", "1")

    cfg = JOB_CONFIG[job]
    selector = cfg["pool_selector"] if source == "pool" else cfg["custom_selector"]
    other_selector = cfg["custom_selector"] if source == "pool" else cfg["pool_selector"]

    row = dict(getattr(shop.db, selector)()[0])
    if discriminator is not None:
        row["service_kind"] = discriminator
    else:
        row.pop("service_kind", None)

    candidate_link = row["link"]
    if job == "expiry":
        subs.info[candidate_link] = usage(0, expire=expire_in(3 * DAY + 3600))
    elif job == "volume":
        subs.info[candidate_link] = usage(8 * GIB)
    elif job == "connection":
        subs.info[candidate_link] = usage(2 * MIB)

    monkeypatch.setattr(shop.db, other_selector, lambda: [])
    monkeypatch.setattr(shop.db, selector, lambda: [as_row(row, representation)])

    log = TelegramLog()
    result = asyncio.run(cfg["run"](RecordingBot(log), shop.db))

    assert result == cfg["legacy_result"]
    assert len(log.events) == 1
    assert log.events[0].chat_id == BUYER
    assert subs.fetched == [candidate_link]

    if job == "expiry":
        assert len(codes(shop, "renewal_reminder")) == 1
        assert len(codes(shop, "volume_reminder")) == 0
        if source == "pool":
            assert flag(shop, "configs", 1, "renewal_reminder_sent") == 1
            assert flag(shop, "custom_configs", shop.cc, "renewal_reminder_sent") == 0
        else:
            assert flag(shop, "custom_configs", shop.cc, "renewal_reminder_sent") == 1
            assert flag(shop, "configs", 1, "renewal_reminder_sent") == 0
    elif job == "volume":
        assert len(codes(shop, "volume_reminder")) == 1
        assert len(codes(shop, "renewal_reminder")) == 0
        if source == "pool":
            assert flag(shop, "configs", 1, "volume_reminder_sent") == 1
            assert flag(shop, "custom_configs", shop.cc, "volume_reminder_sent") == 0
        else:
            # Preserve known legacy custom-volume behavior: marks stock table rather than custom
            assert flag(shop, "custom_configs", shop.cc, "volume_reminder_sent") == 0
            assert flag(shop, "configs", 1, "volume_reminder_sent") == 1
    elif job == "connection":
        assert len(codes(shop, "renewal_reminder")) == 0
        assert len(codes(shop, "volume_reminder")) == 0
        if source == "pool":
            assert flag(shop, "configs", 1, "connect_alert_sent") == 1
            assert flag(shop, "custom_configs", shop.cc, "connect_alert_sent") == 0
        else:
            assert flag(shop, "custom_configs", shop.cc, "connect_alert_sent") == 1
            assert flag(shop, "configs", 1, "connect_alert_sent") == 0


@pytest.mark.parametrize("job", ["expiry", "volume", "connection"])
def test_composite_candidate_does_not_block_later_legacy(
    shop, subs, monkeypatch, caplog, job
):
    p1 = pool_config(shop, POOL_1)
    p2 = pool_config(shop, POOL_2)
    shop.db.set_setting("connect_alert_enabled", "1")

    cfg = JOB_CONFIG[job]
    if job == "expiry":
        subs.info[POOL_1] = usage(0, expire=expire_in(3 * DAY + 3600))
        subs.info[POOL_2] = usage(0, expire=expire_in(3 * DAY + 3600))
    elif job == "volume":
        subs.info[POOL_1] = usage(8 * GIB)
        subs.info[POOL_2] = usage(8 * GIB)
    elif job == "connection":
        subs.info[POOL_1] = usage(2 * MIB)
        subs.info[POOL_2] = usage(2 * MIB)

    original_rows = getattr(shop.db, cfg["pool_selector"])()
    row1 = dict(next(r for r in original_rows if r["link"] == POOL_1))
    row2 = dict(next(r for r in original_rows if r["link"] == POOL_2))

    composite_row = dict(row1, service_kind="composite")
    composite_row["product_name"] = "SECRET-REMINDER-NAME"
    composite_row["link"] = "https://sub.example.invalid/SECRET-REMINDER-NAME"
    subs.info[composite_row["link"]] = subs.info[POOL_1]

    legacy_row = dict(row2, service_kind="legacy")

    monkeypatch.setattr(shop.db, cfg["custom_selector"], lambda: [])
    monkeypatch.setattr(shop.db, cfg["pool_selector"], lambda: [composite_row, legacy_row])

    log = TelegramLog()
    result = asyncio.run(cfg["run"](RecordingBot(log), shop.db))

    assert result == cfg["legacy_result"]
    assert len(log.events) == 1
    assert log.events[0].chat_id == BUYER
    assert subs.fetched == [POOL_2]

    messages = [r.getMessage().lower() for r in caplog.records if r.levelname == "WARNING"]
    assert any("composite" in m and cfg["marker"] in m for m in messages)
    assert "SECRET-REMINDER-NAME" not in caplog.text

    if job == "expiry":
        assert flag(shop, "configs", p1, "renewal_reminder_sent") == 0
        assert flag(shop, "configs", p2, "renewal_reminder_sent") == 1
        assert len(codes(shop, "renewal_reminder")) == 1
        assert len(codes(shop, "volume_reminder")) == 0
    elif job == "volume":
        assert flag(shop, "configs", p1, "volume_reminder_sent") == 0
        assert flag(shop, "configs", p2, "volume_reminder_sent") == 1
        assert len(codes(shop, "volume_reminder")) == 1
        assert len(codes(shop, "renewal_reminder")) == 0
    elif job == "connection":
        assert flag(shop, "configs", p1, "connect_alert_sent") == 0
        assert flag(shop, "configs", p2, "connect_alert_sent") == 1
        assert len(codes(shop, "renewal_reminder")) == 0
        assert len(codes(shop, "volume_reminder")) == 0
