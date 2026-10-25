"""Integration tests for the network guard pytest plugin."""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(pytester, monkeypatch, source, *args):
    monkeypatch.setenv("PYTHONPATH", str(REPO_ROOT))
    pytester.makeconftest('pytest_plugins = ["tests._harness.network_guard"]\n')
    pytester.makepyfile(test_inner=source)
    return pytester.runpytest_subprocess(*args)


def test_deny_option_accepted(pytester, monkeypatch):
    source = """
def test_ok():
    pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    assert result.ret == 0
    result.assert_outcomes(passed=1)


def test_guard_on_without_option(pytester, monkeypatch):
    source = """
import socket

def test_connect():
    socket.create_connection(("192.0.2.1", 9), timeout=1)
"""
    result = _run(pytester, monkeypatch, source)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: connect to 192.0.2.1:9 is not loopback*"])


def test_other_network_value_rejected(pytester, monkeypatch):
    source = """
def test_ok():
    pass
"""
    result = _run(pytester, monkeypatch, source, "--network=allow")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*invalid choice: 'allow'*"])


def test_loopback_tcp_allowed(pytester, monkeypatch):
    source = """
import socket

def test_loopback():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect(("127.0.0.1", port))
    conn, _ = server.accept()
    client1.sendall(b"ok")
    data = conn.recv(1024)
    assert data == b"ok"
    conn.close()
    client1.close()

    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect(("localhost", port))
    conn2, _ = server.accept()
    conn2.close()
    client2.close()
    server.close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    assert result.ret == 0
    result.assert_outcomes(passed=1)


def test_external_connect_fails_even_when_caught(pytester, monkeypatch):
    source = """
import socket

def test_caught():
    try:
        socket.create_connection(("192.0.2.1", 9), timeout=1)
    except Exception:
        pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: connect to 192.0.2.1:9 is not loopback*"])


def test_external_ipv6_connect_fails(pytester, monkeypatch):
    source = """
import socket

def test_ipv6():
    try:
        s = socket.socket(socket.AF_INET6)
        s.connect(("2001:db8::1", 9))
    except Exception:
        pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: connect to 2001:db8::1:9 is not loopback*"])


def test_host_name_lookup_fails(pytester, monkeypatch):
    source = """
import socket

def test_dns():
    try:
        socket.getaddrinfo("example.invalid", 443)
    except Exception:
        pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: name lookup of example.invalid is not allowed*"])


def test_non_loopback_bind_fails(pytester, monkeypatch):
    source = """
import socket

def test_bind():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", 0))
    except Exception:
        pass
    finally:
        s.close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: bind to 0.0.0.0:0 is not loopback*"])


def test_udp_send_to_external_fails(pytester, monkeypatch):
    source = """
import socket

def test_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(b"x", ("192.0.2.1", 9))
    except Exception:
        pass
    finally:
        s.close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*network guard: send to 192.0.2.1:9 is not loopback*"])


def test_sqlite_in_lab_root_allowed(pytester, monkeypatch):
    source = """
import sqlite3

def test_sqlite(tmp_path):
    conn1 = sqlite3.connect(tmp_path / "lab.db")
    conn1.execute("CREATE TABLE t (id INT)")
    conn1.execute("INSERT INTO t VALUES (1)")
    conn1.commit()
    cur = conn1.execute("SELECT id FROM t")
    assert cur.fetchone() == (1,)
    conn1.close()

    conn2 = sqlite3.connect(str(tmp_path / "lab2.db"))
    conn2.close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(passed=1)


def test_sqlite_memory_allowed(pytester, monkeypatch):
    source = """
import sqlite3

def test_mem():
    sqlite3.connect(":memory:").close()
    sqlite3.connect("").close()
    sqlite3.connect("file::memory:", uri=True).close()
    sqlite3.connect("file:memdb1?mode=memory&cache=shared", uri=True).close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(passed=1)


def test_sqlite_outside_lab_root_fails(pytester, monkeypatch):
    source = """
import sqlite3

def test_outside():
    try:
        sqlite3.connect("bot_database.db")
    except Exception:
        pass
    try:
        sqlite3.connect(database="kw.db")
    except Exception:
        pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*network guard: database */bot_database.db is outside the lab root*",
        "*network guard: database */kw.db is outside the lab root*",
    ])
    assert not (pytester.path / "bot_database.db").exists()
    assert not (pytester.path / "kw.db").exists()


def test_sqlite_uri_outside_lab_root_fails(pytester, monkeypatch):
    source = """
import os
import sqlite3

def test_uri_outside():
    try:
        sqlite3.connect("file:" + os.path.abspath("outside.db") + "?mode=rwc", uri=True)
    except Exception:
        pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*network guard: database */outside.db is outside the lab root*",
    ])
    assert not (pytester.path / "outside.db").exists()


def test_unix_socket_paths(pytester, monkeypatch):
    source = """
import os
import socket

def test_inside(tmp_path, monkeypatch):
    # A relative name keeps the socket path under the 108-byte limit
    # however deep TMPDIR is; the guard resolves it inside tmp_path.
    monkeypatch.chdir(tmp_path)
    s = socket.socket(socket.AF_UNIX)
    try:
        s.bind("s")
    finally:
        s.close()
    assert (tmp_path / "s").exists()

def test_outside():
    s = socket.socket(socket.AF_UNIX)
    try:
        try:
            s.bind(os.path.abspath("svc.sock"))
        except Exception:
            pass
    finally:
        s.close()
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines([
        "*network guard: unix socket */svc.sock is outside the lab root*",
    ])


def test_violation_in_fixture_fails_setup(pytester, monkeypatch):
    source = """
import pytest
import socket

@pytest.fixture
def bad_fixture():
    try:
        socket.create_connection(("192.0.2.1", 9), timeout=1)
    except Exception:
        pass
    yield

def test_with_fixture(bad_fixture):
    pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines([
        "*network guard: connect to 192.0.2.1:9 is not loopback*",
    ])


def test_violation_at_import_fails_run(pytester, monkeypatch):
    source = """
import socket

try:
    socket.create_connection(("192.0.2.1", 9), timeout=1)
except Exception:
    pass

def test_ok():
    pass
"""
    result = _run(pytester, monkeypatch, source, "--network=deny")
    result.assert_outcomes(passed=1)
    assert result.ret == 1
    result.stdout.fnmatch_lines([
        "*= network guard =*",
        "*network guard: connect to 192.0.2.1:9 is not loopback*",
    ])
