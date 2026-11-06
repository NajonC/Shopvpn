"""T050g real reseller HTTP models/routes/builder plus scratch-only type guards."""
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
SOURCE='admin_panel/server.py'
PACKET='tests/integration/test_composite_reseller_web_guards.py'
TESTS=[PACKET,'tests/characterization/test_unsupported_surfaces.py']
HELPER='_build_reseller_self_config'
ROUTES={'api_reseller_self_fixed':'ResellerSelfFixedBody','api_reseller_self_custom':'ResellerSelfBuildBody'}
PRED='product is not None and "service_kind" in product.keys() and product["service_kind"] == "composite"'
HG='    if '+PRED+':\n        raise HTTPException(403, "Composite product cannot use reseller web supply")\n'
RP='getattr(body, "service_kind", "legacy") == "composite"'
RG='    if '+RP+':\n        raise HTTPException(403, "Composite request cannot use reseller web supply")\n'
FIELD='    service_kind: str = "legacy"\n'


def once(s,b,a):
    assert s.count(b)==1,(b,s.count(b))
    return s.replace(b,a)


def change(source,name,fn):
    found=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.AsyncFunctionDef,ast.ClassDef)) and n.name==name]
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
    with tempfile.TemporaryDirectory(prefix='t050g-review-') as directory:
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
        reference=change(reference,HELPER,lambda s:once(s,'    if volume_gb < 0:',HG+'    if volume_gb < 0:'))
        for name,model in ROUTES.items():
            reference=change(reference,model,lambda s:once(s,':\n',':\n'+FIELD))
            anchor='    _require_reseller_admin(admin)' if name.endswith('fixed') else '    profile = _require_reseller_admin(admin)'
            reference=change(reference,name,lambda s:once(s,anchor,RG+anchor))

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
                    assert c.get('classname')=='tests.integration.test_composite_reseller_web_guards',c.attrib
            results.append({'name':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failed_test_ids':[c.get('classname')+'::'+c.get('name') for c,_ in failed]})
            print(name,results[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        def mutate(name,func,fn):
            s=change(reference,func,fn);assert s!=reference
            run(name,s)
        mutate('helper_omit',HELPER,lambda s:once(s,HG,''))
        mutate('helper_wrong_kind',HELPER,lambda s:once(s,PRED,PRED.replace('== "composite"','== "other"')))
        mutate('helper_reject_legacy',HELPER,lambda s:once(s,PRED,'product is not None and "service_kind" in product.keys()'))
        mutate('helper_reject_absent',HELPER,lambda s:once(s,PRED,'product is not None and ("service_kind" not in product.keys() or product["service_kind"] == "composite")'))
        mutate('helper_no_reason',HELPER,lambda s:once(s,'Composite product cannot use reseller web supply','Unsupported product'))
        mutate('helper_leak_name',HELPER,lambda s:once(s,'"Composite product cannot use reseller web supply"','"Composite product cannot use reseller web supply " + product["name"]'))
        mutate('helper_late_factory',HELPER,lambda s:once(once(s,HG,''),'    provider = get_provider(server)\n','    provider = get_provider(server)\n'+HG))
        mutate('helper_late_commit',HELPER,lambda s:once(once(s,HG,''),'    return {"username": result.username',HG+'    return {"username": result.username'))
        for name,model in ROUTES.items():
            mutate(name+'_omit',name,lambda s:once(s,RG,''))
            mutate(name+'_wrong_kind',name,lambda s:once(s,RP,RP.replace('== "composite"','== "other"')))
            mutate(name+'_reject_legacy',name,lambda s:once(s,RP,'True'))
            mutate(name+'_no_reason',name,lambda s:once(s,'Composite request cannot use reseller web supply','Unsupported request'))
            mutate(name+'_late_commit',name,lambda s:once(once(s,RG,''),'    return result',RG+'    return result'))
            mutate(name+'_discard_marker',model,lambda s:once(s,FIELD,''))
    (HERE/'evidence.md').write_text('# T050g web supply verification\n\nHashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nResults:\n```json\n'+json.dumps(results,indent=2)+'\n```\n\nAll mutants independent with relevant packet assertions; no survivors/errors/skips. Real synthetic signed-session HTTP, main/tenant accounting and external fakes. Scratch auto-cleaned; no production edits.\n')


if __name__=='__main__':main()
