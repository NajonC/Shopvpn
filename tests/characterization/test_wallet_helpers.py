"""Characterize the local finance helpers in ``database.py``: ``_get_conn``
(500–510), ``claim_order`` (3413–3422), ``approve_order`` (3433–3451),
``reject_order`` (3470–3486), wallet helpers (4356–4368), discount usage
(4566–4570), and top-up helpers (4624–4685), at commit 95c55af. Reproduce
with `.venv/bin/python -m pytest tests/characterization/test_wallet_helpers.py
--network=deny`. The database is real; children are real processes through the
T011 harness. Crash points and spies are wrappers on one instance's methods
(synthetic data; substitute, not evidence).

Known unsafe behaviour pinned here: ``reject_order`` commits rejection,
wallet refund, and coupon restore separately, so a crash after the first loses
both credits and a crash after the second loses the coupon; a retry returns
False and repays nothing (cases 13 and 14). ``approve_topup`` commits approval
before crediting, so a crash between them loses the credit for good (case 18).
``add_wallet_credit`` clamps at zero without an error and silently ignores an
unknown user (cases 19–21). ``_get_conn`` rolls back on an ``Exception`` but
leaves a write open on the shared connection after another ``BaseException``;
the next helper's commit publishes it (case 3). Claims and approvals are
single conditional updates, so concurrent duplicates have one winner (cases
5 and 17).
"""

import sqlite3
from types import SimpleNamespace

import pytest

import database
from tests._harness.crash import CRASH_EXIT_CODE, CrashPlan, SimulatedCrash
from tests._harness.multiprocess import run_processes


OWNER = 9001
BUYER = 1001


@pytest.fixture
def shop(tmp_path):
    db_path = str(tmp_path / "main.db")
    db = database.Database(db_path)
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    product_id = db.add_product(db.add_category("VPN"), "Stock 30d", 100_000)
    db.add_configs(product_id, ["vless://stock-1", "vless://stock-2", "vless://stock-3"])
    code_id = db.create_discount_code("SAVE10", fixed_amount=10_000, max_uses=5)
    return SimpleNamespace(
        db=db, db_path=db_path, lab=tmp_path, product_id=product_id, code_id=code_id
    )


def rows(shop, sql, params=()):
    conn = sqlite3.connect(shop.db_path)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def wallet(shop):
    return rows(shop, "SELECT referral_credit FROM users WHERE telegram_id=?", (BUYER,))[0][0]


def coupon_uses(shop):
    return rows(shop, "SELECT used_count FROM discount_codes WHERE id=1")[0][0]


def status(shop, table, row_id):
    return rows(shop, f"SELECT status FROM {table} WHERE id=?", (row_id,))[0][0]


def set_status(shop, table, row_id, value):
    conn = sqlite3.connect(shop.db_path)
    try:
        conn.execute(f"UPDATE {table} SET status=? WHERE id=?", (value, row_id))
        conn.commit()
    finally:
        conn.close()


def order(shop) -> int:
    return shop.db.create_order(BUYER, shop.product_id, 100_000)


def paid_order(shop) -> int:
    shop.db.increment_discount_usage(shop.code_id)
    return shop.db.create_order(
        BUYER,
        shop.product_id,
        100_000,
        wallet_used=30_000,
        discount_code_id=shop.code_id,
        discount_amount=10_000,
    )


def spy(monkeypatch, shop, name, calls, snapshot):
    real_method = getattr(shop.db, name)

    def wrapped(*args):
        calls.append((name, args, snapshot()))
        return real_method(*args)

    monkeypatch.setattr(shop.db, name, wrapped)


def _claim(context, order_id):
    db = database.Database(str(context.lab_root / "main.db"))
    return db.claim_order(order_id)


def _reject(context, order_id):
    db = database.Database(str(context.lab_root / "main.db"))
    real_credit = db.add_wallet_credit
    real_decrement = db.decrement_discount_usage

    def add_wallet_credit(*args):
        context.crash("before wallet refund")
        return real_credit(*args)

    def decrement_discount_usage(*args):
        context.crash("before coupon restore")
        return real_decrement(*args)

    db.add_wallet_credit = add_wallet_credit
    db.decrement_discount_usage = decrement_discount_usage
    return db.reject_order(order_id)


def _approve_topup(context, topup_id):
    db = database.Database(str(context.lab_root / "main.db"))
    real_credit = db.add_wallet_credit

    def add_wallet_credit(*args):
        context.crash("before wallet credit")
        return real_credit(*args)

    db.add_wallet_credit = add_wallet_credit
    return db.approve_topup(topup_id)


def test_helper_commits_when_it_returns(shop):
    shop.db.add_wallet_credit(BUYER, 5_000)
    assert wallet(shop) == 5_000
    assert shop.db._conn.in_transaction is False


def test_exception_in_helper_rolls_back_its_block(shop):
    with pytest.raises(RuntimeError, match="synthetic failure"):
        with shop.db._get_conn() as conn:
            conn.execute(
                "UPDATE users SET referral_credit=7000 WHERE telegram_id=?", (BUYER,)
            )
            raise RuntimeError("synthetic failure")
    assert wallet(shop) == 0
    assert shop.db._conn.in_transaction is False
    assert shop.db.get_wallet_credit(BUYER) == 0


def test_base_exception_leaves_the_write_for_the_next_commit(shop):
    with pytest.raises(SimulatedCrash, match="inside helper"):
        with shop.db._get_conn() as conn:
            conn.execute(
                "UPDATE users SET referral_credit=7000 WHERE telegram_id=?", (BUYER,)
            )
            raise SimulatedCrash("inside helper")
    assert shop.db._conn.in_transaction is True
    assert wallet(shop) == 0
    assert shop.db.get_wallet_credit(BUYER) == 7_000
    assert shop.db._conn.in_transaction is False
    assert wallet(shop) == 7_000


def test_claim_order_moves_only_pending_to_processing(shop):
    ids = [order(shop) for _ in range(4)]
    set_status(shop, "orders", ids[1], "processing")
    set_status(shop, "orders", ids[2], "approved")
    set_status(shop, "orders", ids[3], "rejected")
    assert [shop.db.claim_order(i) for i in (1, 2, 3, 4, 99)] == [True, False, False, False, False]
    assert [status(shop, "orders", i) for i in range(1, 5)] == [
        "processing", "processing", "approved", "rejected"
    ]
    updated = rows(shop, "SELECT id, updated_at FROM orders ORDER BY id")
    assert isinstance(updated[0][1], str)
    assert [row[1] for row in updated[1:]] == [None, None, None]
    assert shop.db.claim_order(1) is False


def test_concurrent_claims_have_one_winner(shop):
    order(shop)
    results = run_processes(_claim, count=2, lab_root=shop.lab, args=(1,))
    assert all(result.exit_code == 0 for result in results)
    assert sorted(result.value for result in results) == [False, True]
    assert status(shop, "orders", 1) == "processing"


def test_approve_order_links_every_config_and_keeps_the_first(shop):
    order(shop)
    assert shop.db.approve_order(1, [2, 3]) is True
    row = rows(shop, "SELECT status, config_id, updated_at FROM orders WHERE id=1")[0]
    assert row[0:2] == ("approved", 2)
    assert isinstance(row[2], str)
    assert rows(shop, "SELECT id, order_id, is_used FROM configs ORDER BY id") == [
        (1, None, 0), (2, 1, 0), (3, 1, 0)
    ]


def test_approve_order_takes_a_claimed_order_and_a_single_id(shop):
    order(shop)
    assert shop.db.claim_order(1) is True
    assert shop.db.approve_order(1, 1) is True
    assert rows(shop, "SELECT config_id FROM orders WHERE id=1")[0] == (1,)
    assert rows(shop, "SELECT id, order_id, is_used FROM configs ORDER BY id") == [
        (1, 1, 0), (2, None, 0), (3, None, 0)
    ]


def test_approve_order_refuses_settled_orders_and_links_nothing(shop):
    order(shop)
    order(shop)
    assert shop.db.approve_order(1, [1]) is True
    assert shop.db.reject_order(2) is True
    assert shop.db.approve_order(1, [2]) is False
    assert shop.db.approve_order(2, [3]) is False
    assert rows(shop, "SELECT status, config_id FROM orders ORDER BY id") == [
        ("approved", 1), ("rejected", None)
    ]
    assert rows(shop, "SELECT id, order_id, is_used FROM configs ORDER BY id") == [
        (1, 1, 0), (2, None, 0), (3, None, 0)
    ]


def test_approve_order_is_one_commit(shop):
    order(shop)
    conn = sqlite3.connect(shop.db_path)
    try:
        conn.execute(
            "CREATE TRIGGER fail_link BEFORE UPDATE OF order_id ON configs "
            "BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END"
        )
        conn.commit()
    finally:
        conn.close()
    with pytest.raises(sqlite3.IntegrityError, match="synthetic failure"):
        shop.db.approve_order(1, [2, 3])
    assert rows(shop, "SELECT status, config_id, updated_at FROM orders WHERE id=1") == [
        ("pending", None, None)
    ]
    assert rows(shop, "SELECT order_id FROM configs ORDER BY id") == [(None,), (None,), (None,)]
    assert shop.db._conn.in_transaction is False


def test_reject_order_commits_rejection_then_refund_then_coupon(shop, monkeypatch):
    paid_order(shop)
    calls = []
    snapshot = lambda: (status(shop, "orders", 1), wallet(shop), coupon_uses(shop))
    spy(monkeypatch, shop, "add_wallet_credit", calls, snapshot)
    spy(monkeypatch, shop, "decrement_discount_usage", calls, snapshot)
    assert shop.db.reject_order(1) is True
    assert calls == [
        ("add_wallet_credit", (1001, 30000), ("rejected", 0, 1)),
        ("decrement_discount_usage", (1,), ("rejected", 30000, 1)),
    ]
    row = rows(shop, "SELECT status, updated_at FROM orders WHERE id=1")[0]
    assert row[0] == "rejected" and isinstance(row[1], str)
    assert wallet(shop) == 30_000
    assert coupon_uses(shop) == 0


def test_reject_order_without_wallet_or_coupon_touches_neither(shop, monkeypatch):
    shop.db.add_wallet_credit(BUYER, 5_000)
    order(shop)
    calls = []
    snapshot = lambda: (status(shop, "orders", 1), wallet(shop), coupon_uses(shop))
    spy(monkeypatch, shop, "add_wallet_credit", calls, snapshot)
    spy(monkeypatch, shop, "decrement_discount_usage", calls, snapshot)
    assert shop.db.reject_order(1) is True
    assert calls == []
    assert wallet(shop) == 5_000
    assert coupon_uses(shop) == 0


def test_reject_order_refunds_only_a_pending_order_and_only_once(shop, monkeypatch):
    paid_order(shop)
    paid_order(shop)
    paid_order(shop)
    assert shop.db.claim_order(1) is True
    assert shop.db.approve_order(2, [1]) is True
    calls = []
    snapshot = lambda: (status(shop, "orders", 3), wallet(shop), coupon_uses(shop))
    spy(monkeypatch, shop, "add_wallet_credit", calls, snapshot)
    spy(monkeypatch, shop, "decrement_discount_usage", calls, snapshot)
    assert shop.db.reject_order(3) is True
    assert len(calls) == 2
    assert [shop.db.reject_order(i) for i in (1, 2, 3, 99)] == [False, False, False, False]
    assert len(calls) == 2
    assert wallet(shop) == 30_000
    assert coupon_uses(shop) == 2
    assert [status(shop, "orders", i) for i in (1, 2, 3)] == [
        "processing", "approved", "rejected"
    ]


def test_crash_after_rejection_commit_loses_refund_and_coupon(shop):
    paid_order(shop)
    (crashed,) = run_processes(
        _reject,
        count=1,
        lab_root=shop.lab,
        args=(1,),
        plans=[CrashPlan().arm("before wallet refund")],
    )
    assert (crashed.exit_code, crashed.crashed_at, crashed.reached) == (
        CRASH_EXIT_CODE, "before wallet refund", ("before wallet refund",)
    )
    assert status(shop, "orders", 1) == "rejected"
    assert wallet(shop) == 0
    assert coupon_uses(shop) == 1
    (restarted,) = run_processes(_reject, count=1, lab_root=shop.lab, args=(1,))
    assert (restarted.exit_code, restarted.value, restarted.reached) == (0, False, ())
    assert wallet(shop) == 0
    assert coupon_uses(shop) == 1
    paid_order(shop)
    (control,) = run_processes(_reject, count=1, lab_root=shop.lab, args=(2,))
    assert (control.exit_code, control.value, control.reached) == (
        0, True, ("before wallet refund", "before coupon restore")
    )
    assert status(shop, "orders", 2) == "rejected"
    assert wallet(shop) == 30_000
    assert coupon_uses(shop) == 1


def test_crash_between_refund_and_coupon_restore_keeps_the_coupon_used(shop):
    paid_order(shop)
    (crashed,) = run_processes(
        _reject,
        count=1,
        lab_root=shop.lab,
        args=(1,),
        plans=[CrashPlan().arm("before coupon restore")],
    )
    assert (crashed.exit_code, crashed.crashed_at, crashed.reached) == (
        CRASH_EXIT_CODE,
        "before coupon restore",
        ("before wallet refund", "before coupon restore"),
    )
    assert status(shop, "orders", 1) == "rejected"
    assert wallet(shop) == 30_000
    assert coupon_uses(shop) == 1
    (restarted,) = run_processes(_reject, count=1, lab_root=shop.lab, args=(1,))
    assert (restarted.exit_code, restarted.value, restarted.reached) == (0, False, ())
    assert wallet(shop) == 30_000
    assert coupon_uses(shop) == 1


def test_approve_topup_commits_approval_before_crediting(shop, monkeypatch):
    shop.db.add_wallet_credit(BUYER, 5_000)
    shop.db.create_topup(BUYER, 50_000)
    calls = []
    snapshot = lambda: (status(shop, "wallet_topups", 1), wallet(shop))
    spy(monkeypatch, shop, "add_wallet_credit", calls, snapshot)
    assert shop.db.approve_topup(1) is True
    assert calls == [("add_wallet_credit", (1001, 50000), ("approved", 5000))]
    assert wallet(shop) == 55_000
    row = rows(shop, "SELECT status, updated_at FROM wallet_topups WHERE id=1")[0]
    assert row[0] == "approved" and isinstance(row[1], str)


def test_approve_topup_credits_only_a_pending_topup_and_only_once(shop, monkeypatch):
    shop.db.add_wallet_credit(BUYER, 5_000)
    shop.db.create_topup(BUYER, 50_000)
    shop.db.create_topup(BUYER, 20_000)
    assert shop.db.reject_topup(2) is True
    calls = []
    snapshot = lambda: (status(shop, "wallet_topups", 1), wallet(shop))
    spy(monkeypatch, shop, "add_wallet_credit", calls, snapshot)
    assert shop.db.approve_topup(1) is True
    assert [shop.db.approve_topup(i) for i in (1, 2, 99)] == [False, False, False]
    assert len(calls) == 1
    assert wallet(shop) == 55_000
    assert [status(shop, "wallet_topups", i) for i in (1, 2)] == ["approved", "rejected"]


def test_concurrent_topup_approvals_credit_once(shop):
    shop.db.add_wallet_credit(BUYER, 5_000)
    shop.db.create_topup(BUYER, 50_000)
    results = run_processes(_approve_topup, count=2, lab_root=shop.lab, args=(1,))
    assert all(result.exit_code == 0 for result in results)
    assert sorted((result.value, result.reached) for result in results) == [
        (False, ()), (True, ("before wallet credit",))
    ]
    assert wallet(shop) == 55_000
    assert status(shop, "wallet_topups", 1) == "approved"


def test_crash_after_topup_approval_loses_the_credit(shop):
    shop.db.add_wallet_credit(BUYER, 5_000)
    shop.db.create_topup(BUYER, 50_000)
    (crashed,) = run_processes(
        _approve_topup,
        count=1,
        lab_root=shop.lab,
        args=(1,),
        plans=[CrashPlan().arm("before wallet credit")],
    )
    assert (crashed.exit_code, crashed.crashed_at, crashed.reached) == (
        CRASH_EXIT_CODE, "before wallet credit", ("before wallet credit",)
    )
    assert status(shop, "wallet_topups", 1) == "approved"
    assert wallet(shop) == 5_000
    (restarted,) = run_processes(_approve_topup, count=1, lab_root=shop.lab, args=(1,))
    assert (restarted.exit_code, restarted.value, restarted.reached) == (0, False, ())
    assert wallet(shop) == 5_000


def test_add_wallet_credit_clamps_the_balance_at_zero(shop):
    assert shop.db.add_wallet_credit(BUYER, 5_000) is None
    assert wallet(shop) == 5_000
    assert shop.db.add_wallet_credit(BUYER, -8_000) is None
    assert wallet(shop) == 0
    assert shop.db.add_wallet_credit(BUYER, 2_500) is None
    assert wallet(shop) == 2_500
    assert shop.db.add_wallet_credit(BUYER, -2_500) is None
    assert wallet(shop) == 0


def test_add_wallet_credit_ignores_an_unknown_user(shop):
    assert shop.db.add_wallet_credit(4242, 10_000) is None
    assert rows(shop, "SELECT COUNT(*) FROM users WHERE telegram_id=4242") == [(0,)]
    assert shop.db.get_wallet_credit(4242) == 0


def test_two_debits_beyond_the_balance_both_pass(shop):
    shop.db.add_wallet_credit(BUYER, 10_000)
    shop.db.add_wallet_credit(BUYER, -8_000)
    assert wallet(shop) == 2_000
    shop.db.add_wallet_credit(BUYER, -8_000)
    assert wallet(shop) == 0
