"""T050p: composite refusal before AI wallet-purchase shortcut processing."""
import asyncio

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
from tests.integration.test_composite_ai_catalog_legacy import catalog, dump


def seed(c, balance):
    c.db.add_or_update_user(5101, 'synthetic_user', 'Synthetic')
    c.db.add_wallet_credit(5101, balance)


def call(c, pid, quantity=2):
    return asyncio.run(ai_support._run_tool(c.db, 5101, 'request_purchase_with_wallet', {'product_id': str(pid), 'quantity': quantity}))


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('selected', ['stock', 'auto'])
def test_composite_ai_wallet_shortcut_refused(catalog, caplog, representation, selected):
    c = catalog
    pid = getattr(c, selected)
    seed(c, 200000 if selected == 'stock' else 400000)
    c.inject(pid, 'composite', representation)
    before = dump(c.db)
    result = call(c, pid)
    assert result.get('ok') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'SECRET-AI-PRODUCT' not in str(result) + caplog.text
    assert dump(c.db) == before
    assert c.counts == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('selected', ['stock', 'auto'])
@pytest.mark.parametrize('shortfall', [0, 1])
def test_legacy_ai_wallet_price_boundary_preserved(catalog, representation, kind, selected, shortfall):
    c = catalog
    pid = getattr(c, selected)
    total = 200000 if selected == 'stock' else 400000
    seed(c, total - shortfall)
    c.inject(pid, kind, representation)
    before = dump(c.db)
    expected = {'ok': True, 'product_id': pid, 'quantity': 2, 'price_toman': total} if not shortfall else {
        'ok': False, 'reason': 'insufficient_wallet', 'wallet_balance_toman': total - 1, 'price_toman': total,
    }
    result = call(c, pid)
    assert result == expected
    assert type(result['price_toman']) is int
    assert dump(c.db) == before
    assert c.db.get_wallet_credit(5101) == total - shortfall
    assert c.counts == ([pid] if selected == 'stock' else [])


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('unrelated', ['auto', 'empty'])
def test_unrelated_composite_does_not_block_ai_wallet_legacy(catalog, representation, unrelated):
    c = catalog
    seed(c, 200000)
    c.inject(getattr(c, unrelated), 'composite', representation)
    before = dump(c.db)
    assert call(c, c.stock) == {'ok': True, 'product_id': c.stock, 'quantity': 2, 'price_toman': 200000}
    assert dump(c.db) == before
    assert c.counts == [c.stock]


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('restriction', ['stock', 'wallet'])
def test_legacy_ai_wallet_existing_refusals_preserved(catalog, representation, restriction):
    c = catalog
    seed(c, 1000000)
    c.inject(c.stock, None, representation)
    if restriction == 'wallet':
        c.db.set_product_payment_methods(c.stock, ['card_to_card'])
    before = dump(c.db)
    assert call(c, c.stock, 3 if restriction == 'stock' else 2) == {
        'ok': False, 'reason': 'out_of_stock' if restriction == 'stock' else 'wallet_not_allowed',
    }
    assert dump(c.db) == before
    assert c.counts == [c.stock]
