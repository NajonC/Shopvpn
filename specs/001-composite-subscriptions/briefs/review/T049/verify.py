"""Mutate actual T049 code in disposable source-only offline scratch.

Reuses T047b2's rule families against production; no reference is installed.
Run from the repository with .venv/bin/python. Evidence is written beside this
runner only after every baseline and independent mutation has been validated.
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
SERVER = "admin_panel/server.py"
SERVICE = "composite/service.py"
SECURITY = "admin_panel/security.py"
AUTHORITY = "tests/integration/test_authority_matrix.py"
ROUTER = "tests/integration/test_composite_router.py"
MUTATIONS = []


def mutation(name, selected, *edits):
    MUTATIONS.append((name, selected, edits))


def server(name, before, after, selected):
    mutation(name, selected, (SERVER, before, after))


bearer = 'authorization.split(None, 1)[:1] and authorization.split(None, 1)[0].lower() == "bearer"'
refusal = '            raise HTTPException(403, "دسترسی کافی نیست.")'
csrf_check = 'not hmac.compare_digest(csrf, expected_csrf)'

server("leak_bearer", refusal + '\n\n        # The legacy verifier',
       '            raise HTTPException(403, authorization.partition(" ")[2])\n\n        # The legacy verifier', "test_http_bearers")
server("leak_cookie", 'raise HTTPException(403, "درخواست معتبر نیست.")',
       'raise HTTPException(403, request.cookies[COOKIE_NAME])', "test_http_cookie_mutations and missing-origin")
server("unguarded_router", 'router.dependencies.append(Depends(composite_gate))',
       'pass  # deliberately omit inherited authority', "test_http_router_refuses")
mutation("omit_role_guards", "test_http_router_refuses_roles_tenants_and_unmapped_owner and staff",
         (SERVER, '        require_owner(admin)', '        pass'),
         (SERVICE, 'or role != "owner"', 'or False'))
mutation("omit_tenant_guards", "test_http_router_refuses_roles_tenants_and_unmapped_owner and reseller",
         (SERVER, '        require_main_tenant(admin)', '        pass'),
         (SERVICE, 'tenant != ""', 'False'))
mutation("omit_owner_mapping", "test_http_router_refuses_roles_tenants_and_unmapped_owner and overlap",
         (SERVICE, 'or actor_id != main_owner_web_admin_id', 'or False'))
server("late_bearer_refusal", '        authorization = request.headers.get("authorization", "")',
       '        await get_current_admin(request)\n        authorization = request.headers.get("authorization", "")',
       "test_http_bearers and mobile")
server("case_sensitive_bearer", bearer, bearer.replace('.lower()', ''), "test_http_bearers")
server("omit_origin", 'request_origin != origin', 'False', "test_http_cookie_mutations and origin")
server("origin_from_host", 'request_origin != origin',
       'request_origin != str(request.base_url).rstrip("/")', "test_http_cookie_mutations and foreign-origin")
server("origin_prefix_match", 'request_origin != origin',
       'not (request_origin or "").startswith(origin)', "test_http_cookie_mutations and suffix-origin")
server("omit_csrf", 'csrf is None\n                    or ' + csrf_check,
       'False', "test_http_cookie_mutations and csrf")
server("unbound_csrf", csrf_check, 'len(csrf) != 64', "test_http_cookie_mutations and other-session-csrf")
server("post_only_csrf", 'request.method.upper() not in {"GET", "HEAD", "OPTIONS"}',
       'request.method.upper() == "POST"', "test_http_cookie_mutations and PATCH")
server("csrf_on_get", 'request.method.upper() not in {"GET", "HEAD", "OPTIONS"}',
       'True', "test_http_router_allows and GET")
mutation("reject_second_mapped_owner", "test_http_router_allows and 2",
         (SERVICE, 'or actor_id != main_owner_web_admin_id', 'or actor_id != 1 or actor_id != main_owner_web_admin_id'))
mutation("omit_signature", "test_http_router_requires_valid_session and tampered",
         (SECURITY, 'if not hmac.compare_digest(expected_sig, sig):', 'if False:'))
mutation("omit_expiry", "test_http_router_requires_valid_session and expired",
         (SECURITY, 'if payload.get("exp", 0) < time.time():', 'if False:'))
server("omit_active", 'if not admin or not admin["is_active"]:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")',
       'if not admin:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")', "test_http_router_requires_valid_session and inactive")
server("optional_cookie", '        admin = await get_current_admin(request)',
       '        admin = await get_current_admin(request) if request.cookies.get(COOKIE_NAME) else {"id": 1, "role": "owner", "tenant": ""}',
       "test_http_router_requires_valid_session and missing")
server("url_bearer_as_authority", refusal + '\n\n        # The legacy verifier',
       '            return\n\n        # The legacy verifier', "test_http_bearers and subscription")

# Configuration, actual app assembly, principal handoff, hostile input.
server("omit_mount", 'app.include_router(composite_router)', 'pass  # deliberately omit mounting',
       "test_real_app_mounts and 200")
server("ignore_configured_owner", 'main_owner_web_admin_id=owner,', 'main_owner_web_admin_id=1,',
       "test_real_app_mounts and 200")
server("infer_missing_owner", 'raw_owner = os.getenv("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID")',
       'raw_owner = os.getenv("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", "2")',
       "test_real_app_mounts and COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID and None")
server("infer_missing_installation", 'installation = os.getenv("COMPOSITE_MAIN_INSTALLATION_ID")',
       'installation = os.getenv("COMPOSITE_MAIN_INSTALLATION_ID", "guessed-main")',
       "test_real_app_mounts and COMPOSITE_MAIN_INSTALLATION_ID")
server("infer_missing_origin", 'origin = os.getenv("COMPOSITE_PUBLIC_ORIGIN")',
       'origin = os.getenv("COMPOSITE_PUBLIC_ORIGIN", "https://panel.example.invalid")',
       "test_real_app_mounts and COMPOSITE_PUBLIC_ORIGIN and None")
server("permit_invalid_config", '        if not configured:', '        if False:',
       "test_invalid_trusted_config")
server("change_principal_installation", 'main_installation_id=main_installation_id,',
       'main_installation_id="guessed-main",', "test_real_app_mounts and 200")
server("wrong_handoff_principal", 'request.state.composite_principal = principal',
       'request.state.composite_principal = composite_service.Principal("web_admin", 999, main_installation_id, "owner", "web")',
       "test_real_app_mounts and 200")
server("reject_nondefault_ports", 'port = parsed.port',
       'port = parsed.port\n        if port is not None:\n            return None', "test_valid_configured_origin")
server("malformed_origin_host", 'if not host or any(char.isspace() or char in "\\\\%<>{}|^`" for char in host):',
       'if not host:', "test_invalid_trusted_config")
server("allow_default_port_origin", 'if port == (443 if parsed.scheme == "https" else 80):',
       'if False:', "test_invalid_trusted_config")
server("non_ascii_csrf_authorized", '                request_origin = csrf = None',
       '                return principal', "test_non_ascii_csrf")
server("non_ascii_session_wrong_status", 'except UnicodeEncodeError:\n            raise HTTPException(401,',
       'except UnicodeEncodeError:\n            raise HTTPException(403,', "test_non_ascii_session")


def main():
    summary = []
    with tempfile.TemporaryDirectory(prefix="t049-review-") as directory:
        scratch = Path(directory)
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        for rel in tracked:
            p = Path(rel)
            if p.suffix == ".py" and (len(p.parts) == 1 or p.parts[0] in {
                    "admin_panel", "miniapp", "panel_providers", "composite"} or
                    rel.startswith("tests/_harness/") or rel in {
                        AUTHORITY, ROUTER, "tests/__init__.py", "tests/conftest.py",
                        "tests/integration/__init__.py"}):
                target = scratch / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
        (scratch / "admin_panel/static").mkdir(exist_ok=True)
        originals = {path: (scratch / path).read_text() for path in (SERVER, SERVICE, SECURITY)}
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
        for name in ("COMPOSITE_MAIN_INSTALLATION_ID", "COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", "COMPOSITE_PUBLIC_ORIGIN"):
            env.pop(name, None)
        subprocess.run([sys.executable, "-c", "from pathlib import Path; import composite.service, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (composite.service, tests))"], cwd=scratch, env=env, check=True)

        def run(selection):
            report = scratch / "result.xml"
            report.unlink(missing_ok=True)
            result = subprocess.run([sys.executable, "-m", "pytest", AUTHORITY, ROUTER,
                                     "--network=deny", "-q", "--tb=short", "-k", selection,
                                     f"--junitxml={report}"], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=90)
            assert report.exists(), result.stdout + result.stderr
            cases = list(ET.parse(report).iter("testcase"))
            assert cases and not any(c.find("error") is not None or c.find("skipped") is not None for c in cases), result.stdout
            failed = []
            for case in cases:
                failure = case.find("failure")
                if failure is not None:
                    # All mutants here deliberately produce assertion failures,
                    # never count broken setup/imports or unrelated exceptions.
                    message = failure.get("message", "")
                    assert message.startswith("assert ") or "AssertionError" in message, result.stdout
                    failed.append(case.get("name"))
            return result.returncode, len(cases), failed, result.stdout

        code, count, failed, output = run("test_http_ or test_invalid_trusted_config or test_valid_configured_origin or test_non_ascii or test_real_app_mounts")
        assert code == 0 and count == 95 and not failed, output
        print("ACTUAL PRODUCTION BASELINE: 95 passed", flush=True)
        for identity, selected, edits in MUTATIONS:
            for path, original in originals.items():
                (scratch / path).write_text(original)
            for path, before, after in edits:
                original = (scratch / path).read_text()
                assert original.count(before) == 1, (identity, path, original.count(before))
                changed = original.replace(before, after)
                compile(changed, path, "exec")
                (scratch / path).write_text(changed)
            code, count, failed, output = run(selected)
            assert code == 1 and failed, f"{identity}: survived or invalid\n{output}"
            row = dict(mutation=identity, disposition="killed", tests=failed)
            summary.append(row)
            print(json.dumps(row), flush=True)
        print(f"{len(MUTATIONS)} killed; no survivors or invalid runs; scratch removed on exit", flush=True)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / SERVER, ROOT / SERVICE, ROOT / SECURITY,
                        ROOT / AUTHORITY, ROOT / ROUTER, Path(__file__))}
    (HERE / "evidence.md").write_text(
        "# T049 actual-code mutation evidence\n\n95 production authority/configuration cases pass. "
        f"All {len(MUTATIONS)} behavior-changing mutants detected by relevant assertions. "
        "No references, survivors or invalid final runs. Scratch automatically removed.\n\n"
        "Reproduce: `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T049/verify.py`.\n\n```json\n" +
        json.dumps({"source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
                    "hashes": hashes, "mutations": summary}, indent=2) + "\n```\n")


if __name__ == "__main__":
    main()
