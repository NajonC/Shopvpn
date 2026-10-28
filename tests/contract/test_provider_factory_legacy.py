"""Characterize the legacy panel-provider factory and shared provider contract at commit cadd522.

Baseline: ``.venv/bin/python -m pytest tests/contract/test_provider_factory_legacy.py --network=deny``.

No substitutes: the tests only import and inspect the providers and call pure helpers.
Known-unsafe list:
(a) a server row without `panel_type` raises `KeyError`, not `PanelError` (case 5);
(b) three providers return `None` from `rename_user` although the base annotation says `str` (case 9);
(c) a full renewal that keeps the remaining volume but adds no volume shrinks the limit to the remaining volume, and a full replacement renewal that adds no volume keeps the old limit (case 14).
The only caller passing `preserve_remaining=True` is `renewal_engine.execute_renewal` (manual full renewal), pinned in `tests/characterization/test_legacy_renewal_reminders.py`.
"""

import asyncio
import dataclasses
import inspect

import pytest

import panel_providers
from panel_providers import base
from panel_providers._http import gb_to_bytes, new_limit_bytes

GIB = 1024 ** 3
IDENTIFIERS = ["pasarguard", "3xui", "marzban", "marzneshin", "hiddify", "alireza", "rebecca", "sui", "wgdashboard", "mikrotik", "ibsng"]
CLASS_NAMES = {
    "pasarguard": "PasarguardProvider", "3xui": "ThreeXUIProvider", "marzban": "MarzbanProvider",
    "marzneshin": "MarzneshinProvider", "hiddify": "HiddifyProvider", "alireza": "AlirezaProvider",
    "rebecca": "RebeccaProvider", "sui": "SUIProvider", "wgdashboard": "WGDashboardProvider",
    "mikrotik": "MikroTikProvider", "ibsng": "IBSngProvider",
}
LABELS = {
    "pasarguard": "PasarGuard", "3xui": "3X-UI", "marzban": "Marzban", "marzneshin": "Marzneshin",
    "hiddify": "Hiddify", "alireza": "Alireza X-UI", "rebecca": "Rebecca", "sui": "S-UI",
    "wgdashboard": "WGDashboard", "mikrotik": "MikroTik", "ibsng": "IBSng",
}
UNSUPPORTED_TYPE = "نوع پنل «{}» پشتیبانی نمی\u200cشود"
NO_SET_ENABLED = "این نوع پنل از فعال/غیرفعال کردن مستقیم کاربر پشتیبانی نمی\u200cکند."
NO_RENAME = "این نوع پنل از تغییر نام کاربر روی خود\u0650 پنل پشتیبانی نمی\u200cکند."
ABSTRACT = {"create_user", "delete_user", "get_user", "get_user_usage", "revoke_credentials", "test_connection", "update_user"}
SET_ENABLED_OVERRIDES = {"pasarguard", "3xui", "marzban", "marzneshin", "hiddify", "alireza", "rebecca", "sui"}
RENAME_OVERRIDES = {"3xui", "marzneshin", "hiddify", "alireza"}
P = base.PanelUserResult
E = inspect.Parameter.empty
BASE_SIGNATURES = {
    # method: ([(name, default, annotation), ...] without self, return annotation)
    "create_user": ([("username", E, str), ("volume_gb", E, int), ("duration_days", E, int)], P),
    "delete_user": ([("username", E, str)], bool),
    "get_user_usage": ([("username", E, str)], dict),
    "get_user": ([("username", E, str)], P),
    "update_user": ([("username", E, str), ("add_volume_gb", 0, float), ("add_days", 0, int), ("reset_usage", False, bool), ("preserve_remaining", False, bool)], P),
    "revoke_credentials": ([("username", E, str)], P),
    "test_connection": ([], bool),
    "set_enabled": ([("username", E, str), ("enabled", E, bool)], None),
    "rename_user": ([("username", E, str), ("new_username", E, str)], str),
}


def params(func):
    return [(p.name, p.default, p.annotation) for p in inspect.signature(func).parameters.values()][1:]


# Case 1
def test_registry_has_the_eleven_identifiers_in_order():
    assert list(panel_providers.PROVIDERS) == IDENTIFIERS
    assert {k: c.__name__ for k, c in panel_providers.PROVIDERS.items()} == CLASS_NAMES


# Case 2
def test_labels_cover_the_same_identifiers():
    assert panel_providers.PANEL_TYPE_LABELS == LABELS
    assert list(panel_providers.PANEL_TYPE_LABELS) == IDENTIFIERS


# Case 3
@pytest.mark.parametrize("ident", IDENTIFIERS, ids=IDENTIFIERS)
def test_get_provider_builds_the_registered_class(ident):
    server = {"panel_type": ident}
    provider = panel_providers.get_provider(server)
    assert type(provider) is panel_providers.PROVIDERS[ident]
    assert isinstance(provider, base.BasePanelProvider)
    assert provider.server is server
    assert type(provider).__mro__[1] is base.BasePanelProvider


# Case 4
@pytest.mark.parametrize("value", ["marzban2", "", "3XUI"], ids=["marzban2", "empty", "3XUI"])
def test_unknown_type_fails_with_panel_error(value):
    with pytest.raises(base.PanelError) as exc_info:
        panel_providers.get_provider({"panel_type": value})
    exc = exc_info.value
    assert type(exc) is base.PanelError
    assert str(exc) == UNSUPPORTED_TYPE.format(value)


# Case 5
def test_missing_panel_type_raises_key_error():
    with pytest.raises(KeyError) as exc_info:
        panel_providers.get_provider({})
    exc = exc_info.value
    assert exc.args == ("panel_type",)
    assert not isinstance(exc, base.PanelError)


# Case 6
def test_result_and_error_types():
    assert [(f.name, f.type, f.default) for f in dataclasses.fields(P)] == [
        ("username", str, dataclasses.MISSING),
        ("subscription_url", str, dataclasses.MISSING),
        ("raw", dict, None),
    ]
    assert P("u1", "https://sub.example.invalid/u1").raw is None
    assert P("u1", "x") == P("u1", "x")
    assert base.PanelError.__bases__ == (Exception,)
    assert base.PanelUsernameTakenError.__bases__ == (base.PanelError,)
    assert panel_providers.PanelError is base.PanelError
    assert panel_providers.PanelUserResult is base.PanelUserResult
    assert panel_providers.PanelUsernameTakenError is base.PanelUsernameTakenError
    assert panel_providers.BasePanelProvider is base.BasePanelProvider


# Case 7
def test_base_class_is_abstract():
    assert base.BasePanelProvider.__abstractmethods__ == frozenset(ABSTRACT)
    with pytest.raises(TypeError):
        base.BasePanelProvider({"panel_type": "3xui"})
    assert params(base.BasePanelProvider.__init__) == [("server", E, E)]


# Case 8
def test_base_signatures():
    for name, (expected_params, ret) in BASE_SIGNATURES.items():
        method = getattr(base.BasePanelProvider, name)
        assert params(method) == expected_params
        assert inspect.signature(method).return_annotation is ret
        assert inspect.iscoroutinefunction(method)


# Case 9
@pytest.mark.parametrize("ident", IDENTIFIERS, ids=IDENTIFIERS)
def test_every_provider_keeps_the_base_signatures(ident):
    cls = panel_providers.PROVIDERS[ident]
    for name, (expected_params, expected_ret) in BASE_SIGNATURES.items():
        method = getattr(cls, name)
        assert params(method) == expected_params
        assert inspect.iscoroutinefunction(method)
        sig = inspect.signature(method)
        if name == "rename_user" and ident in {"3xui", "hiddify", "alireza"}:
            assert sig.return_annotation is None
        else:
            assert sig.return_annotation == expected_ret


# Case 10
def test_optional_capability_overrides():
    assert {k for k, c in panel_providers.PROVIDERS.items() if "set_enabled" in c.__dict__} == SET_ENABLED_OVERRIDES
    assert {k for k, c in panel_providers.PROVIDERS.items() if "rename_user" in c.__dict__} == RENAME_OVERRIDES


# Case 11
@pytest.mark.parametrize(
    "ident",
    [i for i in IDENTIFIERS if i not in SET_ENABLED_OVERRIDES],
    ids=[i for i in IDENTIFIERS if i not in SET_ENABLED_OVERRIDES],
)
def test_default_set_enabled_fails_explicitly(ident):
    provider = panel_providers.get_provider({"panel_type": ident})
    with pytest.raises(base.PanelError) as exc_info:
        asyncio.run(provider.set_enabled("u1", False))
    exc = exc_info.value
    assert str(exc) == NO_SET_ENABLED


# Case 12
@pytest.mark.parametrize(
    "ident",
    [i for i in IDENTIFIERS if i not in RENAME_OVERRIDES],
    ids=[i for i in IDENTIFIERS if i not in RENAME_OVERRIDES],
)
def test_default_rename_user_fails_explicitly(ident):
    provider = panel_providers.get_provider({"panel_type": ident})
    with pytest.raises(base.PanelError) as exc_info:
        asyncio.run(provider.rename_user("u1", "u2"))
    exc = exc_info.value
    assert str(exc) == NO_RENAME


# Case 13
def test_volume_units_are_binary_gigabytes():
    assert gb_to_bytes(1) == 1073741824
    assert gb_to_bytes(0.5) == 536870912
    assert gb_to_bytes("2") == 2147483648
    assert gb_to_bytes(0) == 0
    assert gb_to_bytes(1e-10) == 0


# Case 14
@pytest.mark.parametrize(
    ("current", "used", "add_gb", "reset_usage", "preserve_remaining", "expected"),
    [
        (10 * GIB, 3 * GIB, 20, False, False, 30 * GIB),
        (10 * GIB, 3 * GIB, 20, False, True, 30 * GIB),
        (10 * GIB, 3 * GIB, 20, True, False, 20 * GIB),
        (10 * GIB, 3 * GIB, 20, True, True, 27 * GIB),
        (10 * GIB, 12 * GIB, 20, True, True, 20 * GIB),
        (10 * GIB, 3 * GIB, 0, True, False, 10 * GIB),
        (10 * GIB, 3 * GIB, 0, True, True, 7 * GIB),
        (None, None, 0.5, False, False, 536870912),
        (0, 0, 0, False, False, 0),
        (10 * GIB, None, None, True, True, 10 * GIB),
    ],
    ids=[
        "additive",
        "preserve_ignored_without_reset",
        "full_replacement",
        "full_carryover",
        "carryover_overused_clamps_to_zero",
        "replacement_without_volume_keeps_limit",
        "carryover_without_volume_shrinks_to_remaining",
        "none_values_count_as_zero",
        "all_zero",
        "none_add_and_used",
    ],
)
def test_new_limit_rule(current, used, add_gb, reset_usage, preserve_remaining, expected):
    assert new_limit_bytes(current, used, add_gb, reset_usage, preserve_remaining) == expected
