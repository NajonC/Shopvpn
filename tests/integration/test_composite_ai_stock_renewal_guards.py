"""T050t: AI stock-alias time-renewal previews reject composite metadata."""
import asyncio

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
from tests.integration.test_composite_ai_stock_retrieval_guards import BUYER, FOREIGN, stock
from tests.integration.test_composite_ai_catalog_legacy import dump

TOOLS = ['calculate_renewal_cost', 'renew_service_with_wallet']


def call(t, tool, user=BUYER, **overrides):
    args = {'service_id': f'c{t.cid}', 'mode': 'time', 'amount': 10}
    args.update(overrides)
    return asyncio.run(ai_support._run_tool(t.db, user, tool, args))


def prepare(t, source, kind, representation, user=BUYER, shortfall=0):
    t.db.set_setting('renewal_price_per_day', '300')
    t.db.set_setting('renewal_price_per_gb', '1000')
    t.db.add_wallet_credit(user, 3000-shortfall)
    t.inject(source, kind, representation)
    return dump(t.db)


def expected(t, tool, shortfall):
    if tool == 'renew_service_with_wallet' and shortfall:
        return {'ok': False, 'reason': 'insufficient_wallet', 'wallet_balance_toman': 2999, 'price_toman': 3000}
    return {'ok': True, 'service_id': f'c{t.cid}', 'mode': 'time', 'amount': 10, 'product_id': None,
            'price_toman': 3000, 'summary': '10 روز', 'wallet_balance_toman': 3000-shortfall,
            'wallet_covers_full_amount': not shortfall}


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('tool', TOOLS)
def test_composite_ai_stock_renewal_refused(stock, caplog, representation, source, tool):
    t = stock
    before = prepare(t, source, 'composite', representation)
    result = call(t, tool)
    assert result.get('ok') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'SECRET-AI-STOCK' not in str(result) + caplog.text
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('shortfall', [0, 1])
@pytest.mark.parametrize('tool', TOOLS)
def test_legacy_ai_stock_renewal_exact(stock, representation, source, kind, shortfall, tool):
    t = stock
    before = prepare(t, source, kind, representation, shortfall=shortfall)
    result = call(t, tool)
    assert result == expected(t, tool, shortfall)
    assert type(result['price_toman']) is int
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('tool', TOOLS)
def test_foreign_ai_stock_renewal_opaque(stock, caplog, representation, source, tool):
    t = stock
    before = prepare(t, source, 'composite', representation, user=FOREIGN)
    assert call(t, tool, FOREIGN) == {'ok': False, 'reason': 'service_not_found'}
    assert dump(t.db) == before
    assert t.calls == []
    assert 'SECRET-AI-STOCK' not in caplog.text


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('tool', TOOLS)
def test_unrelated_composite_order_allows_stock_renewal(stock, representation, tool):
    t = stock
    before = prepare(t, 'unrelated', 'composite', representation)
    assert call(t, tool) == expected(t, tool, 0)
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('mode', ['full', 'volume'])
@pytest.mark.parametrize('tool', TOOLS)
def test_stock_renewal_still_time_only(stock, representation, mode, tool):
    t = stock
    before = prepare(t, 'config', None, representation)
    assert call(t, tool, mode=mode) == {'ok': False, 'reason': 'only_time_mode_for_plan_configs'}
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('amount', [0, -1, 'bad'])
@pytest.mark.parametrize('tool', TOOLS)
def test_stock_renewal_invalid_amount_refused(stock, representation, amount, tool):
    t = stock
    before = prepare(t, 'config', None, representation)
    assert call(t, tool, amount=amount) == {'ok': False, 'reason': 'rate_not_configured_or_invalid_amount'}
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('tool', TOOLS)
def test_stock_renewal_missing_rate_refused(stock, representation, tool):
    t = stock
    prepare(t, 'config', None, representation)
    t.db.set_setting('renewal_price_per_day', '0')
    before = dump(t.db)
    assert call(t, tool) == {'ok': False, 'reason': 'rate_not_configured_or_invalid_amount'}
    assert dump(t.db) == before
    assert t.calls == []
