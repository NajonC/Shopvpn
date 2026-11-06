"""T050b scratch-only dispatch reference and independent rule mutations."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
AUTO = 'tests/integration/test_composite_auto_renewal_guards.py'
REMINDER = 'tests/integration/test_composite_reminder_guards.py'
TESTS = [AUTO, REMINDER, 'tests/characterization/test_legacy_renewal_reminders.py']
RR = 'renewal_reminders.py'
CA = 'connect_alerts.py'
RULES = [
    (RR, '_send_single_reminder', 'renewal', False),
    (RR, '_send_single_volume_reminder', 'volume', False),
    (CA, '_process_row', 'connect', False),
    (RR, 'check_and_process_auto_renewals', 'auto', True),
]
PRED = '"service_kind" in row.keys() and row["service_kind"] == "composite"'


def replace_once(text, before, after):
    assert text.count(before) == 1, (before, text.count(before))
    return text.replace(before, after)


def change_function(source, name, transform):
    start = source.index('async def ' + name + '(')
    end = source.find('\nasync def ', start + 1)
    if end == -1:
        end = len(source)
    return source[:start] + transform(source[start:end]) + source[end:]


def guard(marker, auto=False):
    indent = '        ' if auto else '    '
    result = 'continue' if auto else ('return False, False' if marker == 'connect' else 'return False')
    return (f'{indent}if {PRED}:\n'
            f'{indent}    logger.warning("Composite record refused by legacy {marker} job")\n'
            f'{indent}    {result}\n')


def main():
    snapshot = json.loads((HERE / 'snapshot.json').read_text())
    changed = [p for p, sha in snapshot['hashes'].items()
               if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != sha]
    assert not changed, changed
    assert subprocess.check_output(['git', 'diff', '--cached'], cwd=ROOT).decode() == snapshot['staged']
    assert subprocess.check_output(['git', 'diff'], cwd=ROOT).decode() == snapshot['unstaged']
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [RR, CA, *TESTS]}
    records = []
    with tempfile.TemporaryDirectory(prefix='t050b-review-') as directory:
        scratch = Path(directory)
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0') + TESTS
        for rel in set(paths):
            p = Path(rel)
            if p.suffix != '.py' or (len(p.parts)>1 and p.parts[0] not in {'tests','composite','panel_providers','admin_panel','miniapp'}):
                continue
            dest=scratch/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/rel,dest)
        env=dict(os.environ,PYTHONPATH=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHON_DOTENV_DISABLED='1')
        subprocess.run([sys.executable,'-c','from pathlib import Path; import renewal_reminders,connect_alerts,tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (renewal_reminders,connect_alerts,tests))'],cwd=scratch,env=env,check=True)
        reference={p:(scratch/p).read_text() for p in (RR,CA)}
        for path, name, marker, auto in RULES:
            anchor='        user_id = row["user_id"]' if auto else '    user_id = row["assigned_user_id"]'
            reference[path]=change_function(reference[path],name,lambda text:replace_once(text,anchor,guard(marker,auto)+anchor))

        def run(name,sources,baseline=False,marker=None):
            for p,s in sources.items():
                (scratch/p).write_text(s)
            report=scratch/'result.xml'
            # All reference cases; each mutant only tests its corresponding rule family.
            selected = TESTS if baseline else ([AUTO] if marker=='auto' else [REMINDER])
            command=[sys.executable,'-m','pytest',*selected,'--network=deny','-q','--tb=line',f'--junitxml={report}']
            if not baseline and marker != 'auto':
                selection={'renewal':'expiry','volume':'volume','connect':'connection'}[marker]
                command += ['-k',selection]
            proc=subprocess.run(command,cwd=scratch,env=env,capture_output=True,text=True,timeout=90)
            tree=ET.parse(report)
            cases=list(tree.iter('testcase'))
            failures=[(c,c.find('failure')) for c in cases if c.find('failure') is not None]
            assert cases and not list(tree.iter('error')) and not list(tree.iter('skipped')), proc.stdout+proc.stderr
            if baseline:
                assert proc.returncode==0 and not failures,proc.stdout+proc.stderr
            else:
                assert proc.returncode==1 and failures,(name,proc.stdout+proc.stderr)
                for c,f in failures:
                    text=(f.get('message','')+(f.text or '')).lower()
                    assert any(x in text for x in ('assert ','assertionerror')),(name,c.attrib,text)
                    assert c.get('classname','').startswith('tests.integration.test_composite_'),c.attrib
            records.append({'mutation':name,'disposition':'pass' if baseline else 'killed','cases':len(cases),'failures':[c.get('classname')+'::'+c.get('name') for c,_ in failures]})
            print(name,records[-1]['disposition'],len(cases),flush=True)

        run('reference',reference,True)
        for path, name, marker, auto in RULES:
            gate=guard(marker,auto)
            def mutate(label,transform):
                sources=dict(reference)
                sources[path]=change_function(sources[path],name,transform)
                assert sources[path]!=reference[path],label
                run(marker+'_'+label,sources,marker=marker)
            mutate('omit',lambda s:replace_once(s,gate,''))
            mutate('wrong_kind',lambda s:replace_once(s,PRED,PRED.replace('== "composite"','== "other"')))
            mutate('reject_legacy',lambda s:replace_once(s,PRED,'"service_kind" in row.keys()'))
            mutate('reject_absent',lambda s:replace_once(s,PRED,'"service_kind" not in row.keys() or row["service_kind"] == "composite"'))
            warning=f'logger.warning("Composite record refused by legacy {marker} job")'
            indent='            ' if auto else '        '
            mutate('no_reason',lambda s:replace_once(s,indent+warning+'\n',''))
            field='subscription_url' if auto else 'link'
            mutate('leak_link',lambda s:replace_once(s,warning,f'logger.warning("Composite {marker} refused %s", row["{field}"])'))
            if auto:
                late='        await _db(db.add_wallet_credit, user_id, -price)'
                mutate('late_panel',lambda s:replace_once(replace_once(s,gate,''),late,gate+late))
                mutate('abort_batch',lambda s:replace_once(s,gate,gate.replace('continue','return 0')))
            else:
                late='    info = await fetch_sub_info(row["link"])'
                mutate('late_fetch',lambda s:replace_once(replace_once(s,gate,''),late+'\n',late+'\n'+gate))
                late='    need_connect_check =' if marker=='connect' else '    settings ='
                mutate('late_missing_user',lambda s:replace_once(replace_once(s,gate,''),late,gate+late))
                # Helpers return False for a refused row; returning True incorrectly counts it as sent.
                mutate('false_success',lambda s:replace_once(s,gate,gate.replace('return False, False','return True, False') if marker=='connect' else gate.replace('return False','return True')))
        # A top-level early return must not prevent the valid candidate after a composite row.
        for job,fn,marker,zero in [('expiry','check_and_send_renewal_reminders','renewal','0'),('volume','check_and_send_volume_reminders','volume','0'),('connection','check_and_send_connect_alerts','connect','(0, 0)')]:
            path=CA if job=='connection' else RR
            sources=dict(reference)
            block=f'    for row in rows:\n        if {PRED}:\n            return {zero}\n'
            sources[path]=change_function(sources[path],fn,lambda s:replace_once(s,'    for row in rows:\n',block))
            run(marker+'_abort_batch',sources,marker=marker)
    (HERE/'evidence.md').write_text('# T050b reference and mutation evidence\n\nSource hashes:\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\nIndependent results:\n```json\n'+json.dumps(records,indent=2)+'\n```\n\nEvery mutant was applied independently to the passing executable reference. Relevant packet assertion failures only; no survivors/errors/skips. Source-only scratch automatically deleted. No production implementation changed.\n')


if __name__=='__main__':
    main()
