"""Run the real T047a tests against a reference and independent rule mutations.

Source-only export into unique /tmp scratch; never edits production. Invoke with
the repository .venv/bin/python. T048 must adapt these mutations to real code.
"""

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
TEST = "tests/integration/test_authority_matrix.py"
SERVICE = "composite/service.py"
MUTATIONS = [
    ("callback_message_actor", 'actor = getattr(sender, "id", None)',
     'actor = event.message.from_user.id if hasattr(event, "message") else getattr(sender, "id", None)',
     "test_forged_callback_actor"),
    ("payload_actor", 'actor = getattr(sender, "id", None)', 'actor = event.user_id',
     "test_forged_callback_actor"),
    ("payload_tenant", 'return Principal("telegram", actor, tenant_installation_id,',
     'return Principal("telegram", actor, event.tenant_installation_id,',
     "test_own_resources_allowed"),
    ("main_tenant_hardcoded", 'return Principal("telegram", actor, tenant_installation_id,',
     'return Principal("telegram", actor, "synthetic-main-installation",',
     "test_non_main_transport"),
    ("missing_actor_fallback", 'raise AuthorityError("unauthenticated")', 'actor = event.user_id',
     "test_missing_authenticated_sender"),
    ("omit_customer_ownership", 'or customer_telegram_id != principal.authenticated_actor_id', 'or False',
     "test_forged_callback_actor"),
    ("omit_resource_tenant", 'resource_tenant_installation_id != principal.tenant_installation_id', 'False',
     "test_cross_tenant_resource"),
    ("allow_non_main", 'or principal.tenant_installation_id != main_installation_id', 'or False',
     "test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]"),
    ("omit_domain", 'principal.identity_domain != "telegram"', 'False',
     "test_matching_numeric_id"),
    ("omit_interface", 'or principal.authenticated_interface != "telegram"', 'or False',
     "test_matching_numeric_id"),
    ("omit_role", 'or principal.role != "customer"', 'or False',
     "test_matching_numeric_id"),
    ("reverse_ownership", 'customer_telegram_id != principal.authenticated_actor_id',
     'customer_telegram_id == principal.authenticated_actor_id', "test_own_resources_allowed"),
    ("reject_payload_mismatch", 'return Principal("telegram", actor, tenant_installation_id,',
     'if event.user_id != actor or event.tenant_installation_id != tenant_installation_id:\n        raise AuthorityError("forbidden")\n    return Principal("telegram", actor, tenant_installation_id,',
     "test_own_resources_allowed"),
    ("reject_reseller_buyer", 'return Principal("telegram", actor, tenant_installation_id,',
     'if sender.is_reseller:\n        raise AuthorityError("forbidden")\n    return Principal("telegram", actor, tenant_installation_id,',
     "test_own_resources_allowed"),
    ("reject_discount_buyer", 'return Principal("telegram", actor, tenant_installation_id,',
     'if sender.has_discount:\n        raise AuthorityError("forbidden")\n    return Principal("telegram", actor, tenant_installation_id,',
     "test_own_resources_allowed"),
    ("hardcode_owner", 'customer_telegram_id != principal.authenticated_actor_id',
     'customer_telegram_id != 101', "test_ownership_is_not_hardcoded"),
    ("leak_target_in_error", 'raise AuthorityError("not_found")',
     'raise AuthorityError(f"not_found:{resource_tenant_installation_id}:{customer_telegram_id}")',
     "test_cross_tenant_resource"),
]


def main():
    original = (HERE / "reference_service.py").read_text()
    with tempfile.TemporaryDirectory(prefix="t047a-review-") as directory:
        scratch = Path(directory)
        for rel in ("tests/__init__.py", "tests/conftest.py", "tests/integration/__init__.py",
                    "composite/__init__.py", TEST):
            target = scratch / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        shutil.copytree(ROOT / "tests/_harness", scratch / "tests/_harness",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (scratch / SERVICE).write_text(original)
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE="1")
        subprocess.run([sys.executable, "-c", "from pathlib import Path; import composite.service, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (composite.service, tests))"],
                       cwd=scratch, env=env, check=True)

        def run(selection=None):
            report = scratch / "report.xml"
            report.unlink(missing_ok=True)
            command = [sys.executable, "-m", "pytest", TEST, "--network=deny", "-q",
                       "--tb=short", f"--junitxml={report}"]
            if selection:
                command.extend(["-k", selection])
            result = subprocess.run(command, cwd=scratch, env=env, capture_output=True, text=True, timeout=60)
            assert report.exists(), result.stdout + result.stderr
            cases = list(ET.parse(report).iter("testcase"))
            assert cases and not any(c.find("error") is not None or c.find("skipped") is not None for c in cases), result.stdout
            failures = []
            for case in cases:
                failure = case.find("failure")
                if failure is not None:
                    message = failure.get("message", "")
                    assert not any(word in message for word in ("SyntaxError", "ImportError", "AttributeError", "KeyError", "NameError", "TypeError")), result.stdout
                    failures.append(case.get("name"))
            return result.returncode, len(cases), failures, result.stdout

        code, count, failures, output = run()
        assert code == 0 and count == 18 and not failures, output
        print("REFERENCE BASELINE: 18 passed", flush=True)
        for identity, before, after, selected in MUTATIONS:
            assert original.count(before) == 1, identity
            changed = original.replace(before, after)
            compile(changed, SERVICE, "exec")
            (scratch / SERVICE).write_text(changed)
            code, count, failures, output = run(selected)
            assert code == 1 and failures, f"{identity}: surviving/invalid\n{output}"
            print(json.dumps(dict(mutation=identity, disposition="killed", tests=failures)), flush=True)
            (scratch / SERVICE).write_text(original)
        print(f"{len(MUTATIONS)} mutations killed; no unresolved survivors. Scratch removed on exit.", flush=True)
    for path in (ROOT / TEST, HERE / "reference_service.py", Path(__file__)):
        print(f"SHA256 {path.relative_to(ROOT)}: {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
