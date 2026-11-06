"""T050r source-only scratch reference/mutation verification."""
from pathlib import Path
import ast, hashlib, json, os, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = 'ai_support.py'
PACKET = ['tests/integration/test_composite_ai_country_guards.py']
TESTS = PACKET + ['tests/integration/test_composite_ai_catalog_legacy.py','tests/characterization/test_legacy_renewal_reminders.py']
PRED = '"service_kind" in p.keys() and p["service_kind"] == "composite"'
GUARD = '''    visible = {s["id"] for s in servers}
    for p in products:
        if p["panel_server_id"] in visible and "service_kind" in p.keys() and p["service_kind"] == "composite":
            return {"ok": False, "reason": "composite_unsupported"}

'''
REFUSAL = '            return {"ok": False, "reason": "composite_unsupported"}'
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
    reference = change(production, '_tool_get_server_countries', lambda s: once(s, '    by_server = {}', GUARD + '    by_server = {}'))
    yield 'reference', reference
    def mutate(name, before, after):
        return name, change(reference, '_tool_get_server_countries', lambda s: once(s,before,after))
    yield mutate('omit_guard',GUARD,'')
    yield mutate('wrong_marker',PRED,PRED.replace('== "composite"','== "other"'))
    yield mutate('no_reason','"reason": "composite_unsupported"','"reason": "unavailable"')
    yield mutate('return_countries_with_refusal',REFUSAL,REFUSAL[:-1]+', "countries": []}')
    yield mutate('return_plans_with_refusal',REFUSAL,REFUSAL[:-1]+', "plans": []}')
    yield mutate('write_before_refusal',REFUSAL,'            db.set_setting("bad_guard_write", "1")\n'+REFUSAL)
    yield mutate('reject_missing',PRED,'("service_kind" not in p.keys() or p["service_kind"] == "composite")')
    yield mutate('reject_explicit_legacy',PRED,'"service_kind" in p.keys()')
    yield mutate('scan_excluded_server','p["panel_server_id"] in visible and ','')
    yield mutate('ignore_inactive_products','get_custom_config_products(active_only=True)','get_custom_config_products(active_only=False)')
    yield mutate('ignore_inactive_servers','get_panel_servers(active_only=True)','get_panel_servers(active_only=False)')
    yield mutate('ignore_mirror_filter','get_panel_servers(active_only=True)','get_panel_servers(active_only=True, include_mirrors=True)')
    yield mutate('ignore_custom_use','servers = [s for s in servers if ("used_for_custom_config" not in s.keys()) or s["used_for_custom_config"]]','servers = list(servers)')
    yield mutate('empty_catalog_refused','return {"countries": [], "note": "در حال حاضر سروری برای ساخت کانفیگ شخصی تعریف نشده."}','return {"ok": False, "reason": "composite_unsupported"}')
    for name,before,after in [
        ('wrong_country','"name": s["name"]','"name": "wrong"'),
        ('wrong_product','"product_name": p["name"]','"product_name": "wrong"'),
        ('wrong_min','"min_gb": p["min_gb"]','"min_gb": p["min_gb"]+1'),
        ('wrong_max','"max_gb": p["max_gb"]','"max_gb": p["max_gb"]-1'),
        ('drop_second_plan','for p in plans','for p in plans[:1]'),
        ('drop_second_server','for s in servers:\n        plans','for s in servers[:1]:\n        plans'),
    ]:
        yield mutate(name,before,after)


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
    with tempfile.TemporaryDirectory(prefix='t050r-review-') as directory:
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
    (HERE/'evidence.md').write_text('# T050r reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks active products on visible custom-use servers after real SQL reads before unchanged grouping; no production implementation claim.\n')


if __name__ == '__main__':
    main()
