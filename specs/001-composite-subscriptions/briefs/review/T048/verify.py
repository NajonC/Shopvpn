"""Mutate ACTUAL T048 production code in source-only, network-denied scratch.

Reuses the five legacy authentication mutations from accepted T047b1 tooling;
service mutations are adapted to Luna's implementation rather than a reference.
No reference service is installed. Each mutant starts from unchanged source.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SERVICE = "composite/service.py"
AUTHORITY = "tests/integration/test_authority_matrix.py"
RECORDS = "tests/unit/test_service_records.py"
MUTATIONS = []


def service(identity, before, after, selected):
    MUTATIONS.append((identity, SERVICE, before, after, selected))


# T047a: all 17 rules, including valid buyers and alternative actors.
service("callback_message_actor", 'actor_id = getattr(sender, "id", None)',
        'actor_id = event.message.from_user.id if hasattr(event, "message") else getattr(sender, "id", None)', "test_forged_callback_actor")
service("payload_actor", 'actor_id = getattr(sender, "id", None)', 'actor_id = event.user_id', "test_forged_callback_actor")
telegram_return = '"telegram", actor_id, tenant_installation_id, "customer", "telegram"'
service("payload_tenant", telegram_return, '"telegram", actor_id, event.tenant_installation_id, "customer", "telegram"', "test_own_resources_allowed")
service("main_tenant_hardcoded", telegram_return, '"telegram", actor_id, "synthetic-main-installation", "customer", "telegram"', "test_non_main_transport")
service("missing_actor_fallback", 'raise AuthorityError("unauthenticated")', 'actor_id = event.user_id', "test_missing_authenticated_sender")
service("omit_customer_ownership", 'or customer_telegram_id != principal.authenticated_actor_id', 'or False', "test_forged_callback_actor")
service("omit_resource_tenant", 'resource_tenant_installation_id != principal.tenant_installation_id', 'False', "test_cross_tenant_resource")
service("allow_non_main", 'or principal.tenant_installation_id != main_installation_id', 'or False', "test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]")
service("omit_domain", 'principal.identity_domain != "telegram"', 'False', "test_matching_numeric_id")
service("omit_interface", 'or principal.authenticated_interface != "telegram"', 'or False', "test_matching_numeric_id")
service("omit_role", 'or principal.role != "customer"', 'or False', "test_matching_numeric_id")
service("reverse_ownership", 'customer_telegram_id != principal.authenticated_actor_id', 'customer_telegram_id == principal.authenticated_actor_id', "test_own_resources_allowed")
anchor = '    return Principal(\n        "telegram",'
service("reject_payload_mismatch", anchor, '    if event.user_id != actor_id or event.tenant_installation_id != tenant_installation_id:\n        raise AuthorityError("forbidden")\n' + anchor, "test_own_resources_allowed")
service("reject_reseller_buyer", anchor, '    if sender.is_reseller:\n        raise AuthorityError("forbidden")\n' + anchor, "test_own_resources_allowed")
service("reject_discount_buyer", anchor, '    if sender.has_discount:\n        raise AuthorityError("forbidden")\n' + anchor, "test_own_resources_allowed")
service("hardcode_customer_owner", 'customer_telegram_id != principal.authenticated_actor_id', 'customer_telegram_id != 101', "test_ownership_is_not_hardcoded")
service("leak_target_in_error", 'raise AuthorityError("not_found")', 'raise AuthorityError(f"not_found:{resource_tenant_installation_id}:{customer_telegram_id}")', "test_cross_tenant_resource")

# T047b1: the same 16 service rules, adapted to local variables and early guards.
service("omit_web_tenant", 'tenant != ""', 'False', "test_web_signed_tenant")
service("missing_tenant_is_main", 'tenant != ""', 'bool(tenant)', "test_web_adapter_refuses")
service("accept_main_alias", 'tenant != ""', 'tenant not in ("", "main")', "test_web_adapter_refuses")
service("omit_web_role", 'or role != "owner"', 'or False', "test_web_database_staff")
service("omit_mobile", 'if "mobile_token_id" in admin:', 'if False:', "test_web_adapter_refuses")
service("coerce_actor", 'type(actor_id) is not int', 'not isinstance(actor_id, (int, str))', "test_web_adapter_refuses")
service("coerce_mapping", 'type(main_owner_web_admin_id) is not int', 'not isinstance(main_owner_web_admin_id, int)', "test_web_mapping")
service("omit_mapping", 'or actor_id != main_owner_web_admin_id', 'or False', "test_web_telegram_owner_number")
service("telegram_id_fallback", 'or actor_id != main_owner_web_admin_id', 'or (actor_id != main_owner_web_admin_id and actor_id != 2)', "test_web_telegram_owner_number")
web_return = '"web_admin", actor_id, main_installation_id, "owner", "web"'
service("wrong_domain", web_return, '"telegram", actor_id, main_installation_id, "owner", "web"', "test_web_explicit_owner")
service("wrong_interface", web_return, '"web_admin", actor_id, main_installation_id, "owner", "telegram"', "test_web_explicit_owner")
service("wrong_role", web_return, '"web_admin", actor_id, main_installation_id, "customer", "web"', "test_web_explicit_owner")
service("hardcode_web_actor", web_return, '"web_admin", 1, main_installation_id, "owner", "web"', "test_web_explicit_owner")
service("hardcode_installation", web_return, '"web_admin", actor_id, "synthetic-main-installation", "owner", "web"', "test_web_explicit_owner")
service("reject_alternative_owner", 'or actor_id != main_owner_web_admin_id', 'or actor_id != 1 or actor_id != main_owner_web_admin_id', "test_web_explicit_owner")
service("leak_web_id", '    if not isinstance(admin, Mapping):', '    if admin.get("id") == 2:\n        raise AuthorityError("forbidden:2")\n    if not isinstance(admin, Mapping):', "test_web_telegram_owner_number")
# Established session authentication stays real; run its five original mutations.
MUTATIONS.extend(m for m in runpy.run_path(str(HERE.parent / "T047b1/verify.py"))["MUTATIONS"] if m[1] != SERVICE)

# New records: frozen identity/request/progress, private context, preserved facts.
for cls, selected in (("Principal", "test_authenticated_principal_cannot"),
                      ("CommandContext", "test_command_context_retains"),
                      ("CommandResult", "test_result_preserves_distinct")):
    service("mutable_" + cls, '@dataclass(frozen=True)\nclass ' + cls + ':', '@dataclass\nclass ' + cls + ':', selected)
service("expose_private_reason", 'field(default=None, repr=False)', 'field(default=None, repr=True)', "test_command_context_retains")
for identity, assignment, selected in (
    ("claim_confirmed", 'object.__setattr__(self, "state", "confirmed")', "test_result_preserves_distinct"),
    ("reset_clock", 'object.__setattr__(self, "original_clock_at", 0)', "test_result_retains_original"),
    ("drop_restrictions", 'object.__setattr__(self, "desired_restrictions", ())', "test_result_retains_original"),
    ("drop_usage_qualification", 'object.__setattr__(self, "qualified_usage", None)', "test_result_retains_original"),
):
    service(identity, '    support_action: str = ""', '    support_action: str = ""\n\n    def __post_init__(self):\n        ' + assignment, selected)
service("accept_private_result_field", '    support_action: str = ""', '    support_action: str = ""\n    audit_reason: str | None = None', "test_general_result_has_no_raw")


def main():
    summary = []
    with tempfile.TemporaryDirectory(prefix="t048-review-") as directory:
        scratch = Path(directory)
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        source_dirs = {"admin_panel", "miniapp", "panel_providers", "composite"}
        for rel in tracked:
            p = Path(rel)
            if (p.suffix == ".py" and (len(p.parts) == 1 or p.parts[0] in source_dirs
                    or rel.startswith("tests/_harness/") or rel in (AUTHORITY, RECORDS, "tests/__init__.py", "tests/conftest.py", "tests/integration/__init__.py", "tests/unit/__init__.py"))):
                target = scratch / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
        (scratch / "admin_panel/static").mkdir(exist_ok=True)
        originals = {p: (scratch / p).read_text() for p in {m[1] for m in MUTATIONS}}
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
        subprocess.run([sys.executable, "-c", "from pathlib import Path; import composite.service, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (composite.service, tests))"], cwd=scratch, env=env, check=True)

        def run(selection):
            report = scratch / "result.xml"
            report.unlink(missing_ok=True)
            result = subprocess.run([sys.executable, "-m", "pytest", AUTHORITY, RECORDS, "--network=deny", "-q", "--tb=short", "-k", selection, f"--junitxml={report}"], cwd=scratch, env=env, capture_output=True, text=True, timeout=90)
            assert report.exists(), result.stdout + result.stderr
            cases = list(ET.parse(report).iter("testcase"))
            assert cases and not any(c.find("error") is not None or c.find("skipped") is not None for c in cases), result.stdout
            failed = []
            for c in cases:
                f = c.find("failure")
                if f is not None:
                    assert not any(s in f.get("message", "") for s in ("AttributeError", "NameError", "KeyError", "ImportError", "SyntaxError")), result.stdout
                    # A missing expected exception is a relevant assertion failure,
                    # not an actual TypeError raised by broken setup/tooling.
                    message = f.get("message", "")
                    assert "TypeError" not in message or message == "Failed: DID NOT RAISE TypeError", result.stdout
                    failed.append(c.get("name"))
            return result.returncode, len(cases), failed, result.stdout

        code, count, failed, output = run("not test_http_")
        assert code == 0 and count == 50 and not failed, output
        print("ACTUAL PRODUCTION BASELINE: 50 passed", flush=True)
        for identity, path, before, after, selected in MUTATIONS:
            original = originals[path]
            assert original.count(before) == 1, (identity, original.count(before))
            changed = original.replace(before, after)
            compile(changed, path, "exec")
            (scratch / path).write_text(changed)
            code, count, failed, output = run(selected)
            assert code == 1 and failed, f"{identity}: survived or invalid\n{output}"
            row = dict(mutation=identity, disposition="killed", tests=failed)
            summary.append(row)
            print(json.dumps(row), flush=True)
            (scratch / path).write_text(original)
        print(f"{len(MUTATIONS)} killed; no survivors or invalid runs; scratch removed on exit", flush=True)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / SERVICE, ROOT / AUTHORITY, ROOT / RECORDS, Path(__file__), HERE.parent / "T047b1/verify.py", ROOT / "admin_panel/server.py", ROOT / "admin_panel/security.py")}
    # Compact synthetic review evidence only, never payloads or databases.
    (HERE / "evidence.md").write_text(
        "# T048 real-code mutation evidence\n\nProduction baseline: 50 passed. "
        f"All {len(MUTATIONS)} behavior-changing mutants detected; no survivors or invalid runs. "
        "No reference implementation installed. Source-only scratch automatically removed.\n\n"
        "Reproduce: `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T048/verify.py`.\n\n"
        "```json\n" + json.dumps({"source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(), "hashes": hashes, "mutations": summary}, indent=2) + "\n```\n")
    print(json.dumps({"hashes": hashes}), flush=True)


if __name__ == "__main__":
    main()
