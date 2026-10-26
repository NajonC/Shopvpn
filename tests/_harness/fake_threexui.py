"""A controlled standalone 3x-UI v3.9.0 panel: substitute, not evidence.

The implementation is intentionally limited to the routes and data used by
the composite tests. Basis for its behavior:

* Lab (RX-MAN-001/GA-MAN-002 runtime): a missing client traffic lookup returns
  a successful null object; Xray status reports uptime in seconds; disabling
  an enabled client and deleting a client can restart Xray; resetting settings
  restores the panel defaults. Resets, traffic updates, database restores and
  periodic resets can lower stored traffic, while restarts do not lower it;
  disabled clients continue to count traffic. Resetting a disabled client
  zeroed both directions and re-enabled it; restoring a database lowered
  totals by post-backup traffic; a per-client periodic reset left inbound
  totals cumulative; and recreating a deleted email started at zero.
* Source (v3.9.0 source reading): API route authentication and token scopes,
  the JSON response envelope, client create/update validation and defaults,
  traffic view fields, the restart-on-disable setting, and the Xray traffic
  collector: ``QueryStats`` uses ``Reset_: false``, its first stats pass only
  establishes a baseline, lower counters count from zero, and
  ``cadenceXrayTraffic = "@every 5s"``. Panel and service restarts had measured
  losses of 9.0–13.1 seconds because there is no stop-time flush and collection
  waits for a new baseline; Xray-only restarts lost 1.2–4.6 seconds because
  the collector's previous values survive.
* Fake choice: the inbound JSON projection, the three exposed setting values,
  default values for unprovided update fields, and the limited server status
  object. Served bytes have no protocol overhead, unknown/deleted emails are
  ignored, and a missing last counter value counts from zero. Periodic reset is
  triggered manually; restarts happen instantly, so panel/service restart
  loss is at most ten seconds in this model. These views omit fields and
  behavior outside this test model.
* Lab (RX-MAN-001/V-RX-01): writes to one inbound queue in send order and wait
  on a held database; holds near ten seconds allow writes at release, while
  longer holds fail with ``database is locked``; usage collection also waits;
  writes survive caller cancellation and panel/service restarts; held responses
  do not stop writes; and API outage refuses requests immediately.
* Source (v3.9.0 source reading): ``lockInbound`` queues writes per inbound
  without a timeout, and ``Update`` looks up the client before changing it.
* Fake choice: the database-lock threshold is exactly 10,300 ms (the lab saw
  10.3–10.5 s); collector deltas older than that threshold are lost during a
  hold (the lab lost about 39 s per 60 s hold); and API outage is instantaneous.
  A write whose client is already gone still waits for a held database before
  failing, while the real lookup before the lock would fail at once.

Any recognized real route or behavior outside this model raises
``FakeNotModelled`` instead of returning an invented success.
"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import dataclass
import re
import secrets
import uuid

from tests._harness.clock import FakeClock
from tests._harness.fixtures import CompositeFixture, Inbound


EVIDENCE_LABEL = "substitute, not evidence"
COLLECTOR_INTERVAL_MS = 5_000
DB_LOCKED_AFTER_MS = 10_300


class FakeNotModelled(Exception):
    """The fake does not model this real-panel behaviour."""


@dataclass(frozen=True)
class FakeResponse:
    status: int
    body: dict | None


@dataclass(frozen=True)
class RecordedCall:
    method: str
    path: str
    scope: str | None


@dataclass(frozen=True)
class PanelSnapshot:
    """Opaque deep copy of a panel database; only ``restore()`` reads it."""

    _inbounds: dict
    _traffic: dict
    _next_traffic_id: int
    _settings: dict


class _RequestFailure(Exception):
    """A modeled API failure represented by the panel's JSON envelope."""


@dataclass(eq=False)
class _PendingWrite:
    sequence: int
    route: str
    params: tuple
    query: dict
    body: object
    inbound_ids: frozenset[int]
    future: asyncio.Future
    started_ms: int | None = None
    finished: bool = False
    caller_waiting: bool = True


@dataclass(eq=False)
class _DatabaseWaiter:
    sequence: int
    started_ms: int
    deadline_ms: int
    write: _PendingWrite | None = None
    deltas: tuple[tuple[str, int, int], ...] = ()


_STRING_FIELDS = (
    "id",
    "security",
    "password",
    "flow",
    "email",
    "subId",
    "comment",
)
_INTEGER_FIELDS = ("limitIp", "totalGB", "expiryTime", "tgId", "reset")
_CLIENT_DEFAULTS = {
    **{name: "" for name in _STRING_FIELDS},
    **{name: 0 for name in _INTEGER_FIELDS},
    "enable": False,
}
_OMIT_EMPTY = ("id", "password", "flow")

_MODELLED_ROUTES = (
    ("GET", re.compile(r"^/panel/api/inbounds/list$"), "inbounds_list"),
    ("GET", re.compile(r"^/panel/api/inbounds/get/([0-9]+)$"), "inbound_get"),
    ("POST", re.compile(r"^/panel/api/clients/add$"), "clients_add"),
    ("POST", re.compile(r"^/panel/api/clients/update/([^/]+)$"), "clients_update"),
    ("POST", re.compile(r"^/panel/api/clients/del/([^/]+)$"), "clients_del"),
    ("GET", re.compile(r"^/panel/api/clients/traffic/([^/]+)$"), "clients_traffic"),
    ("POST", re.compile(r"^/panel/api/clients/resetTraffic/([^/]+)$"), "clients_reset_traffic"),
    ("POST", re.compile(r"^/panel/api/clients/updateTraffic/([^/]+)$"), "clients_update_traffic"),
    ("POST", re.compile(r"^/panel/api/setting/all$"), "setting_all"),
    ("GET", re.compile(r"^/panel/api/server/status$"), "server_status"),
)

_UNMODELLED_ROUTES = (
    ("GET", "/panel/api/clients/list"),
    ("GET", "/panel/api/clients/list/paged"),
    ("GET", "/panel/api/clients/get/([^/]+)"),
    ("GET", "/panel/api/clients/get/tgId/([^/]+)"),
    ("GET", "/panel/api/clients/subLinks/([^/]+)"),
    ("GET", "/panel/api/clients/links/([^/]+)"),
    ("GET", "/panel/api/clients/export"),
    ("POST", "/panel/api/clients/happLink/([^/]+)"),
    ("POST", "/panel/api/clients/renewalPreview"),
    ("POST", "/panel/api/clients/([^/]+)/(attach|detach|externalLinks)"),
    ("POST", "/panel/api/clients/import"),
    ("POST", "/panel/api/clients/delOrphans"),
    ("POST", "/panel/api/clients/resetAllTraffics"),
    ("POST", "/panel/api/clients/delDepleted"),
    ("POST", "/panel/api/clients/bulkAdjust"),
    ("POST", "/panel/api/clients/bulkEnable"),
    ("POST", "/panel/api/clients/bulkDisable"),
    ("POST", "/panel/api/clients/bulkDel"),
    ("POST", "/panel/api/clients/bulkCreate"),
    ("POST", "/panel/api/clients/bulkAttach"),
    ("POST", "/panel/api/clients/bulkDetach"),
    ("POST", "/panel/api/clients/bulkResetTraffic"),
    ("POST", "/panel/api/clients/ips/([^/]+)"),
    ("POST", "/panel/api/clients/clearIps/([^/]+)"),
    ("POST", "/panel/api/clients/hwids/([^/]+)"),
    ("POST", "/panel/api/clients/onlines"),
    ("POST", "/panel/api/clients/onlinesByGuid"),
    ("POST", "/panel/api/clients/clientIpsByGuid"),
    ("POST", "/panel/api/clients/activeInbounds"),
    ("POST", "/panel/api/clients/lastOnline"),
    ("POST", "/panel/api/setting/defaultSettings"),
    ("POST", "/panel/api/setting/factoryDefaults"),
    ("POST", "/panel/api/setting/update"),
    ("POST", "/panel/api/setting/validateRegex"),
    ("POST", "/panel/api/setting/updateUser"),
    ("POST", "/panel/api/setting/restartPanel"),
    ("POST", "/panel/api/setting/apiTokens/create"),
    ("POST", "/panel/api/setting/apiTokens/delete/([^/]+)"),
    ("POST", "/panel/api/setting/apiTokens/setEnabled/([^/]+)"),
    ("GET", "/panel/api/setting/getDefaultJsonConfig"),
    ("GET", "/panel/api/setting/apiTokens"),
)

_UNMODELLED_PATTERNS = tuple(
    (method, re.compile(rf"^{pattern}$")) for method, pattern in _UNMODELLED_ROUTES
)


class FakeThreeXUIPanel:
    """In-memory model of the selected fixture panel."""

    def __init__(
        self, fixture: CompositeFixture, panel_key: str, clock: FakeClock
    ) -> None:
        self._fixture = fixture
        self._panel_key = panel_key
        self._clock = clock
        self._inbounds: dict[int, dict] = {
            inbound.inbound_id: {
                "source": inbound,
                "clients": [],
                "up": 0,
                "down": 0,
            }
            for inbound in fixture.inbounds
            if inbound.panel_key == panel_key
        }
        self._tokens = {
            "admin": fixture.panel(panel_key).api_token,
            "node-sync": secrets.token_urlsafe(32),
            "monitor": secrets.token_urlsafe(32),
        }
        self._calls: list[RecordedCall] = []
        self._traffic: dict[str, dict] = {}
        self._counters: dict[str, tuple[int, int]] = {}
        self._last_values: dict[str, tuple[int, int]] = {}
        self._next_traffic_id = 1
        self._settings = self._default_settings()
        self._xray_started_ms = clock.true_now_ms()
        self._xray_restarts: list[int] = []
        self._collector_started_ms = clock.true_now_ms()
        self._next_tick_ms = self._collector_started_ms + COLLECTOR_INTERVAL_MS
        self._baseline_pending = True
        self._database_held = False
        self._stalled_inbounds: set[int] = set()
        self._pending_write_list: list[_PendingWrite] = []
        self._database_waiters: list[_DatabaseWaiter] = []
        self._held_responses: list[tuple[asyncio.Future, FakeResponse]] = []
        self._responses_held = False
        self._api_is_down = False
        self._dispatch_sequence = 0
        self._waiter_sequence = 0
        self._processing_time_ms: int | None = None
        self._running_due = False
        self._starting_writes = False
        self._releasing_database = False

    def __repr__(self) -> str:
        return (
            f"FakeThreeXUIPanel(panel_key={self._panel_key!r}, "
            f"inbound_ids={list(self._inbounds)!r})"
        )

    @property
    def tokens(self) -> dict[str, str]:
        return self._tokens.copy()

    @property
    def calls(self) -> list[RecordedCall]:
        return self._calls.copy()

    @property
    def xray_restarts(self) -> tuple[int, ...]:
        return tuple(self._xray_restarts)

    @property
    def pending_writes(self) -> int:
        return len(self._pending_write_list)

    def serve(self, email: str, *, up: int = 0, down: int = 0) -> None:
        """Add panel-counted bytes to a client's cumulative Xray counters."""
        self.collect_due()
        for name, value in (("up", up), ("down", down)):
            if type(value) is not int:
                raise TypeError(f"{name} must be an int, got {type(value).__name__}")
            if value < 0:
                raise ValueError(f"{name} must be >= 0")
        if email not in self._counters:
            return
        current_up, current_down = self._counters[email]
        self._counters[email] = (current_up + up, current_down + down)

    def run_due(self) -> None:
        """Process collector ticks and database-lock deadlines due by true time."""
        errors = self._run_due_internal()
        if errors:
            raise errors[0]

    collect_due = run_due

    def _event_now_ms(self) -> int:
        if self._processing_time_ms is not None:
            return self._processing_time_ms
        return self._clock.true_now_ms()

    def _run_due_internal(self) -> list[FakeNotModelled]:
        if self._running_due:
            return []

        self._running_due = True
        errors: list[FakeNotModelled] = []
        now = self._clock.true_now_ms()
        try:
            while True:
                due_waiters = [
                    waiter
                    for waiter in self._database_waiters
                    if waiter.deadline_ms <= now
                ]
                deadline = min(
                    (waiter.deadline_ms for waiter in due_waiters), default=None
                )
                tick = self._next_tick_ms if self._next_tick_ms <= now else None

                # Deadlines sort before ticks at the same true-time millisecond.
                if deadline is not None and (tick is None or deadline <= tick):
                    self._processing_time_ms = deadline
                    due = min(
                        (w for w in due_waiters if w.deadline_ms == deadline),
                        key=lambda w: w.sequence,
                    )
                    self._database_waiters.remove(due)
                    if due.write is not None:
                        self._finish_write(
                            due.write,
                            response=self._failure("database is locked"),
                            errors=errors,
                            kick=False,
                        )
                        self._start_available_writes(errors)
                    # Collector deltas that reach their deadline are discarded.
                    continue

                if tick is None:
                    break

                self._processing_time_ms = tick
                self._collect_tick(tick)
                self._next_tick_ms += COLLECTOR_INTERVAL_MS

            self._processing_time_ms = None
            self._start_available_writes(errors)
        finally:
            self._processing_time_ms = None
            self._running_due = False
        return errors

    def _collect_tick(self, tick_ms: int) -> None:
        if self._baseline_pending:
            self._last_values = dict(self._counters)
            self._baseline_pending = False
            return

        deltas = []
        for email, (current_up, current_down) in self._counters.items():
            record = self._traffic.get(email)
            if record is None:
                continue

            last = self._last_values.get(email)
            last_up, last_down = last if last is not None else (None, None)
            delta_up = (
                current_up
                if last_up is None or current_up < last_up
                else current_up - last_up
            )
            delta_down = (
                current_down
                if last_down is None or current_down < last_down
                else current_down - last_down
            )
            if delta_up or delta_down:
                deltas.append((email, delta_up, delta_down))
            self._last_values[email] = (current_up, current_down)

        if self._database_held:
            self._waiter_sequence += 1
            self._database_waiters.append(
                _DatabaseWaiter(
                    sequence=self._waiter_sequence,
                    started_ms=tick_ms,
                    deadline_ms=tick_ms + DB_LOCKED_AFTER_MS,
                    deltas=tuple(deltas),
                )
            )
        else:
            self._apply_collector_deltas(deltas)

    def _apply_collector_deltas(
        self, deltas: tuple[tuple[str, int, int], ...] | list[tuple[str, int, int]]
    ) -> None:
        for email, delta_up, delta_down in deltas:
            record = self._traffic.get(email)
            if record is None:
                continue
            record["up"] += delta_up
            record["down"] += delta_down
            inbound = self._inbounds.get(record["inboundId"])
            if inbound is not None:
                inbound["up"] += delta_up
                inbound["down"] += delta_down

    def hold_database(self) -> None:
        self.run_due()
        if self._database_held:
            raise RuntimeError("database is already held")
        self._database_held = True

    def release_database(self) -> None:
        errors = self._run_due_internal()
        if not self._database_held:
            raise RuntimeError("database is not held")

        self._database_held = False
        now = self._clock.true_now_ms()
        self._processing_time_ms = now
        waiters = sorted(self._database_waiters, key=lambda waiter: waiter.sequence)
        self._database_waiters = []
        self._releasing_database = True
        try:
            for waiter in waiters:
                if waiter.deadline_ms <= now:
                    continue
                if waiter.write is not None:
                    self._execute_write(waiter.write, errors, kick=False)
                else:
                    self._apply_collector_deltas(waiter.deltas)
        finally:
            self._releasing_database = False
            self._processing_time_ms = None

        self._start_available_writes(errors)
        if errors:
            raise errors[0]

    def stall_inbound(self, inbound_id: int) -> None:
        self.run_due()
        if inbound_id not in self._inbounds:
            raise KeyError(inbound_id)
        if inbound_id in self._stalled_inbounds:
            raise RuntimeError(f"inbound {inbound_id} is already stalled")
        self._stalled_inbounds.add(inbound_id)

    def release_inbound(self, inbound_id: int) -> None:
        errors = self._run_due_internal()
        if inbound_id not in self._inbounds:
            raise KeyError(inbound_id)
        if inbound_id not in self._stalled_inbounds:
            raise RuntimeError(f"inbound {inbound_id} is not stalled")
        self._stalled_inbounds.remove(inbound_id)
        self._start_available_writes(errors)
        if errors:
            raise errors[0]

    def hold_responses(self) -> None:
        self.run_due()
        if self._responses_held:
            raise RuntimeError("responses are already held")
        self._responses_held = True

    def release_responses(self) -> None:
        errors = self._run_due_internal()
        if not self._responses_held:
            raise RuntimeError("responses are not held")
        self._responses_held = False
        held, self._held_responses = self._held_responses, []
        for future, response in held:
            if not future.done():
                future.set_result(response)
        if errors:
            raise errors[0]

    def api_down(self) -> None:
        self.run_due()
        self._api_is_down = True

    def api_up(self) -> None:
        self.run_due()
        self._api_is_down = False

    def _publish_answer(
        self, future: asyncio.Future, response: FakeResponse
    ) -> None:
        if self._responses_held:
            self._held_responses.append((future, response))
        elif not future.done():
            future.set_result(response)

    def _dispatch_inbounds(self, route: str, params: tuple, body: object) -> frozenset[int]:
        if route == "clients_add":
            if not isinstance(body, dict):
                return frozenset()
            inbound_ids = body.get("inboundIds")
            if not isinstance(inbound_ids, list):
                return frozenset()
            return frozenset(
                inbound_id
                for inbound_id in inbound_ids
                if type(inbound_id) is int and inbound_id in self._inbounds
            )

        email = params[0]
        if route in {"clients_update", "clients_del", "clients_reset_traffic"}:
            return frozenset(inbound_id for inbound_id, _, _ in self._find_clients(email))
        if route == "clients_update_traffic":
            record = self._traffic.get(email)
            if record is not None:
                return frozenset({record["inboundId"]})
        return frozenset()

    def _write_is_startable(self, candidate: _PendingWrite) -> bool:
        inbound_ids = candidate.inbound_ids
        if inbound_ids & self._stalled_inbounds:
            return False
        for write in self._pending_write_list:
            if write is candidate:
                continue
            if write.finished:
                continue
            if write.started_ms is not None and inbound_ids & write.inbound_ids:
                return False
            if (
                write.started_ms is None
                and write.sequence < candidate.sequence
                and inbound_ids & write.inbound_ids
            ):
                return False
        return True

    def _start_available_writes(self, errors: list[FakeNotModelled]) -> None:
        if self._starting_writes or self._releasing_database:
            return
        self._starting_writes = True
        try:
            while True:
                candidate = next(
                    (
                        write
                        for write in self._pending_write_list
                        if not write.finished
                        and write.started_ms is None
                        and self._write_is_startable(write)
                    ),
                    None,
                )
                if candidate is None:
                    break
                candidate.started_ms = self._event_now_ms()
                if self._database_held:
                    self._waiter_sequence += 1
                    self._database_waiters.append(
                        _DatabaseWaiter(
                            sequence=self._waiter_sequence,
                            started_ms=candidate.started_ms,
                            deadline_ms=candidate.started_ms + DB_LOCKED_AFTER_MS,
                            write=candidate,
                        )
                    )
                else:
                    self._execute_write(candidate, errors, kick=False)
        finally:
            self._starting_writes = False

    def _execute_write(
        self, write: _PendingWrite, errors: list[FakeNotModelled], *, kick: bool
    ) -> None:
        try:
            obj = self._run_route(write.route, write.params, write.query, write.body)
        except _RequestFailure as exc:
            self._finish_write(
                write, response=self._failure(str(exc)), errors=errors, kick=kick
            )
        except FakeNotModelled as exc:
            self._finish_write(write, error=exc, errors=errors, kick=kick)
        else:
            self._finish_write(
                write, response=self._success(obj), errors=errors, kick=kick
            )

    def _finish_write(
        self,
        write: _PendingWrite,
        *,
        response: FakeResponse | None = None,
        error: FakeNotModelled | None = None,
        errors: list[FakeNotModelled],
        kick: bool,
    ) -> None:
        if write.finished:
            return
        write.finished = True
        if write in self._pending_write_list:
            self._pending_write_list.remove(write)
        if error is not None:
            if write.caller_waiting:
                if not write.future.done():
                    write.future.set_exception(error)
            else:
                errors.append(error)
        elif response is not None:
            self._publish_answer(write.future, response)
        if kick and not self._releasing_database:
            self._start_available_writes(errors)

    def restart(self, mode: str) -> None:
        """Restart Xray, the panel, or both while preserving stored totals."""
        self.collect_due()
        if mode not in {"xray", "panel", "service"}:
            raise ValueError(f"unknown restart mode: {mode}")

        now = self._clock.true_now_ms()
        if mode in {"xray", "service"}:
            self._counters = {email: (0, 0) for email in self._counters}
            self._xray_restarts.append(now)
            self._xray_started_ms = now
        if mode in {"panel", "service"}:
            self._database_waiters = [
                waiter for waiter in self._database_waiters if waiter.write is not None
            ]
            self._last_values.clear()
            self._collector_started_ms = now
            self._next_tick_ms = now + COLLECTOR_INTERVAL_MS
            self._baseline_pending = True

    def periodic_reset(self, email: str) -> None:
        """Manually apply a configured per-client traffic reset."""
        self.collect_due()
        record = self._traffic.get(email)
        if record is None:
            raise KeyError(email)
        record["up"] = 0
        record["down"] = 0

    def snapshot(self) -> PanelSnapshot:
        """Return a deep copy of the panel's database state."""
        self.collect_due()
        return PanelSnapshot(
            _inbounds=deepcopy(self._inbounds),
            _traffic=deepcopy(self._traffic),
            _next_traffic_id=self._next_traffic_id,
            _settings=deepcopy(self._settings),
        )

    def restore(self, snapshot: PanelSnapshot) -> None:
        """Replace the panel database with a snapshot and restart the service."""
        self.collect_due()
        if self.pending_writes:
            raise FakeNotModelled("restoring while client writes are pending")
        self._inbounds = deepcopy(snapshot._inbounds)
        self._traffic = deepcopy(snapshot._traffic)
        self._next_traffic_id = snapshot._next_traffic_id
        self._settings = deepcopy(snapshot._settings)
        self._counters = {
            client["email"]: (0, 0)
            for _, _, client in self._all_clients()
        }
        self.restart("service")

    def traffic(self, email: str) -> dict | None:
        """Return a copy of one stored traffic record, or ``None``."""
        self.collect_due()
        record = self._traffic.get(email)
        return deepcopy(record) if record is not None else None

    async def handle(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        query: dict[str, str] | None = None,
        body: object = None,
    ) -> FakeResponse:
        """Authenticate and handle one API call using controlled virtual stalls."""
        if self._api_is_down:
            raise ConnectionRefusedError("fake 3x-UI API is down")
        self.collect_due()
        route, params = self._resolve_route(method, path)
        if not path.startswith("/panel/api/") or route is None:
            self._record(method, path, None)
            return await self._answer(FakeResponse(404, None))

        if token is None:
            self._record(method, path, None)
            return await self._answer(FakeResponse(404, None))
        scope = next((name for name, value in self._tokens.items() if token == value), None)
        if scope is None:
            self._record(method, path, None)
            return await self._answer(FakeResponse(401, None))

        self._record(method, path, scope)
        if not self._scope_permits(scope, method, path, route):
            return await self._answer(FakeResponse(
                403,
                {
                    "success": False,
                    "msg": "this API token is not permitted to access this endpoint",
                },
            ))
        if route in {
            "clients_get",
            "clients_get_by_tgid",
            "clients_attach",
            "clients_detach",
            "clients_external_links",
        }:
            raise FakeNotModelled(f"{method} {path}")
        if route == "unmodelled":
            raise FakeNotModelled(f"{method} {path}")

        if route in {
            "clients_add",
            "clients_update",
            "clients_del",
            "clients_reset_traffic",
            "clients_update_traffic",
        }:
            loop = asyncio.get_running_loop()
            self._dispatch_sequence += 1
            write = _PendingWrite(
                sequence=self._dispatch_sequence,
                route=route,
                params=params,
                query=(query or {}).copy(),
                body=deepcopy(body),
                inbound_ids=self._dispatch_inbounds(route, params, body),
                future=loop.create_future(),
            )
            self._pending_write_list.append(write)
            errors: list[FakeNotModelled] = []
            self._start_available_writes(errors)
            if errors:
                write.caller_waiting = False
                raise errors[0]
            try:
                return await asyncio.shield(write.future)
            except asyncio.CancelledError:
                write.caller_waiting = False
                raise
            finally:
                if write.future.done():
                    write.caller_waiting = False

        try:
            obj = self._run_route(route, params, query or {}, body)
        except _RequestFailure as exc:
            return await self._answer(self._failure(str(exc)))
        return await self._answer(self._success(obj))

    async def _answer(self, response: FakeResponse) -> FakeResponse:
        if not self._responses_held:
            return response
        future = asyncio.get_running_loop().create_future()
        self._held_responses.append((future, response))
        return await asyncio.shield(future)

    def seed_client(self, inbound_ids: list[int], client: dict) -> None:
        """Add one client directly, without recording an API call or restart."""
        self.collect_due()
        try:
            self._add_client({"inboundIds": inbound_ids, "client": client})
        except _RequestFailure as exc:
            raise ValueError(str(exc)) from None

    def seed_subscription(
        self, fixture: CompositeFixture, subscription_key: str, *, enable: bool = True
    ) -> None:
        """Seed the subscription credentials whose nodes belong to this panel."""
        self.collect_due()
        subscription = fixture.subscription(subscription_key)
        credentials = {credential.node_key: credential for credential in subscription.credentials}
        for node in fixture.nodes:
            if node.panel_key != self._panel_key or node.key not in credentials:
                continue
            inbound = fixture.inbound(node.panel_key, node.inbound_id)
            credential = credentials[node.key]
            if inbound.protocol == "vless":
                client = {
                    "id": credential.secret,
                    "flow": inbound.flow,
                    "email": credential.email,
                    "enable": enable,
                }
            elif inbound.protocol == "vmess":
                client = {
                    "id": credential.secret,
                    "security": inbound.vmess_cipher,
                    "email": credential.email,
                    "enable": enable,
                }
            elif inbound.protocol == "trojan":
                client = {
                    "password": credential.secret,
                    "email": credential.email,
                    "enable": enable,
                }
            else:
                raise FakeNotModelled(f"seed protocol {inbound.protocol!r}")
            self.seed_client([node.inbound_id], client)

    def client(self, email: str) -> dict | None:
        self.collect_due()
        matches = self._find_clients(email)
        return self._client_json(matches[0][2]) if matches else None

    def inbound_clients(self, inbound_id: int) -> list[dict]:
        self.collect_due()
        inbound = self._inbounds[inbound_id]
        return [self._client_json(client) for client in inbound["clients"]]

    def setting(self, name: str) -> object:
        self.run_due()
        return deepcopy(self._settings[name])

    def set_setting(self, name: str, value: object) -> None:
        self.run_due()
        if name not in self._settings:
            raise KeyError(name)
        self._settings[name] = deepcopy(value)

    def reset_settings(self) -> None:
        self.run_due()
        self._settings = self._default_settings()

    def _default_settings(self) -> dict:
        return {
            "restartXrayOnClientDisable": True,
            "webPort": 2053,
            "webBasePath": "/xui/",
        }

    def _record(self, method: str, path: str, scope: str | None) -> None:
        self._calls.append(RecordedCall(method, path, scope))

    def _resolve_route(self, method: str, path: str) -> tuple[str | None, tuple]:
        for route_method, pattern, route in _MODELLED_ROUTES:
            match = pattern.fullmatch(path)
            if route_method == method and match:
                return route, match.groups()

        for route_method, pattern in _UNMODELLED_PATTERNS:
            match = pattern.fullmatch(path)
            if route_method == method and match:
                if path == "/panel/api/clients/get/tgId/" + (match.group(1) if match.groups() else ""):
                    return "clients_get_by_tgid", match.groups()
                if path.startswith("/panel/api/clients/get/"):
                    return "clients_get", match.groups()
                if path.endswith("/attach"):
                    return "clients_attach", match.groups()
                if path.endswith("/detach"):
                    return "clients_detach", match.groups()
                if path.endswith("/externalLinks"):
                    return "clients_external_links", match.groups()
                return "unmodelled", match.groups()

        return None, ()

    def _scope_permits(self, scope: str, method: str, path: str, route: str) -> bool:
        if scope == "admin":
            return True
        if scope == "monitor":
            return (method, path) == ("GET", "/panel/api/server/status")
        if scope != "node-sync":
            return False
        if (method, path) in {
            ("GET", "/panel/api/server/status"),
            ("GET", "/panel/api/inbounds/list"),
            ("POST", "/panel/api/clients/add"),
        }:
            return True
        return route in {
            "clients_del",
            "clients_update",
            "clients_reset_traffic",
        }

    def _run_route(self, route: str, params: tuple, query: dict, body: object):
        if route == "inbounds_list":
            return [self._inbound_json(inbound_id) for inbound_id in sorted(self._inbounds)]
        if route == "inbound_get":
            inbound_id = int(params[0])
            if inbound_id not in self._inbounds:
                raise _RequestFailure("record not found")
            return self._inbound_json(inbound_id)
        if route == "clients_add":
            self._add_client(body)
            return None
        if route == "clients_update":
            self._update_client(params[0], query, body)
            return None
        if route == "clients_del":
            self._delete_client(params[0], query)
            return None
        if route == "clients_traffic":
            return self.traffic(params[0])
        if route == "clients_reset_traffic":
            self._reset_traffic(params[0])
            return None
        if route == "clients_update_traffic":
            self._update_traffic(params[0], body)
            return None
        if route == "setting_all":
            return deepcopy(self._settings)
        if route == "server_status":
            uptime = (self._clock.true_now_ms() - self._xray_started_ms) // 1000
            return {"appStats": {"uptime": uptime}}
        raise FakeNotModelled(f"handler for route {route!r}")

    def _add_client(self, body: object) -> None:
        if not isinstance(body, dict):
            raise _RequestFailure("empty payload")

        raw_client = body.get("client")
        client = raw_client if isinstance(raw_client, dict) else {}
        email = client.get("email")
        if email is None or email == "":
            raise _RequestFailure("client email is required")

        inbound_ids = body.get("inboundIds")
        if inbound_ids is None or inbound_ids == []:
            raise _RequestFailure("at least one inbound is required")
        if not isinstance(inbound_ids, list):
            raise FakeNotModelled("non-list inboundIds in client create")
        for inbound_id in inbound_ids:
            if type(inbound_id) is not int:
                raise FakeNotModelled("non-integer inbound id in client create")
            if inbound_id not in self._inbounds:
                raise _RequestFailure(f"inbound {inbound_id}: record not found")

        values = self._validated_client_values(client, default_enable=True)
        if not values["email"]:
            raise _RequestFailure("client email is required")

        existing_email = self._find_clients(values["email"])
        if existing_email:
            prior_sub_id = existing_email[0][2]["subId"]
            if prior_sub_id and values["subId"] and prior_sub_id == values["subId"]:
                raise FakeNotModelled("re-adding an email with its existing subId")
            raise _RequestFailure(f"email already in use: {values['email']}")

        if values["subId"] and any(
            stored["subId"] == values["subId"]
            for _, _, stored in self._all_clients()
        ):
            raise _RequestFailure(f"subId already in use: {values['subId']}")

        if values["email"] in self._traffic:
            raise FakeNotModelled("reusing an email with a retained traffic record")

        targets = [self._inbounds[inbound_id]["source"] for inbound_id in inbound_ids]
        for inbound in targets:
            if inbound.protocol == "trojan" and not values["password"]:
                raise FakeNotModelled("adding a Trojan client without a password")
            if inbound.protocol not in {"vless", "vmess", "trojan"}:
                raise FakeNotModelled(f"add client for protocol {inbound.protocol!r}")
        if not values["id"] and any(
            inbound.protocol in {"vless", "vmess"} for inbound in targets
        ):
            values["id"] = str(uuid.uuid4())

        now = self._clock.true_now_ms()
        stored_client = {**values, "created_at": now, "updated_at": now}
        for inbound_id in inbound_ids:
            self._inbounds[inbound_id]["clients"].append(deepcopy(stored_client))
        self._counters[values["email"]] = (0, 0)
        self._traffic[values["email"]] = self._new_traffic_record(
            inbound_ids[0], stored_client
        )

    def _update_client(self, path_email: str, query: dict, body: object) -> None:
        if "inboundIds" in query:
            raise FakeNotModelled("client update with inboundIds query")
        matches = self._find_clients(path_email)
        if not matches:
            raise _RequestFailure("record not found")
        if not isinstance(body, dict):
            body = {}
        incoming = self._validated_client_values(body, default_enable=False)
        if not incoming["email"]:
            raise _RequestFailure("client email is required")

        new_email = incoming["email"]
        if any(client["email"] != path_email and client["email"] == new_email for _, _, client in self._all_clients()):
            raise _RequestFailure(f"email already in use: {new_email}")
        if new_email != path_email and new_email in self._traffic:
            raise FakeNotModelled("renaming a client onto a retained traffic record")

        old_client = matches[0][2]
        record = self._traffic.get(path_email)
        if record is None:
            raise FakeNotModelled("updating a client without a traffic record")
        updated = dict(_CLIENT_DEFAULTS)
        updated.update(incoming)
        for field in ("id", "password", "subId"):
            if not updated[field]:
                updated[field] = old_client[field]
        updated["created_at"] = old_client["created_at"]
        updated["updated_at"] = self._clock.true_now_ms()

        for inbound_id, index, _ in matches:
            self._inbounds[inbound_id]["clients"][index] = deepcopy(updated)

        self._traffic.pop(path_email)
        counter = self._counters.pop(path_email, None)
        last_values = self._last_values.pop(path_email, None)
        record["email"] = new_email
        record["enable"] = updated["enable"]
        record["expiryTime"] = updated["expiryTime"]
        record["total"] = updated["totalGB"]
        record["reset"] = updated["reset"]
        self._traffic[new_email] = record
        if counter is not None:
            self._counters[new_email] = counter
        if last_values is not None:
            self._last_values[new_email] = last_values

        if old_client["enable"] and not updated["enable"]:
            self._maybe_restart()

    def _delete_client(self, email: str, query: dict) -> None:
        if not self._find_clients(email):
            raise _RequestFailure(
                f'client "{email}" not found in any inbound or client record'
            )
        for inbound in self._inbounds.values():
            inbound["clients"] = [
                client for client in inbound["clients"] if client["email"] != email
            ]
        self._counters.pop(email, None)
        self._last_values.pop(email, None)
        if query.get("keepTraffic") != "1":
            self._traffic.pop(email, None)
        self._maybe_restart()

    def _maybe_restart(self) -> None:
        if self._settings["restartXrayOnClientDisable"]:
            self.restart("xray")

    def _reset_traffic(self, email: str) -> None:
        matches = self._find_clients(email)
        if not matches:
            raise FakeNotModelled(f"resetting traffic for missing client {email!r}")
        record = self._traffic.get(email)
        if record is None:
            raise FakeNotModelled(f"resetting traffic without a record for {email!r}")

        now = self._clock.true_now_ms()
        record["up"] = 0
        record["down"] = 0
        record["enable"] = True
        for inbound_id, index, _ in matches:
            client = self._inbounds[inbound_id]["clients"][index]
            client["enable"] = True
            client["updated_at"] = now

    def _update_traffic(self, email: str, body: object) -> None:
        record = self._traffic.get(email)
        if record is None:
            raise FakeNotModelled(f"updating traffic for missing record {email!r}")
        if not isinstance(body, dict):
            raise _RequestFailure("invalid traffic body")

        values = {}
        for field in ("upload", "download"):
            value = body.get(field, 0)
            if type(value) is not int:
                raise _RequestFailure(f"invalid traffic field: {field}")
            values[field] = value
        if values["upload"] < 0 or values["download"] < 0:
            raise FakeNotModelled("updating traffic to a negative value")
        record["up"] = values["upload"]
        record["down"] = values["download"]

    def _validated_client_values(self, client: dict, *, default_enable: bool) -> dict:
        values = dict(_CLIENT_DEFAULTS)
        for name in (*_STRING_FIELDS, *_INTEGER_FIELDS, "enable"):
            if name not in client:
                continue
            value = client[name]
            if name in _STRING_FIELDS:
                valid = type(value) is str
            elif name in _INTEGER_FIELDS:
                valid = type(value) is int
            else:
                valid = type(value) is bool
            if not valid:
                raise _RequestFailure(f"invalid client field: {name}")
            values[name] = value
        if "enable" not in client:
            values["enable"] = default_enable
        return values

    def _new_traffic_record(self, inbound_id: int, client: dict) -> dict:
        record = {
            "id": self._next_traffic_id,
            "inboundId": inbound_id,
            "enable": client["enable"],
            "email": client["email"],
            "up": 0,
            "down": 0,
            "expiryTime": client["expiryTime"],
            "total": client["totalGB"],
            "reset": client["reset"],
            "lastOnline": 0,
        }
        self._next_traffic_id += 1
        return record

    def _all_clients(self) -> list[tuple[int, int, dict]]:
        return [
            (inbound_id, index, client)
            for inbound_id in sorted(self._inbounds)
            for index, client in enumerate(self._inbounds[inbound_id]["clients"])
        ]

    def _find_clients(self, email: str) -> list[tuple[int, int, dict]]:
        return [entry for entry in self._all_clients() if entry[2]["email"] == email]

    def _client_json(self, client: dict) -> dict:
        result = {
            field: deepcopy(client[field])
            for field in (*_STRING_FIELDS, *_INTEGER_FIELDS, "enable", "created_at", "updated_at")
        }
        for field in _OMIT_EMPTY:
            if result[field] == "":
                del result[field]
        return result

    def _inbound_json(self, inbound_id: int) -> dict:
        model = self._inbounds[inbound_id]
        source: Inbound = model["source"]
        stream = {
            "network": source.transport,
            "security": source.security,
            "externalProxy": [
                {
                    "forceTls": "same",
                    "dest": proxy.host,
                    "port": proxy.port,
                    "remark": "",
                }
                for proxy in source.external_proxies
            ],
        }
        if source.security == "reality":
            stream["realitySettings"] = {
                "show": False,
                "xver": 0,
                "target": f"{source.sni}:443",
                "serverNames": [source.sni],
                "privateKey": source.reality_private_key,
                "shortIds": [source.reality_short_id],
                "settings": {
                    "publicKey": source.reality_public_key,
                    "fingerprint": source.fingerprint,
                    "serverName": "",
                    "spiderX": "/",
                },
            }
        elif source.security == "tls":
            stream["tlsSettings"] = {
                "serverName": source.sni,
                "alpn": [],
                "settings": {"fingerprint": source.fingerprint},
            }
        else:
            raise FakeNotModelled(f"inbound security {source.security!r}")

        if source.transport == "tcp":
            stream["tcpSettings"] = {"header": {"type": source.tcp_header_type or "none"}}
        elif source.transport == "ws":
            stream["wsSettings"] = {
                "path": source.ws_path,
                "host": source.ws_host,
                "headers": {},
            }
        elif source.transport == "grpc":
            stream["grpcSettings"] = {
                "serviceName": source.grpc_service_name,
                "authority": "",
                "multiMode": source.grpc_mode == "multi",
            }
        else:
            raise FakeNotModelled(f"inbound transport {source.transport!r}")

        clients = [self._client_json(client) for client in model["clients"]]
        settings = {"clients": clients}
        if source.protocol == "vless":
            settings["decryption"] = "none"
        elif source.protocol not in {"trojan", "vmess"}:
            raise FakeNotModelled(f"inbound protocol {source.protocol!r}")
        stats = [
            deepcopy(self._traffic[client["email"]])
            for client in model["clients"]
            if client["email"] in self._traffic
        ]
        return {
            "id": source.inbound_id,
            "up": model["up"],
            "down": model["down"],
            "total": 0,
            "remark": f"inbound-{source.inbound_id}",
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": source.listen_port,
            "protocol": source.protocol,
            "tag": f"inbound-{source.listen_port}",
            "sniffing": {"enabled": False},
            "settings": settings,
            "streamSettings": stream,
            "clientStats": stats,
        }

    @staticmethod
    def _success(obj: object) -> FakeResponse:
        return FakeResponse(
            200,
            {"success": True, "msg": "", "obj": deepcopy(obj)},
        )

    @staticmethod
    def _failure(error: str) -> FakeResponse:
        return FakeResponse(
            200,
            {"success": False, "msg": f"Request failed ({error})", "obj": None},
        )
