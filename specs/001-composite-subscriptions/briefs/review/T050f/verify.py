"""T050f custom-service AI shortcut reference and independent mutants in scratch."""
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

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE='ai_support.py'
PACKET='tests/integration/test_composite_ai_service_guards.py'
TESTS=[PACKET,'tests/characterization/test_legacy_renewal_reminders.py']
TOOLS=['set_service_auto_renew','get_service_history','request_service_qr','request_individual_configs','request_toggle_service_enabled','request_rename_service','request_regenerate_service_access','request_transfer_service','request_delete_service']
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD=('    if name in {\n'+''.join('        '+repr(t)+',\n' for t in TOOLS)+'    }:\n'
       '        target = await _resolve_service_target(db, user_tg_id, args.get("service_id"))\n'
       '        if target and target["kind"] == "custom":\n'
       '            record = target["custom"]\n'
       f'            if {PRED}:\n'
       '                return {"ok": False, "reason": "composite_unsupported"}\n')


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.AsyncFunctionDef) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])


def main():
    snap=json.loads((HERE/'snapshot.json').read_text())
    for p,h in snap['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snap['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snap['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,*TESTS]}
    records=[]
    with tempfile.TemporaryDirectory(prefix='t050f-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();from pathlib import Path;import ai_support,tests;assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (ai_support,tests))'],cwd=scratch,env=env,check=True)
        reference=change((scratch/SOURCE).read_text(),'_run_tool_uncached',lambda s:once(s,'    if name == "check_account_status":',GUARD+'    if name == "check_account_status":'))

        def run(name,source,baseline=False):
            (scratch/SOURCE).write_text(source)
            report=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*(TESTS if baseline else [PACKET]),'--network=deny','-q','--tb=line',f'--junitxml={report}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=90)
            t=ET.parse(report);cases=list(t.iter('testcase'));failed=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(t.iter('error')) and not list(t.iter('skipped')),proc.stdout+proc.stderr
            if baseline:assert proc.returncode==0 and not failed,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and failed,(name,proc.stdout+proc.stderr)
                for c,f in failed:
                    text=(f.get('message','')+(f.text or '')).lower()
                    assert any(x in text for x in ('assert ','assertionerror')),(name,c.attrib,text)
                    assert c.get('classname')=='tests.integration.test_composite_ai_service_guards',c.attrib
            records.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,records[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        def mutate(name,fn,func='_run_tool_uncached'):
            source=change(reference,func,fn);assert source!=reference
            run(name,source)
        mutate('omit',lambda s:once(s,GUARD,''))
        mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"'))
        mutate('no_explicit_reason',lambda s:once(s,'"reason": "composite_unsupported"','"reason": "service_not_found"'))
        for tool in TOOLS:
            mutate('bypass_'+tool,lambda s,tool=tool:once(s,'        '+repr(tool)+',\n',''))
        refusal='                return {"ok": False, "reason": "composite_unsupported"}'
        mutate('fetch_before_refusal',lambda s:once(s,refusal,'                await fetch_sub_info(record["subscription_url"])\n'+refusal))
        mutate('provider_before_refusal',lambda s:once(s,refusal,'                get_provider(db.get_panel_server(record["panel_server_id"]))\n'+refusal))
        mutate('write_before_refusal',lambda s:once(s,refusal,'                db.set_custom_config_auto_renew(record["id"], user_tg_id, True)\n'+refusal))
        for tool in ('set_service_auto_renew','request_toggle_service_enabled'):
            mutate('wrong_enabled_'+tool,lambda s:once(s,'"enabled": enabled','"enabled": not enabled'),'_tool_'+tool)
        mutate('wrong_name',lambda s:once(s,'"new_name": new_name','"new_name": "wrong_name"'),'_tool_request_rename_service')
        mutate('wrong_target',lambda s:once(s,'"target_telegram_id": target_telegram_id','"target_telegram_id": 999999'),'_tool_request_transfer_service')
        mutate('lost_history',lambda s:once(s,'    rows = await asyncio.to_thread(_read)','    rows = []'),'_tool_get_service_history')
    (HERE/'evidence.md').write_text('# T050f custom-service shortcut verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nAll mutants independent against passing executable reference, relevant packet assertions only. No survivors/errors/skips; scratch auto-cleaned. Custom x-service aliases only; stock c aliases and catalog/financial AI tools remain later T050 work.\n')


if __name__=='__main__':main()
