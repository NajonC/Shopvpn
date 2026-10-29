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

Until T035 exists, every test fails because the module is still empty.
"""

from collections import Counter
from contextlib import closing
from dataclasses import dataclass
import os
from pathlib import Path
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
