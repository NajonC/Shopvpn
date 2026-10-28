"""Characterize ``direct_panel_provision.provision_direct`` (34–136) at commit ba6324e.
Reproduce with ``.venv/bin/python -m pytest tests/characterization/test_direct_provision.py --network=deny``.
The VPN panel is a synthetic substitute, not evidence; the database is the real
``database.Database`` on a temporary file.

Known unsafe behaviour: (a) panel names are chosen inside the call and the
panel's provider picks the credentials; nothing is saved before the remote
create (case 9), so a repeated call for the same order creates a second panel
user under a new name instead of finding the first, whether or not the first
was saved (FR-022; case 10); (b) the units built so far live only in memory: a
``PanelError`` deletes the earlier units but leaves the failing unit on the
panel even when the panel applied it (case 11), delete failures are ignored
(case 12), and any other exception, a crash or a database error passes through
with no rollback at all, leaving every created unit on the panel with no local
record (cases 13, 14); (c) local saving happens only after every unit exists on
the panel; a failed save is logged and swallowed and the full list is still
returned, so the buyer is told it succeeded while "my services" misses the
unit (cases 18, 19); without ``user_id`` nothing is saved at all (case 17).
"""

import asyncio
import contextlib
import logging
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import database
import direct_panel_provision
from direct_panel_provision import ProvisionError
from panel_providers.base import PanelError, PanelUserResult, PanelUsernameTakenError
from tests._harness.crash import SimulatedCrash

OWNER = 9001
BUYER = 1001
OTHER_BUYER = 2002
VOLUME_GB = 50
SUB = "https://sub.example.invalid/sub/"
RANDOM_NAME = r"d[a-z0-9]{8}"
PREFIXED_NAME = r"hunter-d[a-z0-9]{8}"
BAD_QUANTITY = "تعداد درخواستی نامعتبر است."
NO_SERVER = "این محصول به هیچ پنلی وصل نشده است."
SERVER_GONE = "پنل متصل به این محصول یافت نشد یا غیرفعال است؛ با پشتیبانی تماس بگیرید."
NO_VOLUME = "حجم این محصول تنظیم نشده است."
NO_UNIQUE_NAME = "ساخت نام کاربری یکتا روی پنل ناموفق بود؛ دوباره تلاش کنید."
PROVISION_FAILED = "خطا در ساخت کانفیگ روی پنل: synthetic timeout"
HISTORY_50_30 = ("purchase", "50 گیگ / 30 روز")
LOG_FAILED = "add_custom_config برای واحد direct-provision ناموفق بود (user_id={}, username={}, order_id={}) - این سرویس در «سرویس\u200cهای من» دیده نخواهد شد."
DB_LOCKED = "synthetic: database is locked"


class FakePanel:
    """Synthetic VPN panel returned by every get_provider call. Substitute, not evidence."""

    def __init__(self, count_rows):
        self.count_rows = count_rows
        self.servers = []          # server["id"] of each get_provider call
        self.users = {}            # username -> (volume_gb, duration_days)
        self.calls = []            # ("create_user", name, volume_gb, duration_days) or ("delete_user", name)
        self.rows_at_create = []   # custom_configs row count when each create_user starts
        self.refuse = lambda name: False   # names the panel reports as duplicates
        self.create_errors = {}    # create_user call number (1-based) -> exception raised after the user is stored
        self.delete_errors = {}    # username -> exception raised before anything is removed

    async def create_user(self, username, volume_gb, duration_days):
        self.calls.append(("create_user", username, volume_gb, duration_days))
        self.rows_at_create.append(self.count_rows())
        if self.refuse(username) or username in self.users:
            raise PanelUsernameTakenError(username)
        self.users[username] = (volume_gb, duration_days)
        error = self.create_errors.get(len(self.rows_at_create))
        if error is not None:
            raise error
        return PanelUserResult(username, SUB + username)

    async def delete_user(self, username):
        self.calls.append(("delete_user", username))
        if username in self.delete_errors:
            raise self.delete_errors[username]
        return self.users.pop(username, None) is not None


def _rows(db_path):
    with contextlib.closing(sqlite3.connect(db_path)) as conn:
        return conn.execute(
            "SELECT id, username, user_id, order_id, panel_server_id, volume_gb, duration_days, "
            "subscription_url, source, status, expires_at FROM custom_configs ORDER BY id"
        ).fetchall()


@pytest.fixture
def shop(tmp_path, monkeypatch):
    db_path = tmp_path / "main.db"
    db = database.Database(str(db_path))
    db.init_db(OWNER)
    server_id = db.add_panel_server(
        "Panel D", "3xui", "https://panel.example.invalid", "synthetic-user", "synthetic-pass"
    )
    category_id = db.add_category("VPN")
    product_id = db.add_product(
        category_id, "Direct 50GB", 120_000, is_auto_provision=True,
        auto_provision_volume_gb=VOLUME_GB, provision_server_id=server_id,
    )
    panel = FakePanel(lambda: len(_rows(db_path)))

    def get_provider(server):
        panel.servers.append(server["id"])
        return panel

    monkeypatch.setattr(direct_panel_provision, "get_provider", get_provider)
    return SimpleNamespace(db=db, db_path=db_path, server_id=server_id, product_id=product_id, panel=panel)


def _product(shop, **overrides):
    return {**dict(shop.db.get_product(shop.product_id)), **overrides}


def _order(shop, config_name="ali", quantity=1):
    return shop.db.create_order(BUYER, shop.product_id, 120_000, quantity=quantity, config_name=config_name)


def _provision(shop, quantity=1, product=None, **kwargs):
    product = product if product is not None else shop.db.get_product(shop.product_id)
    return asyncio.run(direct_panel_provision.provision_direct(shop.db, product, quantity, **kwargs))


def _fail_on_calls(monkeypatch, db, method, calls, error):
    original = getattr(db, method)
    count = 0

    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        if count in calls:
            raise error
        return original(*args, **kwargs)

    monkeypatch.setattr(db, method, wrapper)


def _creates(panel):
    return [call[1] for call in panel.calls if call[0] == "create_user"]


def _deletes(panel):
    return [call[1] for call in panel.calls if call[0] == "delete_user"]


# Case 1
@pytest.mark.parametrize("quantity", [0, -1, 1.0, "2"], ids=["zero", "negative", "float", "text"])
def test_rejects_invalid_quantity(shop, quantity):
    with pytest.raises(ProvisionError) as exc:
        _provision(shop, quantity)
    assert str(exc.value) == BAD_QUANTITY
    assert shop.panel.servers == []
    assert shop.panel.calls == []
    assert _rows(shop.db_path) == []


# Case 2
@pytest.mark.parametrize("case", ["no_server", "missing_server", "inactive_server", "no_volume", "negative_volume"],
                         ids=["no_server", "missing_server", "inactive_server", "no_volume", "negative_volume"])
def test_rejects_unusable_product_or_server(shop, case):
    product = shop.db.get_product(shop.product_id)
    expected = SERVER_GONE if case in {"missing_server", "inactive_server"} else NO_SERVER if case == "no_server" else NO_VOLUME
    if case == "no_server":
        product = _product(shop, provision_server_id=None)
    elif case == "missing_server":
        product = _product(shop, provision_server_id=999)
    elif case == "inactive_server":
        shop.db.update_panel_server(shop.server_id, is_active=0)
    elif case == "no_volume":
        product = _product(shop, auto_provision_volume_gb=None)
    elif case == "negative_volume":
        product = _product(shop, auto_provision_volume_gb=-1)
    with pytest.raises(ProvisionError) as exc:
        _provision(shop, product=product)
    assert str(exc.value) == expected
    assert shop.panel.servers == []
    assert shop.panel.calls == []
    assert _rows(shop.db_path) == []


# Case 3
def test_random_names_without_order(shop):
    result = _provision(shop, 2, user_id=BUYER)
    names = [item["username"] for item in result]
    assert len(result) == 2
    for item in result:
        assert list(item) == ["username", "subscription_url", "volume_gb", "duration_days"]
        assert re.fullmatch(RANDOM_NAME, item["username"])
        assert item["subscription_url"] == SUB + item["username"]
        assert item["volume_gb"] == VOLUME_GB
        assert item["duration_days"] == 30
    assert names[0] != names[1]
    assert shop.panel.calls == [("create_user", n, VOLUME_GB, 30) for n in names]
    assert shop.panel.servers == [shop.server_id]


# Case 4
def test_random_names_use_prefix(shop):
    shop.db.set_custom_config_prefix("  hunter ")
    result = _provision(shop, 1)
    assert re.fullmatch(PREFIXED_NAME, result[0]["username"])


# Case 5
@pytest.mark.parametrize("quantity,expected", [(1, ["ali"]), (3, ["ali_1", "ali_2", "ali_3"])], ids=["single", "three"])
def test_planned_names_from_order(shop, quantity, expected):
    shop.db.set_custom_config_prefix("  hunter ")
    order_id = _order(shop, "ali", quantity)
    result = _provision(shop, quantity, user_id=BUYER, order_id=order_id)
    assert [item["username"] for item in result] == expected
    assert _creates(shop.panel) == expected


# Case 6
def test_order_without_config_name_uses_random_names(shop):
    order_id = _order(shop, None, 1)
    result = _provision(shop, 1, user_id=BUYER, order_id=order_id)
    assert re.fullmatch(RANDOM_NAME, result[0]["username"])


# Case 7
@pytest.mark.parametrize("case", ["local_record", "panel_duplicate"], ids=["local_record", "panel_duplicate"])
def test_name_collision_tries_a_suffix(shop, case):
    if case == "local_record":
        shop.db.add_custom_config(OTHER_BUYER, shop.server_id, "ali", 10, 30, "https://old.example.invalid/ali")
    else:
        shop.panel.refuse = lambda name: name == "ali"
    order_id = _order(shop, "ali", 1)
    result = _provision(shop, 1, user_id=BUYER, order_id=order_id)
    alt = result[0]["username"]
    assert re.fullmatch(r"ali_[a-z0-9]{3}", alt)
    assert _creates(shop.panel) == ([alt] if case == "local_record" else ["ali", alt])


# Case 8
def test_name_exhaustion_rolls_back_earlier_units(shop):
    shop.panel.refuse = lambda name: name.startswith("ali_2")
    order_id = _order(shop, "ali", 3)
    with pytest.raises(ProvisionError) as exc:
        _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert str(exc.value) == NO_UNIQUE_NAME
    creates = _creates(shop.panel)
    assert len(creates) == 6
    assert creates[:2] == ["ali_1", "ali_2"]
    assert all(re.fullmatch(r"ali_2_[a-z0-9]{3}", name) for name in creates[2:])
    assert _deletes(shop.panel) == ["ali_1"]
    assert shop.panel.calls[-1] == ("delete_user", "ali_1")
    assert shop.panel.users == {}
    assert _rows(shop.db_path) == []


# Case 9
def test_nothing_saved_before_remote_create(shop):
    order_id = _order(shop, "ali", 3)
    _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert shop.panel.rows_at_create == [0, 0, 0]
    assert [row[1] for row in _rows(shop.db_path)] == ["ali_1", "ali_2", "ali_3"]
    assert shop.panel.calls[:3] == [("create_user", name, VOLUME_GB, 30) for name in ("ali_1", "ali_2", "ali_3")]


# Case 10
@pytest.mark.parametrize("case", ["first_saved", "first_unsaved"], ids=["first_saved", "first_unsaved"])
def test_repeat_call_creates_a_second_identity(shop, monkeypatch, case):
    order_id = _order(shop, "ali", 1)
    if case == "first_unsaved":
        _fail_on_calls(monkeypatch, shop.db, "add_custom_config", {1}, sqlite3.OperationalError(DB_LOCKED))
    first = _provision(shop, 1, user_id=BUYER, order_id=order_id)
    second = _provision(shop, 1, user_id=BUYER, order_id=order_id)
    alt = second[0]["username"]
    assert first[0]["username"] == "ali"
    assert re.fullmatch(r"ali_[a-z0-9]{3}", alt)
    assert set(shop.panel.users) == {"ali", alt}
    assert _deletes(shop.panel) == []
    if case == "first_saved":
        assert _creates(shop.panel) == ["ali", alt]
        rows = _rows(shop.db_path)
        assert [row[1] for row in rows] == ["ali", alt]
        assert all(row[3] == order_id for row in rows)
    else:
        assert _creates(shop.panel) == ["ali", "ali", alt]
        assert [row[1] for row in _rows(shop.db_path)] == [alt]


# Case 11
def test_panel_error_rolls_back_earlier_units_only(shop):
    shop.panel.create_errors = {3: PanelError("synthetic timeout")}
    order_id = _order(shop, "ali", 3)
    with pytest.raises(ProvisionError) as exc:
        _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert str(exc.value) == PROVISION_FAILED
    assert isinstance(exc.value.__context__, PanelError)
    assert shop.panel.calls == [
        ("create_user", "ali_1", 50, 30), ("create_user", "ali_2", 50, 30),
        ("create_user", "ali_3", 50, 30), ("delete_user", "ali_1"), ("delete_user", "ali_2"),
    ]
    assert shop.panel.users == {"ali_3": (50, 30)}
    assert _rows(shop.db_path) == []


# Case 12
@pytest.mark.parametrize("error", [PanelError("synthetic delete failure"), RuntimeError("synthetic delete failure")], ids=["panel_error", "runtime_error"])
def test_rollback_ignores_delete_errors(shop, error):
    shop.panel.create_errors = {3: PanelError("synthetic timeout")}
    shop.panel.delete_errors = {"ali_1": error}
    order_id = _order(shop, "ali", 3)
    with pytest.raises(ProvisionError) as exc:
        _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert str(exc.value) == PROVISION_FAILED
    assert _deletes(shop.panel) == ["ali_1", "ali_2"]
    assert set(shop.panel.users) == {"ali_1", "ali_3"}
    assert _rows(shop.db_path) == []


# Case 13
@pytest.mark.parametrize("error", [RuntimeError("synthetic"), TimeoutError("synthetic"), SimulatedCrash("direct.after_create_3")],
                         ids=["runtime_error", "timeout", "crash"])
def test_unexpected_error_skips_rollback(shop, error):
    shop.panel.create_errors = {3: error}
    order_id = _order(shop, "ali", 3)
    with pytest.raises(type(error)) as exc:
        _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert exc.value is error
    assert _deletes(shop.panel) == []
    assert set(shop.panel.users) == {"ali_1", "ali_2", "ali_3"}
    assert _rows(shop.db_path) == []


# Case 14
def test_database_error_during_name_check_skips_rollback(shop, monkeypatch):
    error = sqlite3.OperationalError(DB_LOCKED)
    _fail_on_calls(monkeypatch, shop.db, "is_custom_username_taken", {3}, error)
    order_id = _order(shop, "ali", 3)
    with pytest.raises(sqlite3.OperationalError) as exc:
        _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert exc.value is error
    assert _creates(shop.panel) == ["ali_1", "ali_2"]
    assert _deletes(shop.panel) == []
    assert set(shop.panel.users) == {"ali_1", "ali_2"}
    assert _rows(shop.db_path) == []


# Case 15
@pytest.mark.parametrize("case", ["limited", "unlimited"], ids=["limited", "unlimited"])
def test_saves_each_unit_after_all_creates(shop, case):
    product = shop.db.get_product(shop.product_id) if case == "limited" else _product(
        shop, duration_days=0, auto_provision_volume_gb=0
    )
    volume, days = (50, 30) if case == "limited" else (0, 0)
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    order_id = _order(shop, "ali", 3)
    _provision(shop, 3, product=product, user_id=BUYER, order_id=order_id)
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    rows = _rows(shop.db_path)
    expected = [(name, BUYER, order_id, shop.server_id, volume, days, SUB + name, "direct_product", "active")
                for name in ("ali_1", "ali_2", "ali_3")]
    assert [row[1:10] for row in rows] == expected
    if case == "limited":
        for row in rows:
            expires = datetime.fromisoformat(row[10])
            assert before + timedelta(days=30) <= expires <= after + timedelta(days=30)
        expected_history = [HISTORY_50_30]
    else:
        assert all(row[10] is None for row in rows)
        assert [(call[2], call[3]) for call in shop.panel.calls if call[0] == "create_user"] == [(0, 0)] * 3
        expected_history = [("purchase", "0 گیگ / 0 روز")]
    for row in rows:
        history = shop.db.get_custom_config_history(row[0])
        assert [(item["event_type"], item["detail"]) for item in history] == expected_history


# Case 16
def test_null_duration_defaults_to_30(shop):
    result = _provision(shop, 1, product=_product(shop, duration_days=None))
    assert shop.panel.calls[0][3] == 30
    assert result[0]["duration_days"] == 30


# Case 17
def test_no_user_id_saves_nothing(shop):
    order_id = _order(shop, "ali", 2)
    result = _provision(shop, 2, order_id=order_id)
    assert [item["username"] for item in result] == ["ali_1", "ali_2"]
    assert set(shop.panel.users) == {"ali_1", "ali_2"}
    assert _rows(shop.db_path) == []


# Case 18
@pytest.mark.parametrize("case", ["second_unit", "every_unit"], ids=["second_unit", "every_unit"])
def test_save_failure_still_returns_results(shop, monkeypatch, caplog, case):
    caplog.set_level(logging.ERROR, logger="direct_panel_provision")
    calls, failed = ({2}, ["ali_2"]) if case == "second_unit" else ({1, 2, 3}, ["ali_1", "ali_2", "ali_3"])
    _fail_on_calls(monkeypatch, shop.db, "add_custom_config", calls, sqlite3.OperationalError(DB_LOCKED))
    order_id = _order(shop, "ali", 3)
    result = _provision(shop, 3, user_id=BUYER, order_id=order_id)
    assert [item["username"] for item in result] == ["ali_1", "ali_2", "ali_3"]
    expected_rows = ["ali_1", "ali_3"] if case == "second_unit" else []
    assert [row[1] for row in _rows(shop.db_path)] == expected_rows
    assert _deletes(shop.panel) == []
    assert set(shop.panel.users) == {"ali_1", "ali_2", "ali_3"}
    records = [record for record in caplog.records if record.name == "direct_panel_provision"]
    assert [record.getMessage() for record in records] == [LOG_FAILED.format(BUYER, name, order_id) for name in failed]
    assert all(record.levelno == logging.ERROR and record.exc_info[0] is sqlite3.OperationalError for record in records)


# Case 19
def test_history_failure_after_insert_is_swallowed(shop, monkeypatch, caplog):
    caplog.set_level(logging.ERROR, logger="direct_panel_provision")
    _fail_on_calls(monkeypatch, shop.db, "add_custom_config_history", {1}, sqlite3.OperationalError(DB_LOCKED))
    order_id = _order(shop, "ali", 1)
    result = _provision(shop, 1, user_id=BUYER, order_id=order_id)
    assert [item["username"] for item in result] == ["ali"]
    rows = _rows(shop.db_path)
    assert len(rows) == 1 and rows[0][1] == "ali"
    assert shop.db.get_custom_config_history(rows[0][0]) == []
    records = [record for record in caplog.records if record.name == "direct_panel_provision"]
    assert len(records) == 1
    assert records[0].getMessage() == LOG_FAILED.format(BUYER, "ali", order_id)
