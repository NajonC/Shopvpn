"""Offline runner integration tests. Fake only the T3 boundary; run real processes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


RUNNER = Path(__file__).with_name("verification_runner.py")
FAKE_T3 = r'''#!/usr/bin/env python3
import json, sys
from pathlib import Path
base = Path(sys.argv[sys.argv.index('--base-dir') + 1])
config = json.loads((base / 'config.json').read_text())
if sys.argv[2] == 'show':
    print(json.dumps({'thread': {'threadId': config.get('thread', 'test-thread'), 'archived': False}}))
elif sys.argv[2] == 'send':
    message = sys.stdin.read()
    run_id = message.split('[verification-run:', 1)[1].split(']', 1)[0]
    run_dir = base / 'runs' / run_id
    # Delivery must never race ahead of a readable final result.
    result = json.loads((run_dir / 'result.json').read_text())
    assert result['finished_at']
    sent = base / 'messages.jsonl'
    attempt = len(sent.read_text().splitlines()) + 1 if sent.exists() else 1
    with sent.open('a') as out:
        out.write(json.dumps({'message': message, 'attempt': attempt}) + '\n')
    if attempt <= config.get('fail_attempts', 0):
        sys.exit(1)
    print(json.dumps({'delivery': 'queued'}))
'''


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.fake = self.base / "t3"
        self.fake.write_text(FAKE_T3)
        self.fake.chmod(0o700)
        self.config = self.base / "config.json"
        self.config.write_text("{}")
        self.runs = []

    def tearDown(self):
        for run in self.runs:
            (run / "cancel.request").touch()
        for run in self.runs:
            self.wait_for(run / "notification.json")
        self.temp.cleanup()

    def launch(self, code=None, options=(), command=None, success=True):
        argv = [sys.executable, str(RUNNER), "start", "--label", "runner test",
                "--thread", "test-thread", "--t3", str(self.fake),
                "--t3-base-dir", str(self.base), "--state-dir", str(self.base / "runs"),
                "--cwd", str(self.base), "--timeout", "5", "--kill-grace", "0.1",
                *options, "--", *(command or [sys.executable, "-c", code])]
        launched = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        if not success:
            return launched
        self.assertEqual(launched.returncode, 0, launched.stderr)
        run = Path(json.loads(launched.stdout)["run_dir"])
        self.runs.append(run)
        return run

    def wait_for(self, path, seconds=12):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if path.exists():
                value = json.loads(path.read_text())
                if value.get("status") != "retrying":
                    return value
            time.sleep(0.03)
        self.fail(f"Timed out awaiting {path}")

    def finished(self, run):
        self.wait_for(run / "notification.json")
        return json.loads((run / "result.json").read_text())

    def action(self, name, run, *args):
        return subprocess.run([sys.executable, str(RUNNER), name, str(run), *args],
                              capture_output=True, text=True, timeout=5)

    def test_detaches_and_preserves_output_and_argv(self):
        run = self.launch(command=[sys.executable, "-c",
                                  "import time,sys; time.sleep(.7); print(sys.argv[1])",
                                  "literal $(do-not-run); ' spaces"])
        self.assertFalse((run / "result.json").exists(), "Launcher waited for command completion")
        result = self.finished(run)
        self.assertEqual((result["outcome"], result["exit_code"]), ("passed", 0))
        self.assertIn("literal $(do-not-run); ' spaces", (run / "check.log").read_text())
        self.assertEqual(json.loads((run / "notification.json").read_text())["status"], "delivered")

    def test_failure_still_notifies_and_preserves_exit_code(self):
        run = self.launch("print('intentional failure'); raise SystemExit(7)")
        result = self.finished(run)
        self.assertEqual((result["outcome"], result["exit_code"]), ("failed", 7))
        self.assertIn("exit 7", (self.base / "messages.jsonl").read_text())

    def test_timeout_kills_descendants_even_if_the_leader_exits(self):
        child = "import signal,time,pathlib; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(2); pathlib.Path('leaked').touch()"
        code = f"import subprocess,sys,time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(10)"
        run = self.launch(code, options=["--timeout", "0.5"])
        result = self.finished(run)
        self.assertEqual((result["outcome"], result["exit_code"]), ("timeout", 124))
        time.sleep(2)
        self.assertFalse((self.base / "leaked").exists(), "Timed-out descendant survived")
        self.assertIn("timeout", (self.base / "messages.jsonl").read_text())

    def test_launch_error_is_recorded_and_notified(self):
        run = self.launch(command=[str(self.base / "nonexistent")])
        result = self.finished(run)
        self.assertEqual(result["outcome"], "error")
        self.assertIn("FileNotFoundError", result["error"])
        self.assertTrue((self.base / "messages.jsonl").exists())

    def test_signal_exit_is_incomplete_not_a_test_failure(self):
        run = self.launch("import os,signal; os.kill(os.getpid(), signal.SIGKILL)")
        result = self.finished(run)
        self.assertEqual((result["outcome"], result["exit_code"]), ("interrupted", -9))
        self.assertTrue((self.base / "messages.jsonl").exists())

    def test_wrong_thread_fails_before_command_starts(self):
        self.config.write_text(json.dumps({"thread": "wrong-thread"}))
        launched = self.launch("from pathlib import Path; Path('should-not-exist').touch()", success=False)
        self.assertNotEqual(launched.returncode, 0)
        self.assertFalse((self.base / "should-not-exist").exists())
        self.assertFalse((self.base / "runs").exists())

    def test_source_file_change_is_detected(self):
        source = self.base / "source.py"
        source.write_text("before")
        run = self.launch("import time; time.sleep(.7)", options=["--source-file", str(source)])
        source.write_text("after")
        self.assertTrue(self.finished(run)["source_changed"])

    def test_cancellation_suppresses_wake(self):
        run = self.launch("import time; time.sleep(10)")
        self.wait_for(run / "started.json")
        self.assertEqual(self.action("cancel", run).returncode, 0)
        self.assertEqual(self.finished(run)["outcome"], "cancelled")
        self.assertFalse((self.base / "messages.jsonl").exists())

    def test_delivery_retries_are_bounded(self):
        self.config.write_text(json.dumps({"fail_attempts": 10}))
        run = self.launch("pass")
        self.finished(run)
        notification = json.loads((run / "notification.json").read_text())
        self.assertEqual(notification["status"], "failed")
        self.assertEqual(len(notification["attempts"]), 3)
        self.assertEqual(len((self.base / "messages.jsonl").read_text().splitlines()), 3)

    def test_delivery_recovers_after_transient_failure(self):
        self.config.write_text(json.dumps({"fail_attempts": 1}))
        run = self.launch("pass")
        self.finished(run)
        notification = json.loads((run / "notification.json").read_text())
        self.assertEqual(notification["status"], "delivered")
        self.assertEqual(len(notification["attempts"]), 2)

    def test_review_is_explicit_and_repeat_acknowledgement_is_harmless(self):
        run = self.launch("import time; time.sleep(.7)")
        self.assertNotEqual(self.action("acknowledge", run, "--note", "too early").returncode, 0)
        self.finished(run)
        self.assertEqual(self.action("acknowledge", run, "--note", "Reviewed evidence").returncode, 0)
        original = (run / "reviewed.json").read_text()
        self.assertEqual(self.action("acknowledge", run, "--note", "Duplicate callback").returncode, 0)
        self.assertEqual((run / "reviewed.json").read_text(), original)


if __name__ == "__main__":
    unittest.main()
