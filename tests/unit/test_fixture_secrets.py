"""Secret handling of the synthetic fixture factories (tasks.md T008; constitution III).

Secrets are generated per run, never shown by repr and never written to disk.
"""

import base64
import builtins
import io
import os
import re
import uuid

import pytest

from tests._harness.fixtures import a_only_offer_fixture, six_node_fixture

FACTORIES = [six_node_fixture, a_only_offer_fixture]


def _secrets(fixture):
    """Every secret value in a fixture, in a stable order."""
    values = [panel.api_token for panel in fixture.panels]
    for inbound in fixture.inbounds:
        if inbound.security == "reality":
            values += [
                inbound.reality_public_key,
                inbound.reality_private_key,
                inbound.reality_short_id,
            ]
    for subscription in fixture.subscriptions:
        values.append(subscription.url_token)
        values += [credential.secret for credential in subscription.credentials]
    return values


def _urlsafe_bytes(value):
    """Decode unpadded base64url and return the raw bytes."""
    assert re.fullmatch(r"[A-Za-z0-9_-]+", value), "not base64url"
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@pytest.mark.parametrize("factory", FACTORIES)
def test_every_secret_is_present_and_distinct(factory):
    values = _secrets(factory())
    assert all(isinstance(value, str) and value for value in values)
    assert len(set(values)) == len(values)


@pytest.mark.parametrize("factory", FACTORIES)
def test_secrets_are_new_on_every_call(factory):
    first = _secrets(factory())
    second = _secrets(factory())
    assert len(first) == len(second)
    assert set(first).isdisjoint(second)


@pytest.mark.parametrize("factory", FACTORIES)
def test_secret_formats(factory):
    fixture = factory()
    for panel in fixture.panels:
        assert len(_urlsafe_bytes(panel.api_token)) == 32
    for subscription in fixture.subscriptions:
        assert len(_urlsafe_bytes(subscription.url_token)) == 32
        for credential in subscription.credentials:
            if credential.secret_kind == "uuid":
                assert uuid.UUID(credential.secret).version == 4
                assert str(uuid.UUID(credential.secret)) == credential.secret
            else:
                assert credential.secret_kind == "password"
                assert len(_urlsafe_bytes(credential.secret)) == 18
    reality = [inbound for inbound in fixture.inbounds if inbound.security == "reality"]
    assert reality
    for inbound in reality:
        assert len(_urlsafe_bytes(inbound.reality_public_key)) == 32
        assert len(_urlsafe_bytes(inbound.reality_private_key)) == 32
        assert re.fullmatch(r"[0-9a-f]{8}", inbound.reality_short_id)


def test_only_reality_inbounds_carry_reality_secrets():
    for inbound in six_node_fixture().inbounds:
        if inbound.security != "reality":
            assert inbound.reality_public_key == ""
            assert inbound.reality_private_key == ""
            assert inbound.reality_short_id == ""


@pytest.mark.parametrize("factory", FACTORIES)
def test_repr_hides_every_secret(factory):
    fixture = factory()
    text = repr(fixture)
    assert "Credential(" in text and "Panel(" in text
    for value in _secrets(fixture):
        assert value not in text


def test_trojan_credential_is_the_only_password():
    subscription = six_node_fixture().subscription("ali-1")
    kinds = {c.node_key: c.secret_kind for c in subscription.credentials}
    assert kinds == {
        "A-US": "uuid",
        "A-DE": "uuid",
        "A-RU": "uuid",
        "B-CDN": "uuid",
        "B-gRPC": "password",
        "C-Direct": "uuid",
    }


def test_factories_write_nothing(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("fixture factory opened a file")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(io, "open", forbidden)
    monkeypatch.setattr(os, "open", forbidden)
    for factory in FACTORIES:
        factory()
