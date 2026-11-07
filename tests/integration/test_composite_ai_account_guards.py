"""T050u: AI account retrieval refuses composite rows before external reads."""
import asyncio
from collections import Counter
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
from tests.integration.test_composite_ai_stock_retrieval_guards import BUYER, FOREIGN, stock
from tests.integration.test_composite_ai_catalog_legacy import dump
from tests.integration.test_composite_legacy_guards import as_row

SOURCES = ['config', 'order', 'custom', 'pending']
SUMMARY = {'data_available': True, 'used_gb': 4.0, 'total_gb': 10.0, 'remaining_gb': 6.0, 'expires_at_jalali': 'نامحدود'}


@pytest.fixture
def account(stock, monkeypatch):
    t = stock
    sid = t.db.add_panel_server('Synthetic', '3xui', 'https://panel.example.invalid', 'fake-user', 'fake-password')
    cc = t.db.add_custom_config(BUYER, sid, 'custom_1', 10, 30, 'https://sub.example.invalid/custom', expires_at='2099-01-01T00:00:00')
    t.db.add_wallet_credit(BUYER, 1234)
    t.db.add_wallet_credit(FOREIGN, 73)
    pending = next(o['id'] for o in t.db.get_user_orders(BUYER) if o['status'] == 'pending')
    original_custom = t.db.get_custom_configs_for_user

    async def fetch(link):
        t.calls.append(('fetch', link))
        return {'ok': True, 'upload': 1024**3, 'download': 3*1024**3, 'total': 10*1024**3, 'expire': None}

    class Provider:
        async def get_user_usage(self, username):
            t.calls.append(('usage', username))
            return {'status': 'active'}

    def provider(server):
        t.calls.append(('provider', server['id']))
        return Provider()

    monkeypatch.setattr(ai_support, 'fetch_sub_info', fetch)
    monkeypatch.setattr(ai_support, 'get_provider', provider)

    def inject(source, kind, representation):
        t.inject('unrelated' if source == 'pending' else source, kind, representation)
        def custom(*args, **kwargs):
            out = []
            for row in original_custom(*args, **kwargs):
                data = dict(row)
                data.pop('service_kind', None)
                if source == 'custom' and kind is not None and row['id'] == cc:
                    data['service_kind'] = kind
                    if kind == 'composite':
                        data['subscription_url'] = 'https://sub.example.invalid/SECRET-AI-ACCOUNT'
                out.append(as_row(data, representation))
            return out
        monkeypatch.setattr(t.db, 'get_custom_configs_for_user', custom)
    return SimpleNamespace(db=t.db, cid=t.cid, oid=t.oid, pending=pending, sid=sid, cc=cc, inject=inject, calls=t.calls)


def call(t, user=BUYER):
    return asyncio.run(ai_support._run_tool(t.db, user, 'check_account_status', {}))


def legacy_expected(t, enabled=1, auto=0, pending=True):
    return {'wallet_balance_toman': 1234, 'active_services': [
        {'order_id': t.oid, 'service_id': f'c{t.cid}', **SUMMARY},
        {'service_id': f'x{t.cc}', 'name': 'custom_1', 'enabled': bool(enabled), 'auto_renew': bool(auto), **SUMMARY, 'panel_status': 'فعال'},
    ], 'pending_orders': [{'order_id': t.pending, 'status': 'pending'}] if pending else []}


def assert_legacy_calls(t):
    assert Counter(t.calls) == Counter([('fetch', 'https://sub.example.invalid/stock'), ('fetch', 'https://sub.example.invalid/custom'), ('provider', t.sid), ('usage', 'custom_1')])


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', SOURCES)
def test_composite_ai_account_refused_before_external_reads(account, caplog, representation, source):
    t = account
    t.inject(source, 'composite', representation)
    before = dump(t.db)
    result = call(t)
    assert result.get('ok') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'active_services' not in result
    assert 'pending_orders' not in result
    assert 'SECRET-AI-' not in str(result) + caplog.text
    assert t.calls == []
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', SOURCES)
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('enabled,auto', [(1, 0), (0, 1)])
def test_legacy_ai_account_exact(account, representation, source, kind, enabled, auto):
    t = account
    with t.db._get_conn() as conn:
        conn.execute('UPDATE custom_configs SET enabled=?,auto_renew=? WHERE id=?', (enabled, auto, t.cc))
    t.inject(source, kind, representation)
    before = dump(t.db)
    result = call(t)
    assert result == legacy_expected(t, enabled, auto)
    assert type(result['wallet_balance_toman']) is int
    assert_legacy_calls(t)
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('source', SOURCES)
def test_other_owner_composites_do_not_affect_ai_account(account, caplog, representation, source):
    t = account
    t.inject(source, 'composite', representation)
    before = dump(t.db)
    assert call(t, FOREIGN) == {'wallet_balance_toman': 73, 'active_services': [], 'pending_orders': []}
    assert t.calls == []
    assert 'SECRET-AI-' not in caplog.text
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('state', ['rejected', 'hidden'])
def test_unused_composite_order_does_not_block_ai_account(account, representation, state):
    t = account
    with t.db._get_conn() as conn:
        if state == 'rejected':
            conn.execute("UPDATE orders SET status='rejected' WHERE id=?", (t.pending,))
        else:
            conn.execute('UPDATE orders SET user_deleted=1 WHERE id=?', (t.pending,))
    t.inject('pending', 'composite', representation)
    before = dump(t.db)
    assert call(t) == legacy_expected(t, pending=False)
    assert_legacy_calls(t)
    assert dump(t.db) == before
