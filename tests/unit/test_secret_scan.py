"""Secret scanner for test output (tasks.md T012; FR-084; constitution III).

"Panel/subscription secrets and authentication payloads MUST be excluded from
source control, general logs, unauthorized responses and fixtures" [FR-084].
Tests register the secrets they generated, then check captured logs,
exception text, HTTP responses to unauthorized callers and files. A finding
names the kind, a SHA-256 fingerprint and the place, never the value.
"""

import base64
import hashlib
import json
import logging
import os
import secrets
from urllib.parse import quote
import uuid

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_payments import FakePaymentMethod
from tests._harness.fake_threexui import FakeThreeXUIPanel
from tests._harness.fixtures import six_node_fixture
from tests._harness.secret_scan import SecretFinding, SecretLeak, SecretScan, fingerprint


def _token():
    """A fresh 43-character base64url token that contains a letter."""
    return "k" + secrets.token_urlsafe(32)[1:]


def _b64(text):
    return base64.b64encode(text.encode()).decode()


def _scan(**values):
    scan = SecretScan()
    for kind, value in values.items():
        scan.add(kind.replace("_", " "), value)
    return scan


def _leaked_subscription_body(fixture, subscription_key):
    """The real Base64 subscription body, as a 404 must never return it."""
    subscription = fixture.subscription(subscription_key)
    lines = []
    for credential in subscription.credentials:
        node = fixture.node(credential.node_key)
        inbound = fixture.inbound(node.panel_key, node.inbound_id)
        proxy = inbound.external_proxies[0]
        remark = quote(node.remark, safe="")
        if inbound.protocol == "vless":
            query = (
                f"type={inbound.transport}&security={inbound.security}"
                f"&sni={inbound.sni}&fp={inbound.fingerprint}"
            )
            if inbound.security == "reality":
                query += (
                    f"&pbk={inbound.reality_public_key}&sid={inbound.reality_short_id}"
                    f"&flow={inbound.flow}"
                )
            lines.append(f"vless://{credential.secret}@{proxy.host}:{proxy.port}?{query}#{remark}")
        elif inbound.protocol == "trojan":
            lines.append(
                f"trojan://{credential.secret}@{proxy.host}:{proxy.port}"
                f"?type=grpc&serviceName={inbound.grpc_service_name}&security=tls"
                f"&sni={inbound.sni}#{remark}"
            )
        else:
            config = {
                "v": "2",
                "ps": node.remark,
                "add": proxy.host,
                "port": str(proxy.port),
                "id": credential.secret,
                "aid": "0",
                "scy": inbound.vmess_cipher,
                "net": "tcp",
                "type": "none",
                "tls": "tls",
                "sni": inbound.sni,
            }
            lines.append("vmess://" + _b64(json.dumps(config, ensure_ascii=False)))
    return base64.b64encode(("\n".join(lines) + "\n").encode())


def test_fingerprint_is_a_sha256_prefix():
    value = _token()
    assert fingerprint(value) == hashlib.sha256(value.encode()).hexdigest()[:12]


def test_registered_value_is_found_as_written():
    value = _token()
    scan = _scan(panel_token=value)
    assert scan.find(f"answer from panel: {value} done", source="note") == (
        SecretFinding("panel token", fingerprint(value), "note", 0),
    )
    assert scan.find("nothing secret here", source="note") == ()
    assert scan.check_text("nothing secret here", source="note") is None


def test_leak_report_never_contains_the_value():
    value = _token()
    scan = _scan(panel_token=value)
    with pytest.raises(SecretLeak) as leak:
        scan.check_text(f"Authorization: Bearer {value}", source="captured stdout")
    assert isinstance(leak.value, AssertionError)
    assert leak.value.findings == (
        SecretFinding("panel token", fingerprint(value), "captured stdout", 0),
    )
    assert str(leak.value) == f"secrets found:\npanel token {fingerprint(value)} in captured stdout"
    for text in (str(leak.value), repr(leak.value), repr(leak.value.findings), repr(scan)):
        assert value not in text


def test_bytes_with_invalid_utf8_are_scanned():
    value = _token()
    scan = _scan(payment_key=value)
    data = b"\xff\xfe\x00" + value.encode() + b"\x80\xc3"
    assert scan.find(data, source="raw") == (
        SecretFinding("payment key", fingerprint(value), "raw", 0),
    )


def test_base64_in_either_alphabet_at_any_offset():
    value = _token()
    scan = _scan(subscription_token=value)
    plain = f"secret={value};end-of-line".encode()
    blobs = (
        base64.b64encode(plain).decode(),
        base64.urlsafe_b64encode(plain).decode().rstrip("="),
    )
    for blob in blobs:
        for prefix in ("", "a", "ab", "abc"):
            for suffix in ("", " tail", "xyz"):
                assert scan.find(prefix + blob + suffix, source="body") == (
                    SecretFinding("subscription token", fingerprint(value), "body", 1),
                ), (prefix, suffix)


def test_nested_base64_up_to_three_levels():
    value = _token()
    scan = _scan(panel_token=value)
    text = f"x {value} y"
    for depth in (1, 2, 3):
        text = _b64(text)
        assert scan.find(text, source="body") == (
            SecretFinding("panel token", fingerprint(value), "body", depth),
        )


def test_each_value_is_reported_once_at_its_lowest_depth():
    value = _token()
    scan = _scan(panel_token=value)
    text = f"{_b64('id=' + value)} and {value}"
    assert scan.find(text, source="log") == (
        SecretFinding("panel token", fingerprint(value), "log", 0),
    )


def test_uuid_values_match_in_any_case_and_without_hyphens():
    value = str(uuid.uuid4())
    scan = _scan(client_UUID=value)
    forms = (
        value.upper(),
        value.replace("-", ""),
        value.replace("-", "").upper(),
        f"UUID('{value}')",
    )
    for form in forms:
        assert scan.find(f"client {form} added", source="log") == (
            SecretFinding("client UUID", fingerprint(value), "log", 0),
        ), form


def test_other_values_are_case_sensitive():
    value = _token()
    scan = _scan(panel_token=value)
    assert scan.find(value.swapcase(), source="log") == ()


def test_unregistered_subscription_urls_are_found_by_shape():
    scan = SecretScan()
    token = secrets.token_urlsafe(32)
    assert len(token) == 43
    expected = (SecretFinding("subscription URL", fingerprint(token), "access log", 0),)
    assert scan.find(f'"GET /sub/{token} HTTP/1.1" 404', source="access log") == expected
    assert scan.find(f"?u=https%3A%2F%2Fstore%2Fsub%2F{token}", source="access log") == expected
    assert scan.find(f"?u=https%3a%2f%2fstore%2fsub%2f{token}", source="access log") == expected
    for clean in (
        f"/sub/{token[:42]} ",
        f"/sub/{token}A",
        "GET /sub/{token}",
        "GET /sub/[redacted] 404",
    ):
        assert scan.find(clean, source="access log") == (), clean
    assert scan.find(_b64(f"https://s.example.invalid/sub/{token}\n"), source="body") == (
        SecretFinding("subscription URL", fingerprint(token), "body", 1),
    )


def test_registered_token_in_a_url_is_reported_once():
    token = secrets.token_urlsafe(32)
    scan = _scan(subscription_token=token)
    assert scan.find(f"https://s.example.invalid/sub/{token}", source="log") == (
        SecretFinding("subscription token", fingerprint(token), "log", 0),
    )


def test_findings_order_within_one_source():
    first, second = _token(), _token()
    scan = _scan(panel_token=first, payment_key=second)
    urls = sorted((secrets.token_urlsafe(32) for _ in range(2)), key=fingerprint, reverse=True)
    text = f"{second} /sub/{urls[0]} {first} /sub/{urls[1]}"
    assert scan.find(text, source="log") == (
        SecretFinding("panel token", fingerprint(first), "log", 0),
        SecretFinding("payment key", fingerprint(second), "log", 0),
        SecretFinding("subscription URL", fingerprint(urls[1]), "log", 0),
        SecretFinding("subscription URL", fingerprint(urls[0]), "log", 0),
    )


def test_add_fixture_registers_every_generated_secret():
    fixture = six_node_fixture()
    scan = SecretScan()
    scan.add_fixture(fixture)
    expected = [("panel token", fingerprint(panel.api_token)) for panel in fixture.panels]
    expected.append(("REALITY private key", fingerprint(fixture.inbound("A", 1).reality_private_key)))
    for subscription in fixture.subscriptions:
        expected.append(("subscription token", fingerprint(subscription.url_token)))
        for credential in subscription.credentials:
            kind = "client UUID" if credential.secret_kind == "uuid" else "Trojan password"
            expected.append((kind, fingerprint(credential.secret)))
    assert scan.registered == tuple(expected)
    assert len(scan.registered) == 3 + 1 + 3 * 7


def test_identifiers_and_public_values_are_not_secrets():
    fixture = six_node_fixture()
    scan = SecretScan()
    scan.add_fixture(fixture)
    inbound = fixture.inbound("A", 1)
    text = " ".join(
        [tenant.installation_id for tenant in fixture.tenants]
        + [panel.physical_panel_id for panel in fixture.panels]
        + [inbound.reality_public_key, inbound.reality_short_id, inbound.flow]
        + [panel.base_url for panel in fixture.panels]
    )
    assert scan.check_text(text, source="diagnostics") is None


def test_leaked_subscription_body_reveals_every_credential():
    fixture = six_node_fixture()
    scan = SecretScan()
    scan.add_fixture(fixture)
    credentials = fixture.subscription("ali-1").credentials
    expected = tuple(
        SecretFinding(
            "client UUID" if credential.secret_kind == "uuid" else "Trojan password",
            fingerprint(credential.secret),
            "404 body",
            2 if credential.node_key == "C-Direct" else 1,
        )
        for credential in credentials
    )
    body = _leaked_subscription_body(fixture, "ali-1")
    assert scan.find(body, source="404 body") == expected
    with pytest.raises(SecretLeak) as leak:
        scan.check_http(body, source="404")
    assert [finding.source for finding in leak.value.findings] == ["404 body"] * 6
    line = f"client UUID {fingerprint(credentials[5].secret)} in 404 body, base64 depth 2"
    assert line in str(leak.value).splitlines()


def test_add_panel_and_add_payment_method():
    fixture = six_node_fixture()
    panel = FakeThreeXUIPanel(fixture, "A", FakeClock())
    scan = SecretScan()
    scan.add_fixture(fixture)
    before = len(scan.registered)
    scan.add_panel(panel)
    tokens = panel.tokens
    assert scan.registered[before:] == (
        ("panel token", fingerprint(tokens["node-sync"])),
        ("panel token", fingerprint(tokens["monitor"])),
    )
    method = FakePaymentMethod(FakeClock())
    scan.add_payment_method(method)
    assert scan.registered[-1] == ("payment key", fingerprint(method.api_key))
    assert scan.find(f"key={method.api_key}", source="log") == (
        SecretFinding("payment key", fingerprint(method.api_key), "log", 0),
    )


def test_a_repeated_value_keeps_its_first_kind():
    value = _token()
    scan = SecretScan()
    scan.add("panel token", value)
    scan.add("payment key", value)
    assert scan.registered == (("panel token", fingerprint(value)),)


def test_log_records_are_scanned_in_full():
    values = [_token() for _ in range(5)]
    scan = SecretScan()
    for value in values:
        scan.add("panel token", value)

    class Hidden:
        def __str__(self):
            return values[0]

        def __repr__(self):
            return "<hidden>"

    try:
        try:
            raise KeyError(f"panel said {values[2]}")
        except KeyError as inner:
            raise RuntimeError("request failed") from inner
    except RuntimeError as exc:
        exc_info = (type(exc), exc, exc.__traceback__)

    def record(**fields):
        return logging.makeLogRecord({"name": "composite.test", **fields})

    records = [
        record(msg="panel answered %s", args=(Hidden(),)),
        record(msg="clean", panel_auth=values[1]),
        record(msg="request failed", exc_info=exc_info),
        record(msg="all good"),
        record(msg="%s %s", args=(values[4],)),
    ]
    with pytest.raises(SecretLeak) as leak:
        scan.check_logs(records)
    assert leak.value.findings == tuple(
        SecretFinding("panel token", fingerprint(values[index]), f"log record {index} (composite.test)", 0)
        for index in (0, 1, 2, 4)
    )
    assert scan.check_logs([record(msg="all good")]) is None
    assert scan.check_logs([]) is None


def test_captured_pytest_logs(caplog):
    value = _token()
    scan = _scan(panel_token=value)
    logger = logging.getLogger("composite.caplog")
    with caplog.at_level(logging.INFO, logger="composite.caplog"):
        logger.info("starting")
        logger.warning("token=%s", value)
    with pytest.raises(SecretLeak) as leak:
        scan.check_logs(caplog.records)
    assert leak.value.findings == (
        SecretFinding("panel token", fingerprint(value), "log record 1 (composite.caplog)", 0),
    )


def test_exception_text_includes_causes_notes_groups_and_repr():
    values = [_token() for _ in range(4)]
    scan = SecretScan()
    for value in values:
        scan.add("Trojan password", value)

    try:
        try:
            raise KeyError(values[0])
        except KeyError as inner:
            raise RuntimeError("wrapped") from inner
    except RuntimeError as exc:
        chained = exc

    noted = ValueError("plain")
    noted.add_note(f"while using {values[1]}")

    group = ExceptionGroup("several", [ValueError(values[2])])

    class Quiet(Exception):
        def __str__(self):
            return "quiet"

    quiet = Quiet(values[3])

    cases = [
        (chained, values[0], "exception RuntimeError"),
        (noted, values[1], "exception ValueError"),
        (group, values[2], "exception ExceptionGroup"),
        (quiet, values[3], "exception Quiet"),
    ]
    for exc, value, source in cases:
        with pytest.raises(SecretLeak) as leak:
            scan.check_exception(exc)
        assert leak.value.findings == (
            SecretFinding("Trojan password", fingerprint(value), source, 0),
        )
    assert scan.check_exception(ValueError("nothing secret")) is None
    with pytest.raises(TypeError):
        scan.check_exception("not an exception")


def test_http_body_and_headers():
    token, cookie = _token(), _token()
    scan = _scan(subscription_token=token, panel_token=cookie)
    with pytest.raises(SecretLeak) as leak:
        scan.check_http(
            f"moved to {token}".encode(),
            headers=[
                ("Set-Cookie", "a=1"),
                ("Set-Cookie", f"s={cookie}"),
                ("Location", f"https://s.example.invalid/sub/{token}"),
            ],
        )
    assert leak.value.findings == (
        SecretFinding("subscription token", fingerprint(token), "HTTP response body", 0),
        SecretFinding("panel token", fingerprint(cookie), "HTTP response header Set-Cookie", 0),
        SecretFinding("subscription token", fingerprint(token), "HTTP response header Location", 0),
    )
    unregistered = secrets.token_urlsafe(32)
    with pytest.raises(SecretLeak) as leak:
        scan.check_http(
            "",
            headers={"Location": f"https://s.example.invalid/sub/{unregistered}"},
            source="GET /sub/<redacted>",
        )
    assert leak.value.findings == (
        SecretFinding(
            "subscription URL",
            fingerprint(unregistered),
            "GET /sub/<redacted> header Location",
            0,
        ),
    )
    assert scan.check_http(b"Not Found", headers={"Content-Type": "text/plain"}) is None
    assert scan.check_http("Not Found") is None


def test_files_and_names_are_scanned_without_following_symlinks(tmp_path):
    value, named, linked = _token(), _token(), _token()
    scan = _scan(panel_token=value, payment_key=named, client_UUID=linked)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text(f"key {linked}")
    root = tmp_path / "fixtures"
    (root / "nested").mkdir(parents=True)
    (root / "clean.json").write_text('{"ok": true}')
    (root / "nested" / "data.bin").write_bytes(b"\x00\x01" + value.encode() + b"\x00")
    (root / "nested" / "encoded.txt").write_text(_b64(f"token={value};"))
    (root / f"{named}.json").write_text("{}")
    os.symlink(outside / "secret.txt", root / "link.txt")
    os.symlink(outside, root / "linkdir")

    with pytest.raises(SecretLeak) as leak:
        scan.check_files(root)
    assert leak.value.findings == (
        SecretFinding("payment key", fingerprint(named), f"file name {root / (named + '.json')}", 0),
        SecretFinding("panel token", fingerprint(value), f"file {root / 'nested' / 'data.bin'}", 0),
        SecretFinding("panel token", fingerprint(value), f"file {root / 'nested' / 'encoded.txt'}", 1),
    )

    with pytest.raises(SecretLeak) as leak:
        scan.check_files(root / "clean.json", outside / "secret.txt")
    assert leak.value.findings == (
        SecretFinding("client UUID", fingerprint(linked), f"file {outside / 'secret.txt'}", 0),
    )
    assert scan.check_files(root / "clean.json") is None
    with pytest.raises(FileNotFoundError):
        scan.check_files(root / "missing.json")
    with pytest.raises(ValueError):
        scan.check_files(root / "link.txt")


def test_arguments_are_validated():
    value = _token()
    scan = SecretScan()
    for bad_kind, error in ((None, TypeError), (3, TypeError), ("", ValueError)):
        with pytest.raises(error):
            scan.add(bad_kind, value)
    for bad_value, error in ((None, TypeError), (b"x" * 20, TypeError), ("x" * 15, ValueError)):
        with pytest.raises(error):
            scan.add("panel token", bad_value)
    assert scan.registered == ()
    scan.add("panel token", "x" * 16)
    assert len(scan.registered) == 1
    for bad_text in (None, 3, ["text"]):
        with pytest.raises(TypeError):
            scan.find(bad_text, source="s")
        with pytest.raises(TypeError):
            scan.check_text(bad_text, source="s")
        with pytest.raises(TypeError):
            scan.check_http(bad_text)
    for bad_source, error in ((None, TypeError), (3, TypeError), ("", ValueError)):
        with pytest.raises(error):
            scan.find("text", source=bad_source)
        with pytest.raises(error):
            scan.check_http("text", source=bad_source)
    with pytest.raises(TypeError):
        scan.check_logs([object()])
    with pytest.raises(TypeError):
        scan.check_http("text", headers=[("Location", 3)])
