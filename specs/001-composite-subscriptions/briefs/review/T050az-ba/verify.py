"""Reproduce reference/all independent mutants in a disposable source-only scratch."""
from pathlib import Path
import ast, hashlib, json, os, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from variants import variants
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE='blupal_payment.py'
PACKET=['tests/integration/test_composite_blupal_fulfillment_guards.py']
TESTS=PACKET+['tests/characterization/test_callbacks_fsm.py']
def main():
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [SOURCE,*TESTS,'database.py','panel_providers/__init__.py']}
    records=[]
    with tempfile.TemporaryDirectory(prefix=HERE.name+'-') as folder:
        scratch=Path(folder)
        paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')+PACKET
        for rel in set(paths):
            p=Path(rel)
            if p.suffix!='.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):continue
            dest=scratch/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dest)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from tests._harness.legacy_bot import use_synthetic_bot_settings;use_synthetic_bot_settings();import blupal_payment,tests;from pathlib import Path;assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (blupal_payment,tests))'],cwd=scratch,env=env,check=True)
        for name,source in variants((ROOT/SOURCE).read_text()):
            ast.parse(source);(scratch/SOURCE).write_text(source)
            xml=scratch/'result.xml'
            proc=subprocess.run([sys.executable,'-m','pytest',*(TESTS if name=='reference' else PACKET),'--network=deny','-q','--tb=line',f'--junitxml={xml}'],cwd=scratch,env=env,capture_output=True,text=True,timeout=90)
            tree=ET.parse(xml);cases=list(tree.iter('testcase'));fail=[c for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')),(name,proc.stdout,proc.stderr)
            if name=='reference':assert proc.returncode==0 and not fail,(name,proc.stdout,proc.stderr)
            else:
                assert proc.returncode==1 and fail,(name,proc.stdout,proc.stderr)
                for c in fail:
                    message=c.find('failure').get('message','')+(c.find('failure').text or '')
                    assert 'assert' in message.lower() or 'DID NOT RAISE' in message,(name,c.attrib,message)
            records.append(dict(name=name,cases=len(cases),disposition='passed' if name=='reference' else 'killed',failed_test_ids=[c.get('classname')+'::'+c.get('name') for c in fail]))
            print(name,records[-1]['disposition'],len(cases),flush=True)
    (HERE/'evidence.json').write_text(json.dumps(dict(hashes=hashes,records=records,scratch='auto-cleaned'),indent=2))
if __name__=='__main__':main()
