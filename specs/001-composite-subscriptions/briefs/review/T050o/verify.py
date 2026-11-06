"""T050o executable trial eligibility guard reference and independent scratch mutations."""
from pathlib import Path
import ast
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
SOURCE = 'ai_support.py'
PACKET = ['tests/integration/test_composite_ai_trial_guards.py']
TESTS = PACKET + ['tests/characterization/test_free_test_flow.py', 'tests/characterization/test_legacy_renewal_reminders.py']
PRED = '"service_kind" in plan.keys() and plan["service_kind"] == "composite"'
GUARD = ('    for plan in plans:\n'
         '        if "service_kind" in plan.keys() and plan["service_kind"] == "composite":\n'
         '            return {"eligible": False, "reason": "composite_unsupported"}\n')
REFUSAL = '            return {"eligible": False, "reason": "composite_unsupported"}'

def once(s, before, after):
    assert s.count(before) == 1, (before, s.count(before))
    return s.replace(before, after)


def change(source, name, fn):
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.AsyncFunctionDef) and n.name == name]
    assert len(nodes) == 1
    n = nodes[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1]) + fn(''.join(lines[n.lineno-1:n.end_lineno])) + ''.join(lines[n.end_lineno:])


def variants(production):
    reference = change(production, '_tool_request_test_config', lambda s: once(s, '    if not test_enabled:', GUARD + '    if not test_enabled:'))
    yield 'reference', reference
    def mutate(name, before, after):
        return name, change(reference, '_tool_request_test_config', lambda s: once(s, before, after))
    yield mutate('omit_guard', GUARD, '')
    yield mutate('wrong_marker', PRED, PRED.replace('== "composite"', '== "other"'))
    yield mutate('only_first_plan', 'for plan in plans:', 'for plan in plans[:1]:')
    yield mutate('reject_missing', PRED, '"service_kind" not in plan.keys() or plan["service_kind"] == "composite"')
    yield mutate('reject_explicit_legacy', PRED, '"service_kind" in plan.keys()')
    yield mutate('no_reason', '"reason": "composite_unsupported"', '"reason": "unavailable"')
    yield mutate('leak_name', REFUSAL, '            return {"eligible": False, "reason": "composite_unsupported", "name": plan["name"]}')
    yield mutate('log_name', REFUSAL, '            _log.warning("%s", plan["name"])\n' + REFUSAL)
    yield mutate('reserve_before_refusal', REFUSAL, '            db.try_reserve_test_slot(user_tg_id, config.MAX_TEST_PER_USER)\n' + REFUSAL)
    yield mutate('include_inactive', 'db.get_test_config_plans(True)', 'db.get_test_config_plans(False)')
    yield mutate('ignore_disabled', 'if not test_enabled:', 'if False:')
    yield mutate('ignore_used', 'if test_used >= config.MAX_TEST_PER_USER:', 'if False:')
    yield mutate('allow_one_extra', 'if test_used >= config.MAX_TEST_PER_USER:', 'if test_used > config.MAX_TEST_PER_USER:')
    yield mutate('refuse_unused', 'if test_used >= config.MAX_TEST_PER_USER:', 'if test_used >= 0:')
    yield mutate('ignore_no_plan', 'if not plans:', 'if False:')
    yield mutate('reject_missing_user', 'test_used = user["test_used"] if user else 0', 'test_used = user["test_used"] if user else config.MAX_TEST_PER_USER')
    yield mutate('reserve_on_eligibility', '    return {"eligible": True}', '    db.try_reserve_test_slot(user_tg_id, config.MAX_TEST_PER_USER)\n    return {"eligible": True}')

def main():
    snap = json.loads((HERE/'snapshot.json').read_text())
    # Durable reproduction checks examined code, independent of later commits/log edits.
    # Full protected-tree and git-diff checks were performed separately at acceptance.
    for p in [SOURCE, *TESTS]:
        if p in snap['hashes']:
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == snap['hashes'][p], p
    production = (ROOT/SOURCE).read_text()
    mutations = list(variants(production))
    assert len({n for n, _ in mutations}) == len(mutations)
    for name, source in mutations:
        ast.parse(source)
        if name != 'reference':
            assert source != mutations[0][1], name
    if '--preflight' in sys.argv:
        print('preflight', len(mutations), 'valid transformations')
        return
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE, *TESTS]}
    records = []
    with tempfile.TemporaryDirectory(prefix='t050o-review-') as directory:
        scratch = Path(directory)
        paths = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode().split('\0') + PACKET
        for rel in set(paths):
            p = Path(rel)
            if p.suffix != '.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):
                continue
            dest = scratch/rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/rel, dest)
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE='1', PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable, '-c', 'from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();from pathlib import Path;import ai_support,tests;assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (ai_support,tests))'], cwd=scratch, env=env, check=True)
        for name, source in mutations:
            (scratch/SOURCE).write_text(source)
            xml = scratch/'result.xml'
            proc = subprocess.run([sys.executable,'-m','pytest',*(TESTS if name=='reference' else PACKET),'--network=deny','-q','--tb=line',f'--junitxml={xml}'], cwd=scratch, env=env, capture_output=True, text=True, timeout=90)
            tree = ET.parse(xml)
            cases = list(tree.iter('testcase'))
            failed = [(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')), (name,proc.stdout,proc.stderr)
            if name=='reference':
                assert proc.returncode==0 and not failed, (proc.stdout,proc.stderr)
            else:
                assert proc.returncode==1 and failed, (name,proc.stdout,proc.stderr)
                for c,f in failed:
                    assert 'assert' in (f.get('message','')+(f.text or '')).lower(), (name,c.attrib,f.text)
                    assert c.get('classname') in {p.removesuffix('.py').replace('/','.') for p in PACKET}
            records.append({'name':name,'disposition':'passed' if name=='reference' else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name, records[-1]['disposition'], len(cases), flush=True)
    (HERE/'evidence.md').write_text('# T050o reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks active test-plan metadata inside real eligibility function before unchanged legacy eligibility checks; no production implementation claim.\n')


if __name__ == '__main__':
    main()
