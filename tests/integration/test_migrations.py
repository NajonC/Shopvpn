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

T034a's tests pass since T035, and T034b's since T036 and T037. T034c's tests (the last section) check the data-model §5–§7 tables and fail until T038 adds them.
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
