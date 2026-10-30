"""Versioned, additive schema migrations for the composite tables.

The operator must stop every writer of the set before calling ``migrate``. FSM
files are copied but never changed, and each database member changes in its own
explicit transaction.
"""

from dataclasses import dataclass
import os
import sqlite3
import time
from typing import Callable
import urllib.parse

from composite.repository import BUSY_TIMEOUT_S


SCHEMA_VERSION = 1
KIND_TABLES = ("products", "test_config_plans", "orders")


@dataclass(frozen=True)
class AuthorizedPaths:
    """Paths the operator authorizes for one installation upgrade."""

    main: object
    tenants: tuple
    fsm: tuple
    pre_upgrade_dir: object
    base_dir: object


@dataclass(frozen=True)
class SchemaInfo:
    """The highest composite schema version found in a database."""

    version: int
    supported: bool


@dataclass(frozen=True)
class MemberOutcome:
    """The migration result for one database member."""

    path: str
    role: str
    tenant_id: int | None
    from_version: int
    to_version: int
    status: str


@dataclass(frozen=True)
class MigrationReport:
    """Ordered outcomes for the main and reseller databases."""

    outcomes: tuple[MemberOutcome, ...]


class MigrationError(Exception):
    """Base error for refused or unsuccessful migrations."""


class RegistryError(MigrationError):
    """The main database registry does not match authorized tenant files."""


class UnsupportedSchema(MigrationError):
    """A database uses a schema version newer than this release supports."""

    def __init__(self, path: str, version: int) -> None:
        self.path = path
        self.version = version
        super().__init__(f"{path} has composite schema version {version}; this release supports up to {SCHEMA_VERSION}")


class MigrationFailed(MigrationError):
    """A member failed before the complete installation was migrated."""

    def __init__(self, report: MigrationReport) -> None:
        self.report = report
        super().__init__("migration stopped before every member was migrated; issuance stays disabled")


def _read_version(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'composite_schema_versions'"
    ).fetchone()
    if row is None:
        return 0
    return int(conn.execute("SELECT COALESCE(MAX(version), 0) FROM composite_schema_versions").fetchone()[0])


def _readonly_connect(path: str) -> sqlite3.Connection:
    uri = "file:" + urllib.parse.quote(os.path.realpath(path)) + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def inspect_schema(path: str) -> SchemaInfo:
    """Read a database's composite schema version without creating the file."""
    conn = _readonly_connect(path)
    try:
        version = _read_version(conn)
        return SchemaInfo(version, version <= SCHEMA_VERSION)
    finally:
        conn.close()


def issuance_enabled(main_path: str) -> bool:
    """Report whether composite issuance is enabled; always ``False`` for now.

    Nothing can enable issuance yet: its switch belongs to the processing-control
    record a later schema step adds, and ``migrate`` never sets it.
    """
    return False


def _main_v1(conn: sqlite3.Connection) -> None:
    for table in KIND_TABLES:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN service_kind TEXT NOT NULL DEFAULT 'legacy' "
            "CHECK (service_kind IN ('legacy', 'composite'))"
        )
        conn.execute(f"ALTER TABLE {table} ADD COLUMN composite_ref TEXT")
        conn.execute(f"CREATE UNIQUE INDEX idx_{table}_composite_ref ON {table} (composite_ref)")


def _reseller_v1(conn: sqlite3.Connection) -> None:
    for table in KIND_TABLES:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN service_kind TEXT NOT NULL DEFAULT 'legacy' "
            "CHECK (service_kind = 'legacy')"
        )


_STEPS: dict[int, tuple[Callable[[sqlite3.Connection], None], Callable[[sqlite3.Connection], None]]] = {
    1: (_main_v1, _reseller_v1),
}


def migrate(paths: AuthorizedPaths, expected_release: str, *, crash=None) -> MigrationReport:
    """Back up and migrate every authorized database member in order."""
    if not isinstance(expected_release, str) or expected_release == "":
        raise ValueError("expected_release must be a non-empty str")

    pre = os.path.realpath(paths.pre_upgrade_dir)
    if not os.path.isdir(pre) or os.listdir(pre) != []:
        raise MigrationError("pre-upgrade directory must exist and be empty")

    main = os.path.realpath(paths.main)
    if not os.path.isfile(main):
        raise MigrationError(f"main database is not a regular file: {main}")

    conn = _readonly_connect(main)
    try:
        try:
            rows = conn.execute("SELECT id, db_path FROM reseller_bots ORDER BY id").fetchall()
        except sqlite3.OperationalError as exc:
            raise RegistryError("main database has no reseller_bots registry") from exc
    finally:
        conn.close()

    authorized = {os.path.realpath(t) for t in paths.tenants}
    seen: set[str] = set()
    tenant_members: list[tuple[int, str]] = []
    for tenant_id, db_path in rows:
        if not isinstance(db_path, str):
            raise RegistryError(f"reseller {tenant_id} db_path is not a string")
        candidate = db_path if os.path.isabs(db_path) else os.path.join(os.fspath(paths.base_dir), db_path)
        tenant_path = os.path.realpath(candidate)
        if (
            tenant_path in seen
            or tenant_path == main
            or not os.path.isfile(tenant_path)
            or tenant_path not in authorized
        ):
            raise RegistryError(f"invalid or unauthorized reseller database for tenant {tenant_id}")
        seen.add(tenant_path)
        tenant_members.append((tenant_id, tenant_path))
    if authorized != seen:
        raise RegistryError("authorized tenant files do not match reseller registry")

    fsm_files: list[str] = []
    seen_fsm: set[str] = set()
    for fsm_path in paths.fsm:
        real_fsm = os.path.realpath(fsm_path)
        if not os.path.isfile(real_fsm) or real_fsm in seen_fsm or real_fsm == main or real_fsm in seen:
            raise MigrationError(f"invalid FSM database file: {real_fsm}")
        seen_fsm.add(real_fsm)
        fsm_files.append(real_fsm)

    members: list[tuple[str, str, int | None, int]] = []
    for path, role, tenant_id in [(main, "main", None)] + [
        (path, "reseller", tenant_id) for tenant_id, path in tenant_members
    ]:
        info = inspect_schema(path)
        if not info.supported:
            raise UnsupportedSchema(path, info.version)
        members.append((path, role, tenant_id, info.version))

    copies = [(main, f"main-{os.path.basename(main)}")]
    copies.extend((path, f"reseller-{tenant_id}-{os.path.basename(path)}") for tenant_id, path in tenant_members)
    copies.extend((path, f"fsm-{i}-{os.path.basename(path)}") for i, path in enumerate(fsm_files, 1))
    for source_path, name in copies:
        src = dst = None
        try:
            src = _readonly_connect(source_path)
            dst = sqlite3.connect(os.path.join(pre, name))
            src.backup(dst)
        except Exception as exc:
            raise MigrationError(f"pre-upgrade copy of {source_path} failed") from exc
        finally:
            if dst is not None:
                dst.close()
            if src is not None:
                src.close()

    outcomes: list[MemberOutcome] = []
    for index, (path, role, tenant_id, from_version) in enumerate(members):
        if from_version == SCHEMA_VERSION:
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, from_version, "unchanged"))
            continue
        conn = None
        commit_started = False
        status = "failed"
        try:
            conn = sqlite3.connect(path, isolation_level=None, timeout=BUSY_TIMEOUT_S)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA synchronous = FULL")
            conn.execute("BEGIN IMMEDIATE")
            if _read_version(conn) != from_version:
                raise MigrationError(f"composite schema version of {path} changed during the run")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS composite_schema_versions "
                "(version INTEGER PRIMARY KEY, release TEXT NOT NULL, applied_at INTEGER NOT NULL)"
            )
            for version in range(from_version + 1, SCHEMA_VERSION + 1):
                step = _STEPS[version][0 if role == "main" else 1]
                step(conn)
                conn.execute(
                    "INSERT INTO composite_schema_versions (version, release, applied_at) VALUES (?, ?, ?)",
                    (version, expected_release, time.time_ns() // 1_000_000),
                )
            if crash is not None:
                crash("before commit")
            commit_started = True
            conn.execute("COMMIT")
            status = "migrated"
            if crash is not None:
                crash("after commit")
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, SCHEMA_VERSION, status))
        except BaseException as exc:
            if conn is not None and conn.in_transaction:
                try:
                    conn.execute("ROLLBACK")
                except Exception:
                    pass
            if conn is not None:
                conn.close()
                conn = None
            if not isinstance(exc, Exception):
                raise
            if commit_started and status != "migrated":
                # COMMIT itself raised: read the outcome back, never commit again.
                try:
                    committed = inspect_schema(path).version == SCHEMA_VERSION
                except Exception:
                    committed = False
                status = "migrated" if committed else "failed"
            to_version = SCHEMA_VERSION if status == "migrated" else from_version
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, to_version, status))
            outcomes.extend(
                MemberOutcome(later_path, later_role, later_id, later_version, later_version, "not_attempted")
                for later_path, later_role, later_id, later_version in members[index + 1:]
            )
            raise MigrationFailed(MigrationReport(tuple(outcomes))) from exc
        finally:
            if conn is not None:
                conn.close()
    return MigrationReport(tuple(outcomes))
