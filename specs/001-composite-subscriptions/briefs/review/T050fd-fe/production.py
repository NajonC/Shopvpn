"""Collect exact production failures; only missing dispatch assertions are admissible."""
import json,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
xml=Path(sys.argv[1]);log=xml.with_suffix('.log')
with log.open('w') as out:
    result=subprocess.run([sys.executable,'-m','pytest','tests/integration/test_composite_telegram_inline_stock_alerts.py','--network=deny','-q','--tb=line',f'--junitxml={xml}'],stdout=out,stderr=subprocess.STDOUT)
tree=ET.parse(xml);cases=list(tree.iter('testcase'));fail={c.get('classname')+'::'+c.get('name'):c.find('failure').get('message','') for c in cases if c.find('failure') is not None}
assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped'))
assert result.returncode==1 and fail
assert all('missing T053' in v for v in fail.values()),fail
(HERE/'expected_failures.json').write_text(json.dumps(fail,indent=2))
print('PASS',len(cases)-len(fail),'DECLARED FAIL',len(fail),'TOTAL',len(cases))
