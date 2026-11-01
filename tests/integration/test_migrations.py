"""Integration tests for the composite migration runner (T034a, the first part of
T034, written before T035; FR-083; constitution IV; contracts/operations.md
"Additive upgrade"). Reproduce with `.venv/bin/python -m pytest
tests/integration/test_migrations.py --network=deny`. SQLite is real; every
installation is synthetic and built under ``tmp_path``.

T034 is split by the task it tests: T034a pins the runner T035 builds; later
parts add the data-model DDL checks (T036-T040) and the ``users.test_used``
reconciliation (T041) to this file.

Each installation is a main-store file whose ``reseller_bots`` registry names
three reseller files: tenant 7 (active, relative ``reseller_7.db``), tenant 8
(inactive, historical name ``reseller_8_level2.db``, absolute path) and tenant 9
(no live bot, ``no-bot:`` token, absolute path), plus FSM files for main and the
tenants that ran a bot. It comes in three shapes: ``historical`` (an older
legacy release, built from raw SQL), ``current`` (pre-feature, built by legacy
``Database.init_db``) and ``feature`` (``current`` migrated once, with
composite rows added).

The interface these tests pin, which T035 builds in ``composite/migrations.py``:

- ``SCHEMA_VERSION``: the composite schema version this code writes, an int >= 1.
- ``AuthorizedPaths(main, tenants, fsm, pre_upgrade_dir, base_dir)``, a frozen
  dataclass of path-likes: the main-store file; the reseller files the operator
  authorizes; the FSM files of the set; an existing empty directory for this
  run's pre-upgrade copies; and the directory a relative
  ``reseller_bots.db_path`` resolves against (legacy ``config.resolve_db_path``
  uses ``config.BASE_DIR``). Files are compared after ``os.path.realpath``.
- ``inspect_schema(path) -> SchemaInfo(version, supported)``: ``version`` is the
  file's highest ``composite_schema_versions.version``, or 0 when it has no such
  table; ``supported`` is ``version <= SCHEMA_VERSION``. It changes nothing.
- ``issuance_enabled(main_path) -> bool``. ``migrate`` never enables issuance.
- ``migrate(paths, expected_release, *, crash=None) -> MigrationReport``:
  1. Before changing or copying anything: ``pre_upgrade_dir`` must be an
     existing empty directory, else ``MigrationError``. Every ``reseller_bots``
     row of the main file (active, inactive or without a live bot) is a member;
     its ``db_path`` is used as is when absolute, else joined to ``base_dir``.
     Two rows naming the same file, a row whose file is missing or not in
     ``tenants``, and a ``tenants`` file that no row names raise
     ``RegistryError``. A member above ``SCHEMA_VERSION`` raises
     ``UnsupportedSchema`` (``path``, ``version``).
  2. Copies every member and every FSM file into ``pre_upgrade_dir`` with
     SQLite's online backup, and never changes or removes those copies.
  3. Migrates main, then the reseller files in ascending ``reseller_bots.id``.
     Each member below ``SCHEMA_VERSION`` changes in one explicit transaction on
     its own connection: its changes, ``crash("before commit")``, ``COMMIT``,
     ``crash("after commit")``. A member already at ``SCHEMA_VERSION`` is left
     as it is and reaches no crash point. FSM files are never changed.
  4. An ``Exception`` while migrating a member, including one raised by
     ``crash``, rolls that member back and stops the run: ``MigrationFailed``
     is raised with ``report``. Anything else (``SimulatedCrash``) propagates
     unchanged.
- Main gets ``composite_schema_versions(version INTEGER PRIMARY KEY, release
  TEXT NOT NULL, applied_at INTEGER NOT NULL)``, one row per applied version
  1..``SCHEMA_VERSION`` with ``expected_release`` and the UTC epoch
  milliseconds; and, on ``products``, ``test_config_plans`` and ``orders``,
  ``service_kind`` (``NOT NULL DEFAULT 'legacy'``, only ``'legacy'`` or
  ``'composite'``) and ``composite_ref`` (optional, unique when set). No other
  legacy table gains or loses a column, row or index.
- Each reseller file gets ``composite_schema_versions`` and ``service_kind``
  (only ``'legacy'``) on the same three tables: no other table, no
  ``composite_ref``.
- ``MigrationReport(outcomes)``: one ``MemberOutcome(path, role, tenant_id,
  from_version, to_version, status)`` per member, main first, then reseller
  files by id. ``path`` is the realpath string, ``role`` ``"main"`` or
  ``"reseller"``, ``tenant_id`` the registry id (``None`` for main), ``status``
  ``"migrated"``, ``"unchanged"``, ``"failed"`` or ``"not_attempted"``;
  ``to_version`` equals ``from_version`` unless ``"migrated"``.
- Errors: ``MigrationError`` and its subclasses ``RegistryError``,
  ``UnsupportedSchema`` and ``MigrationFailed``.

T034a's tests pass since T035, T034b's since T036 and T037, T034c's since T038 and T034d's since T039. T034e's tests check the data-model §10 lifecycle-work, drift and discrepancy tables and T034f1's (the last section) its batch tables; both fail until T040 adds them.
"""

from collections import Counter
from contextlib import closing
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import sqlite3
import time

import pytest

import composite.migrations as migrations
import database
from tests._harness.crash import CrashPlan, SimulatedCrash


RELEASE = "synthetic-release-1"
OTHER_RELEASE = "synthetic-release-2"
SHAPES = ("historical", "current", "feature")
KIND_TABLES = ("products", "test_config_plans", "orders")

MAIN_OWNER = 1001
MAIN_ADMIN = 1002
# (id, bot_token, bot_username, owner_telegram_id, is_active, has_live_bot)
TENANTS = (
    (7, "synthetic-bot-token-7", "shop7_bot", 7001, 1, 1),
    (8, "synthetic-bot-token-8", "shop8_bot", 8001, 0, 1),
    (9, "no-bot:9:9001", None, 9001, 1, 0),
)
TENANT_OWNERS = {tid: owner for tid, _, _, owner, _, _ in TENANTS}
# (telegram_id, username, test_used, referral_credit)
USERS = ((50001, "alice", 1, 12000), (50002, "bob", 0, 0))

REF_PRODUCT = "6f1c2a52-0d55-4c55-9a4e-000000000001"
REF_TEST_PLAN = "6f1c2a52-0d55-4c55-9a4e-000000000002"
REF_ORDER = "6f1c2a52-0d55-4c55-9a4e-000000000003"

HISTORICAL_SCRIPT = """
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER UNIQUE NOT NULL, username TEXT, first_name TEXT, is_blocked INTEGER DEFAULT 0, test_used INTEGER DEFAULT 0, referred_by INTEGER, referral_credit INTEGER DEFAULT 0, joined_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE admins (telegram_id INTEGER PRIMARY KEY);
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, is_active INTEGER DEFAULT 1, sort_order INTEGER DEFAULT 0);
CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER NOT NULL, name TEXT NOT NULL, price INTEGER NOT NULL, description TEXT DEFAULT '', is_active INTEGER DEFAULT 1, payment_methods TEXT, FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE);
CREATE TABLE panel_servers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, panel_type TEXT NOT NULL DEFAULT 'pasarguard', api_url TEXT NOT NULL, default_group TEXT, is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE test_config_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, name_prefix TEXT NOT NULL DEFAULT 'test', panel_server_id INTEGER NOT NULL REFERENCES panel_servers(id), volume_mb INTEGER NOT NULL DEFAULT 1024, duration_hours INTEGER NOT NULL DEFAULT 24, is_active INTEGER DEFAULT 1, sort_order INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX idx_test_plans_active ON test_config_plans(is_active);
CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, status TEXT DEFAULT 'pending', receipt_file_id TEXT, config_id INTEGER, admin_chat_id INTEGER, admin_message_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE TABLE reseller_bots (id INTEGER PRIMARY KEY AUTOINCREMENT, bot_token TEXT UNIQUE NOT NULL, bot_username TEXT, owner_telegram_id INTEGER NOT NULL, owner_name TEXT, db_path TEXT NOT NULL, is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""

FSM_DDL = """
CREATE TABLE fsm_storage (
    bot_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    thread_id INTEGER,
    business_connection_id TEXT,
    destiny TEXT NOT NULL DEFAULT 'default',
    state TEXT,
    data TEXT,
    PRIMARY KEY (bot_id, chat_id, user_id, thread_id, business_connection_id, destiny)
)
"""

VERSIONS_DDL = (
    "CREATE TABLE composite_schema_versions "
    "(version INTEGER PRIMARY KEY, release TEXT NOT NULL, applied_at INTEGER NOT NULL)"
)


# Helpers


def _now_ms():
    return time.time_ns() // 1_000_000


def _real(path):
    return os.path.realpath(path)


def _fresh_dir(tmp_path, name):
    path = tmp_path / name
    path.mkdir()
    return path


def _dump(path):
    with closing(sqlite3.connect(path)) as conn:
        return tuple(conn.iterdump())


def _tables(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return {r[0] for r in rows}


def _columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def _snapshot(path):
    """Columns, rows by rowid, and index/trigger/view SQL of every table."""
    with closing(sqlite3.connect(path)) as conn:
        tables = {}
        for table in _tables(conn):
            cols = _columns(conn, table)
            col_list = ", ".join(f'"{c}"' for c in cols)
            rows = conn.execute(f'SELECT {col_list} FROM "{table}" ORDER BY rowid').fetchall()
            tables[table] = (cols, rows)
        objects = {
            (r[0], r[1]): r[2]
            for r in conn.execute(
                "SELECT type, name, sql FROM sqlite_master "
                "WHERE type IN ('index', 'trigger', 'view') AND sql IS NOT NULL"
            )
        }
    return tables, objects


def _sqlite_files(directory):
    found = []
    for path in sorted(Path(directory).rglob("*")):
        if path.is_file():
            with open(path, "rb") as fh:
                if fh.read(16) == b"SQLite format 3\x00":
                    found.append(path)
    return found


def _copies(directory):
    return Counter(_dump(p) for p in _sqlite_files(directory))


def _outcomes(report):
    return [(o.path, o.role, o.tenant_id, o.from_version, o.to_version, o.status) for o in report.outcomes]


def _check_clean(path):
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def _make_member(path, owner, historical):
    if historical:
        with closing(sqlite3.connect(path)) as conn:
            conn.executescript(HISTORICAL_SCRIPT)
            conn.execute("INSERT INTO admins (telegram_id) VALUES (?)", (owner,))
            conn.commit()
    else:
        db = database.Database(str(path))
        try:
            db.init_db(owner)
        finally:
            db.close()
    with closing(sqlite3.connect(path)) as conn:
        category = conn.execute("INSERT INTO categories (name) VALUES ('VPN')").lastrowid
        user_ids = [
            conn.execute(
                "INSERT INTO users (telegram_id, username, test_used, referral_credit) VALUES (?, ?, ?, ?)", user
            ).lastrowid
            for user in USERS
        ]
        product_ids = [
            conn.execute(
                "INSERT INTO products (category_id, name, price) VALUES (?, ?, ?)", (category, name, price)
            ).lastrowid
            for name, price in (("Monthly 50 GB", 150000), ("Quarterly 200 GB", 400000))
        ]
        panel = conn.execute(
            "INSERT INTO panel_servers (name, api_url) VALUES ('Panel one', 'https://panel-one.invalid/api')"
        ).lastrowid
        conn.execute("INSERT INTO test_config_plans (name, panel_server_id) VALUES ('Trial', ?)", (panel,))
        conn.execute(
            "INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, 'completed')",
            (user_ids[0], product_ids[0]),
        )
        conn.execute(
            "INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, 'pending')", (user_ids[1], product_ids[1])
        )
        conn.commit()


def _make_fsm(path, bot_id):
    with closing(sqlite3.connect(path)) as conn:
        conn.execute(FSM_DDL)
        conn.execute(
            "INSERT INTO fsm_storage "
            "(bot_id, chat_id, user_id, thread_id, business_connection_id, destiny, state, data) "
            "VALUES (?, 50001, 50001, 0, '', 'default', 'BuyStates:waiting_receipt', '{\"order_id\": 2}')",
            (bot_id,),
        )
        conn.commit()


def _add_registry_row(main, tenant_id, token, owner, db_path, *, active=1, live=1, historical=False):
    columns = "id, bot_token, bot_username, owner_telegram_id, owner_name, db_path, is_active"
    values = [tenant_id, token, f"shop{tenant_id}_bot", owner, f"Owner {tenant_id}", db_path, active]
    if not historical:
        columns += ", has_live_bot"
        values.append(live)
    marks = ", ".join("?" for _ in values)
    with closing(sqlite3.connect(main)) as conn:
        conn.execute(f"INSERT INTO reseller_bots ({columns}) VALUES ({marks})", values)
        conn.commit()


@dataclass
class Install:
    root: Path
    main: Path
    tenant_files: dict
    fsm: tuple

    @property
    def members(self):
        return (self.main, *(self.tenant_files[t] for t in sorted(self.tenant_files)))

    def paths(self, pre_upgrade_dir, *, tenants=None):
        return migrations.AuthorizedPaths(
            main=self.main,
            tenants=tuple(self.tenant_files.values()) if tenants is None else tuple(tenants),
            fsm=self.fsm,
            pre_upgrade_dir=pre_upgrade_dir,
            base_dir=self.root,
        )

    def dumps(self):
        return {p: _dump(p) for p in (*self.members, *self.fsm)}

    def expected(self, from_version, to_version, status):
        rows = [(_real(self.main), "main", None, from_version, to_version, status)]
        for tid in sorted(self.tenant_files):
            rows.append((_real(self.tenant_files[tid]), "reseller", tid, from_version, to_version, status))
        return rows


def _build(tmp_path, shape):
    root = _fresh_dir(tmp_path, "install")
    tenant_dir = _fresh_dir(root, "tenants")
    historical = shape == "historical"
    main = root / "bot_database.db"
    files = {7: root / "reseller_7.db", 8: tenant_dir / "reseller_8_level2.db", 9: tenant_dir / "nobot_9.db"}
    registry_paths = {7: "reseller_7.db", 8: str(files[8]), 9: str(files[9])}

    _make_member(main, MAIN_OWNER, historical)
    with closing(sqlite3.connect(main)) as conn:
        if historical:
            conn.execute("INSERT INTO admins (telegram_id) VALUES (?)", (MAIN_ADMIN,))
        else:
            conn.execute("INSERT INTO admins (telegram_id, role) VALUES (?, 'admin')", (MAIN_ADMIN,))
        conn.commit()
    for tid, token, _, owner, active, live in TENANTS:
        _make_member(files[tid], owner, historical)
        _add_registry_row(main, tid, token, owner, registry_paths[tid], active=active, live=live, historical=historical)

    fsm = (
        Path(f"{main}.fsm.sqlite3"),
        Path(f"{files[7]}.fsm.sqlite3"),
        Path(f"{files[8]}.fsm.sqlite3"),
    )
    for path, bot_id in zip(fsm, (1000001, 7000001, 8000001)):
        _make_fsm(path, bot_id)

    install = Install(root=root, main=main, tenant_files=files, fsm=fsm)
    if shape == "feature":
        migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-build")), RELEASE)
        with closing(sqlite3.connect(main)) as conn:
            category = conn.execute("SELECT id FROM categories WHERE name='VPN'").fetchone()[0]
            product = conn.execute(
                "INSERT INTO products (category_id, name, price, service_kind, composite_ref) "
                "VALUES (?, 'Composite six-node', 250000, 'composite', ?)",
                (category, REF_PRODUCT),
            ).lastrowid
            conn.execute(
                "INSERT INTO test_config_plans (name, panel_server_id, service_kind, composite_ref) "
                "VALUES ('Composite quick check', 1, 'composite', ?)",
                (REF_TEST_PLAN,),
            )
            conn.execute(
                "INSERT INTO orders (user_id, product_id, status, service_kind, composite_ref) "
                "VALUES (1, ?, 'pending', 'composite', ?)",
                (product, REF_ORDER),
            )
            conn.commit()
    return install


@dataclass
class TwoRuns:
    shape: str
    install: Install
    snapshots: dict
    before: dict
    after_first: dict
    first: object
    second: object
    pre_first: Path
    pre_second: Path
    started_ms: int
    first_done_ms: int


@pytest.fixture(params=SHAPES)
def two_runs(request, tmp_path):
    started_ms = _now_ms()
    install = _build(tmp_path, request.param)
    snapshots = {p: _snapshot(p) for p in install.members}
    before = install.dumps()
    pre_first = _fresh_dir(tmp_path, "pre-1")
    first = migrations.migrate(install.paths(pre_first), RELEASE)
    first_done_ms = _now_ms()
    after_first = install.dumps()
    pre_second = _fresh_dir(tmp_path, "pre-2")
    second = migrations.migrate(install.paths(pre_second), OTHER_RELEASE)
    return TwoRuns(
        shape=request.param,
        install=install,
        snapshots=snapshots,
        before=before,
        after_first=after_first,
        first=first,
        second=second,
        pre_first=pre_first,
        pre_second=pre_second,
        started_ms=started_ms,
        first_done_ms=first_done_ms,
    )


# Running migrate twice on each shape


def test_first_run_migrates_every_member_and_second_run_none(two_runs):
    version = migrations.SCHEMA_VERSION
    assert isinstance(version, int) and version >= 1
    install = two_runs.install
    if two_runs.shape == "feature":
        assert _outcomes(two_runs.first) == install.expected(version, version, "unchanged")
    else:
        assert _outcomes(two_runs.first) == install.expected(0, version, "migrated")
    assert _outcomes(two_runs.second) == install.expected(version, version, "unchanged")
    for path in install.members:
        info = migrations.inspect_schema(path)
        assert (info.version, info.supported) == (version, True)


def test_second_run_changes_no_file(two_runs):
    assert two_runs.install.dumps() == two_runs.after_first


def test_every_legacy_column_row_and_index_is_kept(two_runs):
    install = two_runs.install
    pre_feature = two_runs.shape != "feature"
    for path in install.members:
        added_here = {"service_kind", "composite_ref"} if path == install.main else {"service_kind"}
        before_tables, before_objects = two_runs.snapshots[path]
        after_tables, after_objects = _snapshot(path)
        assert set(before_tables) <= set(after_tables)
        for table, (cols, rows) in before_tables.items():
            after_cols = after_tables[table][0]
            assert after_cols[: len(cols)] == cols, (path.name, table)
            expected_added = added_here if pre_feature and table in KIND_TABLES else set()
            assert set(after_cols[len(cols) :]) == expected_added, (path.name, table)
            assert len(after_cols) == len(cols) + len(expected_added)
            col_list = ", ".join(f'"{c}"' for c in cols)
            with closing(sqlite3.connect(path)) as conn:
                kept = conn.execute(f'SELECT {col_list} FROM "{table}" ORDER BY rowid').fetchall()
            assert kept == rows, (path.name, table)
        for key, sql in before_objects.items():
            assert after_objects.get(key) == sql, (path.name, key)


def test_existing_rows_become_legacy(two_runs):
    install = two_runs.install
    for path in install.members:
        with closing(sqlite3.connect(path)) as conn:
            for table in KIND_TABLES:
                if path == install.main:
                    rows = conn.execute(f"SELECT service_kind, composite_ref FROM {table} ORDER BY id").fetchall()
                else:
                    rows = [(r[0], None) for r in conn.execute(f"SELECT service_kind FROM {table} ORDER BY id")]
                legacy_count = 2 if table in ("products", "orders") else 1
                expected = [("legacy", None)] * legacy_count
                if two_runs.shape == "feature" and path == install.main:
                    ref = {"products": REF_PRODUCT, "test_config_plans": REF_TEST_PLAN, "orders": REF_ORDER}[table]
                    expected.append(("composite", ref))
                assert rows == expected, (path.name, table)


def test_rows_inserted_by_legacy_code_default_to_legacy(two_runs):
    for path in two_runs.install.members:
        with closing(sqlite3.connect(path)) as conn:
            ids = {
                "products": conn.execute(
                    "INSERT INTO products (category_id, name, price) VALUES (1, 'New', 90000)"
                ).lastrowid,
                "test_config_plans": conn.execute(
                    "INSERT INTO test_config_plans (name, panel_server_id) VALUES ('New trial', 1)"
                ).lastrowid,
                "orders": conn.execute("INSERT INTO orders (user_id, product_id) VALUES (1, 1)").lastrowid,
            }
            for table, row_id in ids.items():
                kind = conn.execute(f"SELECT service_kind FROM {table} WHERE id = ?", (row_id,)).fetchone()[0]
                assert kind == "legacy", (path.name, table)
            conn.rollback()


def test_integrity_and_foreign_keys_hold(two_runs):
    for path in two_runs.install.members:
        _check_clean(path)


def test_owners_registry_and_customer_counts_are_kept(two_runs):
    install = two_runs.install
    historical = two_runs.shape == "historical"
    with closing(sqlite3.connect(install.main)) as conn:
        if historical:
            assert conn.execute("SELECT telegram_id FROM admins ORDER BY telegram_id").fetchall() == [
                (MAIN_OWNER,),
                (MAIN_ADMIN,),
            ]
        else:
            assert conn.execute("SELECT telegram_id, role FROM admins ORDER BY telegram_id").fetchall() == [
                (MAIN_OWNER, "owner"),
                (MAIN_ADMIN, "admin"),
            ]
        registry = conn.execute(
            "SELECT id, bot_token, owner_telegram_id, db_path, is_active FROM reseller_bots ORDER BY id"
        ).fetchall()
    assert registry == [
        (7, "synthetic-bot-token-7", 7001, "reseller_7.db", 1),
        (8, "synthetic-bot-token-8", 8001, str(install.tenant_files[8]), 0),
        (9, "no-bot:9:9001", 9001, str(install.tenant_files[9]), 1),
    ]
    for tid, path in install.tenant_files.items():
        with closing(sqlite3.connect(path)) as conn:
            owners = conn.execute("SELECT telegram_id FROM admins").fetchall()
        assert owners == [(TENANT_OWNERS[tid],)]
    for path in install.members:
        with closing(sqlite3.connect(path)) as conn:
            users = conn.execute("SELECT telegram_id, username, test_used, referral_credit FROM users ORDER BY id")
            assert users.fetchall() == list(USERS), path.name


def test_schema_versions_record_the_applying_release(two_runs):
    version = migrations.SCHEMA_VERSION
    for path in two_runs.install.members:
        with closing(sqlite3.connect(path)) as conn:
            rows = conn.execute("SELECT version, release, applied_at FROM composite_schema_versions ORDER BY version")
            rows = rows.fetchall()
        assert [(v, r) for v, r, _ in rows] == [(v, RELEASE) for v in range(1, version + 1)], path.name
        for _, _, applied_at in rows:
            assert isinstance(applied_at, int)
            assert two_runs.started_ms <= applied_at <= two_runs.first_done_ms


def test_reseller_files_get_no_composite_eligibility(two_runs):
    install = two_runs.install
    for path in install.tenant_files.values():
        before_tables = set(two_runs.snapshots[path][0])
        with closing(sqlite3.connect(path)) as conn:
            tables = _tables(conn)
            assert {t for t in tables if t.startswith("composite_")} == {"composite_schema_versions"}
            assert tables - before_tables <= {"composite_schema_versions"}
            for table in KIND_TABLES:
                assert "composite_ref" not in _columns(conn, table)
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO products (category_id, name, price, service_kind) VALUES (1, 'X', 1, 'composite')"
                )
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("UPDATE orders SET service_kind = 'composite' WHERE id = 1")
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO test_config_plans (name, panel_server_id, service_kind) VALUES ('X', 1, 'composite')"
                )
            conn.rollback()


def test_main_composite_reference_is_optional_and_unique(two_runs):
    inserts = {
        "products": "INSERT INTO products (category_id, name, price, service_kind, composite_ref) VALUES (1, 'P', 1, ?, ?)",
        "test_config_plans": "INSERT INTO test_config_plans (name, panel_server_id, service_kind, composite_ref) VALUES ('T', 1, ?, ?)",
        "orders": "INSERT INTO orders (user_id, product_id, service_kind, composite_ref) VALUES (1, 1, ?, ?)",
    }
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        for table, sql in inserts.items():
            ref = f"ref-{table}"
            conn.execute(sql, ("composite", ref))
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(sql, ("composite", ref))
            conn.execute(sql, ("legacy", None))
            conn.execute(sql, ("legacy", None))
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(sql, ("bogus", f"other-{table}"))
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(sql, (None, f"null-{table}"))
        conn.rollback()


def test_fsm_files_are_never_changed(two_runs):
    for path in two_runs.install.fsm:
        assert _dump(path) == two_runs.before[path]


def test_each_run_copies_the_whole_set_before_changing_it(two_runs):
    assert _copies(two_runs.pre_first) == Counter(two_runs.before.values())
    assert _copies(two_runs.pre_second) == Counter(two_runs.after_first.values())


def test_issuance_stays_disabled(two_runs):
    assert migrations.issuance_enabled(two_runs.install.main) is False


# Legacy initialization after the upgrade


@pytest.mark.parametrize("shape", ("historical", "current"))
def test_legacy_init_after_migrate_keeps_composite_columns(tmp_path, shape):
    install = _build(tmp_path, shape)
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    owners = {install.main: MAIN_OWNER, **{install.tenant_files[t]: TENANT_OWNERS[t] for t in install.tenant_files}}
    for path in install.members:
        db = database.Database(str(path))
        try:
            db.init_db(owners[path])
        finally:
            db.close()
    version = migrations.SCHEMA_VERSION
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(version, version, "unchanged")
    for path in install.members:
        _check_clean(path)
        with closing(sqlite3.connect(path)) as conn:
            assert "quantity" in _columns(conn, "orders")
            for table in KIND_TABLES:
                kinds = {r[0] for r in conn.execute(f"SELECT service_kind FROM {table}")}
                assert kinds == {"legacy"}, (path.name, table)


# Inspection


def test_inspect_schema_of_a_pre_feature_file_changes_nothing(tmp_path):
    install = _build(tmp_path, "current")
    before = install.dumps()
    info = migrations.inspect_schema(install.main)
    assert (info.version, info.supported) == (0, True)
    assert migrations.issuance_enabled(install.main) is False
    assert install.dumps() == before


# Refusals before any change


def test_future_main_schema_is_refused(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    future = migrations.SCHEMA_VERSION + 1
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("INSERT INTO composite_schema_versions VALUES (?, 'synthetic-future', ?)", (future, _now_ms()))
        conn.commit()
    before = install.dumps()
    pre = _fresh_dir(tmp_path, "pre-2")
    with pytest.raises(migrations.UnsupportedSchema) as raised:
        migrations.migrate(install.paths(pre), RELEASE)
    assert isinstance(raised.value, migrations.MigrationError)
    assert (raised.value.path, raised.value.version) == (_real(install.main), future)
    assert install.dumps() == before
    assert _sqlite_files(pre) == []
    info = migrations.inspect_schema(install.main)
    assert (info.version, info.supported) == (future, False)
    assert migrations.issuance_enabled(install.main) is False


def test_future_tenant_schema_is_refused_before_main_changes(tmp_path):
    install = _build(tmp_path, "current")
    future = migrations.SCHEMA_VERSION + 1
    with closing(sqlite3.connect(install.tenant_files[8])) as conn:
        conn.execute(VERSIONS_DDL)
        conn.execute("INSERT INTO composite_schema_versions VALUES (?, 'synthetic-future', ?)", (future, _now_ms()))
        conn.commit()
    before = install.dumps()
    pre = _fresh_dir(tmp_path, "pre-1")
    with pytest.raises(migrations.UnsupportedSchema) as raised:
        migrations.migrate(install.paths(pre), RELEASE)
    assert (raised.value.path, raised.value.version) == (_real(install.tenant_files[8]), future)
    assert install.dumps() == before
    assert _sqlite_files(pre) == []
    assert migrations.inspect_schema(install.main).version == 0


@pytest.mark.parametrize("problem", ("duplicate", "unauthorized", "unregistered", "missing"))
def test_registry_problems_are_refused_before_any_change(tmp_path, problem):
    install = _build(tmp_path, "current")
    tenants = list(install.tenant_files.values())
    if problem == "duplicate":
        _add_registry_row(install.main, 10, "synthetic-bot-token-10", 10001, "tenants/../reseller_7.db")
    elif problem == "unauthorized":
        tenants.remove(install.tenant_files[9])
    elif problem == "unregistered":
        stray = install.root / "tenants" / "stray.db"
        _make_member(stray, 10001, historical=False)
        tenants.append(stray)
    else:
        gone = install.root / "tenants" / "gone.db"
        _add_registry_row(install.main, 10, "synthetic-bot-token-10", 10001, str(gone))
        tenants.append(gone)
    before = install.dumps()
    pre = _fresh_dir(tmp_path, "pre-1")
    with pytest.raises(migrations.RegistryError) as raised:
        migrations.migrate(install.paths(pre, tenants=tenants), RELEASE)
    assert isinstance(raised.value, migrations.MigrationError)
    assert install.dumps() == before
    assert _sqlite_files(pre) == []
    assert not (install.root / "tenants" / "gone.db").exists()


@pytest.mark.parametrize("problem", ("not_empty", "missing"))
def test_pre_upgrade_dir_must_be_an_empty_directory(tmp_path, problem):
    install = _build(tmp_path, "current")
    pre = tmp_path / "pre-1"
    older = pre / "older-copy.db"
    if problem == "not_empty":
        pre.mkdir()
        with closing(sqlite3.connect(older)) as conn:
            conn.execute("CREATE TABLE kept (x INTEGER)")
            conn.execute("INSERT INTO kept VALUES (1)")
            conn.commit()
        older_dump = _dump(older)
    before = install.dumps()
    with pytest.raises(migrations.MigrationError):
        migrations.migrate(install.paths(pre), RELEASE)
    assert install.dumps() == before
    if problem == "not_empty":
        assert _sqlite_files(pre) == [older]
        assert _dump(older) == older_dump
    else:
        assert not pre.exists()


# Failures part way through the set


def test_member_failure_stops_the_run_and_keeps_the_pre_upgrade_set(tmp_path):
    install = _build(tmp_path, "current")
    before = install.dumps()
    version = migrations.SCHEMA_VERSION
    points = []

    def fail_third_commit(point):
        points.append(point)
        if point == "before commit" and points.count("before commit") == 3:
            raise sqlite3.OperationalError("disk I/O error")

    pre_first = _fresh_dir(tmp_path, "pre-1")
    with pytest.raises(migrations.MigrationFailed) as raised:
        migrations.migrate(install.paths(pre_first), RELEASE, crash=fail_third_commit)
    assert isinstance(raised.value, migrations.MigrationError)
    assert points == ["before commit", "after commit", "before commit", "after commit", "before commit"]
    main, t7, t8, t9 = (_real(p) for p in install.members)
    assert _outcomes(raised.value.report) == [
        (main, "main", None, 0, version, "migrated"),
        (t7, "reseller", 7, 0, version, "migrated"),
        (t8, "reseller", 8, 0, 0, "failed"),
        (t9, "reseller", 9, 0, 0, "not_attempted"),
    ]
    assert migrations.inspect_schema(install.main).version == version
    assert migrations.inspect_schema(install.tenant_files[7]).version == version
    for tid in (8, 9):
        assert _dump(install.tenant_files[tid]) == before[install.tenant_files[tid]]
    assert migrations.issuance_enabled(install.main) is False
    assert _copies(pre_first) == Counter(before.values())

    rerun = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(rerun) == [
        (main, "main", None, version, version, "unchanged"),
        (t7, "reseller", 7, version, version, "unchanged"),
        (t8, "reseller", 8, 0, version, "migrated"),
        (t9, "reseller", 9, 0, version, "migrated"),
    ]
    assert migrations.issuance_enabled(install.main) is False
    assert _copies(pre_first) == Counter(before.values())


@pytest.mark.parametrize(
    ("point", "hit", "committed"),
    (("before commit", 1, 0), ("after commit", 1, 1), ("before commit", 3, 2), ("after commit", 3, 3)),
)
def test_crash_keeps_only_committed_members(tmp_path, point, hit, committed):
    install = _build(tmp_path, "current")
    before = install.dumps()
    version = migrations.SCHEMA_VERSION
    plan = CrashPlan().arm(point, hit=hit)
    pre_first = _fresh_dir(tmp_path, "pre-1")
    with pytest.raises(SimulatedCrash):
        migrations.migrate(install.paths(pre_first), RELEASE, crash=plan)
    steps = ["before commit", "after commit"] * 4
    assert plan.reached == tuple(steps[: steps.index(point) + 2 * (hit - 1) + 1])
    members = install.members
    for path in members[:committed]:
        assert migrations.inspect_schema(path).version == version
    for path in members[committed:]:
        assert _dump(path) == before[path], path.name
    assert migrations.issuance_enabled(install.main) is False
    assert _copies(pre_first) == Counter(before.values())

    rerun = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    expected = install.expected(0, version, "migrated")
    for i in range(committed):
        expected[i] = (*expected[i][:3], version, version, "unchanged")
    assert _outcomes(rerun) == expected
    for path in members:
        _check_clean(path)


# Data-model §1–§4 tables (T034b: checks for T036 and T037)

T0 = 1_793_318_400_000  # 2026-10-30T00:00:00Z in UTC epoch milliseconds
DESCRIPTOR_A1 = '{"address": "a.example.invalid", "port": 443, "sni": "a.example.invalid", "fingerprint": "chrome", "flow": "xtls-rprx-vision"}'
DESCRIPTOR_A1_NEW = '{"address": "a2.example.invalid", "port": 443, "sni": "a2.example.invalid", "fingerprint": "chrome", "flow": "xtls-rprx-vision"}'


def _digest(n):
    return hashlib.sha256(f"synthetic-url-token-{n}".encode()).digest()


# One valid row per table, in parent-before-child order.
BASE_ROWS = {
    "composite_physical_panels": {"physical_panel_id": "pp-a", "provider": "3xui", "authority_fingerprint": "authority-fp-a", "endpoint_ref": "endpoint-ref-a", "tls_trust_ref": "tls-trust-a", "panel_version": "v3.9.0", "core_version": "v26.9.30", "capability_manifest_revision": "manifest-1", "route_namespace_version": 1, "restart_xray_on_client_disable": "off", "restart_xray_on_client_disable_checked_at": T0, "write_stall_misses": 0, "write_stall_escalation_ref": None},
    "composite_panel_aliases": {"alias_id": "pa-main-1", "physical_panel_id": "pp-a", "database_installation_id": "inst-main", "tenant_id": "main", "local_panel_server_id": 1},
    "composite_prepared_bindings": {"binding_id": "pb-a1", "physical_panel_id": "pp-a", "inbound_id": 1, "settings_fingerprint": "settings-fp-a1", "egress_key": "out-de", "route_namespace": "cmp1"},
    "composite_plans": {"plan_id": "cp-paid", "kind": "paid"},
    "composite_plan_versions": {"plan_version_id": "cpv-paid-1", "plan_id": "cp-paid", "kind": "paid", "version": 1, "allowance_bytes": 53_687_091_200, "duration_seconds": 2_592_000, "base_price": 250_000},
    "composite_plan_nodes": {"plan_node_id": "cpn-1", "plan_version_id": "cpv-paid-1", "ordinal": 1, "logical_node_key": "node-a1", "binding_id": "pb-a1", "protocol": "vless", "transport": "tcp", "security": "reality", "descriptor": DESCRIPTOR_A1, "owner_pick": None, "remark": "A1", "egress": "out-de"},
    "composite_offers": {"offer_id": "of-1", "plan_version_id": "cpv-paid-1", "allowance_bytes": 53_687_091_200, "duration_seconds": 2_592_000, "base_price": 250_000, "payable_price": 225_000, "accepted_by": "telegram:50001", "accepted_at": T0},
    "composite_offer_nodes": {"offer_node_id": "ofn-1", "offer_id": "of-1", "ordinal": 1, "logical_node_key": "node-a1", "binding_id": "pb-a1", "protocol": "vless", "transport": "tcp", "security": "reality", "descriptor": DESCRIPTOR_A1, "owner_pick": None, "egress": "out-de"},
    "composite_subscriptions": {"subscription_id": "sub-1", "tenant_installation_id": "inst-main", "customer_telegram_id": 50001, "offer_id": "of-1", "kind": "paid", "lifecycle": "preparing"},
    "composite_subscription_nodes": {"subscription_id": "sub-1", "logical_node_key": "node-a1", "descriptor": DESCRIPTOR_A1},
    "composite_tokens": {"token_id": "tok-1", "subscription_id": "sub-1", "token_generation": 1, "token_digest": _digest(1), "encrypted_token": None, "status": "current"},
    "composite_config_generations": {"generation_id": "gen-1", "subscription_id": "sub-1", "generation": 1, "state": "preparing", "prepared_at": T0, "verified_at": None, "published_at": None},
}
SUBSCRIPTION_EXTRA_COLUMNS = ("available_at", "expires_at", "customer_disabled", "owner_suspended", "reporting_suspended", "recovery_hold_case", "replacement_delivery_block", "initial_delivery_block", "cancel_accepted_at", "cancel_wait_kind", "cancel_final_started_at")
FLAGS = ("customer_disabled", "owner_suspended", "reporting_suspended", "replacement_delivery_block", "initial_delivery_block")
# (child table, child columns, parent table, parent columns)
EXPECTED_FKS = (
    ("composite_panel_aliases", ("physical_panel_id",), "composite_physical_panels", ("physical_panel_id",)),
    ("composite_prepared_bindings", ("physical_panel_id",), "composite_physical_panels", ("physical_panel_id",)),
    ("composite_plan_versions", ("plan_id", "kind"), "composite_plans", ("plan_id", "kind")),
    ("composite_plan_nodes", ("plan_version_id",), "composite_plan_versions", ("plan_version_id",)),
    ("composite_plan_nodes", ("binding_id",), "composite_prepared_bindings", ("binding_id",)),
    ("composite_offers", ("plan_version_id",), "composite_plan_versions", ("plan_version_id",)),
    ("composite_offer_nodes", ("offer_id",), "composite_offers", ("offer_id",)),
    ("composite_offer_nodes", ("binding_id",), "composite_prepared_bindings", ("binding_id",)),
    ("composite_subscriptions", ("offer_id",), "composite_offers", ("offer_id",)),
    ("composite_subscription_nodes", ("subscription_id",), "composite_subscriptions", ("subscription_id",)),
    ("composite_tokens", ("subscription_id",), "composite_subscriptions", ("subscription_id",)),
    ("composite_config_generations", ("subscription_id",), "composite_subscriptions", ("subscription_id",)),
)


def _insert(conn, table, **changes):
    row = {**BASE_ROWS[table], **changes}
    cols = tuple(row)
    marks = ", ".join("?" for _ in cols)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({marks})", tuple(row.values()))


def _chain(conn, until=None):
    assert until is None or until in BASE_ROWS
    for table in BASE_ROWS:
        if table == until:
            return
        _insert(conn, table)


def _one(conn, sql, *args):
    return conn.execute(sql, args).fetchone()


@pytest.fixture
def main_db(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    conn = sqlite3.connect(install.main)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def test_main_gets_the_section_1_to_4_tables(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        tables = _tables(conn)
        for table, row in BASE_ROWS.items():
            assert table in tables
            assert set(row) <= set(_columns(conn, table))
        cols = set(_columns(conn, "composite_subscriptions"))
        assert set(SUBSCRIPTION_EXTRA_COLUMNS) <= cols
        assert "enabled" not in cols and "is_active" not in cols


def test_section_1_to_4_foreign_keys_are_restrict(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        found = set()
        for table in BASE_ROWS:
            grouped = {}
            for row in conn.execute(f"PRAGMA foreign_key_list({table})"):
                grouped.setdefault(row[0], []).append(row)
            for rows in grouped.values():
                rows.sort(key=lambda row: row[1])
                parent = rows[0][2]
                to_cols = tuple(row[4] for row in rows)
                if any(col is None for col in to_cols):
                    to_cols = tuple(r[1] for r in sorted((r for r in conn.execute(f"PRAGMA table_info({parent})") if r[5] > 0), key=lambda r: r[5]))
                found.add((table, tuple(row[3] for row in rows), parent, to_cols))
                assert all(row[6] == "RESTRICT" for row in rows)
        assert set(EXPECTED_FKS) <= found


def test_rows_in_every_new_table_survive_a_rerun(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _chain(conn)
        conn.commit()
    before = _dump(install.main)
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(migrations.SCHEMA_VERSION, migrations.SCHEMA_VERSION, "unchanged")
    assert _dump(install.main) == before
    _check_clean(install.main)
    with closing(sqlite3.connect(install.main)) as conn:
        assert all(_one(conn, f"SELECT count(*) FROM {table}")[0] == 1 for table in BASE_ROWS)


def test_panel_provider_is_3xui_only(main_db):
    _insert(main_db, "composite_physical_panels")
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        _insert(main_db, "composite_physical_panels", physical_panel_id="pp-b", authority_fingerprint="fp-b", provider="pasarguard")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("NOT NULL constraint failed: composite_physical_panels.provider")):
        _insert(main_db, "composite_physical_panels", physical_panel_id="pp-c", authority_fingerprint="fp-c", provider=None)


@pytest.mark.parametrize("value, checked, accepted", [("off", T0, True), ("on", T0, True), ("unreadable", T0, True), (None, None, True), ("maybe", T0, False), ("off", None, False), (None, T0, False)], ids=["off-checked", "on-checked", "unreadable-checked", "not-checked", "invalid-value", "missing-time", "time-without-value"])
def test_panel_restart_setting_is_recorded_with_its_check_time(main_db, value, checked, accepted):
    changes = dict(physical_panel_id=f"pp-{value}-{checked}", authority_fingerprint=f"fp-{value}-{checked}", restart_xray_on_client_disable=value, restart_xray_on_client_disable_checked_at=checked)
    if accepted:
        _insert(main_db, "composite_physical_panels", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_physical_panels", **changes)


@pytest.mark.parametrize("misses, accepted", [(3, True), (-1, False)], ids=["nonnegative", "negative"])
def test_panel_write_stall_misses_are_never_negative(main_db, misses, accepted):
    changes = {"physical_panel_id": f"pp-{misses}", "authority_fingerprint": f"fp-{misses}", "write_stall_misses": misses}
    if accepted:
        _insert(main_db, "composite_physical_panels", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_physical_panels", **changes)


def test_alias_is_unique_per_installation_tenant_and_local_server(main_db):
    _chain(main_db, until="composite_prepared_bindings")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_panel_aliases.database_installation_id, composite_panel_aliases.tenant_id, composite_panel_aliases.local_panel_server_id")):
        _insert(main_db, "composite_panel_aliases", alias_id="pa-dup")
    for alias_id, changes in [("pa-2", {"database_installation_id": "inst-reseller-7"}), ("pa-3", {"tenant_id": "reseller-7"}), ("pa-4", {"local_panel_server_id": 2})]:
        _insert(main_db, "composite_panel_aliases", alias_id=alias_id, **changes)


@pytest.mark.parametrize("column", ["database_installation_id", "tenant_id", "local_panel_server_id"])
def test_alias_key_columns_are_required(main_db, column):
    _chain(main_db, until="composite_panel_aliases")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape(f"NOT NULL constraint failed: composite_panel_aliases.{column}")):
        _insert(main_db, "composite_panel_aliases", **{column: None})


def test_one_inbound_carries_several_bindings(main_db):
    _chain(main_db, until="composite_plans")
    for i in range(2, 6):
        _insert(main_db, "composite_prepared_bindings", binding_id=f"pb-a1-{i}", egress_key=f"out-{i}")
    assert _one(main_db, "SELECT count(*) FROM composite_prepared_bindings")[0] == 5


@pytest.mark.parametrize("sql, table, key", [("DELETE FROM composite_physical_panels WHERE physical_panel_id = 'pp-a'", "composite_physical_panels", "physical_panel_id"), ("DELETE FROM composite_prepared_bindings WHERE binding_id = 'pb-a1'", "composite_prepared_bindings", "binding_id"), ("DELETE FROM composite_plans WHERE plan_id = 'cp-paid'", "composite_plans", "plan_id"), ("DELETE FROM composite_plan_versions WHERE plan_version_id = 'cpv-paid-1'", "composite_plan_versions", "plan_version_id"), ("DELETE FROM composite_subscriptions WHERE subscription_id = 'sub-1'", "composite_subscriptions", "subscription_id")], ids=["panel", "binding", "plan", "version", "subscription"])
def test_protected_parent_cannot_be_deleted(main_db, sql, table, key):
    _chain(main_db)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        main_db.execute(sql)
    assert _one(main_db, f"SELECT count(*) FROM {table} WHERE {key} = ?", BASE_ROWS[table][key])[0] == 1


@pytest.mark.parametrize("child, columns, parent, parent_columns", EXPECTED_FKS)
def test_child_row_needs_its_parent(main_db, child, columns, parent, parent_columns):
    _chain(main_db, until=child)
    missing = {"composite_physical_panels": "pp-missing", "composite_plans": "cp-missing", "composite_plan_versions": "cpv-missing", "composite_prepared_bindings": "pb-missing", "composite_offers": "of-missing", "composite_subscriptions": "sub-missing"}[parent]
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _insert(main_db, child, **{columns[0]: missing})


@pytest.mark.parametrize("kind, accepted", [("paid", True), ("test", True), ("campaign", True), ("trial", False), (None, False)], ids=["paid", "test", "campaign", "invalid", "null"])
def test_plan_kind_is_paid_test_or_campaign(main_db, kind, accepted):
    changes = {"plan_id": f"cp-{kind}", "kind": kind}
    if accepted:
        _insert(main_db, "composite_plans", **changes)
    else:
        error = "CHECK constraint failed" if kind is not None else re.escape("NOT NULL constraint failed: composite_plans.kind")
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, "composite_plans", **changes)


@pytest.mark.parametrize("changes, accepted", [({}, True), ({"base_price": 1}, True), ({"base_price": 0}, False), ({"base_price": -1}, False), ({"base_price": 250000.5}, False), ({"duration_seconds": 2_591_999}, False), ({"duration_seconds": 2_592_001}, False), ({"duration_seconds": 2_678_400}, False), ({"duration_seconds": 0}, False), ({"allowance_bytes": 0}, False), ({"allowance_bytes": -1}, False), ({"allowance_bytes": 53_687_091_200.5}, False)], ids=["valid", "positive-price", "zero-price", "negative-price", "fractional-price", "short", "off-by-one", "too-long", "zero-duration", "zero-bytes", "negative-bytes", "fractional-bytes"])
def test_paid_version_terms(main_db, changes, accepted):
    _chain(main_db, until="composite_plan_versions")
    if accepted:
        _insert(main_db, "composite_plan_versions", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_plan_versions", **changes)


@pytest.mark.parametrize("kind", ["test", "campaign"])
@pytest.mark.parametrize("allowance, duration, accepted", [(209_715_200, 3_600, True), (209_715_200, 7_200, True), (16_106_127_360, 1_296_000, True), (209_715_200, 0, False), (209_715_200, -3_600, False), (209_715_200, 1_800, False), (209_715_200, 3_599, False), (209_715_200, 5_400, False), (0, 3_600, False), (-1, 3_600, False)], ids=["hour", "two-hours", "campaign-default", "zero-duration", "negative-duration", "half-hour", "non-hour", "ninety-minutes", "zero-bytes", "negative-bytes"])
def test_test_and_campaign_version_terms(main_db, kind, allowance, duration, accepted):
    _chain(main_db, until="composite_plan_versions")
    _insert(main_db, "composite_plans", plan_id="cp-x", kind=kind)
    changes = {"plan_version_id": f"cpv-x-{kind}-{allowance}-{duration}", "plan_id": "cp-x", "kind": kind, "version": 1, "allowance_bytes": allowance, "duration_seconds": duration, "base_price": 0}
    if accepted:
        _insert(main_db, "composite_plan_versions", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_plan_versions", **changes)


@pytest.mark.parametrize("case", ["kind-mismatch", "duplicate-version", "next-version", "update-kind"])
def test_version_kind_and_number(main_db, case):
    _chain(main_db, until="composite_plan_nodes")
    if case == "kind-mismatch":
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
            _insert(main_db, "composite_plan_versions", plan_version_id="cpv-x", kind="test", version=2, allowance_bytes=209_715_200, duration_seconds=3_600, base_price=0)
    elif case == "duplicate-version":
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_plan_versions.plan_id, composite_plan_versions.version")):
            _insert(main_db, "composite_plan_versions", plan_version_id="cpv-dup", version=1)
    elif case == "next-version":
        _insert(main_db, "composite_plan_versions", plan_version_id="cpv-paid-2", version=2)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
            main_db.execute("UPDATE composite_plans SET kind = 'test' WHERE plan_id = 'cp-paid'")


@pytest.mark.parametrize("table", ["composite_plan_nodes", "composite_offer_nodes"], ids=["plan-nodes", "offer-nodes"])
@pytest.mark.parametrize("case", ["ordinal", "logical-key", "different", "other-parent"])
def test_nodes_are_unique_per_parent_by_ordinal_and_key(main_db, table, case):
    if table == "composite_plan_nodes":
        _chain(main_db, until="composite_offers")
        parent, other, p = "cpv-paid-1", "cpv-paid-2", "plan_version_id"
        _insert(main_db, "composite_plan_versions", plan_version_id=other, version=2)
    else:
        _chain(main_db, until="composite_subscriptions")
        parent, other, p = "of-1", "of-2", "offer_id"
        _insert(main_db, "composite_offers", offer_id=other)
    changes = {p: parent, "ordinal": 2, "logical_node_key": "node-a2"}
    if table == "composite_plan_nodes":
        changes["plan_node_id"] = "cpn-extra"
    else:
        changes.update(offer_node_id="ofn-extra", binding_id="pb-a1")
    if case == "ordinal":
        changes.update(ordinal=1)
        with pytest.raises(sqlite3.IntegrityError, match=re.escape(f"UNIQUE constraint failed: {table}.{p}, {table}.ordinal")):
            _insert(main_db, table, **changes)
    elif case == "logical-key":
        changes.update(logical_node_key="node-a1")
        with pytest.raises(sqlite3.IntegrityError, match=re.escape(f"UNIQUE constraint failed: {table}.{p}, {table}.logical_node_key")):
            _insert(main_db, table, **changes)
    elif case == "other-parent":
        changes.update(**{p: other, "ordinal": 1, "logical_node_key": "node-a1"})
        _insert(main_db, table, **changes)
    else:
        _insert(main_db, table, **changes)


def test_node_sets_have_no_maximum_size(main_db):
    _chain(main_db, until="composite_plan_nodes")
    for i in range(1, 8):
        _insert(main_db, "composite_plan_nodes", plan_node_id=f"cpn-{i}", ordinal=i, logical_node_key=f"node-{i}")
    _insert(main_db, "composite_offers")
    for i in range(1, 8):
        _insert(main_db, "composite_offer_nodes", offer_node_id=f"ofn-{i}", ordinal=i, logical_node_key=f"node-{i}")
    _insert(main_db, "composite_subscriptions")
    for i in range(1, 8):
        _insert(main_db, "composite_subscription_nodes", logical_node_key=f"node-{i}")
    for table in ("composite_plan_nodes", "composite_offer_nodes", "composite_subscription_nodes"):
        assert _one(main_db, f"SELECT count(*) FROM {table}")[0] == 7


@pytest.mark.parametrize("table", ["composite_plan_nodes", "composite_offer_nodes"], ids=["plan-node", "offer-node"])
def test_node_protocol_and_descriptor(main_db, table):
    _chain(main_db, until="composite_plan_nodes" if table == "composite_plan_nodes" else "composite_offer_nodes")
    id_col = "plan_node_id" if table == "composite_plan_nodes" else "offer_node_id"
    parent_col = "plan_version_id" if table == "composite_plan_nodes" else "offer_id"
    parent_id = "cpv-paid-1" if table == "composite_plan_nodes" else "of-1"
    n = 1
    for protocol in ("vless", "vmess", "trojan"):
        _insert(main_db, table, **{id_col: f"node-{table}-{n}", parent_col: parent_id, "ordinal": n, "logical_node_key": f"node-p{n}", "protocol": protocol})
        n += 1
    for changes, error in [({"protocol": "shadowsocks"}, "CHECK constraint failed"), ({"protocol": None}, re.escape(f"NOT NULL constraint failed: {table}.protocol")), ({"descriptor": None}, re.escape(f"NOT NULL constraint failed: {table}.descriptor"))]:
        base = {id_col: f"node-{table}-{n}", parent_col: parent_id, "ordinal": n, "logical_node_key": f"node-p{n}"}
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, table, **base, **changes)
        n += 1


def test_plan_node_version_never_changes(main_db):
    _chain(main_db, until="composite_offers")
    _insert(main_db, "composite_plan_versions", plan_version_id="cpv-paid-2", version=2)
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("UPDATE composite_plan_nodes SET plan_version_id = 'cpv-paid-2' WHERE plan_node_id = 'cpn-1'")
    assert _one(main_db, "SELECT plan_version_id FROM composite_plan_nodes WHERE plan_node_id = 'cpn-1'")[0] == "cpv-paid-1"


def test_offers_and_offer_nodes_are_immutable(main_db):
    _chain(main_db, until="composite_subscriptions")
    _insert(main_db, "composite_offers", offer_id="of-2")
    for sql, query, expected in [("UPDATE composite_offers SET payable_price = 0 WHERE offer_id = 'of-1'", "SELECT payable_price FROM composite_offers WHERE offer_id = 'of-1'", 225000), ("DELETE FROM composite_offers WHERE offer_id = 'of-2'", "SELECT count(*) FROM composite_offers WHERE offer_id = 'of-2'", 1), (f"UPDATE composite_offer_nodes SET descriptor = '{DESCRIPTOR_A1_NEW}' WHERE offer_node_id = 'ofn-1'", "SELECT descriptor FROM composite_offer_nodes WHERE offer_node_id = 'ofn-1'", DESCRIPTOR_A1), ("DELETE FROM composite_offer_nodes WHERE offer_node_id = 'ofn-1'", "SELECT count(*) FROM composite_offer_nodes WHERE offer_node_id = 'ofn-1'", 1)]:
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute(sql)
        assert _one(main_db, query)[0] == expected


@pytest.mark.parametrize("changes, accepted", [({"payable_price": 0}, True), ({"payable_price": 250_000}, True), ({"payable_price": -1}, False), ({"payable_price": 250_001}, False), ({"allowance_bytes": 0}, False), ({"duration_seconds": 0}, False), ({"allowance_bytes": 1.5}, False)], ids=["zero-payable", "full-price", "negative-price", "above-base", "zero-bytes", "zero-duration", "fractional-bytes"])
def test_offer_terms(main_db, changes, accepted):
    _chain(main_db, until="composite_offer_nodes")
    if accepted:
        _insert(main_db, "composite_offers", offer_id=f"of-{changes}", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_offers", offer_id=f"of-{changes}", **changes)


@pytest.mark.parametrize("lifecycle, extra, accepted", [("preparing", {}, True), ("fulfilled", {"available_at": T0, "expires_at": T0 + 2_592_000_000}, True), ("cancel_pending", {"cancel_accepted_at": T0, "cancel_wait_kind": "authorized_renewal"}, True), ("cancelled", {"cancel_accepted_at": T0, "cancel_final_started_at": T0}, True), ("failed_unfulfilled", {}, True), ("active", {}, False), ("expired", {}, False), ("exhausted", {}, False), (None, {}, False)], ids=["preparing", "fulfilled", "cancel-pending", "cancelled", "failed", "active", "expired", "exhausted", "null"])
def test_subscription_lifecycle_values(main_db, lifecycle, extra, accepted):
    _chain(main_db, until="composite_subscription_nodes")
    changes = {"subscription_id": f"sub-life-{lifecycle}", "lifecycle": lifecycle, **extra}
    if accepted:
        _insert(main_db, "composite_subscriptions", **changes)
    else:
        error = "CHECK constraint failed" if lifecycle is not None else re.escape("NOT NULL constraint failed: composite_subscriptions.lifecycle")
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, "composite_subscriptions", **changes)


@pytest.mark.parametrize("kind, accepted", [("paid", True), ("test", True), ("trial", False)], ids=["paid", "test", "invalid"])
def test_subscription_kind_is_paid_or_test(main_db, kind, accepted):
    _chain(main_db, until="composite_subscription_nodes")
    changes = {"subscription_id": f"sub-kind-{kind}", "kind": kind}
    if accepted:
        _insert(main_db, "composite_subscriptions", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_subscriptions", **changes)


def test_restrictions_are_independent(main_db):
    _chain(main_db, until="composite_subscription_nodes")
    assert _one(main_db, "SELECT customer_disabled, owner_suspended, reporting_suspended, recovery_hold_case, replacement_delivery_block, initial_delivery_block FROM composite_subscriptions WHERE subscription_id='sub-1'") == (0, 0, 0, None, 0, 0)
    for flag in FLAGS:
        _insert(main_db, "composite_subscriptions", subscription_id=f"sub-{flag}", **{flag: 1})
        got = _one(main_db, f"SELECT {', '.join(FLAGS)} FROM composite_subscriptions WHERE subscription_id=?", f"sub-{flag}")
        assert got == tuple(int(col == flag) for col in FLAGS)
    _insert(main_db, "composite_subscriptions", subscription_id="sub-all", **{flag: 1 for flag in FLAGS})
    main_db.execute("UPDATE composite_subscriptions SET customer_disabled = 0 WHERE subscription_id = 'sub-all'")
    assert _one(main_db, f"SELECT {', '.join(FLAGS)} FROM composite_subscriptions WHERE subscription_id='sub-all'") == (0, 1, 1, 1, 1)
    for changes, error in [({"customer_disabled": 2}, "CHECK constraint failed"), ({"owner_suspended": -1}, "CHECK constraint failed"), ({"reporting_suspended": None}, re.escape("NOT NULL constraint failed: composite_subscriptions.reporting_suspended"))]:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, "composite_subscriptions", subscription_id=f"sub-bad-{changes}", **changes)


@pytest.mark.parametrize("accepted, timestamp, wait, final", [(True, T0, "authorized_renewal", None), (True, T0, "initial_provisioning", None), (True, T0, None, T0), (True, T0, "authorized_renewal", T0 + 60_000), (False, T0, "renewal", None), (False, None, "authorized_renewal", None), (False, None, None, T0), (False, T0, None, T0 - 1)], ids=["renewal-wait", "provisioning-wait", "final", "wait-and-final", "invalid-wait", "missing-accepted", "final-without-accepted", "final-before-accepted"])
def test_cancellation_fields(main_db, accepted, timestamp, wait, final):
    _chain(main_db, until="composite_subscription_nodes")
    changes = {"subscription_id": f"sub-cancel-{timestamp}-{wait}-{final}", "lifecycle": "cancel_pending", "cancel_accepted_at": timestamp, "cancel_wait_kind": wait, "cancel_final_started_at": final}
    if accepted:
        _insert(main_db, "composite_subscriptions", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_subscriptions", **changes)


def test_subscription_tenant_and_customer_never_change(main_db):
    _chain(main_db, until="composite_subscription_nodes")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("UPDATE composite_subscriptions SET tenant_installation_id = 'inst-other' WHERE subscription_id = 'sub-1'")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("UPDATE composite_subscriptions SET customer_telegram_id = 50002 WHERE subscription_id = 'sub-1'")
    assert _one(main_db, "SELECT tenant_installation_id, customer_telegram_id FROM composite_subscriptions WHERE subscription_id='sub-1'") == ("inst-main", 50001)
    main_db.execute("UPDATE composite_subscriptions SET lifecycle = 'fulfilled', available_at = ?, expires_at = ? WHERE subscription_id = 'sub-1'", (T0, T0 + 2_592_000_000))


def test_current_descriptor_per_logical_node(main_db):
    _chain(main_db, until="composite_tokens")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_subscription_nodes.subscription_id, composite_subscription_nodes.logical_node_key")):
        _insert(main_db, "composite_subscription_nodes")
    _insert(main_db, "composite_subscription_nodes", logical_node_key="node-a2")
    main_db.execute("UPDATE composite_subscription_nodes SET descriptor=? WHERE subscription_id='sub-1' AND logical_node_key='node-a1'", (DESCRIPTOR_A1_NEW,))
    assert _one(main_db, "SELECT descriptor FROM composite_subscription_nodes WHERE subscription_id='sub-1' AND logical_node_key='node-a1'")[0] == DESCRIPTOR_A1_NEW
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("NOT NULL constraint failed: composite_subscription_nodes.descriptor")):
        _insert(main_db, "composite_subscription_nodes", logical_node_key="node-a3", descriptor=None)


def _sub2(conn):
    _insert(conn, "composite_subscriptions", subscription_id="sub-2")


def test_token_digest_is_a_unique_sha256_value(main_db):
    _chain(main_db, until="composite_tokens")
    _insert(main_db, "composite_tokens")
    _sub2(main_db)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_tokens.token_digest")):
        _insert(main_db, "composite_tokens", token_id="tok-dup", subscription_id="sub-2", token_generation=1, token_digest=_digest(1))
    for digest, error in [(_digest(2)[:31], "CHECK constraint failed"), (_digest(2).hex(), "CHECK constraint failed"), (_digest(2).hex()[:32], "CHECK constraint failed"), (None, re.escape("NOT NULL constraint failed: composite_tokens.token_digest"))]:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, "composite_tokens", token_id=f"tok-invalid-{digest}", subscription_id="sub-2", token_generation=1, token_digest=digest)
    _insert(main_db, "composite_tokens", token_id="tok-2", subscription_id="sub-2", token_generation=1, token_digest=_digest(2))


@pytest.mark.parametrize("case, status, accepted", [("candidate", "candidate", True), ("revoked", "revoked", True), ("superseded", "superseded", True), ("second-revoked", "revoked", True), ("invalid", "expired", False), ("null", None, False)], ids=["candidate", "revoked", "superseded", "second-revoked", "invalid", "null"])
def test_token_status_and_one_current_token(main_db, case, status, accepted):
    _chain(main_db, until="composite_tokens")
    _insert(main_db, "composite_tokens", token_id="tok-1")
    _sub2(main_db)
    changes = {"token_id": f"tok-{status}-{accepted}", "token_generation": 2, "token_digest": _digest(2), "status": status}
    if accepted:
        _insert(main_db, "composite_tokens", **changes)
        if case == "second-revoked":
            _insert(main_db, "composite_tokens", token_id="tok-revoked-again", token_generation=3, token_digest=_digest(3), status="revoked")
    else:
        error = "CHECK constraint failed" if status is not None else re.escape("NOT NULL constraint failed: composite_tokens.status")
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _insert(main_db, "composite_tokens", **changes)
    if status == "candidate":
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_tokens.subscription_id")):
            _insert(main_db, "composite_tokens", token_id="tok-current-dup", token_generation=3, token_digest=_digest(3), status="current")
        _insert(main_db, "composite_tokens", token_id="tok-current-sub2", subscription_id="sub-2", token_generation=1, token_digest=_digest(4), status="current")


def test_token_tombstones_are_kept(main_db):
    _chain(main_db)
    for token_id, status, number in [("tok-r", "revoked", 5), ("tok-s", "superseded", 6)]:
        _insert(main_db, "composite_tokens", token_id=token_id, token_generation=number, token_digest=_digest(number), status=status)
    for token_id in ("tok-r", "tok-s"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute("DELETE FROM composite_tokens WHERE token_id=?", (token_id,))
        assert _one(main_db, "SELECT count(*) FROM composite_tokens WHERE token_id=?", token_id)[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("UPDATE composite_tokens SET token_digest=? WHERE token_id='tok-r'", (_digest(9),))
    assert _one(main_db, "SELECT token_digest FROM composite_tokens WHERE token_id='tok-r'")[0] == _digest(5)
    main_db.execute("UPDATE composite_tokens SET status='revoked' WHERE token_id='tok-1'")
    for token_id in ("tok-r", "tok-1", "tok-s"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute("UPDATE composite_tokens SET status='current' WHERE token_id=?", (token_id,))
    _insert(main_db, "composite_tokens", token_id="tok-c", token_generation=7, token_digest=_digest(7), status="candidate")
    main_db.execute("UPDATE composite_tokens SET status='current' WHERE token_id='tok-c'")


@pytest.mark.parametrize("case", ["base", "complete", "published", "retired", "second-retired", "blocked", "invalid", "null", "second-published", "other-sub", "duplicate-generation"])
def test_generation_states_and_one_published_generation(main_db, case):
    _chain(main_db, until="composite_config_generations")
    _sub2(main_db)
    vt, pt = T0 + 1_000, T0 + 2_000
    if case == "base":
        _insert(main_db, "composite_config_generations")
    elif case in ("complete", "published", "retired", "second-retired", "second-published", "other-sub"):
        state = "complete_verified" if case == "complete" else "published" if case in ("published", "second-published", "other-sub") else "retired"
        sid = "sub-2" if case == "other-sub" else "sub-1"
        gen = 2 if case in ("second-retired", "second-published") else 1
        gid = f"gen-{case}"
        if case == "other-sub":
            _insert(main_db, "composite_config_generations", generation_id="gen-pub", generation=1, state="published", verified_at=vt, published_at=pt)
        if case == "second-published":
            _insert(main_db, "composite_config_generations", generation_id="gen-pub", generation=1, state="published", verified_at=vt, published_at=pt)
            with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_config_generations.subscription_id")):
                _insert(main_db, "composite_config_generations", generation_id=gid, subscription_id=sid, generation=gen, state=state, verified_at=vt, published_at=pt)
        else:
            _insert(main_db, "composite_config_generations", generation_id=gid, subscription_id=sid, generation=gen, state=state, verified_at=vt, published_at=pt if state in ("published", "retired") else None)
            if case == "retired":
                _insert(main_db, "composite_config_generations", generation_id="gen-retired-2", generation=2, state="retired", verified_at=vt, published_at=pt)
    elif case == "blocked":
        _insert(main_db, "composite_config_generations", state="blocked_uncertain")
    elif case == "invalid":
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_config_generations", state="failed")
    elif case == "null":
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("NOT NULL constraint failed: composite_config_generations.state")):
            _insert(main_db, "composite_config_generations", state=None)
    elif case == "duplicate-generation":
        _insert(main_db, "composite_config_generations")
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_config_generations.subscription_id, composite_config_generations.generation")):
            _insert(main_db, "composite_config_generations", generation_id="gen-dup")


@pytest.mark.parametrize("case", ["published-unverified", "published-unpublished", "complete-unverified", "transition"])
def test_published_generation_was_verified(main_db, case):
    _chain(main_db, until="composite_config_generations")
    _sub2(main_db)
    vt, pt = T0 + 1_000, T0 + 2_000
    if case == "transition":
        _insert(main_db, "composite_config_generations")
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            main_db.execute("UPDATE composite_config_generations SET state='published' WHERE generation_id='gen-1'")
    else:
        values = {"state": "complete_verified", "verified_at": None}
        if case.startswith("published"):
            values["state"] = "published"
            values["published_at"] = pt if case == "published-unverified" else None
            values["verified_at"] = None if case == "published-unverified" else vt
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _insert(main_db, "composite_config_generations", **values)


# Data-model §5–§7 tables (T034c: checks for T038)

SECRET_BLOB = bytes(range(60))  # stands in for an AES-GCM nonce, ciphertext and tag
PREVIOUS_EXPIRY = T0 + 2_592_000_000  # ep-1's expiry
CARRY = {"carried_bytes": 21_474_836_480, "available_bytes": 75_161_927_680}  # 20 GiB carried onto 50 GiB

# One valid row per table, in parent-before-child order. _chain(conn) supplies the §1-§4 parents.
ROWS_5_7 = {
    "composite_meters": {"meter_id": "m-1", "subscription_id": "sub-1", "physical_panel_id": "pp-a", "traffic_key": "cmp1-c7f3a9", "serving_class": "serving", "required_current": 1, "upload_epoch": 0, "download_epoch": 0, "last_observation_id": None, "last_observed_at": None, "failure_state": None, "restart_loss_annotations": None},
    "composite_children": {"child_id": "ch-1", "subscription_id": "sub-1", "logical_node_key": "node-a1", "credential_generation": 1, "physical_panel_id": "pp-a", "remote_email": "cmp1-c7f3a9", "protocol": "vless", "encrypted_secret": SECRET_BLOB, "secret_key_id": "key-v1", "secret_fingerprint": "secret-fp-1", "sub_id_ref": None, "meter_id": "m-1", "desired_state": "enabled", "desired_revision": 1, "confirmed_access": "unknown", "confirmed_at": None, "retired_at": None, "retire_reason": None},
    "composite_child_attachments": {"attachment_id": "att-1", "child_id": "ch-1", "physical_panel_id": "pp-a", "binding_id": "pb-a1", "settings_fingerprint": "settings-fp-a1", "egress_key": "out-de", "expected_member": 1, "confirmed_member": "unknown"},
    "composite_cleanup_obligations": {"obligation_id": "co-1", "child_id": "ch-1", "meter_id": "m-1", "responsible_actor": "main:inst-main", "reason": "terminal_revocation", "desired_outcome": "removed", "status": "open", "disabled_at": None, "final_upload_bytes": None, "final_download_bytes": None, "deleted_at": None, "still_growing_at_delete": None, "next_check_at": None, "escalation_ref": None},
    "composite_observations": {"observation_id": "obs-1", "meter_id": "m-1", "upload_epoch": 0, "download_epoch": 0, "upload_bytes": 1_000, "download_bytes": 8_000, "dispatched_at": T0 - 400, "received_at": T0, "outcome": "accepted", "restart_evidence": None, "evidence_hash": "evidence-1"},
    "composite_entitlement_periods": {"period_id": "ep-1", "subscription_id": "sub-1", "operation_id": "op-1", "grant_kind": "initial_paid", "offer_id": "of-1", "authorized_at": T0 - 60_000, "effective_at": T0, "previous_period_id": None, "previous_expires_at": None, "timely_payment": 0, "purchased_bytes": 53_687_091_200, "purchased_seconds": 2_592_000, "carried_bytes": 0, "carried_ms": 0, "forfeited_ms": 0, "available_bytes": 53_687_091_200, "expires_at": PREVIOUS_EXPIRY, "uncertainty": None},
    "composite_meter_deltas": {"delta_id": "d-1", "meter_id": "m-1", "direction": "upload", "epoch": 0, "predecessor_observation_id": "obs-1", "current_observation_id": "obs-2", "delta_bytes": 500, "interval_start_at": T0, "interval_end_at": T0 + 15_000, "child_id": "ch-1", "period_id": "ep-1", "allocation_state": "attributed"},
    "composite_usage_gaps": {"gap_id": "gap-1", "meter_id": "m-1", "subscription_id": "sub-1", "direction": "download", "before_observation_id": "obs-1", "after_observation_id": "obs-2", "lower_bound_bytes": 0, "upper_bound_bytes": None, "reason": "missing_history", "state": "unresolved", "settled_by": None, "settled_at": None, "settlement_reason": None, "accepted_risk": None, "remaining_uncertainty": None},
    "composite_boundary_readings": {"period_id": "ep-1", "meter_id": "m-1", "direction": "upload", "epoch": 0, "observation_id": "obs-1", "cumulative_bytes": 1_000, "received_at": T0, "age_ms": 0, "required_current": 1},
    "composite_reminder_periods": {"reminder_period_id": "rp-1", "period_id": "ep-1", "grant_kind": "initial_paid", "allowance_bytes": 53_687_091_200, "expires_at": PREVIOUS_EXPIRY},
    "composite_reminders": {"reminder_id": "rm-1", "reminder_period_id": "rp-1", "reminder_type": "expiry", "expiry_threshold_seconds": 432_000, "quota_mode": None, "quota_percent": None, "quota_remaining_bytes": None, "status": "armed", "condition_met_at": None, "due_at": None},
}
CHAIN_5_7 = (
    ("composite_meters", {}), ("composite_children", {}), ("composite_child_attachments", {}),
    ("composite_cleanup_obligations", {}), ("composite_observations", {}),
    ("composite_observations", {"observation_id": "obs-2", "upload_bytes": 1_500, "download_bytes": 9_000, "dispatched_at": T0 + 14_600, "received_at": T0 + 15_000, "evidence_hash": "evidence-2"}),
    ("composite_entitlement_periods", {}), ("composite_meter_deltas", {}), ("composite_usage_gaps", {}),
    ("composite_boundary_readings", {}), ("composite_reminder_periods", {}), ("composite_reminders", {}),
)
EXPECTED_FKS_5_7 = (
    ("composite_meters", ("subscription_id",), "composite_subscriptions", ("subscription_id",)),
    ("composite_meters", ("physical_panel_id",), "composite_physical_panels", ("physical_panel_id",)),
    ("composite_meters", ("last_observation_id",), "composite_observations", ("observation_id",)),
    ("composite_children", ("subscription_id", "logical_node_key"), "composite_subscription_nodes", ("subscription_id", "logical_node_key")),
    ("composite_children", ("physical_panel_id",), "composite_physical_panels", ("physical_panel_id",)),
    ("composite_children", ("meter_id", "subscription_id"), "composite_meters", ("meter_id", "subscription_id")),
    ("composite_child_attachments", ("child_id", "physical_panel_id"), "composite_children", ("child_id", "physical_panel_id")),
    ("composite_child_attachments", ("binding_id", "physical_panel_id"), "composite_prepared_bindings", ("binding_id", "physical_panel_id")),
    ("composite_cleanup_obligations", ("child_id",), "composite_children", ("child_id",)),
    ("composite_cleanup_obligations", ("meter_id",), "composite_meters", ("meter_id",)),
    ("composite_observations", ("meter_id",), "composite_meters", ("meter_id",)),
    ("composite_entitlement_periods", ("subscription_id",), "composite_subscriptions", ("subscription_id",)),
    ("composite_entitlement_periods", ("offer_id",), "composite_offers", ("offer_id",)),
    ("composite_entitlement_periods", ("previous_period_id",), "composite_entitlement_periods", ("period_id",)),
    ("composite_meter_deltas", ("predecessor_observation_id", "meter_id"), "composite_observations", ("observation_id", "meter_id")),
    ("composite_meter_deltas", ("current_observation_id", "meter_id"), "composite_observations", ("observation_id", "meter_id")),
    ("composite_meter_deltas", ("child_id",), "composite_children", ("child_id",)),
    ("composite_meter_deltas", ("period_id",), "composite_entitlement_periods", ("period_id",)),
    ("composite_usage_gaps", ("meter_id", "subscription_id"), "composite_meters", ("meter_id", "subscription_id")),
    ("composite_usage_gaps", ("before_observation_id", "meter_id"), "composite_observations", ("observation_id", "meter_id")),
    ("composite_usage_gaps", ("after_observation_id", "meter_id"), "composite_observations", ("observation_id", "meter_id")),
    ("composite_boundary_readings", ("period_id",), "composite_entitlement_periods", ("period_id",)),
    ("composite_boundary_readings", ("observation_id", "meter_id"), "composite_observations", ("observation_id", "meter_id")),
    ("composite_reminder_periods", ("period_id", "grant_kind"), "composite_entitlement_periods", ("period_id", "grant_kind")),
    ("composite_reminders", ("reminder_period_id",), "composite_reminder_periods", ("reminder_period_id",)),
)

def _put(conn, table, **changes):
    row = {**ROWS_5_7[table], **changes}
    cols = tuple(row)
    marks = ", ".join("?" for _ in cols)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({marks})", tuple(row.values()))


def _chain57(conn, until=None):
    assert until is None or until in ROWS_5_7
    _chain(conn)
    for table, changes in CHAIN_5_7:
        if table == until:
            return
        _put(conn, table, **changes)


def _panel_b(conn):
    _insert(conn, "composite_physical_panels", physical_panel_id="pp-b", authority_fingerprint="authority-fp-b")


def _renewal(remaining, carried_ms, forfeited_ms, expires_extra=0, **changes):
    """A renewal period ep-r after ep-1, applied `remaining` ms before ep-1's expiry."""
    effective = PREVIOUS_EXPIRY - remaining
    row = {"period_id": "ep-r", "operation_id": "op-r", "grant_kind": "renewal", "previous_period_id": "ep-1", "previous_expires_at": PREVIOUS_EXPIRY, "effective_at": effective, "authorized_at": effective - 60_000, "carried_ms": carried_ms, "forfeited_ms": forfeited_ms, "expires_at": effective + 2_592_000_000 + carried_ms + expires_extra}
    return {**row, **changes}


def _fk_missing(conn, table, column, value):
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(conn, table, **{column: value})


def test_main_gets_the_section_5_to_7_tables(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        for table, row in ROWS_5_7.items():
            assert table in _tables(conn)
            assert set(row) <= set(_columns(conn, table))


def test_section_5_to_7_foreign_keys_are_restrict(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        found = set()
        for table in ROWS_5_7:
            grouped = {}
            for row in conn.execute(f"PRAGMA foreign_key_list({table})"):
                grouped.setdefault(row[0], []).append(row)
            for rows in grouped.values():
                rows.sort(key=lambda row: row[1])
                parent = rows[0][2]
                to_cols = tuple(row[4] for row in rows)
                if any(col is None for col in to_cols):
                    to_cols = tuple(r[1] for r in sorted((r for r in conn.execute(f"PRAGMA table_info({parent})") if r[5] > 0), key=lambda r: r[5]))
                found.add((table, tuple(row[3] for row in rows), parent, to_cols))
                assert all(row[6] == "RESTRICT" for row in rows)
        assert set(EXPECTED_FKS_5_7) <= found


def test_rows_in_every_section_5_to_7_table_survive_a_rerun(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _chain57(conn)
        conn.commit()
    before = _dump(install.main)
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(migrations.SCHEMA_VERSION, migrations.SCHEMA_VERSION, "unchanged")
    assert _dump(install.main) == before
    _check_clean(install.main)
    with closing(sqlite3.connect(install.main)) as conn:
        assert _one(conn, "SELECT count(*) FROM composite_observations")[0] == 2
        assert all(_one(conn, f"SELECT count(*) FROM {table}")[0] == 1 for table in ROWS_5_7 if table != "composite_observations")


@pytest.mark.parametrize("sql, table, key", [("DELETE FROM composite_meters WHERE meter_id = 'm-1'", "composite_meters", "meter_id"), ("DELETE FROM composite_observations WHERE observation_id = 'obs-1'", "composite_observations", "observation_id"), ("DELETE FROM composite_entitlement_periods WHERE period_id = 'ep-1'", "composite_entitlement_periods", "period_id"), ("DELETE FROM composite_reminder_periods WHERE reminder_period_id = 'rp-1'", "composite_reminder_periods", "reminder_period_id"), ("DELETE FROM composite_subscription_nodes WHERE subscription_id = 'sub-1' AND logical_node_key = 'node-a1'", "composite_subscription_nodes", "subscription_id")], ids=["meter", "observation", "period", "reminder-period", "subscription-node"])
def test_section_5_to_7_parents_cannot_be_deleted(main_db, sql, table, key):
    _chain57(main_db)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        main_db.execute(sql)
    assert _one(main_db, f"SELECT count(*) FROM {table} WHERE {key} = ?", "sub-1" if table == "composite_subscription_nodes" else ROWS_5_7[table][key])[0] == 1


@pytest.mark.parametrize("child, columns, parent, parent_columns", EXPECTED_FKS_5_7)
def test_section_5_to_7_child_row_needs_its_parent(main_db, child, columns, parent, parent_columns):
    _chain57(main_db, until=child)
    missing = {"composite_subscriptions": "sub-missing", "composite_subscription_nodes": "sub-missing", "composite_physical_panels": "pp-missing", "composite_observations": "obs-missing", "composite_meters": "m-missing", "composite_children": "ch-missing", "composite_prepared_bindings": "pb-missing", "composite_offers": "of-missing", "composite_entitlement_periods": "ep-missing", "composite_reminder_periods": "rp-missing"}[parent]
    _fk_missing(main_db, child, columns[0], missing)


def test_child_remote_identity_is_unique_per_panel(main_db):
    _chain57(main_db, until="composite_child_attachments")
    _panel_b(main_db)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_children.physical_panel_id, composite_children.remote_email")):
        _put(main_db, "composite_children", child_id="ch-2", credential_generation=2, meter_id=None)
    _put(main_db, "composite_children", child_id="ch-3", credential_generation=2, physical_panel_id="pp-b", meter_id=None)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_children.subscription_id, composite_children.logical_node_key, composite_children.credential_generation")):
        _put(main_db, "composite_children", child_id="ch-4", credential_generation=2, remote_email="cmp1-d4", meter_id=None)
    _put(main_db, "composite_children", child_id="ch-5", credential_generation=3, remote_email="cmp1-d4", meter_id=None)


@pytest.mark.parametrize("changes, error", [({"protocol": "vmess"}, None), ({"protocol": "trojan"}, None), ({"desired_state": "disabled"}, None), ({"desired_state": "removed"}, None), ({"confirmed_access": "partial"}, None), ({"confirmed_access": "confirmed_eligible"}, None), ({"confirmed_access": "confirmed_fresh_auth_denied"}, None), ({"retired_at": T0, "retire_reason": "leak_replacement"}, None), ({"meter_id": None}, None), ({"credential_generation": 0}, "CHECK constraint failed"), ({"credential_generation": -1}, "CHECK constraint failed"), ({"credential_generation": 1.5}, "CHECK constraint failed"), ({"protocol": "shadowsocks"}, "CHECK constraint failed"), ({"desired_state": "paused"}, "CHECK constraint failed"), ({"confirmed_access": "confirmed"}, "CHECK constraint failed"), ({"desired_revision": -1}, "CHECK constraint failed"), ({"retired_at": T0}, "CHECK constraint failed"), ({"retire_reason": "leak_replacement"}, "CHECK constraint failed"), ({"encrypted_secret": "plain-secret-text"}, "CHECK constraint failed"), *[({column: None}, re.escape(f"NOT NULL constraint failed: composite_children.{column}")) for column in ("encrypted_secret", "secret_key_id", "remote_email")]], ids=["vmess", "trojan", "disabled", "removed", "partial", "eligible", "denied", "retired", "no-meter", "generation-zero", "generation-negative", "generation-fractional", "protocol-invalid", "state-invalid", "access-invalid", "revision-negative", "retirement-without-reason", "reason-without-retirement", "plaintext-secret", "secret-null", "key-null", "email-null"])
def test_child_column_values(main_db, changes, error):
    _chain57(main_db, until="composite_children")
    if error is None:
        _put(main_db, "composite_children", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_children", **changes)


@pytest.mark.parametrize("column, value, extra", [("remote_email", "cmp1-other", {}), ("physical_panel_id", "pp-b", {}), ("credential_generation", 2, {}), ("logical_node_key", "node-a2", {}), ("subscription_id", "sub-2", {"meter_id": None}), ("protocol", "vmess", {}), ("secret_fingerprint", "secret-fp-2", {})], ids=["email", "panel", "generation", "node", "subscription", "protocol", "fingerprint"])
def test_child_identity_never_changes(main_db, column, value, extra):
    _chain57(main_db, until="composite_child_attachments")
    _panel_b(main_db)
    _insert(main_db, "composite_subscription_nodes", logical_node_key="node-a2")
    _sub2(main_db)
    _insert(main_db, "composite_subscription_nodes", subscription_id="sub-2", logical_node_key="node-a1")
    original = ROWS_5_7["composite_children"][column]
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute(f"UPDATE composite_children SET {column} = ?{', meter_id = NULL' if extra else ''} WHERE child_id = 'ch-1'", (value,))
    assert _one(main_db, f"SELECT {column} FROM composite_children WHERE child_id='ch-1'")[0] == original


def test_children_are_kept_and_their_state_changes(main_db):
    _chain57(main_db, until="composite_child_attachments")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("DELETE FROM composite_children WHERE child_id='ch-1'")
    assert _one(main_db, "SELECT count(*) FROM composite_children WHERE child_id='ch-1'")[0] == 1
    main_db.execute("UPDATE composite_children SET desired_state='disabled', desired_revision=2, confirmed_access='confirmed_fresh_auth_denied', confirmed_at=?, retired_at=?, retire_reason='cancelled' WHERE child_id='ch-1'", (T0 + 5_000, T0 + 5_000))
    assert _one(main_db, "SELECT desired_state, desired_revision, confirmed_access, confirmed_at, retired_at, retire_reason FROM composite_children WHERE child_id='ch-1'") == ("disabled", 2, "confirmed_fresh_auth_denied", T0 + 5_000, T0 + 5_000, "cancelled")


def test_child_meter_belongs_to_the_same_subscription(main_db):
    _chain57(main_db, until="composite_child_attachments")
    _sub2(main_db)
    _insert(main_db, "composite_subscription_nodes", subscription_id="sub-2", logical_node_key="node-a1")
    _put(main_db, "composite_meters", meter_id="m-2", subscription_id="sub-2", traffic_key="cmp1-b2")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_children", child_id="ch-2", subscription_id="sub-2", remote_email="cmp1-b2", meter_id="m-1")
    _put(main_db, "composite_children", child_id="ch-2", subscription_id="sub-2", remote_email="cmp1-b2", meter_id="m-2")
    _put(main_db, "composite_children", child_id="ch-3", credential_generation=2, remote_email="cmp1-c3", meter_id=None)


def test_attachment_inbound_is_on_the_child_panel(main_db):
    _chain57(main_db, until="composite_child_attachments")
    _panel_b(main_db)
    _insert(main_db, "composite_prepared_bindings", binding_id="pb-b1", physical_panel_id="pp-b")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_child_attachments", attachment_id="att-x", binding_id="pb-b1")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_child_attachments", attachment_id="att-y", binding_id="pb-b1", physical_panel_id="pp-b")
    _put(main_db, "composite_child_attachments")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_child_attachments.child_id, composite_child_attachments.binding_id")):
        _put(main_db, "composite_child_attachments", attachment_id="att-2")
    _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
    _put(main_db, "composite_child_attachments", attachment_id="att-3", binding_id="pb-a2")


@pytest.mark.parametrize("changes, error", [({"expected_member": 0}, None), ({"confirmed_member": "present"}, None), ({"confirmed_member": "absent"}, None), ({"expected_member": 2}, "CHECK constraint failed"), ({"confirmed_member": "maybe"}, "CHECK constraint failed"), ({"expected_member": None}, re.escape("NOT NULL constraint failed: composite_child_attachments.expected_member"))], ids=["not-expected", "present", "absent", "invalid-expected", "invalid-confirmed", "null-expected"])
def test_attachment_membership_values(main_db, changes, error):
    _chain57(main_db, until="composite_child_attachments")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_child_attachments", **changes)
    else:
        _put(main_db, "composite_child_attachments", **changes)


@pytest.mark.parametrize("changes, error", [({"status": "escalated"}, None), ({"desired_outcome": "fresh_auth_denied"}, None), ({"meter_id": None}, None), ({"status": "done"}, "CHECK constraint failed"), ({"desired_outcome": "ignored"}, "CHECK constraint failed"), ({"responsible_actor": None}, re.escape("NOT NULL constraint failed: composite_cleanup_obligations.responsible_actor")), ({"reason": None}, re.escape("NOT NULL constraint failed: composite_cleanup_obligations.reason"))], ids=["escalated", "denied", "no-meter", "bad-status", "bad-outcome", "no-actor", "no-reason"])
def test_cleanup_obligation_values(main_db, changes, error):
    _chain57(main_db, until="composite_cleanup_obligations")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_cleanup_obligations", **changes)
    else:
        _put(main_db, "composite_cleanup_obligations", **changes)


CLEANUP_ACCEPTED = [(T0, None, None, None, None), (T0, 4_000, 9_000, T0 + 120_000, 0), (T0, 4_000, 9_000, T0 + 1_800_000, 1)]
CLEANUP_REJECTED = [(None, 4_000, 9_000, T0 + 120_000, 0), (T0, 4_000, 9_000, T0 - 1, 0), (T0, None, 9_000, T0 + 120_000, 0), (T0, 4_000, None, T0 + 120_000, 0), (T0, 4_000, 9_000, T0 + 120_000, None), (T0, 4_000, 9_000, None, 0), (T0, 4_000, 9_000, T0 + 120_000, 2), (T0, -1, 9_000, None, None)]

@pytest.mark.parametrize("values, accepted", [(v, True) for v in CLEANUP_ACCEPTED] + [(v, False) for v in CLEANUP_REJECTED], ids=["valid-disabled", "valid-removed-settled", "valid-growing"] + [f"invalid-{i}" for i in range(8)])
def test_cleanup_disables_reads_then_deletes(main_db, values, accepted):
    _chain57(main_db, until="composite_cleanup_obligations")
    names = ("disabled_at", "final_upload_bytes", "final_download_bytes", "deleted_at", "still_growing_at_delete")
    changes = dict(zip(names, values))
    if accepted:
        _put(main_db, "composite_cleanup_obligations", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_cleanup_obligations", **changes)


@pytest.mark.parametrize("outcome, values, accepted", [("removed", (T0, 4_000, 9_000, T0 + 120_000, 0), True), ("fresh_auth_denied", (T0, None, None, None, None), True), ("removed", (T0, None, None, None, None), False), ("fresh_auth_denied", (None, None, None, None, None), False)], ids=["removed-complete", "denied", "removed-incomplete", "denied-unrecorded"])
def test_cleanup_resolution_needs_its_outcome(main_db, outcome, values, accepted):
    _chain57(main_db, until="composite_cleanup_obligations")
    names = ("disabled_at", "final_upload_bytes", "final_download_bytes", "deleted_at", "still_growing_at_delete")
    if not accepted:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_cleanup_obligations", status="resolved", desired_outcome=outcome, **dict(zip(names, values)))
    else:
        _put(main_db, "composite_cleanup_obligations", status="resolved", desired_outcome=outcome, **dict(zip(names, values)))


def test_cleanup_obligations_are_never_erased(main_db):
    _chain57(main_db, until="composite_observations")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("DELETE FROM composite_cleanup_obligations WHERE obligation_id='co-1'")
    main_db.execute("UPDATE composite_subscriptions SET lifecycle='cancelled', cancel_accepted_at=?, cancel_final_started_at=? WHERE subscription_id='sub-1'", (T0, T0))
    assert _one(main_db, "SELECT status FROM composite_cleanup_obligations WHERE obligation_id='co-1'")[0] == "open"
    main_db.execute("UPDATE composite_cleanup_obligations SET disabled_at=?, final_upload_bytes=4000, final_download_bytes=9000, deleted_at=?, still_growing_at_delete=0, status='resolved' WHERE obligation_id='co-1'", (T0, T0 + 120_000))


def test_meter_bucket_has_one_owner(main_db):
    _chain57(main_db, until="composite_children")
    _sub2(main_db)
    _panel_b(main_db)
    for meter_id, subscription_id in (("m-2", "sub-2"), ("m-3", "sub-1")):
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_meters.physical_panel_id, composite_meters.traffic_key")):
            _put(main_db, "composite_meters", meter_id=meter_id, subscription_id=subscription_id)
    _put(main_db, "composite_meters", meter_id="m-4", subscription_id="sub-2", physical_panel_id="pp-b")
    _put(main_db, "composite_meters", meter_id="m-5", subscription_id="sub-2", traffic_key="cmp1-b5")


@pytest.mark.parametrize("changes, error", [({"serving_class": "retired", "required_current": 0}, None), ({"serving_class": "emergency_exposure", "required_current": 0}, None), ({"serving_class": "serving", "required_current": 0}, None), ({"serving_class": "retired", "required_current": 1}, "CHECK constraint failed"), ({"serving_class": "emergency_exposure", "required_current": 1}, "CHECK constraint failed"), ({"serving_class": "stale", "required_current": 0}, "CHECK constraint failed"), ({"required_current": 2}, "CHECK constraint failed"), ({"upload_epoch": -1}, "CHECK constraint failed"), ({"download_epoch": 1.5}, "CHECK constraint failed"), ({"traffic_key": None}, re.escape("NOT NULL constraint failed: composite_meters.traffic_key")), ({"serving_class": None}, re.escape("NOT NULL constraint failed: composite_meters.serving_class"))], ids=["retired", "exposure", "serving-optional", "retired-required", "exposure-required", "bad-class", "bad-required", "upload-negative", "download-fractional", "no-key", "no-class"])
def test_meter_values(main_db, changes, error):
    _chain57(main_db, until="composite_meters")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_meters", **changes)
    else:
        _put(main_db, "composite_meters", **changes)


@pytest.mark.parametrize("changes, error", [({"upload_bytes": 0, "download_bytes": 0}, None), ({"download_bytes": 9_223_372_036_854_775_807}, None), ({"received_at": T0 + 15_000}, None), ({"upload_bytes": -1}, "CHECK constraint failed"), ({"download_bytes": 1.5}, "CHECK constraint failed"), ({"upload_bytes": "n/a"}, "CHECK constraint failed"), ({"upload_epoch": -1}, "CHECK constraint failed"), ({"upload_bytes": None}, re.escape("NOT NULL constraint failed: composite_observations.upload_bytes")), ({"download_bytes": None}, re.escape("NOT NULL constraint failed: composite_observations.download_bytes"))], ids=["zero", "max-int", "unchanged-fresh", "negative", "fractional", "text", "epoch-negative", "upload-null", "download-null"])
def test_observation_totals_are_signed_64_bit_integers(main_db, changes, error):
    _chain57(main_db, until="composite_observations")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_observations", **changes)
    else:
        _put(main_db, "composite_observations", **changes)
    # SQLite parses an out-of-range integer literal as REAL; bind-time overflow would bypass the constraint.
    if changes == {"upload_epoch": -1}:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            main_db.execute("INSERT INTO composite_observations (observation_id, meter_id, upload_epoch, download_epoch, upload_bytes, download_bytes, received_at, outcome, evidence_hash) VALUES ('obs-big', 'm-1', 0, 0, 9223372036854775808, 0, ?, 'accepted', 'evidence-big')", (T0,))


@pytest.mark.parametrize("changes, error", [({"outcome": "out_of_order"}, None), ({"dispatched_at": None}, None), ({"received_at": "2026-10-30T00:00:15Z"}, "CHECK constraint failed"), ({"received_at": T0 + 15_000.5}, "CHECK constraint failed"), ({"outcome": "failed"}, "CHECK constraint failed"), ({"outcome": "timeout"}, "CHECK constraint failed"), ({"received_at": None}, re.escape("NOT NULL constraint failed: composite_observations.received_at")), ({"outcome": None}, re.escape("NOT NULL constraint failed: composite_observations.outcome")), ({"evidence_hash": None}, re.escape("NOT NULL constraint failed: composite_observations.evidence_hash"))], ids=["late", "no-dispatch", "text-time", "fractional-time", "failed", "timeout", "no-receipt", "no-outcome", "no-evidence"])
def test_observation_time_and_outcome(main_db, changes, error):
    _chain57(main_db, until="composite_observations")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_observations", **changes)
    else:
        _put(main_db, "composite_observations", **changes)


def test_observations_are_never_rewritten(main_db):
    _chain57(main_db, until="composite_entitlement_periods")
    expected = (1_500, T0 + 15_000, "accepted")
    for sql in ("UPDATE composite_observations SET upload_bytes=1200 WHERE observation_id='obs-2'", f"UPDATE composite_observations SET received_at={T0 + 16_000} WHERE observation_id='obs-2'", "UPDATE composite_observations SET outcome='out_of_order' WHERE observation_id='obs-2'"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute(sql)
        assert _one(main_db, "SELECT upload_bytes, received_at, outcome FROM composite_observations WHERE observation_id='obs-2'") == expected
    _put(main_db, "composite_observations", observation_id="obs-3", outcome="out_of_order", upload_bytes=1_400, download_bytes=8_900, received_at=T0 + 14_000, evidence_hash="evidence-3")


def test_delta_is_unique_per_meter_direction_epoch_and_predecessor(main_db):
    _chain57(main_db, until="composite_usage_gaps")
    _put(main_db, "composite_observations", observation_id="obs-3", upload_bytes=2_000, download_bytes=9_500, received_at=T0 + 30_000, evidence_hash="evidence-3")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_meter_deltas.meter_id, composite_meter_deltas.direction, composite_meter_deltas.epoch, composite_meter_deltas.predecessor_observation_id")):
        _put(main_db, "composite_meter_deltas", delta_id="d-2", current_observation_id="obs-3")
    _put(main_db, "composite_meter_deltas", delta_id="d-3", direction="download", delta_bytes=1_000)
    _put(main_db, "composite_meter_deltas", delta_id="d-4", epoch=1)
    _put(main_db, "composite_meter_deltas", delta_id="d-5", predecessor_observation_id="obs-2", current_observation_id="obs-3")


@pytest.mark.parametrize("changes, error", [({"delta_bytes": 0}, None), ({"allocation_state": "absorbed_exposure"}, None), ({"allocation_state": "gap_affected"}, None), ({"period_id": None}, None), ({"delta_bytes": -1}, "CHECK constraint failed"), ({"delta_bytes": 1.5}, "CHECK constraint failed"), ({"allocation_state": "carried"}, "CHECK constraint failed"), ({"direction": "both"}, "CHECK constraint failed"), ({"epoch": -1}, "CHECK constraint failed"), ({"predecessor_observation_id": "obs-2"}, "CHECK constraint failed"), ({"allocation_state": None}, re.escape("NOT NULL constraint failed: composite_meter_deltas.allocation_state")), ({"child_id": None}, re.escape("NOT NULL constraint failed: composite_meter_deltas.child_id"))], ids=["zero", "exposure", "gap", "no-period", "negative", "fractional", "carried", "both", "epoch", "same-observation", "no-allocation", "no-child"])
def test_delta_values(main_db, changes, error):
    _chain57(main_db, until="composite_meter_deltas")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_meter_deltas", **changes)
    else:
        _put(main_db, "composite_meter_deltas", **changes)


def test_delta_uses_observations_of_its_own_meter(main_db):
    _chain57(main_db, until="composite_meter_deltas")
    _put(main_db, "composite_meters", meter_id="m-2", traffic_key="cmp1-m2", serving_class="retired", required_current=0)
    _put(main_db, "composite_observations", observation_id="obs-m2a", meter_id="m-2", received_at=T0, evidence_hash="evidence-m2a")
    _put(main_db, "composite_observations", observation_id="obs-m2b", meter_id="m-2", received_at=T0 + 15_000, evidence_hash="evidence-m2b")
    for delta_id, meter, prev, curr in (("d-x", "m-1", "obs-1", "obs-m2b"), ("d-y", "m-1", "obs-m2a", "obs-2"), ("d-z", "m-2", "obs-1", "obs-2")):
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
            _put(main_db, "composite_meter_deltas", delta_id=delta_id, meter_id=meter, predecessor_observation_id=prev, current_observation_id=curr)
    _put(main_db, "composite_meter_deltas", delta_id="d-m2", meter_id="m-2", predecessor_observation_id="obs-m2a", current_observation_id="obs-m2b")


def test_deltas_are_kept_and_their_bytes_never_change(main_db):
    _chain57(main_db)
    for sql in ("DELETE FROM composite_meter_deltas WHERE delta_id='d-1'", "UPDATE composite_meter_deltas SET delta_bytes=400 WHERE delta_id='d-1'", "UPDATE composite_meter_deltas SET epoch=1 WHERE delta_id='d-1'", "UPDATE composite_meter_deltas SET direction='download' WHERE delta_id='d-1'"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute(sql)
        assert _one(main_db, "SELECT delta_bytes, epoch, direction FROM composite_meter_deltas WHERE delta_id='d-1'") == (500, 0, "upload")
    main_db.execute("UPDATE composite_meter_deltas SET allocation_state='gap_affected', period_id=NULL WHERE delta_id='d-1'")


@pytest.mark.parametrize("changes, error", [({"reason": "decrease"}, None), ({"reason": "reset"}, None), ({"lower_bound_bytes": 500, "upper_bound_bytes": 500}, None), ({"lower_bound_bytes": 500, "upper_bound_bytes": 600}, None), ({"state": "usage_settled", "settled_by": "web:owner-1", "settled_at": T0+3_600_000, "settlement_reason": "panel history lost", "accepted_risk": "store absorbs the unknown usage"}, None), ({"before_observation_id": None, "after_observation_id": None}, None), ({"reason": "restart_loss"}, "CHECK constraint failed"), ({"state": "resolved"}, "CHECK constraint failed"), ({"direction": "both"}, "CHECK constraint failed"), ({"lower_bound_bytes": -1}, "CHECK constraint failed"), ({"lower_bound_bytes": 500, "upper_bound_bytes": 400}, "CHECK constraint failed"), *[({"state": "usage_settled", "settled_by": "web:owner-1", "settled_at": T0+3_600_000, "settlement_reason": "panel history lost", "accepted_risk": "store absorbs the unknown usage", column: None}, "CHECK constraint failed") for column in ("settled_by", "settled_at", "settlement_reason", "accepted_risk")], ({"lower_bound_bytes": None}, re.escape("NOT NULL constraint failed: composite_usage_gaps.lower_bound_bytes"))], ids=["decrease", "reset", "equal-bound", "upper-bound", "settled", "no-brackets", "restart-loss", "bad-state", "both", "negative", "upper-too-low", "no-settled-by", "no-settled-at", "no-reason", "no-risk", "no-lower-bound"])
def test_usage_gap_values(main_db, changes, error):
    _chain57(main_db, until="composite_usage_gaps")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_usage_gaps", **changes)
    else:
        _put(main_db, "composite_usage_gaps", **changes)


def test_usage_gap_belongs_to_the_meter_owner_and_is_kept(main_db):
    _chain57(main_db)
    _sub2(main_db)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_usage_gaps", gap_id="gap-x", subscription_id="sub-2")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("DELETE FROM composite_usage_gaps WHERE gap_id='gap-1'")
    assert _one(main_db, "SELECT count(*) FROM composite_usage_gaps WHERE gap_id='gap-1'")[0] == 1
    main_db.execute("UPDATE composite_usage_gaps SET state='usage_settled', settled_by='web:owner-1', settled_at=?, settlement_reason='panel history lost', accepted_risk='store absorbs the unknown usage' WHERE gap_id='gap-1'", (T0 + 3_600_000,))


@pytest.mark.parametrize("kind, operation, accepted, error", [("initial_test", "op-t", True, None), ("renewal", "op-r", True, None), ("conversion", "op-c", True, None), ("refund", "op-z", False, "CHECK constraint failed"), (None, "op-z", False, re.escape("NOT NULL constraint failed: composite_entitlement_periods.grant_kind"))], ids=["test", "renewal", "conversion", "invalid", "null"])
def test_entitlement_period_kind_and_operation(main_db, kind, operation, accepted, error):
    _chain57(main_db, until="composite_meter_deltas")
    if accepted:
        _put(main_db, "composite_entitlement_periods", period_id=f"ep-{operation}", operation_id=operation, grant_kind=kind)
    else:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_entitlement_periods", period_id=f"ep-{operation}", operation_id=operation, grant_kind=kind)
    if kind == "initial_test":
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_entitlement_periods.operation_id")):
            _put(main_db, "composite_entitlement_periods", period_id="ep-dup", operation_id="op-1")


@pytest.mark.parametrize("changes, accepted", [(_renewal(907_200_000, 907_200_000, 0, **CARRY), True), (_renewal(907_200_000, 907_200_000, 0, carried_bytes=21_474_836_480), False), (_renewal(907_200_000, 907_200_000, 0, **{**CARRY, "available_bytes": 75_161_927_681}), False), (_renewal(907_200_000, 907_200_000, 0, purchased_bytes=0, carried_bytes=21_474_836_480, available_bytes=21_474_836_480), False), (_renewal(907_200_000, 907_200_000, 0, carried_bytes=-1, available_bytes=53_687_091_199), False)], ids=["sum", "carry-not-added", "wrong-sum", "zero-purchased", "negative-carry"])
def test_period_allowance_is_new_plus_carried(main_db, changes, accepted):
    _chain57(main_db, until="composite_meter_deltas")
    if accepted:
        _put(main_db, "composite_entitlement_periods", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_entitlement_periods", **changes)


@pytest.mark.parametrize("changes, accepted", [(_renewal(907_200_000, 907_200_000, 0), True), (_renewal(1_728_000_000, 1_296_000_000, 432_000_000), True), (_renewal(1_296_000_000, 1_296_000_000, 0), True), (_renewal(907_200_500, 907_200_500, 0), True), (_renewal(0, 0, 0), True), (_renewal(-1_000, 0, 0), True), (_renewal(907_200_500, 907_200_000, 500), False), (_renewal(1_728_000_000, 1_728_000_000, 0), False), (_renewal(1_728_000_000, 1_296_000_000, 0), False), (_renewal(907_200_000, 0, 907_200_000), False), (_renewal(907_200_000, 907_200_000, 0, expires_extra=1), False), (_renewal(907_200_000, 907_200_000, 0, expires_extra=-1), False), (_renewal(-1_000, 0, 1_000), False), ({**ROWS_5_7["composite_entitlement_periods"], "period_id": "ep-x", "operation_id": "op-x", "carried_ms": 1, "expires_at": PREVIOUS_EXPIRY + 1}, False)], ids=["10d12h", "20d-cap", "15d", "fractional-ms", "at-expiry", "expired", "fractional-forfeit", "over-cap", "missing-forfeit", "all-forfeited", "expiry-plus-ms", "expiry-minus-ms", "expired-forfeit", "initial-no-carry"])
def test_renewal_expiry_follows_the_45_day_cap(main_db, changes, accepted):
    _chain57(main_db, until="composite_meter_deltas")
    if accepted:
        _put(main_db, "composite_entitlement_periods", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_entitlement_periods", **changes)


@pytest.mark.parametrize("changes, accepted", [(_renewal(907_200_000, 907_200_000, 0, **CARRY), True), (_renewal(-60_000, 0, 0, timely_payment=1, authorized_at=PREVIOUS_EXPIRY-1, **CARRY), True), (_renewal(-60_000, 0, 0, timely_payment=1, authorized_at=PREVIOUS_EXPIRY-1), True), (_renewal(-60_000, 0, 0, **CARRY), False), (_renewal(0, 0, 0, **CARRY), False), (_renewal(-60_000, 0, 0, timely_payment=1, authorized_at=PREVIOUS_EXPIRY, **CARRY), False), (_renewal(-60_000, 0, 0, timely_payment=1, authorized_at=None), False), (_renewal(907_200_000, 907_200_000, 0, timely_payment=2), False), ({**ROWS_5_7["composite_entitlement_periods"], "period_id": "ep-x", "operation_id": "op-x", "carried_bytes": 1, "available_bytes": 53_687_091_201}, False)], ids=["valid-old-term", "timely-expired-carry", "timely-no-carry", "late-carry", "at-expiry-carry", "authorized-at-expiry", "missing-authorization", "bad-flag", "bytes-carried"])
def test_carryover_needs_a_valid_old_term_or_timely_payment(main_db, changes, accepted):
    _chain57(main_db, until="composite_meter_deltas")
    if accepted:
        _put(main_db, "composite_entitlement_periods", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_entitlement_periods", **changes)


def test_boundary_reading_is_unique_per_period_meter_and_direction(main_db):
    _chain57(main_db, until="composite_reminder_periods")
    _put(main_db, "composite_meters", meter_id="m-2", traffic_key="cmp1-m2")
    _put(main_db, "composite_observations", observation_id="obs-m2a", meter_id="m-2", evidence_hash="evidence-m2a")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_boundary_readings.period_id, composite_boundary_readings.meter_id, composite_boundary_readings.direction")):
        _put(main_db, "composite_boundary_readings", observation_id="obs-2", cumulative_bytes=1_500, received_at=T0+15_000)
    _put(main_db, "composite_boundary_readings", direction="download", cumulative_bytes=8_000)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_boundary_readings", meter_id="m-2", observation_id="obs-1")
    _put(main_db, "composite_boundary_readings", meter_id="m-2", observation_id="obs-m2a")


@pytest.mark.parametrize("changes, error", [({"required_current": 1, "age_ms": 60_000}, None), ({"required_current": 0, "age_ms": 120_000}, None), ({"epoch": 3}, None), ({"required_current": 1, "age_ms": 60_001}, "CHECK constraint failed"), ({"required_current": 0, "age_ms": -1}, "CHECK constraint failed"), ({"required_current": 2}, "CHECK constraint failed"), ({"direction": "both"}, "CHECK constraint failed"), ({"cumulative_bytes": -1}, "CHECK constraint failed"), ({"epoch": -1}, "CHECK constraint failed"), ({"cumulative_bytes": None}, re.escape("NOT NULL constraint failed: composite_boundary_readings.cumulative_bytes")), ({"age_ms": None}, re.escape("NOT NULL constraint failed: composite_boundary_readings.age_ms"))], ids=["fresh-required", "stale-retired", "epoch", "stale-required", "negative-age", "bad-required", "both", "negative-bytes", "negative-epoch", "no-cumulative", "no-age"])
def test_boundary_reading_values(main_db, changes, error):
    _chain57(main_db, until="composite_boundary_readings")
    if error:
        with pytest.raises(sqlite3.IntegrityError, match=error):
            _put(main_db, "composite_boundary_readings", **changes)
    else:
        _put(main_db, "composite_boundary_readings", **changes)


def test_boundary_readings_are_immutable(main_db):
    _chain57(main_db)
    for sql in ("UPDATE composite_boundary_readings SET cumulative_bytes=1500", "UPDATE composite_boundary_readings SET age_ms=5000", "UPDATE composite_boundary_readings SET observation_id='obs-2'", "DELETE FROM composite_boundary_readings"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute(sql)
        assert _one(main_db, "SELECT cumulative_bytes, age_ms, observation_id FROM composite_boundary_readings") == (1_000, 0, "obs-1")


def test_reminder_period_is_one_per_paid_period(main_db):
    _chain57(main_db, until="composite_reminder_periods")
    _put(main_db, "composite_reminder_periods")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_reminder_periods.period_id")):
        _put(main_db, "composite_reminder_periods", reminder_period_id="rp-2")
    _put(main_db, "composite_entitlement_periods", period_id="ep-t", operation_id="op-t", grant_kind="initial_test")
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        _put(main_db, "composite_reminder_periods", reminder_period_id="rp-t", period_id="ep-t", grant_kind="initial_test")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put(main_db, "composite_reminder_periods", reminder_period_id="rp-t2", period_id="ep-t")
    for period_id, kind in (("ep-r", "renewal"), ("ep-c", "conversion")):
        _put(main_db, "composite_entitlement_periods", period_id=period_id, operation_id=f"op-{kind}", grant_kind=kind)
        _put(main_db, "composite_reminder_periods", reminder_period_id=f"rp-{kind}", period_id=period_id, grant_kind=kind)
    _put(main_db, "composite_entitlement_periods", period_id="ep-z", operation_id="op-z")
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        _put(main_db, "composite_reminder_periods", reminder_period_id="rp-z", period_id="ep-z", allowance_bytes=0)


def test_reminder_is_one_per_period_and_type(main_db):
    _chain57(main_db)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_reminders.reminder_period_id, composite_reminders.reminder_type")):
        _put(main_db, "composite_reminders", reminder_id="rm-2")
    _put(main_db, "composite_reminders", reminder_id="rm-3", reminder_type="quota", expiry_threshold_seconds=None, quota_mode="percent", quota_percent=80)
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        _put(main_db, "composite_reminders", reminder_id="rm-4", reminder_type="renewal", expiry_threshold_seconds=None, quota_mode="percent", quota_percent=80)


@pytest.mark.parametrize("changes, accepted", [({}, True), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent", "quota_percent": 80}, True), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent", "quota_percent": 100}, True), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "remaining_bytes", "quota_remaining_bytes": 2_147_483_648}, True), ({"quota_mode": "percent", "quota_percent": 80}, False), ({"expiry_threshold_seconds": None}, False), ({"expiry_threshold_seconds": 0}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_percent": 80}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent", "quota_percent": 80, "quota_remaining_bytes": 2_147_483_648}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "remaining_bytes", "quota_remaining_bytes": 2_147_483_648, "quota_percent": 80}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent"}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent", "quota_percent": 0}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "percent", "quota_percent": 101}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "remaining_bytes", "quota_remaining_bytes": 0}, False), ({"reminder_type": "quota", "expiry_threshold_seconds": None, "quota_mode": "lifetime", "quota_percent": 80}, False), ({"reminder_type": "quota", "quota_mode": "percent", "quota_percent": 80, "expiry_threshold_seconds": 432_000}, False)], ids=["expiry-base", "percent-80", "percent-100", "remaining-2gib", "expiry-with-quota", "expiry-no-threshold", "expiry-zero", "quota-no-mode", "both-quota-values", "remaining-with-percent", "percent-no-value", "percent-zero", "percent-over", "remaining-zero", "lifetime", "quota-with-expiry"])
def test_reminder_threshold_snapshot(main_db, changes, accepted):
    _chain57(main_db, until="composite_reminders")
    if accepted:
        _put(main_db, "composite_reminders", **changes)
    else:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            _put(main_db, "composite_reminders", **changes)


def test_reminder_due_time_and_acceptance_are_final(main_db):
    _chain57(main_db)
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        main_db.execute("UPDATE composite_reminders SET status='due' WHERE reminder_id='rm-1'")
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        main_db.execute(f"UPDATE composite_reminders SET condition_met_at={T0+2_000}, due_at={T0+1_000}, status='due' WHERE reminder_id='rm-1'")
    main_db.execute(f"UPDATE composite_reminders SET condition_met_at={T0+1_000}, due_at={T0+1_000}, status='due' WHERE reminder_id='rm-1'")
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute(f"UPDATE composite_reminders SET due_at={T0+2_000} WHERE reminder_id='rm-1'")
    assert _one(main_db, "SELECT due_at FROM composite_reminders WHERE reminder_id='rm-1'")[0] == T0 + 1_000
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        main_db.execute("UPDATE composite_reminders SET status='sent' WHERE reminder_id='rm-1'")
    main_db.execute("UPDATE composite_reminders SET status='accepted' WHERE reminder_id='rm-1'")
    for status in ("armed", "due", "cancelled"):
        with pytest.raises(sqlite3.IntegrityError):
            main_db.execute("UPDATE composite_reminders SET status=? WHERE reminder_id='rm-1'", (status,))
        assert _one(main_db, "SELECT status FROM composite_reminders WHERE reminder_id='rm-1'")[0] == "accepted"
    with pytest.raises(sqlite3.IntegrityError):
        main_db.execute("DELETE FROM composite_reminders WHERE reminder_id='rm-1'")
    _put(main_db, "composite_reminders", reminder_id="rm-q", reminder_type="quota", expiry_threshold_seconds=None, quota_mode="percent", quota_percent=80)
    main_db.execute("UPDATE composite_reminders SET status='cancelled' WHERE reminder_id='rm-q'")


# Data-model §8–§9 tables (T034d: checks for T039)

QUOTE_RULES = '{"rate": "10/1", "charges": [2000], "offset": 0, "rounding": "none"}'
# One valid row per table, in parent-before-child order. _chain89(conn) supplies the parents.
ROWS_8_9 = {
    "composite_checkouts": {"checkout_id": "ck-1", "order_id": 101, "tenant_installation_id": "inst-main", "customer_telegram_id": 50001, "offer_id": "of-1", "kind": "initial", "target_subscription_id": None, "principal": "telegram:50001", "request_key": "confirm-1", "status": "awaiting_payment", "final_price": 225_000, "wallet_amount": 30_000, "authorization_source": None, "authorized_at": None, "deadline_at": None, "original_receipt_id": None, "fulfillment_operation_id": None, "terminal_reason": None, "terminal_at": None, "created_at": T0},
    "composite_payment_attempts": {"attempt_id": "pa-1", "checkout_id": "ck-1", "method": "card_to_card", "provider": "manual-card", "merchant_namespace": "card-ns-1", "config_version": "cfg-1", "creation_intent": "intent-pa-1", "provider_invoice_ref": "inv-1", "create_state": "created", "native_amount": 1_970_000, "currency": "IRR", "minor_unit_scale": 0, "store_remainder": 195_000, "invoice_value": 197_000, "quote_rules": QUOTE_RULES, "quote_version": "quote-v1", "quote_accepted_at": T0 + 1_000, "valid_until": None, "recovery_ref": None, "status": "open"},
    "composite_manual_decisions": {"decision_id": "md-1", "attempt_id": "pa-1", "principal": "web:owner-1", "principal_role": "owner", "interface": "web", "provider_reference": "bank-ref-1", "evidence_digest": "evidence-md-1", "tenant_installation_id": "inst-main", "customer_telegram_id": 50001, "amount": 1_970_000, "currency": "IRR", "method": "card_to_card", "decision": "approved", "reason": None, "decided_at": T0 + 60_000, "idempotency_key": "decide-1"},
    "composite_payment_receipts": {"receipt_id": "rc-1", "attempt_id": "pa-1", "checkout_id": "ck-1", "provider": "manual-card", "merchant_namespace": "card-ns-1", "transaction_reference": "bank-ref-1", "tenant_installation_id": "inst-main", "beneficiary_telegram_id": 50001, "native_amount": 1_970_000, "currency": "IRR", "invoice_value": 197_000, "verification_source": "manual", "manual_decision_id": "md-1", "evidence_digest": "evidence-rc-1", "verified_at": T0 + 60_000, "outcome": "original_funding"},
    "financial_obligations": {"obligation_id": "fo-1", "effect_key": "wallet_debit:ck-1", "tenant_installation_id": "inst-main", "beneficiary_telegram_id": 50001, "kind": "wallet_debit", "amount": 30_000, "evidence_ref": None, "checkout_id": "ck-1", "receipt_id": None, "batch_ref": None, "member_ref": None, "triggered_at": T0, "due_at": T0, "state": "owed", "ledger_seq": None, "settled_at": None},
    "wallet_effects": {"ledger_seq": 1, "obligation_id": "fo-1", "beneficiary_telegram_id": 50001, "kind": "wallet_debit", "amount": 30_000, "balance_before": 42_000, "balance_after": 12_000, "applied_at": T0},
    "composite_campaigns": {"campaign_id": "cmp-1", "plan_id": "cp-camp", "plan_kind": "campaign", "lifetime_cap": 150, "served_count": 0, "closed_at": None, "history_verified_at": T0},
    "composite_test_claims": {"claim_id": "tc-1", "tenant_installation_id": "inst-main", "customer_telegram_id": 50001, "offer_id": "of-t1", "campaign_id": "cmp-1", "accepted_seq": 1, "accepted_at": T0, "deadline_at": T0 + 900_000, "status": "fulfilled", "fulfilled_at": T0 + 300_000, "retrieval_evidence": "retrieved-tc-1", "terminal_at": None, "terminal_reason": None},
    "resource_reservations": {"reservation_id": "rr-1", "resource": "coupon", "checkout_id": "ck-1", "claim_id": None, "legacy_order_id": None, "legacy_test_ref": None, "tenant_installation_id": "inst-main", "customer_telegram_id": 50001, "coupon_code_id": 7, "campaign_id": None, "sequence": 1, "accepted_at": T0, "state": "held", "transition_key": None, "transitioned_at": None},
    "composite_campaign_recipients": {"campaign_id": "cmp-1", "customer_telegram_id": 50001, "claim_id": "tc-1", "claim_status": "fulfilled", "fulfilled_at": T0 + 300_000},
}
CLAIM_HOLD = {"checkout_id": None, "coupon_code_id": None, "claim_id": "tc-1", "state": "consumed", "transition_key": "fulfil:tc-1", "transitioned_at": T0 + 300_000}
# _chain89 inserts these in order: rr-2 and rr-3 are tc-1's ordinary-test and campaign-place holds.
CHAIN_8_9 = (("composite_checkouts", {}), ("composite_payment_attempts", {}), ("composite_manual_decisions", {}), ("composite_payment_receipts", {}), ("financial_obligations", {}), ("wallet_effects", {}), ("composite_campaigns", {}), ("composite_test_claims", {}), ("resource_reservations", {}), ("resource_reservations", {"reservation_id": "rr-2", "resource": "ordinary_test", "sequence": 2, **CLAIM_HOLD}), ("resource_reservations", {"reservation_id": "rr-3", "resource": "campaign_place", "campaign_id": "cmp-1", "sequence": 3, **CLAIM_HOLD}), ("composite_campaign_recipients", {}))
EXPECTED_FKS_8_9 = (
    ("composite_checkouts", ("order_id",), "orders", ("id",)), ("composite_checkouts", ("offer_id",), "composite_offers", ("offer_id",)), ("composite_checkouts", ("target_subscription_id",), "composite_subscriptions", ("subscription_id",)), ("composite_checkouts", ("original_receipt_id", "checkout_id"), "composite_payment_receipts", ("receipt_id", "checkout_id")),
    ("composite_payment_attempts", ("checkout_id",), "composite_checkouts", ("checkout_id",)), ("composite_manual_decisions", ("attempt_id",), "composite_payment_attempts", ("attempt_id",)), ("composite_payment_receipts", ("attempt_id", "checkout_id"), "composite_payment_attempts", ("attempt_id", "checkout_id")), ("composite_payment_receipts", ("manual_decision_id", "attempt_id"), "composite_manual_decisions", ("decision_id", "attempt_id")), ("financial_obligations", ("checkout_id",), "composite_checkouts", ("checkout_id",)), ("financial_obligations", ("receipt_id", "checkout_id"), "composite_payment_receipts", ("receipt_id", "checkout_id")), ("financial_obligations", ("ledger_seq", "obligation_id"), "wallet_effects", ("ledger_seq", "obligation_id")), ("wallet_effects", ("obligation_id", "beneficiary_telegram_id", "kind", "amount"), "financial_obligations", ("obligation_id", "beneficiary_telegram_id", "kind", "amount")), ("composite_campaigns", ("plan_id", "plan_kind"), "composite_plans", ("plan_id", "kind")), ("composite_test_claims", ("offer_id",), "composite_offers", ("offer_id",)), ("composite_test_claims", ("campaign_id",), "composite_campaigns", ("campaign_id",)), ("resource_reservations", ("checkout_id",), "composite_checkouts", ("checkout_id",)), ("resource_reservations", ("claim_id",), "composite_test_claims", ("claim_id",)), ("resource_reservations", ("claim_id", "campaign_id"), "composite_test_claims", ("claim_id", "campaign_id")), ("resource_reservations", ("legacy_order_id",), "orders", ("id",)), ("composite_campaign_recipients", ("campaign_id",), "composite_campaigns", ("campaign_id",)), ("composite_campaign_recipients", ("claim_id", "campaign_id", "customer_telegram_id", "claim_status"), "composite_test_claims", ("claim_id", "campaign_id", "customer_telegram_id", "status")),
)

WALLET_AUTH = {"status": "authorized", "final_price": 225_000, "wallet_amount": 225_000, "authorization_source": "wallet", "authorized_at": T0 + 1_000, "deadline_at": T0 + 901_000}
ZERO_AUTH = {"status": "authorized", "final_price": 0, "wallet_amount": 0, "authorization_source": "zero_price", "authorized_at": T0 + 1_000, "deadline_at": T0 + 901_000}
CHECKOUT_STATES = {"quoted": {"status": "quoted"}, "awaiting_payment": {}, "manual_review": {"status": "manual_review"}, "authorized": WALLET_AUTH, "fulfilling": {**WALLET_AUTH, "status": "fulfilling", "fulfillment_operation_id": "op-f1"}, "fulfilled": {**WALLET_AUTH, "status": "fulfilled", "fulfillment_operation_id": "op-f1"}, "rejected": {"status": "rejected", "terminal_reason": "owner_rejected", "terminal_at": T0 + 5_000}, "cancelled": {"status": "cancelled", "terminal_reason": "customer_cancelled", "terminal_at": T0 + 5_000}, "failed": {**WALLET_AUTH, "status": "failed", "terminal_reason": "deadline_missed", "terminal_at": T0 + 901_000}}
RENEWAL_1 = {"checkout_id": "ck-r1", "order_id": 102, "offer_id": "of-2", "kind": "renewal", "target_subscription_id": "sub-1", "request_key": "confirm-r1"}
PROVIDER_VERIFIED = {"verification_source": "provider", "manual_decision_id": None}
RECEIPT_CREDIT = {"receipt_id": "rc-1", "due_at": T0 + 60_000}
PENDING_CLAIM = {"status": "pending", "fulfilled_at": None, "retrieval_evidence": None}
NO_COUPON = {"checkout_id": None, "coupon_code_id": None}
TRANSITION = {"transition_key": "op-t1", "transitioned_at": T0 + 1_000}
SETTLE = "UPDATE financial_obligations SET state = 'settled', ledger_seq = ?, settled_at = ? WHERE obligation_id = ?"
MOVE = "UPDATE resource_reservations SET state = ?, transition_key = ?, transitioned_at = ? WHERE reservation_id = ?"

def _put89(conn, table, **changes):
    row = {**ROWS_8_9[table], **changes}
    cols = tuple(row)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", tuple(row.values()))

def _order(conn, order_id):
    conn.execute("INSERT INTO orders (id, user_id, product_id, status, service_kind, composite_ref) VALUES (?, 1, 1, 'pending', 'composite', ?)", (order_id, f"order-ref-{order_id}"))

def _offer(conn, offer_id):
    _insert(conn, "composite_offers", offer_id=offer_id)

def _test_offer(conn, offer_id):
    _insert(conn, "composite_offers", offer_id=offer_id, plan_version_id="cpv-camp-1", allowance_bytes=16_106_127_360, duration_seconds=1_296_000, base_price=0, payable_price=0)

def _chain89(conn, until=None):
    assert until is None or until in ROWS_8_9
    _chain(conn)
    _order(conn, 101)
    _insert(conn, "composite_plans", plan_id="cp-camp", kind="campaign")
    _insert(conn, "composite_plan_versions", plan_version_id="cpv-camp-1", plan_id="cp-camp", kind="campaign", allowance_bytes=16_106_127_360, duration_seconds=1_296_000, base_price=0)
    _test_offer(conn, "of-t1")
    for table, changes in CHAIN_8_9:
        if table == until: break
        _put89(conn, table, **changes)

def _checkout2(conn):
    _order(conn, 102)
    _offer(conn, "of-2")
    _put89(conn, "composite_checkouts", checkout_id="ck-2", order_id=102, offer_id="of-2", request_key="confirm-2")

def _campaign2(conn):
    _insert(conn, "composite_plans", plan_id="cp-camp2", kind="campaign")
    _put89(conn, "composite_campaigns", campaign_id="cmp-2", plan_id="cp-camp2")

def _trigger_refuses(conn, sql, args=()):
    with pytest.raises(sqlite3.IntegrityError) as error:
        conn.execute(sql, args)
    assert "constraint failed" not in str(error.value)

def test_main_gets_the_section_8_to_9_tables(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        tables = _tables(conn)
        for table, row in ROWS_8_9.items():
            assert table in tables
            assert set(row) <= set(_columns(conn, table))

def test_section_8_to_9_foreign_keys_are_restrict(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        found = set()
        for table in ROWS_8_9:
            groups = {}
            for row in conn.execute(f"PRAGMA foreign_key_list({table})"):
                groups.setdefault(row[0], []).append(row)
            for rows in groups.values():
                rows.sort(key=lambda row: row[1])
                parent = rows[0][2]
                cols = tuple(row[4] for row in rows)
                if any(col is None for col in cols):
                    cols = tuple(r[1] for r in sorted((r for r in conn.execute(f"PRAGMA table_info({parent})") if r[5] > 0), key=lambda r: r[5]))
                found.add((table, tuple(row[3] for row in rows), parent, cols))
                assert all(row[6] == "RESTRICT" for row in rows)
        assert set(EXPECTED_FKS_8_9) <= found

def test_rows_in_every_section_8_to_9_table_survive_a_rerun(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _chain89(conn)
        conn.commit()
    before = _dump(install.main)
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(migrations.SCHEMA_VERSION, migrations.SCHEMA_VERSION, "unchanged")
    assert _dump(install.main) == before
    _check_clean(install.main)
    with closing(sqlite3.connect(install.main)) as conn:
        assert _one(conn, "SELECT count(*) FROM resource_reservations")[0] == 3
        assert all(_one(conn, f"SELECT count(*) FROM {table}")[0] == 1 for table in ROWS_8_9 if table != "resource_reservations")

@pytest.mark.parametrize("case", ["checkout-order", "legacy-order-reservation", "campaign-plan"], ids=["checkout-order", "legacy-order-reservation", "campaign-plan"])
def test_section_8_to_9_parents_cannot_be_deleted(main_db, case):
    _chain89(main_db)
    if case == "legacy-order-reservation":
        _put89(main_db, "resource_reservations", reservation_id="rr-l", checkout_id=None, legacy_order_id=2, sequence=9)
        sql = "DELETE FROM orders WHERE id=2"
    elif case == "campaign-plan":
        _campaign2(main_db)
        sql = "DELETE FROM composite_plans WHERE plan_id='cp-camp2'"
    else:
        sql = "DELETE FROM orders WHERE id=101"
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        main_db.execute(sql)
    if case == "campaign-plan":
        assert _one(main_db, "SELECT plan_id FROM composite_plans WHERE plan_id='cp-camp2'") == ("cp-camp2",)
    elif case == "legacy-order-reservation":
        assert _one(main_db, "SELECT id FROM orders WHERE id=2") == (2,)
    else:
        assert _one(main_db, "SELECT id FROM orders WHERE id=101") == (101,)

@pytest.mark.parametrize("fk", EXPECTED_FKS_8_9, ids=[f"{x[0]}-{i}" for i, x in enumerate(EXPECTED_FKS_8_9, 1)])
def test_section_8_to_9_child_row_needs_its_parent(main_db, fk):
    table = fk[0]
    _chain89(main_db, until=table)
    cases = (
        {"order_id": 999}, {"offer_id": "of-missing"}, {"kind": "renewal", "target_subscription_id": "sub-missing"},
        {"status": "authorized", "authorization_source": "receipt", "authorized_at": T0 + 60_000, "deadline_at": T0 + 960_000, "original_receipt_id": "rc-missing"},
        {"checkout_id": "ck-missing"}, {"attempt_id": "pa-missing"}, {"attempt_id": "pa-missing"}, {"manual_decision_id": "md-missing"},
        {"checkout_id": "ck-missing"}, {"kind": "extra_credit", "effect_key": "extra_credit:rc-missing", "receipt_id": "rc-missing", "due_at": T0 + 60_000},
        {"state": "settled", "ledger_seq": 999, "settled_at": T0}, {"obligation_id": "fo-missing"}, {"plan_id": "cp-missing"},
        {"offer_id": "of-missing"}, {"campaign_id": "cmp-missing"}, {"checkout_id": "ck-missing"},
        {"resource": "ordinary_test", "checkout_id": None, "coupon_code_id": None, "claim_id": "tc-missing"},
        {"resource": "campaign_place", "checkout_id": None, "coupon_code_id": None, "claim_id": "tc-missing", "campaign_id": "cmp-1"},
        {"checkout_id": None, "legacy_order_id": 999}, {"campaign_id": "cmp-missing"}, {"claim_id": "tc-missing"},
    )
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        _put89(main_db, table, **cases[EXPECTED_FKS_8_9.index(fk)])

def _case_error(conn, table, changes, expected):
    if expected == "accepted":
        _put89(conn, table, **changes)
        return
    with pytest.raises(sqlite3.IntegrityError, match=expected):
        _put89(conn, table, **changes)


def _case_id(value):
    if isinstance(value, dict):
        return ",".join(f"{key}={item}" for key, item in value.items())[:72]
    return str(value)


CHECK = "CHECK constraint failed"
FK = "FOREIGN KEY constraint failed"


@pytest.mark.parametrize("changes, expected", [
    ({"kind": "renewal", "target_subscription_id": "sub-1"}, "accepted"),
    ({"kind": "conversion", "target_subscription_id": "sub-1"}, "accepted"),
    ({"status": "quoted"}, "accepted"), ({"status": "manual_review"}, "accepted"),
    ({"wallet_amount": 0}, "accepted"), ({"wallet_amount": 225_000}, "accepted"),
    ({"kind": "gift", "target_subscription_id": "sub-1"}, CHECK), ({"status": "expired"}, CHECK), ({"status": "pending"}, CHECK),
    ({"final_price": -1}, CHECK), ({"final_price": 1.5}, CHECK), ({"final_price": "n/a"}, CHECK),
    ({"wallet_amount": -1}, CHECK), ({"wallet_amount": 225_001}, CHECK), ({"wallet_amount": 0.5}, CHECK),
    ({"kind": "initial", "target_subscription_id": "sub-1"}, CHECK), ({"kind": "renewal"}, CHECK), ({"kind": "conversion"}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_checkouts.{col}")) for col in ("order_id", "tenant_installation_id", "customer_telegram_id", "offer_id", "kind", "principal", "request_key", "status", "final_price", "created_at")],
], ids=["renewal", "conversion", "quoted", "review", "wallet-zero", "wallet-full", "bad-kind", "bad-expired", "bad-pending", "negative-price", "float-price", "text-price", "negative-wallet", "over-wallet", "float-wallet", "initial-target", "renewal-no-target", "conversion-no-target"] + [f"null-{c}" for c in ("order_id", "tenant_installation_id", "customer_telegram_id", "offer_id", "kind", "principal", "request_key", "status", "final_price", "created_at")])
def test_checkout_column_values(main_db, changes, expected):
    _chain89(main_db, until="composite_checkouts")
    _case_error(main_db, "composite_checkouts", changes, expected)


@pytest.mark.parametrize("changes, expected", [(WALLET_AUTH, "accepted"), (ZERO_AUTH, "accepted"), *[(CHECKOUT_STATES[s], "accepted") for s in ("fulfilling", "fulfilled", "failed", "rejected", "cancelled")], ({**WALLET_AUTH, "status": "cancelled", "terminal_reason": "subscription_cancelled", "terminal_at": T0 + 5_000}, "accepted"),
    ({**WALLET_AUTH, "wallet_amount": 224_999}, CHECK), ({**WALLET_AUTH, "final_price": 0, "wallet_amount": 0}, CHECK), ({**ZERO_AUTH, "final_price": 225_000}, CHECK), ({**ZERO_AUTH, "final_price": 225_000, "wallet_amount": 225_000}, CHECK), ({**WALLET_AUTH, "authorized_at": None, "deadline_at": None}, CHECK), ({**WALLET_AUTH, "authorization_source": None}, CHECK),
    *[({**WALLET_AUTH, "deadline_at": v}, CHECK) for v in (T0 + 901_001, T0 + 900_999, None)], ({"deadline_at": T0 + 901_000}, CHECK), ({"status": "authorized"}, CHECK), *[({**WALLET_AUTH, "status": s}, CHECK) for s in ("awaiting_payment", "quoted", "manual_review")], ({**CHECKOUT_STATES["rejected"], **WALLET_AUTH, "status": "rejected"}, CHECK), ({"status": "failed", "terminal_reason": "deadline_missed", "terminal_at": T0 + 5_000}, CHECK), ({"status": "fulfilled", "fulfillment_operation_id": "op-f1"}, CHECK), ({**WALLET_AUTH, "status": "fulfilling"}, CHECK), ({**WALLET_AUTH, "status": "fulfilled"}, CHECK), ({"status": "cancelled"}, CHECK), ({"status": "cancelled", "terminal_at": T0 + 5_000}, CHECK), ({"status": "cancelled", "terminal_reason": "customer_cancelled"}, CHECK), ({"terminal_reason": "customer_cancelled", "terminal_at": T0 + 5_000}, CHECK), ({**WALLET_AUTH, "authorization_source": "receipt"}, CHECK), ({**WALLET_AUTH, "authorization_source": "card"}, CHECK), ({"status": "authorized", "authorization_source": "receipt", "authorized_at": T0 + 60_000, "deadline_at": T0 + 960_000}, CHECK), ({**WALLET_AUTH, "original_receipt_id": "rc-missing"}, CHECK), ({**WALLET_AUTH, "authorization_source": "receipt", "original_receipt_id": "rc-missing"}, CHECK)], ids=lambda value: _case_id(value))
def test_checkout_authorization_and_deadline(main_db, changes, expected):
    _chain89(main_db, until="composite_checkouts")
    _case_error(main_db, "composite_checkouts", changes, expected)


def test_checkout_order_offer_and_request_are_unique(main_db):
    _chain89(main_db, until="composite_payment_attempts")
    _order(main_db, 102)
    _offer(main_db, "of-2")
    cases = [({"offer_id": "of-2", "request_key": "confirm-2"}, "UNIQUE constraint failed: composite_checkouts.order_id"), ({"order_id": 102, "request_key": "confirm-2"}, "UNIQUE constraint failed: composite_checkouts.offer_id"), ({"order_id": 102, "offer_id": "of-2"}, "UNIQUE constraint failed: composite_checkouts.principal, composite_checkouts.request_key"), ({"order_id": 102, "offer_id": "of-2", "principal": "telegram:50002", "customer_telegram_id": 50002}, "accepted")]
    for changes, expected in cases:
        if expected == "accepted":
            _put89(main_db, "composite_checkouts", checkout_id="ck-2", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected)):
                _put89(main_db, "composite_checkouts", checkout_id="ck-2", **changes)


def test_checkout_is_authorized_by_its_own_original_receipt(main_db):
    _chain89(main_db, until="financial_obligations")
    _checkout2(main_db)
    auth = "UPDATE composite_checkouts SET status = 'authorized', authorization_source = 'receipt', authorized_at = ?, deadline_at = ?, original_receipt_id = ? WHERE checkout_id = ?"
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        main_db.execute(auth, (T0 + 60_000, T0 + 960_000, "rc-1", "ck-2"))
    main_db.execute(auth, (T0 + 60_000, T0 + 960_000, "rc-1", "ck-1"))
    _put89(main_db, "composite_payment_receipts", receipt_id="rc-2", transaction_reference="bank-ref-2", outcome="extra_credit", **PROVIDER_VERIFIED)
    for sql, args in [("UPDATE composite_checkouts SET original_receipt_id = 'rc-2' WHERE checkout_id = 'ck-1'", ()), ("UPDATE composite_checkouts SET authorized_at = ?, deadline_at = ? WHERE checkout_id = 'ck-1'", (T0 + 70_000, T0 + 970_000)), ("UPDATE composite_checkouts SET authorization_source = 'wallet' WHERE checkout_id = 'ck-1'", ()), ("UPDATE composite_checkouts SET status = 'awaiting_payment', authorization_source = NULL, authorized_at = NULL, deadline_at = NULL, original_receipt_id = NULL WHERE checkout_id = 'ck-1'", ())]:
        _trigger_refuses(main_db, sql, args)
    assert _one(main_db, "SELECT status, authorization_source, authorized_at, deadline_at, original_receipt_id FROM composite_checkouts WHERE checkout_id='ck-1'") == ("authorized", "receipt", T0 + 60_000, T0 + 960_000, "rc-1")
    main_db.execute("UPDATE composite_checkouts SET status = 'fulfilling', fulfillment_operation_id = 'op-f1' WHERE checkout_id = 'ck-1'")


@pytest.mark.parametrize("state", (*CHECKOUT_STATES, "other-subscription"), ids=(*CHECKOUT_STATES, "other-subscription"))
def test_one_open_renewal_or_conversion_per_subscription(main_db, state):
    _chain89(main_db, until="composite_payment_attempts")
    for order_id in (102, 103, 104):
        _order(main_db, order_id)
    for offer_id in ("of-2", "of-3", "of-4"):
        _offer(main_db, offer_id)
    if state == "other-subscription":
        _sub2(main_db)
        _put89(main_db, "composite_checkouts", **RENEWAL_1)
        _put89(main_db, "composite_checkouts", checkout_id="ck-r2", order_id=103, offer_id="of-3", kind="renewal", target_subscription_id="sub-2", request_key="confirm-r2")
        _put89(main_db, "composite_checkouts", checkout_id="ck-i2", order_id=104, offer_id="of-4", request_key="confirm-i2")
        return
    _put89(main_db, "composite_checkouts", **{**RENEWAL_1, **CHECKOUT_STATES[state]})
    open_state = state in ("quoted", "awaiting_payment", "manual_review", "authorized", "fulfilling")
    changes = {"checkout_id": "ck-r2", "order_id": 103, "offer_id": "of-3", "kind": "renewal", "target_subscription_id": "sub-1", "request_key": "confirm-r2"}
    if open_state:
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_checkouts.target_subscription_id")):
            _put89(main_db, "composite_checkouts", **changes)
    else:
        _put89(main_db, "composite_checkouts", **changes)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_checkouts.target_subscription_id")):
        _put89(main_db, "composite_checkouts", checkout_id="ck-c", order_id=104, offer_id="of-4", kind="conversion", target_subscription_id="sub-1", request_key="confirm-c")


@pytest.mark.parametrize("column, value", [("kind", "conversion"), ("target_subscription_id", "sub-2"), ("offer_id", "of-3"), ("order_id", 103), ("tenant_installation_id", "inst-other"), ("customer_telegram_id", 50002), ("final_price", 200_000), ("wallet_amount", 20_000), ("principal", "web:owner-1"), ("request_key", "confirm-x"), ("created_at", T0 + 1)], ids=["kind", "target", "offer", "order", "tenant", "customer", "price", "wallet", "principal", "request", "created"])
def test_checkout_terms_never_change(main_db, column, value):
    _chain89(main_db, until="composite_payment_attempts")
    _order(main_db, 102)
    _order(main_db, 103)
    _offer(main_db, "of-2")
    _offer(main_db, "of-3")
    _sub2(main_db)
    _put89(main_db, "composite_checkouts", **RENEWAL_1)
    _trigger_refuses(main_db, f"UPDATE composite_checkouts SET {column} = ? WHERE checkout_id = 'ck-r1'", (value,))


@pytest.mark.parametrize("scenario", ["fulfilled", "failed", "rejected", "cancelled", "delete", "manual-review-cancel"], ids=["fulfilled", "failed", "rejected", "cancelled", "delete", "manual-review-cancel"])
def test_finished_checkouts_never_reopen(main_db, scenario):
    if scenario in ("fulfilled", "failed", "rejected", "cancelled"):
        _chain89(main_db, until="composite_checkouts")
        sql = {"fulfilled": "UPDATE composite_checkouts SET status = 'fulfilling' WHERE checkout_id = 'ck-1'", "failed": "UPDATE composite_checkouts SET status = 'authorized', terminal_reason = NULL, terminal_at = NULL WHERE checkout_id = 'ck-1'", "rejected": "UPDATE composite_checkouts SET status = 'quoted', terminal_reason = NULL, terminal_at = NULL WHERE checkout_id = 'ck-1'", "cancelled": "UPDATE composite_checkouts SET status = 'awaiting_payment', terminal_reason = NULL, terminal_at = NULL WHERE checkout_id = 'ck-1'"}[scenario]
        _put89(main_db, "composite_checkouts", **CHECKOUT_STATES[scenario])
        _trigger_refuses(main_db, sql)
    elif scenario == "delete":
        _chain89(main_db, until="composite_payment_attempts")
        _trigger_refuses(main_db, "DELETE FROM composite_checkouts WHERE checkout_id = 'ck-1'")
    else:
        _chain89(main_db, until="composite_payment_attempts")
        main_db.execute("UPDATE composite_checkouts SET status = 'manual_review' WHERE checkout_id = 'ck-1'")
        main_db.execute("UPDATE composite_checkouts SET status = 'cancelled', terminal_reason = 'customer_cancelled', terminal_at = ? WHERE checkout_id = 'ck-1'", (T0 + 5_000,))


@pytest.mark.parametrize("changes, expected", [
    ({"create_state": "pending", "provider_invoice_ref": None}, "accepted"), ({"create_state": "uncertain", "provider_invoice_ref": None}, "accepted"), ({"create_state": "failed", "provider_invoice_ref": None}, "accepted"),
    ({"status": "verified"}, "accepted"), ({"status": "expired"}, "accepted"), ({"status": "closed"}, "accepted"), ({"valid_until": T0 + 1_001}, "accepted"), ({"invoice_value": 195_000}, "accepted"), ({"minor_unit_scale": 2}, "accepted"),
    ({"create_state": "created", "provider_invoice_ref": None}, CHECK), ({"create_state": "pending"}, CHECK), ({"create_state": "uncertain"}, CHECK), ({"create_state": "unknown", "provider_invoice_ref": None}, CHECK), ({"status": "paid"}, CHECK), ({"native_amount": 0}, CHECK), ({"native_amount": -1}, CHECK), ({"native_amount": 1.5}, CHECK), ({"native_amount": "n/a"}, CHECK), ({"store_remainder": 0}, CHECK), ({"invoice_value": 194_999}, CHECK), ({"invoice_value": 197_000.5}, CHECK), ({"minor_unit_scale": -1}, CHECK), ({"valid_until": T0 + 1_000}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_payment_attempts.{col}")) for col in ("checkout_id", "method", "provider", "merchant_namespace", "config_version", "creation_intent", "currency", "quote_rules", "quote_version", "quote_accepted_at", "invoice_value")],
], ids=lambda value: _case_id(value))
def test_attempt_column_values(main_db, changes, expected):
    _chain89(main_db, until="composite_payment_attempts")
    _case_error(main_db, "composite_payment_attempts", changes, expected)


def test_attempt_intent_and_invoice_are_unique(main_db):
    _chain89(main_db, until="composite_manual_decisions")
    cases = [({"attempt_id": "pa-2", "provider_invoice_ref": "inv-2"}, "UNIQUE constraint failed: composite_payment_attempts.creation_intent"), ({"attempt_id": "pa-3", "creation_intent": "intent-pa-3"}, "UNIQUE constraint failed: composite_payment_attempts.provider, composite_payment_attempts.merchant_namespace, composite_payment_attempts.provider_invoice_ref"), ({"attempt_id": "pa-4", "creation_intent": "intent-pa-4", "merchant_namespace": "card-ns-2"}, None), ({"attempt_id": "pa-5", "creation_intent": "intent-pa-5", "provider_invoice_ref": None, "create_state": "uncertain"}, None), ({"attempt_id": "pa-6", "creation_intent": "intent-pa-6", "provider_invoice_ref": None, "create_state": "uncertain"}, None)]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "composite_payment_attempts", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected)):
                _put89(main_db, "composite_payment_attempts", **changes)


@pytest.mark.parametrize("column, value", [("native_amount", 1_960_000), ("currency", "USD"), ("minor_unit_scale", 2), ("store_remainder", 190_000), ("invoice_value", 198_000), ("quote_rules", '{"rate": "11/1"}'), ("quote_version", "quote-v2"), ("quote_accepted_at", T0 + 2_000), ("valid_until", T0 + 3_600_000), ("checkout_id", "ck-2"), ("creation_intent", "intent-x"), ("provider_invoice_ref", "inv-x"), ("method", "crypto"), ("provider", "other"), ("merchant_namespace", "card-ns-2"), ("config_version", "cfg-2")], ids=["native", "currency", "scale", "remainder", "invoice", "rules", "version", "accepted", "validity", "checkout", "intent", "provider-ref", "method", "provider", "namespace", "config"])
def test_attempt_quote_never_changes(main_db, column, value):
    _chain89(main_db, until="composite_manual_decisions")
    _checkout2(main_db)
    _trigger_refuses(main_db, f"UPDATE composite_payment_attempts SET {column} = ? WHERE attempt_id = 'pa-1'", (value,))


@pytest.mark.parametrize("scenario", ["verify-reconcile-delete"], ids=["verify-reconcile-delete"])
def test_attempt_verification_reconciliation_and_delete(main_db, scenario):
    _chain89(main_db, until="composite_manual_decisions")
    main_db.execute("UPDATE composite_payment_attempts SET status = 'verified' WHERE attempt_id = 'pa-1'")
    _put89(main_db, "composite_payment_attempts", attempt_id="pa-2", creation_intent="intent-pa-2", provider_invoice_ref=None, create_state="uncertain")
    main_db.execute("UPDATE composite_payment_attempts SET create_state = 'created', provider_invoice_ref = 'inv-2' WHERE attempt_id = 'pa-2'")
    _trigger_refuses(main_db, "DELETE FROM composite_payment_attempts WHERE attempt_id = 'pa-2'")


@pytest.mark.parametrize("changes, expected", [
    ({"interface": "telegram", "principal": "telegram:1001"}, "accepted"), ({"decision": "rejected", "reason": "amount does not match", "provider_reference": None, "amount": None}, "accepted"), ({"decision": "mismatch_hold", "reason": "amount differs from the quote", "amount": 1_000_000}, "accepted"), ({"reason": "checked against bank statement"}, "accepted"),
    ({"principal_role": "staff"}, CHECK), ({"principal_role": "admin"}, CHECK), ({"interface": "mini_app"}, CHECK), ({"decision": "pending", "reason": "waiting for the bank"}, CHECK), ({"provider_reference": None}, CHECK), ({"amount": None}, CHECK), ({"decision": "rejected"}, CHECK), ({"decision": "mismatch_hold"}, CHECK), ({"amount": 0}, CHECK), ({"amount": 1.5}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_manual_decisions.{col}")) for col in ("attempt_id", "principal", "principal_role", "evidence_digest", "tenant_installation_id", "customer_telegram_id", "currency", "method", "decided_at", "idempotency_key")],
], ids=lambda value: _case_id(value))
def test_manual_decision_values(main_db, changes, expected):
    _chain89(main_db, until="composite_manual_decisions")
    _case_error(main_db, "composite_manual_decisions", changes, expected)


def test_manual_decisions_are_final(main_db):
    _chain89(main_db, until="composite_payment_receipts")
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_manual_decisions.idempotency_key")):
        _put89(main_db, "composite_manual_decisions", decision_id="md-2", interface="telegram")
    _trigger_refuses(main_db, "UPDATE composite_manual_decisions SET decision = 'rejected', reason = 'changed mind' WHERE decision_id = 'md-1'")
    _trigger_refuses(main_db, "UPDATE composite_manual_decisions SET decided_at = ? WHERE decision_id = 'md-1'", (T0 + 61_000,))
    _trigger_refuses(main_db, "DELETE FROM composite_manual_decisions WHERE decision_id = 'md-1'")


@pytest.mark.parametrize("changes, expected", [
    ({"outcome": "extra_credit"}, "accepted"), ({"outcome": "terminal_late_credit"}, "accepted"), ({"outcome": "mismatch_hold", "invoice_value": None}, "accepted"), ({**PROVIDER_VERIFIED}, "accepted"),
    ({"outcome": "refund"}, CHECK), ({"verification_source": "client", "manual_decision_id": None}, CHECK), ({"verification_source": "provider"}, CHECK), ({"manual_decision_id": None}, CHECK), ({"native_amount": 0}, CHECK), ({"native_amount": 1.5}, CHECK), ({"invoice_value": None}, CHECK), ({"outcome": "extra_credit", "invoice_value": None}, CHECK), ({"invoice_value": 0}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_payment_receipts.{col}")) for col in ("transaction_reference", "provider", "merchant_namespace", "tenant_installation_id", "beneficiary_telegram_id", "currency", "evidence_digest", "verified_at", "outcome")],
], ids=lambda value: _case_id(value))
def test_receipt_values(main_db, changes, expected):
    _chain89(main_db, until="composite_payment_receipts")
    _case_error(main_db, "composite_payment_receipts", changes, expected)


def test_transaction_reference_settles_one_context(main_db):
    _chain89(main_db, until="financial_obligations")
    _checkout2(main_db)
    _put89(main_db, "composite_payment_attempts", attempt_id="pa-2", checkout_id="ck-2", creation_intent="intent-pa-2", provider_invoice_ref="inv-2")
    cases = [
        ({"receipt_id": "rc-2", "attempt_id": "pa-2", "checkout_id": "ck-2", **PROVIDER_VERIFIED}, "UNIQUE constraint failed: composite_payment_receipts.provider, composite_payment_receipts.merchant_namespace, composite_payment_receipts.transaction_reference"),
        ({"receipt_id": "rc-3", "checkout_id": "ck-2", "transaction_reference": "bank-ref-3", **PROVIDER_VERIFIED}, FK),
        ({"receipt_id": "rc-4", "attempt_id": "pa-2", "checkout_id": "ck-2", "transaction_reference": "bank-ref-4"}, FK),
        ({"receipt_id": "rc-5", "attempt_id": "pa-2", "checkout_id": "ck-2", "merchant_namespace": "card-ns-2", **PROVIDER_VERIFIED}, None),
        ({"receipt_id": "rc-6", "transaction_reference": "bank-ref-6", **PROVIDER_VERIFIED}, "UNIQUE constraint failed: composite_payment_receipts.checkout_id"),
        ({"receipt_id": "rc-7", "transaction_reference": "bank-ref-7", "outcome": "extra_credit", **PROVIDER_VERIFIED}, None),
        ({"receipt_id": "rc-8", "transaction_reference": "bank-ref-8", "outcome": "extra_credit", **PROVIDER_VERIFIED}, None),
    ]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "composite_payment_receipts", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected) if expected.startswith("UNIQUE") else expected):
                _put89(main_db, "composite_payment_receipts", **changes)


@pytest.mark.parametrize("column, value", [("provider", "other"), ("merchant_namespace", "card-ns-2"), ("transaction_reference", "bank-ref-9"), ("tenant_installation_id", "inst-other"), ("beneficiary_telegram_id", 50002), ("native_amount", 1_000_000), ("currency", "USD"), ("invoice_value", 100_000), ("evidence_digest", "evidence-x"), ("verified_at", T0 + 70_000), ("outcome", "extra_credit"), ("outcome", "mismatch_hold")], ids=["provider", "namespace", "reference", "tenant", "beneficiary", "amount", "currency", "value", "digest", "verified", "extra", "mismatch"])
def test_receipts_are_kept_and_their_evidence_never_changes(main_db, column, value):
    _chain89(main_db, until="financial_obligations")
    _trigger_refuses(main_db, f"UPDATE composite_payment_receipts SET {column} = ? WHERE receipt_id = 'rc-1'", (value,))


@pytest.mark.parametrize("scenario", ["delete-original", "extra-to-late"], ids=["delete-original", "extra-to-late"])
def test_receipt_deletion_and_credit_outcome_are_final(main_db, scenario):
    _chain89(main_db, until="financial_obligations")
    if scenario == "delete-original":
        _trigger_refuses(main_db, "DELETE FROM composite_payment_receipts WHERE receipt_id = 'rc-1'")
    else:
        _put89(main_db, "composite_payment_receipts", receipt_id="rc-2", transaction_reference="bank-ref-2", outcome="extra_credit", **PROVIDER_VERIFIED)
        _trigger_refuses(main_db, "UPDATE composite_payment_receipts SET outcome = 'terminal_late_credit' WHERE receipt_id = 'rc-2'")


@pytest.mark.parametrize("changes, expected", [
    ({"kind": "wallet_release", "due_at": T0 + 60_000}, "accepted"), ({"kind": "full_refund", "amount": 227_000, "due_at": T0 + 60_000}, "accepted"), ({"kind": "late_credit", **RECEIPT_CREDIT}, "accepted"), ({"kind": "extra_credit", **RECEIPT_CREDIT}, "accepted"), ({"kind": "support_compensation", "checkout_id": None, "due_at": T0 + 86_400_000}, "accepted"), ({"kind": "topup_credit", "checkout_id": None}, "accepted"), ({"kind": "support_compensation"}, "accepted"), ({"state": "evidence_hold"}, "accepted"), ({"due_at": T0 + 1}, "accepted"),
    ({"kind": "debit"}, CHECK), ({"amount": 0}, CHECK), ({"amount": -1}, CHECK), ({"amount": 1.5}, CHECK), ({"state": "queued"}, CHECK), ({"state": "settled"}, CHECK), ({"settled_at": T0}, CHECK), ({"checkout_id": None}, CHECK), ({"kind": "wallet_release", "checkout_id": None, "due_at": T0 + 60_000}, CHECK), ({"kind": "full_refund", "checkout_id": None, "due_at": T0 + 60_000}, CHECK), ({"kind": "extra_credit", "due_at": T0 + 60_000}, CHECK), ({"kind": "late_credit", "due_at": T0 + 60_000}, CHECK), ({"kind": "support_compensation", "receipt_id": "rc-1"}, CHECK), ({"kind": "full_refund", **RECEIPT_CREDIT}, CHECK), ({"kind": "extra_credit", **RECEIPT_CREDIT, "checkout_id": None}, CHECK), ({"kind": "full_refund", "due_at": T0 + 60_001}, CHECK), ({"kind": "wallet_release", "due_at": T0 + 59_999}, CHECK), ({"kind": "extra_credit", **RECEIPT_CREDIT, "due_at": T0 + 120_000}, CHECK), ({"due_at": T0 - 1}, CHECK), ({"kind": "topup_credit", "checkout_id": None, "due_at": T0 - 1}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: financial_obligations.{col}")) for col in ("effect_key", "tenant_installation_id", "beneficiary_telegram_id", "kind", "amount", "triggered_at", "due_at", "state")],
], ids=lambda value: _case_id(value))
def test_obligation_column_values(main_db, changes, expected):
    _chain89(main_db, until="financial_obligations")
    _case_error(main_db, "financial_obligations", changes, expected)


def test_each_financial_effect_happens_once(main_db):
    _chain89(main_db, until="wallet_effects")
    cases = [
        ({"obligation_id": "fo-2", "kind": "support_compensation", "amount": 5_000, "checkout_id": None}, "UNIQUE constraint failed: financial_obligations.effect_key"),
        ({"obligation_id": "fo-3", "effect_key": "wallet_debit:ck-1:again"}, "UNIQUE constraint failed: financial_obligations.checkout_id, financial_obligations.kind"),
        ({"obligation_id": "fo-4", "effect_key": "full_refund:ck-1", "kind": "full_refund", "amount": 227_000, "due_at": T0 + 60_000}, None),
        ({"obligation_id": "fo-5", "effect_key": "full_refund:ck-1:again", "kind": "full_refund", "amount": 227_000, "due_at": T0 + 60_000}, "UNIQUE constraint failed: financial_obligations.checkout_id, financial_obligations.kind"),
        ({"obligation_id": "fo-6", "effect_key": "wallet_release:ck-1", "kind": "wallet_release", "due_at": T0 + 60_000}, None),
        ({"obligation_id": "fo-7", "effect_key": "wallet_release:ck-1:again", "kind": "wallet_release", "due_at": T0 + 60_000}, "UNIQUE constraint failed: financial_obligations.checkout_id, financial_obligations.kind"),
        ({"obligation_id": "fo-8", "effect_key": "extra_credit:rc-1", "kind": "extra_credit", "amount": 197_000, **RECEIPT_CREDIT}, None),
        ({"obligation_id": "fo-9", "effect_key": "late_credit:rc-1", "kind": "late_credit", "amount": 197_000, **RECEIPT_CREDIT}, "UNIQUE constraint failed: financial_obligations.receipt_id"),
        ({"obligation_id": "fo-10", "effect_key": "support:1", "kind": "support_compensation", "amount": 5_000}, None),
        ({"obligation_id": "fo-11", "effect_key": "support:2", "kind": "support_compensation", "amount": 5_000}, None),
    ]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "financial_obligations", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected)):
                _put89(main_db, "financial_obligations", **changes)


@pytest.mark.parametrize("changes, expected", [({"amount": 20_000, "balance_after": 22_000}, FK), ({"beneficiary_telegram_id": 50002}, FK), ({"kind": "wallet_release", "balance_after": 72_000}, FK), ({"balance_before": 20_000, "balance_after": -10_000}, CHECK), ({"balance_before": 20_000, "balance_after": 0}, CHECK), ({"balance_after": 12_001}, CHECK), ({"balance_after": 72_000}, CHECK), ({"balance_before": 30_000, "balance_after": 0}, "accepted")], ids=["amount-mismatch", "beneficiary-mismatch", "kind-mismatch", "negative", "clamped-zero", "wrong-after", "debit-added", "exact-debit"])
def test_wallet_effect_must_settle_exact_amount(main_db, changes, expected):
    _chain89(main_db, until="wallet_effects")
    _case_error(main_db, "wallet_effects", changes, expected)


@pytest.mark.parametrize("scenario", ["unique-and-settle", "same-entry-only"], ids=["unique-and-settle", "same-entry-only"])
def test_settlement_needs_its_own_unclamped_ledger_entry(main_db, scenario):
    _chain89(main_db, until="wallet_effects")
    if scenario == "unique-and-settle":
        with pytest.raises(sqlite3.IntegrityError, match=FK):
            main_db.execute(SETTLE, (1, T0, "fo-1"))
        _put89(main_db, "wallet_effects")
        with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: wallet_effects.obligation_id")):
            _put89(main_db, "wallet_effects", ledger_seq=2, balance_before=30_000, balance_after=0)
        main_db.execute(SETTLE, (1, T0, "fo-1"))
        _put89(main_db, "financial_obligations", obligation_id="fo-2", effect_key="support:1", kind="support_compensation", amount=5_000, checkout_id=None)
        _put89(main_db, "wallet_effects", ledger_seq=2, obligation_id="fo-2", kind="support_compensation", amount=5_000, balance_before=12_000, balance_after=17_000, applied_at=T0 + 1_000)
        _put89(main_db, "financial_obligations", obligation_id="fo-3", effect_key="support:2", kind="support_compensation", amount=5_000, checkout_id=None)
        with pytest.raises(sqlite3.IntegrityError, match=FK):
            main_db.execute(SETTLE, (2, T0 + 1_000, "fo-3"))
        main_db.execute(SETTLE, (2, T0 + 1_000, "fo-2"))
    else:
        _put89(main_db, "wallet_effects")
        main_db.execute(SETTLE, (1, T0, "fo-1"))
        _put89(main_db, "financial_obligations", obligation_id="fo-2", effect_key="support:1", kind="support_compensation", amount=5_000, checkout_id=None)
        _put89(main_db, "wallet_effects", ledger_seq=2, obligation_id="fo-2", kind="support_compensation", amount=5_000, balance_before=12_000, balance_after=17_000, applied_at=T0 + 1_000)
        _put89(main_db, "financial_obligations", obligation_id="fo-3", effect_key="support:2", kind="support_compensation", amount=5_000, checkout_id=None)
        with pytest.raises(sqlite3.IntegrityError, match=FK):
            main_db.execute(SETTLE, (2, T0 + 1_000, "fo-3"))
        main_db.execute(SETTLE, (2, T0 + 1_000, "fo-2"))


@pytest.mark.parametrize("column, value", [("amount", 6_000), ("beneficiary_telegram_id", 50002), ("effect_key", "support:x"), ("kind", "topup_credit"), ("tenant_installation_id", "inst-other"), ("checkout_id", "ck-1"), ("evidence_ref", "ticket-9"), ("triggered_at", T0 - 1_000), ("due_at", T0 + 1_000), ("batch_ref", "batch-1"), ("member_ref", "member-1")], ids=["amount", "beneficiary", "key", "kind", "tenant", "checkout", "evidence", "triggered", "due", "batch", "member"])
def test_obligation_evidence_is_permanent(main_db, column, value):
    _chain89(main_db, until="wallet_effects")
    _put89(main_db, "wallet_effects")
    main_db.execute(SETTLE, (1, T0, "fo-1"))
    _put89(main_db, "financial_obligations", obligation_id="fo-2", effect_key="support:1", kind="support_compensation", amount=5_000, checkout_id=None, state="evidence_hold")
    _trigger_refuses(main_db, f"UPDATE financial_obligations SET {column} = ? WHERE obligation_id = 'fo-2'", (value,))


def test_obligations_and_ledger_entries_are_permanent(main_db):
    _chain89(main_db, until="wallet_effects")
    _put89(main_db, "wallet_effects")
    main_db.execute(SETTLE, (1, T0, "fo-1"))
    _put89(main_db, "financial_obligations", obligation_id="fo-2", effect_key="support:1", kind="support_compensation", amount=5_000, checkout_id=None, state="evidence_hold")
    main_db.execute("UPDATE financial_obligations SET state = 'owed' WHERE obligation_id = 'fo-2'")
    main_db.execute("UPDATE financial_obligations SET state = 'evidence_hold' WHERE obligation_id = 'fo-2'")
    _trigger_refuses(main_db, "UPDATE financial_obligations SET state = 'owed', ledger_seq = NULL, settled_at = NULL WHERE obligation_id = 'fo-1'")
    _trigger_refuses(main_db, "UPDATE financial_obligations SET settled_at = ? WHERE obligation_id = 'fo-1'", (T0 + 1,))
    _trigger_refuses(main_db, "DELETE FROM financial_obligations WHERE obligation_id = 'fo-2'")
    _trigger_refuses(main_db, "UPDATE wallet_effects SET applied_at = ? WHERE ledger_seq = 1", (T0 + 1,))
    _trigger_refuses(main_db, "DELETE FROM wallet_effects WHERE ledger_seq = 1")


@pytest.mark.parametrize("changes, expected", [({"served_count": 149}, "accepted"), ({"served_count": 150, "closed_at": T0 + 1_000}, "accepted"), ({"history_verified_at": None}, "accepted"), ({"lifetime_cap": 151}, CHECK), ({"lifetime_cap": 149}, CHECK), ({"served_count": 151}, CHECK), ({"served_count": -1}, CHECK), ({"served_count": 1.5}, CHECK), ({"served_count": 150}, CHECK), ({"served_count": 149, "closed_at": T0}, CHECK), ({"plan_kind": "test"}, CHECK), ({"plan_id": "cp-paid"}, FK), *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_campaigns.{col}")) for col in ("plan_id", "lifetime_cap", "served_count")]], ids=lambda value: _case_id(value))
def test_campaign_values(main_db, changes, expected):
    _chain89(main_db, until="composite_campaigns")
    _case_error(main_db, "composite_campaigns", changes, expected)


def test_campaign_places_never_return(main_db):
    _chain89(main_db, until="composite_test_claims")
    _insert(main_db, "composite_plans", plan_id="cp-camp2", kind="campaign")
    main_db.execute("UPDATE composite_campaigns SET served_count = 1 WHERE campaign_id = 'cmp-1'")
    _trigger_refuses(main_db, "UPDATE composite_campaigns SET served_count = 0 WHERE campaign_id = 'cmp-1'")
    _trigger_refuses(main_db, "UPDATE composite_campaigns SET plan_id = 'cp-camp2' WHERE campaign_id = 'cmp-1'")
    main_db.execute("UPDATE composite_campaigns SET served_count = 150, closed_at = ? WHERE campaign_id = 'cmp-1'", (T0 + 9_000,))
    _trigger_refuses(main_db, "UPDATE composite_campaigns SET closed_at = ? WHERE campaign_id = 'cmp-1'", (T0 + 10_000,))
    _trigger_refuses(main_db, "UPDATE composite_campaigns SET served_count = 149, closed_at = NULL WHERE campaign_id = 'cmp-1'")
    _trigger_refuses(main_db, "DELETE FROM composite_campaigns WHERE campaign_id = 'cmp-1'")


@pytest.mark.parametrize("changes, expected", [
    (PENDING_CLAIM, "accepted"), ({**PENDING_CLAIM, "campaign_id": None}, "accepted"), ({"campaign_id": None}, "accepted"), ({**PENDING_CLAIM, "status": "failed", "terminal_at": T0 + 120_000, "terminal_reason": "remote_create_rejected"}, "accepted"), ({**PENDING_CLAIM, "status": "uncertain", "terminal_at": T0 + 900_000, "terminal_reason": "deadline_unknown_outcome"}, "accepted"), ({"fulfilled_at": T0 + 899_999}, "accepted"), ({"accepted_at": T0 + 5_000, "deadline_at": T0 + 905_000, "fulfilled_at": T0 + 904_000}, "accepted"),
    ({"deadline_at": T0 + 900_001}, CHECK), ({"deadline_at": T0 + 899_999}, CHECK), ({"fulfilled_at": T0 + 900_001}, CHECK), ({"retrieval_evidence": None}, CHECK), ({"fulfilled_at": None}, CHECK), ({**PENDING_CLAIM, "fulfilled_at": T0 + 300_000, "retrieval_evidence": "retrieved-tc-1"}, CHECK), ({**PENDING_CLAIM, "status": "failed"}, CHECK), ({**PENDING_CLAIM, "terminal_at": T0 + 120_000, "terminal_reason": "remote_create_rejected"}, CHECK), ({**PENDING_CLAIM, "status": "failed", "terminal_at": T0 + 120_000}, CHECK), ({**PENDING_CLAIM, "status": "cancelled"}, CHECK), ({"accepted_seq": 0}, CHECK), ({"accepted_seq": 1.5}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_test_claims.{col}")) for col in ("tenant_installation_id", "customer_telegram_id", "offer_id", "accepted_seq", "accepted_at", "deadline_at", "status")],
], ids=lambda value: _case_id(value))
def test_claim_values(main_db, changes, expected):
    _chain89(main_db, until="composite_test_claims")
    _case_error(main_db, "composite_test_claims", changes, expected)


def test_one_pending_claim_per_customer(main_db):
    _chain89(main_db, until="resource_reservations")
    for offer_id in ("of-t2", "of-t3", "of-t4", "of-t5"):
        _test_offer(main_db, offer_id)
    cases = [({"claim_id": "tc-2", "offer_id": "of-t2", "accepted_seq": 2, **PENDING_CLAIM}, None), ({"claim_id": "tc-3", "offer_id": "of-t3", "accepted_seq": 3, **PENDING_CLAIM}, "UNIQUE constraint failed: composite_test_claims.customer_telegram_id"), ({"claim_id": "tc-4", "offer_id": "of-t3", "accepted_seq": 4, "customer_telegram_id": 50002, **PENDING_CLAIM}, None), ({"claim_id": "tc-5", "offer_id": "of-t4", "accepted_seq": 5, **{**PENDING_CLAIM, "status": "uncertain", "terminal_at": T0 + 900_000, "terminal_reason": "deadline_unknown_outcome"}}, None), ({"claim_id": "tc-6", "offer_id": "of-t2", "accepted_seq": 6, "customer_telegram_id": 50003, **PENDING_CLAIM}, "UNIQUE constraint failed: composite_test_claims.offer_id"), ({"claim_id": "tc-7", "offer_id": "of-t5", "accepted_seq": 2, "customer_telegram_id": 50003, **PENDING_CLAIM}, "UNIQUE constraint failed: composite_test_claims.accepted_seq")]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "composite_test_claims", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected)):
                _put89(main_db, "composite_test_claims", **changes)


@pytest.mark.parametrize("scenario", ["uncertain-failure", "pending-fulfillment"], ids=["uncertain-failure", "pending-fulfillment"])
def test_claim_deadline_and_outcome_are_final(main_db, scenario):
    _chain89(main_db, until="resource_reservations")
    _test_offer(main_db, "of-t2")
    _put89(main_db, "composite_test_claims", claim_id="tc-2", offer_id="of-t2", accepted_seq=2, accepted_at=T0 + 10_000, deadline_at=T0 + 910_000, **PENDING_CLAIM)
    _campaign2(main_db)
    if scenario == "pending-fulfillment":
        main_db.execute("UPDATE composite_test_claims SET status = 'fulfilled', fulfilled_at = ?, retrieval_evidence = 'retrieved-tc-2' WHERE claim_id = 'tc-2'", (T0 + 600_000,))
        return
    for sql, args in [("UPDATE composite_test_claims SET accepted_at = ?, deadline_at = ? WHERE claim_id = 'tc-2'", (T0 + 70_000, T0 + 970_000)), ("UPDATE composite_test_claims SET customer_telegram_id = ? WHERE claim_id = 'tc-2'", (50002,)), ("UPDATE composite_test_claims SET offer_id = ? WHERE claim_id = 'tc-2'", ("of-t1",)), ("UPDATE composite_test_claims SET campaign_id = ? WHERE claim_id = 'tc-2'", ("cmp-2",)), ("UPDATE composite_test_claims SET campaign_id = ? WHERE claim_id = 'tc-2'", (None,)), ("UPDATE composite_test_claims SET accepted_seq = ? WHERE claim_id = 'tc-2'", (9,)), ("UPDATE composite_test_claims SET tenant_installation_id = ? WHERE claim_id = 'tc-2'", ("inst-other",))]:
        _trigger_refuses(main_db, sql, args)
    main_db.execute("UPDATE composite_test_claims SET status = 'uncertain', terminal_at = ?, terminal_reason = 'deadline_unknown_outcome' WHERE claim_id = 'tc-2'", (T0 + 910_000,))
    _trigger_refuses(main_db, "UPDATE composite_test_claims SET status = 'fulfilled', fulfilled_at = ?, retrieval_evidence = 'late', terminal_at = NULL, terminal_reason = NULL WHERE claim_id = 'tc-2'", (T0 + 909_000,))
    _trigger_refuses(main_db, "UPDATE composite_test_claims SET status = 'pending', terminal_at = NULL, terminal_reason = NULL WHERE claim_id = 'tc-2'")
    main_db.execute("UPDATE composite_test_claims SET status = 'failed', terminal_reason = 'remote_confirmed_absent' WHERE claim_id = 'tc-2'")
    _trigger_refuses(main_db, "UPDATE composite_test_claims SET status = 'pending', terminal_at = NULL, terminal_reason = NULL WHERE claim_id = 'tc-2'")
    _trigger_refuses(main_db, "UPDATE composite_test_claims SET status = 'uncertain' WHERE claim_id = 'tc-2'")
    _trigger_refuses(main_db, "UPDATE composite_test_claims SET status = 'failed', fulfilled_at = NULL, retrieval_evidence = NULL, terminal_at = ?, terminal_reason = 'revoked' WHERE claim_id = 'tc-1'", (T0 + 400_000,))
    _trigger_refuses(main_db, "DELETE FROM composite_test_claims WHERE claim_id = 'tc-1'")


@pytest.mark.parametrize("changes, expected", [
    ({"checkout_id": None, "legacy_order_id": 2}, "accepted"), ({**NO_COUPON, "resource": "ordinary_test", "claim_id": "tc-1"}, "accepted"), ({**NO_COUPON, "resource": "ordinary_test", "legacy_test_ref": "legacy-test-50001-1"}, "accepted"), ({**NO_COUPON, "resource": "campaign_place", "claim_id": "tc-1", "campaign_id": "cmp-1"}, "accepted"), ({"state": "consumed", **TRANSITION}, "accepted"), ({"state": "released", **TRANSITION}, "accepted"), ({"state": "release_pending_refund", **TRANSITION}, "accepted"), ({**NO_COUPON, "resource": "ordinary_test", "claim_id": "tc-1", "state": "uncertain_hold", **TRANSITION}, "accepted"), ({**NO_COUPON, "resource": "campaign_place", "claim_id": "tc-1", "campaign_id": "cmp-1", "state": "uncertain_hold", **TRANSITION}, "accepted"),
    ({**NO_COUPON, "resource": "wallet", "claim_id": "tc-1", "campaign_id": "cmp-1"}, CHECK), ({"state": "pending", **TRANSITION}, CHECK), ({"checkout_id": None}, CHECK), ({"legacy_order_id": 2}, CHECK), ({"claim_id": "tc-1"}, CHECK), ({"legacy_test_ref": "legacy-test-50001-1"}, CHECK), ({"coupon_code_id": None}, CHECK), ({"campaign_id": "cmp-1"}, CHECK), ({"checkout_id": None, "claim_id": "tc-1"}, CHECK), ({"resource": "ordinary_test"}, CHECK), ({**NO_COUPON, "resource": "ordinary_test", "claim_id": "tc-1", "coupon_code_id": 7}, CHECK), ({**NO_COUPON, "resource": "ordinary_test", "claim_id": "tc-1", "campaign_id": "cmp-1"}, CHECK), ({**NO_COUPON, "resource": "ordinary_test", "legacy_order_id": 2}, CHECK), ({**NO_COUPON, "resource": "campaign_place", "claim_id": "tc-1"}, CHECK), ({**NO_COUPON, "resource": "campaign_place", "legacy_test_ref": "legacy-test-50001-1", "campaign_id": "cmp-1"}, CHECK), ({**NO_COUPON, "resource": "campaign_place", "claim_id": "tc-1", "campaign_id": "cmp-1", "coupon_code_id": 7}, CHECK), ({**TRANSITION}, CHECK), ({"state": "consumed"}, CHECK), ({"state": "consumed", "transition_key": "op-t1"}, CHECK), ({"transitioned_at": T0 + 1_000}, CHECK), ({**NO_COUPON, "resource": "ordinary_test", "claim_id": "tc-1", "state": "release_pending_refund", **TRANSITION}, CHECK), ({"state": "uncertain_hold", **TRANSITION}, CHECK), ({"sequence": 0}, CHECK), ({"sequence": 1.5}, CHECK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: resource_reservations.{col}")) for col in ("resource", "tenant_installation_id", "customer_telegram_id", "sequence", "accepted_at", "state")],
], ids=lambda value: _case_id(value))
def test_reservation_values(main_db, changes, expected):
    _chain89(main_db, until="resource_reservations")
    _case_error(main_db, "resource_reservations", changes, expected)


def test_reservation_is_unique_per_holder_and_resource(main_db):
    _chain89(main_db, until="composite_campaign_recipients")
    _test_offer(main_db, "of-t2")
    _put89(main_db, "composite_test_claims", claim_id="tc-2", offer_id="of-t2", accepted_seq=2, customer_telegram_id=50002, **PENDING_CLAIM)
    _campaign2(main_db)
    cases = [({"reservation_id": "rr-4", "sequence": 4, "coupon_code_id": 8}, "UNIQUE constraint failed: resource_reservations.checkout_id, resource_reservations.resource"), ({"reservation_id": "rr-5", "resource": "ordinary_test", "sequence": 5, **CLAIM_HOLD}, "UNIQUE constraint failed: resource_reservations.claim_id, resource_reservations.resource"), ({"reservation_id": "rr-6", "checkout_id": None, "legacy_order_id": 2, "customer_telegram_id": 50002, "sequence": 6}, None), ({"reservation_id": "rr-7", "checkout_id": None, "legacy_order_id": 2, "customer_telegram_id": 50002, "sequence": 7, "coupon_code_id": 8}, "UNIQUE constraint failed: resource_reservations.legacy_order_id, resource_reservations.resource"), ({"reservation_id": "rr-8", "resource": "ordinary_test", "checkout_id": None, "coupon_code_id": None, "legacy_test_ref": "legacy-test-50002-1", "customer_telegram_id": 50002, "sequence": 8}, None), ({"reservation_id": "rr-9", "resource": "ordinary_test", "checkout_id": None, "coupon_code_id": None, "legacy_test_ref": "legacy-test-50002-1", "customer_telegram_id": 50002, "sequence": 9}, "UNIQUE constraint failed: resource_reservations.legacy_test_ref, resource_reservations.resource"), ({"reservation_id": "rr-10", "resource": "ordinary_test", "checkout_id": None, "coupon_code_id": None, "legacy_test_ref": "legacy-test-50002-2", "customer_telegram_id": 50002, "sequence": 1}, "UNIQUE constraint failed: resource_reservations.sequence"), ({"reservation_id": "rr-11", "resource": "campaign_place", "checkout_id": None, "coupon_code_id": None, "claim_id": "tc-2", "customer_telegram_id": 50002, "sequence": 11, "campaign_id": "cmp-2"}, FK), ({"reservation_id": "rr-12", "resource": "campaign_place", "checkout_id": None, "coupon_code_id": None, "claim_id": "tc-2", "customer_telegram_id": 50002, "sequence": 12, "campaign_id": "cmp-1"}, None)]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "resource_reservations", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected) if expected.startswith("UNIQUE") else expected):
                _put89(main_db, "resource_reservations", **changes)


def test_finished_reservations_never_change(main_db):
    _chain89(main_db, until="composite_campaign_recipients")
    _checkout2(main_db)
    _put89(main_db, "resource_reservations", reservation_id="rr-4", checkout_id="ck-2", sequence=4, state="release_pending_refund", **TRANSITION)
    main_db.execute(MOVE, ("consumed", "fulfil:ck-1", T0 + 2_000, "rr-1"))
    for args in [("released", "release:ck-1", T0 + 3_000, "rr-1"), ("held", None, None, "rr-1"), ("held", None, None, "rr-4"), ("consumed", "fulfil:ck-2", T0 + 3_000, "rr-4")]:
        _trigger_refuses(main_db, MOVE, args)
    main_db.execute(MOVE, ("released", "refund-settled:ck-2", T0 + 3_000, "rr-4"))
    for args in [("held", None, None, "rr-4"), ("release_pending_refund", "x", T0 + 4_000, "rr-4")]:
        _trigger_refuses(main_db, MOVE, args)
    _put89(main_db, "resource_reservations", reservation_id="rr-5", resource="ordinary_test", checkout_id=None, coupon_code_id=None, legacy_test_ref="legacy-test-50001-1", sequence=5)
    main_db.execute(MOVE, ("uncertain_hold", "deadline:legacy-test-50001-1", T0 + 900_000, "rr-5"))
    main_db.execute(MOVE, ("released", "confirmed-failure:legacy-test-50001-1", T0 + 950_000, "rr-5"))


@pytest.mark.parametrize("column, value", [("coupon_code_id", 8), ("sequence", 40), ("checkout_id", "ck-2"), ("customer_telegram_id", 50002), ("tenant_installation_id", "inst-other"), ("accepted_at", T0 + 1), ("resource", "ordinary_test"), ("campaign_id", "cmp-1")], ids=["coupon", "sequence", "checkout", "customer", "tenant", "accepted", "resource", "campaign"])
def test_reservation_holder_and_resource_never_change(main_db, column, value):
    _chain89(main_db, until="composite_campaign_recipients")
    _trigger_refuses(main_db, f"UPDATE resource_reservations SET {column} = ? WHERE reservation_id = 'rr-1'", (value,))


def test_reservations_and_recipients_are_permanent(main_db):
    _chain89(main_db, until="composite_campaign_recipients")
    _trigger_refuses(main_db, "UPDATE resource_reservations SET campaign_id = 'cmp-1', resource = 'campaign_place' WHERE reservation_id = 'rr-2'")
    _trigger_refuses(main_db, "DELETE FROM resource_reservations WHERE reservation_id = 'rr-1'")


def test_campaign_recipient_once_per_user_and_claim(main_db):
    _chain89(main_db, until="composite_campaign_recipients")
    for offer_id in ("of-t2", "of-t3", "of-t4", "of-t5"):
        _test_offer(main_db, offer_id)
    _put89(main_db, "composite_test_claims", claim_id="tc-p", offer_id="of-t2", accepted_seq=2, customer_telegram_id=50002, **PENDING_CLAIM)
    _put89(main_db, "composite_test_claims", claim_id="tc-o", offer_id="of-t3", accepted_seq=3, customer_telegram_id=50003, campaign_id=None)
    _put89(main_db, "composite_test_claims", claim_id="tc-2", offer_id="of-t4", accepted_seq=4)
    _campaign2(main_db)
    _put89(main_db, "composite_test_claims", claim_id="tc-3", offer_id="of-t5", accepted_seq=5, campaign_id="cmp-2")
    cases = [({"customer_telegram_id": 50002, "claim_id": "tc-p"}, FK), ({"customer_telegram_id": 50002, "claim_id": "tc-p", "claim_status": "pending"}, CHECK), ({"customer_telegram_id": 50003, "claim_id": "tc-o"}, FK), ({"customer_telegram_id": 50002, "claim_id": "tc-2"}, FK), ({}, None), ({"claim_id": "tc-2"}, "UNIQUE constraint failed: composite_campaign_recipients.campaign_id, composite_campaign_recipients.customer_telegram_id"), ({"campaign_id": "cmp-2", "claim_id": "tc-1"}, "UNIQUE constraint failed: composite_campaign_recipients.claim_id"), ({"campaign_id": "cmp-2", "claim_id": "tc-3"}, None)]
    for changes, expected in cases:
        if expected is None:
            _put89(main_db, "composite_campaign_recipients", **changes)
        else:
            with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected) if expected.startswith("UNIQUE") else expected):
                _put89(main_db, "composite_campaign_recipients", **changes)


def test_campaign_recipients_are_permanent(main_db):
    _chain89(main_db)
    _trigger_refuses(main_db, "UPDATE composite_campaign_recipients SET fulfilled_at = ? WHERE claim_id = 'tc-1'", (T0 + 1,))
    _trigger_refuses(main_db, "DELETE FROM composite_campaign_recipients WHERE claim_id = 'tc-1'")
    assert _one(main_db, "SELECT campaign_id, customer_telegram_id, claim_id, fulfilled_at FROM composite_campaign_recipients WHERE claim_id='tc-1'") == ("cmp-1", 50001, "tc-1", T0 + 300_000)


# Data-model §10 lifecycle work, drift and discrepancies (T034e: checks for T040 part a)

DESCRIPTOR_A1_OLD = '{"address": "a.example.invalid", "port": 8443, "sni": "a.example.invalid", "fingerprint": "chrome", "flow": "xtls-rprx-vision"}'
ROWS_10 = {
    "composite_operations": {"operation_id": "op-1", "business_key": "fulfil:ck-1", "kind": "fulfillment", "subscription_id": "sub-1", "checkout_id": "ck-1", "claim_id": None, "discrepancy_id": None, "actor": "system:worker", "reason": None, "desired_revision": 1, "status": "in_progress", "phase": "create_children", "accepted_at": T0 + 1_000, "authorized_at": T0 + 1_000, "ready_at": None, "final_stage_at": None, "target_at": None, "deadline_at": T0 + 901_000, "escalation_at": None, "missed_target_at": None, "prerequisite_ref": None, "recovery_evidence_ref": None, "worker_epoch": 1, "restore_epoch": 0, "last_error": None, "escalation_ref": None, "finished_at": None},
    "composite_remote_work": {"work_id": "rw-1", "operation_id": "op-1", "child_id": "ch-1", "action": "create", "desired_revision": 1, "payload_fingerprint": "payload-fp-1", "encrypted_ref": None, "status": "dispatched", "next_attempt_at": None, "observed_state": None, "observed_at": None, "observed_matches": None, "runtime_required": 0, "runtime_evidence_ref": None, "confirmed_at": None, "hold_reason": None, "created_at": T0 + 1_000},
    "composite_remote_attempts": {"attempt_id": "ra-1", "work_id": "rw-1", "attempt_no": 1, "dispatched_at": T0 + 2_000, "timeout_ms": 15_000, "worker_epoch": 1, "outcome": "applied", "completed_at": T0 + 2_500, "connection_closed_at": None, "quarantine_until": None, "error_ref": None},
    "composite_drift_sweeps": {"sweep_id": "sw-1", "physical_panel_id": "pp-a", "inbound_id": 1, "started_at": T0 + 30_000, "timeout_ms": 15_000, "ended_at": None, "outcome": None, "error_ref": None},
    "composite_discrepancies": {"discrepancy_id": "dc-1", "kind": "descriptor", "child_id": None, "binding_id": "pb-a1", "observed_values": DESCRIPTOR_A1_NEW, "observed_at": T0 + 60_000, "detected_at": T0 + 60_000, "closed_at": None, "closure_reason": None},
    "composite_discrepancy_descriptors": {"discrepancy_id": "dc-1", "discrepancy_kind": "descriptor", "descriptor": DESCRIPTOR_A1, "recorded_at": T0 + 60_000},
    "composite_divergences": {"divergence_id": "dv-1", "sweep_id": "sw-1", "physical_panel_id": "pp-a", "child_id": "ch-1", "kind": "state", "observed_fields": '{"enable": false}', "desired_fields": '{"enable": true}', "detected_at": T0 + 30_400, "repeat_count": 1, "repair_work_id": None, "repair_state": "pending", "repaired_at": None, "discrepancy_id": None, "exposure": "access_lost", "exposure_from": T0 + 2_500, "exposure_resolved_at": None},
}
EXPECTED_FKS_10 = (
    ("composite_operations", ("subscription_id",), "composite_subscriptions", ("subscription_id",)), ("composite_operations", ("checkout_id",), "composite_checkouts", ("checkout_id",)), ("composite_operations", ("claim_id",), "composite_test_claims", ("claim_id",)), ("composite_operations", ("discrepancy_id",), "composite_discrepancies", ("discrepancy_id",)),
    ("composite_remote_work", ("operation_id",), "composite_operations", ("operation_id",)), ("composite_remote_work", ("child_id",), "composite_children", ("child_id",)), ("composite_remote_attempts", ("work_id",), "composite_remote_work", ("work_id",)), ("composite_drift_sweeps", ("physical_panel_id",), "composite_physical_panels", ("physical_panel_id",)),
    ("composite_discrepancies", ("child_id",), "composite_children", ("child_id",)), ("composite_discrepancies", ("binding_id",), "composite_prepared_bindings", ("binding_id",)), ("composite_discrepancy_descriptors", ("discrepancy_id", "discrepancy_kind"), "composite_discrepancies", ("discrepancy_id", "kind")),
    ("composite_divergences", ("sweep_id", "physical_panel_id"), "composite_drift_sweeps", ("sweep_id", "physical_panel_id")), ("composite_divergences", ("child_id", "physical_panel_id"), "composite_children", ("child_id", "physical_panel_id")), ("composite_divergences", ("repair_work_id", "child_id"), "composite_remote_work", ("work_id", "child_id")), ("composite_divergences", ("discrepancy_id", "child_id"), "composite_discrepancies", ("discrepancy_id", "child_id")),
)
SUBSCRIPTION_KINDS = ("customer_disable", "customer_resume", "owner_suspend", "owner_resume", "reporting_suspend", "reporting_resume", "leak_replacement", "cancellation", "move", "cleanup", "drift_repair")
ON_SUB = {"checkout_id": None, "authorized_at": None, "deadline_at": None}
CONFIRMED = {"status": "confirmed", "observed_state": '{"enable": true}', "observed_at": T0 + 3_000, "observed_matches": 1, "confirmed_at": T0 + 3_000}
IN_FLIGHT = {"outcome": "in_flight", "completed_at": None}
UNCERTAIN = {"outcome": "uncertain", "completed_at": None, "connection_closed_at": T0 + 17_000, "quarantine_until": T0 + 47_000}
CHILD_DISCREPANCY = {"kind": "repeated_divergence", "child_id": "ch-1", "binding_id": None, "observed_values": None, "observed_at": None}
REPAIRED = {"repair_work_id": "rw-r", "repair_state": "repaired", "repaired_at": T0 + 31_000}
NOT_REPAIRABLE = {"kind": "missing", "observed_fields": "{}", "repair_state": "not_repairable", "discrepancy_id": "dc-c1"}
CONFIRM = "UPDATE composite_remote_work SET status = 'confirmed', observed_state = 'read-back-1', observed_at = ?, observed_matches = 1, confirmed_at = ? WHERE work_id = 'rw-1'"
FINISH = "UPDATE composite_drift_sweeps SET ended_at = ?, outcome = ?, error_ref = ? WHERE sweep_id = ?"


def _put10(conn, table, **changes):
    row = {**ROWS_10[table], **changes}
    cols = tuple(row)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", tuple(row.values()))


def _chain10(conn, until=None):
    assert until is None or until in ROWS_10
    _chain57(conn, until="composite_child_attachments")
    _order(conn, 101)
    _put89(conn, "composite_checkouts", **WALLET_AUTH)
    _insert(conn, "composite_plans", plan_id="cp-camp", kind="campaign")
    _insert(conn, "composite_plan_versions", plan_version_id="cpv-camp-1", plan_id="cp-camp", kind="campaign", allowance_bytes=16_106_127_360, duration_seconds=1_296_000, base_price=0)
    _test_offer(conn, "of-t1")
    _put89(conn, "composite_test_claims", campaign_id=None)
    for table in ROWS_10:
        if table == until:
            break
        _put10(conn, table)


def _child2(conn):
    _put(conn, "composite_children", child_id="ch-2", credential_generation=2, remote_email="cmp1-d8e4b0", secret_fingerprint="secret-fp-2", meter_id=None)


def _repair_parents(conn):
    _put10(conn, "composite_operations", operation_id="op-r", business_key="repair:ch-1", kind="drift_repair", **ON_SUB)
    _put10(conn, "composite_remote_work", work_id="rw-r", operation_id="op-r", action="enable")
    _put10(conn, "composite_discrepancies", discrepancy_id="dc-c1", **CHILD_DISCREPANCY)


def test_main_gets_the_section_10_tables(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        tables = _tables(conn)
        for table, row in ROWS_10.items():
            assert table in tables
            assert set(row) <= set(_columns(conn, table))


def test_section_10_foreign_keys_are_restrict(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        found = set()
        for table in ROWS_10:
            groups = {}
            for row in conn.execute(f"PRAGMA foreign_key_list({table})"):
                groups.setdefault(row[0], []).append(row)
            for rows in groups.values():
                rows.sort(key=lambda row: row[1])
                parent = rows[0][2]
                cols = tuple(row[4] for row in rows)
                if any(col is None for col in cols):
                    cols = tuple(row[1] for row in sorted((row for row in conn.execute(f"PRAGMA table_info({parent})") if row[5] > 0), key=lambda row: row[5]))
                found.add((table, tuple(row[3] for row in rows), parent, cols))
                assert all(row[6] == "RESTRICT" for row in rows)
        assert set(EXPECTED_FKS_10) <= found


def test_rows_in_every_section_10_table_survive_a_rerun(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _chain10(conn)
        conn.commit()
    before = _dump(install.main)
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(migrations.SCHEMA_VERSION, migrations.SCHEMA_VERSION, "unchanged")
    assert _dump(install.main) == before
    _check_clean(install.main)
    with closing(sqlite3.connect(install.main)) as conn:
        assert all(_one(conn, f"SELECT count(*) FROM {table}")[0] == 1 for table in ROWS_10)


def _expect10(conn, table, changes, expected):
    if expected == "accepted":
        _put10(conn, table, **changes)
    elif expected == "TRG":
        with pytest.raises(sqlite3.IntegrityError) as error:
            _put10(conn, table, **changes)
        assert "constraint failed" not in str(error.value)
    else:
        with pytest.raises(sqlite3.IntegrityError, match=expected):
            _put10(conn, table, **changes)


def _uq10(*columns):
    return re.escape("UNIQUE constraint failed: " + ", ".join(f"{table}.{column}" for table, column in columns))


@pytest.mark.parametrize("case", ["sweep", "binding", "panel"], ids=["sweep-with-divergence", "binding-with-discrepancy", "panel-with-sweep"])
def test_section_10_parents_cannot_be_deleted(main_db, case):
    _chain10(main_db)
    if case == "sweep":
        sql, parent, key = "DELETE FROM composite_drift_sweeps WHERE sweep_id = 'sw-1'", "composite_drift_sweeps", "sweep_id='sw-1'"
    elif case == "binding":
        _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
        _put10(main_db, "composite_discrepancies", discrepancy_id="dc-2", binding_id="pb-a2")
        sql, parent, key = "DELETE FROM composite_prepared_bindings WHERE binding_id = 'pb-a2'", "composite_prepared_bindings", "binding_id='pb-a2'"
    else:
        _panel_b(main_db)
        _put10(main_db, "composite_drift_sweeps", sweep_id="sw-b", physical_panel_id="pp-b")
        sql, parent, key = "DELETE FROM composite_physical_panels WHERE physical_panel_id = 'pp-b'", "composite_physical_panels", "physical_panel_id='pp-b'"
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        main_db.execute(sql)
    assert _one(main_db, f"SELECT {key.split('=')[0]} FROM {parent} WHERE {key}")[0] is not None


@pytest.mark.parametrize("index,changes", list(enumerate((
    {"subscription_id": "sub-missing"}, {"checkout_id": "ck-missing"},
    {"kind": "test_fulfillment", "checkout_id": None, "claim_id": "tc-missing"},
    {"kind": "checkout_rejection", "discrepancy_id": "dc-missing"},
    {"operation_id": "op-missing"}, {"child_id": "ch-missing"}, {"work_id": "rw-missing"},
    {"physical_panel_id": "pp-missing"}, {**CHILD_DISCREPANCY, "child_id": "ch-missing"}, {"binding_id": "pb-missing"},
    {"discrepancy_id": "dc-missing"}, {"sweep_id": "sw-missing"}, {"child_id": "ch-missing"},
    {"repair_work_id": "rw-missing"}, {"discrepancy_id": "dc-missing"},
), 1)), ids=[f"fk-{i}" for i in range(1, 16)])
def test_section_10_child_row_needs_its_parent(main_db, index, changes):
    table = EXPECTED_FKS_10[index - 1][0]
    _chain10(main_db, until=table)
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        _put10(main_db, table, **changes)


_OPERATION_CASES = [
    ({"kind": "test_fulfillment", "business_key": "test:tc-1", "checkout_id": None, "claim_id": "tc-1"}, "accepted"),
    ({"kind": "checkout_rejection", "business_key": "reject:ck-1", "subscription_id": None, "authorized_at": None, "deadline_at": None}, "accepted"),
    *[({"kind": k, "business_key": f"{k}:sub-1", **ON_SUB}, "accepted") for k in SUBSCRIPTION_KINDS],
    ({"subscription_id": None}, "accepted"), ({"status": "accepted"}, "accepted"),
    ({"status": "manual_hold", "last_error": "attempts exhausted"}, "accepted"),
    *[({"status": status, "finished_at": T0 + 300_000}, "accepted") for status in ("succeeded", "failed", "superseded")],
    ({"status": "failed", "finished_at": T0 + 1_000}, "accepted"), ({"desired_revision": None}, "accepted"),
    ({"desired_revision": 0}, "accepted"), ({"ready_at": T0 + 1_000, "final_stage_at": T0 + 1_000, "target_at": T0 + 1_000, "escalation_at": T0 + 1_000, "deadline_at": T0 + 1_000}, "accepted"),
    ({"target_at": T0 + 61_000, "missed_target_at": T0 + 61_000}, "accepted"),
    *[({"kind": "refund", **ON_SUB}, CHECK), ({"status": "running"}, CHECK), ({"status": "succeeded"}, CHECK), ({"finished_at": T0 + 300_000}, CHECK), ({"status": "succeeded", "finished_at": T0 + 999}, CHECK),
      ({"checkout_id": None}, CHECK), ({"claim_id": "tc-1"}, CHECK), ({"kind": "test_fulfillment", "claim_id": "tc-1"}, CHECK), ({"kind": "test_fulfillment", "checkout_id": None}, CHECK),
      ({"kind": "checkout_rejection", "checkout_id": None}, CHECK), ({"kind": "checkout_rejection", "claim_id": "tc-1"}, CHECK), ({"kind": "customer_disable"}, CHECK),
      ({"kind": "customer_disable", **ON_SUB, "subscription_id": None}, CHECK), ({"kind": "customer_disable", **ON_SUB, "claim_id": "tc-1"}, CHECK),
      *[({col: T0 + 999}, CHECK) for col in ("authorized_at", "ready_at", "final_stage_at", "target_at", "deadline_at", "escalation_at")],
      ({"missed_target_at": T0 + 61_000}, CHECK), ({"target_at": T0 + 61_000, "missed_target_at": T0 + 60_999}, CHECK),
      ({"desired_revision": -1}, CHECK), ({"desired_revision": 1.5}, CHECK), ({"restore_epoch": -1}, CHECK), ({"restore_epoch": "n/a"}, CHECK)],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_operations.{col}")) for col in ("business_key", "kind", "actor", "status", "accepted_at", "restore_epoch")],
]


@pytest.mark.parametrize("changes,expected", _OPERATION_CASES, ids=[_case_id(changes) for changes, _ in _OPERATION_CASES])
def test_operation_column_values(main_db, changes, expected):
    _chain10(main_db, until="composite_operations")
    _expect10(main_db, "composite_operations", changes, expected)


def test_operation_command_identity_is_unique(main_db):
    _chain10(main_db, until="composite_remote_work")
    _checkout2(main_db)
    with pytest.raises(sqlite3.IntegrityError, match=re.escape("UNIQUE constraint failed: composite_operations.business_key")):
        _put10(main_db, "composite_operations", operation_id="op-2", kind="customer_disable", **ON_SUB)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_operations", "checkout_id"), ("composite_operations", "kind"))):
        _put10(main_db, "composite_operations", operation_id="op-3", business_key="fulfil:ck-1:again")
    _put10(main_db, "composite_operations", operation_id="op-4", business_key="fulfil:ck-2", checkout_id="ck-2", subscription_id=None)
    _put10(main_db, "composite_operations", operation_id="op-5", business_key="test:tc-1", kind="test_fulfillment", checkout_id=None, claim_id="tc-1")
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_operations", "claim_id"), ("composite_operations", "kind"))):
        _put10(main_db, "composite_operations", operation_id="op-6", business_key="test:tc-1:again", kind="test_fulfillment", checkout_id=None, claim_id="tc-1")


def _sql10(conn, sql, args=(), expected="accepted"):
    if expected == "accepted":
        conn.execute(sql, args)
        return
    if expected == "TRG":
        _trigger_refuses(conn, sql, args)
        return
    with pytest.raises(sqlite3.IntegrityError, match=expected):
        conn.execute(sql, args)


def test_protective_commands_are_admissible_while_work_is_busy(main_db):
    _chain10(main_db, until="composite_remote_work")
    _sub2(main_db)
    uq_open = _uq10(("composite_operations", "subscription_id"), ("composite_operations", "kind"))
    for op, kind, key in (("op-d", "customer_disable", "disable:sub-1"), ("op-s", "owner_suspend", "suspend:sub-1"), ("op-c", "cancellation", "cancel:sub-1"), ("op-l", "leak_replacement", "leak:sub-1:1")):
        _put10(main_db, "composite_operations", operation_id=op, kind=kind, business_key=key, **ON_SUB, status="accepted" if op == "op-c" else "in_progress")
    def leak2():
        _put10(main_db, "composite_operations", operation_id="op-l2", kind="leak_replacement", business_key="leak:sub-1:2", **ON_SUB)
    with pytest.raises(sqlite3.IntegrityError, match=uq_open):
        _put10(main_db, "composite_operations", operation_id="op-c2", kind="cancellation", business_key="cancel:sub-1:again", **ON_SUB)
    with pytest.raises(sqlite3.IntegrityError, match=uq_open):
        leak2()
    _sql10(main_db, "UPDATE composite_operations SET status = 'manual_hold' WHERE operation_id = 'op-l'")
    with pytest.raises(sqlite3.IntegrityError, match=uq_open):
        leak2()
    _sql10(main_db, "UPDATE composite_operations SET status = 'failed', finished_at = ? WHERE operation_id = 'op-l'", (T0 + 120_000,))
    leak2()
    _put10(main_db, "composite_operations", operation_id="op-d2", kind="customer_disable", business_key="disable:sub-1:again", **ON_SUB)
    _put10(main_db, "composite_operations", operation_id="op-l9", kind="leak_replacement", business_key="leak:sub-2:1", **ON_SUB, subscription_id="sub-2")


@pytest.mark.parametrize("column,value", [("authorized_at", T0 + 2_000), ("deadline_at", T0 + 902_000), ("deadline_at", None), ("subscription_id", "sub-2"), ("desired_revision", 2), ("accepted_at", T0 + 2_000), ("business_key", "fulfil:x"), ("kind", "checkout_rejection"), ("checkout_id", "ck-2"), ("claim_id", "tc-1"), ("actor", "web:owner-1")], ids=["authorized", "deadline-later", "deadline-clear", "subscription", "revision", "accepted", "business-key", "kind", "checkout", "claim", "actor"])
def test_operation_clocks_never_restart(main_db, column, value):
    _chain10(main_db, until="composite_remote_work")
    _sub2(main_db)
    _checkout2(main_db)
    _sql10(main_db, f"UPDATE composite_operations SET {column} = ? WHERE operation_id = 'op-1'", (value,), "TRG")


def test_operation_clock_progression_and_mutable_state(main_db):
    _chain10(main_db, until="composite_remote_work")
    for col, first, second in (("ready_at", T0 + 400_000, T0 + 400_001), ("final_stage_at", T0 + 500_000, T0 + 500_001), ("escalation_at", T0 + 901_000, T0 + 901_001), ("target_at", T0 + 61_000, T0 + 61_001)):
        _sql10(main_db, f"UPDATE composite_operations SET {col} = ? WHERE operation_id = 'op-1'", (first,))
        _sql10(main_db, f"UPDATE composite_operations SET {col} = ? WHERE operation_id = 'op-1'", (second,), "TRG")
    _sql10(main_db, "UPDATE composite_operations SET missed_target_at = ? WHERE operation_id = 'op-1'", (T0 + 61_000,))
    _sql10(main_db, "UPDATE composite_operations SET missed_target_at = NULL WHERE operation_id = 'op-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_operations SET status = 'manual_hold', phase = 'await_owner', last_error = 'attempts exhausted', escalation_ref = 'esc-1', worker_epoch = 2, restore_epoch = 1 WHERE operation_id = 'op-1'")


def test_operation_subscription_can_be_set_once(main_db):
    _chain10(main_db, until="composite_remote_work")
    _checkout2(main_db)
    _put10(main_db, "composite_operations", operation_id="op-n", business_key="fulfil:ck-2", checkout_id="ck-2", subscription_id=None, desired_revision=None, authorized_at=None, deadline_at=None)
    _sql10(main_db, "UPDATE composite_operations SET subscription_id = 'sub-1', desired_revision = 3, authorized_at = ?, deadline_at = ? WHERE operation_id = 'op-n'", (T0 + 5_000, T0 + 905_000))


@pytest.mark.parametrize("status", ["succeeded", "failed", "superseded"])
def test_finished_operations_never_reopen(main_db, status):
    _chain10(main_db, until="composite_remote_work")
    _sql10(main_db, "UPDATE composite_operations SET status = ?, finished_at = ? WHERE operation_id = 'op-1'", (status, T0 + 300_000))
    _sql10(main_db, "UPDATE composite_operations SET status = 'in_progress', finished_at = NULL WHERE operation_id = 'op-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_operations SET phase = 'x' WHERE operation_id = 'op-1'", (), "TRG")


def test_finished_operation_cannot_be_deleted(main_db):
    _chain10(main_db, until="composite_remote_work")
    _sql10(main_db, "DELETE FROM composite_operations WHERE operation_id = 'op-1'", (), "TRG")


def test_rejection_work_links_its_discrepancy(main_db):
    _chain10(main_db, until="composite_divergences")
    _checkout2(main_db)
    reject = {"kind": "checkout_rejection", "checkout_id": "ck-2", "subscription_id": None, "authorized_at": None, "deadline_at": None, "discrepancy_id": "dc-1"}
    _put10(main_db, "composite_operations", operation_id="op-x", business_key="reject:ck-2", **reject)
    with pytest.raises(sqlite3.IntegrityError, match=CHECK):
        _put10(main_db, "composite_operations", operation_id="op-y", business_key="disable:sub-1", kind="customer_disable", **ON_SUB, discrepancy_id="dc-1")
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_operations", "checkout_id"), ("composite_operations", "kind"))):
        _put10(main_db, "composite_operations", operation_id="op-z", business_key="reject:ck-2:again", **reject)
    _sql10(main_db, "UPDATE composite_operations SET discrepancy_id = NULL WHERE operation_id = 'op-x'", (), "TRG")


_WORK_CASES = [
    *[({"action": action}, "accepted") for action in ("enable", "disable", "delete")],
    ({"status": "queued"}, "accepted"), ({"status": "uncertain"}, "accepted"), ({"status": "manual_hold", "hold_reason": "attempts exhausted"}, "accepted"),
    ({"encrypted_ref": SECRET_BLOB}, "accepted"), ({"desired_revision": 0}, "accepted"), (CONFIRMED, "accepted"),
    ({**CONFIRMED, "runtime_required": 1, "runtime_evidence_ref": "runtime-1"}, "accepted"),
    ({"observed_state": '{"enable": false}', "observed_at": T0 + 3_000, "observed_matches": 0}, "accepted"),
    *[({"action": "update"}, CHECK), ({"status": "safe_to_retry"}, CHECK), ({"status": "execution_hold"}, CHECK),
      ({"status": "confirmed", "observed_state": '{"enable": true}', "observed_at": T0 + 3_000, "observed_matches": 1}, CHECK), ({"confirmed_at": T0 + 3_000}, CHECK),
      ({**CONFIRMED, "observed_matches": 0}, CHECK), ({**CONFIRMED, "confirmed_at": T0 + 2_999}, CHECK), ({**CONFIRMED, "runtime_required": 1}, CHECK),
      ({"status": "confirmed", "confirmed_at": T0 + 3_000}, CHECK), ({"status": "manual_hold"}, CHECK), ({"hold_reason": "attempts exhausted"}, CHECK),
      ({"encrypted_ref": "plain-text-ref"}, CHECK), ({"desired_revision": -1}, CHECK), ({"desired_revision": 1.5}, CHECK),
      ({"observed_state": '{"enable": true}'}, CHECK), ({"observed_at": T0 + 3_000}, CHECK), ({"observed_matches": 1}, CHECK),
      ({"observed_state": '{"enable": true}', "observed_at": T0 + 3_000, "observed_matches": 2}, CHECK), ({"runtime_required": 2}, CHECK)],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_remote_work.{col}")) for col in ("operation_id", "child_id", "action", "desired_revision", "payload_fingerprint", "status", "runtime_required", "created_at")],
]


@pytest.mark.parametrize("changes,expected", _WORK_CASES, ids=[_case_id(changes) for changes, _ in _WORK_CASES])
def test_remote_work_column_values(main_db, changes, expected):
    _chain10(main_db, until="composite_remote_work")
    _expect10(main_db, "composite_remote_work", changes, expected)


def test_remote_work_identity_is_unique(main_db):
    _chain10(main_db, until="composite_remote_attempts")
    _child2(main_db)
    dupe = _uq10(("composite_remote_work", "operation_id"), ("composite_remote_work", "child_id"), ("composite_remote_work", "action"), ("composite_remote_work", "desired_revision"))
    with pytest.raises(sqlite3.IntegrityError, match=dupe):
        _put10(main_db, "composite_remote_work", work_id="rw-2")
    _put10(main_db, "composite_remote_work", work_id="rw-3", desired_revision=2)
    _put10(main_db, "composite_remote_work", work_id="rw-4", action="disable")
    _put10(main_db, "composite_remote_work", work_id="rw-5", child_id="ch-2")


@pytest.mark.parametrize("column,value", [("operation_id", "op-2"), ("child_id", "ch-2"), ("action", "enable"), ("desired_revision", 2), ("payload_fingerprint", "payload-fp-x"), ("created_at", T0 + 1)], ids=["operation", "child", "action", "revision", "fingerprint", "created"])
def test_remote_work_identity_never_changes(main_db, column, value):
    _chain10(main_db, until="composite_remote_attempts")
    _child2(main_db)
    _put10(main_db, "composite_operations", operation_id="op-2", business_key="disable:sub-1", kind="customer_disable", **ON_SUB)
    _sql10(main_db, f"UPDATE composite_remote_work SET {column} = ? WHERE work_id = 'rw-1'", (value,), "TRG")


def test_uncertain_work_can_be_rescheduled_but_not_deleted(main_db):
    _chain10(main_db, until="composite_remote_attempts")
    _sql10(main_db, "UPDATE composite_remote_work SET status = 'uncertain', next_attempt_at = ? WHERE work_id = 'rw-1'", (T0 + 47_500,))
    _sql10(main_db, "DELETE FROM composite_remote_work WHERE work_id = 'rw-1'", (), "TRG")


def test_confirmation_needs_a_read_back_after_the_latest_write(main_db):
    _chain10(main_db, until="composite_drift_sweeps")
    _sql10(main_db, CONFIRM, (T0 + 2_000, T0 + 2_000), "TRG")
    _sql10(main_db, CONFIRM, (T0 + 1_500, T0 + 3_000), "TRG")
    _put10(main_db, "composite_remote_attempts", attempt_id="ra-2", attempt_no=2, dispatched_at=T0 + 4_000, **IN_FLIGHT)
    _sql10(main_db, CONFIRM, (T0 + 3_000, T0 + 3_000), "TRG")
    _sql10(main_db, CONFIRM, (T0 + 4_001, T0 + 4_001))
    _sql10(main_db, "UPDATE composite_remote_work SET status = 'dispatched', confirmed_at = NULL WHERE work_id = 'rw-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_remote_work SET observed_at = ? WHERE work_id = 'rw-1'", (T0 + 5_000,), "TRG")
    _expect10(main_db, "composite_remote_attempts", {"attempt_id": "ra-3", "attempt_no": 3, "dispatched_at": T0 + 6_000, "completed_at": T0 + 6_500}, "TRG")


def test_remote_work_without_writes_can_confirm_from_readback(main_db):
    _chain10(main_db, until="composite_drift_sweeps")
    _put10(main_db, "composite_remote_work", work_id="rw-2", desired_revision=2, **CONFIRMED)


_ATTEMPT_CASES = [
    (UNCERTAIN, "accepted"), (IN_FLIGHT, "accepted"), ({"outcome": "rejected_no_effect", "error_ref": "database is locked"}, "accepted"),
    ({"attempt_no": 5}, "accepted"), ({"completed_at": T0 + 17_000}, "accepted"), ({"completed_at": T0 + 2_000}, "accepted"),
    ({"timeout_ms": 1, "completed_at": T0 + 2_001}, "accepted"), ({**UNCERTAIN, "connection_closed_at": T0 + 2_000, "quarantine_until": T0 + 32_000}, "accepted"),
    *[({"attempt_no": 0}, CHECK), ({"attempt_no": 6}, CHECK), ({"attempt_no": 1.5}, CHECK), ({**IN_FLIGHT, "timeout_ms": 0}, CHECK), ({**IN_FLIGHT, "timeout_ms": 15_001}, CHECK), ({"timeout_ms": 1_000.5}, CHECK), ({"worker_epoch": -1}, CHECK),
      ({"outcome": "timeout"}, CHECK), ({"outcome": "confirmed"}, CHECK), ({"completed_at": None}, CHECK), ({"completed_at": T0 + 1_999}, CHECK), ({"completed_at": T0 + 17_001}, CHECK),
      ({"connection_closed_at": T0 + 2_500}, CHECK), ({"quarantine_until": T0 + 32_500}, CHECK), ({**IN_FLIGHT, "completed_at": T0 + 2_500}, CHECK), ({**IN_FLIGHT, "connection_closed_at": T0 + 17_000}, CHECK), ({**IN_FLIGHT, "quarantine_until": T0 + 47_000}, CHECK),
      ({**UNCERTAIN, "completed_at": T0 + 2_500}, CHECK), ({**UNCERTAIN, "connection_closed_at": None}, CHECK), ({**UNCERTAIN, "quarantine_until": None}, CHECK), ({**UNCERTAIN, "quarantine_until": T0 + 17_000}, CHECK), ({**UNCERTAIN, "quarantine_until": T0 + 16_999}, CHECK),
      ({**UNCERTAIN, "connection_closed_at": T0 + 1_999, "quarantine_until": T0 + 31_999}, CHECK), ({"outcome": "rejected_no_effect"}, CHECK)],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_remote_attempts.{col}")) for col in ("work_id", "attempt_no", "dispatched_at", "timeout_ms", "worker_epoch", "outcome")],
]


@pytest.mark.parametrize("changes,expected", _ATTEMPT_CASES, ids=[_case_id(changes) for changes, _ in _ATTEMPT_CASES])
def test_attempt_values(main_db, changes, expected):
    _chain10(main_db, until="composite_remote_attempts")
    _expect10(main_db, "composite_remote_attempts", changes, expected)


def test_at_most_five_attempts_per_work(main_db):
    _chain10(main_db, until="composite_drift_sweeps")
    for n in (2, 3, 4, 5):
        _put10(main_db, "composite_remote_attempts", attempt_id=f"ra-{n}", attempt_no=n, dispatched_at=T0 + n * 20_000, completed_at=T0 + n * 20_000 + 500)
    uq = _uq10(("composite_remote_attempts", "work_id"), ("composite_remote_attempts", "attempt_no"))
    with pytest.raises(sqlite3.IntegrityError, match=uq):
        _put10(main_db, "composite_remote_attempts", attempt_id="ra-6", attempt_no=5, dispatched_at=T0 + 120_000, completed_at=T0 + 120_500)
    with pytest.raises(sqlite3.IntegrityError, match=CHECK):
        _put10(main_db, "composite_remote_attempts", attempt_id="ra-6", attempt_no=6, dispatched_at=T0 + 120_000, completed_at=T0 + 120_500)
    _put10(main_db, "composite_remote_work", work_id="rw-2", desired_revision=2)
    _put10(main_db, "composite_remote_attempts", attempt_id="ra-7", work_id="rw-2", dispatched_at=T0 + 140_000, completed_at=T0 + 140_500)


def test_attempt_outcome_and_quarantine_are_final(main_db):
    _chain10(main_db, until="composite_drift_sweeps")
    _put10(main_db, "composite_remote_attempts", attempt_id="ra-2", attempt_no=2, dispatched_at=T0 + 20_000, **IN_FLIGHT)
    _sql10(main_db, "UPDATE composite_remote_attempts SET outcome = 'uncertain', connection_closed_at = ?, quarantine_until = ? WHERE attempt_id = 'ra-2'", (T0 + 35_000, T0 + 65_000))
    _sql10(main_db, "UPDATE composite_remote_attempts SET quarantine_until = ? WHERE attempt_id = 'ra-2'", (T0 + 50_000,), "TRG")
    _sql10(main_db, "UPDATE composite_remote_attempts SET outcome = 'applied', completed_at = ?, connection_closed_at = NULL, quarantine_until = NULL WHERE attempt_id = 'ra-2'", (T0 + 30_000,), "TRG")
    _sql10(main_db, "UPDATE composite_remote_attempts SET outcome = 'uncertain', completed_at = NULL, connection_closed_at = ?, quarantine_until = ? WHERE attempt_id = 'ra-1'", (T0 + 17_000, T0 + 47_000), "TRG")
    _sql10(main_db, "UPDATE composite_remote_attempts SET error_ref = 'x' WHERE attempt_id = 'ra-1'", (), "TRG")
    _sql10(main_db, "DELETE FROM composite_remote_attempts WHERE attempt_id = 'ra-1'", (), "TRG")


@pytest.mark.parametrize("column,value", [("work_id", "rw-2"), ("attempt_no", 3), ("dispatched_at", T0 + 20_001), ("timeout_ms", 10_000), ("worker_epoch", 2)], ids=["work", "number", "dispatch", "timeout", "epoch"])
def test_attempt_identity_never_changes(main_db, column, value):
    _chain10(main_db, until="composite_drift_sweeps")
    _put10(main_db, "composite_remote_work", work_id="rw-2", desired_revision=2)
    _put10(main_db, "composite_remote_attempts", attempt_id="ra-2", attempt_no=2, dispatched_at=T0 + 20_000, **IN_FLIGHT)
    _sql10(main_db, f"UPDATE composite_remote_attempts SET {column} = ? WHERE attempt_id = 'ra-2'", (value,), "TRG")


def test_in_flight_attempt_can_be_definitely_rejected(main_db):
    _chain10(main_db, until="composite_drift_sweeps")
    _put10(main_db, "composite_remote_attempts", attempt_id="ra-2", attempt_no=2, dispatched_at=T0 + 20_000, **IN_FLIGHT)
    _sql10(main_db, "UPDATE composite_remote_attempts SET outcome = 'rejected_no_effect', completed_at = ?, error_ref = 'database is locked' WHERE attempt_id = 'ra-2'", (T0 + 30_000,))


_SWEEP_CASES = [
    ({"ended_at": T0 + 30_400, "outcome": "consistent"}, "accepted"), ({"ended_at": T0 + 45_000, "outcome": "consistent"}, "accepted"),
    ({"ended_at": T0 + 45_001, "outcome": "unknown", "error_ref": "read timed out"}, "accepted"), ({"ended_at": T0 + 30_100, "outcome": "unknown", "error_ref": "tls handshake failed"}, "accepted"),
    *[({"outcome": "drifted", "ended_at": T0 + 30_400}, CHECK), ({"outcome": "consistent"}, CHECK), ({"ended_at": T0 + 30_400}, CHECK), ({"ended_at": T0 + 29_999, "outcome": "unknown", "error_ref": "x"}, CHECK),
      ({"ended_at": T0 + 45_001, "outcome": "consistent"}, CHECK), ({"ended_at": T0 + 30_400, "outcome": "unknown"}, CHECK), ({"ended_at": T0 + 30_400, "outcome": "consistent", "error_ref": "x"}, CHECK), ({"error_ref": "x"}, CHECK),
      ({"timeout_ms": 0}, CHECK), ({"timeout_ms": 15_001}, CHECK), ({"timeout_ms": 1.5}, CHECK), ({"ended_at": T0 + 30_400, "outcome": "diverged"}, "TRG")],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_drift_sweeps.{col}")) for col in ("physical_panel_id", "inbound_id", "started_at", "timeout_ms")],
]


@pytest.mark.parametrize("changes,expected", _SWEEP_CASES, ids=[_case_id(changes) for changes, _ in _SWEEP_CASES])
def test_sweep_values(main_db, changes, expected):
    _chain10(main_db, until="composite_drift_sweeps")
    if expected == "TRG":
        with pytest.raises(sqlite3.IntegrityError) as error:
            _put10(main_db, "composite_drift_sweeps", **changes)
        assert "constraint failed" not in str(error.value)
    else:
        _expect10(main_db, "composite_drift_sweeps", changes, expected)


def test_sweep_outcome_matches_its_divergences(main_db):
    _chain10(main_db)
    _sql10(main_db, FINISH, (T0 + 30_400, "consistent", None, "sw-1"), "TRG")
    _sql10(main_db, FINISH, (T0 + 30_400, "diverged", None, "sw-1"))
    with pytest.raises(sqlite3.IntegrityError) as error:
        _put10(main_db, "composite_divergences", divergence_id="dv-2", detected_at=T0 + 30_500)
    assert "constraint failed" not in str(error.value)
    _sql10(main_db, "UPDATE composite_drift_sweeps SET outcome = 'consistent' WHERE sweep_id = 'sw-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_drift_sweeps SET ended_at = ? WHERE sweep_id = 'sw-1'", (T0 + 30_500,), "TRG")
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-2", started_at=T0 + 60_000)
    _sql10(main_db, FINISH, (T0 + 60_400, "diverged", None, "sw-2"), "TRG")
    _sql10(main_db, FINISH, (T0 + 60_400, "consistent", None, "sw-2"))
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-3", started_at=T0 + 90_000)
    _put10(main_db, "composite_divergences", divergence_id="dv-3", sweep_id="sw-3", detected_at=T0 + 90_200, repeat_count=2)
    _sql10(main_db, FINISH, (T0 + 105_001, "unknown", "read timed out", "sw-3"))


@pytest.mark.parametrize("column,value", [("physical_panel_id", "pp-b"), ("inbound_id", 2), ("started_at", T0 + 60_001), ("timeout_ms", 10_000)], ids=["panel", "inbound", "start", "timeout"])
def test_running_sweep_identity_never_changes(main_db, column, value):
    _chain10(main_db)
    _panel_b(main_db)
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-2", started_at=T0 + 60_000)
    _sql10(main_db, f"UPDATE composite_drift_sweeps SET {column} = ? WHERE sweep_id = 'sw-2'", (value,), "TRG")


def test_finished_sweep_without_divergences_can_be_compacted(main_db):
    _chain10(main_db)
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-2", started_at=T0 + 60_000, ended_at=T0 + 60_400, outcome="consistent")
    _sql10(main_db, "DELETE FROM composite_drift_sweeps WHERE sweep_id = 'sw-2'")
    assert _one(main_db, "SELECT sweep_id FROM composite_drift_sweeps WHERE sweep_id='sw-2'") is None


_DISCREPANCY_CASES = [
    (CHILD_DISCREPANCY, "accepted"), ({**CHILD_DISCREPANCY, "kind": "identity"}, "accepted"), ({"observed_at": T0 + 90_000}, "accepted"),
    ({"closed_at": T0 + 120_000, "closure_reason": "panel_restored"}, "accepted"), ({"closed_at": T0 + 120_000, "closure_reason": "no_longer_in_use"}, "accepted"),
    ({**CHILD_DISCREPANCY, "closed_at": T0 + 120_000, "closure_reason": "owner_resolved"}, "accepted"), ({"closed_at": T0 + 60_000, "closure_reason": "panel_restored"}, "accepted"),
    *[({**CHILD_DISCREPANCY, "kind": "drift"}, CHECK), ({"binding_id": None}, CHECK), ({"child_id": "ch-1"}, CHECK), ({"observed_values": None}, CHECK), ({"observed_at": None}, CHECK),
      ({**CHILD_DISCREPANCY, "child_id": None}, CHECK), ({**CHILD_DISCREPANCY, "binding_id": "pb-a1"}, CHECK), ({**CHILD_DISCREPANCY, "observed_values": DESCRIPTOR_A1_NEW}, CHECK), ({**CHILD_DISCREPANCY, "observed_at": T0 + 60_000}, CHECK),
      ({"observed_at": T0 + 59_999}, CHECK), ({"closed_at": T0 + 120_000}, CHECK), ({"closure_reason": "panel_restored"}, CHECK), ({"closed_at": T0 + 59_999, "closure_reason": "panel_restored"}, CHECK),
      ({"closed_at": T0 + 120_000, "closure_reason": "owner_resolved"}, CHECK), ({"closed_at": T0 + 120_000, "closure_reason": "superseded"}, CHECK),
      ({**CHILD_DISCREPANCY, "closed_at": T0 + 120_000, "closure_reason": "panel_restored"}, CHECK), ({**CHILD_DISCREPANCY, "closed_at": T0 + 120_000, "closure_reason": "no_longer_in_use"}, CHECK)],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_discrepancies.{col}")) for col in ("kind", "detected_at")],
]


@pytest.mark.parametrize("changes,expected", _DISCREPANCY_CASES, ids=[_case_id(changes) for changes, _ in _DISCREPANCY_CASES])
def test_discrepancy_values(main_db, changes, expected):
    _chain10(main_db, until="composite_discrepancies")
    _expect10(main_db, "composite_discrepancies", changes, expected)


def test_one_open_discrepancy_per_binding_and_child(main_db):
    _chain10(main_db, until="composite_discrepancy_descriptors")
    _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_discrepancies", "binding_id"))):
        _put10(main_db, "composite_discrepancies", discrepancy_id="dc-2")
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-3", binding_id="pb-a2")
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-c1", **CHILD_DISCREPANCY)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_discrepancies", "child_id"), ("composite_discrepancies", "kind"))):
        _put10(main_db, "composite_discrepancies", discrepancy_id="dc-c2", **CHILD_DISCREPANCY)
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-i1", **{**CHILD_DISCREPANCY, "kind": "identity"})
    _sql10(main_db, "UPDATE composite_discrepancies SET closed_at = ?, closure_reason = 'panel_restored' WHERE discrepancy_id = 'dc-1'", (T0 + 120_000,))
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-2", detected_at=T0 + 130_000, observed_at=T0 + 130_000)
    _sql10(main_db, "UPDATE composite_discrepancies SET closed_at = ?, closure_reason = 'owner_resolved' WHERE discrepancy_id = 'dc-c1'", (T0 + 120_000,))
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-c2", **CHILD_DISCREPANCY)


@pytest.mark.parametrize("column,value", [("kind", "identity"), ("binding_id", "pb-a2"), ("child_id", "ch-1"), ("detected_at", T0 + 60_001)], ids=["kind", "binding", "child", "detected"])
def test_discrepancy_evidence_identity_never_changes(main_db, column, value):
    _chain10(main_db, until="composite_discrepancy_descriptors")
    _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
    _sql10(main_db, f"UPDATE composite_discrepancies SET {column} = ? WHERE discrepancy_id = 'dc-1'", (value,), "TRG")


def test_discrepancy_evidence_is_kept(main_db):
    _chain10(main_db, until="composite_discrepancy_descriptors")
    _sql10(main_db, "UPDATE composite_discrepancies SET observed_values = ?, observed_at = ? WHERE discrepancy_id = 'dc-1'", (DESCRIPTOR_A1, T0 + 90_000))
    _sql10(main_db, "UPDATE composite_discrepancies SET closed_at = ?, closure_reason = 'panel_restored' WHERE discrepancy_id = 'dc-1'", (T0 + 120_000,))
    _sql10(main_db, "UPDATE composite_discrepancies SET closed_at = NULL, closure_reason = NULL WHERE discrepancy_id = 'dc-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_discrepancies SET observed_values = ? WHERE discrepancy_id = 'dc-1'", (DESCRIPTOR_A1_NEW,), "TRG")
    _sql10(main_db, "DELETE FROM composite_discrepancies WHERE discrepancy_id = 'dc-1'", (), "TRG")


@pytest.mark.parametrize("column", ["descriptor", "recorded_at", "discrepancy_kind"], ids=["descriptor", "recorded", "kind"])
def test_discrepancy_descriptor_required_columns(main_db, column):
    _chain10(main_db, until="composite_discrepancy_descriptors")
    _expect10(main_db, "composite_discrepancy_descriptors", {column: None}, re.escape(f"NOT NULL constraint failed: composite_discrepancy_descriptors.{column}"))


def test_discrepancy_descriptor_kind_is_checked(main_db):
    _chain10(main_db, until="composite_discrepancy_descriptors")
    _expect10(main_db, "composite_discrepancy_descriptors", {"discrepancy_kind": "repeated_divergence"}, CHECK)


def test_descriptors_belong_to_an_open_descriptor_discrepancy(main_db):
    _chain10(main_db, until="composite_divergences")
    uq = _uq10(("composite_discrepancy_descriptors", "discrepancy_id"), ("composite_discrepancy_descriptors", "descriptor"))
    with pytest.raises(sqlite3.IntegrityError, match=uq):
        _put10(main_db, "composite_discrepancy_descriptors", recorded_at=T0 + 70_000)
    _put10(main_db, "composite_discrepancy_descriptors", descriptor=DESCRIPTOR_A1_OLD)
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-c1", **CHILD_DISCREPANCY)
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        _put10(main_db, "composite_discrepancy_descriptors", discrepancy_id="dc-c1")
    _sql10(main_db, "UPDATE composite_discrepancy_descriptors SET descriptor = ? WHERE descriptor = ?", (DESCRIPTOR_A1_NEW, DESCRIPTOR_A1), "TRG")
    _sql10(main_db, "UPDATE composite_discrepancy_descriptors SET recorded_at = ? WHERE descriptor = ?", (T0 + 60_001, DESCRIPTOR_A1), "TRG")
    _sql10(main_db, "DELETE FROM composite_discrepancy_descriptors WHERE descriptor = ?", (DESCRIPTOR_A1,), "TRG")
    _sql10(main_db, "UPDATE composite_discrepancies SET closed_at = ?, closure_reason = 'no_longer_in_use' WHERE discrepancy_id = 'dc-1'", (T0 + 120_000,))
    with pytest.raises(sqlite3.IntegrityError) as error:
        _put10(main_db, "composite_discrepancy_descriptors", descriptor=DESCRIPTOR_A1_NEW, recorded_at=T0 + 130_000)
    assert "constraint failed" not in str(error.value)


_DIVERGENCE_CASES = [
    (REPAIRED, "accepted"), ({**REPAIRED, "exposure_resolved_at": T0 + 31_000}, "accepted"), ({"repair_work_id": "rw-r"}, "accepted"),
    ({"repair_state": "failed", "repair_work_id": "rw-r"}, "accepted"), ({"repair_state": "paused", "discrepancy_id": "dc-c1"}, "accepted"),
    ({"kind": "reappeared", "exposure": "access_gained"}, "accepted"), (NOT_REPAIRABLE, "accepted"),
    ({**NOT_REPAIRABLE, "kind": "identity", "observed_fields": '{"email": "cmp1-renamed"}'}, "accepted"),
    ({"exposure": "none", "exposure_from": None}, "accepted"), ({"repeat_count": 3, "discrepancy_id": "dc-c1"}, "accepted"),
    ({"exposure_from": T0 + 30_400}, "accepted"), ({"exposure_resolved_at": T0 + 30_400}, "accepted"),
    *[({"kind": "late_write"}, CHECK), ({"observed_fields": '{"enable": true}'}, CHECK), ({"repeat_count": 0}, CHECK), ({"repeat_count": 1.5}, CHECK), ({"repair_state": "done"}, CHECK),
      ({"repair_state": "repaired", "repaired_at": T0 + 31_000}, CHECK), ({"repair_work_id": "rw-r", "repair_state": "repaired"}, CHECK), ({"repaired_at": T0 + 31_000}, CHECK), ({**REPAIRED, "repaired_at": T0 + 30_399}, CHECK),
      ({"repair_state": "not_repairable", "discrepancy_id": "dc-c1"}, CHECK), ({**NOT_REPAIRABLE, "repair_state": "pending"}, CHECK), ({**NOT_REPAIRABLE, "repair_work_id": "rw-r"}, CHECK), ({**NOT_REPAIRABLE, "discrepancy_id": None}, CHECK), ({"repair_state": "paused"}, CHECK),
      ({"exposure": "leak"}, CHECK), ({"exposure": "none"}, CHECK), ({"exposure": "none", "exposure_from": None, "exposure_resolved_at": T0 + 31_000}, CHECK), ({"exposure_from": None}, CHECK), ({"exposure_from": T0 + 30_401}, CHECK), ({"exposure_resolved_at": T0 + 30_399}, CHECK)],
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_divergences.{col}")) for col in ("sweep_id", "physical_panel_id", "child_id", "kind", "observed_fields", "desired_fields", "detected_at", "repeat_count", "repair_state", "exposure")],
]


@pytest.mark.parametrize("changes,expected", _DIVERGENCE_CASES, ids=[_case_id(changes) for changes, _ in _DIVERGENCE_CASES])
def test_divergence_values(main_db, changes, expected):
    _chain10(main_db, until="composite_divergences")
    _repair_parents(main_db)
    _expect10(main_db, "composite_divergences", changes, expected)


def test_divergence_child_is_on_the_swept_panel_and_owns_its_links(main_db):
    _chain10(main_db, until="composite_divergences")
    _panel_b(main_db)
    _child2(main_db)
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-b", physical_panel_id="pp-b")
    _put10(main_db, "composite_remote_work", work_id="rw-2", child_id="ch-2")
    _put10(main_db, "composite_discrepancies", discrepancy_id="dc-c2", **{**CHILD_DISCREPANCY, "child_id": "ch-2"})
    cases = [
        ({"sweep_id": "sw-b"}, FK),
        ({"sweep_id": "sw-b", "physical_panel_id": "pp-b"}, FK),
        ({"repair_work_id": "rw-2"}, FK),
        ({"discrepancy_id": "dc-c2", "repair_state": "paused"}, FK),
        ({"discrepancy_id": "dc-1", "repair_state": "paused"}, FK),
    ]
    for changes, expected in cases:
        with pytest.raises(sqlite3.IntegrityError, match=expected):
            _put10(main_db, "composite_divergences", divergence_id="dv-2", **changes)
    _put10(main_db, "composite_divergences", divergence_id="dv-2", child_id="ch-2", repair_work_id="rw-2", discrepancy_id="dc-c2", repair_state="paused")


@pytest.mark.parametrize("column,value", [("sweep_id", "sw-2"), ("child_id", "ch-2"), ("physical_panel_id", "pp-b"), ("kind", "reappeared"), ("observed_fields", '{"enable": "unknown"}'), ("desired_fields", '{"enable": false}'), ("detected_at", T0 + 30_401), ("repeat_count", 2), ("exposure", "access_gained"), ("exposure_from", T0 + 2_000)], ids=["sweep", "child", "panel", "kind", "observed", "desired", "detected", "repeat", "exposure", "exposure-from"])
def test_divergence_evidence_never_changes(main_db, column, value):
    _chain10(main_db)
    _repair_parents(main_db)
    _child2(main_db)
    _panel_b(main_db)
    _put10(main_db, "composite_drift_sweeps", sweep_id="sw-2", started_at=T0 + 60_000)
    _sql10(main_db, f"UPDATE composite_divergences SET {column} = ? WHERE divergence_id = 'dv-1'", (value,), "TRG")


def test_divergence_repair_and_exposure_are_monotonic(main_db):
    _chain10(main_db)
    _repair_parents(main_db)
    _sql10(main_db, "UPDATE composite_divergences SET discrepancy_id = 'dc-c1', repair_state = 'paused' WHERE divergence_id = 'dv-1'")
    _sql10(main_db, "UPDATE composite_divergences SET repair_state = 'pending' WHERE divergence_id = 'dv-1'")
    _sql10(main_db, "UPDATE composite_divergences SET repair_work_id = 'rw-r' WHERE divergence_id = 'dv-1'")
    _sql10(main_db, "UPDATE composite_divergences SET repair_state = 'repaired', repaired_at = ? WHERE divergence_id = 'dv-1'", (T0 + 31_000,))
    _sql10(main_db, "UPDATE composite_divergences SET exposure_resolved_at = ? WHERE divergence_id = 'dv-1'", (T0 + 31_000,))
    _sql10(main_db, "UPDATE composite_divergences SET repair_state = 'pending', repaired_at = NULL WHERE divergence_id = 'dv-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET repair_state = 'failed' WHERE divergence_id = 'dv-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET repaired_at = ? WHERE divergence_id = 'dv-1'", (T0 + 32_000,), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET repair_work_id = NULL WHERE divergence_id = 'dv-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET exposure_resolved_at = ? WHERE divergence_id = 'dv-1'", (T0 + 32_000,), "TRG")


def test_divergences_are_kept_until_resolved(main_db):
    _chain10(main_db)
    _repair_parents(main_db)
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET repair_work_id = 'rw-r', repair_state = 'repaired', repaired_at = ? WHERE divergence_id = 'dv-1'", (T0 + 31_000,))
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-1'", (), "TRG")
    _sql10(main_db, "UPDATE composite_divergences SET exposure_resolved_at = ? WHERE divergence_id = 'dv-1'", (T0 + 31_000,))
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-1'")


def test_divergence_deletion_requires_resolved_repair_and_exposure(main_db):
    _chain10(main_db, until="composite_divergences")
    _repair_parents(main_db)
    _put10(main_db, "composite_divergences", divergence_id="dv-n", exposure="none", exposure_from=None, **REPAIRED)
    _put10(main_db, "composite_divergences", divergence_id="dv-m", exposure="none", exposure_from=None, **NOT_REPAIRABLE)
    _put10(main_db, "composite_divergences", divergence_id="dv-f", exposure="none", exposure_from=None, repair_state="failed", repair_work_id="rw-r")
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-n'")
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-m'", (), "TRG")
    _sql10(main_db, "DELETE FROM composite_divergences WHERE divergence_id = 'dv-f'", (), "TRG")


# Data-model §10 batches (T034f1: checks for T040 part b)

# One valid row per table, in parent-before-child order: a same-inbound move of sub-1, previewed and not yet authorized.
ROWS_10B = {
    "composite_batches": {"batch_id": "bt-1", "action": "move", "preview_digest": _digest(101), "actor": "web:owner-1", "reason": "new address on inbound 1", "emergency": 0, "emergency_acceptance_ref": None, "amount": None, "member_count": 1, "total_amount": None, "previewed_at": T0 + 100_000, "authorized_at": None},
    "composite_batch_members": {"member_id": "bm-1", "batch_id": "bt-1", "action": "move", "subscription_id": "sub-1", "customer_telegram_id": 50001, "subscription_context": None, "amount": None, "obligation_kind": None, "operation_id": None, "obligation_id": None, "result": "pending", "finished_at": None, "failure_reason": None},
    "composite_batch_member_nodes": {"member_id": "bm-1", "member_action": "move", "subscription_id": "sub-1", "logical_node_key": "node-a1", "target_binding_id": "pb-a1", "target_descriptor": DESCRIPTOR_A1_NEW, "owner_pick": None, "read_at": T0 + 99_000},
}
# (child table, child columns, parent table, parent columns)
EXPECTED_FKS_10B = (
    ("composite_batch_members", ("batch_id", "action"), "composite_batches", ("batch_id", "action")),
    ("composite_batch_members", ("batch_id", "amount"), "composite_batches", ("batch_id", "amount")),
    ("composite_batch_members", ("subscription_id", "customer_telegram_id"), "composite_subscriptions", ("subscription_id", "customer_telegram_id")),
    ("composite_batch_members", ("operation_id", "subscription_id", "action"), "composite_operations", ("operation_id", "subscription_id", "kind")),
    ("composite_batch_members", ("obligation_id", "customer_telegram_id", "obligation_kind", "amount"), "financial_obligations", ("obligation_id", "beneficiary_telegram_id", "kind", "amount")),
    ("composite_batch_member_nodes", ("member_id", "member_action", "subscription_id"), "composite_batch_members", ("member_id", "action", "subscription_id")),
    ("composite_batch_member_nodes", ("subscription_id", "logical_node_key"), "composite_subscription_nodes", ("subscription_id", "logical_node_key")),
    ("composite_batch_member_nodes", ("target_binding_id",), "composite_prepared_bindings", ("binding_id",)),
)
COMPENSATION = {"action": "compensation", "amount": 50, "member_count": 10, "total_amount": 500}  # 10 customers x 50 = 500
CREDIT_MEMBER = {"action": "compensation", "subscription_id": None, "amount": 50, "obligation_kind": "support_compensation"}
AUTHORIZE = "UPDATE composite_batches SET authorized_at = ? WHERE batch_id = ?"
LINK = "UPDATE composite_batch_members SET operation_id = ? WHERE member_id = ?"
LINK_CREDIT = "UPDATE composite_batch_members SET obligation_id = ? WHERE member_id = ?"
RESULT = "UPDATE composite_batch_members SET result = ?, finished_at = ?, failure_reason = ? WHERE member_id = ?"


def _put10b(conn, table, **changes):
    row = {**ROWS_10B[table], **changes}
    cols = tuple(row)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", tuple(row.values()))


def _chain10b(conn, until=None):
    assert until is None or until in ROWS_10B
    _chain10(conn, until="composite_remote_work")
    for table in ROWS_10B:
        if table == until:
            break
        _put10b(conn, table)


def _sub3(conn):
    _insert(conn, "composite_subscriptions", subscription_id="sub-3", customer_telegram_id=50002)


def _op(conn, operation_id, kind, subscription_id="sub-1"):
    _put10(conn, "composite_operations", operation_id=operation_id, business_key=f"{kind}:{operation_id}", kind=kind, subscription_id=subscription_id, **ON_SUB)


def _credit(conn, obligation_id, customer, amount=50, kind="support_compensation"):
    _put89(conn, "financial_obligations", obligation_id=obligation_id, effect_key=f"support:{obligation_id}", beneficiary_telegram_id=customer, kind=kind, amount=amount, checkout_id=None)


def _expect10b(conn, table, changes, expected):
    if expected == "accepted":
        _put10b(conn, table, **changes)
    elif expected == "TRG":
        with pytest.raises(sqlite3.IntegrityError) as error:
            _put10b(conn, table, **changes)
        assert "constraint failed" not in str(error.value)
    else:
        with pytest.raises(sqlite3.IntegrityError, match=expected):
            _put10b(conn, table, **changes)


def test_main_gets_the_batch_tables(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        tables = _tables(conn)
        for table, row in ROWS_10B.items():
            assert table in tables
            assert set(row) <= set(_columns(conn, table))


def test_batch_foreign_keys_are_restrict(two_runs):
    with closing(sqlite3.connect(two_runs.install.main)) as conn:
        found = set()
        for table in ROWS_10B:
            groups = {}
            for row in conn.execute(f"PRAGMA foreign_key_list({table})"):
                groups.setdefault(row[0], []).append(row)
            for rows in groups.values():
                rows.sort(key=lambda row: row[1])
                parent = rows[0][2]
                cols = tuple(row[4] for row in rows)
                if any(col is None for col in cols):
                    cols = tuple(row[1] for row in sorted((row for row in conn.execute(f"PRAGMA table_info({parent})") if row[5] > 0), key=lambda row: row[5]))
                found.add((table, tuple(row[3] for row in rows), parent, cols))
                assert all(row[6] == "RESTRICT" for row in rows)
        assert set(EXPECTED_FKS_10B) <= found


def test_rows_in_every_batch_table_survive_a_rerun(tmp_path):
    install = _build(tmp_path, "current")
    migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-1")), RELEASE)
    with closing(sqlite3.connect(install.main)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _chain10b(conn)
        conn.execute(AUTHORIZE, (T0 + 160_000, "bt-1"))
        conn.commit()
    before = _dump(install.main)
    report = migrations.migrate(install.paths(_fresh_dir(tmp_path, "pre-2")), RELEASE)
    assert _outcomes(report) == install.expected(migrations.SCHEMA_VERSION, migrations.SCHEMA_VERSION, "unchanged")
    assert _dump(install.main) == before
    _check_clean(install.main)
    with closing(sqlite3.connect(install.main)) as conn:
        assert all(_one(conn, f"SELECT count(*) FROM {table}")[0] == 1 for table in ROWS_10B)
        assert _one(conn, "SELECT authorized_at FROM composite_batches WHERE batch_id = 'bt-1'")[0] == T0 + 160_000


@pytest.mark.parametrize("case", ["batch", "member", "binding"], ids=["batch-used-by-member", "member-used-by-node", "binding-used-by-node"])
def test_batch_parents_cannot_be_deleted(main_db, case):
    if case == "batch":
        _chain10b(main_db, until="composite_batch_member_nodes")
        sql, parent, where = "DELETE FROM composite_batches WHERE batch_id = 'bt-1'", "composite_batches", "batch_id = 'bt-1'"
    elif case == "member":
        _chain10b(main_db)
        sql, parent, where = "DELETE FROM composite_batch_members WHERE member_id = 'bm-1'", "composite_batch_members", "member_id = 'bm-1'"
    else:
        _chain10b(main_db, until="composite_batch_member_nodes")
        _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
        _put10b(main_db, "composite_batch_member_nodes", target_binding_id="pb-a2", target_descriptor=DESCRIPTOR_A1)
        sql, parent, where = "DELETE FROM composite_prepared_bindings WHERE binding_id = 'pb-a2'", "composite_prepared_bindings", "binding_id = 'pb-a2'"
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        main_db.execute(sql)
    key = where.split(" = ")[0]
    assert _one(main_db, f"SELECT {key} FROM {parent} WHERE {where}")[0] is not None


@pytest.mark.parametrize("table,setup,changes", [
    ("composite_batch_members", "member", {"batch_id": "bt-missing"}),
    ("composite_batch_members", "credit", {"member_id": "bm-c1", "batch_id": "bt-c", **CREDIT_MEMBER, "amount": 40}),
    ("composite_batch_members", "member", {"subscription_id": "sub-missing"}),
    ("composite_batch_members", "member", {"customer_telegram_id": 50002}),
    ("composite_batch_member_nodes", "node", {"member_id": "bm-missing"}),
    ("composite_batch_member_nodes", "subnode", {"subscription_id": "sub-2"}),
    ("composite_batch_member_nodes", "node", {"logical_node_key": "node-x"}),
    ("composite_batch_member_nodes", "node", {"target_binding_id": "pb-missing"}),
], ids=["member-batch", "member-batch-amount", "member-subscription", "member-customer", "node-member", "node-subscription", "node-logical-key", "node-binding"])
def test_batch_child_row_needs_its_parent(main_db, table, setup, changes):
    if setup in ("member", "credit"):
        _chain10b(main_db, until="composite_batch_members")
    else:
        _chain10b(main_db, until="composite_batch_member_nodes")
    if setup == "credit":
        _put10b(main_db, "composite_batches", batch_id="bt-c", preview_digest=_digest(102), **COMPENSATION)
    elif setup == "subnode":
        _sub2(main_db)
        _insert(main_db, "composite_subscription_nodes", subscription_id="sub-2")
    with pytest.raises(sqlite3.IntegrityError, match=FK):
        _put10b(main_db, table, **changes)


_BATCH_VALUES = [
    ({"action": "owner_suspend"}, "accepted"), ({"action": "owner_resume"}, "accepted"), ({"action": "cancellation"}, "accepted"),
    (COMPENSATION, "accepted"), ({"emergency": 1, "emergency_acceptance_ref": "unmeasured old usage accepted"}, "accepted"), ({"member_count": 151}, "accepted"),
    ({"action": "delete"}, CHECK), ({"action": "customer_disable"}, CHECK), ({"preview_digest": _digest(101)[:31]}, CHECK),
    ({"preview_digest": _digest(101).hex()}, CHECK), ({"preview_digest": "x" * 32}, CHECK), ({"reason": ""}, CHECK),
    ({"emergency": 2}, CHECK), ({"emergency": 1}, CHECK), ({"emergency_acceptance_ref": "x"}, CHECK),
    ({"action": "owner_suspend", "emergency": 1, "emergency_acceptance_ref": "x"}, CHECK), ({"amount": 50}, CHECK),
    ({**COMPENSATION, "amount": None}, CHECK), ({**COMPENSATION, "amount": 0, "total_amount": 0}, CHECK),
    ({**COMPENSATION, "amount": -50, "total_amount": -500}, CHECK), ({**COMPENSATION, "amount": 50.5, "total_amount": 505}, CHECK),
    ({**COMPENSATION, "total_amount": 499}, CHECK), ({**COMPENSATION, "total_amount": None}, CHECK), ({"total_amount": 500}, CHECK),
    ({"member_count": 0}, CHECK), ({"member_count": 1.5}, CHECK), ({"authorized_at": T0 + 100_000}, "TRG"),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_batches.{col}")) for col in ("action", "preview_digest", "actor", "reason", "emergency", "member_count", "previewed_at")],
]


@pytest.mark.parametrize("changes,expected", _BATCH_VALUES, ids=[_case_id(changes) for changes, _ in _BATCH_VALUES])
def test_batch_column_values(main_db, changes, expected):
    _chain10b(main_db, until="composite_batches")
    _expect10b(main_db, "composite_batches", changes, expected)


@pytest.mark.parametrize("case", ["duplicate", "distinct", "fixed", "authorization"], ids=["duplicate-digest", "distinct-digest", "preview-fields-fixed", "authorization-once"])
def test_batch_preview_is_unique_and_never_changes(main_db, case):
    if case == "duplicate":
        _chain10b(main_db, until="composite_batch_members")
        with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_batches", "preview_digest"))):
            _put10b(main_db, "composite_batches", batch_id="bt-2")
    elif case == "distinct":
        _chain10b(main_db, until="composite_batch_members")
        _put10b(main_db, "composite_batches", batch_id="bt-3", preview_digest=_digest(102))
    elif case == "fixed":
        _chain10b(main_db, until="composite_batch_members")
        for col, value in [("action", "owner_suspend"), ("preview_digest", _digest(102)), ("actor", "web:owner-2"), ("reason", "other reason"), ("emergency", 1), ("emergency_acceptance_ref", "x"), ("amount", 50), ("member_count", 2), ("total_amount", 500), ("previewed_at", T0 + 100_001), ("batch_id", "bt-9")]:
            _sql10(main_db, f"UPDATE composite_batches SET {col} = ? WHERE batch_id = 'bt-1'", (value,), "TRG")
    else:
        _chain10b(main_db)
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"))
        _sql10(main_db, AUTHORIZE, (T0 + 170_000, "bt-1"), "TRG")
        _sql10(main_db, "UPDATE composite_batches SET authorized_at = NULL WHERE batch_id = 'bt-1'", (), "TRG")
        _sql10(main_db, "DELETE FROM composite_batches WHERE batch_id = 'bt-1'", (), "TRG")


@pytest.mark.parametrize("case", ["move", "suspend", "compensation"], ids=["move-needs-exact-members-and-map", "suspend-exact-members", "compensation-does-not-need-map"])
def test_authorization_needs_the_exact_previewed_members(main_db, case):
    if case == "move":
        _chain10b(main_db, until="composite_batch_members")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"), "TRG")
        _put10b(main_db, "composite_batch_members")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"), "TRG")
        _put10b(main_db, "composite_batch_member_nodes")
        _sql10(main_db, AUTHORIZE, (T0 + 99_999, "bt-1"), CHECK)
        _sql10(main_db, AUTHORIZE, (T0 + 100_000, "bt-1"))
    elif case == "suspend":
        _chain10b(main_db, until="composite_batches")
        _sub2(main_db)
        _sub3(main_db)
        _put10b(main_db, "composite_batches", batch_id="bt-s", action="owner_suspend", member_count=2, preview_digest=_digest(103))
        _put10b(main_db, "composite_batch_members", member_id="bm-s1", batch_id="bt-s", action="owner_suspend")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-s"), "TRG")
        _put10b(main_db, "composite_batch_members", member_id="bm-s2", batch_id="bt-s", action="owner_suspend", subscription_id="sub-2")
        _put10b(main_db, "composite_batch_members", member_id="bm-s3", batch_id="bt-s", action="owner_suspend", subscription_id="sub-3", customer_telegram_id=50002)
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-s"), "TRG")
        _sql10(main_db, "DELETE FROM composite_batch_members WHERE member_id = 'bm-s3'")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-s"))
    else:
        _chain10b(main_db, until="composite_batches")
        _put10b(main_db, "composite_batches", batch_id="bt-c", **{**COMPENSATION, "member_count": 2, "total_amount": 100})
        _put10b(main_db, "composite_batch_members", member_id="bm-c1", batch_id="bt-c", **CREDIT_MEMBER)
        _put10b(main_db, "composite_batch_members", member_id="bm-c2", batch_id="bt-c", **CREDIT_MEMBER, customer_telegram_id=50002)
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-c"))


@pytest.mark.parametrize("case", ["authorized", "preview"], ids=["locked-after-authorization", "discardable-preview"])
def test_members_and_mapping_are_fixed_once_authorized(main_db, case):
    _chain10b(main_db)
    if case == "authorized":
        _sub2(main_db)
        _insert(main_db, "composite_subscription_nodes", logical_node_key="node-a2")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"))
        _expect10b(main_db, "composite_batch_members", {"member_id": "bm-2", "subscription_id": "sub-2"}, "TRG")
        _expect10b(main_db, "composite_batch_member_nodes", {"logical_node_key": "node-a2"}, "TRG")
        _sql10(main_db, "UPDATE composite_batch_member_nodes SET target_descriptor = ? WHERE member_id = 'bm-1'", (DESCRIPTOR_A1,), "TRG")
        _sql10(main_db, "DELETE FROM composite_batch_member_nodes WHERE member_id = 'bm-1'", (), "TRG")
        _sql10(main_db, "DELETE FROM composite_batch_members WHERE member_id = 'bm-1'", (), "TRG")
    else:
        _insert(main_db, "composite_subscription_nodes", logical_node_key="node-a2")
        _put10b(main_db, "composite_batch_member_nodes", logical_node_key="node-a2")
        _sql10(main_db, "UPDATE composite_batch_member_nodes SET owner_pick = 'x' WHERE member_id = 'bm-1'", (), "TRG")
        _sql10(main_db, "DELETE FROM composite_batch_member_nodes WHERE member_id = 'bm-1'")
        _sql10(main_db, "DELETE FROM composite_batch_members WHERE member_id = 'bm-1'")
        _sql10(main_db, "DELETE FROM composite_batches WHERE batch_id = 'bt-1'")
        assert all(_one(main_db, f"SELECT count(*) FROM {table}")[0] == 0 for table in ROWS_10B)


_MEMBER_VALUES = [
    ({}, {}, "accepted"), ({"action": "owner_suspend"}, {"action": "owner_suspend"}, "accepted"),
    ({"action": "owner_suspend"}, {"action": "owner_suspend", "subscription_id": "sub-3", "customer_telegram_id": 50002}, "accepted"),
    (COMPENSATION, CREDIT_MEMBER, "accepted"), (COMPENSATION, {**CREDIT_MEMBER, "customer_telegram_id": 50002}, "accepted"),
    (COMPENSATION, {**CREDIT_MEMBER, "subscription_context": '["sub-1"]'}, "accepted"),
    ({}, {"subscription_id": None}, CHECK), (COMPENSATION, {**CREDIT_MEMBER, "subscription_id": "sub-1"}, CHECK),
    (COMPENSATION, {**CREDIT_MEMBER, "amount": None}, CHECK), (COMPENSATION, {**CREDIT_MEMBER, "obligation_kind": None}, CHECK),
    (COMPENSATION, {**CREDIT_MEMBER, "obligation_kind": "topup_credit"}, CHECK), ({}, {"amount": 50}, CHECK),
    ({}, {"obligation_kind": "support_compensation"}, CHECK), ({}, {"subscription_context": '["sub-1"]'}, CHECK),
    ({}, {"result": "done"}, CHECK), ({}, {"result": "succeeded", "finished_at": T0 + 200_000}, CHECK),
    ({}, {"finished_at": T0 + 200_000}, CHECK), ({}, {"failure_reason": "x"}, CHECK),
    ({}, {"action": "owner_suspend"}, FK), ({}, {"customer_telegram_id": 50002}, FK),
    ({}, {"operation_id": "op-1"}, "TRG"), (COMPENSATION, {**CREDIT_MEMBER, "obligation_id": "fo-c1"}, "TRG"),
    *[({}, {col: None}, re.escape(f"NOT NULL constraint failed: composite_batch_members.{col}")) for col in ("batch_id", "action", "customer_telegram_id", "result")],
]


@pytest.mark.parametrize("batch,changes,expected", _MEMBER_VALUES, ids=[_case_id({**batch, **changes}) for batch, changes, _ in _MEMBER_VALUES])
def test_member_column_values(main_db, batch, changes, expected):
    _chain10b(main_db, until="composite_batches")
    _sub3(main_db)
    _put10b(main_db, "composite_batches", **batch)
    _expect10b(main_db, "composite_batch_members", changes, expected)


def test_one_member_per_subscription_or_customer(main_db):
    _chain10b(main_db)
    _sub2(main_db)
    _sub3(main_db)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_batch_member_nodes", "member_id"), ("composite_batch_member_nodes", "logical_node_key"))):
        _put10b(main_db, "composite_batch_member_nodes", read_at=T0 + 99_500)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_batch_members", "batch_id"), ("composite_batch_members", "subscription_id"))):
        _put10b(main_db, "composite_batch_members", member_id="bm-2")
    _put10b(main_db, "composite_batch_members", member_id="bm-3", subscription_id="sub-2")
    _put10b(main_db, "composite_batches", batch_id="bt-2", preview_digest=_digest(102))
    _put10b(main_db, "composite_batch_members", member_id="bm-4", batch_id="bt-2")
    _put10b(main_db, "composite_batches", batch_id="bt-c", preview_digest=_digest(103), **COMPENSATION)
    _put10b(main_db, "composite_batch_members", member_id="bm-c1", batch_id="bt-c", **CREDIT_MEMBER)
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_batch_members", "batch_id"), ("composite_batch_members", "customer_telegram_id"))):
        _put10b(main_db, "composite_batch_members", member_id="bm-c2", batch_id="bt-c", **CREDIT_MEMBER)
    _put10b(main_db, "composite_batch_members", member_id="bm-c3", batch_id="bt-c", **CREDIT_MEMBER, customer_telegram_id=50002)


@pytest.mark.parametrize("case", ["matching", "shared"], ids=["authorized-effect-matches", "pending-operation-can-be-shared"])
def test_member_operation_matches_its_subscription_and_action(main_db, case):
    if case == "matching":
        _chain10b(main_db)
        _sub2(main_db)
        _op(main_db, "op-m", "move")
        _op(main_db, "op-m2", "move", "sub-2")
        _op(main_db, "op-s", "owner_suspend")
        _op(main_db, "op-m3", "move")
        _sql10(main_db, LINK, ("op-m", "bm-1"), "TRG")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"))
        for operation in ("op-missing", "op-s", "op-m2", "op-1"):
            _sql10(main_db, LINK, (operation, "bm-1"), FK)
        _sql10(main_db, LINK, ("op-m", "bm-1"))
        _sql10(main_db, LINK, ("op-m3", "bm-1"), "TRG")
        _sql10(main_db, "UPDATE composite_batch_members SET operation_id = NULL WHERE member_id = 'bm-1'", (), "TRG")
    else:
        _chain10b(main_db, until="composite_batches")
        _put10b(main_db, "composite_batches", batch_id="bt-x1", action="cancellation")
        _put10b(main_db, "composite_batches", batch_id="bt-x2", action="cancellation", preview_digest=_digest(102))
        _put10b(main_db, "composite_batch_members", member_id="bm-x1", batch_id="bt-x1", action="cancellation")
        _put10b(main_db, "composite_batch_members", member_id="bm-x2", batch_id="bt-x2", action="cancellation")
        _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-x1"))
        _sql10(main_db, AUTHORIZE, (T0 + 170_000, "bt-x2"))
        _op(main_db, "op-c", "cancellation")
        _sql10(main_db, LINK, ("op-c", "bm-x1"))
        _sql10(main_db, LINK, ("op-c", "bm-x2"))


def test_compensation_member_links_one_equal_credit(main_db):
    _chain10b(main_db, until="composite_batches")
    _put10b(main_db, "composite_batches", batch_id="bt-c", **{**COMPENSATION, "member_count": 2, "total_amount": 100})
    _put10b(main_db, "composite_batch_members", member_id="bm-c1", batch_id="bt-c", **CREDIT_MEMBER)
    _put10b(main_db, "composite_batch_members", member_id="bm-c2", batch_id="bt-c", **CREDIT_MEMBER, customer_telegram_id=50002)
    _credit(main_db, "fo-c1", 50001)
    _credit(main_db, "fo-c2", 50002)
    _credit(main_db, "fo-x", 50001, amount=60)
    _credit(main_db, "fo-t", 50001, kind="topup_credit")
    _sql10(main_db, LINK_CREDIT, ("fo-c1", "bm-c1"), "TRG")
    _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-c"))
    for obligation in ("fo-missing", "fo-x", "fo-t", "fo-c2"):
        _sql10(main_db, LINK_CREDIT, (obligation, "bm-c1"), FK)
    _sql10(main_db, LINK_CREDIT, ("fo-c1", "bm-c1"))
    with pytest.raises(sqlite3.IntegrityError, match=_uq10(("composite_batch_members", "obligation_id"))):
        main_db.execute(LINK_CREDIT, ("fo-c1", "bm-c2"))
    _sql10(main_db, LINK_CREDIT, ("fo-c2", "bm-c2"))
    _sql10(main_db, LINK_CREDIT, ("fo-c2", "bm-c1"), "TRG")
    _sql10(main_db, LINK, ("op-1", "bm-c1"), CHECK)


def test_finished_members_stay_finished(main_db):
    _chain10b(main_db)
    _op(main_db, "op-m", "move")
    _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"))
    _sql10(main_db, RESULT, ("succeeded", T0 + 400_000, None, "bm-1"), CHECK)
    _sql10(main_db, LINK, ("op-m", "bm-1"))
    _sql10(main_db, RESULT, ("succeeded", None, None, "bm-1"), CHECK)
    _sql10(main_db, RESULT, ("failed", T0 + 400_000, None, "bm-1"), CHECK)
    _sql10(main_db, RESULT, ("succeeded", T0 + 400_000, "x", "bm-1"), CHECK)
    _sql10(main_db, RESULT, ("done", T0 + 400_000, None, "bm-1"), CHECK)
    _sql10(main_db, RESULT, ("succeeded", T0 + 400_000, None, "bm-1"))
    _sql10(main_db, RESULT, ("pending", None, None, "bm-1"), "TRG")
    _sql10(main_db, RESULT, ("failed", T0 + 400_000, "late", "bm-1"), "TRG")
    _sql10(main_db, "UPDATE composite_batch_members SET finished_at = ? WHERE member_id = 'bm-1'", (T0 + 400_001,), "TRG")


def test_failed_member_stays_failed(main_db):
    _chain10b(main_db)
    _op(main_db, "op-m", "move")
    _sql10(main_db, AUTHORIZE, (T0 + 160_000, "bt-1"))
    _sql10(main_db, LINK, ("op-m", "bm-1"))
    _sql10(main_db, RESULT, ("failed", T0 + 400_000, "subscription was cancelled", "bm-1"))
    _sql10(main_db, RESULT, ("succeeded", T0 + 400_000, None, "bm-1"), "TRG")


@pytest.mark.parametrize("column,value", [("member_id", "bm-9"), ("batch_id", "bt-2"), ("action", "owner_suspend"), ("subscription_id", "sub-2"), ("customer_telegram_id", 50002), ("subscription_context", "x"), ("amount", 50), ("obligation_kind", "support_compensation")], ids=["member-id", "batch", "action", "subscription", "customer", "context", "amount", "obligation-kind"])
def test_member_identity_never_changes(main_db, column, value):
    _chain10b(main_db, until="composite_batch_member_nodes")
    _sub2(main_db)
    _put10b(main_db, "composite_batches", batch_id="bt-2", preview_digest=_digest(102))
    _sql10(main_db, f"UPDATE composite_batch_members SET {column} = ? WHERE member_id = 'bm-1'", (value,), "TRG")


_NODE_VALUES = [
    ({}, "accepted"), ({"target_binding_id": "pb-a2", "target_descriptor": DESCRIPTOR_A1}, "accepted"),
    ({"owner_pick": '{"host": "a2.example.invalid"}'}, "accepted"), ({"read_at": T0 + 100_000}, "accepted"),
    ({"read_at": T0 + 100_001}, "TRG"), ({"member_action": "owner_suspend"}, CHECK),
    ({"logical_node_key": "node-x"}, FK), ({"member_id": "bm-missing"}, FK),
    *[({col: None}, re.escape(f"NOT NULL constraint failed: composite_batch_member_nodes.{col}")) for col in ("member_id", "member_action", "subscription_id", "logical_node_key", "target_binding_id", "target_descriptor", "read_at")],
]


@pytest.mark.parametrize("changes,expected", _NODE_VALUES, ids=[_case_id(changes) for changes, _ in _NODE_VALUES])
def test_move_mapping_values(main_db, changes, expected):
    _chain10b(main_db, until="composite_batch_member_nodes")
    _insert(main_db, "composite_prepared_bindings", binding_id="pb-a2", inbound_id=2)
    _expect10b(main_db, "composite_batch_member_nodes", changes, expected)
