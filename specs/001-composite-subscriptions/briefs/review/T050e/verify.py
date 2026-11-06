"""T050e source-only reseller provisioning reference and independent mutations."""
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
SOURCE='reseller_auto_provision.py'
PACKET='tests/integration/test_composite_reseller_provision_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py']
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
REASON='Composite record cannot use reseller provisioning'
AUTO='provision_auto_config';PLAN='provision_test_config';FIXED='provision_reseller_fixed_product'
GATES={AUTO:('    dispatch_order = local_db.get_order(order_id) if order_id is not None else None\n'
            '    for record in (product, dispatch_order):\n'),
       PLAN:'    for record in (plan,):\n',FIXED:'    for record in (product,):\n'}
GATES={name:head+'        if record is not None and '+PRED+':\n            raise ProvisionError("'+REASON+'")\n' for name,head in GATES.items()}
ANCHORS={AUTO:'    owner_id = local_db.get_owner_telegram_id()',PLAN:'    volume_gb = plan["volume_mb"] / 1024.0',FIXED:'    if not product or not product["is_active"] or not product["is_auto_provision"]:'}


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.AsyncFunctionDef) and n.name==name]
    assert len(nodes)==1
    n=nodes[0];lines=source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1])+fn(''.join(lines[n.lineno-1:n.end_lineno]))+''.join(lines[n.end_lineno:])


def main():
    snapshot=json.loads((HERE/'snapshot.json').read_text())
    for p,h in snapshot['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snapshot['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snapshot['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,*TESTS]}
    results=[]
    with tempfile.TemporaryDirectory(prefix='t050e-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        (scratch/'admin_panel/static').mkdir(parents=True,exist_ok=True)
        (scratch/'miniapp/static').mkdir(parents=True,exist_ok=True)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();from pathlib import Path;import reseller_auto_provision,tests;assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (reseller_auto_provision,tests))'],cwd=scratch,env=env,check=True)
        reference=(scratch/SOURCE).read_text()
        for name,gate in GATES.items():reference=change(reference,name,lambda s:once(s,ANCHORS[name],gate+ANCHORS[name]))

        def run(name,source,baseline=False):
            (scratch/SOURCE).write_text(source)
            report=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*(TESTS if baseline else [PACKET]),'--network=deny','-q','--tb=line',f'--junitxml={report}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=120)
            t=ET.parse(report);cases=list(t.iter('testcase'));fail=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(t.iter('error')) and not list(t.iter('skipped')),proc.stdout+proc.stderr
            if baseline:assert proc.returncode==0 and not fail,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and fail,(name,proc.stdout+proc.stderr)
                for c,f in fail:
                    text=(f.get('message','')+(f.text or '')).lower()
                    intended_overstrict=(name.endswith(('reject_legacy','reject_absent')) and c.get('name','').startswith('test_legacy_reseller_') and text.startswith('reseller_auto_provision.provisionerror: '+REASON.lower()))
                    assert any(x in text for x in ('assert ','assertionerror','did not raise')) or intended_overstrict,(name,c.attrib,text)
                    assert c.get('classname')=='tests.integration.test_composite_reseller_provision_guards',c.attrib
            results.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in fail]})
            print(name,results[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        for name,gate in GATES.items():
            def mutate(label,fn):
                modified=change(reference,name,fn);assert modified!=reference
                run(name+'_'+label,modified)
            mutate('omit',lambda s:once(s,gate,''))
            mutate('wrong_kind',lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
            mutate('no_reason',lambda s:once(s,REASON,'Unsupported record'))
            data='plan' if name==PLAN else 'product'
            mutate('leak_name',lambda s:once(s,'"'+REASON+'"','"'+REASON+' " + '+data+'["name"]'))
            mutate('reject_legacy',lambda s:once(s,PRED,'"service_kind" in record.keys()'))
            mutate('reject_absent',lambda s:once(s,PRED,'("service_kind" not in record.keys() or record["service_kind"] == "composite")'))
            anchor='    return built[0]' if name==PLAN else '    return built'
            mutate('late_commit',lambda s:once(once(s,gate,''),anchor,gate+anchor))
            if name==AUTO:
                mutate('omit_product',lambda s:once(s,'for record in (product, dispatch_order):','for record in (None, dispatch_order):'))
                mutate('omit_order',lambda s:once(s,'for record in (product, dispatch_order):','for record in (product, None):'))
            if name!=PLAN:
                factory='    provider = get_provider(server)\n'
                mutate('late_factory',lambda s:once(once(s,gate,''),factory,factory+gate))
    (HERE/'evidence.md').write_text('# T050e reference and mutation evidence\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nAll mutants independent; relevant packet assertions or exact deliberate over-strict exceptions only. No survivors/errors/skips. Synthetic source-only scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
