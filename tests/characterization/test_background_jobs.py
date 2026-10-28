"""Characterize background job ownership in ``main.py`` and ``bot_manager.py`` at commit 9286b41.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_background_jobs.py --network=deny``.
Telegram is a fake aiogram session and the six job loops are recorders that wait until cancelled,
as the real loops do (substitute, not evidence). Every database is a SQLite file under ``tmp_path``.

Ownership (FR-085 startup/shutdown): every background job belongs to a running bot. ``start_bot``
starts polling plus five jobs bound to that bot's own ``Bot`` and ``Database``, and the main bot
alone gets the extra-gateway poll (case 1). A tenant without a running bot has no jobs: ``main()``
skips inactive and ``has_live_bot=0`` tenants, and a tenant whose start fails keeps no instance
(cases 2, 7); the reconciler skips them too and never starts the main bot (case 5).

Known unsafe behaviour: (a) ``stop_bot`` re-raises the ``CancelledError`` of the polling task it
cancelled, so it stops after that task: the tenant's five jobs and aiogram's inner polling task keep
running with no instance left to own them (case 4); (b) the same error ends
``reconcile_resellers_loop`` the first time it stops a disabled tenant, before that pass's purge
(case 6); (c) the deferred purge deletes a queued database without checking ``reseller_bots``, so an
active no-bot tenant loses its database, and it leaves the main file's ``-wal``/``-shm`` behind
(case 5); (d) a failed start still initializes the tenant database and writes ``bot_role`` (cases 2,
7); (e) cancelling ``main()`` never reaches ``stop_all``, because awaiting the cancelled reconciler
raises inside its ``finally`` (case 8); (f) SIGTERM/SIGINT reach only the last bot whose polling
started, and its stopped polling goes unnoticed while another bot runs (case 9); when it was the only
bot, ``main()`` ends by ``CancelledError`` after stopping one job (case 10). Importing ``main``
creates ``logs/bot.log`` in the working directory.
"""

import asyncio
import contextlib
import dataclasses
import importlib
import os
import signal

import pytest
from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import GetMe, GetUpdates
from aiogram.types import User
from aiogram.utils.token import TokenValidationError

import bot_manager
import database
import extra_gateway_payment
from tests._harness.legacy_bot import SYNTHETIC_BOT_TOKEN, SYNTHETIC_OWNER_ID

MAIN = SYNTHETIC_BOT_TOKEN
TENANT_A = "200001:tenant-a-synthetic"
TENANT_B = "200002:tenant-b-no-live-bot"
TENANT_C = "200003:tenant-c-disabled"
TENANT_GONE = "200009:tenant-deleted"
BAD_TOKEN = "bad-token"
STARTUP_TELEGRAM = ["DeleteWebhook", "SetChatMenuButton", "GetMe", "GetUpdates"]
TENANT_JOBS = ["backup_loop", "cache_autorefresh_loop", "connect_alert_loop", "renewal_reminder_loop", "temp_message_cleanup_loop"]
MAIN_JOBS = sorted(TENANT_JOBS + ["poll_loop"])
INSTANCE_KEYS = {
    "bot", "dp", "task", "reminder_task", "connect_alert_task", "backup_task",
    "cache_refresh_task", "temp_msg_task", "extra_gateway_task", "db_path",
}
JOB_TASK_KEYS = ["reminder_task", "connect_alert_task", "backup_task", "cache_refresh_task", "temp_msg_task"]


class FakeTelegramSession(BaseSession):
    """Answers every Bot API call locally; ``getUpdates`` waits forever like an idle long poll."""

    def __init__(self, calls):
        super().__init__()
        self.calls = calls

    async def make_request(self, bot, method, timeout=None):
        self.calls.append((bot.token, type(method).__name__))
        if isinstance(method, GetMe):
            return User(id=bot.id, is_bot=True, first_name="synthetic")
        if isinstance(method, GetUpdates):
            await asyncio.Event().wait()
        return True

    async def stream_content(self, url, headers=None, timeout=30, chunk_size=65536, raise_for_status=True):
        raise NotImplementedError
        yield b""

    async def close(self):
        pass


@dataclasses.dataclass
class Job:
    name: str
    bot: object
    db: object
    args: tuple
    stopped: bool = False


@dataclasses.dataclass
class Legacy:
    jobs: list
    calls: list

    def job_names(self, db_path):
        return sorted(j.name for j in self.jobs if j.db.db_path == db_path)

    def telegram(self, token):
        return [name for t, name in self.calls if t == token]


def _recorder(name, jobs):
    async def loop(*args):
        if name == "cache_autorefresh_loop":
            job = Job(name, None, args[0], args)
        else:
            job = Job(name, args[0], args[1], args)
        jobs.append(job)
        try:
            await asyncio.Event().wait()
        finally:
            job.stopped = True

    return loop


@pytest.fixture
def legacy(monkeypatch):
    jobs, calls = [], []
    for name in ("renewal_reminder_loop", "connect_alert_loop", "backup_loop", "temp_message_cleanup_loop"):
        monkeypatch.setattr(bot_manager, name, _recorder(name, jobs))
    monkeypatch.setattr(extra_gateway_payment, "poll_loop", _recorder("poll_loop", jobs))
    monkeypatch.setattr(database.Database, "cache_autorefresh_loop", _recorder("cache_autorefresh_loop", jobs))
    monkeypatch.setattr(
        bot_manager, "Bot",
        lambda token, default=None: Bot(token=token, default=default, session=FakeTelegramSession(calls)),
    )
    return Legacy(jobs, calls)


@pytest.fixture
def legacy_main(monkeypatch, tmp_path, legacy):
    """Import ``main`` from ``tmp_path`` (it creates ``logs/`` on import) and record its manager."""
    monkeypatch.chdir(tmp_path)
    main = importlib.import_module("main")
    managers = []

    class RecordingManager(bot_manager.BotManager):
        def __init__(self):
            super().__init__()
            managers.append(self)

    monkeypatch.setattr(main, "BotManager", RecordingManager)
    monkeypatch.setattr(main, "DB_PATH", str(tmp_path / "main.db"))
    return main, managers


async def _until(predicate, timeout=2.0):
    for _ in range(int(timeout / 0.01)):
        if predicate():
            return
        await asyncio.sleep(0.01)
    raise AssertionError("condition not reached")


def _path(tmp_path, name):
    return str(tmp_path / f"{name}.db")


def _main_db(tmp_path):
    db = database.Database(_path(tmp_path, "main"))
    db.init_db(owner_id=SYNTHETIC_OWNER_ID)
    return db


def _register(main_db, token, n, db_path, *, live=True, active=True, slug=None):
    bot_id = main_db.register_reseller_bot(token, f"tenant_{n}_bot", 700000000 + n, f"Tenant {n}", db_path, has_live_bot=1 if live else 0)
    if slug:
        main_db.set_reseller_link_slug(bot_id, slug)
    if not active:
        main_db.toggle_reseller_bot(bot_id)
    return bot_id


def _setting(db_path, key):
    return database.Database(db_path).get_setting(key)


def _task_named(qualname):
    return [t for t in asyncio.all_tasks() if t.get_coro().__qualname__ == qualname]


async def _start_main_and_a(manager, tmp_path, legacy):
    assert await manager.start_bot(MAIN, _path(tmp_path, "main"), SYNTHETIC_OWNER_ID, is_main_bot=True) is True
    assert await manager.start_bot(TENANT_A, _path(tmp_path, "a"), 700000001, is_main_bot=False) is True
    await _until(lambda: legacy.telegram(MAIN) == STARTUP_TELEGRAM and legacy.telegram(TENANT_A) == STARTUP_TELEGRAM)


async def _start_legacy_main(main, managers):
    """Run ``main.main()`` until its startup created the reconciler task."""
    task = asyncio.create_task(main.main())
    await _until(lambda: bool(_task_named("BotManager.reconcile_resellers_loop")))
    return task, managers[0], _task_named("BotManager.reconcile_resellers_loop")[0]


# Case 1
def test_start_bot_owns_jobs_per_bot(tmp_path, legacy):
    main_path, a_path = _path(tmp_path, "main"), _path(tmp_path, "a")

    async def scenario():
        m = bot_manager.BotManager()
        await _start_main_and_a(m, tmp_path, legacy)
        main_inst, a_inst = m.instances[MAIN], m.instances[TENANT_A]

        assert set(m.instances) == {MAIN, TENANT_A}
        assert set(main_inst) == INSTANCE_KEYS and set(a_inst) == INSTANCE_KEYS
        assert main_inst["db_path"] == main_path and a_inst["db_path"] == a_path
        assert isinstance(main_inst["extra_gateway_task"], asyncio.Task)
        assert a_inst["extra_gateway_task"] is None
        assert legacy.job_names(main_path) == MAIN_JOBS
        assert legacy.job_names(a_path) == TENANT_JOBS
        for inst, path, token in ((main_inst, main_path, MAIN), (a_inst, a_path, TENANT_A)):
            own = [j for j in legacy.jobs if j.db.db_path == path]
            assert len({id(j.db) for j in own}) == 1
            assert all(j.bot is inst["bot"] for j in own if j.name != "cache_autorefresh_loop")
            assert [j.args[2] for j in own if j.name == "backup_loop"] == [path]
            assert inst["bot"].token == token
        assert _setting(a_path, "bot_role") == "full_reseller"
        assert _setting(main_path, "bot_role") == ""

        assert await m.start_bot(TENANT_A, a_path, 700000001, is_main_bot=False) is False
        assert m.instances[TENANT_A] is a_inst
        assert len(legacy.jobs) == 11
        assert legacy.telegram(TENANT_A) == STARTUP_TELEGRAM

    asyncio.run(scenario())


# Case 2
def test_failed_start_keeps_no_instance_but_writes_tenant_db(tmp_path, legacy):
    e_path = _path(tmp_path, "e")

    async def scenario():
        m = bot_manager.BotManager()
        with pytest.raises(TokenValidationError):
            await m.start_bot(BAD_TOKEN, e_path, 700000005, is_main_bot=False)
        assert m.instances == {}
        assert legacy.jobs == [] and legacy.calls == []
        assert _setting(e_path, "bot_role") == "full_reseller"

    asyncio.run(scenario())


# Case 3
def test_stop_bot_unknown_token_returns_false(legacy):
    async def scenario():
        return await bot_manager.BotManager().stop_bot("200099:never-started")

    assert asyncio.run(scenario()) is False


# Case 4
def test_stop_bot_raises_after_cancelling_polling_and_orphans_jobs(tmp_path, legacy):
    async def scenario():
        m = bot_manager.BotManager()
        await _start_main_and_a(m, tmp_path, legacy)
        a_inst = m.instances[TENANT_A]

        with pytest.raises(asyncio.CancelledError):
            await m.stop_bot(TENANT_A)

        assert set(m.instances) == {MAIN}
        assert a_inst["task"].cancelled()
        assert [key for key in JOB_TASK_KEYS if a_inst[key].done()] == []
        assert [j.name for j in legacy.jobs if j.stopped] == []
        assert not m.instances[MAIN]["task"].done()
        # aiogram's inner polling task of the stopped tenant is never cancelled.
        assert len([t for t in _task_named("Dispatcher._polling") if not t.done()]) == 2

    asyncio.run(scenario())


# Case 5
def test_reconcile_starts_live_tenants_and_runs_deferred_purge(tmp_path, legacy):
    a_path, b_path, c_path = _path(tmp_path, "a"), _path(tmp_path, "b"), _path(tmp_path, "c")
    gone_path, a_old_path = _path(tmp_path, "gone"), _path(tmp_path, "a-old")
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_A, 1, a_path, slug="alpha")
    _register(main_db, TENANT_B, 2, b_path, live=False)
    _register(main_db, TENANT_C, 3, c_path, active=False)
    for name in (gone_path, gone_path + "-wal", gone_path + "-shm", gone_path + ".fsm.sqlite3",
                 gone_path + ".fsm.sqlite3-wal", gone_path + ".fsm.sqlite3-shm", b_path, a_old_path):
        open(name, "w").close()
    main_db.queue_db_purge(TENANT_GONE, gone_path)
    main_db.queue_db_purge(TENANT_B, b_path)
    main_db.queue_db_purge(TENANT_A, a_old_path)

    async def scenario():
        m = bot_manager.BotManager()
        loop_task = asyncio.create_task(m.reconcile_resellers_loop(main_db, MAIN, interval=0.01))
        try:
            await _until(lambda: TENANT_A in m.instances and len(main_db.list_pending_db_purges()) == 1)
        finally:
            loop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await loop_task

        assert set(m.instances) == {TENANT_A}
        assert m.instances[TENANT_A]["menu_checked"] is True
        assert legacy.job_names(a_path) == TENANT_JOBS
        assert [j for j in legacy.jobs if j.db.db_path != a_path] == []
        assert _setting(a_path, "miniapp_tenant_id") == "alpha"
        assert _setting(a_path, "bot_role") == "full_reseller"
        assert not os.path.exists(c_path)
        # Purge of a token with no running bot: database and FSM files removed, main WAL/SHM kept.
        assert sorted(p.name for p in tmp_path.iterdir() if p.name.startswith("gone")) == ["gone.db-shm", "gone.db-wal"]
        # The no-bot tenant is still active in reseller_bots, yet its database was deleted.
        assert not os.path.exists(b_path)
        assert TENANT_B in [r["bot_token"] for r in main_db.list_reseller_bots(active_only=True)]
        # A purge queued for a running bot waits.
        assert os.path.exists(a_old_path)
        assert [(r["bot_token"], r["db_path"]) for r in main_db.list_pending_db_purges()] == [(TENANT_A, a_old_path)]

    asyncio.run(scenario())


# Case 6
def test_reconcile_loop_dies_when_stopping_disabled_tenant(tmp_path, legacy):
    c_path, gone_path = _path(tmp_path, "c"), _path(tmp_path, "gone")
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_C, 3, c_path, active=False)
    open(gone_path, "w").close()
    main_db.queue_db_purge(TENANT_GONE, gone_path)

    async def scenario():
        m = bot_manager.BotManager()
        assert await m.start_bot(MAIN, _path(tmp_path, "main"), SYNTHETIC_OWNER_ID, is_main_bot=True) is True
        assert await m.start_bot(TENANT_C, c_path, 700000003, is_main_bot=False) is True
        c_inst = m.instances[TENANT_C]

        loop_task = asyncio.create_task(m.reconcile_resellers_loop(main_db, MAIN, interval=0.01))
        await _until(loop_task.done)

        assert loop_task.cancelled()
        assert set(m.instances) == {MAIN}
        assert c_inst["task"].cancelled()
        assert [key for key in JOB_TASK_KEYS if c_inst[key].done()] == []
        assert [j.name for j in legacy.jobs if j.stopped] == []
        # The purge step of that pass never ran.
        assert os.path.exists(gone_path)
        assert [r["bot_token"] for r in main_db.list_pending_db_purges()] == [TENANT_GONE]

    asyncio.run(scenario())


# Case 7
def test_main_starts_main_bot_and_live_active_tenants_only(tmp_path, legacy_main, legacy):
    main, managers = legacy_main
    main_path, a_path, b_path, c_path, e_path = (_path(tmp_path, n) for n in ("main", "a", "b", "c", "e"))
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_A, 1, a_path)
    _register(main_db, TENANT_B, 2, b_path, live=False)
    _register(main_db, TENANT_C, 3, c_path, active=False)
    _register(main_db, BAD_TOKEN, 4, e_path)

    async def scenario():
        task, m, reconcile_task = await _start_legacy_main(main, managers)
        try:
            assert set(m.instances) == {MAIN, TENANT_A}
            assert legacy.job_names(main_path) == MAIN_JOBS
            assert legacy.job_names(a_path) == TENANT_JOBS
            assert len(legacy.jobs) == 11
            assert _setting(a_path, "miniapp_tenant_id") == "1"
            assert _setting(a_path, "bot_role") == "full_reseller"
            assert not os.path.exists(b_path)
            assert not os.path.exists(c_path)
            assert _setting(e_path, "miniapp_tenant_id") == "4"
            assert _setting(e_path, "bot_role") == "full_reseller"
            assert not reconcile_task.done() and not task.done()
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    asyncio.run(scenario())


# Case 8
def test_main_cancel_never_reaches_stop_all(tmp_path, legacy_main, legacy):
    main, managers = legacy_main
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_A, 1, _path(tmp_path, "a"))

    async def scenario():
        task, m, reconcile_task = await _start_legacy_main(main, managers)
        polling = [m.instances[MAIN]["task"], m.instances[TENANT_A]["task"]]
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert reconcile_task.cancelled()
        assert set(m.instances) == {MAIN, TENANT_A}
        assert [t.done() for t in polling] == [False, False]
        assert [j.name for j in legacy.jobs if j.stopped] == []

    asyncio.run(scenario())


# Case 9
def test_signals_reach_only_last_started_bot(tmp_path, legacy_main, legacy):
    main, managers = legacy_main
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_A, 1, _path(tmp_path, "a"))

    async def scenario():
        task, m, reconcile_task = await _start_legacy_main(main, managers)
        try:
            await _until(lambda: legacy.telegram(TENANT_A) == STARTUP_TELEGRAM)
            a_inst = m.instances[TENANT_A]
            # Private asyncio attribute (CPython 3.12 Unix loop): the registered signal handles.
            handles = asyncio.get_running_loop()._signal_handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                assert handles[sig]._callback.__self__ is a_inst["dp"]
                assert handles[sig]._args == (sig,)

            handles[signal.SIGTERM]._run()
            await _until(a_inst["task"].done)
            await asyncio.sleep(0.2)

            assert a_inst["task"].result() is None
            assert set(m.instances) == {MAIN, TENANT_A}
            assert not m.instances[MAIN]["task"].done()
            assert not task.done() and not reconcile_task.done()
            assert [j.name for j in legacy.jobs if j.stopped] == []
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    asyncio.run(scenario())


# Case 10
def test_main_bot_start_failure_then_only_tenant_stops(tmp_path, monkeypatch, legacy_main, legacy):
    main, managers = legacy_main
    monkeypatch.setattr(main, "BOT_TOKEN", BAD_TOKEN)
    a_path = _path(tmp_path, "a")
    main_db = _main_db(tmp_path)
    _register(main_db, TENANT_A, 1, a_path)

    async def scenario():
        task, m, reconcile_task = await _start_legacy_main(main, managers)
        await _until(lambda: legacy.telegram(TENANT_A) == STARTUP_TELEGRAM)
        assert set(m.instances) == {TENANT_A}
        assert legacy.job_names(_path(tmp_path, "main")) == []
        assert not task.done()

        asyncio.get_running_loop()._signal_handlers[signal.SIGTERM]._run()
        await _until(task.done)

        assert task.cancelled()
        assert reconcile_task.cancelled()
        assert m.instances == {}
        assert [j.name for j in legacy.jobs if j.stopped] == ["renewal_reminder_loop"]
        assert legacy.job_names(a_path) == TENANT_JOBS

    asyncio.run(scenario())
