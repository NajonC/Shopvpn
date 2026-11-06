"""T050i relevant owned retrieval metadata, guarded before auth writes in scratch."""
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
SOURCE='miniapp/server.py';PACKET='tests/integration/test_composite_miniapp_retrieval_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py']
ENDPOINTS=['api_orders','api_custom_configs','api_sub_info','api_expiring','api_card_auto_invoice_status','api_custom_config_history']
REASON='Composite Mini App retrieval is unsupported'
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD=('    operation = getattr(request.scope.get("endpoint"), "__name__", "")\n'
       '    if operation in {\n'+''.join('        '+repr(n)+',\n' for n in ENDPOINTS)+'    }:\n'
       '        db = tenant.db\n        user_id = tg_user["id"]\n'
       '        orders, customs, rows = [], [], []\n'
       '        if operation == "api_orders":\n            orders = list(db.get_user_orders(user_id))\n'
       '        elif operation == "api_custom_configs":\n            customs = list(db.get_custom_configs_for_user(user_id))\n'
       '        elif operation in {"api_sub_info", "api_expiring"}:\n'
       '            all_orders = list(db.get_user_orders(user_id))\n'
       '            all_customs = list(db.get_custom_configs_for_user(user_id))\n'
       '            if operation == "api_sub_info":\n'
       '                link = request.query_params.get("link")\n'
       '                customs = [c for c in all_customs if c["subscription_url"] == link]\n'
       '                for order in all_orders:\n'
       '                    configs = db.get_order_configs(order["id"]) if order["status"] == "approved" else []\n'
       '                    if not configs and order["config_id"]:\n'
       '                        config = db.get_config_by_id(order["config_id"])\n'
       '                        configs = [config] if config else []\n'
       '                    if any(c["link"] == link for c in configs):\n                        orders.append(order)\n'
       '            else:\n'
       '                rows = list(db.get_expiring_configs_for_user(user_id))\n'
       '                customs = [c for c in all_customs if any(r["product_id"] is None and r["config_id"] == c["id"] and r["link"] == c["subscription_url"] for r in rows)]\n'
       '                for order in all_orders:\n'
       '                    configs = db.get_order_configs(order["id"]) if order["status"] == "approved" else []\n'
       '                    if not configs and order["config_id"]:\n'
       '                        config = db.get_config_by_id(order["config_id"])\n'
       '                        configs = [config] if config else []\n'
       '                    if any(r["product_id"] is not None and r["config_id"] == c["id"] and r["link"] == c["link"] for r in rows for c in configs):\n                        orders.append(order)\n'
       '        elif operation == "api_custom_config_history":\n'
       '            raw_id = request.path_params.get("custom_config_id")\n'
       '            try:\n                custom_id = int(raw_id)\n'
       '            except (ValueError, TypeError):\n                custom_id = None\n'
       '            custom = db.get_custom_config_owned(custom_id, user_id) if custom_id is not None else None\n'
       '            customs = [custom] if custom else []\n'
       '        elif operation == "api_card_auto_invoice_status":\n'
       '            try:\n                invoice_id = int(request.path_params.get("invoice_id"))\n'
       '            except (ValueError, TypeError):\n                invoice_id = None\n'
       '            invoice = db.get_card_to_card_invoice(invoice_id) if invoice_id is not None else None\n'
       '            if invoice and invoice["user_id"] == user_id and invoice["kind"] == "order":\n'
       '                order = db.get_order(invoice["ref_id"])\n'
       '                if order and order["user_id"] == user_id:\n                    orders.append(order)\n'
       '        for custom in customs:\n'
       '            if custom["order_id"]:\n'
       '                parent = db.get_order(custom["order_id"])\n'
       '                if parent and parent["user_id"] == user_id:\n                    orders.append(parent)\n'
       '        records = [*orders, *customs, *rows]\n'
       '        product_ids = [o["product_id"] for o in orders if o["product_id"]] + [r["product_id"] for r in rows if r["product_id"]]\n'
       '        for product_id in product_ids:\n'
       '            product = db.get_product(product_id)\n'
       '            if product is not None:\n                records.append(product)\n'
       '        for record in records:\n'
       f'            if {PRED}:\n'
       f'                raise HTTPException(403, "{REASON}")\n')


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
    with tempfile.TemporaryDirectory(prefix='t050i-review-') as directory:
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
                    assert c.get('classname')=='tests.integration.test_composite_miniapp_retrieval_guards',c.attrib
            results.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,results[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        def mutate(name,fn,func='get_verified_user'):
            s=change(reference,func,fn);assert s!=reference
            run(name,s)
        mutate('omit',lambda s:once(s,GUARD,''))
        mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
        for endpoint in ENDPOINTS:mutate('bypass_'+endpoint,lambda s,endpoint=endpoint:once(s,'        '+repr(endpoint)+',\n',''))
        for category in ('orders','customs','rows'):
            mutate('omit_'+category,lambda s,category=category:once(s,'        records = [*orders, *customs, *rows]','        records = ['+', '.join('*'+c for c in ('orders','customs','rows') if c!=category)+']'))
        mutate('omit_products',lambda s:once(s,'                records.append(product)','                pass'))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'"service_kind" not in record.keys() or record["service_kind"] == "composite"'))
        mutate('no_reason',lambda s:once(s,REASON,'Unsupported retrieval'))
        leak='"'+REASON+' " + next((str(r[k]) for r in records for k in ("subscription_url", "link", "name") if k in r.keys()), "")'
        mutate('leak_link_or_name',lambda s:once(s,'"'+REASON+'"',leak))
        mutate('late_auth',lambda s:once(once(s,GUARD,''),'    return tg_user["id"], tenant.db, tenant',GUARD+'    return tg_user["id"], tenant.db, tenant'))
        refusal='                raise HTTPException(403, "'+REASON+'")'
        mutate('fetch_before_refusal',lambda s:once(s,refusal,'                await fetch_sub_info("https://sub.example.invalid/mutant")\n'+refusal))
        mutate('block_unrelated_sub_info',lambda s:once(s,'                customs = [c for c in all_customs if c["subscription_url"] == link]','                customs = all_customs'))
        mutate('block_unrelated_expiry',lambda s:once(s,'                customs = [c for c in all_customs if any(r["product_id"] is None and r["config_id"] == c["id"] and r["link"] == c["subscription_url"] for r in rows)]','                customs = all_customs'))
        mutate('wrong_order_link',lambda s:once(s,'"link": (None if cfg_disabled else (cfg["link"] if cfg else None)),','"link": None,'),'api_orders')
        mutate('wrong_custom_link',lambda s:once(s,'"subscription_url": c["subscription_url"]','"subscription_url": ""'),'api_custom_configs')
        mutate('wrong_sub_info',lambda s:once(s,'    return info','    return {"wrong": True}'),'api_sub_info')
        mutate('lost_expiring',lambda s:once(s,'    return result','    return []'),'api_expiring')
        mutate('lost_history',lambda s:once(s,'    return [','    return []\n    unused = ['),'api_custom_config_history')
        mutate('wrong_invoice_amount',lambda s:once(s,'"amount_toman": invoice["amount_toman"]','"amount_toman": invoice["amount_toman"] + 1'),'api_card_auto_invoice_status')
    (HERE/'evidence.md').write_text('# T050i retrieval verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nIndependent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy exports preserved; unrelated composites do not block requested legacy sub/expiry. Source-only scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
