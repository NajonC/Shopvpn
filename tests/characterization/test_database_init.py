"""Characterize the SQLite foundations in ``database.py`` at commit e827855.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_database_init.py --network=deny``.
Every database is a SQLite file under ``tmp_path`` (SQLite 3.45.1).

Known unsafe behaviour (FR-083):
(a) `init_db` is not one transaction: `executescript` commits each `CREATE` at
    once, so a `users` table older than `referred_by` stops `init_db` at an
    index and leaves some tables created and no owner or settings, and a retry
    fails the same way (case 13);
(b) a different `owner_id` silently deletes every admin of an existing database
    (case 9);
(c) `replace_file` accepts any file, so the next query fails with "file is not a
    database" (case 15);
(d) two restores in the same second overwrite the first pre-restore copy
    (case 16);
(e) `replace_file` does not coordinate other connections: another open
    connection keeps reading the old data and, when it closes, writes the old
    database back over the restored file (case 18).
"""

import datetime
import logging
import sqlite3
import threading
import time

import pytest

import database


# Helpers


def _db(tmp_path, name="main.db"):
    return database.Database(str(tmp_path / name))


def _raw(path):
    return sqlite3.connect(str(path))


def _tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def _columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _schema(conn):
    return [tuple(r) for r in conn.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name")]


def _make_upload(path, value):
    conn = _raw(path)
    try:
        conn.execute("CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO settings (key, value) VALUES ('shop_name', ?)", (value,))
        conn.commit()
    finally:
        conn.close()


class _FrozenDatetime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return datetime.datetime(2026, 1, 2, 3, 4, 5)


PRE = "pre_restore_20260102_030405.db"

LEGACY_SCRIPT = """
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER UNIQUE NOT NULL, username TEXT, first_name TEXT, referred_by INTEGER);
INSERT INTO users (telegram_id, username, first_name) VALUES (777, 'legacy_user', 'Legacy');
CREATE TABLE admins (telegram_id INTEGER PRIMARY KEY);
INSERT INTO admins VALUES (1001);
INSERT INTO admins VALUES (1002);
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
INSERT INTO settings VALUES ('btn_my_orders', 'OLD');
INSERT INTO settings VALUES ('shop_name', 'Kept');
CREATE TABLE web_admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'admin', is_active INTEGER DEFAULT 1, created_at TEXT, last_login TEXT);
INSERT INTO web_admins (username, password_hash, role) VALUES ('w_mid', 'h', 'mid'), ('w_x', 'h', 'weird'), ('w_owner', 'h', 'owner');
CREATE TABLE reseller_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, status TEXT);
INSERT INTO reseller_requests (user_id, status) VALUES (1, 'pending'), (2, ''), (3, NULL), (4, 'approved');
"""

OLD_USERS_SCRIPT = """
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER UNIQUE NOT NULL, username TEXT, first_name TEXT);
INSERT INTO users (telegram_id) VALUES (9);
"""

EXTRA_KEYS = {"_migrated_btn_my_orders_rename", "reseller_tiers_four_level_v2", "reseller_tiers_menu_v2"}


# Case 1
def test_connect_pragmas(tmp_path):
    db = _db(tmp_path)
    try:
        with db._get_conn() as conn:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
            assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
            assert conn.execute("PRAGMA synchronous").fetchone()[0] == 1
            assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 4000
            assert isinstance(conn.execute("SELECT 1 AS a").fetchone(), sqlite3.Row)
            # The -wal file appears with the first write, not when WAL mode is set.
            conn.execute("CREATE TABLE t (x INTEGER)")
        assert (tmp_path / "main.db-wal").exists()
    finally:
        db.close()


# Case 2
def test_connection_usable_from_another_thread(tmp_path):
    db = _db(tmp_path)
    try:
        with db._get_conn() as conn:
            assert conn.execute("SELECT 1").fetchone()[0] == 1
        out = []
        exc = []

        def run():
            try:
                with db._get_conn() as c:
                    out.append(c.execute("SELECT 2").fetchone()[0])
            except Exception as e:
                exc.append(e)

        t = threading.Thread(target=run)
        t.start()
        t.join()
        assert out == [2]
        assert not exc
    finally:
        db.close()


# Case 3
def test_get_conn_reuses_one_connection(tmp_path):
    db = _db(tmp_path)
    try:
        assert db._conn is None
        with db._get_conn() as c1:
            pass
        with db._get_conn() as c2:
            pass
        assert c1 is c2
        assert c1 is db._conn
    finally:
        db.close()


# Case 4
def test_get_conn_commits_on_exit(tmp_path):
    db = _db(tmp_path)
    try:
        with db._get_conn() as conn:
            conn.execute("CREATE TABLE t (x INTEGER)")
            conn.execute("INSERT INTO t VALUES (1)")
        raw = _raw(tmp_path / "main.db")
        try:
            assert raw.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
        finally:
            raw.close()
    finally:
        db.close()


# Case 5
def test_get_conn_rolls_back_and_reraises(tmp_path):
    db = _db(tmp_path)
    try:
        with db._get_conn() as conn:
            conn.execute("CREATE TABLE t (x INTEGER)")
        kept = db._conn
        with pytest.raises(RuntimeError, match="boom"):
            with db._get_conn() as conn:
                conn.execute("INSERT INTO t VALUES (2)")
                raise RuntimeError("boom")
        raw = _raw(tmp_path / "main.db")
        try:
            assert raw.execute("SELECT COUNT(*) FROM t WHERE x = 2").fetchone()[0] == 0
        finally:
            raw.close()
        assert db._conn is kept
    finally:
        db.close()


# Case 6
def test_busy_timeout_is_four_seconds(tmp_path):
    db = _db(tmp_path)
    try:
        with db._get_conn() as conn:
            conn.execute("CREATE TABLE t (x INTEGER)")
        path = str(tmp_path / "main.db")
        raw = sqlite3.connect(path, timeout=0, isolation_level=None)
        try:
            raw.execute("BEGIN IMMEDIATE")
            t0 = time.monotonic()
            with pytest.raises(sqlite3.OperationalError, match="database is locked"):
                with db._get_conn() as conn:
                    conn.execute("INSERT INTO t VALUES (1)")
            elapsed = time.monotonic() - t0
            assert 3.5 <= elapsed < 10
        finally:
            try:
                raw.rollback()
            except Exception:
                pass
            raw.close()
    finally:
        db.close()


# Case 7
def test_init_db_fresh_schema(tmp_path):
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        with db._get_conn() as conn:
            admins = conn.execute("SELECT telegram_id, role FROM admins").fetchall()
            assert [tuple(r) for r in admins] == [(1001, "owner")]
            assert _columns(conn, "admins") == ["telegram_id", "role"]
            assert {
                "users",
                "orders",
                "configs",
                "custom_configs",
                "settings",
                "admins",
                "web_admins",
                "reseller_bots",
                "pending_db_purges",
                "temp_messages",
            } <= _tables(conn)
            setting_rows = conn.execute("SELECT key FROM settings").fetchall()
            assert {r[0] for r in setting_rows} == set(database.DEFAULT_SETTINGS) | EXTRA_KEYS
            tiers = conn.execute("SELECT code FROM reseller_tiers ORDER BY code").fetchall()
            assert [r[0] for r in tiers] == ["bronze", "gold", "silver", "vip"]
            assert conn.execute("SELECT COUNT(*) FROM custom_config_products").fetchone()[0] == 0
            assert conn.execute("SELECT COUNT(*) FROM test_config_plans").fetchone()[0] == 0
            assert _columns(conn, "web_admins")[-1] == "permissions"
            assert any(r[1] == "idx_users_owner_reseller_id" and r[0] == "index" for r in _schema(conn))
            marker = conn.execute("SELECT value FROM settings WHERE key='_migrated_btn_my_orders_rename'").fetchone()
            assert marker is not None and marker[0] == "1"
    finally:
        db.close()


# Case 8
def test_init_db_is_repeatable(tmp_path):
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        db.set_setting("welcome_text", "Mine")
        with db._get_conn() as conn:
            conn.execute("INSERT INTO users (telegram_id) VALUES (5)")
            before = _schema(conn)
            settings_count = conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
        db.init_db(1001)
        with db._get_conn() as conn:
            assert _schema(conn) == before
            assert conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0] == settings_count
            assert settings_count == len(database.DEFAULT_SETTINGS) + 3
            assert conn.execute("SELECT value FROM settings WHERE key='welcome_text'").fetchone()[0] == "Mine"
            users = conn.execute("SELECT telegram_id FROM users").fetchall()
            assert [tuple(r) for r in users] == [(5,)]
            admins = conn.execute("SELECT telegram_id, role FROM admins").fetchall()
            assert [tuple(r) for r in admins] == [(1001, "owner")]
        assert db.get_setting("welcome_text") == "Mine"
    finally:
        db.close()


# Case 9
def test_init_db_new_owner_rebuilds_admins(tmp_path, caplog):
    caplog.set_level(logging.WARNING, logger="database")
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        with db._get_conn() as conn:
            conn.execute("INSERT INTO admins (telegram_id, role) VALUES (1002, 'admin')")
            conn.execute("INSERT INTO users (telegram_id) VALUES (5)")
        db.init_db(2002)
        with db._get_conn() as conn:
            admins = conn.execute("SELECT telegram_id, role FROM admins").fetchall()
            assert [tuple(r) for r in admins] == [(2002, "owner")]
            users = conn.execute("SELECT telegram_id FROM users").fetchall()
            assert [tuple(r) for r in users] == [(5,)]
        records = [r for r in caplog.records if r.name == "database" and r.levelno == logging.WARNING]
        assert len(records) == 1
        assert records[0].args == (1001, 2002)
    finally:
        db.close()


# Case 10
def test_init_db_same_owner_keeps_admins(tmp_path):
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        with db._get_conn() as conn:
            conn.execute("INSERT INTO admins (telegram_id, role) VALUES (1002, 'admin')")
        db.init_db(1001)
        with db._get_conn() as conn:
            admins = conn.execute("SELECT telegram_id, role FROM admins ORDER BY telegram_id").fetchall()
            assert [tuple(r) for r in admins] == [(1001, "owner"), (1002, "admin")]
    finally:
        db.close()


# Case 11
def test_migrate_columns_upgrades_legacy_schema(tmp_path):
    path = tmp_path / "main.db"
    raw = _raw(path)
    try:
        raw.executescript(LEGACY_SCRIPT)
        raw.commit()
    finally:
        raw.close()

    db = _db(tmp_path)
    try:
        db.init_db(1001)
        with db._get_conn() as conn:
            user = conn.execute("SELECT * FROM users WHERE telegram_id = 777").fetchone()
            assert isinstance(user, sqlite3.Row)
            assert user["telegram_id"] == 777
            assert user["username"] == "legacy_user"
            assert user["first_name"] == "Legacy"
            assert user["owner_reseller_id"] is None
            assert user["referral_credit"] == 0
            assert user["reseller_supply_model"] == "volume_credit"
            assert user["is_reseller"] == 0
            assert user["force_join_exempt"] == 0
            assert "acquisition_source" in _columns(conn, "users")

            admins = conn.execute("SELECT telegram_id, role FROM admins ORDER BY telegram_id").fetchall()
            assert [tuple(r) for r in admins] == [(1001, "owner"), (1002, "admin")]

            btn_val = conn.execute("SELECT value FROM settings WHERE key='btn_my_orders'").fetchone()[0]
            assert btn_val == database.DEFAULT_SETTINGS["btn_my_orders"]
            assert conn.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0] == "Kept"
            assert conn.execute("SELECT value FROM settings WHERE key='_migrated_btn_my_orders_rename'").fetchone()[0] == "1"

            web_admins = conn.execute("SELECT username, role, permissions FROM web_admins ORDER BY id").fetchall()
            assert [tuple(r) for r in web_admins] == [
                ("w_mid", "mid", '["orders", "users", "tickets", "broadcast"]'),
                ("w_x", "weird", "[]"),
                (
                    "w_owner",
                    "owner",
                    '["orders", "users", "catalog", "discounts", "tickets", "broadcast", "resellers", "panels", "system", "settings", "backup"]',
                ),
            ]

            reseller_reqs = conn.execute(
                "SELECT id, status, volume_gb, supply_model FROM reseller_requests ORDER BY id"
            ).fetchall()
            assert [tuple(r) for r in reseller_reqs] == [
                (1, "pending_review", 0, "volume_credit"),
                (2, "pending_review", 0, "volume_credit"),
                (3, "pending_review", 0, "volume_credit"),
                (4, "approved", 0, "volume_credit"),
            ]

        db.set_setting("btn_my_orders", "ADMIN")
        db.init_db(1001)
        assert db.get_setting("btn_my_orders") == "ADMIN"
    finally:
        db.close()


# Case 12
def test_migrate_columns_twice_changes_nothing(tmp_path):
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        with db._get_conn() as conn:
            before = _schema(conn)
            db._migrate_columns(conn)
            db._migrate_columns(conn)
            assert _schema(conn) == before
    finally:
        db.close()


# Case 13
def test_init_db_fails_partway_on_users_without_referred_by(tmp_path):
    path = tmp_path / "main.db"
    raw = _raw(path)
    try:
        raw.executescript(OLD_USERS_SCRIPT)
        raw.commit()
    finally:
        raw.close()

    db = _db(tmp_path)
    try:
        for _ in range(2):
            with pytest.raises(sqlite3.OperationalError, match="no such column: referred_by"):
                db.init_db(1001)
    finally:
        db.close()

    raw = _raw(path)
    try:
        assert _columns(raw, "users") == ["id", "telegram_id", "username", "first_name"]
        assert raw.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        tables = _tables(raw)
        assert {"admins", "settings", "orders", "reseller_bots", "pending_db_purges"} <= tables
        assert "web_admins" not in tables
        assert "temp_messages" not in tables
        assert raw.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0
        assert raw.execute("SELECT COUNT(*) FROM settings").fetchone()[0] == 0
        assert _columns(raw, "admins") == ["telegram_id"]
    finally:
        raw.close()


# Case 14
def test_replace_file_swaps_file_and_keeps_pre_restore_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "datetime", _FrozenDatetime)
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        db.set_setting("shop_name", "Before")
        assert db.get_setting("shop_name") == "Before"
        old = db._conn
        upload_path = tmp_path / "upload.db"
        _make_upload(upload_path, "Uploaded")
        ret = db.replace_file(str(upload_path))
        assert ret == str(tmp_path / "backups" / PRE)
        assert db._conn is None
        assert db._settings_cache is None
        assert db._admin_cache is None
        assert (tmp_path / "main.db").read_bytes() == upload_path.read_bytes()
        assert not (tmp_path / "main.db-wal").exists()
        assert not (tmp_path / "main.db-shm").exists()
        with pytest.raises(sqlite3.ProgrammingError):
            old.execute("SELECT 1")
        pre_conn = _raw(ret)
        try:
            assert pre_conn.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0] == "Before"
            adm = pre_conn.execute("SELECT telegram_id, role FROM admins").fetchall()
            assert [tuple(r) for r in adm] == [(1001, "owner")]
        finally:
            pre_conn.close()
        assert db.get_setting("shop_name") == "Uploaded"
    finally:
        db.close()


# Case 15
def test_replace_file_accepts_any_file(tmp_path):
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        bad = tmp_path / "bad.db"
        bad.write_text("not a database")
        ret = db.replace_file(str(bad))
        assert (tmp_path / "backups" / ret.split("/")[-1]).exists()
        with pytest.raises(sqlite3.DatabaseError, match="file is not a database"):
            db.get_setting("shop_name")
        assert db._conn is None
    finally:
        db.close()


# Case 16
def test_replace_file_same_second_overwrites_pre_restore_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "datetime", _FrozenDatetime)
    db = _db(tmp_path)
    try:
        db.init_db(1001)
        db.set_setting("shop_name", "Before")
        u1 = tmp_path / "u1.db"
        u2 = tmp_path / "u2.db"
        _make_upload(u1, "Uploaded")
        _make_upload(u2, "Second")
        r1 = db.replace_file(str(u1))
        r2 = db.replace_file(str(u2))
        assert r1 == r2
        assert sorted(p.name for p in (tmp_path / "backups").iterdir()) == [PRE]
        conn = _raw(r1)
        try:
            assert conn.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0] == "Uploaded"
        finally:
            conn.close()
        assert db.get_setting("shop_name") == "Second"
    finally:
        db.close()


# Case 17
def test_replace_file_without_current_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "datetime", _FrozenDatetime)
    (tmp_path / "sub").mkdir()
    db = database.Database(str(tmp_path / "sub" / "none.db"))
    try:
        upload = tmp_path / "upload.db"
        _make_upload(upload, "Uploaded")
        ret = db.replace_file(str(upload))
        assert ret == str(tmp_path / "sub" / "backups" / PRE)
        assert not (tmp_path / "sub" / "backups" / PRE).exists()
        assert (tmp_path / "sub" / "none.db").read_bytes() == upload.read_bytes()
    finally:
        db.close()


# Case 18
def test_replace_file_undone_by_another_open_connection(tmp_path):
    db = _db(tmp_path)
    other = None
    try:
        db.init_db(1001)
        other = _db(tmp_path)
        other.set_setting("shop_name", "OtherWrote")
        upload = tmp_path / "upload.db"
        _make_upload(upload, "Uploaded")
        ret = db.replace_file(str(upload))

        pre_conn = _raw(ret)
        try:
            assert pre_conn.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0] == "OtherWrote"
        finally:
            pre_conn.close()

        with other._get_conn() as c:
            val = c.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0]
            assert val == "OtherWrote"

        # Do not call any db method between replace_file and other.close();
        # that open waits 30 seconds and fails with "database is locked".
        other.close()

        assert db.get_setting("shop_name") == "OtherWrote"
        raw = _raw(tmp_path / "main.db")
        try:
            assert "admins" in _tables(raw)
        finally:
            raw.close()
    finally:
        if other is not None:
            other.close()
        db.close()
