"""Network denial pytest plugin for offline tests.

This plugin ensures offline tests remain isolated from external network services
and unauthorized local resources.

Coverage:
- Blocks network sockets to any non-loopback address (IPv4 and IPv6).
- Blocks host-name DNS lookups for anything other than localhost and IP literals.
- Blocks SQLite database connections outside pytest's temporary directory (lab root).
- Blocks UNIX sockets outside the lab root (including abstract sockets).

Limitations:
- Child processes started by a test are not guarded.
- C extensions with their own socket implementations are not guarded.
- sendmsg is not guarded.
"""

import ipaddress
import os
import socket
import sqlite3
from typing import Any
import urllib.parse

import pytest


class NetworkGuardError(RuntimeError):
    """Raised when a test reaches for the network or a database outside the lab root."""


class _NetworkGuardState:
    def __init__(self) -> None:
        self.installed: bool = False
        self.lab_roots: set[str] = set()
        self.current_phase_messages: list[str] | None = None
        self.outside_messages: list[str] = []
        self.saved_originals: dict[str, Any] = {}

    def install(self) -> None:
        if self.installed:
            return
        self.saved_originals = {
            "socket_connect": socket.socket.connect,
            "socket_connect_ex": socket.socket.connect_ex,
            "socket_bind": socket.socket.bind,
            "socket_sendto": socket.socket.sendto,
            "getaddrinfo": socket.getaddrinfo,
            "gethostbyname": socket.gethostbyname,
            "gethostbyname_ex": socket.gethostbyname_ex,
            "sqlite3_connect": sqlite3.connect,
        }
        socket.socket.connect = _guarded_socket_connect
        socket.socket.connect_ex = _guarded_socket_connect_ex
        socket.socket.bind = _guarded_socket_bind
        socket.socket.sendto = _guarded_socket_sendto
        socket.getaddrinfo = _guarded_getaddrinfo
        socket.gethostbyname = _guarded_gethostbyname
        socket.gethostbyname_ex = _guarded_gethostbyname_ex
        sqlite3.connect = _guarded_sqlite3_connect
        self.installed = True

    def uninstall(self) -> None:
        if not self.installed:
            return
        socket.socket.connect = self.saved_originals["socket_connect"]
        socket.socket.connect_ex = self.saved_originals["socket_connect_ex"]
        socket.socket.bind = self.saved_originals["socket_bind"]
        socket.socket.sendto = self.saved_originals["socket_sendto"]
        socket.getaddrinfo = self.saved_originals["getaddrinfo"]
        socket.gethostbyname = self.saved_originals["gethostbyname"]
        socket.gethostbyname_ex = self.saved_originals["gethostbyname_ex"]
        sqlite3.connect = self.saved_originals["sqlite3_connect"]
        self.saved_originals.clear()
        self.lab_roots.clear()
        self.current_phase_messages = None
        self.outside_messages.clear()
        self.installed = False

    def record(self, message: str) -> None:
        if self.current_phase_messages is not None:
            self.current_phase_messages.append(message)
        else:
            self.outside_messages.append(message)

    def begin_phase(self) -> None:
        self.current_phase_messages = []

    def end_phase(self) -> list[str]:
        messages = self.current_phase_messages or []
        self.current_phase_messages = None
        return messages


_state = _NetworkGuardState()


def _deny(message: str) -> None:
    _state.record(message)
    raise NetworkGuardError(message)


def _is_loopback(host: Any) -> bool:
    if isinstance(host, bytes):
        try:
            host = host.decode("ascii")
        except UnicodeDecodeError:
            return False
    if not isinstance(host, str):
        return False
    if host.lower() == "localhost":
        return True
    ip_str = host.split("%", 1)[0]
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if ip.is_loopback:
        return True
    ipv4_mapped = getattr(ip, "ipv4_mapped", None)
    if ipv4_mapped is not None and ipv4_mapped.is_loopback:
        return True
    return False


def _is_inside_lab_root(path: str) -> bool:
    if not _state.lab_roots:
        return False
    real_path = os.path.realpath(path)
    for root in _state.lab_roots:
        try:
            if os.path.commonpath([root, real_path]) == root:
                return True
        except ValueError:
            continue
    return False


def _check_socket_address(sock: socket.socket, address: Any, action: str) -> None:
    family = sock.family
    if family in (socket.AF_INET, getattr(socket, "AF_INET6", -1)):
        host = address[0]
        port = address[1]
        if not _is_loopback(host):
            _deny(f"network guard: {action} to {host}:{port} is not loopback")
    elif family == getattr(socket, "AF_UNIX", -1):
        if hasattr(address, "__fspath__"):
            address = os.fspath(address)
        path = os.fsdecode(address)
        if not path or path.startswith("\0"):
            _deny("network guard: unix socket <abstract> is outside the lab root")
        else:
            real_path = os.path.realpath(path)
            if not _is_inside_lab_root(real_path):
                _deny(f"network guard: unix socket {real_path} is outside the lab root")
    else:
        family_name = getattr(family, "name", str(family))
        _deny(f"network guard: {action} on socket family {family_name} is not allowed")


def _is_allowed_name_lookup(host: Any) -> bool:
    if host is None:
        return True
    if isinstance(host, bytes):
        try:
            host = host.decode("ascii")
        except UnicodeDecodeError:
            return False
    if not isinstance(host, str):
        return False
    if host == "" or host.lower() == "localhost":
        return True
    ip_str = host.split("%", 1)[0]
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def _check_host_name(host: Any) -> None:
    if not _is_allowed_name_lookup(host):
        _deny(f"network guard: name lookup of {host} is not allowed")


def _check_sqlite_database(database: Any, uri: bool = False) -> None:
    if hasattr(database, "__fspath__"):
        database = os.fspath(database)
    if isinstance(database, bytes):
        database = os.fsdecode(database)

    if database in (":memory:", ""):
        return

    check_path = None
    if uri and isinstance(database, str) and database.startswith("file:"):
        uri_body = database[5:]
        uri_body = uri_body.split("#", 1)[0]
        if "?" in uri_body:
            path_part, query_part = uri_body.split("?", 1)
        else:
            path_part, query_part = uri_body, ""

        if path_part.startswith("//"):
            authority_and_path = path_part[2:]
            if "/" in authority_and_path:
                authority, rest = authority_and_path.split("/", 1)
                path_part = "/" + rest
            else:
                authority = authority_and_path
                path_part = ""
            if authority.lower() not in ("", "localhost"):
                raw_path_without_query = uri_body.split("?", 1)[0]
                _deny(f"network guard: database {raw_path_without_query} is outside the lab root")

        path_part = urllib.parse.unquote(path_part)
        query_params = urllib.parse.parse_qs(query_part)
        if path_part == ":memory:" or "memory" in query_params.get("mode", []):
            return
        check_path = path_part
    else:
        check_path = database

    real_path = os.path.realpath(check_path)
    if not _is_inside_lab_root(real_path):
        _deny(f"network guard: database {real_path} is outside the lab root")


def _guarded_socket_connect(self: socket.socket, *args: Any, **kwargs: Any) -> Any:
    address = args[0] if args else kwargs.get("address")
    _check_socket_address(self, address, action="connect")
    return _state.saved_originals["socket_connect"](self, *args, **kwargs)


def _guarded_socket_connect_ex(self: socket.socket, *args: Any, **kwargs: Any) -> Any:
    address = args[0] if args else kwargs.get("address")
    _check_socket_address(self, address, action="connect")
    return _state.saved_originals["socket_connect_ex"](self, *args, **kwargs)


def _guarded_socket_bind(self: socket.socket, *args: Any, **kwargs: Any) -> Any:
    address = args[0] if args else kwargs.get("address")
    _check_socket_address(self, address, action="bind")
    return _state.saved_originals["socket_bind"](self, *args, **kwargs)


def _guarded_socket_sendto(self: socket.socket, *args: Any, **kwargs: Any) -> Any:
    if len(args) >= 2:
        address = args[-1]
    elif "address" in kwargs:
        address = kwargs["address"]
    else:
        return _state.saved_originals["socket_sendto"](self, *args, **kwargs)
    _check_socket_address(self, address, action="send")
    return _state.saved_originals["socket_sendto"](self, *args, **kwargs)


def _guarded_getaddrinfo(*args: Any, **kwargs: Any) -> Any:
    host = args[0] if args else kwargs.get("host")
    _check_host_name(host)
    return _state.saved_originals["getaddrinfo"](*args, **kwargs)


def _guarded_gethostbyname(*args: Any, **kwargs: Any) -> Any:
    host = args[0] if args else kwargs.get("hostname", kwargs.get("host"))
    _check_host_name(host)
    return _state.saved_originals["gethostbyname"](*args, **kwargs)


def _guarded_gethostbyname_ex(*args: Any, **kwargs: Any) -> Any:
    host = args[0] if args else kwargs.get("hostname", kwargs.get("host"))
    _check_host_name(host)
    return _state.saved_originals["gethostbyname_ex"](*args, **kwargs)


def _guarded_sqlite3_connect(*args: Any, **kwargs: Any) -> Any:
    database = args[0] if args else kwargs.get("database")
    uri = False
    if "uri" in kwargs:
        uri = bool(kwargs["uri"])
    elif len(args) > 7:
        uri = bool(args[7])

    if database is not None:
        _check_sqlite_database(database, uri=uri)
    return _state.saved_originals["sqlite3_connect"](*args, **kwargs)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--network",
        action="store",
        choices=("deny",),
        default="deny",
        help="Network access policy (choices: deny)",
    )


def pytest_configure(config: pytest.Config) -> None:
    _state.install()


def pytest_unconfigure(config: pytest.Config) -> None:
    _state.uninstall()


@pytest.fixture(scope="session", autouse=True)
def _network_guard_lab_root(tmp_path_factory: pytest.TempPathFactory):
    root = os.path.realpath(str(tmp_path_factory.getbasetemp()))
    _state.lab_roots.add(root)
    yield root


def _begin_phase() -> None:
    _state.begin_phase()


def _end_phase() -> None:
    messages = _state.end_phase()
    if messages:
        pytest.fail("\n".join(messages), pytrace=False)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_setup(item: pytest.Item):
    _begin_phase()
    try:
        return (yield)
    finally:
        _end_phase()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item):
    _begin_phase()
    try:
        return (yield)
    finally:
        _end_phase()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item: pytest.Item):
    _begin_phase()
    try:
        return (yield)
    finally:
        _end_phase()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int | pytest.ExitCode) -> None:
    if _state.outside_messages:
        if session.exitstatus in (pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED):
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter: Any) -> None:
    if _state.outside_messages:
        terminalreporter.section("network guard")
        for msg in _state.outside_messages:
            terminalreporter.write_line(msg)
