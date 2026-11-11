"""Full offline run plus exact prior/new missing-behavior comparison."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
xml=Path(sys.argv[1]);log=xml.with_suffix('.log')
with log.open('w') as out:
    result=subprocess.run([sys.executable,'-m','pytest','tests/characterization','tests/unit','tests/contract','tests/integration','tests/acceptance','--network=deny','-q','--tb=line',f'--junitxml={xml}'],stdout=out,stderr=subprocess.STDOUT)
assert result.returncode==1,(result.returncode,str(log))
subprocess.run([sys.executable,str(HERE/'compare.py'),str(xml),str(HERE.parent/'T050ez-fa/offline-failures.json')],check=True)
