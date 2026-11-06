"""T050c executable scratch reference and independent dispatch/publication mutants."""
from pathlib import Path
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
DIRECT='direct_panel_provision.py'
DELIVERY='config_delivery.py'
DT='tests/integration/test_composite_direct_guards.py'
LT='tests/integration/test_composite_delivery_guards.py'
TESTS=[DT,LT,'tests/characterization/test_direct_provision.py','tests/characterization/test_buy_start.py','tests/characterization/test_order_approval.py']
PRED='"service_kind" in record.keys() and record["service_kind"] == "composite"'
DG=('    dispatch_order = db.get_order(order_id) if order_id is not None else None\n'
    '    for record in (product, dispatch_order):\n'
    f'        if record is not None and {PRED}:\n'
    '            raise ProvisionError("Composite records cannot use legacy direct provisioning")\n')
LG=('    dispatch_order = db.get_order(order_id) if db is not None and order_id is not None else None\n'
    '    dispatch_product = db.get_product(dispatch_order["product_id"]) if dispatch_order is not None and dispatch_order["product_id"] else None\n'
    '    for record in (dispatch_order, dispatch_product):\n'
    f'        if record is not None and {PRED}:\n'
    '            raise ValueError("Composite records cannot use legacy delivery")\n')


def replace_once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def main():
    snap=json.loads((HERE/'snapshot.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in snap['hashes'].items())
    assert subprocess.check_output(['git','diff','--cached'],cwd=ROOT).decode()==snap['staged']
    assert subprocess.check_output(['git','diff'],cwd=ROOT).decode()==snap['unstaged']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [DIRECT,DELIVERY,*TESTS]}
    results=[]
    with tempfile.TemporaryDirectory(prefix='t050c-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+TESTS
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):
                continue
            dest=scratch/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/rel,dest)
        (scratch/'admin_panel/static').mkdir(parents=True,exist_ok=True)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from pathlib import Path; import direct_panel_provision,config_delivery,tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (direct_panel_provision,config_delivery,tests))'],cwd=scratch,env=env,check=True)
        reference={p:(scratch/p).read_text() for p in (DIRECT,DELIVERY)}
        reference[DIRECT]=replace_once(reference[DIRECT],'    server_id = product["provision_server_id"]',DG+'    server_id = product["provision_server_id"]')
        reference[DELIVERY]=replace_once(reference[DELIVERY],'    if isinstance(links, str):',LG+'    if isinstance(links, str):')

        def run(name,sources,path=None):
            for p,s in sources.items(): (scratch/p).write_text(s)
            baseline=path is None
            selected=TESTS if baseline else ([DT] if path==DIRECT else [LT])
            report=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*selected,'--network=deny','-q','--tb=line',f'--junitxml={report}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=120)
            tree=ET.parse(report); cases=list(tree.iter('testcase'))
            failed=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')),proc.stdout+proc.stderr
            if baseline:
                assert proc.returncode==0 and not failed,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and failed,(name,proc.stdout+proc.stderr)
                for c,f in failed:
                    text=(f.get('message','')+(f.text or '')).lower()
                    expected_error=(name.endswith(('reject_legacy','reject_absent','reject_nodb'))
                        and c.get('name','').startswith('test_legacy_')
                        and (text.startswith('direct_panel_provision.provisionerror: composite records cannot use legacy direct provisioning') if path==DIRECT else text.startswith('valueerror: composite records cannot use legacy delivery')))
                    assert any(x in text for x in ('assert ','assertionerror','did not raise')) or expected_error,(name,c.attrib,text)
                    assert c.get('classname','').startswith('tests.integration.test_composite_'),c.attrib
            results.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,results[-1]['disposition'],len(cases),flush=True)

        run('reference',reference)
        for path,gate,label in [(DIRECT,DG,'direct'),(DELIVERY,LG,'delivery')]:
            def mutate(name,transform):
                sources=dict(reference);sources[path]=transform(sources[path]);assert sources[path]!=reference[path],name
                run(label+'_'+name,sources,path)
            mutate('omit',lambda s:replace_once(s,gate,''))
            if path==DIRECT:
                mutate('omit_product',lambda s:replace_once(s,'for record in (product, dispatch_order):','for record in (None, dispatch_order):'))
                mutate('omit_order',lambda s:replace_once(s,'for record in (product, dispatch_order):','for record in (product, None):'))
                reason='Composite records cannot use legacy direct provisioning'
            else:
                mutate('omit_product',lambda s:replace_once(s,'for record in (dispatch_order, dispatch_product):','for record in (dispatch_order, None):'))
                mutate('omit_order',lambda s:replace_once(s,'for record in (dispatch_order, dispatch_product):','for record in (None, dispatch_product):'))
                reason='Composite records cannot use legacy delivery'
            mutate('wrong_kind',lambda s:replace_once(s,PRED,PRED.replace('== "composite"','== "other"')))
            mutate('no_reason',lambda s:replace_once(s,reason,'Unsupported record'))
            field='product["name"]' if path==DIRECT else 'links if isinstance(links, str) else str(links)'
            mutate('leak_secret',lambda s:replace_once(s,'"'+reason+'"','"'+reason+' " + '+field))
            mutate('reject_legacy',lambda s:replace_once(s,PRED,'"service_kind" in record.keys()'))
            mutate('reject_absent',lambda s:replace_once(s,PRED,'("service_kind" not in record.keys() or record["service_kind"] == "composite")'))
            if path==DIRECT:
                # Factory selection itself must not happen for a rejected record.
                anchor='    prefix = db.get_custom_config_prefix()'
                mutate('late_factory',lambda s:replace_once(replace_once(s,gate,''),anchor,gate+anchor))
                mutate('late_provision',lambda s:replace_once(replace_once(s,gate,''),'    return built',gate+'    return built'))
            else:
                indented='\n'.join('    '+line if line else line for line in gate.split('\n'))
                mutate('late_publication',lambda s:replace_once(replace_once(s,gate,''),'        if sub_link_on:',indented+'        if sub_link_on:'))
                mutate('reject_nodb',lambda s:replace_once(s,gate,'    if db is None:\n        raise ValueError("Composite records cannot use legacy delivery")\n'+gate))
    (HERE/'evidence.md').write_text('# T050c reference and mutation evidence\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nIndependent mutations against passing reference; relevant assertions or exact deliberate over-strict exceptions in positive controls only. No survivors/errors/skips. Scratch auto-cleaned; no production code changed.\n')


if __name__=='__main__': main()
