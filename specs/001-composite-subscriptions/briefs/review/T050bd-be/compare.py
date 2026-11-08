"""Compare final XML against accepted failure IDs and stable assertion reasons."""
from pathlib import Path
import hashlib,json,re,sys
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
def stable(message):
    # Pytest's first assertion line is stable; following explanatory repr lines
    # contain process addresses, temporary roots and collection-order details.
    line=re.sub(r'0x[0-9a-fA-F]+','<address>',message.splitlines()[0])
    return re.sub(r'(?:\d{4}-\d{2}-\d{2}|\.\.\.\d{1,2})? \d{2}:\d{2}:\d{2}', '<datetime>', line)
def main(xml,baseline):
    tree=ET.parse(xml);cases=list(tree.iter('testcase'))
    assert not list(tree.iter('error')) and not list(tree.iter('skipped'))
    fail={c.get('classname')+'::'+c.get('name'):c.find('failure').get('message','') for c in cases if c.find('failure') is not None}
    old=json.loads(Path(baseline).read_text())
    new={k:v for k,v in fail.items() if k.startswith('tests.integration.test_composite_gateway_renewal_guards::')}
    assert len(new)==48 and all('test_composite_renewal_refused_before_claim' in k and v.startswith('AssertionError:') for k,v in new.items()),new
    assert set(fail)==set(old)|set(new),(set(fail)-set(old)-set(new),set(old)-set(fail))
    mismatch={k:(stable(v),stable(fail[k])) for k,v in old.items() if stable(v)!=stable(fail[k])}
    assert not mismatch,mismatch
    snap=json.loads((HERE/'snapshot.json').read_text())
    changed=[p for p,h in snap['hashes'].items() if p!='specs/001-composite-subscriptions/tasks.md' and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    assert not changed,changed
    evidence=json.loads((HERE/'evidence.json').read_text())
    for p,h in evidence['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    (HERE/'offline-failures.json').write_text(json.dumps(fail,indent=2))
    (HERE/'expected_failures.json').write_text(json.dumps(new,indent=2))
    print('PASS',len(cases)-len(fail),'FAIL declared',len(fail),'TOTAL',len(cases),'prior identities/stable reasons and protected hashes match')
if __name__=='__main__':main(*sys.argv[1:])
