"""Database access for the composite tables.

Work must be a fast synchronous function doing local SQL only, never network
I/O or awaiting, because it runs inside the write transaction.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import inspect
import math
import os
import re
import sqlite3
from typing import Callable


BUSY_TIMEOUT_S = 1.0
BUSY_RETRIES = 3


@dataclass(frozen=True)
class EffectKey:
    """Name one row by a unique key column."""

    table: str
    column: str
    value: object


class RepositoryError(Exception):
    """Base class for repository failures."""


class RepositoryBusy(RepositoryError):
    """The database stayed busy through all configured attempts."""

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(f"database stayed busy after {attempts} attempts")


class IndeterminateCommit(RepositoryError):
    """A commit failed and its outcome must be checked by effect key."""

    def __init__(self, effect: EffectKey | None) -> None:
        self.effect = effect
        super().__init__("COMMIT failed; its outcome is unknown until the effect key is queried")


class PragmaMismatch(RepositoryError):
    """A required SQLite setting did not read back as configured."""

    def __init__(self, pragma: str, expected: object, actual: object) -> None:
        self.pragma = pragma
        self.expected = expected
        self.actual = actual
        super().__init__(f"PRAGMA {pragma} reads {actual!r}, expected {expected!r}")


class TransactionOwnershipError(RepositoryError):
    """Work ended the transaction owned by the repository."""

    def __init__(self) -> None:
        super().__init__("work ended the repository's transaction itself")


class Repository:
    """Run short SQLite commands on one dedicated worker connection."""

    def __init__(
        self,
        path: object,
        *,
        busy_timeout_s: int | float = BUSY_TIMEOUT_S,
        busy_retries: int = BUSY_RETRIES,
        crash: Callable[[str], object] | None = None,
        connect: Callable[..., sqlite3.Connection] | None = None,
    ) -> None:
        database = os.fspath(path)
        if not isinstance(database, str):
            raise TypeError("path must resolve to a str")
        if isinstance(busy_timeout_s, bool) or not isinstance(busy_timeout_s, (int, float)):
            raise TypeError("busy_timeout_s must be an int or float")
        if not math.isfinite(busy_timeout_s):
            raise ValueError("busy_timeout_s must be finite")
        timeout_ms = round(busy_timeout_s * 1000)
        if timeout_ms < 1:
            raise ValueError("busy_timeout_s must round to at least one millisecond")
        if isinstance(busy_retries, bool) or not isinstance(busy_retries, int):
            raise TypeError("busy_retries must be an int")
        if busy_retries < 0:
            raise ValueError("busy_retries must be >= 0")

        self._database = database
        self._busy_timeout_s = busy_timeout_s
        self._busy_timeout_ms = timeout_ms
        self._busy_retries = busy_retries
        self._crash = crash
        self._connect = connect
        self._connection: sqlite3.Connection | None = None
        self._closed = False
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="composite-repository"
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RepositoryError("repository is closed")

    def _open(self) -> sqlite3.Connection:
        self._ensure_open()
        if self._connection is not None:
            return self._connection
        connector = self._connect or sqlite3.connect
        connection = connector(
            self._database,
            isolation_level=None,
            timeout=self._busy_timeout_s,
        )
        try:
            connection.execute(f"PRAGMA busy_timeout = {self._busy_timeout_ms}")
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA synchronous = FULL")
            for name, expected in (
                ("journal_mode", "wal"),
                ("foreign_keys", 1),
                ("synchronous", 2),
                ("busy_timeout", self._busy_timeout_ms),
            ):
                actual = connection.execute(f"PRAGMA {name}").fetchone()[0]
                if actual != expected:
                    raise PragmaMismatch(name, expected, actual)
        except BaseException:
            try:
                connection.close()
            except BaseException:
                pass
            raise
        self._connection = connection
        return connection

    def _discard_connection(self) -> None:
        connection = self._connection
        if connection is None:
            return
        try:
            connection.close()
        except BaseException:
            pass
        self._connection = None

    def _rollback(self) -> None:
        connection = self._connection
        if connection is None:
            return
        try:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
        except BaseException:
            self._discard_connection()

    async def run(
        self,
        work: Callable[[sqlite3.Connection], object],
        *,
        effect: EffectKey | None = None,
    ) -> object:
        """Run one synchronous function in an explicit immediate transaction."""
        if effect is not None and not isinstance(effect, EffectKey):
            raise TypeError("effect must be an EffectKey or None")

        def command() -> object:
            self._ensure_open()
            connection = self._open()
            for attempt in range(self._busy_retries + 1):
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    break
                except sqlite3.OperationalError as exc:
                    code = getattr(exc, "sqlite_errorcode", None)
                    if code is None or (code & 0xFF) != sqlite3.SQLITE_BUSY:
                        raise
                    if attempt == self._busy_retries:
                        raise RepositoryBusy(self._busy_retries + 1) from exc

            try:
                result = work(connection)
            except BaseException:
                self._rollback()
                raise
            if inspect.isawaitable(result):
                close_result = getattr(result, "close", None)
                if callable(close_result):
                    try:
                        close_result()
                    except BaseException:
                        pass
                self._rollback()
                raise TypeError("work must be a plain function; it returned an awaitable")
            if not connection.in_transaction:
                raise TransactionOwnershipError()
            if self._crash is not None:
                try:
                    self._crash("before commit")
                except BaseException:
                    self._rollback()
                    raise
            try:
                connection.execute("COMMIT")
            except BaseException as exc:
                try:
                    connection.rollback()
                except BaseException:
                    pass
                self._discard_connection()
                raise IndeterminateCommit(effect) from exc
            if self._crash is not None:
                self._crash("after commit")
            return result

        self._ensure_open()
        return await asyncio.get_running_loop().run_in_executor(self._executor, command)

    async def query_effect(self, key: EffectKey) -> dict[str, object] | None:
        """Read a row by a validated single-column primary or unique key."""
        if not isinstance(key, EffectKey):
            raise TypeError("key must be an EffectKey")
        identifier = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
        if (
            not isinstance(key.table, str)
            or identifier.fullmatch(key.table) is None
            or not isinstance(key.column, str)
            or identifier.fullmatch(key.column) is None
        ):
            raise ValueError("table and column must be plain identifiers")

        def query() -> dict[str, object] | None:
            self._ensure_open()
            connection = self._open()
            primary = connection.execute(
                "SELECT name FROM pragma_table_info(?) WHERE pk > 0", (key.table,)
            ).fetchall()
            qualifies = len(primary) == 1 and primary[0][0] == key.column
            if not qualifies:
                indexes = connection.execute(
                    'SELECT name, "unique", partial FROM pragma_index_list(?)', (key.table,)
                ).fetchall()
                for index_name, unique, partial in indexes:
                    if unique != 1 or partial != 0:
                        continue
                    columns = connection.execute(
                        "SELECT name FROM pragma_index_info(?)", (index_name,)
                    ).fetchall()
                    if len(columns) == 1 and columns[0][0] == key.column:
                        qualifies = True
                        break
            if not qualifies:
                raise ValueError("column must be a single-column primary or unique key")
            cursor = connection.execute(
                f'SELECT * FROM "{key.table}" WHERE "{key.column}" = ?', (key.value,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(zip((description[0] for description in cursor.description), row))

        self._ensure_open()
        return await asyncio.get_running_loop().run_in_executor(self._executor, query)

    async def close(self) -> None:
        """Close the dedicated connection and stop its worker thread."""
        if self._closed:
            return
        self._closed = True

        def shutdown_connection() -> None:
            self._discard_connection()

        await asyncio.get_running_loop().run_in_executor(self._executor, shutdown_connection)
        self._executor.shutdown(wait=True)
