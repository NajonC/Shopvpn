"""Characterize backup and restore in ``backup.py`` at commit 1f2f399.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_backup_restore.py --network=deny``.
Every file is under ``tmp_path``; reseller databases sit in ``reseller_dbs`` as in
production; the restore callers are characterized in a later part.

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
(g) SFTP never verifies the host key, ``known_hosts=None`` (case 19).
"""

import datetime
import logging
import os
import pathlib
import sqlite3
import zipfile

import pytest

import backup
import database


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
