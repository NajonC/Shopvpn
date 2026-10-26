"""Synthetic test world fixtures for composite subscriptions (tasks.md T008; spec FR-002).

Provides plain frozen dataclasses and two factory functions:
- six_node_fixture(): the six-node acceptance fixture with panels A, B, C.
- a_only_offer_fixture(): the initial live A-only offer with five choices.
"""

from dataclasses import dataclass, field
import secrets
import uuid


@dataclass(frozen=True)
class Tenant:
    key: str  # "main" | "reseller"
    tenant_id: str  # "main" | "reseller-7"
    installation_id: str  # str(uuid.uuid4()), new per call; not a secret


@dataclass(frozen=True)
class Customer:
    key: str
    tenant_key: str
    telegram_id: int
    local_user_id: int  # users.id in that tenant's database


@dataclass(frozen=True)
class WebAdmin:
    admin_row_id: int
    username: str
    role: str  # "owner" | "staff"


@dataclass(frozen=True)
class Panel:
    key: str  # "A" | "B" | "C"
    physical_panel_id: str  # str(uuid.uuid4()), new per call; not a secret
    base_url: str
    api_token: str = field(repr=False)  # secrets.token_urlsafe(32)


@dataclass(frozen=True)
class PanelAlias:
    installation_id: str  # the owning tenant's installation_id
    tenant_id: str
    local_panel_server_id: int
    panel_key: str


@dataclass(frozen=True)
class ExternalProxy:
    host: str
    port: int


@dataclass(frozen=True)
class Inbound:
    panel_key: str
    inbound_id: int
    protocol: str  # "vless" | "trojan" | "vmess"
    transport: str  # "tcp" | "ws" | "grpc"
    security: str  # "reality" | "tls"
    listen_port: int
    external_proxies: tuple[ExternalProxy, ...]
    sni: str
    fingerprint: str
    flow: str = ""
    ws_host: str = ""
    ws_path: str = ""
    grpc_service_name: str = ""
    grpc_mode: str = ""
    vmess_cipher: str = ""
    tcp_header_type: str = ""
    reality_public_key: str = field(default="", repr=False)  # REALITY only
    reality_private_key: str = field(default="", repr=False)  # REALITY only
    reality_short_id: str = field(default="", repr=False)  # REALITY only


@dataclass(frozen=True)
class Node:
    key: str
    ordinal: int  # 1-based, the export order
    panel_key: str
    inbound_id: int
    remark: str
    egress: str  # outbound tag on that panel


@dataclass(frozen=True)
class Credential:
    node_key: str
    email: str
    secret_kind: str  # "uuid" (VLESS/VMess) | "password" (Trojan)
    secret: str = field(repr=False)


@dataclass(frozen=True)
class Subscription:
    key: str
    customer_key: str
    allowance_bytes: int
    duration_seconds: int
    node_keys: tuple[str, ...]
    credentials: tuple[Credential, ...]  # one per node, in node order
    url_token: str = field(repr=False)  # secrets.token_urlsafe(32)


@dataclass(frozen=True)
class CompositeFixture:
    tenants: tuple[Tenant, ...]
    customers: tuple[Customer, ...]
    web_admins: tuple[WebAdmin, ...]
    main_owner_telegram_id: int
    panels: tuple[Panel, ...]
    aliases: tuple[PanelAlias, ...]
    inbounds: tuple[Inbound, ...]
    nodes: tuple[Node, ...]
    subscriptions: tuple[Subscription, ...]

    def tenant(self, key: str) -> Tenant:
        for t in self.tenants:
            if t.key == key:
                return t
        raise KeyError(f"Tenant {key!r} not found")

    def customer(self, key: str) -> Customer:
        for c in self.customers:
            if c.key == key:
                return c
        raise KeyError(f"Customer {key!r} not found")

    def panel(self, key: str) -> Panel:
        for p in self.panels:
            if p.key == key:
                return p
        raise KeyError(f"Panel {key!r} not found")

    def inbound(self, panel_key: str, inbound_id: int) -> Inbound:
        for ib in self.inbounds:
            if ib.panel_key == panel_key and ib.inbound_id == inbound_id:
                return ib
        raise KeyError(f"Inbound ({panel_key!r}, {inbound_id!r}) not found")

    def node(self, key: str) -> Node:
        for n in self.nodes:
            if n.key == key:
                return n
        raise KeyError(f"Node {key!r} not found")

    def subscription(self, key: str) -> Subscription:
        for s in self.subscriptions:
            if s.key == key:
                return s
        raise KeyError(f"Subscription {key!r} not found")


GIB = 1_073_741_824
PAID_ALLOWANCE_BYTES = 50 * GIB  # 53_687_091_200
PAID_DURATION_SECONDS = 2_592_000
MAIN_OWNER_TELEGRAM_ID = 9001


def _build_tenants() -> tuple[Tenant, Tenant]:
    return (
        Tenant(key="main", tenant_id="main", installation_id=str(uuid.uuid4())),
        Tenant(key="reseller", tenant_id="reseller-7", installation_id=str(uuid.uuid4())),
    )


def _build_customers() -> tuple[Customer, ...]:
    return (
        Customer(key="ali", tenant_key="main", telegram_id=1001, local_user_id=1),
        Customer(key="sara", tenant_key="main", telegram_id=1002, local_user_id=2),
        Customer(key="ali-r", tenant_key="reseller", telegram_id=1001, local_user_id=3),
        Customer(key="reza-r", tenant_key="reseller", telegram_id=2001, local_user_id=1),
    )


def _build_web_admins() -> tuple[WebAdmin, ...]:
    return (
        WebAdmin(admin_row_id=1001, username="owner", role="owner"),
        WebAdmin(admin_row_id=1002, username="staff", role="staff"),
    )


def _build_inbound_a1() -> Inbound:
    return Inbound(
        panel_key="A",
        inbound_id=1,
        protocol="vless",
        transport="tcp",
        security="reality",
        listen_port=443,
        external_proxies=(ExternalProxy(host="a.example.invalid", port=443),),
        sni="a.example.invalid",
        fingerprint="chrome",
        flow="xtls-rprx-vision",
        reality_public_key=secrets.token_urlsafe(32),
        reality_private_key=secrets.token_urlsafe(32),
        reality_short_id=secrets.token_hex(4),
    )


def six_node_fixture() -> CompositeFixture:
    main_tenant, reseller_tenant = _build_tenants()
    customers = _build_customers()
    web_admins = _build_web_admins()

    panels = (
        Panel(
            key="A",
            physical_panel_id=str(uuid.uuid4()),
            base_url="https://panel-a.example.invalid:2053/xui",
            api_token=secrets.token_urlsafe(32),
        ),
        Panel(
            key="B",
            physical_panel_id=str(uuid.uuid4()),
            base_url="https://panel-b.example.invalid:2053/xui",
            api_token=secrets.token_urlsafe(32),
        ),
        Panel(
            key="C",
            physical_panel_id=str(uuid.uuid4()),
            base_url="https://panel-c.example.invalid:2053/xui",
            api_token=secrets.token_urlsafe(32),
        ),
    )

    aliases = (
        PanelAlias(
            installation_id=main_tenant.installation_id,
            tenant_id=main_tenant.tenant_id,
            local_panel_server_id=1,
            panel_key="A",
        ),
        PanelAlias(
            installation_id=main_tenant.installation_id,
            tenant_id=main_tenant.tenant_id,
            local_panel_server_id=2,
            panel_key="B",
        ),
        PanelAlias(
            installation_id=main_tenant.installation_id,
            tenant_id=main_tenant.tenant_id,
            local_panel_server_id=3,
            panel_key="C",
        ),
        PanelAlias(
            installation_id=reseller_tenant.installation_id,
            tenant_id=reseller_tenant.tenant_id,
            local_panel_server_id=1,
            panel_key="B",
        ),
        PanelAlias(
            installation_id=reseller_tenant.installation_id,
            tenant_id=reseller_tenant.tenant_id,
            local_panel_server_id=9,
            panel_key="A",
        ),
    )

    inbounds = (
        _build_inbound_a1(),
        Inbound(
            panel_key="B",
            inbound_id=1,
            protocol="vless",
            transport="ws",
            security="tls",
            listen_port=8443,
            external_proxies=(ExternalProxy(host="cdn-b.example.invalid", port=443),),
            sni="cdn-b.example.invalid",
            fingerprint="chrome",
            ws_host="cdn-b.example.invalid",
            ws_path="/vless-ws",
        ),
        Inbound(
            panel_key="B",
            inbound_id=2,
            protocol="trojan",
            transport="grpc",
            security="tls",
            listen_port=2083,
            external_proxies=(ExternalProxy(host="b.example.invalid", port=2083),),
            sni="b.example.invalid",
            fingerprint="chrome",
            grpc_service_name="trojan-grpc",
            grpc_mode="gun",
        ),
        Inbound(
            panel_key="C",
            inbound_id=1,
            protocol="vmess",
            transport="tcp",
            security="tls",
            listen_port=8443,
            external_proxies=(ExternalProxy(host="c.example.invalid", port=8443),),
            sni="c.example.invalid",
            fingerprint="chrome",
            vmess_cipher="auto",
            tcp_header_type="none",
        ),
    )

    nodes = (
        Node(key="A-US", ordinal=1, panel_key="A", inbound_id=1, remark="🇺🇸 US - Reality", egress="out-us"),
        Node(key="A-DE", ordinal=2, panel_key="A", inbound_id=1, remark="🇩🇪 DE - Reality", egress="out-de"),
        Node(key="A-RU", ordinal=3, panel_key="A", inbound_id=1, remark="🇷🇺 RU - Reality", egress="out-ru"),
        Node(key="B-CDN", ordinal=4, panel_key="B", inbound_id=1, remark="Server B - CDN", egress="out-b"),
        Node(key="B-gRPC", ordinal=5, panel_key="B", inbound_id=2, remark="Server B - gRPC", egress="out-b"),
        Node(key="C-Direct", ordinal=6, panel_key="C", inbound_id=1, remark="Server C - Direct", egress="direct"),
    )

    node_keys = tuple(n.key for n in nodes)

    node_suffixes = {
        "A-US": "us",
        "A-DE": "de",
        "A-RU": "ru",
        "B-CDN": "cdn",
        "B-gRPC": "grpc",
        "C-Direct": "direct",
    }

    def make_subscription(sub_key: str, customer_key: str, n: int) -> Subscription:
        credentials = []
        for nk in node_keys:
            suffix = node_suffixes[nk]
            email = f"{customer_key}_sub{n}_{suffix}"
            if nk == "B-gRPC":
                credentials.append(
                    Credential(
                        node_key=nk,
                        email=email,
                        secret_kind="password",
                        secret=secrets.token_urlsafe(18),
                    )
                )
            else:
                credentials.append(
                    Credential(
                        node_key=nk,
                        email=email,
                        secret_kind="uuid",
                        secret=str(uuid.uuid4()),
                    )
                )
        return Subscription(
            key=sub_key,
            customer_key=customer_key,
            allowance_bytes=PAID_ALLOWANCE_BYTES,
            duration_seconds=PAID_DURATION_SECONDS,
            node_keys=node_keys,
            credentials=tuple(credentials),
            url_token=secrets.token_urlsafe(32),
        )

    subscriptions = (
        make_subscription("ali-1", "ali", 1),
        make_subscription("ali-2", "ali", 2),
        make_subscription("sara-1", "sara", 1),
    )

    return CompositeFixture(
        tenants=(main_tenant, reseller_tenant),
        customers=customers,
        web_admins=web_admins,
        main_owner_telegram_id=MAIN_OWNER_TELEGRAM_ID,
        panels=panels,
        aliases=aliases,
        inbounds=inbounds,
        nodes=nodes,
        subscriptions=subscriptions,
    )


def a_only_offer_fixture() -> CompositeFixture:
    main_tenant, reseller_tenant = _build_tenants()
    customers = _build_customers()
    web_admins = _build_web_admins()

    panels = (
        Panel(
            key="A",
            physical_panel_id=str(uuid.uuid4()),
            base_url="https://panel-a.example.invalid:2053/xui",
            api_token=secrets.token_urlsafe(32),
        ),
    )

    aliases = (
        PanelAlias(
            installation_id=main_tenant.installation_id,
            tenant_id=main_tenant.tenant_id,
            local_panel_server_id=1,
            panel_key="A",
        ),
        PanelAlias(
            installation_id=reseller_tenant.installation_id,
            tenant_id=reseller_tenant.tenant_id,
            local_panel_server_id=9,
            panel_key="A",
        ),
    )

    inbounds = (_build_inbound_a1(),)

    nodes = (
        Node(key="A-US", ordinal=1, panel_key="A", inbound_id=1, remark="🇺🇸 US - Reality", egress="out-us"),
        Node(key="A-DE", ordinal=2, panel_key="A", inbound_id=1, remark="🇩🇪 DE - Reality", egress="out-de"),
        Node(key="A-RU", ordinal=3, panel_key="A", inbound_id=1, remark="🇷🇺 RU - Reality", egress="out-ru"),
        Node(key="A-NL", ordinal=4, panel_key="A", inbound_id=1, remark="🇳🇱 NL - Reality", egress="out-nl"),
        Node(key="A-FI", ordinal=5, panel_key="A", inbound_id=1, remark="🇫🇮 FI - Reality", egress="out-fi"),
    )

    node_keys = tuple(n.key for n in nodes)

    node_suffixes = {
        "A-US": "us",
        "A-DE": "de",
        "A-RU": "ru",
        "A-NL": "nl",
        "A-FI": "fi",
    }

    credentials = tuple(
        Credential(
            node_key=nk,
            email=f"ali_sub1_{node_suffixes[nk]}",
            secret_kind="uuid",
            secret=str(uuid.uuid4()),
        )
        for nk in node_keys
    )

    subscriptions = (
        Subscription(
            key="ali-1",
            customer_key="ali",
            allowance_bytes=PAID_ALLOWANCE_BYTES,
            duration_seconds=PAID_DURATION_SECONDS,
            node_keys=node_keys,
            credentials=credentials,
            url_token=secrets.token_urlsafe(32),
        ),
    )

    return CompositeFixture(
        tenants=(main_tenant, reseller_tenant),
        customers=customers,
        web_admins=web_admins,
        main_owner_telegram_id=MAIN_OWNER_TELEGRAM_ID,
        panels=panels,
        aliases=aliases,
        inbounds=inbounds,
        nodes=nodes,
        subscriptions=subscriptions,
    )
