"""T043 real-code mutations. Run with .venv/bin/python from the repository root.

Copies only the pure module, predicate tests and offline harness into a unique
/tmp directory. Every mutation starts from the unchanged source. No real state,
configuration, network, dependencies or production checkout writes are needed.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
TEST = 'tests/unit/test_models_predicates.py'
MODEL = 'composite/models.py'
FILES = [MODEL, 'composite/__init__.py', TEST, 'tests/__init__.py',
         'tests/unit/__init__.py', 'tests/conftest.py',
         'tests/_harness/__init__.py', 'tests/_harness/network_guard.py']
MUTANTS = []


def add(name, scope, old, new, equivalent=None):
    MUTANTS.append((name, scope, old, new, equivalent))


add('expiry-equality', 'is_expired', 'now >= facts.expires_at', 'now > facts.expires_at')
add('expiry-overstrict', 'is_expired', 'now >= facts.expires_at', 'True')
add('expiry-None', 'is_expired', 'return False', 'return True')
add('expiry-epoch-zero', 'is_expired', 'facts.expires_at is None', 'not facts.expires_at')
add('quota-equality', 'is_exhausted', '>=', '>')
add('quota-overstrict', 'is_exhausted', 'facts.used_bytes >= facts.allowance_bytes', 'True')
add('access-deny-setup', 'desired_access', 'if facts.lifecycle == Lifecycle.PREPARING:\n        pass', 'if facts.lifecycle == Lifecycle.PREPARING:\n        return False')
add('access-deny-fulfilled', 'desired_access', 'elif facts.lifecycle == Lifecycle.FULFILLED:\n        pass', 'elif facts.lifecycle == Lifecycle.FULFILLED:\n        return False')
for state in ('CANCELLED', 'FAILED_UNFULFILLED'):
    add('access-allow-' + state, 'desired_access', 'facts.lifecycle == Lifecycle.PREPARING', f'facts.lifecycle in (Lifecycle.PREPARING, Lifecycle.{state})')
add('access-allow-initial-cancel', 'desired_access', 'facts.cancel_wait_kind == CancelWaitKind.AUTHORIZED_RENEWAL', 'True')
add('access-deny-renewal-wait', 'desired_access', 'facts.cancel_wait_kind == CancelWaitKind.AUTHORIZED_RENEWAL', 'False')
for name, guard in [
    ('final', 'facts.cancel_final_started_at is not None'),
    ('initial', 'facts.initial_delivery_block'),
    ('customer', 'facts.customer_disabled'),
    ('owner', 'facts.owner_suspended'),
    ('reporting', 'facts.reporting_suspended'),
    ('recovery', 'facts.recovery_hold_case is not None'),
    ('expired', 'is_expired(facts, now)'),
    ('exhausted', 'is_exhausted(facts)'),
]:
    add('access-omit-' + name, 'desired_access', f'if {guard}:', 'if False:')
add('access-final-epoch-zero', 'desired_access', 'facts.cancel_final_started_at is not None', 'facts.cancel_final_started_at')
for name, expression in [('publication', 'facts.has_published_generation'),
                         ('availability', 'facts.available_at is not None'),
                         ('replacement', 'not facts.replacement_delivery_block')]:
    add('access-require-' + name, 'desired_access', 'return True', 'return ' + expression)
for state, other in [('REVOKED', 'SUPERSEDED'), ('SUPERSEDED', 'REVOKED')]:
    add('publication-allow-' + state, 'publication', '(TokenStatus.REVOKED, TokenStatus.SUPERSEDED)', f'(TokenStatus.{other},)')
for state, other in [('CANCELLED', 'FAILED_UNFULFILLED'), ('FAILED_UNFULFILLED', 'CANCELLED')]:
    add('publication-allow-' + state, 'publication', '(Lifecycle.CANCELLED, Lifecycle.FAILED_UNFULFILLED)', f'(Lifecycle.{other},)')
for name, expression in [
    ('final', 'facts.cancel_final_started_at is not None'),
    ('candidate', 'token_status == TokenStatus.CANDIDATE'),
    ('preparing', 'facts.lifecycle == Lifecycle.PREPARING'),
    ('initial-cancel', 'facts.cancel_wait_kind == CancelWaitKind.INITIAL_PROVISIONING'),
    ('initial-block', 'facts.initial_delivery_block'),
    ('replacement', 'facts.replacement_delivery_block'),
    ('recovery', 'facts.recovery_hold_case is not None'),
]:
    add('publication-omit-' + name, 'publication', expression, 'False')
add('publication-final-epoch-zero', 'publication', 'facts.cancel_final_started_at is not None', 'facts.cancel_final_started_at')
add('publication-owner-first', 'publication', '    if (', '    if facts.owner_suspended:\n        return Publication.STATUS_ONLY\n\n    if (')  # two matches: narrowed by the helper below
add('publication-owner-needs-generation', 'publication', 'if facts.owner_suspended:', 'if facts.owner_suspended and facts.has_published_generation:')
add('publication-omit-owner', 'publication', 'if facts.owner_suspended:', 'if False:')
add('publication-ignore-generation', 'publication', 'if is_previously_fulfilled and facts.has_published_generation:', 'if is_previously_fulfilled:')
add('publication-ignore-fulfillment', 'publication', 'if is_previously_fulfilled and facts.has_published_generation:', 'if facts.has_published_generation:')
add('publication-deny-renewal-wait', 'publication', 'facts.cancel_wait_kind == CancelWaitKind.AUTHORIZED_RENEWAL', 'False')
for name, condition in [('customer', 'facts.customer_disabled'), ('reporting', 'facts.reporting_suspended'), ('exhaustion', 'is_exhausted(facts)'), ('expiry', 'is_expired(facts, 1_767_225_600_000)')]:
    add('publication-restrict-' + name, 'publication', '    is_previously_fulfilled =', f'    if {condition}:\n        return Publication.UNAVAILABLE\n\n    is_previously_fulfilled =')
add('confirmation-remove-empty-guard', 'confirmed_access', '    if total_attachments == 0:\n        return ConfirmedAccess.UNKNOWN\n', '', 'Equivalent: sum of empty evidence is zero, and the later qualifying_count == 0 guard returns UNKNOWN before any confirmation.')
add('confirmation-freshness-equality', 'confirmed_access', 'rb.observed_at > evidence.latest_write_at', 'rb.observed_at >= evidence.latest_write_at')
add('confirmation-ignore-freshness', 'confirmed_access', 'rb.observed_at > evidence.latest_write_at', 'True')
add('confirmation-ignore-mismatch', 'confirmed_access', 'rb.matches is True', 'True')
add('confirmation-missing-is-match', 'confirmed_access', 'if rb is not None\n        and rb.matches is True\n        and rb.observed_at > evidence.latest_write_at', 'if rb is None or (rb.matches is True and rb.observed_at > evidence.latest_write_at)')
add('confirmation-unknown-is-partial', 'confirmed_access', 'if qualifying_count == 0:\n        return ConfirmedAccess.UNKNOWN', 'if qualifying_count == 0:\n        return ConfirmedAccess.PARTIAL')
add('confirmation-any-is-enough', 'confirmed_access', 'if qualifying_count < total_attachments:', 'if False:')
add('confirmation-partial-is-unknown', 'confirmed_access', 'if qualifying_count < total_attachments:\n        return ConfirmedAccess.PARTIAL', 'if qualifying_count < total_attachments:\n        return ConfirmedAccess.UNKNOWN')
add('confirmation-ignore-runtime', 'confirmed_access', 'if evidence.runtime_required and not evidence.runtime_evidence:', 'if False:')
add('confirmation-always-require-runtime', 'confirmed_access', 'if evidence.runtime_required and not evidence.runtime_evidence:', 'if not evidence.runtime_evidence:')
add('confirmation-runtime-partial-is-unknown', 'confirmed_access', 'if evidence.runtime_required and not evidence.runtime_evidence:\n        return ConfirmedAccess.PARTIAL', 'if evidence.runtime_required and not evidence.runtime_evidence:\n        return ConfirmedAccess.UNKNOWN')
add('confirmation-ignore-requests', 'confirmed_access', 'for req in evidence.uncertain_requests:', 'for req in ():')
add('confirmation-first-request-only', 'confirmed_access', 'for req in evidence.uncertain_requests:', 'for req in evidence.uncertain_requests[:1]:')
add('confirmation-same-state-blocks', 'confirmed_access', 'req.carries == evidence.desired', 'False')
add('confirmation-reducing-state-blocks', 'confirmed_access', 'evidence.desired in (ChildDesiredState.DISABLED, ChildDesiredState.REMOVED)', 'False')
add('confirmation-any-reducing-request-harmless', 'confirmed_access', 'evidence.desired in (ChildDesiredState.DISABLED, ChildDesiredState.REMOVED)\n                and req.carries', 'True\n                and req.carries')
add('confirmation-quarantine-equality', 'confirmed_access', 'now < req.quarantine_until', 'now <= req.quarantine_until')
add('confirmation-expired-request-blocks', 'confirmed_access', 'now < req.quarantine_until', 'True')
add('confirmation-harmless-request-blocks', 'confirmed_access', 'not is_harmless and now', 'now')
add('confirmation-quarantine-partial-is-unknown', 'confirmed_access', 'if not is_harmless and now < req.quarantine_until:\n            return ConfirmedAccess.PARTIAL', 'if not is_harmless and now < req.quarantine_until:\n            return ConfirmedAccess.UNKNOWN')
add('confirmation-enabled-is-denied', 'confirmed_access', 'return ConfirmedAccess.CONFIRMED_ELIGIBLE', 'return ConfirmedAccess.CONFIRMED_FRESH_AUTH_DENIED')
add('confirmation-denied-is-eligible', 'confirmed_access', 'return ConfirmedAccess.CONFIRMED_FRESH_AUTH_DENIED', 'return ConfirmedAccess.CONFIRMED_ELIGIBLE')
for cls in ('SubscriptionAccessFacts', 'AttachmentReadBack', 'UncertainRequest', 'ChildAccessEvidence'):
    add('mutable-' + cls, None, '@dataclass(frozen=True)\nclass ' + cls, '@dataclass(frozen=False)\nclass ' + cls)


def mutate(source, scope, old, new, name):
    start, end = 0, len(source)
    if scope is not None:
        function, = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == scope]
        lines = source.splitlines(keepends=True)
        start, end = sum(map(len, lines[:function.lineno - 1])), sum(map(len, lines[:function.end_lineno]))
    section = source[start:end]
    expected = 2 if name == 'publication-owner-first' else 1
    assert section.count(old) == expected, (name, section.count(old), expected)
    changed = source[:start] + section.replace(old, new, 1) + source[end:]
    assert changed != source
    compile(changed, MODEL, 'exec')
    return changed


def main():
    source = (ROOT / MODEL).read_text()
    results = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
               'test_sha256': hashlib.sha256((ROOT / TEST).read_bytes()).hexdigest(), 'mutants': []}
    with tempfile.TemporaryDirectory(prefix='shopvpn-t043-mutations-') as directory:
        scratch = Path(directory)
        for relative in FILES:
            src = ROOT / relative
            if src.exists():
                dst = scratch / relative
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        env = {**os.environ, 'PYTHONPATH': str(scratch), 'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'}
        imported = subprocess.check_output([sys.executable, '-B', '-c', 'import composite.models as m; print(m.__file__)'], cwd=scratch, env=env, text=True).strip()
        assert imported == str(scratch / MODEL), imported

        def run():
            process = subprocess.run([sys.executable, '-B', '-m', 'pytest', TEST, '--network=deny', '-q', '-x', '--tb=short', '-p', 'no:cacheprovider', '--junitxml=result.xml'], cwd=scratch, env=env, capture_output=True, text=True, timeout=30)
            xml = ET.parse(scratch / 'result.xml').getroot()
            assert not xml.findall('.//error'), process.stdout
            failures = [(case.attrib['name'], case.find('failure')) for case in xml.findall('.//testcase') if case.find('failure') is not None]
            for name, failure in failures:
                body = (failure.text or '')
                assert 'AssertionError' in body or 'Failed: DID NOT RAISE' in body, (name, body)
            return process.returncode, failures, len(xml.findall('.//testcase'))

        code, failures, count = run()
        assert code == 0 and not failures, 'Unmodified baseline failed'
        results['baseline_passed'] = count
        for name, scope, old, new, equivalent in MUTANTS:
            (scratch / MODEL).write_text(mutate(source, scope, old, new, name))
            code, failures, count = run()
            disposition = 'killed' if code == 1 and failures else 'equivalent' if code == 0 and equivalent else 'SURVIVED' if code == 0 else 'INVALID'
            result = {'id': name, 'disposition': disposition, 'failure': failures[0][0] if failures else None}
            if equivalent:
                result['proof'] = equivalent
            results['mutants'].append(result)
            print(json.dumps(result), flush=True)
        (scratch / MODEL).write_text(source)
        code, failures, count = run()
        assert code == 0 and count == results['baseline_passed']
    results['scratch_deleted'] = True
    print('RESULT_JSON=' + json.dumps(results), flush=True)
    assert all(r['disposition'] in ('killed', 'equivalent') for r in results['mutants']), 'Unresolved mutants'


if __name__ == '__main__':
    main()
