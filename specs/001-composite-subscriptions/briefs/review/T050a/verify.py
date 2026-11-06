"""Scratch-only reference and independent mutations for T050a; no production edits."""
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
TESTS = ['tests/integration/test_composite_legacy_guards.py',
         'tests/integration/test_composite_stock_guards.py',
         'tests/characterization/test_legacy_renewal_reminders.py']
MANUAL = 'renewal_engine.py'
STOCK = 'stock_alerts.py'
MG = ('    if "service_kind" in order.keys() and order["service_kind"] == "composite":\n'
      '        raise RenewalError("Composite order cannot use legacy renewal")\n')
SG = ('    product = db.get_product(product_id)\n'
      '    if product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite":\n'
      '        logger.warning("Composite product refused by legacy stock alert")\n'
      '        return\n')


def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def main():
    snapshot = json.loads((HERE / 'snapshot.json').read_text())
    changed = [p for p, sha in snapshot['hashes'].items()
               if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != sha]
    assert not changed, changed
    assert hashlib.sha256((ROOT / TESTS[0]).read_bytes()).hexdigest() == snapshot['protected_test_sha256']
    assert subprocess.check_output(['git','diff','--cached'], cwd=ROOT).decode() == snapshot['staged']
    assert subprocess.check_output(['git','diff'], cwd=ROOT).decode() == snapshot['unstaged']
    source_hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                     for p in [MANUAL, STOCK, *TESTS]}
    results = []
    with tempfile.TemporaryDirectory(prefix='t050a-review-') as directory:
        scratch = Path(directory)
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        paths += TESTS
        for rel in set(paths):
            p = Path(rel)
            if p.suffix != '.py' or (len(p.parts) > 1 and p.parts[0] not in {
                    'tests', 'composite', 'panel_providers', 'admin_panel', 'miniapp'}):
                continue
            dest = scratch / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE='1', PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable, '-c', 'from pathlib import Path; import renewal_engine, stock_alerts, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (renewal_engine,stock_alerts,tests))'], cwd=scratch, env=env, check=True)
        original = {p: (scratch / p).read_text() for p in (MANUAL, STOCK)}
        reference = {
            MANUAL: replace_once(original[MANUAL], '    kind = order["renewal_target_kind"]', MG + '    kind = order["renewal_target_kind"]'),
            STOCK: replace_once(original[STOCK], '    try:\n        stock =', SG + '    try:\n        stock ='),
        }
        mutations = [
            ('manual_omit', MANUAL, MG, ''),
            ('manual_wrong_kind', MANUAL, 'order["service_kind"] == "composite"', 'order["service_kind"] == "other"'),
            ('manual_reject_legacy', MANUAL, 'order["service_kind"] == "composite"', 'True'),
            ('manual_reject_absent', MANUAL, '"service_kind" in order.keys() and order["service_kind"] == "composite"', '"service_kind" not in order.keys() or order["service_kind"] == "composite"'),
            ('stock_omit', STOCK, SG, ''),
            ('stock_no_reason', STOCK, '        logger.warning("Composite product refused by legacy stock alert")\n', ''),
            ('stock_leak_name', STOCK, 'logger.warning("Composite product refused by legacy stock alert")', 'logger.warning("Composite stock refused %s", product["name"])'),
            ('stock_reject_legacy', STOCK, 'product["service_kind"] == "composite"', 'True'),
            ('stock_reject_absent', STOCK, '"service_kind" in product.keys() and product["service_kind"] == "composite"', '("service_kind" not in product.keys() or product["service_kind"] == "composite")'),
        ]

        def run(name, sources, baseline=False):
            for p, source in sources.items():
                (scratch / p).write_text(source)
            report = scratch / 'result.xml'
            proc = subprocess.run([sys.executable, '-m', 'pytest', *(TESTS if baseline else TESTS[:2]), '--network=deny', '-q', '--tb=line', f'--junitxml={report}'], cwd=scratch, env=env, capture_output=True, text=True, timeout=90)
            tree = ET.parse(report)
            cases = list(tree.iter('testcase'))
            failures = [(c, c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')), proc.stdout + proc.stderr
            if baseline:
                assert proc.returncode == 0 and not failures, proc.stdout + proc.stderr
            else:
                assert proc.returncode == 1 and failures, (name, proc.stdout + proc.stderr)
                for case, failure in failures:
                    text = (failure.get('message', '') + (failure.text or '')).lower()
                    assert (any(marker in text for marker in ('assert ', 'assertionerror', 'did not raise'))
                            or (name in {'manual_reject_legacy', 'manual_reject_absent'}
                                and case.get('name', '').startswith('test_legacy_manual_renewal_still_runs')
                                and text.startswith('renewal_engine.renewalerror: composite order cannot use legacy renewal'))), (name, text)
                    assert case.get('classname', '').startswith('tests.integration.test_composite_'), (name, case.attrib)
            results.append({'name':name,'passes':len(cases)-len(failures),'failed_test_ids':[c.get('classname') + '::' + c.get('name') for c, _ in failures], 'disposition':'pass' if baseline else 'killed'})
            print(name, results[-1]['disposition'], len(cases), flush=True)

        run('reference', reference, True)
        for name, path, before, after in mutations:
            mutant = dict(reference)
            mutant[path] = replace_once(mutant[path], before, after)
            run(name, mutant)
        # Ordering mutants must still explicitly refuse, but after an observable effect.
        late = dict(reference)
        late[MANUAL] = replace_once(late[MANUAL], MG, '').replace('        return "✅ سرویس شما با موفقیت تمدید شد."', MG.replace('    ', '        ', 1).replace('        raise', '            raise') + '        return "✅ سرویس شما با موفقیت تمدید شد."')
        assert late[MANUAL] != reference[MANUAL]
        run('manual_late', late)
        late = dict(reference)
        late[STOCK] = replace_once(late[STOCK], SG, '')
        late[STOCK] = replace_once(late[STOCK], '    if not should_alert:', SG + '    if not should_alert:')
        run('stock_late', late)
    (HERE / 'evidence.md').write_text('# T050a reference and mutations\n\nSource SHA256:\n```json\n' + json.dumps(source_hashes, indent=2) + '\n```\n\nResults:\n```json\n' + json.dumps(results, indent=2) + '\n```\n\nAll mutants independently applied to the passing reference. All failures are relevant packet assertions or the exact expected RenewalError from deliberate over-strict mutations on legacy-positive cases; no errors/skips. Scratch automatically deleted.\n')


if __name__ == '__main__':
    main()
