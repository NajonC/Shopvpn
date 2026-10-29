"""Characterize backup and restore in ``backup.py`` at commit 1f2f399.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_backup_restore.py --network=deny``.
Every file is under ``tmp_path``; reseller databases sit in ``reseller_dbs`` as in
production; cases 21–30 characterize the restore callers in ``handlers_admin.py``,
``admin_panel/server.py`` and ``manage.sh`` at commit 7effd72, with the bot manager,
Telegram downloads and the web session cookie as substitutes.

Known unsafe behaviour (FR-076; FR-083):
(a) retention keeps the names that sort last, so a foreign ``main_zzz.db`` makes
``create_backup`` delete the backup it just made and still return its path (case 4);
(b) two backups or restores in the same second share one file name and the later
overwrites the earlier (cases 5, 16);
(c) a full backup has no coherent cut: the reseller list is read after the main
copy, so a reseller registered in between is archived but missing from the archived
main (case 10); a reseller copy that fails still leaves an empty member in the
archive (case 9);
(d) ``restore_full_backup`` replaces main before it checks any tenant file, and
every tenant pre-restore copy in one second goes to the same
``reseller_dbs/backups/pre_restore_<ts>.db``, so only the last survives (cases 16, 17);
(e) a reseller listed in the restored main but absent from the archive is reported
nowhere and keeps its newer file (case 16);
(f) ``restore_backup`` ignores its ``db_path`` argument and accepts any SQLite file
whatever its schema (case 15);
(g) SFTP never verifies the host key, ``known_hosts=None`` (case 19);
(h) the Telegram full restore stops only the running resellers named in the archive, looked up in the live main before it is replaced; it never stops the main bot or the web panel, never restarts the bots it stopped, and a failed restore leaves them stopped (cases 21, 22);
(i) uploads are checked shallowly: the full upload checks only member names and counts ``reseller_x.db`` as a reseller, and a rejected upload leaves its temporary file behind (cases 24, 27);
(j) the single Telegram restore accepts a SQLite file with a foreign schema, replaces the database and then crashes on the admin log with no reply after the progress message (case 26);
(k) the web restore accepts ``RESTORE`` in any case with surrounding spaces and any case of ``.db``, ``.sqlite``, ``.sqlite3`` (case 29);
(l) ``manage.sh`` restores only ``bot_database.db`` through ``restore_backup``; reseller databases are not restored (case 30).
"""

import asyncio
import datetime
import logging
import os
import pathlib
import shutil
import sqlite3
import tempfile
import zipfile
from types import SimpleNamespace

import httpx
import pytest

import backup
import database
import handlers_admin
from states import AdminRestoreBackup, AdminRestoreFullBackup
from tests._harness.legacy_bot import FakeCallbackQuery, FakeMessage, FakeUser, RecordingBot, TelegramEvent, TelegramLog, callback_rows, find_handler, make_state
from tests._harness.legacy_web import load_admin_panel, session_cookie


TS = "20260102_030405"
OWNER = 9001
NOT_SQLITE = b"not a database" * 20  # 280 bytes
SQLITE_HEADER = b"SQLite format 3\x00"
MANIFEST_HEADER = "بکاپ کامل - شامل بات اصلی + همه\u200cی بات\u200cهای نمایندگی (سطح \u06f1 و سطح \u06f2)"
MANIFEST_DATE = "تاریخ: 2026-01-02 06:34"
ACTIVE = "فعال"
INACTIVE = "غیرفعال"
COPY_FAILED = "[ناموفق - رد شد]"
FILE_MISSING = "[فایل پیدا نشد - رد شد]"
MAIN_INVALID = "فایل main_bot.db داخل zip پیدا نشد یا دیتابیس sqlite معتبری نیست."
BAD_NAME = "نام فایل نامعتبر است."
INVALID_SQLITE = "دیتابیس sqlite معتبر نیست."
REPLACE_FAILED = "خطا هنگام جایگزینی فایل."
UPLOAD_INVALID = "فایل ارسالی یک دیتابیس sqlite معتبر نیست."
SFTP_EMPTY = "آدرس سرور و یوزرنیم SSH نمی\u200cتوانند خالی باشند."
SFTP_NO_AUTH = "باید یکی از پسورد یا مسیر کلید خصوصی SSH مشخص شود."

FULL_WORKING = "⏳ در حال بازیابی کامل..."
FULL_MAIN_DONE = "✅ دیتابیس بات اصلی بازیابی شد."
FULL_FAILED = "❌ بازیابی کامل ناموفق بود: "
TMP_MISSING = "❌ فایل موقت پیدا نشد، دوباره تلاش کن."
DENY = "⛔\ufe0f این بخش فقط برای مدیران کامل در دسترس است."
ZIP_ONLY = "❌ فایل باید همان zip «بکاپ کامل» باشد. دوباره ارسال کن."
ZIP_NO_MAIN = "❌ این zip شامل main_bot.db نیست؛ فایل «بکاپ کامل» درستی به نظر نمی\u200cرسد."
SINGLE_WORKING = "⏳ در حال بازیابی..."
SINGLE_FAILED = "❌ بازیابی ناموفق بود: "
SINGLE_LOG = "بازیابی دیتابیس از فایل بکاپ آپلودی"
UPLOAD_NOT_SQLITE = "❌ این فایل یک دیتابیس sqlite معتبر نیست. عملیات لغو شد."
WEB_OWNER_ONLY = "این بخش فقط برای مالک است."
WEB_PHRASE = "برای تایید بازیابی، عبارت RESTORE را دقیقا\u064b وارد کن."
WEB_EXTENSION = "فایل باید پسوند .db یا .sqlite داشته باشد."
WEB_NOT_SQLITE = "این فایل یک دیتابیس sqlite معتبر نیست."
SINGLE_DONE = "✅ دیتابیس با موفقیت بازیابی شد.\nاز نسخه\u200cی قبلی هم یک بکاپ ایمن (pre_restore) کنار دیتابیس ذخیره شد."


def full_restored(n):
    return f"✅ {n} دیتابیس نماینده بازیابی شد:"


def full_skipped(n):
    return f"⚠\ufe0f {n} مورد رد شد:"


def stopped_note(n):
    return f"\nℹ\ufe0f {n} بات نماینده برای جایگزینی دیتابیس موقتا\u064b متوقف شد و ظرف چند ثانیه\u200cی آینده خودش دوباره روشن می\u200cشود."


def full_log(restored, skipped):
    return f"بازیابی کامل: {restored} نماینده بازیابی، {skipped} رد شد."


def full_received(n):
    return f"📦 فایل دریافت شد (0.0 مگابایت) — شامل بات اصلی + {n} دیتابیس نماینده.\n\n⚠\ufe0f با تایید، دیتابیس بات اصلی و دیتابیس همین نماینده\u200cها جایگزین می\u200cشود (از وضعیت فعلی هر کدام هم قبلش یک نسخه\u200cی pre_restore ذخیره می\u200cشود). مطمئنی؟"


def web_log(name):
    return f"دیتابیس از فایل آپلودی بازیابی شد؛ نسخه\u200cی قبلی: {name} (پنل وب - owner)"


NON_OWNER = 4242
WEB_OWNER = (1, "owner", "owner")
WEB_MID = (2, "mid1", "mid")
MANAGE_SH = pathlib.Path(__file__).resolve().parents[2] / "manage.sh"


@pytest.fixture
def uploads(tmp_path, monkeypatch):
    root = tmp_path / "tmp"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    return root


def _staged(uploads, folder, name):
    directory = uploads / folder
    directory.mkdir()
    return directory / name


class _BotManager:
    def __init__(self, live, running):
        self.live = live
        self.running = set(running)
        self.calls = []

    def is_running(self, token):
        self.calls.append(("is_running", token))
        return token in self.running

    async def stop_bot(self, token):
        self.calls.append(("stop_bot", token, self.live.get_setting("shop_name")))
        self.running.discard(token)


class _UploadBot(RecordingBot):
    def __init__(self, log, files):
        super().__init__(log)
        self.files = files
        self.downloads = []

    async def get_file(self, file_id):
        return SimpleNamespace(file_path=file_id)

    async def download_file(self, file_path, destination):
        self.downloads.append(file_path)
        shutil.copyfile(self.files[file_path], destination)


def _upload(log, bot, file_id, file_name):
    message = FakeMessage(log, OWNER, from_user=FakeUser(OWNER), document=SimpleNamespace(file_id=file_id, file_name=file_name))
    message.bot = bot
    return message


async def _state(group_state, **data):
    state = make_state(OWNER)
    await state.set_state(group_state)
    if data:
        await state.update_data(**data)
    return state


async def _press(handler, log, user, data, state):
    return await handler(FakeCallbackQuery(log, FakeUser(user), data, FakeMessage(log, OWNER)), state)


def _admin_logs(path):
    conn = sqlite3.connect(str(path))
    try:
        return conn.execute("SELECT admin_id, action, details, record_type, record_id FROM admin_logs ORDER BY id").fetchall()
    finally:
        conn.close()


def _edit(text):
    return TelegramEvent("edit_text", OWNER, 1, text)


def _answer(text=None, alert=False):
    return TelegramEvent("callback_answer", None, None, text, show_alert=alert)


@pytest.fixture
def web(monkeypatch, tmp_path_factory, tmp_path):
    panel = load_admin_panel(tmp_path_factory.getbasetemp())
    live = _main(tmp_path / "main.db", "LiveMain")
    monkeypatch.setattr(panel.MAIN_TENANT, "db", live)
    for admin_id, username, role in (WEB_OWNER, WEB_MID):
        assert live.create_web_admin(username, "synthetic-hash", role=role) == admin_id
    yield SimpleNamespace(panel=panel, live=live)
    live.close()


async def _post_restore(panel, who, file_name, content, phrase):
    headers = {"Cookie": "panel_session=" + session_cookie(panel.ADMIN_PANEL_SECRET, *who)}
    transport = httpx.ASGITransport(app=panel.app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://panel.test") as client:
        return await client.post("/api/system/backup/restore", headers=headers, files={"file": (file_name, content)}, data={"confirm_phrase": phrase})


def unknown_id(reseller_id):
    return f"نماینده\u200cای با id={reseller_id} در دیتابیس اصلی\u0650 بازیابی\u200cشده پیدا نشد."


def key_missing(path):
    return f"فایل کلید خصوصی در مسیر «{path}» روی این سرور پیدا نشد."


class _FrozenDatetime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return datetime.datetime(2026, 1, 2, 3, 4, 5)

    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(2026, 1, 2, 6, 34, 5)


@pytest.fixture
def frozen(monkeypatch):
    monkeypatch.setattr(backup, "datetime", _FrozenDatetime)
    monkeypatch.setattr(database, "datetime", _FrozenDatetime)


def _make_db(path, value):
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO settings VALUES ('shop_name', ?)", (value,))
        conn.commit()
    finally:
        conn.close()


def _value(path):
    conn = sqlite3.connect(str(path))
    try:
        return conn.execute("SELECT value FROM settings WHERE key='shop_name'").fetchone()[0]
    finally:
        conn.close()


def _tables(path):
    conn = sqlite3.connect(str(path))
    try:
        return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()


def _main(path, value=None):
    db = database.Database(str(path))
    db.init_db(OWNER)
    if value is not None:
        db.set_setting("shop_name", value)
    return db


def _reseller(db, n, path):
    return db.register_reseller_bot(f"100{n}:synthetic-r{n}", f"r{n}bot", 5000 + n, f"R{n}", str(path))


def _zip(path, members):
    with zipfile.ZipFile(path, "w") as zf:
        for name, source in members.items():
            if isinstance(source, pathlib.Path):
                zf.write(source, arcname=name)
            else:
                zf.writestr(name, source)


def _restored(n, rd):
    return {"id": n, "bot_username": f"r{n}bot", "db_path": str(rd / f"r{n}.db")}


# Case 1
def test_create_backup_missing_db_returns_none(tmp_path):
    bk = tmp_path / "bk"
    none = tmp_path / "none.db"
    assert backup.create_backup(str(none), str(bk)) is None
    assert not bk.exists()
    assert not none.exists()


# Case 2
def test_create_backup_copies_uncommitted_wal_pages(tmp_path, frozen):
    db = _main(tmp_path / "main.db", "Live")
    try:
        assert (tmp_path / "main.db-wal").stat().st_size > 0
        ret = backup.create_backup(db.db_path, str(tmp_path / "bk"))
        assert ret == str(tmp_path / "bk" / f"main_{TS}.db")
        assert _value(ret) == "Live"
        assert db.get_setting("shop_name") == "Live"
    finally:
        db.close()


# Case 3
def test_create_backup_retention_by_name_sort(tmp_path, frozen):
    db = _main(tmp_path / "main.db")
    bk = tmp_path / "bk"
    bk.mkdir()
    try:
        for name in ("main_20250101_000000.db", "main_20250201_000000.db", "other_20250101_000000.db", "main.db.bak"):
            (bk / name).write_text("x")
        backup.create_backup(db.db_path, str(bk), keep=2)
        assert sorted(os.listdir(bk)) == ["main.db.bak", "main_20250201_000000.db", f"main_{TS}.db", "other_20250101_000000.db"]
    finally:
        db.close()


# Case 4
def test_create_backup_can_delete_its_own_backup(tmp_path, frozen):
    db = _main(tmp_path / "main.db")
    bk = tmp_path / "bk"
    bk.mkdir()
    (bk / "main_zzz.db").write_text("x")
    try:
        ret = backup.create_backup(db.db_path, str(bk), keep=1)
        assert ret == str(bk / f"main_{TS}.db")
        assert not os.path.exists(ret)
        assert os.listdir(bk) == ["main_zzz.db"]
    finally:
        db.close()


# Case 5
def test_create_backup_same_second_overwrites(tmp_path, frozen):
    db = _main(tmp_path / "main.db", "First")
    bk = tmp_path / "bk"
    try:
        r1 = backup.create_backup(db.db_path, str(bk))
        db.set_setting("shop_name", "Second")
        r2 = backup.create_backup(db.db_path, str(bk))
        assert r1 == r2
        assert os.listdir(bk) == [f"main_{TS}.db"]
        assert _value(r2) == "Second"
    finally:
        db.close()


# Case 6
def test_safe_copy_replaces_destination_content(tmp_path):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    _make_db(a, "A")
    conn = sqlite3.connect(str(b))
    try:
        conn.execute("CREATE TABLE other (y)")
        conn.commit()
    finally:
        conn.close()
    backup._sqlite_safe_copy(str(a), str(b))
    assert _tables(b) == {"settings"}
    assert _value(b) == "A"


# Case 7
def test_safe_copy_missing_source_creates_empty_file(tmp_path):
    src, dst = tmp_path / "nope.db", tmp_path / "dst.db"
    backup._sqlite_safe_copy(str(src), str(dst))
    assert src.exists() and src.stat().st_size == 0
    assert dst.exists()
    assert _tables(dst) == set()


# Case 8
def test_create_full_backup_missing_main_returns_none(tmp_path):
    out = tmp_path / "out"
    assert backup.create_full_backup(None, str(tmp_path / "none.db"), str(out)) is None
    assert not out.exists()


# Case 9
def test_create_full_backup_archive_and_manifest(tmp_path, frozen, caplog):
    caplog.set_level(logging.ERROR, logger="backup")
    main = _main(tmp_path / "main.db")
    rd, out = tmp_path / "reseller_dbs", tmp_path / "out"
    rd.mkdir()
    try:
        _reseller(main, 1, rd / "r1.db"); _make_db(rd / "r1.db", "R1")
        _reseller(main, 2, rd / "r2.db"); _make_db(rd / "r2.db", "R2"); main.toggle_reseller_bot(2)
        _reseller(main, 3, rd / "r3.db")
        _reseller(main, 4, rd / "r4.db"); (rd / "r4.db").write_bytes(NOT_SQLITE)
        ret = backup.create_full_backup(main, main.db_path, str(out))
        assert ret == str(out / f"full_backup_{TS}.zip")
        assert os.listdir(out) == [f"full_backup_{TS}.zip"]
        with zipfile.ZipFile(ret) as zf:
            assert sorted(zf.namelist()) == ["main_bot.db", "manifest.txt", "reseller_1.db", "reseller_2.db", "reseller_4.db"]
            assert zf.getinfo("reseller_4.db").file_size == 0
            zf.extractall(tmp_path / "x")
            x = tmp_path / "x"
            assert _value(x / "reseller_1.db") == "R1"
            assert _value(x / "reseller_2.db") == "R2"
            conn = sqlite3.connect(str(x / "main_bot.db"))
            try:
                assert conn.execute("SELECT id FROM reseller_bots ORDER BY id").fetchall() == [(1,), (2,), (3,), (4,)]
            finally:
                conn.close()
            expected = "\n".join([MANIFEST_HEADER, MANIFEST_DATE, "", f"main_bot.db  <-  {main.db_path}", f"reseller_1.db  <-  {rd / 'r1.db'}  (owner_id=5001, {ACTIVE})", f"reseller_2.db  <-  {rd / 'r2.db'}  (owner_id=5002, {INACTIVE})", f"{FILE_MISSING}  <-  {rd / 'r3.db'}  (owner_id=5003)", f"reseller_4.db  <-  {rd / 'r4.db'}  {COPY_FAILED}"])
            assert zf.read("manifest.txt").decode("utf-8") == expected
        records = [r for r in caplog.records if r.name == "backup" and r.levelno == logging.ERROR]
        assert len(records) == 1 and records[0].args == (str(rd / "r4.db"),)
    finally:
        main.close()


# Case 10
def test_create_full_backup_has_no_coherent_cut(tmp_path, frozen, monkeypatch):
    main = _main(tmp_path / "main.db")
    rd, out = tmp_path / "reseller_dbs", tmp_path / "out"
    rd.mkdir()
    try:
        _reseller(main, 1, rd / "r1.db"); _make_db(rd / "r1.db", "R1")
        real = main.list_reseller_bots
        called = False
        def late(active_only=False):
            nonlocal called
            if not called:
                called = True
                _reseller(main, 5, rd / "r5.db"); _make_db(rd / "r5.db", "R5")
            return real(active_only=active_only)
        monkeypatch.setattr(main, "list_reseller_bots", late)
        ret = backup.create_full_backup(main, main.db_path, str(out))
        with zipfile.ZipFile(ret) as zf:
            assert "reseller_2.db" in zf.namelist()
            zf.extractall(tmp_path / "x")
            assert _value(tmp_path / "x" / "reseller_2.db") == "R5"
            conn = sqlite3.connect(str(tmp_path / "x" / "main_bot.db"))
            try:
                assert conn.execute("SELECT id FROM reseller_bots ORDER BY id").fetchall() == [(1,)]
            finally:
                conn.close()
            assert zf.read("manifest.txt").decode("utf-8").splitlines()[-1] == f"reseller_2.db  <-  {rd / 'r5.db'}  (owner_id=5005, {ACTIVE})"
    finally:
        main.close()


# Case 11
def test_create_full_backup_retention_by_name_sort(tmp_path, frozen):
    main = _main(tmp_path / "main.db")
    out = tmp_path / "out"
    out.mkdir()
    try:
        for name in ("full_backup_20250101_000000.zip", "full_backup_20250201_000000.zip", "full_backup_zzz.zip"):
            (out / name).write_text("x")
        ret = backup.create_full_backup(main, main.db_path, str(out), keep=2)
        assert sorted(os.listdir(out)) == [f"full_backup_{TS}.zip", "full_backup_zzz.zip"]
        assert os.path.exists(ret)
    finally:
        main.close()


# Case 12
def test_create_full_backup_failure_leaves_empty_output_dir(tmp_path, frozen):
    main = _main(tmp_path / "main.db")
    bad, out = tmp_path / "bad.db", tmp_path / "out"
    bad.write_bytes(NOT_SQLITE)
    try:
        with pytest.raises(sqlite3.DatabaseError, match="file is not a database"):
            backup.create_full_backup(main, str(bad), str(out))
        assert os.listdir(out) == []
    finally:
        main.close()


# Case 13
def test_is_valid_sqlite_db_is_shallow(tmp_path):
    missing, header, bad, padded, user_version, made = [tmp_path / n for n in ("missing", "header", "bad", "padded", "user_version", "made")]
    header.write_bytes(SQLITE_HEADER); bad.write_bytes(NOT_SQLITE); padded.write_bytes(SQLITE_HEADER + b"\x00" * 200)
    conn = sqlite3.connect(str(user_version))
    try:
        conn.execute("PRAGMA user_version = 1")
    finally:
        conn.close()
    _make_db(made, "x")
    assert not backup.is_valid_sqlite_db(str(missing))
    assert not backup.is_valid_sqlite_db(str(header))
    assert not backup.is_valid_sqlite_db(str(bad))
    assert not backup.is_valid_sqlite_db(str(padded))
    assert backup.is_valid_sqlite_db(str(user_version))
    assert backup.is_valid_sqlite_db(str(made))


# Case 14
def test_restore_backup_rejects_invalid_upload(tmp_path):
    db = _main(tmp_path / "main.db", "Live")
    upload = tmp_path / "upload.db"
    upload.write_bytes(SQLITE_HEADER)
    try:
        with pytest.raises(ValueError) as exc:
            backup.restore_backup(db, db.db_path, str(upload))
        assert str(exc.value) == UPLOAD_INVALID
        assert not (tmp_path / "backups").exists()
        assert db.get_setting("shop_name") == "Live"
    finally:
        db.close()


# Case 15
def test_restore_backup_ignores_db_path_and_schema(tmp_path, frozen):
    db = _main(tmp_path / "main.db")
    notes = tmp_path / "notes.db"
    conn = sqlite3.connect(str(notes))
    try:
        conn.execute("CREATE TABLE notes (x)")
    finally:
        conn.close()
    try:
        ret = backup.restore_backup(db, str(tmp_path / "elsewhere.db"), str(notes))
        assert ret == str(tmp_path / "backups" / f"pre_restore_{TS}.db")
        assert not (tmp_path / "elsewhere.db").exists()
        assert _tables(tmp_path / "main.db") == {"notes"}
        assert "settings" in _tables(ret)
    finally:
        db.close()


# Case 16
def test_restore_full_backup_both_archive_names(tmp_path, frozen):
    main_live = _main(tmp_path / "main.db", "LiveMain")
    rd = tmp_path / "reseller_dbs"; rd.mkdir()
    for n, v in ((1, "R1Live"), (2, "R2Live"), (3, "R3Live")):
        _make_db(rd / f"r{n}.db", v)
    src = tmp_path / "src"; src.mkdir()
    archived = _main(src / "main.db", "ArchivedMain")
    try:
        for n in (1, 2, 3): _reseller(archived, n, rd / f"r{n}.db")
        archived.close()
        _make_db(src / "r1.db", "R1Archived"); _make_db(src / "r2_plain.db", "R2Plain"); _make_db(src / "r2_level.db", "R2Level")
        z = tmp_path / "full.zip"
        _zip(z, {"main_bot.db": src / "main.db", "reseller_1.db": src / "r1.db", "reseller_2.db": src / "r2_plain.db", "reseller_2_level2.db": src / "r2_level.db", "manifest.txt": b"m"})
        result = backup.restore_full_backup(main_live, main_live.db_path, str(z))
        assert result == {"main_restored": True, "main_pre_restore_path": str(tmp_path / "backups" / f"pre_restore_{TS}.db"), "resellers_restored": [_restored(1, rd), _restored(2, rd), _restored(2, rd)], "resellers_skipped": []}
        assert main_live.get_setting("shop_name") == "ArchivedMain"
        assert _value(rd / "r1.db") == "R1Archived"
        assert _value(rd / "r2.db") == "R2Level"
        assert _value(rd / "r3.db") == "R3Live"
        assert _value(result["main_pre_restore_path"]) == "LiveMain"
        assert os.listdir(rd / "backups") == [f"pre_restore_{TS}.db"]
        assert _value(rd / "backups" / f"pre_restore_{TS}.db") == "R2Plain"
        assert not os.path.exists(str(z) + "_extract")
    finally:
        archived.close(); main_live.close()


# Case 17
def test_restore_full_backup_replaces_main_before_tenant_checks(tmp_path, frozen, caplog):
    caplog.set_level(logging.ERROR, logger="backup")
    live = _main(tmp_path / "main.db", "LiveMain")
    rd = tmp_path / "reseller_dbs"; rd.mkdir()
    _make_db(rd / "r1.db", "R1Live")
    afile = tmp_path / "afile"; afile.write_text("x")
    src = tmp_path / "src"; src.mkdir()
    archived = _main(src / "main.db", "ArchivedMain")
    try:
        _reseller(archived, 1, rd / "r1.db"); _reseller(archived, 2, afile / "r2.db")
        archived.close()
        _make_db(src / "r2.db", "R2Archived"); _make_db(src / "r9.db", "R9")
        z = tmp_path / "full.zip"
        _zip(z, {"main_bot.db": src / "main.db", "reseller_1.db": NOT_SQLITE, "reseller_2.db": src / "r2.db", "reseller_9.db": src / "r9.db", "reseller_x.db": b"zz"})
        result = backup.restore_full_backup(live, live.db_path, str(z))
        assert result["main_restored"] is True
        assert result["resellers_restored"] == []
        assert result["resellers_skipped"] == [{"file": "reseller_1.db", "reason": INVALID_SQLITE}, {"file": "reseller_2.db", "reason": REPLACE_FAILED}, {"file": "reseller_9.db", "reason": unknown_id(9)}, {"file": "reseller_x.db", "reason": BAD_NAME}]
        assert live.get_setting("shop_name") == "ArchivedMain"
        assert _value(rd / "r1.db") == "R1Live"
        records = [r for r in caplog.records if r.name == "backup" and r.levelno == logging.ERROR]
        assert len(records) == 1 and records[0].args == (2, str(afile / "r2.db"))
    finally:
        archived.close(); live.close()


# Case 18
def test_restore_full_backup_invalid_main_changes_nothing(tmp_path, frozen):
    live = _main(tmp_path / "main.db", "LiveMain")
    rd = tmp_path / "reseller_dbs"; rd.mkdir(); _make_db(rd / "r1.db", "R1Live")
    src = tmp_path / "src"; src.mkdir(); _make_db(src / "r1.db", "R1Archived")
    try:
        for i, members in enumerate(({"main_bot.db": NOT_SQLITE, "reseller_1.db": src / "r1.db"}, {"reseller_1.db": src / "r1.db"})):
            z = tmp_path / f"bad{i}.zip"; _zip(z, members)
            with pytest.raises(ValueError) as exc:
                backup.restore_full_backup(live, live.db_path, str(z))
            assert str(exc.value) == MAIN_INVALID
            assert live.get_setting("shop_name") == "LiveMain"
            assert _value(rd / "r1.db") == "R1Live"
            assert not (tmp_path / "backups").exists()
            assert not (rd / "backups").exists()
            assert not os.path.exists(str(z) + "_extract")
    finally:
        live.close()


# Case 19
def test_sftp_kwargs_never_verify_host_key(tmp_path):
    key = tmp_path / "id_synthetic"; key.write_text("synthetic")
    assert backup._build_sftp_connect_kwargs("backup.example.invalid", 0, "backup-user", password="synthetic-pass") == {"host": "backup.example.invalid", "port": 22, "username": "backup-user", "known_hosts": None, "password": "synthetic-pass"}
    assert backup._build_sftp_connect_kwargs("backup.example.invalid", 2222, "backup-user", password="synthetic-pass", key_path=str(key)) == {"host": "backup.example.invalid", "port": 2222, "username": "backup-user", "known_hosts": None, "client_keys": [str(key)], "password": "synthetic-pass"}
    assert backup._build_sftp_connect_kwargs("backup.example.invalid", 22, "backup-user", key_path=str(key)) == {"host": "backup.example.invalid", "port": 22, "username": "backup-user", "known_hosts": None, "client_keys": [str(key)]}


# Case 20
def test_sftp_kwargs_validation(tmp_path):
    with pytest.raises(ValueError) as exc: backup._build_sftp_connect_kwargs("", 22, "user", password="p")
    assert str(exc.value) == SFTP_EMPTY
    with pytest.raises(ValueError) as exc: backup._build_sftp_connect_kwargs("host", 22, "", password="p")
    assert str(exc.value) == SFTP_EMPTY
    with pytest.raises(ValueError) as exc: backup._build_sftp_connect_kwargs("host", 22, "user")
    assert str(exc.value) == SFTP_NO_AUTH
    with pytest.raises(ValueError) as exc: backup._build_sftp_connect_kwargs("host", 22, "user", password="", key_path="")
    assert str(exc.value) == SFTP_NO_AUTH
    missing = tmp_path / "missing_key"
    with pytest.raises(ValueError) as exc: backup._build_sftp_connect_kwargs("host", 22, "user", key_path=str(missing))
    assert str(exc.value) == key_missing(str(missing))


# Case 21
def test_telegram_full_restore_stops_listed_running_resellers_first(tmp_path, frozen, uploads):
    rd = tmp_path / "reseller_dbs"; rd.mkdir()
    src = tmp_path / "src"; src.mkdir()
    live = _main(tmp_path / "main.db", "LiveMain")
    archived = _main(src / "main.db", "ArchivedMain")
    try:
        for n in (1, 2, 3):
            path = rd / f"r{n}.db"
            _reseller(live, n, path); _make_db(path, f"R{n}Live")
            _reseller(archived, n, path)
        archived.close()
        _make_db(src / "r1.db", "R1Archived"); _make_db(src / "r2.db", "R2Archived")
        z = _staged(uploads, "restore_full_x", "uploaded.zip")
        _zip(z, {"main_bot.db": src / "main.db", "reseller_1.db": src / "r1.db", "reseller_2_level2.db": src / "r2.db", "reseller_x.db": b"zz", "reseller_9.db": src / "r1.db"})
        bm = _BotManager(live, {"1001:synthetic-r1", "1003:synthetic-r3"})
        router = handlers_admin.create_admin_router(live, is_main_bot=True, bot_manager=bm)
        handler = find_handler(router, "callback_query", "cb_restore_full_confirm")
        state = asyncio.run(_state(AdminRestoreFullBackup.waiting_confirm, restore_full_tmp_path=str(z)))
        log = TelegramLog()
        assert asyncio.run(_press(handler, log, OWNER, "adm_restore_full_confirm", state)) is None
        assert asyncio.run(state.get_state()) is None and asyncio.run(state.get_data()) == {}
        assert log.events == [_edit(FULL_WORKING), _edit("\n".join([FULL_MAIN_DONE, full_restored(2), "  • @r1bot", "  • @r2bot", full_skipped(2), f"  • reseller_9.db: {unknown_id(9)}", f"  • reseller_x.db: {BAD_NAME}", stopped_note(1)])), _answer()]
        assert bm.calls == [("is_running", "1001:synthetic-r1"), ("stop_bot", "1001:synthetic-r1", "LiveMain"), ("is_running", "1002:synthetic-r2")]
        assert bm.running == {"1003:synthetic-r3"}
        assert live.get_setting("shop_name") == "ArchivedMain"
        assert [_value(rd / f"r{n}.db") for n in (1, 2, 3)] == ["R1Archived", "R2Archived", "R3Live"]
        assert os.listdir(uploads) == []
        assert _admin_logs(tmp_path / "main.db") == [(OWNER, "backup_full_restore", full_log(2, 2), None, None)]
    finally:
        archived.close(); live.close()


# Case 22
def test_telegram_full_restore_failure_leaves_bots_stopped(tmp_path, frozen, uploads):
    rd = tmp_path / "reseller_dbs"; rd.mkdir()
    src = tmp_path / "src"; src.mkdir()
    live = _main(tmp_path / "main.db", "LiveMain")
    try:
        _reseller(live, 1, rd / "r1.db"); _make_db(rd / "r1.db", "R1Live")
        _make_db(src / "r1.db", "R1Archived")
        z = _staged(uploads, "restore_full_x", "uploaded.zip")
        _zip(z, {"main_bot.db": NOT_SQLITE, "reseller_1.db": src / "r1.db"})
        bm = _BotManager(live, {"1001:synthetic-r1"})
        router = handlers_admin.create_admin_router(live, is_main_bot=True, bot_manager=bm)
        handler = find_handler(router, "callback_query", "cb_restore_full_confirm")
        state = asyncio.run(_state(AdminRestoreFullBackup.waiting_confirm, restore_full_tmp_path=str(z)))
        log = TelegramLog()
        asyncio.run(_press(handler, log, OWNER, "adm_restore_full_confirm", state))
        assert log.events == [_edit(FULL_WORKING), _edit(FULL_FAILED + MAIN_INVALID)]
        assert bm.calls == [("is_running", "1001:synthetic-r1"), ("stop_bot", "1001:synthetic-r1", "LiveMain")]
        assert bm.running == set()
        assert live.get_setting("shop_name") == "LiveMain" and _value(rd / "r1.db") == "R1Live"
        assert os.listdir(uploads) == [] and _admin_logs(tmp_path / "main.db") == []
    finally:
        live.close()


# Case 23
def test_telegram_full_restore_guards(tmp_path, uploads):
    live = _main(tmp_path / "main.db", "LiveMain")
    bm = _BotManager(live, set())
    try:
        router = handlers_admin.create_admin_router(live, is_main_bot=True, bot_manager=bm)
        handler = find_handler(router, "callback_query", "cb_restore_full_confirm")
        log = TelegramLog(); state = asyncio.run(_state(AdminRestoreFullBackup.waiting_confirm, restore_full_tmp_path=str(uploads / "gone" / "uploaded.zip")))
        asyncio.run(_press(handler, log, OWNER, "adm_restore_full_confirm", state))
        assert log.events == [_edit(TMP_MISSING)] and asyncio.run(state.get_state()) is None
        log = TelegramLog(); state = asyncio.run(_state(AdminRestoreFullBackup.waiting_confirm, restore_full_tmp_path="x"))
        asyncio.run(_press(handler, log, NON_OWNER, "adm_restore_full_confirm", state))
        assert log.events == [_answer(DENY, alert=True)]
        assert asyncio.run(state.get_state()) == AdminRestoreFullBackup.waiting_confirm.state
        assert asyncio.run(state.get_data()) == {"restore_full_tmp_path": "x"}
        router = handlers_admin.create_admin_router(live, is_main_bot=False, bot_manager=bm)
        handler = find_handler(router, "callback_query", "cb_restore_full_confirm")
        log = TelegramLog(); state = asyncio.run(_state(AdminRestoreFullBackup.waiting_confirm, restore_full_tmp_path="x"))
        asyncio.run(_press(handler, log, OWNER, "adm_restore_full_confirm", state))
        assert log.events == [_answer(DENY, alert=True)]
        assert asyncio.run(state.get_state()) == AdminRestoreFullBackup.waiting_confirm.state
        assert asyncio.run(state.get_data()) == {"restore_full_tmp_path": "x"}
        assert bm.calls == []
    finally:
        live.close()


# Case 24
def test_telegram_full_upload_checks_only_names(tmp_path, uploads):
    live = _main(tmp_path / "main.db", "LiveMain")
    try:
        router = handlers_admin.create_admin_router(live, is_main_bot=True)
        handler = find_handler(router, "message", "on_restore_full_file")
        a = tmp_path / "a.zip"; _zip(a, {"main_bot.db": b"x", "reseller_1.db": b"x", "reseller_2_level2.db": b"x", "reseller_x.db": b"x", "manifest.txt": b"m"})
        b = tmp_path / "b.zip"; _zip(b, {"reseller_1.db": b"x"})
        log = TelegramLog(); bot = _UploadBot(log, {"a": a, "b": b})
        state = asyncio.run(_state(AdminRestoreFullBackup.waiting_file))
        asyncio.run(handler(_upload(log, bot, "a", "full.db"), state))
        event = log.events[-1]
        assert (event.kind, event.chat_id, event.text) == ("message_answer", OWNER, ZIP_ONLY)
        assert bot.downloads == [] and asyncio.run(state.get_state()) == AdminRestoreFullBackup.waiting_file.state
        asyncio.run(handler(_upload(log, bot, "b", "b.ZIP"), state))
        assert (log.events[-1].kind, log.events[-1].chat_id, log.events[-1].text) == ("message_answer", OWNER, ZIP_NO_MAIN)
        assert asyncio.run(state.get_state()) == AdminRestoreFullBackup.waiting_file.state and asyncio.run(state.get_data()) == {}
        asyncio.run(handler(_upload(log, bot, "a", "a.zip"), state))
        event = log.events[-1]
        assert (event.kind, event.chat_id, event.text) == ("message_answer", OWNER, full_received(3))
        assert callback_rows(event.reply_markup) == [["adm_restore_full_confirm"], ["adm_restore_full_cancel"]]
        assert asyncio.run(state.get_state()) == AdminRestoreFullBackup.waiting_confirm.state
        staged = pathlib.Path(asyncio.run(state.get_data())["restore_full_tmp_path"])
        assert staged.exists() and staged.name == "uploaded.zip" and staged.parent.name.startswith("restore_full_")
        assert bot.downloads == ["b", "a"]
        folders = list(uploads.iterdir())
        assert len(folders) == 2 and all(p.name.startswith("restore_full_") and [x.name for x in p.iterdir()] == ["uploaded.zip"] for p in folders)
    finally:
        live.close()


# Case 25
def test_telegram_single_restore_replaces_router_db(tmp_path, frozen, uploads):
    live = _main(tmp_path / "shop.db", "LiveShop")
    src = tmp_path / "src"; src.mkdir(); archived = _main(src / "shop.db", "ArchivedShop")
    archived.close()
    try:
        u = _staged(uploads, "restore_x", "uploaded.db"); shutil.copyfile(src / "shop.db", u)
        router = handlers_admin.create_admin_router(live, is_main_bot=False)
        handler = find_handler(router, "callback_query", "cb_restore_confirm")
        state = asyncio.run(_state(AdminRestoreBackup.waiting_confirm, restore_tmp_path=str(u)))
        log = TelegramLog(); asyncio.run(_press(handler, log, OWNER, "adm_restore_confirm", state))
        assert log.events == [_edit(SINGLE_WORKING), _edit(SINGLE_DONE), _answer()]
        assert asyncio.run(state.get_state()) is None and live.get_setting("shop_name") == "ArchivedShop"
        assert os.listdir(tmp_path / "backups") == [f"pre_restore_{TS}.db"]
        assert _value(tmp_path / "backups" / f"pre_restore_{TS}.db") == "LiveShop"
        assert os.listdir(uploads) == []
        assert _admin_logs(tmp_path / "shop.db") == [(OWNER, "backup_restore", SINGLE_LOG, None, None)]
    finally:
        archived.close(); live.close()


# Case 26
def test_telegram_single_restore_foreign_schema_crashes_after_replacing(tmp_path, frozen, uploads):
    live = _main(tmp_path / "shop.db", "LiveShop")
    try:
        u = _staged(uploads, "restore_x", "uploaded.db")
        conn = sqlite3.connect(str(u))
        try:
            conn.execute("CREATE TABLE notes (x)"); conn.commit()
        finally:
            conn.close()
        router = handlers_admin.create_admin_router(live, is_main_bot=True)
        handler = find_handler(router, "callback_query", "cb_restore_confirm")
        state = asyncio.run(_state(AdminRestoreBackup.waiting_confirm, restore_tmp_path=str(u)))
        log = TelegramLog()
        with pytest.raises(sqlite3.OperationalError, match="no such table: admin_logs"):
            asyncio.run(_press(handler, log, OWNER, "adm_restore_confirm", state))
        assert log.events == [_edit(SINGLE_WORKING)]
        assert _tables(tmp_path / "shop.db") == {"notes"}
        assert (tmp_path / "backups" / f"pre_restore_{TS}.db").exists()
        assert os.listdir(uploads) == []
    finally:
        live.close()


# Case 27
def test_telegram_single_restore_rejections(tmp_path, uploads):
    live = _main(tmp_path / "shop.db", "LiveShop")
    try:
        router = handlers_admin.create_admin_router(live, is_main_bot=True)
        handler = find_handler(router, "callback_query", "cb_restore_confirm")
        u = _staged(uploads, "restore_x", "uploaded.db"); u.write_bytes(SQLITE_HEADER)
        state = asyncio.run(_state(AdminRestoreBackup.waiting_confirm, restore_tmp_path=str(u)))
        log = TelegramLog(); asyncio.run(_press(handler, log, OWNER, "adm_restore_confirm", state))
        assert log.events == [_edit(SINGLE_WORKING), _edit(SINGLE_FAILED + UPLOAD_INVALID)]
        assert os.listdir(uploads) == [] and live.get_setting("shop_name") == "LiveShop"
        assert not (tmp_path / "backups").exists()
        log = TelegramLog(); h = tmp_path / "header.db"; h.write_bytes(SQLITE_HEADER)
        bot = _UploadBot(log, {"h": h}); state = asyncio.run(_state(AdminRestoreBackup.waiting_file))
        file_handler = find_handler(router, "message", "on_restore_file")
        asyncio.run(file_handler(_upload(log, bot, "h", "x.db"), state))
        assert (log.events[-1].kind, log.events[-1].text) == ("message_answer", UPLOAD_NOT_SQLITE)
        assert asyncio.run(state.get_state()) == AdminRestoreBackup.waiting_file.state and asyncio.run(state.get_data()) == {}
        folders = list(uploads.iterdir())
        assert len(folders) == 1 and folders[0].name.startswith("restore_") and [x.name for x in folders[0].iterdir()] == ["uploaded.db"]
    finally:
        live.close()


# Case 28
def test_web_restore_refusals(web, tmp_path, uploads):
    src = tmp_path / "src"; src.mkdir(); archived = _main(src / "main.db", "ArchivedMain"); archived.close()
    good = (src / "main.db").read_bytes()
    cases = [
        (WEB_MID, "a.db", good, "RESTORE", 403, WEB_OWNER_ONLY),
        (WEB_OWNER, "a.db", good, "restore x", 400, WEB_PHRASE),
        (WEB_OWNER, "a.zip", good, "RESTORE", 400, WEB_EXTENSION),
        (WEB_OWNER, "a.db", SQLITE_HEADER, "RESTORE", 400, WEB_NOT_SQLITE),
    ]
    for who, name, content, phrase, status, detail in cases:
        response = asyncio.run(_post_restore(web.panel, who, name, content, phrase))
        assert response.status_code == status and response.json() == {"detail": detail}
    assert web.live.get_setting("shop_name") == "LiveMain"
    assert not (tmp_path / "backups").exists() and os.listdir(uploads) == []


# Case 29
def test_web_restore_replaces_main_tenant(web, tmp_path, uploads, frozen):
    src = tmp_path / "src"; src.mkdir(); archived = _main(src / "main.db", "ArchivedMain"); archived.close()
    response = asyncio.run(_post_restore(web.panel, WEB_OWNER, "a.SQLITE3", (src / "main.db").read_bytes(), " restore "))
    assert response.status_code == 200 and response.json() == {"ok": True, "pre_restore_backup": f"pre_restore_{TS}.db"}
    assert web.live.get_setting("shop_name") == "ArchivedMain"
    assert _value(tmp_path / "backups" / f"pre_restore_{TS}.db") == "LiveMain"
    assert _admin_logs(tmp_path / "main.db") == [(1, "backup_restore", web_log(f"pre_restore_{TS}.db"), None, None)]
    assert os.listdir(uploads) == []


# Case 30
def test_manage_sh_restore_restores_main_only():
    text = MANAGE_SH.read_text(encoding="utf-8")
    start = text.index("restore_backup_cli() {\n")
    end = text.index("\n}\n", start) + 3
    body = text[start:end]
    parts = [
        'from backup import is_valid_sqlite_db',
        'sys.exit(0 if is_valid_sqlite_db(sys.argv[1]) else 1)',
        '[ "$CONFIRM" != "yes" ]',
        'sudo systemctl stop "$SERVICE_NAME"',
        "db = Database('bot_database.db')",
        "pre = restore_backup(db, 'bot_database.db', sys.argv[1])",
        'if [[ "$RESTORE_OUT" != OK:* ]]; then',
        'sudo systemctl start "$SERVICE_NAME"',
    ]
    position = 0
    for part in parts:
        found = body.index(part, position)
        position = found + len(part)
    assert all(word not in body for word in ("reseller", "restore_full_backup", "create_backup"))
