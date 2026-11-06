"""T050n: exact legacy AI catalog contract and isolated discriminator fixture."""
import asyncio
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
import database
from tests.integration.test_composite_legacy_guards import as_row


@pytest.fixture
def catalog(tmp_path, monkeypatch):
    db = database.Database(str(tmp_path / 'catalog.db'))
    db.init_db(9001)
    cat = db.add_category('Catalog')
    stock = db.add_product(cat, 'Stock', 100000, 'Stock description', 30)
    auto = db.add_product(cat, 'Automatic', 200000, 'Auto description', 60, True, 20)
    empty = db.add_product(cat, 'Empty', 300000)
    db.add_configs(stock, ['vless://synthetic@stock.invalid:443#1', 'vless://synthetic@stock.invalid:443#2'])
    counts = []
    original_count = db.count_available_configs
    monkeypatch.setattr(db, 'count_available_configs', lambda pid: (counts.append(pid), original_count(pid))[1])
    original_get, original_list = db.get_product, db.get_products

    def inject(pid, kind, representation):
        def convert(row):
            value = dict(row)
            value.pop('service_kind', None)
            if kind is not None:
                value['service_kind'] = kind
            if value['id'] == pid and kind == 'composite':
                value['name'] = 'SECRET-AI-PRODUCT'
            return as_row(value, representation)
        def selected_only(row):
            if row['id'] == pid:
                return convert(row)
            data = dict(row)
            data.pop('service_kind', None)
            return as_row(data, representation)
        monkeypatch.setattr(db, 'get_product', lambda selected: selected_only(original_get(selected)))
        monkeypatch.setattr(db, 'get_products', lambda category_id, active_only=True: [selected_only(row) for row in original_list(category_id, active_only)])

    yield SimpleNamespace(db=db, cat=cat, stock=stock, auto=auto, empty=empty, counts=counts, inject=inject)
    db.close()


def dump(db):
    with db._get_conn() as conn:
        return list(conn.iterdump())


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
def test_legacy_ai_catalog_exact(catalog, representation, kind):
    c = catalog
    c.inject(c.stock, kind, representation)
    before = dump(c.db)
    result = asyncio.run(ai_support._run_tool(c.db, 5101, 'list_products', {}))
    assert result == {'categories': [{'category': 'Catalog', 'products': [
        {'product_id': c.stock, 'name': 'Stock', 'price_toman': 100000, 'duration_days': 30, 'description': 'Stock description', 'in_stock': True, 'stock_count': 2},
        {'product_id': c.auto, 'name': 'Automatic', 'price_toman': 200000, 'duration_days': 60, 'description': 'Auto description', 'in_stock': True, 'stock_count': 'نامحدود (آنی)'},
        {'product_id': c.empty, 'name': 'Empty', 'price_toman': 300000, 'duration_days': 30, 'description': '', 'in_stock': False, 'stock_count': 0},
    ]}]}
    assert c.counts == [c.stock, c.empty]
    for pid, name in [(c.stock, 'Stock'), (c.auto, 'Automatic'), (c.empty, 'Empty')]:
        assert asyncio.run(ai_support._run_tool(c.db, 5101, 'show_purchase_options', {'product_id': str(pid)})) == {'ok': True, 'product_id': pid, 'name': name}
    assert dump(c.db) == before
