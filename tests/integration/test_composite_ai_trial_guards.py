"""T050o: unsupported AI trial eligibility must not advertise composite plans."""
import asyncio
from types import SimpleNamespace

import pytest
from tests._harness.legacy_bot import use_synthetic_bot_settings

use_synthetic_bot_settings()
import ai_support
import config
import database
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_ai_catalog_legacy import dump


@pytest.fixture
def trial(tmp_path, monkeypatch):
    db = database.Database(str(tmp_path / 'trial.db'))
    db.init_db(9001)
    db.add_or_update_user(5101, 'synthetic_user', 'Synthetic')
    sid = db.add_panel_server('Synthetic', '3xui', 'https://panel.example.invalid', 'fake-user', 'fake-password')
    assert db.get_test_config_plans(True) == []
    pid = db.create_test_config_plan('Safe trial', 'tst', sid, 512, 12)
    original = db.get_test_config_plans

    def inject(selected, kind, representation):
        def plans(active_only=False):
            out = []
            for row in original(active_only):
                data = dict(row)
                data.pop('service_kind', None)
                if row['id'] == selected and kind is not None:
                    data['service_kind'] = kind
                    if kind == 'composite':
                        data['name'] = 'SECRET-AI-TRIAL'
                out.append(as_row(data, representation))
            return out
        monkeypatch.setattr(db, 'get_test_config_plans', plans)

    yield SimpleNamespace(db=db, pid=pid, sid=sid, inject=inject)
    db.close()


def call(db):
    return asyncio.run(ai_support._run_tool(db, 5101, 'request_test_config', {}))


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('mixed', [False, True])
def test_composite_ai_trial_refused(trial, caplog, representation, mixed):
    t = trial
    composite_id = t.db.create_test_config_plan('Composite alternative', 'cmp', t.sid, 1024, 24) if mixed else t.pid
    t.inject(composite_id, 'composite', representation)
    before = dump(t.db)
    result = call(t.db)
    assert result.get('eligible') is False
    assert 'composite' in str(result.get('reason', '')).lower()
    assert 'SECRET-AI-TRIAL' not in str(result) + caplog.text
    assert dump(t.db) == before
    assert t.db.get_user(5101)['test_used'] == 0


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
@pytest.mark.parametrize('kind', [None, 'legacy'])
@pytest.mark.parametrize('state', ['eligible', 'disabled', 'used', 'no_plan', 'no_user'])
def test_legacy_ai_trial_eligibility_preserved(trial, representation, kind, state):
    t = trial
    assert config.MAX_TEST_PER_USER == 1
    if state == 'disabled':
        t.db.set_setting('test_enabled', '0')
    elif state == 'used':
        assert t.db.try_reserve_test_slot(5101, 1)
    elif state == 'no_plan':
        t.db.update_test_config_plan(t.pid, is_active=0)
    elif state == 'no_user':
        with t.db._get_conn() as conn:
            conn.execute('DELETE FROM users WHERE telegram_id=?', (5101,))
    t.inject(t.pid, kind, representation)
    before = dump(t.db)
    expected = {'eligible': True} if state in ('eligible', 'no_user') else {
        'eligible': False, 'reason': {'disabled': 'test_disabled', 'used': 'already_used', 'no_plan': 'no_plan_defined'}[state],
    }
    assert call(t.db) == expected
    assert dump(t.db) == before


@pytest.mark.parametrize('representation', ['dict', 'sqlite'])
def test_inactive_composite_trial_does_not_block_legacy(trial, representation):
    t = trial
    other = t.db.create_test_config_plan('Inactive composite', 'inactive', t.sid, 1024, 24)
    t.db.update_test_config_plan(other, is_active=0)
    t.inject(other, 'composite', representation)
    before = dump(t.db)
    assert call(t.db) == {'eligible': True}
    assert dump(t.db) == before
