"""T050s source-only scratch reference/mutations."""
from pathlib import Path
import ast, hashlib, json, os, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = 'ai_support.py'
PACKET = ['tests/integration/test_composite_ai_stock_retrieval_guards.py']
TESTS = PACKET + ['tests/characterization/test_legacy_renewal_reminders.py']
PRED = '"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD = '''    if name in {"request_service_qr", "request_individual_configs"}:
        target = await _resolve_service_target(db, user_tg_id, args.get("service_id"))
        if target and target["kind"] == "config":
            cfg = target["config"]
            orders = await asyncio.to_thread(db.get_user_orders, user_tg_id)
            records = [cfg] + [o for o in orders if o["config_id"] == cfg["id"] and o["status"] == "approved"]
            for record in records:
                if "service_kind" in record.keys() and record["service_kind"] == "composite":
                    return {"ok": False, "reason": "composite_unsupported"}
'''
REFUSAL = '                    return {"ok": False, "reason": "composite_unsupported"}'
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
    reference = change(production, '_run_tool_uncached', lambda s: once(s,'    if name == "check_account_status":',GUARD+'    if name == "check_account_status":'))
    yield 'reference', reference
    def mutate(name,before,after,func='_run_tool_uncached'):
        return name,change(reference,func,lambda s:once(s,before,after))
    yield mutate('omit_both',GUARD,'')
    yield mutate('omit_config','records = [cfg] +','records = [] +')
    yield mutate('omit_order','records = [cfg] + [o for o in orders if o["config_id"] == cfg["id"] and o["status"] == "approved"]','records = [cfg]')
    yield mutate('omit_qr','if name in {"request_service_qr", "request_individual_configs"}:','if name in {"request_individual_configs"}:')
    yield mutate('omit_individual','if name in {"request_service_qr", "request_individual_configs"}:','if name in {"request_service_qr"}:')
    yield mutate('wrong_marker',PRED,PRED.replace('== "composite"','== "other"'))
    yield mutate('no_reason','"reason": "composite_unsupported"','"reason": "unavailable"')
    yield mutate('reject_missing',PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"')
    yield mutate('reject_explicit_legacy',PRED,'"service_kind" in record.keys()')
    yield mutate('scan_unrelated','[o for o in orders if o["config_id"] == cfg["id"] and o["status"] == "approved"]','list(orders)')
    yield mutate('leak_response',REFUSAL,REFUSAL[:-1]+', "link": cfg["link"]}')
    yield mutate('leak_log',REFUSAL,'                    _log.warning("%s", cfg["link"])\n'+REFUSAL)
    yield mutate('fetch_before_refusal',REFUSAL,'                    await fetch_sub_info(cfg["link"])\n'+REFUSAL)
    yield mutate('provider_before_refusal',REFUSAL,'                    get_provider({})\n'+REFUSAL)
    yield mutate('write_before_refusal',REFUSAL,'                    db.set_setting("bad_guard_write", "1")\n'+REFUSAL)
    yield mutate('wrong_requester','db.get_user_orders(user_tg_id)','db.get_user_orders(5101)','_resolve_service_target')
    yield mutate('preflight_wrong_requester','_resolve_service_target(db, user_tg_id, args.get("service_id"))','_resolve_service_target(db, 5101, args.get("service_id"))')
    yield mutate('ignore_disabled','if not cfg or (("is_disabled" in cfg.keys()) and cfg["is_disabled"]):','if not cfg:','_resolve_service_target')
    yield mutate('ignore_approved','o["config_id"] == target_id and o["status"] == "approved"','o["config_id"] == target_id','_resolve_service_target')
    for tool in ['request_service_qr','request_individual_configs']:
        yield mutate('wrong_id_'+tool,'"service_id": service_id','"service_id": "c999"','_tool_'+tool)
    yield mutate('qr_accept_empty','if not link:','if link is None:','_tool_request_service_qr')
    yield mutate('qr_reject_native','if not link:','if not link or not str(link).startswith("https://"):','_tool_request_service_qr')
    yield mutate('individual_accept_native','if not link or not str(link).startswith(("http://", "https://")):','if not link:','_tool_request_individual_configs')


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
    with tempfile.TemporaryDirectory(prefix='t050s-review-') as directory:
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
    (HERE/'evidence.md').write_text('# T050s reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference resolves real owned stock targets, checks config and matching approved-order metadata before unchanged retrieval shortcuts; no production implementation claim.\n')


if __name__ == '__main__':
    main()
