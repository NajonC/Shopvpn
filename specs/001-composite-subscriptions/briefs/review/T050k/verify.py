"""T050k relevant owned retrieval metadata, guarded before auth writes in scratch."""
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
SOURCE='miniapp/server.py';PACKET='tests/integration/test_composite_miniapp_renewal_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py','tests/characterization/test_legacy_renewal_reminders.py']
ENDPOINTS=['api_custom_config_renewal_full_plans','api_custom_config_renew_full']
REASON='Composite Mini App renewal is unsupported'
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD='    operation = getattr(request.scope.get("endpoint"), "__name__", "")\n    if operation in {\'api_custom_config_renewal_full_plans\', \'api_custom_config_renew_full\'}:\n        db = tenant.db\n        user_id = tg_user["id"]\n        try:\n            custom_id = int(request.path_params.get("custom_config_id"))\n        except (ValueError, TypeError):\n            custom_id = None\n        custom = db.get_custom_config_owned(custom_id, user_id) if custom_id is not None else None\n        records = [custom] if custom else []\n        if custom and custom["order_id"]:\n            order = db.get_order(custom["order_id"])\n            if order and order["user_id"] == user_id:\n                records.append(order)\n                product = db.get_product(order["product_id"])\n                if product is not None:\n                    records.append(product)\n        if operation == "api_custom_config_renewal_full_plans" and custom:\n            records.extend(p for p in db.get_all_products() if p["is_active"] and p["is_auto_provision"] and p["provision_server_id"] == custom["panel_server_id"])\n        elif operation == "api_custom_config_renew_full":\n            body = await request.json()\n            records.append(body)\n            selected = db.get_product(body.get("product_id"))\n            if selected is not None:\n                records.append(selected)\n        for record in records:\n            if "service_kind" in record.keys() and record["service_kind"] == "composite":\n                raise HTTPException(403, "Composite Mini App renewal is unsupported")\n'


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
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,'renewal_engine.py',*TESTS]}
    results=[]
    with tempfile.TemporaryDirectory(prefix='t050k-review-') as directory:
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
                    assert c.get('classname')=='tests.integration.test_composite_miniapp_renewal_guards',c.attrib
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
        mutate('omit_custom',lambda s:once(s,'records = [custom] if custom else []','records = []'))
        mutate('omit_parent_order',lambda s:once(s,'                records.append(order)','                pass'))
        mutate('omit_parent_product',lambda s:once(s,'                    records.append(product)','                    pass'))
        mutate('omit_plan_products',lambda s:once(s,'            records.extend(p for p in db.get_all_products() if p["is_active"] and p["is_auto_provision"] and p["provision_server_id"] == custom["panel_server_id"])','            pass'))
        mutate('omit_selected',lambda s:once(s,'                records.append(selected)','                pass'))
        mutate('omit_request',lambda s:once(s,'            records.append(body)','            pass'))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"'))
        mutate('no_reason',lambda s:once(s,REASON,'Unsupported renewal'))
        mutate('leak_link',lambda s:once(s,'"'+REASON+'"','"'+REASON+' " + custom["subscription_url"]'))
        mutate('late_auth',lambda s:once(once(s,GUARD,''),'    return tg_user["id"], tenant.db, tenant',GUARD+'    return tg_user["id"], tenant.db, tenant'))
        refusal='                raise HTTPException(403, "'+REASON+'")'
        mutate('debit_before_refusal',lambda s:once(s,refusal,'                db.add_wallet_credit(user_id, -1)\n'+refusal))
        mutate('remote_before_refusal',lambda s:once(s,refusal,'                await execute_renewal(db, dict(renewal_target_kind="custom", renewal_target_id=custom["id"], renewal_mode="full", renewal_add_volume_gb=20, renewal_add_days=30, user_id=user_id))\n'+refusal))
        mutate('block_unrelated',lambda s:once(s,' and p["provision_server_id"] == custom["panel_server_id"]',''))
        mutate('wrong_plan_quote',lambda s:once(s,'"price": final_price,','"price": final_price + 1,'),'api_custom_config_renewal_full_plans')
        mutate('wrong_plan_volume',lambda s:once(s,'"volume_gb": p["auto_provision_volume_gb"]','"volume_gb": 0'),'api_custom_config_renewal_full_plans')
        mutate('lost_wallet_debit',lambda s:once(s,'        db.add_wallet_credit(tg_id, -wallet_used)','        pass'),'api_custom_config_renew_full')
        mutate('wrong_checkout_price',lambda s:once(s,'    price = product["price"]','    price = product["price"] + 1'),'api_custom_config_renew_full')
        mutate('wrong_renewal_target',lambda s:once(s,'tg_id, "custom", cc["id"], "full",','tg_id, "custom", cc["id"] + 1, "full",'),'api_custom_config_renew_full')
        mutate('lost_approval',lambda s:once(s,'            db.approve_renewal_order(order_id)','            pass'),'api_custom_config_renew_full')
        engine_path=scratch/'renewal_engine.py'
        engine=engine_path.read_text()
        for name,before,after in (
            ('lost_carryover','preserve_remaining=(mode == "full")','preserve_remaining=False'),
            ('lost_full_reset','reset_usage=(mode == "full")','reset_usage=False'),
            ('wrong_readback','set_volume_gb = usage["data_limit_bytes"] / (1024 ** 3)','set_volume_gb = 20'),
            ('lost_local_renewal','        db.apply_custom_config_renewal(\n            cc["id"], add_volume, add_days, full_reset=(mode == "full"), set_volume_gb=set_volume_gb,\n        )','        pass')
        ):
            engine_path.write_text(once(engine,before,after))
            try:run(name,reference)
            finally:engine_path.write_text(engine)
    (HERE/'evidence.md').write_text('# T050k renewal verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nIndependent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy renewal preserved; unrelated other-panel composites do not block selected legacy plans. Source-only scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
