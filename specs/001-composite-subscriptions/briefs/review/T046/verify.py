"""T046 real-code mutation checks in a source-only offline scratch directory."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TESTS = ('tests/unit/test_audit_writer.py', 'tests/unit/test_secrets_and_audit.py')
AUDIT = 'composite/audit.py'
MIGRATIONS = 'composite/migrations.py'
MUTATIONS = []
for field in ('event_id', 'occurred_at', 'actor_domain', 'actor_id', 'action',
              'resource_kind', 'resource_id', 'reason', 'evidence_ref'):
    replacement = 'event.occurred_at + 1' if field == 'occurred_at' else "'system'" if field == 'actor_domain' else "'incorrect'"
    MUTATIONS.append((f'wrong_{field}', AUDIT, [(f'        event.{field},', f'        {replacement},')], 'test_write_retains_exact_metadata'))
MUTATIONS.extend([
    ('frozen_event', AUDIT, [('@dataclass(frozen=True)', '@dataclass(frozen=False)')], 'test_write_retains_exact_metadata'),
    ('refuse_system', AUDIT, [('    params = (', "    if event.actor_domain == 'system':\n        raise AuditWriteError()\n    params = (")], 'test_write_retains_exact_metadata'),
    ('refuse_null_reason', AUDIT, [('    params = (', '    if event.reason is None:\n        raise AuditWriteError()\n    params = (')], 'test_optional_metadata'),
    ('omit_insert', AUDIT, [('        conn.execute(_INSERT_AUDIT_EVENT_SQL, params)', '        pass')], 'test_write_retains_exact_metadata'),
    ('ignore_duplicate', AUDIT, [('INSERT INTO composite_audit_events', 'INSERT OR IGNORE INTO composite_audit_events')], 'test_duplicate'),
    ('replace_duplicate', AUDIT, [('INSERT INTO composite_audit_events', 'INSERT OR REPLACE INTO composite_audit_events')], 'test_duplicate'),
    ('commit_write', AUDIT, [('        conn.execute(_INSERT_AUDIT_EVENT_SQL, params)', '        conn.execute(_INSERT_AUDIT_EVENT_SQL, params)\n        conn.commit()')], 'test_writer_does_not_commit'),
    ('rollback_error', AUDIT, [('    except sqlite3.Error:\n        raise AuditWriteError() from None', '    except sqlite3.Error:\n        conn.rollback()\n        raise AuditWriteError() from None')], 'test_duplicate'),
    ('diagnostic_missing_id', AUDIT, [('        "record_id": record_id,', '        "record_id": None,')], 'test_diagnostic_contains'),
    ('diagnostic_claims_success', AUDIT, [('        "record_id": record_id,', '        "record_id": record_id,\n        "completed": True,')], 'test_diagnostic_contains'),
    ('diagnostic_error_text', AUDIT, [('    del error', '    detail = str(error)'), ('        "record_id": record_id,', '        "record_id": record_id,\n        "detail": detail,')], 'test_diagnostic_contains'),
    ('stored_extra_fields', AUDIT, [('        diagnostics_payload = json.dumps(sanitized)', '        diagnostics_payload = json.dumps({key: value for key, value in diagnostic.items() if key != "error"})')], 'test_writer_sanitizes'),
    ('stored_missing_id', AUDIT, [('            "record_id": diagnostic["record_id"],', '            "record_id": None,')], 'test_writer_sanitizes'),
    ('swallow_write_error', AUDIT, [('        raise AuditWriteError() from None', '        return event.event_id')], 'test_database_error'),
    ('backend_error_text', AUDIT, [('    except sqlite3.Error:\n        raise AuditWriteError() from None', '    except sqlite3.Error as error:\n        raise AuditWriteError(str(error)) from None')], 'test_database_error'),
    ('backend_error_chain', AUDIT, [('        raise AuditWriteError() from None', '        raise AuditWriteError()')], 'test_database_error'),
    ('missing_update_guard', MIGRATIONS, [("BEGIN SELECT RAISE(ABORT, 'audit events are immutable'); END", 'BEGIN SELECT 1; END')], 'test_written_rows'),
    ('missing_delete_guard', MIGRATIONS, [("BEGIN SELECT RAISE(ABORT, 'audit events are kept'); END", 'BEGIN SELECT 1; END')], 'test_written_rows'),
])


def main():
    originals = {rel: (ROOT / rel).read_text() for rel in (AUDIT, MIGRATIONS)}
    with tempfile.TemporaryDirectory(prefix='t046-review-') as directory:
        scratch = Path(directory)
        for rel in ('tests/__init__.py', 'tests/conftest.py', 'composite/__init__.py',
                    'composite/secrets.py', 'composite/repository.py', AUDIT, MIGRATIONS, *TESTS):
            target = scratch / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        shutil.copytree(ROOT / 'tests/_harness', scratch / 'tests/_harness', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable, '-c', 'import composite.audit,composite.migrations,tests; from pathlib import Path; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (composite.audit,composite.migrations,tests))'], cwd=scratch, env=env, check=True)

        def run(selection=None):
            report = scratch / 'report.xml'
            report.unlink(missing_ok=True)
            command = [sys.executable, '-m', 'pytest', *TESTS, '--network=deny', '-q', '--tb=no', f'--junitxml={report}']
            if selection:
                command.extend(['-k', selection])
            result = subprocess.run(command, cwd=scratch, env=env, capture_output=True, text=True, timeout=60)
            assert report.exists(), 'invalid run: missing JUnit'
            cases = list(ET.parse(report).iter('testcase'))
            assert cases and not any(c.find('error') is not None or c.find('skipped') is not None for c in cases), 'invalid collection/setup'
            failures = []
            for case in cases:
                failure = case.find('failure')
                if failure is not None:
                    message = failure.get('message', '')
                    assert not any(word in message for word in ('SyntaxError', 'ImportError', 'ModuleNotFoundError', 'AttributeError', 'KeyError', 'NameError', 'TypeError')), 'invalid mutation failure'
                    failures.append(case.get('name'))
            return result.returncode, len(cases), failures

        code, count, failures = run()
        assert code == 0 and count == 34 and not failures, 'baseline must pass'
        print('REAL IMPLEMENTATION BASELINE: 34 passed', flush=True)
        for identity, rel, edits, expected in MUTATIONS:
            mutated = originals[rel]
            for before, after in edits:
                assert mutated.count(before) == 1, f'{identity}: edit count mismatch'
                mutated = mutated.replace(before, after)
            compile(mutated, rel, 'exec')
            (scratch / rel).write_text(mutated)
            for cache in scratch.rglob('__pycache__'):
                shutil.rmtree(cache)
            code, count, failures = run(expected)
            assert code == 1 and any(name.startswith(expected) for name in failures), f'{identity}: surviving or invalid mutation'
            print(json.dumps({'mutation': identity, 'disposition': 'killed', 'tests': failures}), flush=True)
            (scratch / rel).write_text(originals[rel])
        print(f'{len(MUTATIONS)} mutations killed; no survivors; scratch removed on exit.', flush=True)
        for rel in (AUDIT, MIGRATIONS, *TESTS):
            print(f'SHA256 {rel}: {hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}')


if __name__ == '__main__':
    main()
