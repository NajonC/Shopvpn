"""Fake payment method adapter (tasks.md T010; contracts/application.md).

The adapter quotes an exact native amount, creates invoices keyed by a durable
intent, and verifies receipts with the provider instead of trusting the
notification hint. Wrong amounts and currencies are reported as they were
paid, so the service can hold them; missing or unparseable amounts are
evidence failures, never zero or a guess.
"""

import asyncio
import dataclasses

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_payments import (
    EVIDENCE_LABEL,
    AttemptQuote,
    AttemptRef,
    CheckoutRef,
    EvidenceFailure,
    FakePaymentMethod,
    InvoiceObservation,
    VerifiedReceipt,
)
import tests._harness.fake_payments as fake_payments

CHECKOUT = CheckoutRef(checkout_id="chk-1", tenant_id="main", customer_id=1001)
OTHER_CHECKOUT = CheckoutRef(checkout_id="chk-2", tenant_id="main", customer_id=1002)


def _method(**kwargs):
    clock = FakeClock()
    return clock, FakePaymentMethod(clock, **kwargs)


async def _attempt(
    method, *, remainder=73_000, attempt_id="att-1", intent_key="intent-1", checkout=CHECKOUT
):
    quote = await method.quote_attempt(checkout, "cfg-1", remainder)
    return AttemptRef(
        attempt_id=attempt_id, intent_key=intent_key, checkout=checkout, quote=quote
    )


async def _paid_attempt(method, **pay_kwargs):
    attempt = await _attempt(method)
    created = await method.create_or_reconcile_invoice(attempt)
    transaction = method.pay(created.invoice_id, **pay_kwargs)
    return attempt, transaction


def test_label_and_docstring():
    assert EVIDENCE_LABEL == "substitute, not evidence"
    assert EVIDENCE_LABEL in fake_payments.__doc__


# Quotes


def test_quote_is_exact_full_value_and_frozen():
    async def scenario():
        clock, method = _method(
            rate_minor_per_unit=10, rounding_increment=1_000, charge_units=3_000
        )
        clock.step_wall(7_000)
        quote = await method.quote_attempt(CHECKOUT, "cfg-1", 70_000)
        assert quote == AttemptQuote(
            method="fake-gateway",
            merchant="fake-merchant",
            checkout_id="chk-1",
            remainder_units=70_000,
            charge_units=3_000,
            invoice_value_units=73_000,
            rate_minor_per_unit=10,
            rounding_increment=1_000,
            rounding_mode="up",
            native_amount=730_000,
            currency="IRR",
            scale=0,
            valid_until_ms=clock.now_ms() + 900_000,
            evidence_version="cfg-1",
        )
        rounded = await method.quote_attempt(CHECKOUT, "cfg-1", 70_001)
        assert rounded.invoice_value_units == 73_001
        assert rounded.native_amount == 731_000
        with pytest.raises(dataclasses.FrozenInstanceError):
            quote.native_amount = 1

    asyncio.run(scenario())


def test_default_quote_has_no_rounding_or_charges():
    async def scenario():
        _, method = _method()
        quote = await method.quote_attempt(CHECKOUT, "cfg-2", 73_000)
        assert (quote.charge_units, quote.invoice_value_units) == (0, 73_000)
        assert (quote.rate_minor_per_unit, quote.rounding_increment) == (10, 1)
        assert quote.native_amount == 730_000
        assert quote.evidence_version == "cfg-2"

    asyncio.run(scenario())


def test_quote_refuses_a_bad_remainder():
    async def scenario():
        _, method = _method()
        for bad in (True, 1.5, "73000", None):
            with pytest.raises(TypeError):
                await method.quote_attempt(CHECKOUT, "cfg-1", bad)
        for bad in (0, -1):
            with pytest.raises(ValueError):
                await method.quote_attempt(CHECKOUT, "cfg-1", bad)

    asyncio.run(scenario())


# Invoice creation


def test_invoice_creation_is_keyed_by_the_intent():
    async def scenario():
        _, method = _method()
        first = await _attempt(method)
        assert await method.create_or_reconcile_invoice(first) == InvoiceObservation(
            intent_key="intent-1", state="created", invoice_id="inv-1", reason=""
        )
        again = await method.create_or_reconcile_invoice(first)
        assert again.invoice_id == "inv-1"
        second = await _attempt(method, attempt_id="att-2", intent_key="intent-2")
        assert (await method.create_or_reconcile_invoice(second)).invoice_id == "inv-2"

    asyncio.run(scenario())


def test_lost_create_response_is_uncertain_and_reconciles_to_the_same_invoice():
    async def scenario():
        _, method = _method()
        attempt = await _attempt(method)
        method.lose_next_create_response()
        lost = await method.create_or_reconcile_invoice(attempt)
        assert (lost.state, lost.invoice_id) == ("uncertain", None)
        assert lost.reason == "response lost"
        reconciled = await method.create_or_reconcile_invoice(attempt)
        assert (reconciled.state, reconciled.invoice_id) == ("created", "inv-1")
        other = await _attempt(method, attempt_id="att-2", intent_key="intent-2")
        assert (await method.create_or_reconcile_invoice(other)).invoice_id == "inv-2"

    asyncio.run(scenario())


def test_rejected_create_creates_nothing():
    async def scenario():
        _, method = _method()
        attempt = await _attempt(method)
        method.reject_next_create()
        assert await method.create_or_reconcile_invoice(attempt) == InvoiceObservation(
            intent_key="intent-1", state="rejected", invoice_id=None, reason="create rejected"
        )
        assert (await method.create_or_reconcile_invoice(attempt)).invoice_id == "inv-1"

    asyncio.run(scenario())


def test_unavailable_provider_creates_nothing():
    async def scenario():
        _, method = _method()
        attempt = await _attempt(method)
        method.set_available(False)
        assert await method.create_or_reconcile_invoice(attempt) == InvoiceObservation(
            intent_key="intent-1",
            state="uncertain",
            invoice_id=None,
            reason="provider unavailable",
        )
        method.set_available(True)
        assert (await method.create_or_reconcile_invoice(attempt)).invoice_id == "inv-1"

    asyncio.run(scenario())


# Verification


def test_exact_payment_verifies_with_full_linkage():
    async def scenario():
        clock, method = _method()
        attempt, transaction = await _paid_attempt(method)
        assert transaction == "txn-1"
        clock.advance(4_000)
        clock.step_wall(-60_000)
        assert clock.now_ms() != clock.true_now_ms()
        receipt = await method.verify_receipt(attempt, method.hint_for(transaction))
        assert receipt == VerifiedReceipt(
            method="fake-gateway",
            merchant="fake-merchant",
            transaction_reference="txn-1",
            invoice_id="inv-1",
            tenant_id="main",
            customer_id=1001,
            checkout_id="chk-1",
            attempt_id="att-1",
            native_amount=730_000,
            currency="IRR",
            quote=attempt.quote,
            verification_source="fake provider API",
            verified_at_ms=clock.now_ms(),
        )
        requeried = await method.verify_receipt(attempt, None)
        assert requeried.transaction_reference == "txn-1"

    asyncio.run(scenario())


def test_repeated_hint_is_the_same_receipt():
    async def scenario():
        clock, method = _method()
        attempt, transaction = await _paid_attempt(method)
        hint = method.hint_for(transaction)
        first = await method.verify_receipt(attempt, hint)
        clock.advance(30_000)
        second = await method.verify_receipt(attempt, hint)
        assert second.transaction_reference == first.transaction_reference
        assert second.verified_at_ms == first.verified_at_ms + 30_000
        assert dataclasses.replace(second, verified_at_ms=first.verified_at_ms) == first

    asyncio.run(scenario())


def test_distinct_payments_on_one_invoice_have_distinct_references():
    async def scenario():
        _, method = _method()
        attempt, first = await _paid_attempt(method)
        second = method.pay("inv-1")
        assert (first, second) == ("txn-1", "txn-2")
        receipts = [
            await method.verify_receipt(attempt, method.hint_for(transaction))
            for transaction in (first, second)
        ]
        assert [r.transaction_reference for r in receipts] == ["txn-1", "txn-2"]
        assert {r.attempt_id for r in receipts} == {"att-1"}
        assert (await method.verify_receipt(attempt, None)).transaction_reference == "txn-1"

    asyncio.run(scenario())


def test_hint_claims_are_ignored():
    async def scenario():
        _, method = _method()
        attempt, transaction = await _paid_attempt(method)
        hint = method.hint_for(transaction)
        assert hint == {
            "invoice_id": "inv-1",
            "transaction": "txn-1",
            "status": "paid",
            "amount": "730000",
        }
        forged = {**hint, "amount": "1", "status": "paid"}
        receipt = await method.verify_receipt(attempt, forged)
        assert receipt.native_amount == 730_000

        _, unpaid = _method()
        unpaid_attempt = await _attempt(unpaid)
        await unpaid.create_or_reconcile_invoice(unpaid_attempt)
        assert await unpaid.verify_receipt(
            unpaid_attempt, {"status": "paid", "amount": "730000"}
        ) == EvidenceFailure(
            definite=False, reason="no payment found", missing_field=None, reference="inv-1"
        )

    asyncio.run(scenario())


def test_mismatched_amount_or_currency_is_reported_as_paid():
    async def scenario():
        _, method = _method()
        attempt, short = await _paid_attempt(method, amount="729000")
        receipt = await method.verify_receipt(attempt, method.hint_for(short))
        assert (receipt.native_amount, receipt.currency) == (729_000, "IRR")
        assert receipt.quote.native_amount == 730_000

        foreign = method.pay("inv-1", currency="USD")
        receipt = await method.verify_receipt(attempt, method.hint_for(foreign))
        assert (receipt.native_amount, receipt.currency) == (730_000, "USD")

    asyncio.run(scenario())


def test_missing_or_unparseable_amount_is_an_evidence_failure():
    async def scenario():
        cases = {
            None: "amount missing",
            "": "amount missing",
            "73x": "amount unparseable",
            "730000.0": "amount unparseable",
            "-730000": "amount unparseable",
            " 730000": "amount unparseable",
            "NaN": "amount unparseable",
            "Infinity": "amount unparseable",
            "1e6": "amount unparseable",
            "٧٣٠٠٠٠": "amount unparseable",
            730_000: "amount unparseable",
        }
        for raw, reason in cases.items():
            _, method = _method()
            attempt, transaction = await _paid_attempt(method, amount=raw)
            assert await method.verify_receipt(
                attempt, method.hint_for(transaction)
            ) == EvidenceFailure(
                definite=False, reason=reason, missing_field="amount", reference="txn-1"
            ), raw

    asyncio.run(scenario())


def test_missing_currency_is_an_evidence_failure():
    async def scenario():
        for raw in (None, ""):
            _, method = _method()
            attempt, transaction = await _paid_attempt(method, currency=raw)
            assert await method.verify_receipt(
                attempt, method.hint_for(transaction)
            ) == EvidenceFailure(
                definite=False,
                reason="currency missing",
                missing_field="currency",
                reference="txn-1",
            )

    asyncio.run(scenario())


def test_refused_payment_is_a_definite_rejection():
    async def scenario():
        _, method = _method()
        attempt = await _attempt(method)
        await method.create_or_reconcile_invoice(attempt)
        method.refuse("inv-1")
        assert await method.verify_receipt(attempt, None) == EvidenceFailure(
            definite=True, reason="payment refused", missing_field=None, reference="inv-1"
        )

    asyncio.run(scenario())


def test_unavailable_provider_makes_verification_uncertain():
    async def scenario():
        _, method = _method()
        attempt, transaction = await _paid_attempt(method)
        method.set_available(False)
        assert await method.verify_receipt(
            attempt, method.hint_for(transaction)
        ) == EvidenceFailure(
            definite=False, reason="provider unavailable", missing_field=None, reference=None
        )
        method.set_available(True)
        receipt = await method.verify_receipt(attempt, method.hint_for(transaction))
        assert receipt.transaction_reference == "txn-1"

    asyncio.run(scenario())


def test_unknown_or_foreign_transaction_is_rejected():
    async def scenario():
        _, method = _method()
        attempt, _ = await _paid_attempt(method)
        assert await method.verify_receipt(
            attempt, {"transaction": "txn-999", "status": "paid"}
        ) == EvidenceFailure(
            definite=True, reason="unknown transaction", missing_field=None, reference=None
        )

        other = await _attempt(
            method, attempt_id="att-2", intent_key="intent-2", checkout=OTHER_CHECKOUT
        )
        await method.create_or_reconcile_invoice(other)
        foreign = method.pay("inv-2")
        assert await method.verify_receipt(
            attempt, method.hint_for(foreign)
        ) == EvidenceFailure(
            definite=True,
            reason="transaction belongs to another attempt",
            missing_field=None,
            reference=None,
        )

    asyncio.run(scenario())


def test_verification_without_an_invoice_is_a_definite_failure():
    async def scenario():
        _, method = _method()
        attempt = await _attempt(method)
        assert await method.verify_receipt(attempt, None) == EvidenceFailure(
            definite=True,
            reason="no invoice for this attempt",
            missing_field=None,
            reference=None,
        )

    asyncio.run(scenario())


def test_provider_controls_refuse_misuse():
    async def scenario():
        _, method = _method()
        with pytest.raises(KeyError):
            method.pay("inv-1")
        with pytest.raises(KeyError):
            method.refuse("inv-1")
        with pytest.raises(KeyError):
            method.hint_for("txn-1")
        attempt, _ = await _paid_attempt(method)
        with pytest.raises(ValueError):
            method.refuse("inv-1")
        second = await _attempt(method, attempt_id="att-2", intent_key="intent-2")
        await method.create_or_reconcile_invoice(second)
        method.refuse("inv-2")
        with pytest.raises(ValueError):
            method.pay("inv-2")

    asyncio.run(scenario())


def test_calls_record_only_adapter_calls():
    async def scenario():
        _, method = _method()
        assert method.calls == ()
        attempt, transaction = await _paid_attempt(method)
        method.hint_for(transaction)
        await method.verify_receipt(attempt, None)
        assert method.calls == (
            "quote_attempt",
            "create_or_reconcile_invoice",
            "verify_receipt",
        )

    asyncio.run(scenario())


def test_api_key_never_appears():
    async def scenario():
        clock, method = _method()
        assert isinstance(method.api_key, str) and len(method.api_key) >= 32
        assert FakePaymentMethod(clock).api_key != method.api_key
        attempt, transaction = await _paid_attempt(method)
        results = [
            attempt,
            await method.create_or_reconcile_invoice(attempt),
            await method.verify_receipt(attempt, method.hint_for(transaction)),
            await method.verify_receipt(attempt, {"transaction": "txn-999"}),
            method.hint_for(transaction),
        ]
        method.set_available(False)
        results.append(await method.verify_receipt(attempt, None))
        shown = repr(method) + str(method) + "".join(repr(r) + str(r) for r in results)
        assert method.api_key not in shown

    asyncio.run(scenario())
