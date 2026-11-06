"""T050l relevant owned retrieval metadata, guarded before auth writes in scratch."""
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
SOURCE='miniapp/server.py';PACKET='tests/integration/test_composite_miniapp_trial_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py','tests/characterization/test_free_test_flow.py']
ENDPOINTS=['api_test_config_status','api_test_config_claim']
REASON='Composite Mini App trial is unsupported'
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD='    operation = getattr(request.scope.get("endpoint"), "__name__", "")\n    if operation in {\'api_test_config_status\', \'api_test_config_claim\'}:\n        db = tenant.db\n        user_id = tg_user["id"]\n        plans = list(db.get_test_config_plans(active_only=True))\n        records = []\n        if operation == "api_test_config_status":\n            records.extend(plans)\n            user = db.get_user(user_id)\n            if user and user["test_used"] >= MAX_TEST_PER_USER:\n                custom = db.get_test_custom_config_for_user(user_id)\n                if custom:\n                    records.append(custom)\n                else:\n                    stock = db.get_assigned_test_config(user_id)\n                    if stock:\n                        records.append(stock)\n        else:\n            body = await request.json()\n            records.append(body)\n            if body.get("plan_id") is not None:\n                records.extend(p for p in plans if p["id"] == body["plan_id"])\n            elif len(plans) == 1:\n                records.extend(plans)\n        for record in records:\n            if "service_kind" in record.keys() and record["service_kind"] == "composite":\n                raise HTTPException(403, "Composite Mini App trial is unsupported")\n'


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    found=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(found)==1
    n=found[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])


def main():
    snap=json.loads((HERE/'snapshot.json').read_text())
    for p,h in snap['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snap['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snap['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,'test_config_provision.py',*TESTS]}
    results=[]
    with tempfile.TemporaryDirectory(prefix='t050l-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        for rel in ('miniapp/static','admin_panel/static'):(scratch/rel).mkdir(parents=True,exist_ok=True)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();from pathlib import Path;import tests;assert Path(tests.__file__).is_relative_to(Path.cwd())'],cwd=scratch,env=env,check=True)
        reference=(scratch/SOURCE).read_text()
        reference=once(reference,'def get_verified_user(x_init_data: str = Header(...), tenant: Tenant = Depends(get_tenant)):', 'async def get_verified_user(request: Request, x_init_data: str = Header(...), tenant: Tenant = Depends(get_tenant)):')
        reference=change(reference,'get_verified_user',lambda s:once(s,'    tg_user = result["user"]\n','    tg_user = result["user"]\n'+GUARD))

        def run(name,source,baseline=False):
            ast.parse(source)
            (scratch/SOURCE).write_text(source)
            report=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*(TESTS if baseline else [PACKET]),'--network=deny','-q','--tb=line',f'--junitxml={report}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=120)
            t=ET.parse(report);cases=list(t.iter('testcase'));failed=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(t.iter('error')) and not list(t.iter('skipped')),proc.stdout+proc.stderr
            if baseline:assert proc.returncode==0 and not failed,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and failed,(name,proc.stdout+proc.stderr)
                for c,f in failed:
                    text=(f.get('message','')+(f.text or '')).lower()
                    assert any(x in text for x in ('assert ','assertionerror')),(name,c.attrib,text)
                    assert c.get('classname')=='tests.integration.test_composite_miniapp_trial_guards',c.attrib
            results.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,results[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        def mutate(name,fn,func='get_verified_user'):
            s=change(reference,func,fn);assert s!=reference
            run(name,s)
        mutate('omit',lambda s:once(s,GUARD,''))
        mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
        for endpoint in ENDPOINTS:
            mutate('bypass_'+endpoint,lambda s,endpoint=endpoint:once(s,repr(endpoint),repr('unused_'+endpoint)))
        mutate('omit_status_plans',lambda s:once(s,'\n            records.extend(plans)\n','\n            pass\n'))
        mutate('omit_status_custom',lambda s:once(s,'                    records.append(custom)','                    pass'))
        mutate('omit_status_stock',lambda s:once(s,'                        records.append(stock)','                        pass'))
        mutate('omit_explicit_plan',lambda s:once(s,'                records.extend(p for p in plans if p["id"] == body["plan_id"])','                pass'))
        mutate('omit_implicit_plan',lambda s:once(s,'                records.extend(plans)','                pass'))
        mutate('omit_request',lambda s:once(s,'            records.append(body)','            pass'))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"'))
        mutate('no_reason',lambda s:once(s,REASON,'Unsupported trial'))
        mutate('leak_link',lambda s:once(s,REASON,REASON+' https://sub.example.invalid/SECRET-TRIAL-LINK'))
        mutate('late_auth',lambda s:once(once(s,GUARD,''),'    return tg_user["id"], tenant.db, tenant',GUARD+'    return tg_user["id"], tenant.db, tenant'))
        refusal='                raise HTTPException(403, "'+REASON+'")'
        mutate('reserve_before_refusal',lambda s:once(s,refusal,'                db.try_reserve_test_slot(user_id, MAX_TEST_PER_USER)\n'+refusal))
        mutate('remote_before_refusal',lambda s:once(s,refusal,'                if plans:\n                    await provision_test_plan(db, plans[0], user_id=user_id)\n'+refusal))
        mutate('block_unrelated',lambda s:once(s,'                records.extend(p for p in plans if p["id"] == body["plan_id"])','                records.extend(plans)'))
        mutate('wrong_used',lambda s:once(s,'"used": used','"used": not used'),'api_test_config_status')
        mutate('lost_status_link',lambda s:once(s,'"link": link','"link": None'),'api_test_config_status')
        mutate('wrong_status_label',lambda s:once(s,'"amount_label": format_plan_amount(p)','"amount_label": "wrong"'),'api_test_config_status')
        mutate('lost_plan_reservation',lambda s:once(s,'        if not db.try_reserve_test_slot(tg_id, MAX_TEST_PER_USER):','        if False:'),'api_test_config_claim')
        mutate('lost_stock_reservation',lambda s:once(s,'\n    if not db.try_reserve_test_slot(tg_id, MAX_TEST_PER_USER):\n','\n    if False:\n'),'api_test_config_claim')
        mutate('lost_stock_assignment',lambda s:once(s,'    result = db.take_unused_test_config(tg_id)','    result = {"link": "https://sub.example.invalid/SECRET-TRIAL-LINK"}'),'api_test_config_claim')
        provision_path=scratch/'test_config_provision.py'
        provision=provision_path.read_text()
        for name,before,after in (
            ('wrong_volume_unit','volume_gb = plan["volume_mb"] / 1024.0','volume_gb = plan["volume_mb"] / 1000.0'),
            ('wrong_duration_unit','duration_days = plan["duration_hours"] / 24.0','duration_days = plan["duration_hours"] / 12.0'),
            ('wrong_claimant','            user_id, server["id"], username, volume_gb, duration_days,','            9001, server["id"], username, volume_gb, duration_days,'),
            ('lost_local_record','        db.add_custom_config(\n            user_id, server["id"], username, volume_gb, duration_days,\n            result.subscription_url, source="test", product_id=plan["id"],\n        )','        pass'),
        ):
            altered=once(provision,before,after);ast.parse(altered)
            provision_path.write_text(altered)
            try:run(name,reference)
            finally:provision_path.write_text(provision)
    (HERE/'evidence.md').write_text('# T050l trial verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nIndependent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy trial selection/allowance/provision/exports preserved; unselected composite plan does not block explicit legacy claim. Source-only scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
