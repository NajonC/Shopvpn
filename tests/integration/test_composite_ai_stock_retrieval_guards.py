"""T050s: owned stock-alias retrieval stays outside composite AI shortcuts."""
import asyncio
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
import database
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump

BUYER, FOREIGN = 5101, 5102
TOOLS = ['request_service_qr', 'request_individual_configs']


@pytest.fixture
def stock(tmp_path, monkeypatch):
    db = database.Database(str(tmp_path / 'stock.db'))
    db.init_db(9001)
    db.add_or_update_user(BUYER, 'buyer', 'Buyer')
    db.add_or_update_user(FOREIGN, 'foreign', 'Foreign')
    cat = db.add_category('Stock')
    pid = db.add_product(cat, 'Stock', 1000)
    db.add_configs(pid, ['https://sub.example.invalid/stock'])
    with db._get_conn() as conn:
        cid = conn.execute('SELECT id FROM configs WHERE product_id=?', (pid,)).fetchone()['id']
    oid = db.create_order(BUYER, pid, 1000)
    assert db.approve_order(oid, cid)
    unrelated = db.create_order(BUYER, pid, 1000)
    get_config, get_orders = db.get_config_by_id, db.get_user_orders
    calls = []

    async def fetch(*args, **kwargs):
        calls.append(('fetch', args))
        return {}

    def provider(*args, **kwargs):
        calls.append(('provider', args))
        return object()

    monkeypatch.setattr(ai_support, 'fetch_sub_info', fetch)
    monkeypatch.setattr(ai_support, 'get_provider', provider)

    def inject(source, kind, representation):
        def convert(row, category):
            if row is None:
                return None
            data = dict(row)
            data.pop('service_kind', None)
            selected = category == source or (source == 'unrelated' and category == 'order' and row['id'] == unrelated)
            if source == 'order' and category == 'order':
                selected = row['id'] == oid
            if selected and kind is not None:
                data['service_kind'] = kind
                if kind == 'composite' and category == 'config':
                    data['link'] = 'https://sub.example.invalid/SECRET-AI-STOCK'
            return as_row(data, representation)
        monkeypatch.setattr(db, 'get_config_by_id', lambda *args: convert(get_config(*args), 'config'))
        monkeypatch.setattr(db, 'get_user_orders', lambda *args: [convert(o, 'order') for o in get_orders(*args)])

    try:
        yield SimpleNamespace(db=db, cid=cid, oid=oid, inject=inject, calls=calls)
    finally:
        db.close()


def call(t, tool, user=BUYER):
    return asyncio.run(ai_support._run_tool(t.db, user, tool, {'service_id': f'c{t.cid}'}))


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('tool', TOOLS)
def test_composite_ai_stock_retrieval_refused(stock, caplog, representation, source, tool):
    t = stock
    t.inject(source, 'composite', representation)
    before = dump(t.db)
    result = call(t, tool)
    assert result.get('ok') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'SECRET-AI-STOCK' not in str(result) + caplog.text
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('tool', TOOLS)
def test_legacy_ai_stock_retrieval_preserved(stock, representation, kind, source, tool):
    t = stock
    t.inject(source, kind, representation)
    before = dump(t.db)
    assert call(t, tool) == {'ok': True, 'service_id': f'c{t.cid}'}
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', ['config', 'order'])
@pytest.mark.parametrize('tool', TOOLS)
def test_foreign_ai_stock_retrieval_opaque(stock, caplog, representation, source, tool):
    t = stock
    t.inject(source, 'composite', representation)
    before = dump(t.db)
    assert call(t, tool, FOREIGN) == {'ok': False, 'reason': 'service_not_found'}
    assert dump(t.db) == before
    assert t.calls == []
    assert 'SECRET-AI-STOCK' not in caplog.text


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('tool', TOOLS)
def test_unrelated_composite_order_allows_legacy_stock_retrieval(stock, representation, tool):
    t = stock
    t.inject('unrelated', 'composite', representation)
    before = dump(t.db)
    assert call(t, tool) == {'ok': True, 'service_id': f'c{t.cid}'}
    assert dump(t.db) == before
    assert t.calls == []


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('state', ['disabled', 'unapproved', 'empty_link', 'native_link'])
@pytest.mark.parametrize('tool', TOOLS)
def test_legacy_stock_retrieval_restrictions(stock, representation, state, tool):
    t = stock
    with t.db._get_conn() as conn:
        if state == 'disabled':
            conn.execute('UPDATE configs SET is_disabled=1 WHERE id=?', (t.cid,))
        elif state == 'unapproved':
            conn.execute("UPDATE orders SET status='pending' WHERE id=?", (t.oid,))
        else:
            conn.execute('UPDATE configs SET link=? WHERE id=?', ('' if state == 'empty_link' else 'vless://synthetic@node.invalid:443', t.cid))
    t.inject('config', None, representation)
    before = dump(t.db)
    if state in ('disabled', 'unapproved'):
        expected = {'ok': False, 'reason': 'service_not_found'}
    elif state == 'empty_link':
        expected = {'ok': False, 'reason': 'no_link_available' if tool == 'request_service_qr' else 'no_individual_configs_available'}
    elif tool == 'request_service_qr':
        expected = {'ok': True, 'service_id': f'c{t.cid}'}
    else:
        expected = {'ok': False, 'reason': 'no_individual_configs_available'}
    assert call(t, tool) == expected
    assert dump(t.db) == before
    assert t.calls == []
