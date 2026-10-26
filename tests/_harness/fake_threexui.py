"""A controlled standalone 3x-UI v3.9.0 panel: substitute, not evidence.

The implementation is intentionally limited to the routes and data used by
the composite tests. Basis for its behavior:

* Lab (RX-MAN-001/GA-MAN-002 runtime): a missing client traffic lookup returns
  a successful null object; Xray status reports uptime in seconds; disabling
  an enabled client and deleting a client can restart Xray; resetting settings
  restores the panel defaults.
* Source (v3.9.0 source reading): API route authentication and token scopes,
  the JSON response envelope, client create/update validation and defaults,
  traffic view fields, and the restart-on-disable setting.
* Fake choice: the inbound JSON projection, the three exposed setting values,
  default values for unprovided update fields, and the limited server status
  object. These views omit fields and behavior outside this test model.

Any recognized real route or behavior outside this model raises
``FakeNotModelled`` instead of returning an invented success.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
import secrets
import uuid

from tests._harness.clock import FakeClock
from tests._harness.fixtures import CompositeFixture, Inbound


EVIDENCE_LABEL = "substitute, not evidence"


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


class _RequestFailure(Exception):
    """A modeled API failure represented by the panel's JSON envelope."""


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
    ("POST", "/panel/api/clients/resetTraffic/([^/]+)"),
    ("POST", "/panel/api/clients/updateTraffic/([^/]+)"),
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
            inbound.inbound_id: {"source": inbound, "clients": []}
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
        self._next_traffic_id = 1
        self._settings = self._default_settings()
        self._xray_started_ms = clock.true_now_ms()
        self._xray_restarts: list[int] = []

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

    async def handle(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        query: dict[str, str] | None = None,
        body: object = None,
    ) -> FakeResponse:
        """Authenticate and handle one API call without performing I/O."""
        route, params = self._resolve_route(method, path)
        if not path.startswith("/panel/api/") or route is None:
            self._record(method, path, None)
            return FakeResponse(404, None)

        if token is None:
            self._record(method, path, None)
            return FakeResponse(404, None)
        scope = next((name for name, value in self._tokens.items() if token == value), None)
        if scope is None:
            self._record(method, path, None)
            return FakeResponse(401, None)

        self._record(method, path, scope)
        if not self._scope_permits(scope, method, path, route):
            return FakeResponse(
                403,
                {
                    "success": False,
                    "msg": "this API token is not permitted to access this endpoint",
                },
            )
        if route in {
            "clients_get",
            "clients_get_by_tgid",
            "clients_attach",
            "clients_detach",
            "clients_external_links",
            "clients_reset_traffic",
        }:
            raise FakeNotModelled(f"{method} {path}")
        if route == "unmodelled":
            raise FakeNotModelled(f"{method} {path}")

        try:
            obj = self._run_route(route, params, query or {}, body)
        except _RequestFailure as exc:
            return self._failure(str(exc))
        return self._success(obj)

    def seed_client(self, inbound_ids: list[int], client: dict) -> None:
        """Add one client directly, without recording an API call or restart."""
        try:
            self._add_client({"inboundIds": inbound_ids, "client": client})
        except _RequestFailure as exc:
            raise ValueError(str(exc)) from None

    def seed_subscription(
        self, fixture: CompositeFixture, subscription_key: str, *, enable: bool = True
    ) -> None:
        """Seed the subscription credentials whose nodes belong to this panel."""
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
        matches = self._find_clients(email)
        return self._client_json(matches[0][2]) if matches else None

    def inbound_clients(self, inbound_id: int) -> list[dict]:
        inbound = self._inbounds[inbound_id]
        return [self._client_json(client) for client in inbound["clients"]]

    def setting(self, name: str) -> object:
        return deepcopy(self._settings[name])

    def set_setting(self, name: str, value: object) -> None:
        if name not in self._settings:
            raise KeyError(name)
        self._settings[name] = deepcopy(value)

    def reset_settings(self) -> None:
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
                if path.startswith("/panel/api/clients/resetTraffic/"):
                    return "clients_reset_traffic", match.groups()
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
            record = self._traffic.get(params[0])
            return deepcopy(record) if record is not None else None
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
        record["email"] = new_email
        record["enable"] = updated["enable"]
        record["expiryTime"] = updated["expiryTime"]
        record["total"] = updated["totalGB"]
        record["reset"] = updated["reset"]
        self._traffic[new_email] = record

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
        if query.get("keepTraffic") != "1":
            self._traffic.pop(email, None)
        self._maybe_restart()

    def _maybe_restart(self) -> None:
        if self._settings["restartXrayOnClientDisable"]:
            now = self._clock.true_now_ms()
            self._xray_restarts.append(now)
            self._xray_started_ms = now

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
            "up": 0,
            "down": 0,
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
