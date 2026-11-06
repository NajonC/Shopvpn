"""T050d: real bot/web order review in source-only scratch with input guards."""
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
BOT='handlers_admin.py'
WEB='admin_panel/server.py'
PACKET='tests/integration/test_composite_order_review_guards.py'
TESTS=[PACKET,'tests/characterization/test_order_approval.py','tests/characterization/test_wallet_helpers.py']
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
RULES=[(BOT,'cb_order_approve','approve','telegram'),(BOT,'cb_order_reject','reject','telegram'),(WEB,'api_approve_order','approve','web'),(WEB,'api_reject_order','reject','web')]


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def node(source,name):
    found=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.AsyncFunctionDef) and n.name==name]
    assert len(found)==1,name
    return found[0]


def transform(source,name,fn):
    n=node(source,name)
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])


def guard(channel):
    indent='        ' if channel=='telegram' else '    '
    result=('    await call.answer("Composite records cannot use legacy order review", show_alert=True)\n'+indent+'    return\n') if channel=='telegram' else '    raise HTTPException(403, "Composite records cannot use legacy order review")\n'
    return (indent+'dispatch_product = (await asyncio.to_thread(db.get_product, order["product_id"])) if order and order["product_id"] else None\n'
            +indent+'if any(record is not None and '+PRED+' for record in (order, dispatch_product)):\n'
            +indent+result)


def main():
    snap=json.loads((HERE/'snapshot.json').read_text())
    for p,h in snap['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snap['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snap['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [BOT,WEB,*TESTS]}
    records=[]
    with tempfile.TemporaryDirectory(prefix='t050d-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        (scratch/'admin_panel/static').mkdir(parents=True,exist_ok=True)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings; use_synthetic_bot_settings(); from pathlib import Path; import handlers_admin, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (handlers_admin,tests))'],cwd=scratch,env=env,check=True)
        reference={p:(scratch/p).read_text() for p in (BOT,WEB)}
        for path,name,action,channel in RULES:
            n=node(reference[path],name)
            assignments=[a for a in n.body if isinstance(a,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='order' for t in a.targets)]
            assert len(assignments)==1
            lines=reference[path].splitlines(keepends=True)
            index=assignments[0].end_lineno
            reference[path]=''.join(lines[:index])+guard(channel)+''.join(lines[index:])

        def run(name,sources,action=None,channel=None):
            for p,s in sources.items():(scratch/p).write_text(s)
            baseline=action is None
            report=scratch/'result.xml'
            cmd=[sys.executable,'-m','pytest',*(TESTS if baseline else [PACKET]),'--network=deny','-q','--tb=line',f'--junitxml={report}']
            if not baseline:cmd+=['-k',action+' and '+channel]
            proc=subprocess.run(cmd,cwd=scratch,env=env,capture_output=True,text=True,timeout=120)
            tree=ET.parse(report);cases=list(tree.iter('testcase'));failed=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')),proc.stdout+proc.stderr
            if baseline:assert proc.returncode==0 and not failed,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and failed,(name,proc.stdout+proc.stderr)
                for c,f in failed:
                    text=(f.get('message','')+(f.text or '')).lower()
                    assert any(x in text for x in ('assert ','assertionerror')),(name,c.attrib,text)
                    assert c.get('classname')=='tests.integration.test_composite_order_review_guards',c.attrib
            records.append({'mutation':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,records[-1]['disposition'],len(cases),flush=True)

        run('reference',reference)
        for path,name,action,channel in RULES:
            gate=guard(channel)
            def mutate(label,fn):
                sources=dict(reference);sources[path]=transform(sources[path],name,fn);assert sources[path]!=reference[path]
                run(channel+'_'+action+'_'+label,sources,action,channel)
            mutate('omit',lambda s:once(s,gate,''))
            mutate('omit_order',lambda s:once(s,'for record in (order, dispatch_product)','for record in (None, dispatch_product)'))
            mutate('omit_product',lambda s:once(s,'for record in (order, dispatch_product)','for record in (order, None)'))
            mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
            mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
            mutate('reject_absent',lambda s:once(s,PRED,'("service_kind" not in record.keys() or record["service_kind"] == "composite")'))
            mutate('no_reason',lambda s:once(s,'Composite records cannot use legacy order review','Unsupported order'))
            mutate('leak_receipt',lambda s:once(s,'"Composite records cannot use legacy order review"','"Composite records cannot use legacy order review " + order["receipt_file_id"]'))
            def late(s):
                s=once(s,gate,'')
                lines=s.splitlines(keepends=True)
                matches=[i for i,l in enumerate(lines) if ('if order["is_renewal"]:' in l if action=='approve' else 'db.log_admin_action' in l)]
                assert matches
                i=matches[0]
                return ''.join(lines[:i])+gate+''.join(lines[i:])
            mutate('late_effect',late)
    (HERE/'evidence.md').write_text('# T050d reference and mutation evidence\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nAll mutations independent against actual handlers plus scratch-only guards; packet assertions only, no survivors/errors/skips. Synthetic auth and services; scratch auto-cleaned. No production edits.\n')


if __name__=='__main__':main()
