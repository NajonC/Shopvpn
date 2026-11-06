"""T050h Mini App type refusal after real signature validation, before auth writes."""
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
SOURCE='miniapp/server.py'
PACKET='tests/integration/test_composite_miniapp_purchase_invoice_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py']
INVOICES=['api_order_crypto_invoice','api_order_abangateway_invoice','api_order_blupal_invoice','api_order_noapay_invoice','api_order_extra_gateway_invoice','api_order_custom_gateway_invoice','api_order_card_auto_invoice']
ENDPOINTS=['api_create_order',*INVOICES]
EXTRA=['zarinpal','aqayepardakht','tetra98','cubepay','nowpayments','tgstars']
REASON='Composite Mini App operation is unsupported'
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
GUARD=('    operation = getattr(request.scope.get("endpoint"), "__name__", "")\n'
       '    if operation in {\n'+''.join('        '+repr(n)+',\n' for n in ENDPOINTS)+'    }:\n'
       '        payload = await request.json() if operation == "api_create_order" else {}\n'
       '        if not isinstance(payload, dict):\n            payload = {}\n'
       '        dispatch_order = None\n'
       '        if operation != "api_create_order":\n'
       '            try:\n                dispatch_order_id = int(request.path_params.get("order_id", ""))\n'
       '            except (ValueError, TypeError):\n                dispatch_order_id = None\n'
       '            dispatch_order = tenant.db.get_order(dispatch_order_id) if dispatch_order_id is not None else None\n'
       '            if dispatch_order and dispatch_order["user_id"] != tg_user["id"]:\n                dispatch_order = None\n'
       '        dispatch_product_id = payload.get("product_id") if operation == "api_create_order" else (dispatch_order["product_id"] if dispatch_order else None)\n'
       '        dispatch_product = tenant.db.get_product(dispatch_product_id) if dispatch_product_id else None\n'
       '        for record in (dispatch_order, dispatch_product):\n'
       f'            if record is not None and {PRED}:\n'
       f'                raise HTTPException(403, "{REASON}")\n'
       '        if payload.get("service_kind") == "composite":\n'
       f'            raise HTTPException(403, "{REASON}")\n')


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.FunctionDef)) and n.name==name]
    assert len(nodes)==1,name
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])


def main():
    snap=json.loads((HERE/'snapshot.json').read_text())
    for p,h in snap['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snap['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snap['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,*TESTS]}
    records=[]
    with tempfile.TemporaryDirectory(prefix='t050h-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        for rel in ('admin_panel/static','miniapp/static'):(scratch/rel).mkdir(parents=True,exist_ok=True)
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
                    assert c.get('classname')=='tests.integration.test_composite_miniapp_purchase_invoice_guards',c.attrib
            records.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,records[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        def mutate(name,fn,func='get_verified_user'):
            source=change(reference,func,fn);assert source!=reference
            run(name,source)
        mutate('omit_guard',lambda s:once(s,GUARD,''))
        mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
        mutate('omit_request_marker',lambda s:once(s,'        if payload.get("service_kind") == "composite":','        if False:'))
        mutate('omit_order',lambda s:once(s,'for record in (dispatch_order, dispatch_product):','for record in (None, dispatch_product):'))
        mutate('omit_product',lambda s:once(s,'for record in (dispatch_order, dispatch_product):','for record in (dispatch_order, None):'))
        for name in ENDPOINTS:
            mutate('bypass_'+name,lambda s,name=name:once(s,'        '+repr(name)+',\n',''))
        for gateway in EXTRA:
            mutate('bypass_extra_'+gateway,lambda s,gateway=gateway:once(s,'    }:\n','    } and request.path_params.get("gateway") != '+repr(gateway)+':\n'))
        mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
        mutate('reject_absent',lambda s:once(s,PRED,'("service_kind" not in record.keys() or record["service_kind"] == "composite")'))
        def no_reason(s):
            assert s.count(REASON)==2
            return s.replace(REASON,'Unsupported operation')
        mutate('no_explicit_reason',no_reason)
        def leak(s):
            assert s.count('"'+REASON+'"')==2
            return s.replace('"'+REASON+'"','"'+REASON+' " + (dispatch_product["name"] if dispatch_product else "")')
        mutate('leak_product_name',leak)
        mutate('late_after_auth_write',lambda s:once(once(s,GUARD,''),'    return tg_user["id"], tenant.db, tenant',GUARD+'    return tg_user["id"], tenant.db, tenant'))
        for name in INVOICES:
            def wrong_amount(s):
                assert s.count('order["final_price"]')>=2
                return s.replace('order["final_price"]','(order["final_price"] + 1)')
            mutate('wrong_amount_'+name,wrong_amount,name)
        mutate('lost_checkout_wallet_debit',lambda s:once(s,'    wallet_used = min(wallet_credit, price_after_code)','    wallet_used = 0'),'api_create_order')
    (HERE/'evidence.md').write_text('# T050h checkout/invoice verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nIndependent mutants against actual signed-auth/route code plus scratch-only early guard. Relevant packet assertions only; no survivors/errors/skips. Existing legacy auth sequence write preserved; rejected composites leave full DB unchanged. Scratch auto-cleaned; no production edits/payment-provider acceptance claim.\n')


if __name__=='__main__':main()
