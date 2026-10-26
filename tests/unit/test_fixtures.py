"""Structure of the synthetic fixture factories (tasks.md T008; spec FR-002)."""

import dataclasses

import pytest

from tests._harness.fixtures import (
    PAID_ALLOWANCE_BYTES,
    PAID_DURATION_SECONDS,
    Customer,
    ExternalProxy,
    Node,
    PanelAlias,
    WebAdmin,
    a_only_offer_fixture,
    six_node_fixture,
)


def test_six_node_panels_and_aliases():
    six = six_node_fixture()
    panel_keys = tuple(p.key for p in six.panels)
    assert panel_keys == ("A", "B", "C")
    assert six.panel("A").base_url == "https://panel-a.example.invalid:2053/xui"
    assert six.panel("B").base_url == "https://panel-b.example.invalid:2053/xui"
    assert six.panel("C").base_url == "https://panel-c.example.invalid:2053/xui"

    main_tenant = six.tenant("main")
    reseller_tenant = six.tenant("reseller")
    assert main_tenant.installation_id != reseller_tenant.installation_id

    expected_aliases = (
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
    assert six.aliases == expected_aliases


def test_six_node_inbounds():
    six = six_node_fixture()
    inbound_keys = [(ib.panel_key, ib.inbound_id) for ib in six.inbounds]
    assert inbound_keys == [("A", 1), ("B", 1), ("B", 2), ("C", 1)]
    # Inbound id 1 exists on A, B and C:
    assert {ib.panel_key for ib in six.inbounds if ib.inbound_id == 1} == {"A", "B", "C"}

    a1 = six.inbound("A", 1)
    assert a1.protocol == "vless"
    assert a1.transport == "tcp"
    assert a1.security == "reality"
    assert a1.listen_port == 443
    assert a1.external_proxies == (ExternalProxy(host="a.example.invalid", port=443),)
    assert a1.sni == "a.example.invalid"
    assert a1.fingerprint == "chrome"
    assert a1.flow == "xtls-rprx-vision"

    b1 = six.inbound("B", 1)
    assert b1.protocol == "vless"
    assert b1.transport == "ws"
    assert b1.security == "tls"
    assert b1.listen_port == 8443
    assert b1.external_proxies == (ExternalProxy(host="cdn-b.example.invalid", port=443),)
    assert b1.sni == "cdn-b.example.invalid"
    assert b1.fingerprint == "chrome"
    assert b1.ws_host == "cdn-b.example.invalid"
    assert b1.ws_path == "/vless-ws"

    b2 = six.inbound("B", 2)
    assert b2.protocol == "trojan"
    assert b2.transport == "grpc"
    assert b2.security == "tls"
    assert b2.listen_port == 2083
    assert b2.external_proxies == (ExternalProxy(host="b.example.invalid", port=2083),)
    assert b2.sni == "b.example.invalid"
    assert b2.fingerprint == "chrome"
    assert b2.grpc_service_name == "trojan-grpc"
    assert b2.grpc_mode == "gun"

    c1 = six.inbound("C", 1)
    assert c1.protocol == "vmess"
    assert c1.transport == "tcp"
    assert c1.security == "tls"
    assert c1.listen_port == 8443
    assert c1.external_proxies == (ExternalProxy(host="c.example.invalid", port=8443),)
    assert c1.sni == "c.example.invalid"
    assert c1.fingerprint == "chrome"
    assert c1.vmess_cipher == "auto"
    assert c1.tcp_header_type == "none"


def test_six_node_nodes():
    six = six_node_fixture()
    expected_nodes = (
        Node(key="A-US", ordinal=1, panel_key="A", inbound_id=1, remark="🇺🇸 US - Reality", egress="out-us"),
        Node(key="A-DE", ordinal=2, panel_key="A", inbound_id=1, remark="🇩🇪 DE - Reality", egress="out-de"),
        Node(key="A-RU", ordinal=3, panel_key="A", inbound_id=1, remark="🇷🇺 RU - Reality", egress="out-ru"),
        Node(key="B-CDN", ordinal=4, panel_key="B", inbound_id=1, remark="Server B - CDN", egress="out-b"),
        Node(key="B-gRPC", ordinal=5, panel_key="B", inbound_id=2, remark="Server B - gRPC", egress="out-b"),
        Node(key="C-Direct", ordinal=6, panel_key="C", inbound_id=1, remark="Server C - Direct", egress="direct"),
    )
    assert six.nodes == expected_nodes

    a_nodes = [n for n in six.nodes if n.panel_key == "A"]
    assert len(a_nodes) == 3
    for n in a_nodes:
        assert (n.panel_key, n.inbound_id) == ("A", 1)


def test_six_node_subscriptions():
    six = six_node_fixture()
    assert tuple(s.key for s in six.subscriptions) == ("ali-1", "ali-2", "sara-1")
    assert [s.customer_key for s in six.subscriptions] == ["ali", "ali", "sara"]

    expected_node_keys = ("A-US", "A-DE", "A-RU", "B-CDN", "B-gRPC", "C-Direct")
    expected_kinds = ["uuid", "uuid", "uuid", "uuid", "password", "uuid"]

    for sub in six.subscriptions:
        assert sub.allowance_bytes == 53_687_091_200
        assert sub.allowance_bytes == PAID_ALLOWANCE_BYTES
        assert sub.duration_seconds == 2_592_000
        assert sub.duration_seconds == PAID_DURATION_SECONDS
        assert sub.node_keys == expected_node_keys
        assert [c.node_key for c in sub.credentials] == list(expected_node_keys)
        assert [c.secret_kind for c in sub.credentials] == expected_kinds

    ali1 = six.subscription("ali-1")
    assert [c.email for c in ali1.credentials] == [
        "ali_sub1_us",
        "ali_sub1_de",
        "ali_sub1_ru",
        "ali_sub1_cdn",
        "ali_sub1_grpc",
        "ali_sub1_direct",
    ]

    ali2 = six.subscription("ali-2")
    assert [c.email for c in ali2.credentials] == [
        "ali_sub2_us",
        "ali_sub2_de",
        "ali_sub2_ru",
        "ali_sub2_cdn",
        "ali_sub2_grpc",
        "ali_sub2_direct",
    ]

    sara1 = six.subscription("sara-1")
    assert [c.email for c in sara1.credentials] == [
        "sara_sub1_us",
        "sara_sub1_de",
        "sara_sub1_ru",
        "sara_sub1_cdn",
        "sara_sub1_grpc",
        "sara_sub1_direct",
    ]


def test_tenants_customers_and_admins():
    six = six_node_fixture()
    assert [t.key for t in six.tenants] == ["main", "reseller"]
    assert [t.tenant_id for t in six.tenants] == ["main", "reseller-7"]

    expected_customers = (
        Customer(key="ali", tenant_key="main", telegram_id=1001, local_user_id=1),
        Customer(key="sara", tenant_key="main", telegram_id=1002, local_user_id=2),
        Customer(key="ali-r", tenant_key="reseller", telegram_id=1001, local_user_id=3),
        Customer(key="reza-r", tenant_key="reseller", telegram_id=2001, local_user_id=1),
    )
    assert six.customers == expected_customers

    # ali and ali-r share telegram id 1001
    assert six.customer("ali").telegram_id == six.customer("ali-r").telegram_id == 1001
    # ali and reza-r share local id 1
    assert six.customer("ali").local_user_id == six.customer("reza-r").local_user_id == 1

    expected_admins = (
        WebAdmin(admin_row_id=1001, username="owner", role="owner"),
        WebAdmin(admin_row_id=1002, username="staff", role="staff"),
    )
    assert six.web_admins == expected_admins
    assert six.main_owner_telegram_id == 9001


def test_a_only_offer():
    a5 = a_only_offer_fixture()
    six = six_node_fixture()

    assert len(a5.panels) == 1
    assert a5.panels[0].key == "A"
    assert a5.panels[0].base_url == "https://panel-a.example.invalid:2053/xui"

    main_tenant = a5.tenant("main")
    reseller_tenant = a5.tenant("reseller")
    assert a5.aliases == (
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

    assert len(a5.inbounds) == 1
    inbound = a5.inbounds[0]
    six_a1 = six.inbound("A", 1)
    assert inbound.panel_key == six_a1.panel_key == "A"
    assert inbound.inbound_id == six_a1.inbound_id == 1
    assert inbound.protocol == six_a1.protocol == "vless"
    assert inbound.transport == six_a1.transport == "tcp"
    assert inbound.security == six_a1.security == "reality"
    assert inbound.listen_port == six_a1.listen_port == 443
    assert inbound.external_proxies == six_a1.external_proxies
    assert inbound.sni == six_a1.sni
    assert inbound.fingerprint == six_a1.fingerprint
    assert inbound.flow == six_a1.flow

    expected_nodes = (
        Node(key="A-US", ordinal=1, panel_key="A", inbound_id=1, remark="🇺🇸 US - Reality", egress="out-us"),
        Node(key="A-DE", ordinal=2, panel_key="A", inbound_id=1, remark="🇩🇪 DE - Reality", egress="out-de"),
        Node(key="A-RU", ordinal=3, panel_key="A", inbound_id=1, remark="🇷🇺 RU - Reality", egress="out-ru"),
        Node(key="A-NL", ordinal=4, panel_key="A", inbound_id=1, remark="🇳🇱 NL - Reality", egress="out-nl"),
        Node(key="A-FI", ordinal=5, panel_key="A", inbound_id=1, remark="🇫🇮 FI - Reality", egress="out-fi"),
    )
    assert a5.nodes == expected_nodes

    assert len(a5.subscriptions) == 1
    sub = a5.subscriptions[0]
    assert sub.key == "ali-1"
    assert sub.customer_key == "ali"
    assert sub.allowance_bytes == PAID_ALLOWANCE_BYTES
    assert sub.duration_seconds == PAID_DURATION_SECONDS
    assert sub.node_keys == ("A-US", "A-DE", "A-RU", "A-NL", "A-FI")
    assert len(sub.credentials) == 5
    assert [c.secret_kind for c in sub.credentials] == ["uuid"] * 5
    assert [c.email for c in sub.credentials] == [
        "ali_sub1_us",
        "ali_sub1_de",
        "ali_sub1_ru",
        "ali_sub1_nl",
        "ali_sub1_fi",
    ]


def test_lookups():
    six = six_node_fixture()
    assert six.node("B-gRPC").inbound_id == 2
    assert six.inbound("B", 2).protocol == "trojan"
    assert six.customer("reza-r").telegram_id == 2001
    assert six.subscription("sara-1").customer_key == "sara"

    with pytest.raises(KeyError):
        six.tenant("unknown")
    with pytest.raises(KeyError):
        six.customer("unknown")
    with pytest.raises(KeyError):
        six.panel("unknown")
    with pytest.raises(KeyError):
        six.inbound("X", 999)
    with pytest.raises(KeyError):
        six.node("unknown")
    with pytest.raises(KeyError):
        six.subscription("unknown")


def test_frozen():
    six = six_node_fixture()
    node = six.nodes[0]
    sub = six.subscriptions[0]

    with pytest.raises(dataclasses.FrozenInstanceError):
        node.remark = "other"  # type: ignore[misc]

    with pytest.raises(dataclasses.FrozenInstanceError):
        sub.allowance_bytes = 123  # type: ignore[misc]

    with pytest.raises(dataclasses.FrozenInstanceError):
        six.main_owner_telegram_id = 123  # type: ignore[misc]


def test_structure_repeats():
    six1 = six_node_fixture()
    six2 = six_node_fixture()
    assert six1.nodes == six2.nodes
    assert six1.web_admins == six2.web_admins
    assert six1.customers == six2.customers
