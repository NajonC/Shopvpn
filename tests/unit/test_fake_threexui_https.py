"""HTTPS front of the fake 3x-UI panel (tasks.md T009 part d; RX-MAN-001).

V-RX-01(b) on lab replicas of v3.9.0 showed, over TLS:
- a request not fully delivered before the client closed never executed;
- a request whose missing bytes arrived after the client closed executed
  (split-deliver);
- a whole request whose answer was held executed after the client closed
  (b2-late).

The composite client must use verified TLS, a bearer token and a fresh,
explicitly closed connection per call, whose close time is the quarantine
origin. Times are the FakeClock's; real time only bounds the waits for
sockets.
"""

import asyncio
import hashlib
import json
import logging
import ssl
import time
from urllib.parse import quote

import aiohttp
import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import (
    FakeNotModelled,
    FakeServedRequest,
    FakeThreeXUIPanel,
    FakeThreeXUIServer,
    make_certificate,
)
from tests._harness.fixtures import six_node_fixture

US = "ali_sub1_us"
OK = {"success": True, "msg": "", "obj": None}
REFUSED_SCOPE = {
    "success": False,
    "msg": "this API token is not permitted to access this endpoint",
}
LATE_ID = "33333333-3333-4333-8333-333333333333"


def _panel(key="A"):
    fixture = six_node_fixture()
    clock = FakeClock()
    panel = FakeThreeXUIPanel(fixture, key, clock)
    panel.seed_subscription(fixture, "ali-1")
    panel.set_setting("restartXrayOnClientDisable", False)
    return clock, panel


async def _request(
    server,
    method,
    path,
    *,
    token=None,
    json_body=None,
    data=None,
    headers=None,
    timeout_s=5.0,
    context=None,
):
    """One call on a fresh connection that is closed before this returns."""
    connector = aiohttp.TCPConnector(
        ssl=context or server.certificate.client_context(), force_close=True
    )
    all_headers = dict(headers or {})
    if token is not None:
        all_headers["Authorization"] = f"Bearer {token}"
    async with aiohttp.ClientSession(
        connector=connector, timeout=aiohttp.ClientTimeout(total=timeout_s)
    ) as session:
        async with session.request(
            method,
            f"https://127.0.0.1:{server.port}{path}",
            json=json_body,
            data=data,
            headers=all_headers,
        ) as response:
            return response.status, await response.read()


def _disable_us(server, panel, **kwargs):
    return _request(
        server,
        "POST",
        f"/xui/panel/api/clients/update/{US}",
        token=panel.tokens["admin"],
        json_body={"email": US, "enable": False},
        **kwargs,
    )


async def _until(predicate, timeout_s=2.0):
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout_s
    while not predicate():
        if loop.time() > deadline:
            raise AssertionError("condition not reached in time")
        await asyncio.sleep(0.001)


def _only_request(server):
    (connection,) = server.connections
    (request,) = connection.requests
    return connection, request


# TLS and certificates


def test_serves_verified_https_on_loopback():
    async def scenario():
        _, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            assert server.base_url == f"https://127.0.0.1:{server.port}/xui"
            status, body = await _request(
                server,
                "GET",
                "/xui/panel/api/inbounds/list",
                token=panel.tokens["admin"],
            )
            assert status == 200
            assert [inbound["id"] for inbound in json.loads(body)["obj"]] == [1]

            for server_hostname in ("127.0.0.1", "localhost"):
                _, writer = await asyncio.open_connection(
                    "127.0.0.1",
                    server.port,
                    ssl=server.certificate.client_context(),
                    server_hostname=server_hostname,
                )
                der = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
                writer.close()
                await writer.wait_closed()
                assert hashlib.sha256(der).hexdigest() == server.certificate.sha256_fingerprint

    asyncio.run(scenario())


def test_certificate_with_wrong_identity_is_rejected():
    async def scenario():
        _, panel = _panel()
        wrong = make_certificate(ip_addresses=(), dns_names=("wrong-name.invalid",))
        async with FakeThreeXUIServer(panel, certificate=wrong) as server:
            assert server.certificate is wrong
            with pytest.raises(aiohttp.ClientConnectorCertificateError):
                await _request(
                    server,
                    "GET",
                    "/xui/panel/api/inbounds/list",
                    token=panel.tokens["admin"],
                    context=wrong.client_context(),
                )
            assert server.connections == ()
        assert panel.calls == []

    asyncio.run(scenario())


def test_untrusted_certificate_is_rejected():
    async def scenario():
        _, panel = _panel()
        other = make_certificate()
        async with FakeThreeXUIServer(panel) as server:
            with pytest.raises(aiohttp.ClientConnectorCertificateError):
                await _request(
                    server,
                    "GET",
                    "/xui/panel/api/inbounds/list",
                    token=panel.tokens["admin"],
                    context=other.client_context(),
                )
        assert panel.calls == []

    asyncio.run(scenario())


def test_certificates_are_new_per_front_and_hide_the_key():
    first, second = make_certificate(), make_certificate()
    assert first.sha256_fingerprint != second.sha256_fingerprint
    assert first.key_pem != second.key_pem
    assert b"PRIVATE KEY" in first.key_pem
    assert first.sha256_fingerprint == hashlib.sha256(
        ssl.PEM_cert_to_DER_cert(first.cert_pem.decode("ascii"))
    ).hexdigest()
    assert "PRIVATE" not in repr(first)

    _, panel = _panel()
    one, two = FakeThreeXUIServer(panel), FakeThreeXUIServer(panel)
    assert one.certificate.sha256_fingerprint != two.certificate.sha256_fingerprint
    assert "PRIVATE" not in repr(one)


# Tokens and secrets


def test_bearer_token_maps_to_panel_scopes():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        async with FakeThreeXUIServer(panel) as server:
            status, body = await _request(
                server, "POST", "/xui/panel/api/setting/all", token=admin
            )
            assert status == 200
            assert json.loads(body)["obj"]["restartXrayOnClientDisable"] is False

            status, body = await _request(
                server,
                "POST",
                "/xui/panel/api/setting/all",
                token=panel.tokens["node-sync"],
            )
            assert (status, json.loads(body)) == (403, REFUSED_SCOPE)

            status, body = await _request(
                server,
                "GET",
                "/xui/panel/api/inbounds/list",
                token=panel.tokens["monitor"],
            )
            assert (status, json.loads(body)) == (403, REFUSED_SCOPE)

            assert await _request(
                server, "GET", "/xui/panel/api/inbounds/list", token="not-a-panel-token"
            ) == (401, b"")
            assert await _request(server, "GET", "/xui/panel/api/inbounds/list") == (
                404,
                b"",
            )
            assert await _request(
                server,
                "GET",
                "/xui/panel/api/inbounds/list",
                headers={"Authorization": f"Basic {admin}"},
            ) == (404, b"")

        assert [(call.method, call.path, call.scope) for call in panel.calls] == [
            ("POST", "/panel/api/setting/all", "admin"),
            ("POST", "/panel/api/setting/all", "node-sync"),
            ("GET", "/panel/api/inbounds/list", "monitor"),
            ("GET", "/panel/api/inbounds/list", None),
            ("GET", "/panel/api/inbounds/list", None),
            ("GET", "/panel/api/inbounds/list", None),
        ]

    asyncio.run(scenario())


def test_front_logs_and_records_no_secret(caplog):
    caplog.set_level(logging.DEBUG)
    secret_id = "44444444-4444-4444-8444-444444444444"

    async def scenario():
        _, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            status, _ = await _request(
                server,
                "POST",
                "/xui/panel/api/clients/add",
                token=panel.tokens["admin"],
                json_body={"inboundIds": [1], "client": {"email": "logged", "id": secret_id}},
            )
            assert status == 200
            await server.wait_connections_closed()
            shown = repr(server) + repr(server.connections)
            return panel.tokens["admin"], server.certificate.key_pem.decode("ascii"), shown

    admin, key_pem, shown = asyncio.run(scenario())
    assert not [record for record in caplog.records if record.name == "aiohttp.access"]
    for secret in (admin, secret_id, key_pem):
        assert secret not in caplog.text
        assert secret not in shown


# Request mapping


def test_base_path_is_stripped_and_required():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        async with FakeThreeXUIServer(panel) as server:
            status, _ = await _request(
                server, "GET", "/xui/panel/api/inbounds/list", token=admin
            )
            assert status == 200
            assert await _request(
                server, "GET", "/panel/api/inbounds/list", token=admin
            ) == (404, b"")
            assert await _request(
                server, "GET", "/xuix/panel/api/inbounds/list", token=admin
            ) == (404, b"")
        assert [(call.method, call.path) for call in panel.calls] == [
            ("GET", "/panel/api/inbounds/list")
        ]

    asyncio.run(scenario())


def test_custom_and_empty_base_path():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        async with FakeThreeXUIServer(panel, base_path="/hidden-path") as server:
            assert server.base_url == f"https://127.0.0.1:{server.port}/hidden-path"
            status, _ = await _request(
                server, "GET", "/hidden-path/panel/api/server/status", token=admin
            )
            assert status == 200
        async with FakeThreeXUIServer(panel, base_path="") as server:
            assert server.base_url == f"https://127.0.0.1:{server.port}"
            status, _ = await _request(
                server, "GET", "/panel/api/server/status", token=admin
            )
            assert status == 200

    asyncio.run(scenario())
    _, panel = _panel()
    for bad in ("xui", "/xui/", "/"):
        with pytest.raises(ValueError):
            FakeThreeXUIServer(panel, base_path=bad)


def test_json_body_query_and_decoded_email_reach_the_panel():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        email = "late one"
        async with FakeThreeXUIServer(panel) as server:
            status, body = await _request(
                server,
                "POST",
                "/xui/panel/api/clients/add",
                token=admin,
                json_body={"inboundIds": [1], "client": {"email": email, "id": LATE_ID}},
            )
            assert (status, json.loads(body)) == (200, OK)
            status, body = await _request(
                server,
                "POST",
                f"/xui/panel/api/clients/update/{quote(email)}",
                token=admin,
                json_body={"email": email, "enable": False},
            )
            assert (status, json.loads(body)) == (200, OK)
            assert panel.client(email)["enable"] is False
            status, body = await _request(
                server,
                "POST",
                f"/xui/panel/api/clients/del/{quote(email)}?keepTraffic=1",
                token=admin,
            )
            assert (status, json.loads(body)) == (200, OK)
        assert panel.client(email) is None
        assert panel.traffic(email) is not None
        assert panel.calls[1].path == "/panel/api/clients/update/late one"

    asyncio.run(scenario())


def test_unmodelled_route_answers_500_and_fails_on_close():
    async def scenario():
        _, panel = _panel()
        server = FakeThreeXUIServer(panel)
        await server.start()
        assert await _request(
            server, "GET", "/xui/panel/api/clients/list", token=panel.tokens["admin"]
        ) == (500, b"")
        with pytest.raises(FakeNotModelled):
            await server.close()

    asyncio.run(scenario())


def test_body_that_is_not_json_is_not_modelled():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        server = FakeThreeXUIServer(panel)
        await server.start()
        assert await _request(
            server,
            "POST",
            "/xui/panel/api/clients/add",
            token=admin,
            data=b"email=x",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) == (500, b"")
        assert await _request(
            server,
            "POST",
            "/xui/panel/api/clients/add",
            token=admin,
            data=b"{not json",
            headers={"Content-Type": "application/json"},
        ) == (500, b"")
        assert panel.calls == []
        with pytest.raises(FakeNotModelled):
            await server.close()

    asyncio.run(scenario())


# Connection log


def test_each_fresh_connection_is_logged_with_its_open_and_close_times():
    async def scenario():
        clock, panel = _panel()
        start = clock.true_now_ms()
        async with FakeThreeXUIServer(panel) as server:
            await _request(
                server, "GET", "/xui/panel/api/server/status", token=panel.tokens["admin"]
            )
            await server.wait_connections_closed()
            clock.advance(1_000)
            await _disable_us(server, panel)
            await server.wait_connections_closed()
            first, second = server.connections
        assert (first.index, first.opened_ms, first.closed_ms) == (0, start, start)
        assert first.requests == (
            FakeServedRequest("GET", "/xui/panel/api/server/status", start, "answered", 200),
        )
        assert (second.index, second.opened_ms, second.closed_ms) == (
            1,
            start + 1_000,
            start + 1_000,
        )
        assert second.requests == (
            FakeServedRequest(
                "POST", f"/xui/panel/api/clients/update/{US}", start + 1_000, "answered", 200
            ),
        )

    asyncio.run(scenario())


def test_pooled_connection_shows_in_the_log_and_closes_when_seen():
    async def scenario():
        clock, panel = _panel()
        start = clock.true_now_ms()
        headers = {"Authorization": f"Bearer {panel.tokens['admin']}"}
        async with FakeThreeXUIServer(panel) as server:
            connector = aiohttp.TCPConnector(ssl=server.certificate.client_context())
            async with aiohttp.ClientSession(connector=connector) as session:
                for _ in range(2):
                    async with session.get(
                        server.base_url + "/panel/api/server/status", headers=headers
                    ) as response:
                        assert response.status == 200
                        await response.read()
                (connection,) = server.connections
                assert len(connection.requests) == 2
                assert connection.closed_ms is None
                with pytest.raises(TimeoutError):
                    await server.wait_connections_closed(timeout_s=0.05)
                clock.advance(5_000)
            await server.wait_connections_closed()
            (connection,) = server.connections
            assert connection.closed_ms == start + 5_000

    asyncio.run(scenario())


# Transport faults (V-RX-01(b))


def test_request_held_in_transit_then_dropped_never_executes():
    async def scenario():
        clock, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            server.hold_requests()
            with pytest.raises(TimeoutError):
                await _disable_us(server, panel, timeout_s=0.3)
            await server.wait_connections_closed()
            assert server.held_requests == 1
            assert panel.calls == []
            assert panel.pending_writes == 0
            _, request = _only_request(server)
            assert (request.state, request.status) == ("in transit", None)

            server.drop_requests()
            assert server.held_requests == 0
            _, request = _only_request(server)
            assert (request.state, request.status) == ("dropped", None)
            clock.advance(60_000)
            panel.run_due()
        assert panel.client(US)["enable"] is True
        assert panel.calls == []

    asyncio.run(scenario())


def test_held_request_delivered_after_the_client_closed_executes():
    async def scenario():
        clock, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            server.hold_requests()
            with pytest.raises(TimeoutError):
                await _disable_us(server, panel, timeout_s=0.3)
            await server.wait_connections_closed()
            connection, _ = _only_request(server)
            clock.advance(3_500)
            server.deliver_requests()
            # The panel has the request as soon as deliver_requests() returns.
            assert server.held_requests == 0
            assert panel.client(US)["enable"] is False
            assert panel.client(US)["updated_at"] == connection.closed_ms + 3_500
            assert [(call.method, call.path, call.scope) for call in panel.calls] == [
                ("POST", f"/panel/api/clients/update/{US}", "admin")
            ]
            await _until(lambda: _only_request(server)[1].state == "answer dropped")
            assert _only_request(server)[1].status == 200

    asyncio.run(scenario())


def test_held_request_delivered_while_the_client_waits_is_answered():
    async def scenario():
        _, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            server.hold_requests()
            call = asyncio.create_task(
                _request(
                    server,
                    "GET",
                    "/xui/panel/api/server/status",
                    token=panel.tokens["admin"],
                )
            )
            await _until(lambda: server.held_requests == 1)
            assert not call.done()
            assert panel.calls == []
            server.deliver_requests()
            status, body = await call
            assert status == 200
            assert json.loads(body)["success"] is True
            await server.wait_connections_closed()
            _, request = _only_request(server)
            assert (request.state, request.status) == ("answered", 200)

    asyncio.run(scenario())


def test_matching_hold_lets_the_read_back_through_before_the_create_lands():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        seen = []

        def writes_only(method, path):
            seen.append((method, path))
            return method == "POST"

        async with FakeThreeXUIServer(panel) as server:
            server.hold_requests(writes_only)
            with pytest.raises(TimeoutError):
                await _request(
                    server,
                    "POST",
                    "/xui/panel/api/clients/add",
                    token=admin,
                    json_body={"inboundIds": [1], "client": {"email": "late", "id": LATE_ID}},
                    timeout_s=0.3,
                )
            status, body = await _request(
                server, "GET", "/xui/panel/api/clients/traffic/late", token=admin
            )
            assert (status, json.loads(body)) == (200, OK)
            assert server.held_requests == 1
            server.deliver_requests()
            assert panel.client("late")["id"] == LATE_ID
        assert seen == [
            ("POST", "/panel/api/clients/add"),
            ("GET", "/panel/api/clients/traffic/late"),
        ]

    asyncio.run(scenario())


def test_whole_request_with_held_answer_executes_after_the_client_closed():
    async def scenario():
        clock, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            panel.stall_inbound(1)
            with pytest.raises(TimeoutError):
                await _disable_us(server, panel, timeout_s=0.3)
            await server.wait_connections_closed()
            assert panel.pending_writes == 1
            connection, request = _only_request(server)
            assert (request.state, request.status) == ("at panel", None)
            clock.advance(3_500)
            panel.release_inbound(1)
            assert panel.client(US)["enable"] is False
            assert panel.client(US)["updated_at"] == connection.closed_ms + 3_500
            await _until(lambda: _only_request(server)[1].state == "answer dropped")
            assert _only_request(server)[1].status == 200

    asyncio.run(scenario())


def test_held_panel_answer_reaches_a_client_that_still_waits():
    async def scenario():
        _, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            panel.hold_responses()
            call = asyncio.create_task(
                _request(
                    server,
                    "GET",
                    "/xui/panel/api/server/status",
                    token=panel.tokens["admin"],
                )
            )
            await _until(lambda: len(panel.calls) == 1)
            assert not call.done()
            panel.release_responses()
            status, _ = await call
            assert status == 200

    asyncio.run(scenario())


def test_drop_closes_the_connection_of_a_waiting_client():
    async def scenario():
        _, panel = _panel()
        async with FakeThreeXUIServer(panel) as server:
            server.hold_requests()
            call = asyncio.create_task(_disable_us(server, panel))
            await _until(lambda: server.held_requests == 1)
            server.drop_requests()
            with pytest.raises(aiohttp.ClientConnectionError) as failure:
                await call
            assert not isinstance(failure.value, aiohttp.ClientConnectorError)
            await server.wait_connections_closed()
        assert panel.client(US)["enable"] is True
        assert panel.calls == []

    asyncio.run(scenario())


def test_api_down_refuses_connections_and_api_up_reopens_the_same_port():
    async def scenario():
        _, panel = _panel()
        admin = panel.tokens["admin"]
        headers = {"Authorization": f"Bearer {admin}"}
        async with FakeThreeXUIServer(panel) as server:
            port = server.port
            connector = aiohttp.TCPConnector(ssl=server.certificate.client_context())
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    server.base_url + "/panel/api/server/status", headers=headers
                ) as response:
                    assert response.status == 200
                    await response.read()
                server.hold_requests()
                held = asyncio.create_task(_disable_us(server, panel))
                await _until(lambda: server.held_requests == 1)

                panel.api_down()
                assert server.held_requests == 0
                with pytest.raises(RuntimeError):
                    server.deliver_requests()
                await server.wait_connections_closed()
                with pytest.raises(aiohttp.ClientConnectionError):
                    await held
                with pytest.raises(aiohttp.ClientConnectorError) as refused:
                    await _request(
                        server, "GET", "/xui/panel/api/server/status", token=admin
                    )
                assert not isinstance(refused.value, aiohttp.ClientSSLError)

                panel.api_up()
                assert server.port == port
                status, _ = await _request(
                    server, "GET", "/xui/panel/api/server/status", token=admin
                )
                assert status == 200
        assert panel.client(US)["enable"] is True
        assert [call.path for call in panel.calls] == [
            "/panel/api/server/status",
            "/panel/api/server/status",
        ]

    asyncio.run(scenario())


def test_close_drops_held_requests():
    async def scenario():
        _, panel = _panel()
        server = FakeThreeXUIServer(panel)
        await server.start()
        server.hold_requests()
        call = asyncio.create_task(_disable_us(server, panel))
        await _until(lambda: server.held_requests == 1)
        await server.close()
        with pytest.raises(aiohttp.ClientConnectionError):
            await call
        assert server.held_requests == 0
        _, request = _only_request(server)
        assert request.state == "dropped"
        assert panel.client(US)["enable"] is True
        assert panel.calls == []

    asyncio.run(scenario())


def test_close_is_prompt_and_pending_panel_writes_survive():
    async def scenario():
        _, panel = _panel()
        server = FakeThreeXUIServer(panel)
        await server.start()
        panel.stall_inbound(1)
        call = asyncio.create_task(_disable_us(server, panel))
        await _until(lambda: panel.pending_writes == 1)
        started = time.monotonic()
        await server.close()
        assert time.monotonic() - started < 1.0
        with pytest.raises(aiohttp.ClientConnectionError):
            await call
        assert panel.pending_writes == 1
        panel.release_inbound(1)
        assert panel.client(US)["enable"] is False
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_misuse_raises():
    async def scenario():
        _, panel = _panel()
        server = FakeThreeXUIServer(panel)
        with pytest.raises(RuntimeError):
            server.port
        with pytest.raises(RuntimeError):
            server.base_url
        panel.api_down()
        with pytest.raises(RuntimeError):
            await server.start()
        panel.api_up()
        await server.start()
        with pytest.raises(RuntimeError):
            await server.start()
        with pytest.raises(RuntimeError):
            server.deliver_requests()
        with pytest.raises(RuntimeError):
            server.drop_requests()
        server.hold_requests()
        with pytest.raises(RuntimeError):
            server.hold_requests()
        server.drop_requests()
        await server.close()
        with pytest.raises(RuntimeError):
            await server.start()

    asyncio.run(scenario())
