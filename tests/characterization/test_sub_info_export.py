"""Characterize the legacy export converters and fetch in ``sub_info.py`` at commit 77c1f4d.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_sub_info_export.py --network=deny``.
The subscription server is a loopback stub (substitute, not evidence).

Known unsafe behaviour: (a) converters lose or invent fields: the VLESS `flow` is dropped and only the first `vnext`/user is used (case 3), VMess `alterId`/`security` become "0"/"auto" (case 5), the fingerprint defaults to `chrome` and an empty short id is dropped (cases 1, 2), xhttp settings and the sing-box gRPC `service_name` are ignored (cases 1, 9); (b) a sing-box REALITY outbound with `tls.enabled` becomes plain TLS with no REALITY keys (case 8); (c) `_session` disables TLS verification (case 11); (d) every fetch failure, and a base64-encoded JSON body, becomes an empty list (case 13); (e) diagnostics log the full subscription URL with its token, and the info line logs the first 200 characters of the body, credentials included (case 14). Composite export must not import this module (case 15; FR-049, FR-081).
"""

import ast
import asyncio
import base64
import contextlib
import json
import logging
import pathlib

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

import sub_info

H = "node.example.invalid"
UUID = "11111111-1111-4111-8111-111111111111"
TOKEN_PATH = "/sub/synthetic-sub-token"
UA = "v2rayNG/1.8.29"
L1 = "vless://u1@a.example.invalid:443?type=tcp#A"
L2 = "trojan://p@b.example.invalid:443#B"
REALITY_STREAM = {"network": "tcp", "security": "reality", "realitySettings": {"serverName": "www.example.com", "publicKey": "PBK", "shortId": "ab12", "fingerprint": "firefox"}}
XRAY_VLESS = {"protocol": "vless", "tag": "proxy", "settings": {"vnext": [{"address": H, "port": 443, "users": [{"id": UUID, "flow": "xtls-rprx-vision", "encryption": "none", "email": "ali@shop"}]}, {"address": "second.example.invalid", "port": 443, "users": [{"id": "x"}]}]}, "streamSettings": REALITY_STREAM}
SB_REALITY = {"type": "vless", "tag": "sb-tag", "server": H, "server_port": 443, "uuid": UUID, "flow": "xtls-rprx-vision", "tls": {"enabled": True, "server_name": "www.example.com", "utls": {"enabled": True, "fingerprint": "chrome"}, "reality": {"enabled": True, "public_key": "PBK", "short_id": "ab12"}}}
XRAY_JSON = {"remarks": "Prof", "outbounds": [{"protocol": "vless", "settings": {"vnext": [{"address": "a.example.invalid", "port": 443, "users": [{"id": "u1", "flow": "xtls-rprx-vision"}]}]}}, {"protocol": "freedom", "tag": "direct"}]}
NET_NONE = {"security": "none", "network": "tcp", "sni": H, "ws_path": "/", "ws_host": H, "header_type": "none", "reality": {}}


@contextlib.asynccontextmanager
async def stub_sub(status, body, content_type="text/plain"):
    seen = []
    app = web.Application()

    async def answer(request):
        seen.append((request.method, request.path_qs, request.headers.get("User-Agent")))
        return web.Response(status=status, text=body, content_type=content_type)

    app.router.add_route("*", "/{tail:.*}", answer)
    server = TestServer(app, host="127.0.0.1")
    await server.start_server()
    try:
        yield str(server.make_url(TOKEN_PATH)), seen
    finally:
        await server.close()


def _fetch(status, body, content_type="text/plain"):
    async def scenario():
        async with stub_sub(status, body, content_type) as (url, seen):
            res = await sub_info.fetch_individual_links(url)
            return res, url, seen

    return asyncio.run(scenario())


def _fetch_refused():
    async def scenario():
        app = web.Application()
        server = TestServer(app, host="127.0.0.1")
        await server.start_server()
        url = str(server.make_url(TOKEN_PATH))
        await server.close()
        res = await sub_info.fetch_individual_links(url)
        return res, url

    return asyncio.run(scenario())


def _copy(d):
    return json.loads(json.dumps(d))


def _vmess(uri):
    assert uri.startswith("vmess://")
    return json.loads(base64.b64decode(uri[len("vmess://"):]))


# Case 1
@pytest.mark.parametrize(
    ("stream", "expected"),
    [
        (None, NET_NONE),
        (
            {"network": "WS", "security": "TLS", "wsSettings": {"path": "/ws", "headers": {"Host": "cdn.example.invalid"}}, "tlsSettings": {"serverName": "sni.example.invalid"}},
            {"security": "tls", "network": "ws", "sni": "sni.example.invalid", "ws_path": "/ws", "ws_host": "cdn.example.invalid", "header_type": "none", "reality": {}},
        ),
        (
            {"network": "grpc", "security": "reality", "grpcSettings": {"serviceName": "svc"}, "realitySettings": {"serverName": "www.example.com", "publicKey": "PBK", "shortId": "ab12"}},
            {"security": "reality", "network": "grpc", "sni": "www.example.com", "ws_path": "svc", "ws_host": H, "header_type": "none", "reality": {"pbk": "PBK", "sid": "ab12", "fp": "chrome", "spx": ""}},
        ),
        (
            {"network": "tcp", "tcpSettings": {"header": {"type": "http", "request": {"headers": {"Host": ["h1.example.invalid", "h2.example.invalid"]}, "path": ["/p1", "/p2"]}}}},
            {"security": "none", "network": "tcp", "sni": "h1.example.invalid", "ws_path": "/p1", "ws_host": "h1.example.invalid", "header_type": "http", "reality": {}},
        ),
        (
            {"network": "xhttp", "security": "tls", "xhttpSettings": {"path": "/xh", "host": "x.example.invalid"}},
            dict(NET_NONE, security="tls", network="xhttp"),
        ),
        (
            {"network": "httpupgrade", "httpupgradeSettings": {"path": "/up", "host": "up.example.invalid"}},
            {"security": "none", "network": "httpupgrade", "sni": "up.example.invalid", "ws_path": "/up", "ws_host": "up.example.invalid", "header_type": "none", "reality": {}},
        ),
    ],
    ids=["empty", "ws_tls", "grpc_reality", "tcp_http_header", "xhttp_ignored", "httpupgrade"],
)
def test_net_params_from_stream(stream, expected):
    assert sub_info._net_params_from_stream(stream, H) == expected


# Case 2
@pytest.mark.parametrize(
    ("scheme", "host", "port", "auth", "remark", "stream", "expected"),
    [
        (
            "vless",
            H,
            443,
            UUID,
            "DE 1",
            {"network": "grpc", "security": "reality", "grpcSettings": {"serviceName": "svc"}, "realitySettings": {"serverName": "www.example.com", "publicKey": "PBK", "shortId": "ab12", "spiderX": "/spx"}},
            "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=grpc&security=reality&encryption=none&sni=www.example.com&serviceName=svc&pbk=PBK&sid=ab12&fp=chrome&spx=%2Fspx#DE%201",
        ),
        (
            "trojan",
            H,
            8443,
            "p@ss/w:rd",
            None,
            {"network": "ws", "security": "tls", "wsSettings": {"path": "/ws", "headers": {"Host": "cdn.example.invalid"}}, "tlsSettings": {"serverName": "sni.example.invalid"}},
            "trojan://p%40ss%2Fw%3Ard@node.example.invalid:8443?type=ws&security=tls&sni=sni.example.invalid&host=cdn.example.invalid&path=%2Fws#node.example.invalid",
        ),
        (
            "vless",
            H,
            80,
            "uuid-x",
            "",
            None,
            "vless://uuid-x@node.example.invalid:80?type=tcp&security=none&encryption=none#node.example.invalid",
        ),
        (
            "vless",
            H,
            443,
            "u",
            "r",
            {"network": "tcp", "security": "reality", "realitySettings": {"publicKey": "PBK"}},
            "vless://u@node.example.invalid:443?type=tcp&security=reality&encryption=none&sni=node.example.invalid&pbk=PBK&fp=chrome#r",
        ),
    ],
    ids=["vless_grpc_reality", "trojan_ws_tls_quoted", "plain_empty_remark", "reality_empty_sid_dropped"],
)
def test_vless_or_trojan_uri(scheme, host, port, auth, remark, stream, expected):
    net = sub_info._net_params_from_stream(stream, H)
    assert sub_info._vless_or_trojan_uri(scheme, host, port, auth, remark, net) == expected


# Case 3
def test_xray_vless_drops_flow_and_later_entries():
    uri = sub_info._xray_outbound_to_uri(XRAY_VLESS, "Profile")
    assert uri == "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=tcp&security=reality&encryption=none&sni=www.example.com&pbk=PBK&sid=ab12&fp=firefox#ali%40shop"
    assert "flow" not in uri
    assert "second.example.invalid" not in uri


# Case 4
P = "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=tcp&security=reality&encryption=none&sni=www.example.com&pbk=PBK&sid=ab12&fp=firefox#"
_no_email = _copy(XRAY_VLESS)
del _no_email["settings"]["vnext"][0]["users"][0]["email"]
_no_tag = _copy(_no_email)
del _no_tag["tag"]


@pytest.mark.parametrize(
    ("ob", "profile_remark", "expected"),
    [
        (XRAY_VLESS, "Profile", P + "ali%40shop"),
        (_no_email, "Profile", P + "Profile"),
        (_no_email, None, P + "proxy"),
        (_no_tag, None, P + H),
    ],
    ids=["email", "profile", "tag", "host"],
)
def test_xray_remark_precedence(ob, profile_remark, expected):
    assert sub_info._xray_outbound_to_uri(ob, profile_remark) == expected


# Case 5
def test_xray_vmess_invents_fields():
    ob = {
        "protocol": "vmess",
        "settings": {
            "vnext": [{"address": H, "port": 8080, "users": [{"id": UUID, "alterId": 64, "security": "aes-128-gcm"}]}]
        },
        "streamSettings": {"network": "ws", "wsSettings": {"path": "/vm"}},
    }
    payload = _vmess(sub_info._xray_outbound_to_uri(ob, "Profile"))
    assert list(payload.items()) == [
        ("v", "2"),
        ("ps", "Profile"),
        ("add", H),
        ("port", "8080"),
        ("id", UUID),
        ("aid", "0"),
        ("scy", "auto"),
        ("net", "ws"),
        ("type", "none"),
        ("host", H),
        ("path", "/vm"),
        ("tls", ""),
        ("sni", H),
    ]


# Case 6
@pytest.mark.parametrize(
    ("ob", "profile_remark", "expected"),
    [
        (
            {
                "protocol": "trojan",
                "settings": {"servers": [{"address": H, "port": 443, "password": "secret-pass", "email": "t@shop"}]},
                "streamSettings": {"network": "grpc", "security": "tls", "grpcSettings": {"serviceName": "tg"}, "tlsSettings": {"serverName": "sni.example.invalid"}},
            },
            None,
            "trojan://secret-pass@node.example.invalid:443?type=grpc&security=tls&sni=sni.example.invalid&serviceName=tg#t%40shop",
        ),
        (
            {
                "protocol": "shadowsocks",
                "settings": {"servers": [{"address": H, "port": 8388, "method": "chacha20-ietf-poly1305", "password": "sspass"}]},
            },
            "Prof",
            "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpzc3Bhc3M@node.example.invalid:8388#Prof",
        ),
    ],
    ids=["trojan", "shadowsocks"],
)
def test_xray_trojan_and_shadowsocks(ob, profile_remark, expected):
    assert sub_info._xray_outbound_to_uri(ob, profile_remark) == expected


# Case 7
@pytest.mark.parametrize(
    "ob",
    [
        {"protocol": "vless", "settings": {"vnext": [{"address": H, "port": 1, "users": [{}]}]}},
        {"protocol": "vless", "settings": {"vnext": [{"address": H, "users": [{"id": UUID}]}]}},
        {"protocol": "freedom"},
        {"protocol": "shadowsocks", "settings": {"servers": [{"address": H, "port": 1, "method": "m"}]}},
        {"protocol": "trojan", "settings": {"servers": [{"address": H, "port": 1}]}},
        {"protocol": "vmess", "settings": {}},
    ],
    ids=["no_uuid", "no_port", "freedom", "ss_no_password", "trojan_no_password", "no_vnext"],
)
def test_xray_unusable_outbounds_return_none(ob):
    assert sub_info._xray_outbound_to_uri(ob) is None


# Case 8
_sb_reality_tls_disabled = _copy(SB_REALITY)
_sb_reality_tls_disabled["tls"]["enabled"] = False


@pytest.mark.parametrize(
    ("ob", "expected"),
    [
        (SB_REALITY, "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=tcp&security=tls&encryption=none&sni=www.example.com#sb-tag"),
        (_sb_reality_tls_disabled, "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=tcp&security=reality&encryption=none&sni=www.example.com&pbk=PBK&sid=ab12&fp=chrome#sb-tag"),
    ],
    ids=["tls_enabled", "tls_disabled"],
)
def test_singbox_reality_becomes_tls(ob, expected):
    assert sub_info._singbox_outbound_to_uri(ob, None) == expected


# Case 9
@pytest.mark.parametrize(
    ("ob", "remark", "expected"),
    [
        (
            {"type": "trojan", "tag": "t", "server": H, "server_port": 443, "password": "pw", "tls": {"enabled": True, "server_name": "sni.example.invalid"}, "transport": {"type": "ws", "path": "/tw", "headers": {"Host": "cdn.example.invalid"}}},
            "Prof",
            "trojan://pw@node.example.invalid:443?type=ws&security=tls&sni=sni.example.invalid&host=cdn.example.invalid&path=%2Ftw#Prof",
        ),
        (
            {"type": "vless", "server": H, "server_port": 443, "uuid": UUID, "tls": {"enabled": True}, "transport": {"type": "grpc", "service_name": "gsvc"}},
            None,
            "vless://11111111-1111-4111-8111-111111111111@node.example.invalid:443?type=grpc&security=tls&encryption=none&sni=node.example.invalid&serviceName=%2F#node.example.invalid",
        ),
        (
            {"type": "vmess", "server": H, "server_port": 80, "uuid": UUID, "security": "auto", "alter_id": 0},
            None,
            [("v", "2"), ("ps", H), ("add", H), ("port", "80"), ("id", UUID), ("aid", "0"), ("scy", "auto"), ("net", "tcp"), ("type", "none"), ("host", H), ("path", "/"), ("tls", ""), ("sni", H)],
        ),
        (
            {"type": "shadowsocks", "server": H, "server_port": 8388, "method": "aes-256-gcm", "password": "p"},
            None,
            "ss://YWVzLTI1Ni1nY206cA@node.example.invalid:8388#node.example.invalid",
        ),
    ],
    ids=["trojan_ws", "vless_grpc_service_name_lost", "vmess_plain", "shadowsocks"],
)
def test_singbox_transports(ob, remark, expected):
    res = sub_info._singbox_outbound_to_uri(ob, remark)
    if isinstance(expected, list):
        assert list(_vmess(res).items()) == expected
    else:
        assert res == expected


# Case 10
@pytest.mark.parametrize(
    "ob",
    [
        {"type": "hysteria2", "server": H, "server_port": 443, "password": "p"},
        {"type": "direct"},
        {"type": "vless", "server": H, "uuid": UUID},
        {"type": "vless", "server": H, "server_port": 1},
    ],
    ids=["hysteria2", "direct", "no_port", "no_uuid"],
)
def test_singbox_unusable_outbounds_return_none(ob):
    assert sub_info._singbox_outbound_to_uri(ob) is None


# Case 11
def test_session_disables_tls():
    async def scenario():
        s1, s2 = sub_info._session(), sub_info._session()
        try:
            assert s1 is not s2
            assert s1.connector is not s2.connector
            assert s1.connector._ssl is False  # private attribute of aiohttp 3.14.5
            assert s1.timeout == aiohttp.ClientTimeout(total=10)
        finally:
            await s1.close()
            await s2.close()

    asyncio.run(scenario())


# Case 12
_urlsafe_body = base64.urlsafe_b64encode(b"vless://u?x=>>>\n").decode().rstrip("=")
assert "-" in _urlsafe_body


@pytest.mark.parametrize(
    ("body", "content_type", "expected"),
    [
        (base64.b64encode(f"{L1}\n\n  {L2}  \nnot-a-link\n".encode()).decode(), "text/plain", [L1, L2]),
        (f"{L1}\r\n{L2}\n", "text/plain", [L1, L2]),
        (_urlsafe_body, "text/plain", ["vless://u?x=>>>"]),
        (json.dumps([XRAY_JSON, "junk"]), "text/plain", ["vless://u1@a.example.invalid:443?type=tcp&security=none&encryption=none#Prof"]),
        (f'<html><body><p>Subscription Information</p><code>{L1}&amp;x=1</code><a href="{L2}">x</a></body></html>', "text/html", [L1 + "&x=1", L2]),
    ],
    ids=["base64_lines", "plain_lines", "urlsafe_base64", "xray_json_list", "html_page"],
)
def test_fetch_parses_bodies(body, content_type, expected):
    result, url, seen = _fetch(200, body, content_type=content_type)
    assert seen == [("GET", TOKEN_PATH, UA)]
    assert result == expected


# Case 13
@pytest.mark.parametrize(
    "call",
    [
        lambda: _fetch(404, "nope")[0],
        lambda: _fetch_refused()[0],
        lambda: _fetch(200, "hello world")[0],
        # the "base64 of a full JSON" branch never runs because the decoded text has no ://
        lambda: _fetch(200, base64.b64encode(json.dumps(XRAY_JSON).encode()).decode())[0],
    ],
    ids=["http_404", "refused", "no_config", "base64_json"],
)
def test_fetch_failures_return_empty_list(call):
    assert call() == []


# Case 14
@pytest.mark.parametrize(
    ("case_id", "runner"),
    [
        ("success", lambda: _fetch(200, f"{L1}\r\n{L2}\n")),
        ("http_404", lambda: _fetch(404, "nope")),
        ("refused", lambda: _fetch_refused()),
        ("no_config", lambda: _fetch(200, "hello world")),
    ],
    ids=["success", "http_404", "refused", "no_config"],
)
def test_fetch_diagnostics_expose_url_and_body(case_id, runner, caplog):
    caplog.set_level(logging.INFO, logger="sub_info")
    res = runner()
    url = res[1]
    recs = [r for r in caplog.records if r.name == "sub_info"]
    assert TOKEN_PATH in url
    assert all(url in r.getMessage() for r in recs)

    if case_id == "success":
        body = f"{L1}\r\n{L2}\n"
        assert [(r.levelno, r.args) for r in recs] == [(logging.INFO, (len(body), url, body))]
        assert "u1@a.example.invalid" in recs[0].getMessage()
    elif case_id == "http_404":
        assert [(r.levelno, r.args) for r in recs] == [(logging.WARNING, (404, url))]
    elif case_id == "refused":
        assert [(r.levelno, r.args) for r in recs] == [(logging.ERROR, (url,))]
        assert issubclass(recs[0].exc_info[0], aiohttp.ClientConnectionError)
    elif case_id == "no_config":
        assert [(r.levelno, r.args) for r in recs] == [
            (logging.INFO, (11, url, "hello world")),
            (logging.WARNING, (url, "hello world")),
        ]


# Case 15
def test_composite_never_imports_sub_info():
    root = pathlib.Path(__file__).resolve().parents[2] / "composite"
    files = sorted(root.rglob("*.py"))
    assert files
    offenders = []
    for f in files:
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "sub_info" or alias.name.startswith("sub_info."):
                        offenders.append((f, alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    if node.module == "sub_info" or node.module.startswith("sub_info."):
                        offenders.append((f, node.module))
    assert offenders == []
