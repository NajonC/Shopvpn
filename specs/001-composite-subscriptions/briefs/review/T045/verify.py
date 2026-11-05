"""T045 real-implementation mutations in an ephemeral, source-only offline copy.

Run with the repository .venv/bin/python. Only IDs/dispositions are printed;
pytest tracebacks may contain synthetic credentials and stay inside scratch.
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
TESTS = ('tests/unit/test_secrets_and_audit.py', 'tests/unit/test_secrets_failures.py')

# Each tuple contains independent exact edits and the cases that must detect them.
# Apply each mutant to the clean production source; never accumulate mutations.
MUTATIONS = [
    ('active_write', [('key_id = self._current_key_id', "key_id = 'old'")], 'test_round_trip'),
    ('active_only_read', [('key = self._keys.get(value.key_id)', 'key = self._keys.get(self._current_key_id)')], 'test_independently'),
    ('constant_nonce', [('nonce = secrets.token_bytes(12)', 'nonce = bytes(12)')], 'test_encrypt_uses'),
    ('plaintext_storage', [('ciphertext = AESGCM(self._keys[key_id]).encrypt(\n                nonce, plaintext.encode("utf-8"), aad\n            )', 'ciphertext = plaintext.encode("utf-8")')], 'test_round_trip'),
    ('refuse_empty', [('key_id = self._current_key_id', 'if not plaintext: raise ValueError\n            key_id = self._current_key_id')], 'test_round_trip'),
    ('refuse_unicode', [('key_id = self._current_key_id', 'if not plaintext.isascii(): raise ValueError\n            key_id = self._current_key_id')], 'test_round_trip'),
    ('ignore_version', [('or value.version != 1', 'or False')], 'test_decrypt_refuses_invalid_envelope_without_secret_exception[version]'),
    ('ignore_missing_key', [('if key is None:\n                raise ValueError', 'if key is None:\n                return ""')], 'test_decrypt_refuses_invalid_envelope_without_secret_exception[missing]'),
    ('ignore_authentication', [('raise SecretError("Secret decryption failed") from None', 'return ""')], 'test_decrypt_refuses'),
    ('ignore_id_authentication', [('aad = b"shopvpn:secrets:v1:" + value.key_id.encode("utf-8")', 'aad = b"shopvpn:secrets:v1:" + self._current_key_id.encode("utf-8")')], 'test_decrypt_refuses_invalid_envelope_without_secret_exception[key_id]'),
    ('fallback_key', [('copied = dict(keys)', 'copied = dict(keys)\n            copied.setdefault(current_key_id, secrets.token_bytes(32))')], 'test_missing_or_malformed'),
    ('invalid_key', [('len(key) not in (16, 24, 32)', 'False')], 'test_missing_or_malformed'),
    ('reject_valid_key_sizes', [('len(key) not in (16, 24, 32)', 'len(key) != 32')], 'test_supported_aes_keys'),
    ('retain_mutable_configuration', [('copied = dict(keys)', 'copied = keys')], 'test_supported_aes_keys'),
    ('mutable_envelope', [('@dataclass(frozen=True)', '@dataclass')], 'test_round_trip'),
    ('wrong_digest', [('hashlib.sha256(', 'hashlib.sha1(')], 'test_sha256'),
    ('trim_digest', [('token.encode("utf-8")', 'token.strip().encode("utf-8")')], 'test_sha256'),
    ('digest_encoding', [('token.encode("utf-8")', 'token.encode("utf-16")')], 'test_sha256'),
    ('raw_message', [('record.msg = "[redacted]"', 'pass')], 'test_redaction_scrubs'),
    ('raw_args', [('record.args = ()', 'pass')], 'test_redaction_scrubs'),
    ('raw_exception', [('record.exc_info = None', 'pass')], 'test_redaction_scrubs'),
    ('raw_cached_exception', [('record.exc_text = None', 'pass')], 'test_redaction_scrubs'),
    ('raw_stack', [('record.stack_info = None', 'pass')], 'test_redaction_scrubs'),
    ('raw_extra', [('delattr(record, name)', 'pass')], 'test_redaction_scrubs'),
    # Removing explicit message.pop alone is equivalent because the allowlist
    # loop removes message too; this combined loss tests the underlying rule.
    ('raw_formatter_cache', [('and name not in _TRUSTED_FIELDS:', 'and name not in _TRUSTED_FIELDS and name != "message":'), ('record.__dict__.pop("message", None)', 'pass')], 'test_redaction_removes_formatter'),
    ('drop_context', [('record.__dict__.update(trusted)', 'record.__dict__.update({key: None for key in trusted})')], 'test_redaction_scrubs'),
    ('drop_records', [('return True', 'return False')], 'test_redaction_scrubs'),
    ('wrong_severity', [('record.args = ()', 'record.levelno = logging.INFO\n        record.args = ()')], 'test_redaction_scrubs'),
    ('missing_install', [('def install_log_redaction(logger: logging.Logger) -> None:', 'def install_log_redaction(logger: logging.Logger) -> None:\n    return')], 'test_installed_filter'),
    ('ancestor_only_filter', [('handler.addFilter(SecretRedactionFilter())', 'pass')], 'test_installed_filter'),
]
for method in ('encryption', 'decryption'):
    boundary = f'except Exception:\n            raise SecretError("Secret {method} failed") from None'
    MUTATIONS.extend([
        (f'{method}_error_text', [(boundary, f'except Exception as error:\n            raise SecretError(str(error)) from None')], 'test_crypto_backend_failure'),
        (f'{method}_error_chain', [(boundary, f'except Exception:\n            raise SecretError("Secret {method} failed")')], 'test_crypto_backend_failure'),
    ])


def main():
    original = (ROOT / 'composite/secrets.py').read_text()
    with tempfile.TemporaryDirectory(prefix='t045-review-') as directory:
        scratch = Path(directory)
        for rel in ('tests/__init__.py', 'tests/conftest.py', 'composite/__init__.py', 'composite/secrets.py', 'composite/audit.py', *TESTS):
            destination = scratch / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, destination)
        shutil.copytree(ROOT / 'tests/_harness', scratch / 'tests/_harness', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable, '-c', 'import composite.secrets,tests; from pathlib import Path; assert Path(composite.secrets.__file__).is_relative_to(Path.cwd()); assert Path(tests.__file__).is_relative_to(Path.cwd())'], cwd=scratch, env=env, check=True)

        def run(selection):
            report = scratch / 'report.xml'
            report.unlink(missing_ok=True)
            result = subprocess.run([sys.executable, '-m', 'pytest', *TESTS, '--network=deny', '-q', '--tb=no', '-k', selection, f'--junitxml={report}'], cwd=scratch, env=env, capture_output=True, text=True, timeout=60)
            assert report.exists(), 'invalid run: no report'
            cases = list(ET.parse(report).iter('testcase'))
            assert cases and not any(c.find('error') is not None or c.find('skipped') is not None for c in cases), 'invalid collection/setup'
            failures = []
            for case in cases:
                failure = case.find('failure')
                if failure is not None:
                    message = failure.get('message', '')
                    assert not any(word in message for word in ('SyntaxError', 'ImportError', 'ModuleNotFoundError', 'AttributeError', 'KeyError', 'NameError', 'TypeError')), 'invalid mutation'
                    failures.append(case.get('name'))
            return result.returncode, len(cases), failures

        code, count, failures = run('not diagnostic_contains')
        assert code == 0 and count == 26 and not failures, 'real implementation baseline must pass'
        print('PRODUCTION BASELINE: 26 passed', flush=True)
        path = scratch / 'composite/secrets.py'
        for identity, edits, expected in MUTATIONS:
            mutated = original
            for before, after in edits:
                assert mutated.count(before) == 1, f'{identity}: unexpected edit match count'
                mutated = mutated.replace(before, after)
            compile(mutated, str(path), 'exec')
            path.write_text(mutated)
            shutil.rmtree(scratch / 'composite/__pycache__', ignore_errors=True)
            code, count, failures = run(expected)
            assert code == 1 and any(name.startswith(expected) for name in failures), f'{identity}: survivor or invalid run'
            print(json.dumps({'mutation': identity, 'disposition': 'killed', 'tests': failures}), flush=True)
            path.write_text(original)
        print(f'MUTATIONS: {len(MUTATIONS)} killed; no unresolved survivors. Scratch removed on exit.', flush=True)


if __name__ == '__main__':
    main()
