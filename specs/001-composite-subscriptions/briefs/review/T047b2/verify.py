"""Reproduce T047b2 reference/mutations in an isolated source-only scratch copy.

No production implementation is installed. The inherited service references support the router contract. T049 must
rerun this campaign against its actual implementation and verify app mounting. No real configuration/data is exported.
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
SERVER = "admin_panel/server.py"
SECURITY = "admin_panel/security.py"
MUTATIONS = [
    ("leak_raw_bearer", [(SERVER, '            raise HTTPException(403, "forbidden")\n        admin = await get_current_admin(request)', '            raise HTTPException(403, request.headers["authorization"].partition(" ")[2])\n        admin = await get_current_admin(request)')], "test_http_bearers"),
    ("leak_cookie", [(SERVER, '            if request.headers.get("origin") != public_origin:\n                raise HTTPException(403, "forbidden")', '            if request.headers.get("origin") != public_origin:\n                raise HTTPException(403, request.cookies[COOKIE_NAME])')], "test_http_cookie_mutations and missing-origin"),
    ("unguarded_router", [(SERVER, 'dependencies=[Depends(composite_gate)]', 'dependencies=[]')], "test_http_router_refuses"),
    ("omit_role_guards", [(SERVER, '        require_owner(admin)', '        pass'), (SERVICE, 'or admin.get("role") != "owner"', 'or False')], "test_http_router_refuses_roles_tenants_and_unmapped_owner and staff"),
    ("omit_tenant_guards", [(SERVER, '        require_main_tenant(admin)', '        pass'), (SERVICE, 'admin.get("tenant") != ""', 'False')], "test_http_router_refuses_roles_tenants_and_unmapped_owner and reseller"),
    ("omit_owner_mapping", [(SERVICE, 'or admin["id"] != main_owner_web_admin_id', 'or False')], "test_http_router_refuses_roles_tenants_and_unmapped_owner and overlap"),
    ("late_mobile_refusal", [(SERVER, '        if request.headers.get("authorization", "").lower().startswith("bearer "):\n            raise HTTPException(403, "forbidden")\n        admin = await get_current_admin(request)', '        admin = await get_current_admin(request)\n        if request.headers.get("authorization", "").lower().startswith("bearer "):\n            raise HTTPException(403, "forbidden")')], "test_http_bearers_rejected_before_any_database_change and mobile"),
    ("bearer_scheme_case_sensitive", [(SERVER, 'request.headers.get("authorization", "").lower().startswith("bearer ")', 'request.headers.get("authorization", "").startswith("Bearer ")')], "test_http_bearers"),
    ("omit_origin", [(SERVER, 'request.headers.get("origin") != public_origin', 'False')], "test_http_cookie_mutations and origin"),
    ("origin_from_host", [(SERVER, 'request.headers.get("origin") != public_origin', 'request.headers.get("origin") != str(request.base_url).rstrip("/")')], "test_http_cookie_mutations and foreign-origin"),
    ("origin_prefix_match", [(SERVER, 'request.headers.get("origin") != public_origin', 'not request.headers.get("origin", "").startswith(public_origin)')], "test_http_cookie_mutations and suffix-origin"),
    ("omit_csrf", [(SERVER, 'not hmac.compare_digest(expected, supplied)', 'False')], "test_http_cookie_mutations and csrf"),
    ("accept_any_nonempty_csrf", [(SERVER, 'not hmac.compare_digest(expected, supplied)', 'not supplied')], "test_http_cookie_mutations and other-session-csrf"),
    ("post_only", [(SERVER, 'request.method not in {"GET", "HEAD", "OPTIONS"}', 'request.method == "POST"')], "test_http_cookie_mutations and PATCH"),
    ("csrf_on_get", [(SERVER, 'request.method not in {"GET", "HEAD", "OPTIONS"}', 'True')], "test_http_router_allows and GET"),
    ("reject_other_mapped_owner", [(SERVICE, 'or admin["id"] != main_owner_web_admin_id', 'or admin["id"] != 1 or admin["id"] != main_owner_web_admin_id')], "test_http_router_allows and 2"),
    ("omit_hmac", [(SECURITY, 'if not hmac.compare_digest(expected_sig, sig):', 'if False:')], "test_http_router_requires_valid_session and tampered"),
    ("omit_expiry", [(SECURITY, 'if payload.get("exp", 0) < time.time():', 'if False:')], "test_http_router_requires_valid_session and expired"),
    ("omit_active", [(SERVER, 'if not admin or not admin["is_active"]:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")', 'if not admin:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")')], "test_http_router_requires_valid_session and inactive"),
    ("cookie_optional", [(SERVER, '        admin = await get_current_admin(request)', '        admin = await get_current_admin(request) if request.cookies.get(COOKIE_NAME) else {"id": 1, "tenant": "", "role": "owner"}')], "test_http_router_requires_valid_session and missing"),
    ("url_bearer_as_authority", [(SERVER, '            raise HTTPException(403, "forbidden")\n        admin = await get_current_admin(request)', '            return\n        admin = await get_current_admin(request)')], "test_http_bearers_rejected_before_any_database_change and subscription"),
]



def main():
    with tempfile.TemporaryDirectory(prefix="t047b2-review-") as directory:
        scratch = Path(directory)
        # Export tracked Python SOURCE only; no env/runtime files or databases.
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        source_dirs = {"admin_panel", "miniapp", "panel_providers", "composite"}
        for rel in tracked:
            p = Path(rel)
            if (p.suffix == ".py" and (len(p.parts) == 1 or p.parts[0] in source_dirs
                    or rel.startswith("tests/_harness/") or rel in (TEST, "tests/__init__.py", "tests/conftest.py", "tests/integration/__init__.py"))):
                target = scratch / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
        # StaticFiles checks the directory at import; no HTTP/static routes run.
        (scratch / "admin_panel/static").mkdir(exist_ok=True)
        (scratch / SERVICE).write_text(
            (HERE.parent / "T047a/reference_service.py").read_text() + "\n" + (HERE.parent / "T047b1/reference_web.py").read_text())
        with (scratch / SERVER).open("a") as f:
            f.write("\n" + (HERE / "reference_router.py").read_text())
        originals = {p: (scratch / p).read_text() for p in (SERVICE, SERVER, SECURITY)}
        env = dict(os.environ, PYTHONPATH=str(scratch), PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
        subprocess.run([sys.executable, "-c", "from pathlib import Path; import composite.service, tests; assert all(Path(m.__file__).is_relative_to(Path.cwd()) for m in (composite.service, tests))"], cwd=scratch, env=env, check=True)

        def run(selection):
            report = scratch / "result.xml"
            report.unlink(missing_ok=True)
            result = subprocess.run([sys.executable, "-m", "pytest", TEST, "--network=deny", "-q", "--tb=short", "-k", selection, f"--junitxml={report}"], cwd=scratch, env=env, capture_output=True, text=True, timeout=90)
            assert report.exists(), result.stdout + result.stderr
            cases = list(ET.parse(report).iter("testcase"))
            assert cases and not any(c.find("error") is not None or c.find("skipped") is not None for c in cases), result.stdout
            failed = []
            for c in cases:
                f = c.find("failure")
                if f is not None:
                    assert not any(s in f.get("message", "") for s in ("AttributeError", "TypeError", "NameError", "KeyError", "ImportError", "SyntaxError")), result.stdout
                    failed.append(c.get("name"))
            return result.returncode, len(cases), failed, result.stdout

        code, count, failures, output = run("test_http_")
        assert code == 0 and count == 68 and not failures, output
        print("REFERENCE: all 68 T047b2 cases passed", flush=True)
        for identity, edits, selected in MUTATIONS:
            for path in originals:
                (scratch / path).write_text(originals[path])
            for path, before, after in edits:
                original = (scratch / path).read_text()
                assert original.count(before) == 1, (identity, original.count(before))
                changed = original.replace(before, after)
                compile(changed, path, "exec")
                (scratch / path).write_text(changed)
            code, count, failures, output = run(selected)
            assert code == 1 and failures, f"{identity}: survived or invalid\n{output}"
            print(json.dumps(dict(mutation=identity, disposition="killed", tests=failures)), flush=True)
        print(f"{len(MUTATIONS)} killed; no survivors; scratch removed on exit", flush=True)
    for p in (ROOT / TEST, HERE / "reference_router.py", Path(__file__), HERE.parent / "T047a/reference_service.py", ROOT / SERVER, ROOT / SECURITY):
        print(f"SHA256 {p.relative_to(ROOT)}: {hashlib.sha256(p.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
