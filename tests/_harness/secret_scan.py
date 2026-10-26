"""Secret scanner for test output (tasks.md T012; spec FR-084; constitution III).

Tests register the secrets they generated, then check captured logs, exception
text, HTTP responses to unauthorized callers and files:

* "It fails when generated tokens, UUIDs, Trojan passwords, panel tokens,
  subscription URLs or payment keys appear in captured logs, exception text,
  HTTP bodies returned to unauthorized callers, or fixture files" [tasks.md T012].
* "Panel/subscription secrets and authentication payloads MUST be excluded from
  source control, general logs, unauthorized responses and fixtures" [spec FR-084].
* "GET /sub/{token} accepts an opaque 256-bit random base64url token (43
  unpadded characters)"; "Proxy/app/metrics redact full token-bearing path and
  body" [contracts/subscription-http.md].

A value is never revealed: findings, messages and reprs show only its kind and
its fingerprint, the first 12 hex characters of its SHA-256 digest. The module
never logs or prints, and every public ``check_*`` method sets
``__tracebackhide__`` so pytest leaves its frame out of failure reports.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
import base64
import hashlib
import logging
import os
import pathlib
import re
import traceback
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tests._harness.fake_payments import FakePaymentMethod
    from tests._harness.fake_threexui import FakeThreeXUIPanel
    from tests._harness.fixtures import CompositeFixture


_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_SUB_URL_PATTERN = re.compile(
    r"(?:/|%2[Ff])sub(?:/|%2[Ff])([A-Za-z0-9_-]{43})(?![A-Za-z0-9_-])"
)
_B64_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/_-]{16,}")


def fingerprint(value: str) -> str:
    """Return a 12-hex-character SHA-256 fingerprint of the value."""
    return hashlib.sha256(value.encode("utf-8", "surrogateescape")).hexdigest()[:12]


@dataclass(frozen=True)
class SecretFinding:
    kind: str
    fingerprint: str
    source: str
    decodings: int


class SecretLeak(AssertionError):
    findings: tuple[SecretFinding, ...]

    def __init__(self, findings: Sequence[SecretFinding]) -> None:
        self.findings = tuple(findings)
        lines = [
            f"{f.kind} {f.fingerprint} in {f.source}"
            + (f", base64 depth {f.decodings}" if f.decodings > 0 else "")
            for f in self.findings
        ]
        msg = "secrets found:\n" + "\n".join(lines) if lines else "secrets found:"
        super().__init__(msg)


@dataclass(frozen=True)
class _RegisteredSecret:
    kind: str
    value: str = field(repr=False)
    fingerprint: str
    is_uuid: bool
    uuid_canonical: str = field(default="", repr=False)
    uuid_no_hyphens: str = field(default="", repr=False)


def _decode_text(text: str) -> set[str]:
    decoded_texts = set()
    for m in _B64_CANDIDATE_RE.finditer(text):
        match_str = m.group(0)
        for offset in (0, 1, 2, 3):
            candidate = match_str[offset:]
            if len(candidate) % 4 == 1:
                candidate = candidate[:-1]
            if len(candidate) < 2:
                continue
            cand_std = candidate.replace("-", "+").replace("_", "/")
            pad = (-len(cand_std)) % 4
            if pad:
                cand_std = cand_std + ("=" * pad)
            try:
                raw = base64.b64decode(cand_std, validate=True)
                decoded_str = raw.decode("utf-8", "surrogateescape")
                decoded_texts.add(decoded_str)
            except Exception:
                pass
    return decoded_texts


class SecretScan:
    def __init__(self) -> None:
        self._registered: list[_RegisteredSecret] = []
        self._values: dict[str, _RegisteredSecret] = {}

    def __repr__(self) -> str:
        return f"SecretScan(registered={len(self._registered)})"

    @property
    def registered(self) -> tuple[tuple[str, str], ...]:
        return tuple((s.kind, s.fingerprint) for s in self._registered)

    def add(self, kind: str, value: str) -> None:
        if not isinstance(kind, str):
            raise TypeError(f"kind must be a str, got {type(kind).__name__}")
        if kind == "":
            raise ValueError("kind must not be empty")
        if not isinstance(value, str):
            raise TypeError(f"value must be a str, got {type(value).__name__}")
        if len(value) < 16:
            raise ValueError(
                f"value must be at least 16 characters, got length {len(value)}"
            )

        if value in self._values:
            return

        fp = fingerprint(value)
        is_uuid = bool(_UUID_RE.fullmatch(value))
        uuid_canonical = value.lower() if is_uuid else ""
        uuid_no_hyphens = uuid_canonical.replace("-", "") if is_uuid else ""

        secret = _RegisteredSecret(
            kind=kind,
            value=value,
            fingerprint=fp,
            is_uuid=is_uuid,
            uuid_canonical=uuid_canonical,
            uuid_no_hyphens=uuid_no_hyphens,
        )
        self._registered.append(secret)
        self._values[value] = secret

    def add_fixture(self, fixture: "CompositeFixture") -> None:
        for panel in fixture.panels:
            self.add("panel token", panel.api_token)
        for inbound in fixture.inbounds:
            if inbound.reality_private_key:
                self.add("REALITY private key", inbound.reality_private_key)
        for subscription in fixture.subscriptions:
            self.add("subscription token", subscription.url_token)
            for credential in subscription.credentials:
                kind = (
                    "client UUID"
                    if credential.secret_kind == "uuid"
                    else "Trojan password"
                )
                self.add(kind, credential.secret)

    def add_panel(self, panel: "FakeThreeXUIPanel") -> None:
        for token in panel.tokens.values():
            self.add("panel token", token)

    def add_payment_method(self, method: "FakePaymentMethod") -> None:
        self.add("payment key", method.api_key)

    def find(self, text: str | bytes, *, source: str) -> tuple[SecretFinding, ...]:
        if not isinstance(source, str):
            raise TypeError(f"source must be a str, got {type(source).__name__}")
        if source == "":
            raise ValueError("source must not be empty")

        if isinstance(text, bytes):
            decoded_text = text.decode("utf-8", "surrogateescape")
        elif isinstance(text, str):
            decoded_text = text
        else:
            raise TypeError(f"text must be str or bytes, got {type(text).__name__}")

        found_registered: dict[_RegisteredSecret, int] = {}
        found_sub_urls: dict[str, int] = {}

        current_level_texts = {decoded_text}

        for depth in range(4):
            if not current_level_texts:
                break

            for t in current_level_texts:
                t_lower = t.lower()
                for s in self._registered:
                    if s not in found_registered:
                        matched = (
                            (s.uuid_canonical in t_lower or s.uuid_no_hyphens in t_lower)
                            if s.is_uuid
                            else (s.value in t)
                        )
                        if matched:
                            found_registered[s] = depth

                for match in _SUB_URL_PATTERN.finditer(t):
                    token = match.group(1)
                    if token not in self._values:
                        if token not in found_sub_urls:
                            found_sub_urls[token] = depth

            if depth < 3:
                next_level_texts = set()
                for t in current_level_texts:
                    next_level_texts.update(_decode_text(t))
                current_level_texts = next_level_texts

        findings: list[SecretFinding] = []
        for s in self._registered:
            if s in found_registered:
                findings.append(
                    SecretFinding(s.kind, s.fingerprint, source, found_registered[s])
                )

        sub_findings: list[SecretFinding] = []
        for token, depth in found_sub_urls.items():
            sub_findings.append(
                SecretFinding("subscription URL", fingerprint(token), source, depth)
            )
        sub_findings.sort(key=lambda f: f.fingerprint)

        findings.extend(sub_findings)
        return tuple(findings)

    def check_text(self, text: str | bytes, *, source: str) -> None:
        __tracebackhide__ = True
        findings = self.find(text, source=source)
        if findings:
            raise SecretLeak(findings)

    def check_logs(self, records: Iterable[logging.LogRecord]) -> None:
        __tracebackhide__ = True
        if isinstance(records, (str, bytes)) or not isinstance(records, Iterable):
            raise TypeError("records must be an iterable of LogRecord")

        findings: list[SecretFinding] = []
        for i, record in enumerate(records):
            if not isinstance(record, logging.LogRecord):
                raise TypeError(
                    f"record must be a logging.LogRecord, got {type(record).__name__}"
                )

            parts = []
            try:
                parts.append(record.getMessage())
            except Exception:
                pass

            if (
                isinstance(record.exc_info, tuple)
                and len(record.exc_info) > 1
                and record.exc_info[1] is not None
            ):
                parts.append("".join(traceback.format_exception(record.exc_info[1])))

            for v in vars(record).values():
                parts.append(repr(v))

            record_text = "\n".join(parts)
            source = f"log record {i} ({record.name})"
            findings.extend(self.find(record_text, source=source))

        if findings:
            raise SecretLeak(findings)

    def check_exception(self, exc: BaseException) -> None:
        __tracebackhide__ = True
        if not isinstance(exc, BaseException):
            raise TypeError(f"exc must be a BaseException, got {type(exc).__name__}")

        parts = []
        try:
            parts.append(str(exc))
        except Exception:
            pass

        parts.append(repr(exc))
        parts.append("".join(traceback.format_exception(exc)))

        text = "\n".join(parts)
        source = f"exception {type(exc).__name__}"
        findings = self.find(text, source=source)
        if findings:
            raise SecretLeak(findings)

    def check_http(
        self,
        body: str | bytes,
        *,
        headers: Any = None,
        source: str = "HTTP response",
    ) -> None:
        __tracebackhide__ = True
        if not isinstance(source, str):
            raise TypeError(f"source must be a str, got {type(source).__name__}")
        if source == "":
            raise ValueError("source must not be empty")

        if not isinstance(body, (str, bytes)):
            raise TypeError(f"body must be str or bytes, got {type(body).__name__}")

        header_list: list[tuple[str, str]] = []
        if headers is not None:
            if hasattr(headers, "items"):
                items = headers.items()
            elif isinstance(headers, (str, bytes)):
                raise TypeError("headers must not be str or bytes")
            elif isinstance(headers, Iterable):
                items = headers
            else:
                raise TypeError(
                    "headers must be None, have .items(), or be an iterable of pairs"
                )

            for item in items:
                if not isinstance(item, (tuple, list)) or len(item) != 2:
                    raise TypeError("each header item must be a (name, value) pair")
                name, val = item
                if isinstance(name, bytes):
                    name_str = name.decode("utf-8", "surrogateescape")
                elif isinstance(name, str):
                    name_str = name
                else:
                    raise TypeError(
                        f"header name must be str or bytes, got {type(name).__name__}"
                    )

                if isinstance(val, bytes):
                    val_str = val.decode("utf-8", "surrogateescape")
                elif isinstance(val, str):
                    val_str = val
                else:
                    raise TypeError(
                        f"header value must be str or bytes, got {type(val).__name__}"
                    )

                header_list.append((name_str, val_str))

        findings: list[SecretFinding] = []
        findings.extend(self.find(body, source=f"{source} body"))
        for name_str, val_str in header_list:
            findings.extend(
                self.find(
                    f"{name_str}: {val_str}", source=f"{source} header {name_str}"
                )
            )

        if findings:
            raise SecretLeak(findings)

    def check_files(self, *paths: str | os.PathLike[str]) -> None:
        __tracebackhide__ = True
        validated_paths: list[pathlib.Path] = []
        for p in paths:
            path_obj = pathlib.Path(p)
            if path_obj.is_symlink():
                raise ValueError(f"Path is a symlink: {p}")
            if not path_obj.exists():
                raise FileNotFoundError(f"Path does not exist: {p}")
            validated_paths.append(path_obj)

        findings: list[SecretFinding] = []
        for path_obj in validated_paths:
            if path_obj.is_dir():
                entries: list[tuple[str, pathlib.Path, bool]] = []
                for cur_root, dirnames, filenames in os.walk(
                    path_obj, followlinks=False
                ):
                    cur_path = pathlib.Path(cur_root)
                    dirnames[:] = [
                        d for d in dirnames if not (cur_path / d).is_symlink()
                    ]
                    for d in dirnames:
                        sub = cur_path / d
                        rel = sub.relative_to(path_obj).as_posix()
                        entries.append((rel, sub, False))
                    for f in filenames:
                        sub = cur_path / f
                        if sub.is_symlink():
                            continue
                        rel = sub.relative_to(path_obj).as_posix()
                        entries.append((rel, sub, sub.is_file()))

                entries.sort(key=lambda x: x[0])
                for rel_name, full_path, is_reg_file in entries:
                    findings.extend(self.find(rel_name, source=f"file name {full_path}"))
                    if is_reg_file:
                        findings.extend(
                            self.find(full_path.read_bytes(), source=f"file {full_path}")
                        )
            else:
                findings.extend(self.find(path_obj.name, source=f"file name {path_obj}"))
                if path_obj.is_file():
                    findings.extend(
                        self.find(path_obj.read_bytes(), source=f"file {path_obj}")
                    )

        if findings:
            raise SecretLeak(findings)
