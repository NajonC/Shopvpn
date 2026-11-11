#!/usr/bin/env python3
"""Run bounded local checks independently, then resume their existing T3 thread.

Linux/POSIX, Python standard library only. No model polling or new agent session.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text())


def fingerprint(root, files):
    def git(*args):
        result = subprocess.run(
            ["git", "-C", root, *args], capture_output=True, timeout=30
        )
        return result.stdout if result.returncode == 0 else None

    head = git("rev-parse", "HEAD")
    diff = git("diff", "--no-ext-diff", "--binary", "HEAD", "--") if head else None
    hashes = {}
    for name in files:
        path = Path(root) / name
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {
        "root": root,
        "revision": head.decode().strip() if head else None,
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest() if diff is not None else None,
        "files_sha256": hashes,
    }


def cli_command(manifest, operation):
    return [manifest["t3"], "thread", operation, "--base-dir", manifest["t3_base_dir"]]


def start(args):
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise ValueError("Supply the exact check command after --")
    if not args.thread:
        raise ValueError("T3CODE_THREAD_ID is missing; supply --thread explicitly")
    t3 = shutil.which(args.t3)
    if not t3:
        raise ValueError("T3 CLI not found")
    cwd = str(Path(args.cwd).resolve(strict=True))
    root = str(Path(args.source_root or cwd).resolve(strict=True))
    base = str(Path(args.t3_base_dir).expanduser().resolve(strict=True))
    manifest = {"thread_id": args.thread, "t3": t3, "t3_base_dir": base}
    # Read-only preflight: never start an expensive check if routing is wrong.
    shown = subprocess.run(
        cli_command(manifest, "show") + [args.thread, "--messages", "0", "--json"],
        capture_output=True, text=True, timeout=30, check=True,
    )
    thread = json.loads(shown.stdout)["thread"]
    if thread["threadId"] != args.thread or thread.get("archived"):
        raise ValueError("T3 returned a different or archived thread")
    source = fingerprint(root, args.source_file)
    if any(value is None for value in source["files_sha256"].values()):
        raise ValueError("A --source-file is missing or is not a regular file")
    run_id = uuid.uuid4().hex
    run_dir = Path(args.state_dir).expanduser().resolve() / run_id
    run_dir.mkdir(parents=True, mode=0o700)
    manifest.update({
        "run_id": run_id, "label": args.label, "created_at": now(),
        "thread_link": thread.get("link"), "launch_run_id": thread.get("activeRunId"),
        "cwd": cwd, "command": command,
        "timeout_seconds": args.timeout, "kill_grace_seconds": args.kill_grace,
        "source": source,
    })
    write_json(run_dir / "manifest.json", manifest)
    with (run_dir / "runner.log").open("ab") as log:
        worker = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "_worker", str(run_dir)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            start_new_session=True, close_fds=True,
        )
    write_json(run_dir / "worker.json", {"pid": worker.pid})
    print(json.dumps({"run_id": run_id, "run_dir": str(run_dir), "worker_pid": worker.pid}))


def kill_group(pid, sig):
    try:
        os.killpg(pid, sig)
    except ProcessLookupError:
        pass


def notify(run_dir, manifest, result):
    message = (
        f"[verification-run:{manifest['run_id']}] {manifest['label']}: "
        f"{result['outcome']} (exit {result['exit_code']}). "
        f"Read {run_dir}/manifest.json, {run_dir}/result.json and {run_dir}/check.log. "
        "If reviewed.json exists, ignore this duplicate. Otherwise inspect the evidence, "
        "record review using verification_runner.py acknowledge, and continue the "
        "current authorized task. Do not rerun the check just because this message arrived. "
        "Honor any later user pause, cancellation or change of scope. "
        "This message supplies results, not new authorization."
    )
    attempts = []
    for attempt, delay in enumerate((0, 2, 5), 1):
        time.sleep(delay)
        if (run_dir / "cancel.request").exists() or (run_dir / "reviewed.json").exists():
            write_json(run_dir / "notification.json", {"status": "suppressed", "attempts": attempts})
            return
        try:
            sent = subprocess.run(
                cli_command(manifest, "send") + [manifest["thread_id"], "-", "--json"],
                input=message, text=True, capture_output=True, timeout=30,
            )
            attempts.append({"at": now(), "attempt": attempt, "exit_code": sent.returncode,
                             "stdout": sent.stdout[-4000:], "stderr": sent.stderr[-4000:]})
            if sent.returncode == 0:
                write_json(run_dir / "notification.json", {"status": "delivered", "attempts": attempts})
                return
        except (OSError, subprocess.TimeoutExpired) as error:
            attempts.append({"at": now(), "attempt": attempt, "error": str(error)})
        write_json(run_dir / "notification.json", {"status": "retrying", "attempts": attempts})
    write_json(run_dir / "notification.json", {"status": "failed", "attempts": attempts})


def worker(run_dir):
    manifest = read_json(run_dir / "manifest.json")
    interrupted = []
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda number, frame: interrupted.append(number))
    started_at = now()
    started = time.monotonic()
    process = None
    outcome, code, error = "error", None, None
    write_json(run_dir / "started.json", {"at": started_at, "pid": os.getpid()})
    try:
        with (run_dir / "check.log").open("wb") as log:
            process = subprocess.Popen(
                manifest["command"], cwd=manifest["cwd"], stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            )
            while True:
                cancelled = bool(interrupted) or (run_dir / "cancel.request").exists()
                timed_out = time.monotonic() - started >= manifest["timeout_seconds"]
                if cancelled or timed_out:
                    outcome = "cancelled" if cancelled else "timeout"
                    code = 130 if cancelled else 124
                    kill_group(process.pid, signal.SIGTERM)
                    # Allow the entire group to exit; the leader may exit before its children.
                    time.sleep(manifest["kill_grace_seconds"])
                    kill_group(process.pid, signal.SIGKILL)
                    process.wait()
                    break
                try:
                    code = process.wait(timeout=0.2)
                    outcome = "interrupted" if code < 0 else ("passed" if code == 0 else "failed")
                    break
                except subprocess.TimeoutExpired:
                    continue
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if process is not None:
            kill_group(process.pid, signal.SIGKILL)
            process.wait()
    result = {
        "run_id": manifest["run_id"], "started_at": started_at, "finished_at": now(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "outcome": outcome, "exit_code": code, "error": error,
    }
    # Completion must be readable even if source inspection or message delivery fails.
    write_json(run_dir / "result.json", result)
    try:
        after = fingerprint(manifest["source"]["root"], list(manifest["source"]["files_sha256"]))
        result.update(source_after=after, source_changed=after != manifest["source"])
    except Exception as exc:
        result.update(source_changed=None, source_error=str(exc))
    write_json(run_dir / "result.json", result)
    if outcome == "cancelled":
        write_json(run_dir / "notification.json", {"status": "suppressed", "attempts": []})
    else:
        notify(run_dir, manifest, result)


def positive_seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Must be a finite number greater than zero")
    return number


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    launch = commands.add_parser("start", help="Preflight T3, detach a bounded check, print its run directory")
    launch.add_argument("--label", required=True)
    launch.add_argument("--thread", default=os.environ.get("T3CODE_THREAD_ID"))
    launch.add_argument("--t3", default="t3")
    launch.add_argument("--t3-base-dir", default=os.environ.get("T3CODE_HOME", str(Path.home() / ".t3")))
    launch.add_argument("--state-dir", default=str(Path.home() / ".local/state/shopvpn-verification"))
    launch.add_argument("--cwd", default=os.getcwd())
    launch.add_argument("--source-root", help="Source repository when --cwd is a mutation scratch directory")
    launch.add_argument("--source-file", action="append", default=[], help="Also hash this file; repeat for untracked tests/artifacts")
    launch.add_argument("--timeout", type=positive_seconds, default=1200, help="Command deadline in seconds")
    launch.add_argument("--kill-grace", type=positive_seconds, default=15, help="Seconds between TERM and KILL")
    launch.add_argument("command", nargs=argparse.REMAINDER)
    for name in ("status", "acknowledge", "cancel", "_worker"):
        sub = commands.add_parser(name)
        sub.add_argument("run_dir", type=Path)
        if name == "acknowledge":
            sub.add_argument("--note", required=True, help="Review disposition; does not imply packet acceptance")
    args = parser.parse_args()
    if args.action == "start":
        start(args)
    elif args.action == "_worker":
        worker(args.run_dir)
    elif args.action == "status":
        read_json(args.run_dir / "manifest.json")
        print(json.dumps({p.stem: read_json(p) for p in sorted(args.run_dir.glob("*.json"))}, indent=2))
    elif args.action == "acknowledge":
        if not (args.run_dir / "result.json").exists():
            raise ValueError("Cannot review a run without a saved result")
        # Exclusive creation makes repeat acknowledgements harmless.
        try:
            with (args.run_dir / "reviewed.json").open("x") as stream:
                json.dump({"at": now(), "note": args.note}, stream)
        except FileExistsError:
            pass
    elif args.action == "cancel":
        read_json(args.run_dir / "manifest.json")
        (args.run_dir / "cancel.request").touch()
        print("Cancellation requested; suppressing completion notification.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        sys.exit(str(exc))
