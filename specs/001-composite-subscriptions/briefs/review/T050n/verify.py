"""T050n executable catalog guard reference and independent scratch mutations."""
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
PACKET = ['tests/integration/test_composite_ai_catalog_guards.py', 'tests/integration/test_composite_ai_catalog_legacy.py']
TESTS = PACKET + ['tests/characterization/test_legacy_renewal_reminders.py']
PRED = '"service_kind" in product.keys() and product["service_kind"] == "composite"'
GUARD = '''    if name in {"list_products", "show_purchase_options"}:
        if name == "list_products":
            products = [p for cat in await asyncio.to_thread(db.get_categories, active_only=True)
                        for p in await asyncio.to_thread(db.get_products, cat["id"], active_only=True)]
        else:
            try:
                selected = int(args.get("product_id"))
            except (TypeError, ValueError):
                products = []
            else:
                product = await asyncio.to_thread(db.get_product, selected)
                products = [product] if product and product["is_active"] else []
        for product in products:
            if "service_kind" in product.keys() and product["service_kind"] == "composite":
                return {"ok": False, "reason": "composite_unsupported"}
'''
REFUSAL = '                return {"ok": False, "reason": "composite_unsupported"}'


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
    reference = change(production, '_run_tool_uncached', lambda s: once(s, '    if name == "check_account_status":', GUARD + '    if name == "check_account_status":'))
    yield 'reference', reference
    def guard(name, before, after):
        return name, change(reference, '_run_tool_uncached', lambda s: once(s, before, after))
    yield guard('omit_both_gates', GUARD, '')
    yield guard('omit_catalog', 'if name in {"list_products", "show_purchase_options"}:', 'if name in {"show_purchase_options"}:')
    yield guard('omit_options', 'if name in {"list_products", "show_purchase_options"}:', 'if name in {"list_products"}:')
    yield guard('wrong_marker', PRED, PRED.replace('== "composite"', '== "other"'))
    yield guard('reject_missing', PRED, '"service_kind" not in product.keys() or product["service_kind"] == "composite"')
    yield guard('reject_explicit_legacy', PRED, '"service_kind" in product.keys()')
    yield guard('no_reason', '"reason": "composite_unsupported"', '"reason": "unavailable"')
    yield guard('leak_name', REFUSAL, '                return {"ok": False, "reason": "composite_unsupported", "name": product["name"]}')
    yield guard('log_name', REFUSAL, '                _log.warning("%s", product["name"])\n' + REFUSAL)
    yield guard('count_before_refusal', REFUSAL, '                db.count_available_configs(product["id"])\n' + REFUSAL)
    yield guard('write_before_refusal', REFUSAL, '                db.set_setting("bad_guard_write", "1")\n' + REFUSAL)
    for category, condition in [('stock', 'product["name"] != "SECRET-AI-PRODUCT" or product["id"] != 1'), ('auto', 'not product["is_auto_provision"]'), ('empty', 'product["id"] != 3')]:
        yield guard('omit_' + category, PRED, '(' + PRED + ') and (' + condition + ')')
    yield guard('options_scan_unrelated', '        if name == "list_products":', '        if name in {"list_products", "show_purchase_options"}:')
    yield guard('late_catalog_preflight', 'for product in products:', 'for product in products:\n            if name == "list_products" and not product["is_auto_provision"]:\n                db.count_available_configs(product["id"])')
    for name, before, after in [
        ('wrong_price', '"price_toman": p["price"]', '"price_toman": p["price"] + 1'),
        ('wrong_duration', '"duration_days": p["duration_days"]', '"duration_days": 1'),
        ('wrong_description', '"description": p["description"] or ""', '"description": "wrong"'),
        ('wrong_stock_count', 'else stock,', 'else stock + 1,'),
        ('empty_marked_available', 'else stock > 0,', 'else stock >= 0,'),
        ('automatic_marked_unavailable', 'True if p["is_auto_provision"]', 'False if p["is_auto_provision"]'),
        ('lost_product', 'for p in products:', 'for p in products[:1]:'),
    ]:
        yield name, change(reference, '_tool_list_products', lambda s, b=before, a=after: once(s, b, a))
    for name, before, after in [
        ('wrong_option_id', '"product_id": product_id,', '"product_id": product_id + 1,'),
        ('wrong_option_name', '"name": product["name"]', '"name": "wrong"'),
    ]:
        yield name, change(reference, '_tool_show_purchase_options', lambda s, b=before, a=after: once(s, b, a))


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
    with tempfile.TemporaryDirectory(prefix='t050n-review-') as directory:
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
    (HERE/'evidence.md').write_text('# T050n reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference preflights real catalog rows through real getters before the unchanged real dispatcher/catalog output; no production implementation claim.\n')


if __name__ == '__main__':
    main()
