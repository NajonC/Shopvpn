"""Source-only scratch runner; real callback/verifier/SQL, synthetic remote/Telegram."""
from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,sys,tempfile
import xml.etree.ElementTree as ET
from variants_v2 import variants,SOURCES
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PACKET=['tests/integration/test_composite_telegram_inline_stock_alerts.py']
DEPENDENCIES=[]
TESTS=PACKET+['tests/characterization/test_buy_start.py','tests/characterization/test_order_approval.py']

def main():
    inputs={p:(ROOT/p).read_text() for p in SOURCES}
    variants_list=list(variants(*(inputs[p] for p in SOURCES)))
    assert len({x[0] for x in variants_list})==len(variants_list)
    for name,*texts in variants_list:
        for s in texts:ast.parse(s)
        if name!='reference':assert texts!=list(variants_list[0][1:]),name
    if '--preflight' in sys.argv:print('valid transformations',len(variants_list));return
    evidence={'hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES+TESTS+DEPENDENCIES},'records':[]}
    with tempfile.TemporaryDirectory(prefix='T050-inline-stock-review-') as directory:
        scratch=Path(directory)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+PACKET
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            target=scratch/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();import handlers_admin;from pathlib import Path;assert Path(handlers_admin.__file__).is_relative_to(Path.cwd())'],cwd=scratch,env=env,check=True)
        for name,*texts in variants_list:
            for p,s in zip(SOURCES,texts):(scratch/p).write_text(s)
            xml=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*(TESTS if name=='reference' else PACKET),'--network=deny','-q','--tb=line',*(['-k','test_inline_repeat_is_fresh_purchase_not_recovery'] if name in {'ai_guard_overstrict','ai_guard_absent'} else []),*([] if name=='reference' else ['-x']),f'--junitxml={xml}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=1800)
            tree=ET.parse(xml);cases=list(tree.iter('testcase'));failed=[c for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')),(name,proc.stdout,proc.stderr)
            if name=='reference':assert proc.returncode==0 and not failed,(proc.stdout,proc.stderr)
            else:
                assert proc.returncode==1 and failed,(name,proc.stdout,proc.stderr)
                assert all(any(x in c.find('failure').get('message','').lower() for x in ['assert','did not raise','composite_unsupported']) for c in failed),(name,proc.stdout)
            evidence['records'].append({'name':name,'disposition':'passed' if name=='reference' else 'killed','cases':len(cases),'failed_ids':[c.get('classname')+'::'+c.get('name') for c in failed]})
            (HERE/'evidence.json').write_text(json.dumps(evidence,indent=2))
            print(name,evidence['records'][-1]['disposition'],len(cases),flush=True)
if __name__=='__main__':main()
