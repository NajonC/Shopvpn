"""T050v: Telegram custom-plan discovery and selection composite guards."""

from __future__ import annotations

import asyncio
import re
from types import SimpleNamespace

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()

import database
import handlers_user
from states import CustomConfigFlow
from tests._harness.legacy_bot import (
    FakeCallbackQuery,
    FakeMessage,
    FakeUser,
    TelegramLog,
    callback_rows,
    find_handler,
    make_state,
)
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests.integration.test_composite_legacy_guards import as_row

USER_ID = 5101
EXACT_UNAVAILABLE_ALERT = "این پلن دیگر در دسترس نیست."
EXACT_USERNAME_PROMPT = (
    "🛠 ساخت کانفیگ شخصی\n\n"
    "لطفاً یک نام کاربری دلخواه برای کانفیگ خود ارسال کنید، یا از دکمه‌ی زیر یک نام تصادفی بگیر.\n"
    "فقط حروف انگلیسی، عدد و آندرلاین مجاز است (بین ۳ تا ۲۰ کاراکتر)."
)
EXACT_MULTIPLE_PROMPT = (
    "🛠 ساخت کانفیگ شخصی\n\n"
    "لطفاً یکی از پلن‌های زیر را انتخاب کن:\n\n"
    "🛠 <b>Alpha</b>\n\n"
    "🛠 <b>Beta</b>"
)


@pytest.fixture
def catalog(tmp_path, monkeypatch):
    db_path = str(tmp_path / "custom_config.db")
    db = database.Database(db_path)
    db.init_db(9001)
    db.add_or_update_user(USER_ID, "testuser", "Test")

    s1 = db.add_panel_server(
        "Server Alpha", "3xui", "https://panel.example.invalid", "fake_user_1", "fake_pass_1"
    )
    s2 = db.add_panel_server(
        "Server Beta", "3xui", "https://panel.example.invalid", "fake_user_2", "fake_pass_2"
    )

    alpha_id = db.create_custom_config_product(
        "Alpha",
        s1,
        min_gb=5,
        max_gb=1000,
        duration_mode="fixed",
        duration_days=30,
        pricing_mode="flat",
        flat_price_per_gb=100,
    )
    beta_id = db.create_custom_config_product(
        "Beta",
        s2,
        min_gb=5,
        max_gb=1000,
        duration_mode="fixed",
        duration_days=30,
        pricing_mode="flat",
        flat_price_per_gb=100,
    )

    router = handlers_user.create_user_router(db, is_main_bot=True)
    cb_start = find_handler(router, "callback_query", "cb_custom_config_start")
    cb_pick = find_handler(router, "callback_query", "cb_custom_config_pick_product")

    original_get_product = db.get_custom_config_product
    original_get_products = db.get_custom_config_products

    def configure(*, overrides: dict[int, str | None], representation: str):
        def wrapped_get_product(product_id: int):
            row = original_get_product(product_id)
            if row is None:
                return None
            data = dict(row)
            if product_id in overrides:
                kind = overrides[product_id]
                if kind is None:
                    data.pop("service_kind", None)
                else:
                    data["service_kind"] = kind
            else:
                data.pop("service_kind", None)
            return as_row(data, representation)

        def wrapped_get_products(active_only: bool = False):
            rows = original_get_products(active_only)
            result = []
            for row in rows:
                data = dict(row)
                pid = data["id"]
                if pid in overrides:
                    kind = overrides[pid]
                    if kind is None:
                        data.pop("service_kind", None)
                    else:
                        data["service_kind"] = kind
                else:
                    data.pop("service_kind", None)
                result.append(as_row(data, representation))
            return result

        monkeypatch.setattr(db, "get_custom_config_product", wrapped_get_product)
        monkeypatch.setattr(db, "get_custom_config_products", wrapped_get_products)

    try:
        yield SimpleNamespace(
            db=db,
            s1=s1,
            s2=s2,
            alpha_id=alpha_id,
            beta_id=beta_id,
            router=router,
            cb_start=cb_start,
            cb_pick=cb_pick,
            configure=configure,
        )
    finally:
        db.close()


async def assert_composite_refusal(log, state, before_db, after_db):
    refusal_events = [
        event for event in log.events
        if event.text and re.search(r"composite", event.text, re.IGNORECASE)
    ]
    assert refusal_events, (
        f"Expected nonempty customer-facing message/callback reason containing case-insensitive 'composite', "
        f"got events: {log.events}"
    )

    delete_events = log.select("message_delete")
    assert not delete_events, f"Refusal must precede deletion, but message_delete occurred: {delete_events}"

    for event in log.events:
        if event.kind == "callback_answer" and event.text:
            assert re.search(r"composite", event.text, re.IGNORECASE)
        if event.kind in ("message_answer", "edit_text", "edit_caption", "send_message"):
            assert re.search(r"composite", event.text or "", re.IGNORECASE), (
                f"Unexpected non-refusal message event: {event}"
            )

    for event in log.events:
        text = event.text or ""
        assert "نام کاربری" not in text, f"Legacy username prompt exposed: {text}"
        assert "یکی از پلن" not in text, f"Legacy product selection prompt exposed: {text}"

    current_state = await state.get_state()
    current_data = await state.get_data()
    assert current_state == CustomConfigFlow.waiting_product_select.state, (
        f"State must remain waiting_product_select, got {current_state}"
    )
    assert current_data == {"sentinel": "keep"}, (
        f"Data must remain original sentinel, got {current_data}"
    )
    assert after_db == before_db, "Database modified during composite refusal"


# 1. Composite discovery: dict/sqlite x singleton/multiple active catalog
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("catalog_mode", ["singleton", "multiple"])
def test_composite_custom_discovery_refused(catalog, representation, catalog_mode):
    async def _test():
        if catalog_mode == "singleton":
            catalog.db.update_custom_config_product(catalog.beta_id, is_active=0)
            catalog.configure(
                overrides={catalog.alpha_id: "composite", catalog.beta_id: None},
                representation=representation,
            )
        else:
            catalog.configure(
                overrides={catalog.alpha_id: "legacy", catalog.beta_id: "composite"},
                representation=representation,
            )

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, "custom_config_start", msg)

        before_db = dump(catalog.db)
        await catalog.cb_start(call, state)
        after_db = dump(catalog.db)

        await assert_composite_refusal(log, state, before_db, after_db)

    asyncio.run(_test())


# 2. Composite pick: dict/sqlite x Alpha/Beta selected
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("selected", ["alpha", "beta"])
def test_composite_custom_pick_refused(catalog, representation, selected):
    async def _test():
        if selected == "alpha":
            selected_id = catalog.alpha_id
            catalog.configure(
                overrides={catalog.alpha_id: "composite", catalog.beta_id: "legacy"},
                representation=representation,
            )
        else:
            selected_id = catalog.beta_id
            catalog.configure(
                overrides={catalog.alpha_id: "legacy", catalog.beta_id: "composite"},
                representation=representation,
            )

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, f"ccf_pick_product:{selected_id}", msg)

        before_db = dump(catalog.db)
        await catalog.cb_pick(call, state)
        after_db = dump(catalog.db)

        await assert_composite_refusal(log, state, before_db, after_db)

    asyncio.run(_test())


# 3. Legacy discovery: dict/sqlite x missing/legacy x singleton/multiple
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("catalog_mode", ["singleton", "multiple"])
def test_legacy_custom_discovery_success(catalog, representation, discriminator, catalog_mode):
    async def _test():
        if catalog_mode == "singleton":
            catalog.db.update_custom_config_product(catalog.beta_id, is_active=0)
            catalog.configure(
                overrides={catalog.alpha_id: discriminator, catalog.beta_id: None},
                representation=representation,
            )
        else:
            catalog.configure(
                overrides={catalog.alpha_id: discriminator, catalog.beta_id: discriminator},
                representation=representation,
            )

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, "custom_config_start", msg)

        before_db = dump(catalog.db)
        await catalog.cb_start(call, state)
        after_db = dump(catalog.db)

        assert after_db == before_db

        if catalog_mode == "singleton":
            assert await state.get_state() == CustomConfigFlow.waiting_username.state
            assert await state.get_data() == {
                "sentinel": "keep",
                "product_id": catalog.alpha_id,
                "panel_server_id": catalog.s1,
            }
            assert len(log.events) == 3
            ack = log.events[0]
            assert ack.kind == "callback_answer"
            assert not ack.text
            assert not ack.show_alert

            delete_ev = log.events[1]
            assert delete_ev.kind == "message_delete"

            msg_ev = log.events[2]
            assert msg_ev.kind == "message_answer"
            assert msg_ev.text == EXACT_USERNAME_PROMPT
            assert callback_rows(msg_ev.reply_markup) == [
                ["custom_config_random_username"],
                ["cancel_flow"],
            ]
        else:
            assert await state.get_state() == CustomConfigFlow.waiting_product_select.state
            assert await state.get_data() == {"sentinel": "keep"}
            assert len(log.events) == 3
            ack = log.events[0]
            assert ack.kind == "callback_answer"
            assert not ack.text
            assert not ack.show_alert

            delete_ev = log.events[1]
            assert delete_ev.kind == "message_delete"

            msg_ev = log.events[2]
            assert msg_ev.kind == "message_answer"
            assert msg_ev.parse_mode == "HTML"
            assert msg_ev.text == EXACT_MULTIPLE_PROMPT
            assert callback_rows(msg_ev.reply_markup) == [
                [f"ccf_pick_product:{catalog.alpha_id}"],
                [f"ccf_pick_product:{catalog.beta_id}"],
                ["cancel_flow"],
            ]

    asyncio.run(_test())


# 4. Legacy pick: dict/sqlite x missing/legacy x Alpha/Beta
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("selected", ["alpha", "beta"])
def test_legacy_custom_pick_success(catalog, representation, discriminator, selected):
    async def _test():
        catalog.configure(
            overrides={catalog.alpha_id: discriminator, catalog.beta_id: discriminator},
            representation=representation,
        )
        selected_id = catalog.alpha_id if selected == "alpha" else catalog.beta_id
        selected_server_id = catalog.s1 if selected == "alpha" else catalog.s2

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, f"ccf_pick_product:{selected_id}", msg)

        before_db = dump(catalog.db)
        await catalog.cb_pick(call, state)
        after_db = dump(catalog.db)

        assert after_db == before_db
        assert await state.get_state() == CustomConfigFlow.waiting_username.state
        assert await state.get_data() == {
            "sentinel": "keep",
            "product_id": selected_id,
            "panel_server_id": selected_server_id,
        }
        assert len(log.events) == 3
        ack = log.events[0]
        assert ack.kind == "callback_answer"
        assert not ack.text
        assert not ack.show_alert

        delete_ev = log.events[1]
        assert delete_ev.kind == "message_delete"

        msg_ev = log.events[2]
        assert msg_ev.kind == "message_answer"
        assert msg_ev.text == EXACT_USERNAME_PROMPT
        assert callback_rows(msg_ev.reply_markup) == [
            ["custom_config_random_username"],
            ["cancel_flow"],
        ]

    asyncio.run(_test())


# 5. Isolation controls: inactive composite does not affect singleton discovery;
# unselected composite does not affect direct legacy pick
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_isolation_inactive_composite_does_not_affect_discovery(catalog, representation):
    async def _test():
        catalog.db.update_custom_config_product(catalog.beta_id, is_active=0)
        catalog.configure(
            overrides={catalog.alpha_id: "legacy", catalog.beta_id: "composite"},
            representation=representation,
        )

        # Inactive composite does not enter active SQL results
        active_products = catalog.db.get_custom_config_products(active_only=True)
        assert len(active_products) == 1
        assert active_products[0]["id"] == catalog.alpha_id

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, "custom_config_start", msg)

        before_db = dump(catalog.db)
        await catalog.cb_start(call, state)
        after_db = dump(catalog.db)

        assert after_db == before_db
        assert await state.get_state() == CustomConfigFlow.waiting_username.state
        assert await state.get_data() == {
            "sentinel": "keep",
            "product_id": catalog.alpha_id,
            "panel_server_id": catalog.s1,
        }
        assert len(log.events) == 3
        assert log.events[0].kind == "callback_answer"
        assert log.events[1].kind == "message_delete"
        assert log.events[2].kind == "message_answer"
        assert log.events[2].text == EXACT_USERNAME_PROMPT
        assert callback_rows(log.events[2].reply_markup) == [
            ["custom_config_random_username"],
            ["cancel_flow"],
        ]

    asyncio.run(_test())


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_isolation_unselected_composite_does_not_affect_pick(catalog, representation):
    async def _test():
        catalog.configure(
            overrides={catalog.alpha_id: "legacy", catalog.beta_id: "composite"},
            representation=representation,
        )

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, f"ccf_pick_product:{catalog.alpha_id}", msg)

        before_db = dump(catalog.db)
        await catalog.cb_pick(call, state)
        after_db = dump(catalog.db)

        assert after_db == before_db
        assert await state.get_state() == CustomConfigFlow.waiting_username.state
        assert await state.get_data() == {
            "sentinel": "keep",
            "product_id": catalog.alpha_id,
            "panel_server_id": catalog.s1,
        }
        assert len(log.events) == 3
        assert log.events[0].kind == "callback_answer"
        assert log.events[1].kind == "message_delete"
        assert log.events[2].kind == "message_answer"
        assert log.events[2].text == EXACT_USERNAME_PROMPT
        assert callback_rows(log.events[2].reply_markup) == [
            ["custom_config_random_username"],
            ["cancel_flow"],
        ]

    asyncio.run(_test())


# 6. Unavailable selected product controls: missing/inactive selected product
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("condition", ["missing", "inactive"])
def test_unavailable_selected_product_control(catalog, representation, condition):
    async def _test():
        catalog.configure(overrides={}, representation=representation)
        if condition == "missing":
            target_id = 99999
        else:
            catalog.db.update_custom_config_product(catalog.beta_id, is_active=0)
            target_id = catalog.beta_id

        log = TelegramLog()
        user = FakeUser(USER_ID, username="testuser", first_name="Test")
        state = make_state(USER_ID)
        await state.set_state(CustomConfigFlow.waiting_product_select)
        await state.set_data({"sentinel": "keep"})

        msg = FakeMessage(log, USER_ID, from_user=user)
        call = FakeCallbackQuery(log, user, f"ccf_pick_product:{target_id}", msg)

        before_db = dump(catalog.db)
        await catalog.cb_pick(call, state)
        after_db = dump(catalog.db)

        assert after_db == before_db
        assert await state.get_state() == CustomConfigFlow.waiting_product_select.state
        assert await state.get_data() == {"sentinel": "keep"}
        assert log.select("message_delete") == []
        assert log.select("message_answer") == []
        assert len(log.events) == 1
        alert_ev = log.events[0]
        assert alert_ev.kind == "callback_answer"
        assert alert_ev.text == EXACT_UNAVAILABLE_ALERT
        assert alert_ev.show_alert is True

    asyncio.run(_test())
