"""T050q executable custom renewal guard reference and independent scratch mutations."""
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
PACKET = ['tests/integration/test_composite_ai_renewal_guards.py']
TESTS = PACKET + ['tests/characterization/test_legacy_renewal_reminders.py']
TG = '    if target["kind"] == "custom":\n        record = target["custom"]\n        if "service_kind" in record.keys() and record["service_kind"] == "composite":\n            return {"ok": False, "reason": "composite_unsupported"}\n'
PG = '        if "service_kind" in product.keys() and product["service_kind"] == "composite":\n            return {"ok": False, "reason": "composite_unsupported"}\n'

def once(s, before, after):
    assert s.count(before) == 1, (before, s.count(before))
    return s.replace(before, after)


def change(source, name, fn):
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef)) and n.name == name]
    assert len(nodes) == 1
    n = nodes[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1]) + fn(''.join(lines[n.lineno-1:n.end_lineno])) + ''.join(lines[n.end_lineno:])


def variants(production):
    reference = change(production, '_prepare_renewal', lambda s: once(once(s, '    def _is_test():', TG + '    def _is_test():'), '        price = product["price"]', PG + '        price = product["price"]'))
    yield 'reference', reference
    def gate(name, block, before, after):
        return name, change(reference, '_prepare_renewal', lambda s: once(s, block, once(block, before, after)))
    for label,block,variable in [('service',TG,'record'),('product',PG,'product')]:
        pred = f'"service_kind" in {variable}.keys() and {variable}["service_kind"] == "composite"'
        yield label+'_omit', change(reference, '_prepare_renewal', lambda s,block=block: once(s,block,''))
        yield gate(label+'_wrong_marker', block, pred, pred.replace('== "composite"','== "other"'))
        yield gate(label+'_reject_missing', block, pred, f'"service_kind" not in {variable}.keys() or {variable}["service_kind"] == "composite"')
        yield gate(label+'_reject_legacy', block, pred, f'"service_kind" in {variable}.keys()')
        yield gate(label+'_no_reason', block, '"reason": "composite_unsupported"','"reason": "unavailable"')
        field = 'subscription_url' if label=='service' else 'name'
        yield gate(label+'_leak', block, '"reason": "composite_unsupported"', f'"reason": "composite_unsupported", "leak": {variable}["{field}"]')
        refusal = '            return {"ok": False, "reason": "composite_unsupported"}'
        yield gate(label+'_log', block, refusal, f'            _log.warning("%s", {variable}["{field}"])\n'+refusal)
        yield gate(label+'_debit_before_refusal', block, refusal, '            db.add_wallet_credit(user_tg_id, -1)\n'+refusal)
    yield 'omit_both', change(reference, '_prepare_renewal', lambda s: once(once(s,TG,''),PG,''))
    for name,before,after in [
        ('wrong_full_price','price = product["price"]','price = product["price"] + 1'),
        ('wrong_summary','summary_label = product["name"]','summary_label = "wrong"'),
        ('float_price','"price_toman": price,','"price_toman": float(price),'),
        ('wrong_wallet_balance','"wallet_balance_toman": wallet_credit,','"wallet_balance_toman": wallet_credit + 1,'),
        ('wallet_equal_refused','wallet_credit >= price,','wallet_credit > price,'),
        ('wallet_one_short_allowed','wallet_credit >= price,','wallet_credit >= price - 1,'),
        ('wrong_service_id','"service_id": service_id,','"service_id": "x999",'),
        ('wrong_amount','"amount": args.get("amount"),','"amount": 999,'),
        ('wrong_product_id','"product_id": args.get("product_id"),','"product_id": "999",'),
        ('wrong_mode','"mode": mode,','"mode": "wrong",'),
        ('debit_on_quote','    wallet_credit = await asyncio.to_thread(db.get_wallet_credit, user_tg_id)','    db.add_wallet_credit(user_tg_id, -1)\n    wallet_credit = await asyncio.to_thread(db.get_wallet_credit, user_tg_id)'),
    ]:
        yield name, change(reference, '_prepare_renewal', lambda s,b=before,a=after: once(s,b,a))
    yield 'wrong_addon_rate', change(reference, '_renewal_rate_and_price', lambda s: once(s, 'rate_key = "renewal_price_per_gb" if mode == "volume" else "renewal_price_per_day"', 'rate_key = "renewal_price_per_gb"'))
    yield 'wrong_addon_amount', change(reference, '_renewal_rate_and_price', lambda s: once(s, 'return amount, amount * rate', 'return amount, (amount + 1) * rate'))
    yield 'renew_insufficient_allowed', change(reference, '_tool_renew_service_with_wallet', lambda s: once(s, 'if not result["wallet_covers_full_amount"]:', 'if False:'))
    yield 'wrong_owner', change(reference, '_resolve_service_target', lambda s: once(s, 'db.get_custom_config_owned(target_id, user_tg_id)', 'db.get_custom_config_owned(target_id, 1001)'))
    yield 'irrelevant_product_overblock', change(reference, '_prepare_renewal', lambda s: once(s, '    if mode == "full":', '    for unused_product in [await asyncio.to_thread(db.get_product, 1)]:\n        if "service_kind" in unused_product.keys() and unused_product["service_kind"] == "composite":\n            return {"ok": False, "reason": "composite_unsupported"}\n    if mode == "full":'))

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
    with tempfile.TemporaryDirectory(prefix='t050q-review-') as directory:
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
    (HERE/'evidence.md').write_text('# T050q reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks owned custom target and full-renewal selected product inside real preparation function; unchanged real price/wallet/ownership logic remains active. No production implementation claim.\n')


if __name__ == '__main__':
    main()
