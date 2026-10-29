"""Characterize destructive operations in ``database.py`` and ``bot_manager.py`` at commit 0b64247.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_destructive_ops.py --network=deny``.
Every database is a SQLite file under ``tmp_path``; no panel or Telegram is contacted.

Known unsafe behaviour (FR-075; FR-083): (a) ``factory_reset`` has no guard: it erases wallets, panels, customer services and their history, and keeps reseller registrations, queued purges and the deleted staff's mobile tokens (case 1); (b) it turns foreign keys back on inside its transaction, so the connection keeps them off afterwards, even after a rolled-back reset, and accepts a service for a panel that does not exist (cases 2, 4); (c) ``delete_panel_server`` refuses only on customer services; ``force=True`` deletes them with no remote cleanup, keeps their history and the users' panel reference, and test plans and products go without asking (cases 5–7); (d) a tier switch deletes the tenant database files at once, while a connection is still writing to them, queues only the files it could not remove, and keeps the wallet and credit log (case 9); (e) ownership transfer moves only the reseller flags, the registration and the tenant owner role; the tier, inline link, product credit and customers stay with the old owner, and the tenant update runs after the main commit, so a failure there is only logged (cases 11, 12); (f) the deferred purge matches the token, not the path: it deletes the database of another running, active tenant at that path, and a removal that fails stays queued (case 13).
"""

import asyncio
import contextlib
import logging
import os
import sqlite3

import pytest

import bot_manager
import database


OWNER = 9001
NOT_SQLITE = b"not a database" * 20  # 280 bytes
NO_OWNER = "این دیتابیس هیچ owner ثبت\u200cشده\u200cای ندارد؛ factory_reset ناممکن است."


def panel_in_use(count):
    return f"این پنل {count} کانفیگ شخصی ثبت\u200cشده دارد و به همین دلیل قابل حذف نیست."


USER_COLS = "is_reseller, reseller_credit_gb, reseller_supply_model, fixed_product_main_id, reseller_panel_id, reseller_tier, inline_reseller_enabled, referral_credit"


def _main(path):
    db = database.Database(str(path))
    db.init_db(OWNER)
    return db


def _rows(db, sql, params=()):
    with db._get_conn() as conn:
        return [tuple(r) for r in conn.execute(sql, params)]


def _count(db, table):
    return _rows(db, f"SELECT COUNT(*) FROM {table}")[0][0]


def _exec(db, sql, params=()):
    with db._get_conn() as conn:
        conn.execute(sql, params)


def _raw_rows(path, sql):
    conn = sqlite3.connect(str(path))
    try:
        return [tuple(r) for r in conn.execute(sql).fetchall()]
    finally:
        conn.close()


def _panel(db, n):
    return db.add_panel_server(f"P{n}", "3xui", f"https://p{n}.example.invalid", "api-user", "synthetic-pass")


def _config(db, panel_id, n):
    return db.add_custom_config(5001, panel_id, f"cfg{n}", 10, 30, f"https://sub.example.invalid/{n}")


def _user(db, tg_id):
    return _rows(db, f"SELECT {USER_COLS} FROM users WHERE telegram_id=?", (tg_id,))[0]


# Case 1
def test_factory_reset_erases_shop_and_money_records(tmp_path):
    db = _main(tmp_path / "main.db")
    try:
        db.add_admin(9002, "support")
        db.create_web_admin("owner", "synthetic-hash-1", role="owner")
        db.create_web_admin("staff", "synthetic-hash-2", role="admin")
        db.create_mobile_token(2, "phone", "synthetic-token-hash", "syn")
        db.add_or_update_user(5001, "u5001", "U")
        db.add_wallet_credit(5001, 120000)
        sid = _panel(db, 1)
        _config(db, sid, 1)
        _exec(db, "INSERT INTO reseller_credit_log (user_id, delta_gb, reason) VALUES (5001, 40, 'grant')")
        r1 = str(tmp_path / "r1.db")
        db.register_reseller_bot("1001:synthetic-r1", "r1bot", 5001, "R1", r1)
        db.queue_db_purge("1001:synthetic-r1", r1)
        db.set_setting("btn_buy", "Changed")
        db.set_setting("zz_custom", "v")
        assert db.get_setting("btn_buy") == "Changed"

        assert db.factory_reset() is None
        assert _rows(db, "SELECT telegram_id, role FROM admins") == [(9001, "owner")]
        assert _rows(db, "SELECT username, role FROM web_admins") == [("owner", "owner")]
        assert _rows(db, "SELECT admin_id, name FROM mobile_app_tokens") == [(2, "phone")]
        for table in ("users", "panel_servers", "custom_configs", "custom_config_history", "reseller_credit_log"):
            assert _count(db, table) == 0
        assert _rows(db, "SELECT id, bot_token FROM reseller_bots") == [(1, "1001:synthetic-r1")]
        assert _rows(db, "SELECT bot_token, db_path FROM pending_db_purges") == [("1001:synthetic-r1", r1)]
        assert _count(db, "reseller_tiers") == 4
        assert db.get_setting("btn_buy") == database.DEFAULT_SETTINGS["btn_buy"]
        assert db.get_setting("zz_custom") == ""
    finally:
        db.close()


# Case 2
def test_factory_reset_leaves_foreign_keys_off(tmp_path):
    db = _main(tmp_path / "main.db")
    fresh = None
    try:
        assert db._conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        db.factory_reset(owner_id=OWNER)
        assert db._conn.execute("PRAGMA foreign_keys").fetchone()[0] == 0
        assert db.add_custom_config(5001, 999, "orphan", 1, 1, "https://sub.example.invalid/o") == 1
        fresh = database.Database(db.db_path)
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
            fresh.add_custom_config(5001, 998, "orphan2", 1, 1, "https://sub.example.invalid/o2")
    finally:
        if fresh is not None:
            fresh.close()
        db.close()


# Case 3
def test_factory_reset_owner_resolution(tmp_path):
    db = _main(tmp_path / "main.db")
    db2 = None
    try:
        db.add_or_update_user(5001, "u5001", "U")
        _exec(db, "DELETE FROM admins")
        with pytest.raises(ValueError) as exc:
            db.factory_reset()
        assert str(exc.value) == NO_OWNER
        assert _count(db, "users") == 1
        assert db._conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1

        db2 = _main(tmp_path / "other.db")
        db2.add_admin(9002)
        db2.factory_reset(owner_id=7777)
        assert _rows(db2, "SELECT telegram_id, role FROM admins") == [(7777, "owner")]
    finally:
        if db2 is not None:
            db2.close()
        db.close()


# Case 4
def test_factory_reset_rolls_back_but_keeps_foreign_keys_off(tmp_path, monkeypatch):
    db = _main(tmp_path / "main.db")
    try:
        db.add_or_update_user(5001, "u5001", "U")
        _panel(db, 1)
        db.set_setting("btn_buy", "Changed")

        def boom(conn):
            raise RuntimeError("synthetic seed failure")

        monkeypatch.setattr(db, "_seed_default_reseller_tiers", boom)
        with pytest.raises(RuntimeError, match="synthetic seed failure"):
            db.factory_reset()
        assert _count(db, "users") == 1
        assert _count(db, "panel_servers") == 1
        assert _raw_rows(db.db_path, "SELECT value FROM settings WHERE key='btn_buy'") == [("Changed",)]
        assert db._conn.execute("PRAGMA foreign_keys").fetchone()[0] == 0
    finally:
        db.close()


# Case 5
def test_delete_panel_server_refuses_only_on_customer_services(tmp_path):
    db = _main(tmp_path / "main.db")
    try:
        db.add_or_update_user(5001, "u5001", "U")
        s1, s2 = _panel(db, 1), _panel(db, 2)
        _config(db, s1, 1)
        _config(db, s2, 2)
        db.create_test_config_plan("T", "test", s1, 1024, 24)
        db.create_custom_config_product("CP", s1)
        _exec(db, "UPDATE users SET reseller_panel_id=? WHERE telegram_id=5001", (s1,))
        with pytest.raises(ValueError) as exc:
            db.delete_panel_server(s1)
        assert str(exc.value) == panel_in_use(1)
        assert _rows(db, "SELECT id FROM panel_servers ORDER BY id") == [(1,), (2,)]
        assert _count(db, "custom_configs") == 2
        assert _count(db, "test_config_plans") == 1
        assert _count(db, "custom_config_products") == 1
    finally:
        db.close()


# Case 6
def test_delete_panel_server_force_erases_customer_services(tmp_path):
    db = _main(tmp_path / "main.db")
    try:
        db.add_or_update_user(5001, "u5001", "U")
        s1, s2 = _panel(db, 1), _panel(db, 2)
        _config(db, s1, 1)
        _config(db, s2, 2)
        db.create_test_config_plan("T", "test", s1, 1024, 24)
        db.create_custom_config_product("CP", s1)
        _exec(db, "UPDATE users SET reseller_panel_id=? WHERE telegram_id=5001", (s1,))
        assert db.delete_panel_server(s1, force=True) == 1
        assert _rows(db, "SELECT id FROM panel_servers ORDER BY id") == [(2,)]
        assert _rows(db, "SELECT id FROM custom_configs ORDER BY id") == [(2,)]
        assert _count(db, "test_config_plans") == 0
        assert _count(db, "custom_config_products") == 0
        assert _rows(db, "SELECT custom_config_id, event_type FROM custom_config_history ORDER BY id") == [(1, "purchase"), (2, "purchase")]
        assert _rows(db, "SELECT reseller_panel_id FROM users WHERE telegram_id=5001") == [(1,)]
    finally:
        db.close()


# Case 7
def test_delete_panel_server_drops_plans_without_force(tmp_path):
    db = _main(tmp_path / "main.db")
    try:
        s = _panel(db, 3)
        db.create_test_config_plan("T3", "test", s, 1024, 24)
        db.create_custom_config_product("CP3", s)
        assert db.delete_panel_server(s) == 0
        assert _count(db, "panel_servers") == 0
        assert _count(db, "test_config_plans") == 0
        assert _count(db, "custom_config_products") == 0
        assert db.delete_panel_server(424242) == 0
    finally:
        db.close()


# Case 8
def test_switch_agent_tier_without_change_keeps_everything(tmp_path):
    db = _main(tmp_path / "main.db")
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    try:
        for u in (5001, 5002, 5003, 5004, 5005):
            db.add_or_update_user(u, f"u{u}", "U")
        _exec(db, "UPDATE users SET reseller_tier='silver' WHERE telegram_id=5001")
        _exec(db, "UPDATE users SET is_reseller=1, reseller_supply_model='fixed_product' WHERE telegram_id=5002")
        _exec(db, "UPDATE users SET is_reseller=1 WHERE telegram_id=5003")
        _exec(db, "UPDATE users SET inline_reseller_enabled=1 WHERE telegram_id=5004")
        db.register_reseller_bot("1001:synthetic-r1", "r1bot", 5001, "R1", str(rd / "r1.db"))
        assert [db.get_agent_tier(u) for u in (5001, 5002, 5003, 5004, 5005, 424242)] == ["silver", "gold", "vip", "bronze", None, None]
        assert db.switch_agent_tier(5001, "silver") == {"changed": False, "previous": "silver"}
        assert db.switch_agent_tier(5005, "gold") == {"changed": False, "previous": None}
        assert db.switch_agent_tier(424242, "gold") == {"changed": False, "previous": None}
        assert _count(db, "reseller_bots") == 1
    finally:
        db.close()


# Case 9
def test_switch_agent_tier_wipes_tenant_files_at_once(tmp_path):
    db = _main(tmp_path / "main.db")
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    tenant = None
    try:
        for u in (5001, 5002, 6001):
            db.add_or_update_user(u, f"u{u}", "U")
        db.add_wallet_credit(5001, 50000)
        _exec(db, "UPDATE users SET is_reseller=1, reseller_credit_gb=40, reseller_tier='silver', inline_reseller_commission_percent=10, reseller_discount_percent=5, inline_reseller_enabled=1 WHERE telegram_id=5001")
        _exec(db, "UPDATE users SET owner_reseller_id=5001 WHERE telegram_id=6001")
        _exec(db, "INSERT INTO reseller_credit_log (user_id, delta_gb, reason) VALUES (5001, 40, 'grant')")
        _exec(db, "INSERT INTO reseller_product_credit (reseller_id, product_id, qty_remaining) VALUES (5001, 3, 7)")
        tok1, tok2 = "1001:synthetic-r1", "1002:synthetic-r2"
        db.register_reseller_bot(tok1, "r1bot", 5001, "R1", str(rd / "r1.db"))
        db.register_reseller_bot(tok2, "r2bot", 5001, "R2", str(rd / "r2dir"), has_live_bot=0)
        db.toggle_reseller_bot(2)
        db.register_reseller_bot("1003:synthetic-r3", "r3bot", 5002, "R3", str(rd / "r3.db"))
        tenant = database.Database(str(rd / "r1.db"))
        tenant.init_db(5001)
        (rd / "r1.db.fsm.sqlite3").write_text("x")
        (rd / "r2dir").mkdir()
        (rd / "r3.db").write_text("")
        assert (rd / "r1.db-wal").exists()

        assert db.switch_agent_tier(5001, "gold") == {"bots_removed": 2, "changed": True, "previous": "silver"}
        assert sorted(os.listdir(rd)) == ["r2dir", "r3.db"]
        assert _rows(db, "SELECT id, owner_telegram_id FROM reseller_bots") == [(3, 5002)]
        assert _rows(db, "SELECT bot_token, db_path FROM pending_db_purges") == [(tok2, str(rd / "r2dir"))]
        assert _rows(db, "SELECT is_reseller, reseller_credit_gb, reseller_tier, inline_reseller_commission_percent, reseller_discount_percent, inline_reseller_enabled, reseller_supply_model, referral_credit FROM users WHERE telegram_id=5001") == [(0, 0, None, None, None, 0, "volume_credit", 50000)]
        assert _count(db, "reseller_credit_log") == 1
        assert _count(db, "reseller_product_credit") == 0
        assert _rows(db, "SELECT owner_reseller_id FROM users WHERE telegram_id=6001") == [(None,)]
        assert db.get_agent_tier(5001) is None
        tenant.add_or_update_user(7002, "c7002", "C")
        assert sorted(os.listdir(rd)) == ["r2dir", "r3.db"]
    finally:
        if tenant is not None:
            tenant.close()
        db.close()


# Case 10
def test_transfer_missing_or_same_owner(tmp_path):
    db = _main(tmp_path / "main.db")
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    try:
        db.add_or_update_user(5001, "u5001", "U")
        _exec(db, "UPDATE users SET is_reseller=1 WHERE telegram_id=5001")
        b = db.register_reseller_bot("1001:synthetic-r1", "r1bot", 5001, "R1", str(rd / "r1.db"))
        assert db.transfer_reseller_ownership(99, 1) is False
        assert db.transfer_reseller_ownership(b, 5001, "Renamed") is True
        row = db.get_reseller_bot(b)
        assert (row["owner_telegram_id"], row["owner_name"]) == (5001, "Renamed")
        assert db.transfer_reseller_ownership(b, 5001) is True
        row = db.get_reseller_bot(b)
        assert (row["owner_telegram_id"], row["owner_name"]) == (5001, "Renamed")
        assert _rows(db, "SELECT is_reseller FROM users WHERE telegram_id=5001") == [(1,)]
        assert not (rd / "r1.db").exists()
    finally:
        db.close()


# Case 11
def test_transfer_moves_flags_registration_and_tenant_owner_only(tmp_path):
    db = _main(tmp_path / "main.db")
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    try:
        db.add_or_update_user(5001, "u5001", "U")
        db.add_or_update_user(6001, "u6001", "U")
        s1 = _panel(db, 1)
        _exec(db, "UPDATE users SET is_reseller=1, reseller_credit_gb=40, reseller_supply_model='fixed_product', fixed_product_main_id=3, reseller_panel_id=?, reseller_tier='gold', inline_reseller_enabled=1, referral_credit=700 WHERE telegram_id=5001", (s1,))
        _exec(db, "UPDATE users SET owner_reseller_id=5001 WHERE telegram_id=6001")
        _exec(db, "INSERT INTO reseller_product_credit (reseller_id, product_id, qty_remaining) VALUES (5001, 3, 7)")
        b = db.register_reseller_bot("1001:synthetic-r1", "r1bot", 5001, "R1", str(rd / "r1.db"))
        t = database.Database(str(rd / "r1.db"))
        t.init_db(5001)
        t.add_admin(5555)
        t.close()
        assert db.transfer_reseller_ownership(b, 5002, "New") is True
        assert _user(db, 5001) == (0, 0, "volume_credit", None, None, "gold", 1, 700)
        assert _user(db, 5002) == (1, 40, "fixed_product", 3, 1, None, 0, 0)
        row = db.get_reseller_bot(b)
        assert (row["owner_telegram_id"], row["owner_name"]) == (5002, "New")
        assert _rows(db, "SELECT reseller_id, qty_remaining FROM reseller_product_credit") == [(5001, 7)]
        assert _rows(db, "SELECT owner_reseller_id FROM users WHERE telegram_id=6001") == [(5001,)]
        assert _raw_rows(rd / "r1.db", "SELECT telegram_id, role FROM admins ORDER BY telegram_id") == [(5001, "admin"), (5002, "owner"), (5555, "admin")]
    finally:
        db.close()


# Case 12
def test_transfer_commits_main_then_tenant_best_effort(tmp_path, caplog):
    db = _main(tmp_path / "main.db")
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    try:
        caplog.set_level(logging.ERROR, logger="database")
        b2 = db.register_reseller_bot("1002:synthetic-r2", "r2bot", 5003, "R2", str(rd / "r2.db"))
        assert db.transfer_reseller_ownership(b2, 5004) is True
        assert not (rd / "r2.db").exists()
        assert db.get_reseller_bot(b2)["owner_telegram_id"] == 5004
        assert _user(db, 5004) == (0, 0, "volume_credit", None, None, None, 0, 0)
        assert not [r for r in caplog.records if r.name == "database" and r.levelno == logging.ERROR]

        (rd / "r3.db").write_bytes(NOT_SQLITE)
        b3 = db.register_reseller_bot("1003:synthetic-r3", "r3bot", 5005, "R3", str(rd / "r3.db"))
        assert db.transfer_reseller_ownership(b3, 5006) is True
        assert db.get_reseller_bot(b3)["owner_telegram_id"] == 5006
        assert (rd / "r3.db").read_bytes() == NOT_SQLITE
        records = [r for r in caplog.records if r.name == "database" and r.levelno == logging.ERROR]
        assert len(records) == 1
        assert records[0].args == (5006, b3)
        assert records[0].exc_info[0] is sqlite3.DatabaseError
    finally:
        db.close()


# Case 13
def test_deferred_purge_matches_token_not_path(tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.ERROR, logger="bot_manager")
    main_db = _main(tmp_path / "main.db")
    shared = tmp_path / "shared.db"
    d = tmp_path / "dir.db"
    d.mkdir()
    tx, ty, tz = "200001:tenant-x-deleted", "200002:tenant-y-synthetic", "200003:tenant-z-deleted"
    yid = main_db.register_reseller_bot(ty, "ybot", 5002, "Y", str(shared))
    y = database.Database(str(shared))
    try:
        y.init_db(5002)
        y.set_setting("miniapp_tenant_id", str(yid))
    finally:
        y.close()
    main_db.queue_db_purge(tx, str(shared))
    main_db.queue_db_purge(tz, str(d))

    real = main_db.list_reseller_bots
    calls = []

    def once(active_only=False):
        calls.append(active_only)
        if len(calls) >= 2:
            raise asyncio.CancelledError
        return real(active_only=active_only)

    monkeypatch.setattr(main_db, "list_reseller_bots", once)

    async def scenario():
        m = bot_manager.BotManager()
        m.instances[ty] = {"menu_checked": True}
        task = asyncio.create_task(m.reconcile_resellers_loop(main_db, "1:synthetic-main", interval=0))
        with contextlib.suppress(asyncio.CancelledError):
            await task
        assert task.cancelled()
        assert m.instances == {ty: {"menu_checked": True}}

    try:
        asyncio.run(scenario())
        assert len(calls) == 2
        assert not shared.exists()
        assert sorted(n for n in os.listdir(tmp_path) if n.startswith("shared")) == ["shared.db-shm", "shared.db-wal"]
        assert d.is_dir()
        assert [(r["bot_token"], r["db_path"]) for r in main_db.list_pending_db_purges()] == [(tz, str(d))]
        assert [(r["bot_token"], r["is_active"]) for r in real()] == [(ty, 1)]
        records = [r for r in caplog.records if r.name == "bot_manager" and r.levelno == logging.ERROR]
        assert len(records) == 1
        assert records[0].args == (str(d),)
        assert records[0].exc_info[0] is IsADirectoryError
    finally:
        main_db.close()
