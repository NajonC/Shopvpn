"""T050u source-only scratch account reference and independent mutations."""
from pathlib import Path
import ast, hashlib, json, os, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = 'ai_support.py'
PACKET = ['tests/integration/test_composite_ai_account_guards.py']
TESTS = PACKET + ['tests/characterization/test_legacy_renewal_reminders.py']
PRED = '"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD = '''    records = [o for o in orders if o["status"] != "rejected"] + list(custom_configs)
    for order in orders:
        if order["status"] == "approved" and order["config_id"]:
            cfg = await asyncio.to_thread(db.get_config_by_id, order["config_id"])
            if cfg:
                records.append(cfg)
    for record in records:
        if "service_kind" in record.keys() and record["service_kind"] == "composite":
            return {"ok": False, "reason": "composite_unsupported"}

'''
REFUSAL = '            return {"ok": False, "reason": "composite_unsupported"}'
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
    reference = change(production,'_tool_check_account_status',lambda s:once(s,'    pending = [',GUARD+'    pending = ['))
    yield 'reference', reference
    def mutate(name,before,after,func='_tool_check_account_status'):
        return name,change(reference,func,lambda s:once(s,before,after))
    yield mutate('omit_all',GUARD,'')
    yield mutate('omit_order','[o for o in orders if o["status"] != "rejected"] + list(custom_configs)','list(custom_configs)')
    yield mutate('omit_custom',' + list(custom_configs)',' + []')
    yield mutate('omit_config','records.append(cfg)','pass')
    yield mutate('omit_pending','o["status"] != "rejected"','o["status"] == "approved"')
    yield mutate('wrong_marker',PRED,PRED.replace('== "composite"','== "other"'))
    yield mutate('reject_missing',PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"')
    yield mutate('reject_legacy',PRED,'"service_kind" in record.keys()')
    yield mutate('no_reason','"reason": "composite_unsupported"','"reason": "unavailable"')
    yield mutate('expose_services',REFUSAL,REFUSAL[:-1]+', "active_services": []}')
    yield mutate('expose_pending',REFUSAL,REFUSAL[:-1]+', "pending_orders": []}')
    link='(record["link"] if "link" in record.keys() else record["subscription_url"] if "subscription_url" in record.keys() else "")'
    yield mutate('leak_response',REFUSAL,REFUSAL[:-1]+', "leak": '+link+'}')
    yield mutate('leak_log',REFUSAL,'            _log.warning("%s", '+link+')\n'+REFUSAL)
    yield mutate('fetch_before_refusal',REFUSAL,'            await fetch_sub_info("https://sub.example.invalid/too-early")\n'+REFUSAL)
    yield mutate('provider_before_refusal',REFUSAL,'            get_provider(await asyncio.to_thread(db.get_panel_server, 1))\n'+REFUSAL)
    yield mutate('debit_before_refusal',REFUSAL,'            db.add_wallet_credit(user_tg_id, -1)\n'+REFUSAL)
    yield mutate('wrong_order_owner','db.get_user_orders(user_tg_id)','db.get_user_orders(5101)')
    yield mutate('wrong_custom_owner','db.get_custom_configs_for_user(user_tg_id)','db.get_custom_configs_for_user(5101)')
    yield mutate('include_rejected','[o for o in orders if o["status"] != "rejected"]','list(orders)')
    yield mutate('include_hidden','orders = db.get_user_orders(user_tg_id)','with db._get_conn() as conn:\n            orders = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user_tg_id,)).fetchall()')
    for name,before,after in [
        ('wrong_wallet','"wallet_balance_toman": wallet,','"wallet_balance_toman": wallet + 1,'),
        ('float_wallet','"wallet_balance_toman": wallet,','"wallet_balance_toman": float(wallet),'),
        ('wrong_stock_id','f"c{cfg[\'id\']}"','"c999"'),
        ('wrong_custom_id','f"x{cc[\'id\']}"','"x999"'),
        ('wrong_custom_name','"name": cc["display_name"] or cc["username"]','"name": "wrong"'),
        ('wrong_enabled','bool(cc["enabled"])','not bool(cc["enabled"])'),
        ('wrong_auto','bool(cc["auto_renew"])','not bool(cc["auto_renew"])'),
        ('wrong_panel_status','"فعال" if usage.get("status") == "active" else "غیرفعال"','"غیرفعال"'),
        ('drop_stock','*[_plan_service(o) for o in approved_with_config]','*[]'),
        ('drop_custom','*[_custom_service(cc) for cc in custom_configs]','*[]'),
        ('drop_pending','"pending_orders": pending,','"pending_orders": [],'),
        ('write_on_read','    pending = [','    db.set_setting("bad_read_write", "1")\n    pending = ['),
    ]:
        yield mutate(name,before,after)
    for field in ['used_gb','total_gb','remaining_gb']:
        before={'used_gb':'"used_gb": _gb(used)','total_gb':'"total_gb": _gb(total) if total else "نامحدود"','remaining_gb':'out["remaining_gb"] = _gb(max(0, total - used))'}[field]
        after=before.replace('_gb(used)','_gb(used) + 1').replace('_gb(total)','_gb(total) + 1').replace('_gb(max(0, total - used))','_gb(max(0, total - used)) + 1')
        yield mutate('wrong_'+field,before,after,'_summarize_sub_info')


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
    with tempfile.TemporaryDirectory(prefix='t050u-review-') as directory:
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
    (HERE/'evidence.md').write_text('# T050u reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks contributing requester-owned account rows before unchanged real account fetch/summary flow; no production implementation claim.\n')


if __name__ == '__main__':
    main()
