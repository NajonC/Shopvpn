"""T050m relevant owned retrieval metadata, guarded before auth writes in scratch."""
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
SOURCE='miniapp/server.py';PACKET='tests/integration/test_composite_miniapp_custom_receipt_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py','tests/characterization/test_receipt_linkage.py']
ENDPOINTS=['api_create_custom_config','api_order_receipt']
REASON='Composite Mini App checkout/receipt is unsupported'
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD='    operation = getattr(request.scope.get("endpoint"), "__name__", "")\n    if operation in {\'api_create_custom_config\', \'api_order_receipt\'}:\n        db = tenant.db\n        user_id = tg_user["id"]\n        records = []\n        if operation == "api_create_custom_config":\n            body = await request.json()\n            records.append(body)\n        else:\n            try:\n                order_id = int(request.path_params.get("order_id"))\n            except (ValueError, TypeError):\n                order_id = None\n            order = db.get_order(order_id) if order_id is not None else None\n            if order and order["user_id"] == user_id:\n                records.append(order)\n                if order["product_id"]:\n                    product = db.get_product(order["product_id"])\n                    if product is not None:\n                        records.append(product)\n        for record in records:\n            if "service_kind" in record.keys() and record["service_kind"] == "composite":\n                raise HTTPException(403, "Composite Mini App checkout/receipt is unsupported")\n'


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
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,*TESTS]}
    results=[]
    with tempfile.TemporaryDirectory(prefix='t050m-review-') as directory:
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
        reference=change(reference,'api_order_receipt',lambda s:once(once(s,'    order_id: int,\n','    request: Request,\n    order_id: int,\n'),'    tg_id, db, tenant = get_verified_user(x_init_data, tenant)','    tg_id, db, tenant = await get_verified_user(request, x_init_data, tenant)'))

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
                    assert c.get('classname')=='tests.integration.test_composite_miniapp_custom_receipt_guards',c.attrib
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
        mutate('omit_request',lambda s:once(s,'            records.append(body)','            pass'))
        mutate('omit_order',lambda s:once(s,'                records.append(order)','                pass'))
        mutate('omit_product',lambda s:once(s,'                        records.append(product)','                        pass'))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"'))
        mutate('no_reason',lambda s:once(s,REASON,'Unsupported checkout/receipt'))
        mutate('leak_link',lambda s:once(s,REASON,REASON+' https://sub.example.invalid/SECRET-CUSTOM-LINK'))
        mutate('late_auth',lambda s:once(once(s,GUARD,''),'    return tg_user["id"], tenant.db, tenant',GUARD+'    return tg_user["id"], tenant.db, tenant'))
        refusal='                raise HTTPException(403, "'+REASON+'")'
        mutate('debit_before_refusal',lambda s:once(s,refusal,'                db.add_wallet_credit(user_id, -1)\n'+refusal))
        mutate('provider_before_refusal',lambda s:once(s,refusal,'                get_provider(db.get_panel_server_for_usage("custom_config"))\n'+refusal))
        mutate('admin_delivery_before_refusal',lambda s:once(s,refusal,'                await send_photo_to_admins(db, tenant.bot_token, "unsafe", "{}", b"x", "receipt.jpg", "image/jpeg")\n'+refusal))
        mutate('wrong_purchase_price',lambda s:once(s,'    price = db.calc_custom_config_price(body.volume_gb)','    price = db.calc_custom_config_price(body.volume_gb) + 1'),'api_create_custom_config')
        mutate('lost_wallet_debit',lambda s:once(s,'        db.add_wallet_credit(tg_id, -wallet_used)','        pass'),'api_create_custom_config')
        mutate('lost_purchase_approval',lambda s:once(s,'            db.approve_custom_config_order(order_id)','            pass'),'api_create_custom_config')
        mutate('lost_local_record',lambda s:once(s,'\n            db.add_custom_config(\n                tg_id, server["id"], result.username, body.volume_gb, settings["duration_days"],','\n            (lambda *args, **kwargs: None)(\n                tg_id, server["id"], result.username, body.volume_gb, settings["duration_days"],'),'api_create_custom_config')
        mutate('wrong_purchase_link',lambda s:once(s,'return {"status": "approved", "order_id": order_id, "link": result.subscription_url}','return {"status": "approved", "order_id": order_id, "link": "wrong"}'),'api_create_custom_config')
        mutate('wrong_provider_duration',lambda s:once(s,'provider.create_user(username, body.volume_gb, settings["duration_days"])','provider.create_user(username, body.volume_gb, 1)'),'api_create_custom_config')
        mutate('lost_receipt_file',lambda s:once(s,'        db.set_order_receipt(order_id, sent_file_id)','        pass'),'api_order_receipt')
        mutate('lost_admin_message',lambda s:once(s,'        db.set_order_admin_message(order_id, admin_id, message_id)','        pass'),'api_order_receipt')
        mutate('wrong_approve_callback',lambda s:once(s,'f"order_approve:{order_id}"','f"order_approve:{order_id + 1}"'),'api_order_receipt')
        mutate('wrong_payable_caption',lambda s:once(s,"{order['final_price']:,}","{0:,}"),'api_order_receipt')
    (HERE/'evidence.md').write_text('# T050m custom checkout/receipt verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nIndependent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy custom checkout and receipt storage/delivery preserved. Source-only scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
