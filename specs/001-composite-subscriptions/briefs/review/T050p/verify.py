"""T050p executable wallet shortcut guard reference and independent scratch mutations."""
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
PACKET = ['tests/integration/test_composite_ai_wallet_guards.py']
TESTS = PACKET + ['tests/characterization/test_unsupported_surfaces.py']
PRED = '"service_kind" in product.keys() and product["service_kind"] == "composite"'
GUARD = '    if name == "request_purchase_with_wallet":\n        try:\n            selected = int(args.get("product_id"))\n        except (TypeError, ValueError):\n            product = None\n        else:\n            product = await asyncio.to_thread(db.get_product, selected)\n        if product and product["is_active"]:\n            if "service_kind" in product.keys() and product["service_kind"] == "composite":\n                return {"ok": False, "reason": "composite_unsupported"}\n'
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
    yield guard('omit_guard', GUARD, '')
    yield guard('wrong_marker', PRED, PRED.replace('== "composite"', '== "other"'))
    yield guard('omit_stock', PRED, '('+PRED+') and product["is_auto_provision"]')
    yield guard('omit_auto', PRED, '('+PRED+') and not product["is_auto_provision"]')
    yield guard('reject_missing', PRED, '"service_kind" not in product.keys() or product["service_kind"] == "composite"')
    yield guard('reject_explicit_legacy', PRED, '"service_kind" in product.keys()')
    yield guard('no_reason', '"reason": "composite_unsupported"', '"reason": "unavailable"')
    yield guard('leak_name', REFUSAL, '                return {"ok": False, "reason": "composite_unsupported", "name": product["name"]}')
    yield guard('log_name', REFUSAL, '                _log.warning("%s", product["name"])\n' + REFUSAL)
    yield guard('count_before_refusal', REFUSAL, '                db.count_available_configs(product["id"])\n' + REFUSAL)
    yield guard('debit_before_refusal', REFUSAL, '                db.add_wallet_credit(user_tg_id, -1)\n' + REFUSAL)
    yield guard('unrelated_overblock', '        if product and product["is_active"]:', '        for product in await asyncio.to_thread(db.get_all_products):')
    for name,before,after in [
        ('wrong_price', 'total_price = product["price"] * quantity', 'total_price = product["price"] * quantity + 1'),
        ('ignore_quantity', 'total_price = product["price"] * quantity', 'total_price = product["price"]'),
        ('float_price', 'total_price = product["price"] * quantity', 'total_price = product["price"] * quantity / 1'),
        ('wallet_equal_refused', 'wallet_credit < total_price:', 'wallet_credit <= total_price:'),
        ('wallet_one_short_allowed', 'wallet_credit < total_price:', 'wallet_credit < total_price - 1:'),
        ('ignore_stock', 'if stock is not None and stock < quantity:', 'if False:'),
        ('ignore_wallet_permission', 'if not wallet_allowed:', 'if False:'),
        ('wrong_quantity', '"quantity": quantity,', '"quantity": 1,'),
        ('wrong_product', '"product_id": product_id,', '"product_id": product_id + 1,'),
        ('debit_on_preview', '    return {"ok": True, "product_id": product_id', '    db.add_wallet_credit(user_tg_id, -total_price)\n    return {"ok": True, "product_id": product_id'),
    ]:
        yield name, change(reference, '_tool_request_purchase_with_wallet', lambda s,b=before,a=after: once(s,b,a))

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
    with tempfile.TemporaryDirectory(prefix='t050p-review-') as directory:
        scratch = Path(directory)
        # StaticFiles mount requires a directory; no UI assets needed by API tests.
        (scratch/'miniapp/static').mkdir(parents=True)
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
    (HERE/'evidence.md').write_text('# T050p reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference preflights selected product metadata before the unchanged real wallet-purchase shortcut; real reads/prices/permissions/stock remain active. No production implementation claim.\n')


if __name__ == '__main__':
    main()
