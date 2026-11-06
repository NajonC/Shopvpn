"""Reproduce T047b1 reference/mutations in an isolated source-only scratch copy.

No production implementation is installed. The inherited Telegram reference is
supporting code for the one cross-domain test; T048 must rerun both campaigns
against its actual implementation. No real configuration/data is exported.
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
    ("omit_tenant", SERVICE, 'admin.get("tenant") != ""', 'False', "test_web_signed_tenant"),
    ("missing_tenant_is_main", SERVICE, 'admin.get("tenant") != ""', 'bool(admin.get("tenant"))', "test_web_adapter_refuses"),
    ("accept_main_alias", SERVICE, 'admin.get("tenant") != ""', 'admin.get("tenant") not in ("", "main")', "test_web_adapter_refuses"),
    ("omit_role", SERVICE, 'or admin.get("role") != "owner"', 'or False', "test_web_database_staff"),
    ("omit_mobile", SERVICE, 'or "mobile_token_id" in admin', 'or False', "test_web_adapter_refuses"),
    ("coerce_actor", SERVICE, 'type(admin.get("id")) is not int', 'not isinstance(admin.get("id"), (int, str))', "test_web_adapter_refuses"),
    ("coerce_mapping", SERVICE, 'type(main_owner_web_admin_id) is not int', 'not isinstance(main_owner_web_admin_id, int)', "test_web_mapping"),
    ("omit_mapping", SERVICE, 'or admin["id"] != main_owner_web_admin_id', 'or False', "test_web_telegram_owner_number"),
    ("telegram_id_fallback", SERVICE, 'or admin["id"] != main_owner_web_admin_id', 'or (admin["id"] != main_owner_web_admin_id and admin["id"] != 2)', "test_web_telegram_owner_number"),
    ("wrong_domain", SERVICE, 'Principal("web_admin", admin["id"]', 'Principal("telegram", admin["id"]', "test_web_explicit_owner"),
    ("wrong_interface", SERVICE, 'main_installation_id, "owner", "web")', 'main_installation_id, "owner", "telegram")', "test_web_explicit_owner"),
    ("wrong_role", SERVICE, 'main_installation_id, "owner", "web")', 'main_installation_id, "customer", "web")', "test_web_explicit_owner"),
    ("hardcode_web_actor", SERVICE, 'Principal("web_admin", admin["id"],', 'Principal("web_admin", 1,', "test_web_explicit_owner"),
    ("hardcode_installation", SERVICE, 'Principal("web_admin", admin["id"], main_installation_id,', 'Principal("web_admin", admin["id"], "synthetic-main-installation",', "test_web_explicit_owner"),
    ("reject_alternative_owner", SERVICE, 'or admin["id"] != main_owner_web_admin_id', 'or admin["id"] != 1 or admin["id"] != main_owner_web_admin_id', "test_web_explicit_owner"),
    ("leak_web_id", SERVICE, '# A trusted caller supplies the authenticated admin and explicit web binding.', '# A trusted caller supplies the authenticated admin and explicit web binding.\n    if admin["id"] == 2:\n        raise AuthorityError("forbidden:2")', "test_web_telegram_owner_number"),
    ("trust_query_tenant", SERVER, 'tenant = resolve_tenant_by_slug(payload.get("b", ""))', 'tenant = resolve_tenant_by_slug(request.query_params.get("b", ""))', "test_web_signed_tenant"),
    ("trust_signed_role", SERVER, '"role": admin["role"],\n        "permissions": (await asyncio.to_thread(tenant.db.get_web_admin_permissions, admin)),\n        "tenant": tenant.slug,\n        "reseller_profile": reseller_profile,', '"role": payload["r"],\n        "permissions": (await asyncio.to_thread(tenant.db.get_web_admin_permissions, admin)),\n        "tenant": tenant.slug,\n        "reseller_profile": reseller_profile,', "test_web_database_staff"),
    ("omit_session_signature", SECURITY, 'if not hmac.compare_digest(expected_sig, sig):', 'if False:', "test_web_invalid_session_never_reaches_principal_or_effect[tampered]"),
    ("omit_session_expiry", SECURITY, 'if payload.get("exp", 0) < time.time():', 'if False:', "test_web_invalid_session_never_reaches_principal_or_effect[expired]"),
    ("allow_inactive_session", SERVER, 'if not admin or not admin["is_active"]:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")', 'if not admin:\n        raise HTTPException(401, "حساب کاربری غیرفعال یا حذف شده است.")', "test_web_invalid_session_never_reaches_principal_or_effect[inactive]"),
]


def main():
    with tempfile.TemporaryDirectory(prefix="t047b1-review-") as directory:
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
            (HERE.parent / "T047a/reference_service.py").read_text() + "\n" + (HERE / "reference_web.py").read_text())
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

        code, count, failures, output = run("test_web_")
        assert code == 0 and count == 22 and not failures, output
        print("REFERENCE: all 22 T047b1 cases passed", flush=True)
        code, count, failures, output = run("not test_web_")
        assert code == 0 and count == 18 and not failures, output
        print("SUPPORTING T047a reference: all 18 cases passed", flush=True)
        for identity, path, before, after, selected in MUTATIONS:
            original = originals[path]
            assert original.count(before) == 1, (identity, original.count(before))
            changed = original.replace(before, after)
            compile(changed, path, "exec")
            (scratch / path).write_text(changed)
            code, count, failures, output = run(selected)
            assert code == 1 and failures, f"{identity}: survived or invalid\n{output}"
            print(json.dumps(dict(mutation=identity, disposition="killed", tests=failures)), flush=True)
            (scratch / path).write_text(original)
        print(f"{len(MUTATIONS)} killed; no survivors; scratch removed on exit", flush=True)
    for p in (ROOT / TEST, HERE / "reference_web.py", Path(__file__), HERE.parent / "T047a/reference_service.py", ROOT / SERVER, ROOT / SECURITY):
        print(f"SHA256 {p.relative_to(ROOT)}: {hashlib.sha256(p.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
