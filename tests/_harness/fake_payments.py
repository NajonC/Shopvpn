"""A controlled payment method adapter and in-memory provider: substitute, not evidence.

Basis for its behavior:

* Contract (contracts/application.md): result fields and outcomes for
  AttemptQuote, AttemptRef, CheckoutRef, InvoiceObservation, VerifiedReceipt,
  and EvidenceFailure. The owner decided (2026-10-26) that until T075 builds
  the real types in composite/finance.py, this module defines them.
* Fake choice: sequential invoice and transaction numbering (inv-1, txn-1),
  the integer ceiling quote rounding formula, ASCII-digit validation for amounts,
  and in-memory provider controls (availability, rejection, lost responses).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests._harness.clock import FakeClock

EVIDENCE_LABEL = "substitute, not evidence"


@dataclass(frozen=True)
class CheckoutRef:
    checkout_id: str
    tenant_id: str
    customer_id: int


@dataclass(frozen=True)
class AttemptQuote:
    method: str
    merchant: str
    checkout_id: str
    remainder_units: int
    charge_units: int
    invoice_value_units: int
    rate_minor_per_unit: int
    rounding_increment: int
    rounding_mode: str
    native_amount: int
    currency: str
    scale: int
    valid_until_ms: int
    evidence_version: str


@dataclass(frozen=True)
class AttemptRef:
    attempt_id: str
    intent_key: str
    checkout: CheckoutRef
    quote: AttemptQuote


@dataclass(frozen=True)
class InvoiceObservation:
    intent_key: str
    state: str  # "created" | "uncertain" | "rejected"
    invoice_id: str | None
    reason: str


@dataclass(frozen=True)
class VerifiedReceipt:
    method: str
    merchant: str
    transaction_reference: str
    invoice_id: str
    tenant_id: str
    customer_id: int
    checkout_id: str
    attempt_id: str
    native_amount: int
    currency: str
    quote: AttemptQuote
    verification_source: str
    verified_at_ms: int


@dataclass(frozen=True)
class EvidenceFailure:
    definite: bool
    reason: str
    missing_field: str | None = None
    reference: str | None = None


@dataclass
class _TransactionRecord:
    id: str
    invoice_id: str
    amount: object
    currency: object


@dataclass
class _InvoiceRecord:
    id: str
    attempt: AttemptRef
    refused: bool = False
    transactions: list[_TransactionRecord] = field(default_factory=list)


_DEFAULT = object()


class FakePaymentMethod:
    """Fake payment method adapter and in-memory provider."""

    def __init__(
        self,
        clock: FakeClock,
        *,
        method: str = "fake-gateway",
        merchant: str = "fake-merchant",
        currency: str = "IRR",
        scale: int = 0,
        rate_minor_per_unit: int = 10,
        rounding_increment: int = 1,
        charge_units: int = 0,
        validity_ms: int = 900_000,
    ) -> None:
        self.api_key: str = secrets.token_urlsafe(32)
        self._clock: FakeClock = clock
        self._method: str = method
        self._merchant: str = merchant
        self._currency: str = currency
        self._scale: int = scale
        self._rate_minor_per_unit: int = rate_minor_per_unit
        self._rounding_increment: int = rounding_increment
        self._charge_units: int = charge_units
        self._validity_ms: int = validity_ms

        self._calls: list[str] = []
        self._available: bool = True
        self._lose_next_create: bool = False
        self._reject_next_create: bool = False

        self._invoice_counter: int = 0
        self._transaction_counter: int = 0
        self._invoices_by_intent: dict[str, str] = {}
        self._invoices: dict[str, _InvoiceRecord] = {}
        self._transactions: dict[str, _TransactionRecord] = {}

    @property
    def calls(self) -> tuple[str, ...]:
        return tuple(self._calls)

    def __repr__(self) -> str:
        return f"FakePaymentMethod(method={self._method!r}, merchant={self._merchant!r})"

    def __str__(self) -> str:
        return self.__repr__()

    async def quote_attempt(
        self, checkout: CheckoutRef, method_config_version: str, requested_remainder: int
    ) -> AttemptQuote:
        self._calls.append("quote_attempt")
        if type(requested_remainder) is not int:
            raise TypeError(
                f"requested_remainder must be an int, got {type(requested_remainder).__name__}"
            )
        if requested_remainder <= 0:
            raise ValueError(f"requested_remainder must be > 0, got {requested_remainder}")

        invoice_value_units = requested_remainder + self._charge_units
        raw_amount = invoice_value_units * self._rate_minor_per_unit
        inc = self._rounding_increment
        native_amount = ((raw_amount + inc - 1) // inc) * inc

        return AttemptQuote(
            method=self._method,
            merchant=self._merchant,
            checkout_id=checkout.checkout_id,
            remainder_units=requested_remainder,
            charge_units=self._charge_units,
            invoice_value_units=invoice_value_units,
            rate_minor_per_unit=self._rate_minor_per_unit,
            rounding_increment=inc,
            rounding_mode="up",
            native_amount=native_amount,
            currency=self._currency,
            scale=self._scale,
            valid_until_ms=self._clock.now_ms() + self._validity_ms,
            evidence_version=method_config_version,
        )

    async def create_or_reconcile_invoice(self, attempt: AttemptRef) -> InvoiceObservation:
        self._calls.append("create_or_reconcile_invoice")
        if not self._available:
            return InvoiceObservation(
                intent_key=attempt.intent_key,
                state="uncertain",
                invoice_id=None,
                reason="provider unavailable",
            )
        if attempt.intent_key in self._invoices_by_intent:
            inv_id = self._invoices_by_intent[attempt.intent_key]
            return InvoiceObservation(
                intent_key=attempt.intent_key,
                state="created",
                invoice_id=inv_id,
                reason="",
            )
        if self._reject_next_create:
            self._reject_next_create = False
            return InvoiceObservation(
                intent_key=attempt.intent_key,
                state="rejected",
                invoice_id=None,
                reason="create rejected",
            )
        self._invoice_counter += 1
        inv_id = f"inv-{self._invoice_counter}"
        self._invoices[inv_id] = _InvoiceRecord(id=inv_id, attempt=attempt)
        self._invoices_by_intent[attempt.intent_key] = inv_id
        if self._lose_next_create:
            self._lose_next_create = False
            return InvoiceObservation(
                intent_key=attempt.intent_key,
                state="uncertain",
                invoice_id=None,
                reason="response lost",
            )
        return InvoiceObservation(
            intent_key=attempt.intent_key,
            state="created",
            invoice_id=inv_id,
            reason="",
        )

    async def verify_receipt(
        self, attempt: AttemptRef, notification_hint: object
    ) -> VerifiedReceipt | EvidenceFailure:
        self._calls.append("verify_receipt")
        if not self._available:
            return EvidenceFailure(False, "provider unavailable", None, None)

        if attempt.intent_key not in self._invoices_by_intent:
            return EvidenceFailure(True, "no invoice for this attempt", None, None)

        inv_id = self._invoices_by_intent[attempt.intent_key]
        invoice = self._invoices[inv_id]

        target_txn: _TransactionRecord | None = None
        if isinstance(notification_hint, dict) and isinstance(
            notification_hint.get("transaction"), str
        ):
            hint_txn_id = notification_hint["transaction"]
            if hint_txn_id not in self._transactions:
                return EvidenceFailure(True, "unknown transaction", None, None)
            txn = self._transactions[hint_txn_id]
            if txn.invoice_id != inv_id:
                return EvidenceFailure(
                    True, "transaction belongs to another attempt", None, None
                )
            target_txn = txn
        else:
            if invoice.refused:
                return EvidenceFailure(True, "payment refused", None, inv_id)
            if not invoice.transactions:
                return EvidenceFailure(False, "no payment found", None, inv_id)
            target_txn = invoice.transactions[0]

        raw_amount = target_txn.amount
        if raw_amount is None or raw_amount == "":
            return EvidenceFailure(False, "amount missing", "amount", target_txn.id)
        if not (isinstance(raw_amount, str) and re.fullmatch(r"[0-9]+", raw_amount)):
            return EvidenceFailure(False, "amount unparseable", "amount", target_txn.id)

        raw_currency = target_txn.currency
        if raw_currency is None or raw_currency == "":
            return EvidenceFailure(False, "currency missing", "currency", target_txn.id)

        return VerifiedReceipt(
            method=self._method,
            merchant=self._merchant,
            transaction_reference=target_txn.id,
            invoice_id=inv_id,
            tenant_id=invoice.attempt.checkout.tenant_id,
            customer_id=invoice.attempt.checkout.customer_id,
            checkout_id=invoice.attempt.checkout.checkout_id,
            attempt_id=invoice.attempt.attempt_id,
            native_amount=int(raw_amount),
            currency=raw_currency,
            quote=invoice.attempt.quote,
            verification_source="fake provider API",
            verified_at_ms=self._clock.now_ms(),
        )

    def pay(
        self, invoice_id: str, *, amount: object = _DEFAULT, currency: object = _DEFAULT
    ) -> str:
        if invoice_id not in self._invoices:
            raise KeyError(f"Unknown invoice: {invoice_id}")
        invoice = self._invoices[invoice_id]
        if invoice.refused:
            raise ValueError(f"Invoice {invoice_id} is refused")
        self._transaction_counter += 1
        txn_id = f"txn-{self._transaction_counter}"
        stored_amount = (
            str(invoice.attempt.quote.native_amount) if amount is _DEFAULT else amount
        )
        stored_currency = (
            invoice.attempt.quote.currency if currency is _DEFAULT else currency
        )
        txn = _TransactionRecord(
            id=txn_id, invoice_id=invoice_id, amount=stored_amount, currency=stored_currency
        )
        invoice.transactions.append(txn)
        self._transactions[txn_id] = txn
        return txn_id

    def refuse(self, invoice_id: str) -> None:
        if invoice_id not in self._invoices:
            raise KeyError(f"Unknown invoice: {invoice_id}")
        invoice = self._invoices[invoice_id]
        if invoice.transactions:
            raise ValueError(
                f"Cannot refuse invoice {invoice_id} with existing transactions"
            )
        invoice.refused = True

    def hint_for(self, transaction_id: str) -> dict:
        if transaction_id not in self._transactions:
            raise KeyError(f"Unknown transaction: {transaction_id}")
        txn = self._transactions[transaction_id]
        return {
            "invoice_id": txn.invoice_id,
            "transaction": txn.id,
            "status": "paid",
            "amount": txn.amount,
        }

    def set_available(self, available: bool) -> None:
        self._available = available

    def lose_next_create_response(self) -> None:
        self._lose_next_create = True

    def reject_next_create(self) -> None:
        self._reject_next_create = True
