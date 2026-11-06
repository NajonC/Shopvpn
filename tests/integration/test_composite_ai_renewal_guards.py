"""T050q: custom-service AI renewal shortcuts reject composite metadata."""
import asyncio
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
from tests.characterization.test_legacy_renewal_reminders import BUYER, OTHER_USER, shop
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump

TOOLS = ['calculate_renewal_cost', 'renew_service_with_wallet']
SCENARIOS = [('full', 'custom'), ('volume', 'custom'), ('time', 'custom'), ('full', 'product')]
PRICES = {'full': 12000, 'volume': 5000, 'time': 3000}


@pytest.fixture
def renewal(shop, monkeypatch):
    db = shop.db
    cat = db.add_category('Renewal')
    pid = db.add_product(cat, 'Safe renewal', 12000, is_auto_provision=True, auto_provision_volume_gb=20)
    db.set_setting('renewal_price_per_gb', '1000')
    db.set_setting('renewal_price_per_day', '300')
    original_custom, original_product = db.get_custom_config_owned, db.get_product

    def inject(source, kind, representation):
        def convert(row, category):
            if row is None:
                return None
            data = dict(row)
            data.pop('service_kind', None)
            if source == category and kind is not None:
                data['service_kind'] = kind
                if kind == 'composite':
                    if category == 'product':
                        data['name'] = 'SECRET-AI-RENEWAL'
                    else:
                        data['subscription_url'] = 'https://sub.example.invalid/SECRET-AI-RENEWAL'
            return as_row(data, representation)
        monkeypatch.setattr(db, 'get_custom_config_owned', lambda *args: convert(original_custom(*args), 'custom'))
        monkeypatch.setattr(db, 'get_product', lambda *args: convert(original_product(*args), 'product'))
    yield SimpleNamespace(db=db, cc=shop.cc, pid=pid, inject=inject)


def arguments(t, mode):
    return {'service_id': f'x{t.cc}', 'mode': mode, **({'product_id': str(t.pid)} if mode == 'full' else {'amount': 5 if mode == 'volume' else 10})}


def call(t, tool, mode, user=BUYER):
    return asyncio.run(ai_support._run_tool(t.db, user, tool, arguments(t, mode)))


def expected(t, tool, mode, shortfall):
    price = PRICES[mode]
    balance = price - shortfall
    if tool == 'renew_service_with_wallet' and shortfall:
        return {'ok': False, 'reason': 'insufficient_wallet', 'wallet_balance_toman': balance, 'price_toman': price}
    return {
        'ok': True, 'service_id': f'x{t.cc}', 'mode': mode,
        'amount': None if mode == 'full' else 5 if mode == 'volume' else 10,
        'product_id': str(t.pid) if mode == 'full' else None, 'price_toman': price,
        'summary': {'full': 'Safe renewal', 'volume': '5 گیگابایت', 'time': '10 روز'}[mode],
        'wallet_balance_toman': balance, 'wallet_covers_full_amount': not shortfall,
    }


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('mode,source', SCENARIOS)
@pytest.mark.parametrize('tool', TOOLS)
def test_composite_ai_custom_renewal_refused(renewal, caplog, representation, mode, source, tool):
    t = renewal
    t.db.add_wallet_credit(BUYER, PRICES[mode])
    t.inject(source, 'composite', representation)
    before = dump(t.db)
    result = call(t, tool, mode)
    assert result.get('ok') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'SECRET-AI-RENEWAL' not in str(result) + caplog.text
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('mode', ['full', 'volume', 'time'])
@pytest.mark.parametrize('shortfall', [0, 1])
@pytest.mark.parametrize('tool', TOOLS)
def test_legacy_ai_custom_renewal_price_preserved(renewal, representation, kind, mode, shortfall, tool):
    t = renewal
    t.db.add_wallet_credit(BUYER, PRICES[mode] - shortfall)
    t.inject('custom', kind, representation)
    # Full renewal exercises the same representation and discriminator on product too.
    original = t.db.get_product
    if mode == 'full':
        def product(pid):
            data = dict(original(pid))
            if kind is not None:
                data['service_kind'] = kind
            return as_row(data, representation)
        t.db.get_product = product
    before = dump(t.db)
    result = call(t, tool, mode)
    assert result == expected(t, tool, mode, shortfall)
    assert type(result['price_toman']) is int
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('mode', ['volume', 'time'])
@pytest.mark.parametrize('tool', TOOLS)
def test_unselected_composite_product_does_not_block_ai_renewal(renewal, representation, mode, tool):
    t = renewal
    t.db.add_wallet_credit(BUYER, PRICES[mode])
    t.inject('product', 'composite', representation)
    before = dump(t.db)
    assert call(t, tool, mode) == expected(t, tool, mode, 0)
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('tool', TOOLS)
def test_foreign_custom_service_not_disclosed_by_ai_renewal(renewal, representation, tool):
    t = renewal
    t.db.add_wallet_credit(OTHER_USER, 12000)
    t.inject('custom', 'composite', representation)
    before = dump(t.db)
    assert call(t, tool, 'full', OTHER_USER) == {'ok': False, 'reason': 'service_not_found'}
    assert dump(t.db) == before
