"""Compare exact declared missing behavior IDs/reasons and protected sources."""
from pathlib import Path
import hashlib,json,sys
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(HERE.parent/'T050dd-de'))
from compare import stable

def main(xml,baseline):
    tree=ET.parse(xml);cases=list(tree.iter('testcase'))
    assert not list(tree.iter('error')) and not list(tree.iter('skipped'))
    fail={c.get('classname')+'::'+c.get('name'):c.find('failure').get('message','') for c in cases if c.find('failure') is not None}
    old=json.loads(Path(baseline).read_text());new=json.loads((HERE/'expected_failures.json').read_text())
    assert set(fail)==set(old)|set(new),(set(fail)-set(old)-set(new),set(old)-set(fail))
    assert all(stable(fail[k])==stable(v) for k,v in {**old,**new}.items())
    snap=json.loads((HERE/'protected.json').read_text())
    allowed={'specs/001-composite-subscriptions/tasks.md'}
    assert not [p for p,h in snap.items() if p not in allowed and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    evidence=json.loads((HERE/'evidence.json').read_text())
    for p,h in evidence['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    (HERE/'offline-failures.json').write_text(json.dumps(fail,indent=2))
    print('PASS',len(cases)-len(fail),'DECLARED FAIL',len(fail),'TOTAL',len(cases),'exact identities/stable reasons/protected hashes matched')
if __name__=='__main__':main(*sys.argv[1:])
