"""Reproduce T044 reference/mutations offline in an ephemeral source-only copy.

Run from the repository root with .venv/bin/python followed by this file's path.
Output contains test IDs and dispositions only, never pytest tracebacks/secrets.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TEST = "tests/unit/test_secrets_and_audit.py"

# Each replacement is applied exactly once to a fresh reference, never accumulated.
# Last field is the test name required to catch it; import/setup errors are invalid.
MUTATIONS = [
    ("active_write", "secrets", "key_id = self.current_key_id", "key_id = 'old'", "test_round_trip"),
    ("active_only_read", "secrets", "key = self.keys[value.key_id]", "key = self.keys[self.current_key_id]", "test_independently"),
    ("constant_nonce", "secrets", "nonce = os.urandom(12)", "nonce = bytes(12)", "test_encrypt_uses"),
    ("plaintext_storage", "secrets", "ciphertext = AESGCM(self.keys[key_id]).encrypt(nonce, plaintext.encode(\"utf-8\"), aad)", "ciphertext = plaintext.encode('utf-8')", "test_round_trip"),
    ("refuse_empty", "secrets", "key_id = self.current_key_id", "assert plaintext != ''\n        key_id = self.current_key_id", "test_round_trip"),
    ("refuse_unicode", "secrets", "key_id = self.current_key_id", "assert plaintext.isascii()\n        key_id = self.current_key_id", "test_round_trip"),
    ("ignore_version", "secrets", "if value.version != 1:", "if False:", "test_decrypt_refuses"),
    ("ignore_missing_key", "secrets", "key = self.keys[value.key_id]", "if value.key_id not in self.keys: return ''\n            key = self.keys[value.key_id]", "test_decrypt_refuses"),
    ("ignore_authentication", "secrets", "raise SecretError(\"decryption failed\") from None", "return ''", "test_decrypt_refuses"),
    ("ignore_id_authentication", "secrets", "aad = b\"shopvpn:secrets:v1:\" + value.key_id.encode(\"utf-8\")", "aad = b'shopvpn:secrets:v1:' + self.current_key_id.encode('utf-8')", "test_decrypt_refuses"),
    ("fallback_key", "secrets", "raise SecretError(\"missing active key\")", "keys = dict(keys, **{current_key_id: os.urandom(32)})", "test_missing_or_malformed"),
    ("invalid_key", "secrets", "raise SecretError(\"invalid key size\")", "pass", "test_missing_or_malformed"),
    ("wrong_digest", "secrets", "hashlib.sha256(token.encode(\"utf-8\"))", "hashlib.sha1(token.encode('utf-8'))", "test_sha256"),
    ("trim_digest", "secrets", "token.encode(\"utf-8\")", "token.strip().encode('utf-8')", "test_sha256"),
    ("digest_encoding", "secrets", "token.encode(\"utf-8\")", "token.encode('utf-16')", "test_sha256"),
    ("raw_message", "secrets", "record.msg = \"[redacted]\"", "pass", "test_redaction_scrubs"),
    ("raw_args", "secrets", "record.args = ()", "pass", "test_redaction_scrubs"),
    ("raw_exception", "secrets", "record.exc_info = None", "pass", "test_redaction_scrubs"),
    ("raw_cached_exception", "secrets", "record.exc_text = None", "pass", "test_redaction_scrubs"),
    ("raw_stack", "secrets", "record.stack_info = None", "pass", "test_redaction_scrubs"),
    ("raw_extra", "secrets", "delattr(record, key)", "pass", "test_redaction_scrubs"),
    ("drop_context", "secrets", "return True", "record.operation = record.tenant_id = record.record_id = None\n        return True", "test_redaction_scrubs"),
    ("drop_records", "secrets", "return True", "return False", "test_redaction_scrubs"),
    ("missing_install", "secrets", "def install_log_redaction(logger):", "def install_log_redaction(logger):\n    return", "test_installed_filter"),
    ("ancestor_only_filter", "secrets", "handler.addFilter(SecretRedactionFilter())", "pass", "test_installed_filter"),
    ("diagnostic_error", "audit", '"record_id": record_id}', '"record_id": record_id, "error": str(error)}', "test_diagnostic"),
    ("diagnostic_no_record", "audit", ', "record_id": record_id', '', "test_diagnostic"),
    ("diagnostic_success", "audit", '"record_id": record_id}', '"record_id": record_id, "success": True}', "test_diagnostic"),
]


def main():
    originals = {name: (HERE / f"reference_{name}.py").read_text() for name in ("secrets", "audit")}
    with tempfile.TemporaryDirectory(prefix="t044-review-") as directory:
        scratch = Path(directory)
        for rel in ("tests/__init__.py", "tests/unit/__init__.py", "tests/conftest.py", TEST):
            destination = scratch / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = ROOT / rel
            if source.exists():
                shutil.copyfile(source, destination)
            else:
                destination.touch()
        # Harness is test-only source; exclude bytecode and all generated state.
        shutil.copytree(ROOT / "tests/_harness", scratch / "tests/_harness", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (scratch / "composite").mkdir()
        (scratch / "composite/__init__.py").touch()
        for name, source in originals.items():
            (scratch / f"composite/{name}.py").write_text(source)
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE="1")
        # Confirm that the interpreter resolves reviewed modules inside scratch.
        subprocess.run([sys.executable, "-c", "import composite.secrets,tests; from pathlib import Path; assert Path(composite.secrets.__file__).is_relative_to(Path.cwd()); assert Path(tests.__file__).is_relative_to(Path.cwd())"], cwd=scratch, env=env, check=True)

        def run():
            report = scratch / "report.xml"
            process = subprocess.run([sys.executable, "-m", "pytest", TEST, "--network=deny", "-q", "--tb=no", f"--junitxml={report}"], cwd=scratch, env=env, capture_output=True, text=True, timeout=60)
            if not report.exists():
                raise RuntimeError("invalid run: no test report")
            cases = list(ET.parse(report).iter("testcase"))
            failures = [c for c in cases if c.find("failure") is not None]
            errors = [c for c in cases if c.find("error") is not None]
            assert len(cases) == 22 and not errors, "invalid collection/setup"
            for case in failures:
                message = case.find("failure").get("message", "")
                assert not any(x in message for x in ("SyntaxError", "ImportError", "ModuleNotFoundError", "AttributeError")), "invalid mutation"
            return process.returncode, [c.get("name") for c in failures]

        code, failures = run()
        assert code == 0 and not failures, "reference baseline must pass"
        print("REFERENCE: 22 passed", flush=True)
        for identity, module, before, after, expected in MUTATIONS:
            source = originals[module]
            assert source.count(before) == 1, f"{identity}: unexpected edit match count"
            path = scratch / f"composite/{module}.py"
            path.write_text(source.replace(before, after))
            # pytest imports must not reuse compiled bytecode between variants.
            shutil.rmtree(scratch / "composite/__pycache__", ignore_errors=True)
            code, failures = run()
            assert code == 1 and any(name.startswith(expected) for name in failures), f"{identity}: survivor or invalid run"
            print(json.dumps({"mutation": identity, "disposition": "killed", "tests": failures}), flush=True)
            path.write_text(source)
        print(f"MUTATIONS: {len(MUTATIONS)} killed; no unresolved survivors. Scratch removed on exit.", flush=True)


if __name__ == "__main__":
    main()
