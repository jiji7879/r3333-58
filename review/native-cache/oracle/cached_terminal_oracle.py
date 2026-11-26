#!/usr/bin/env python3
"""Independent test oracle for K58 cached native receipts.

This is deliberately a test fixture, not a production patch. It turns every
failure into an explicitly nonterminal INVALID_CACHE decision so tests can
assert security properties without exceptions hiding the resulting status.
Only drat-trim is executed; no SAT solver is called by this module.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

TERMINAL = {"UNSAT_BASE", "SAT_BASE"}
PENDING = "AUGMENTED_UNSAT_PENDING_BASE"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARTIFACT = 64 << 20
MAX_CHECKER_LOG = 1 << 20


class Reject(ValueError):
    """A cached receipt does not establish its claimed state."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise Reject("duplicate-json-key", key)
        out[key] = value
    return out


def _constant(value: str) -> None:
    raise Reject("nonstandard-json-number", value)


def load_json(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_constant)
    except Reject:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Reject("invalid-json", str(exc)) from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_dimacs(data: bytes) -> tuple[int, list[list[int]]]:
    """Small independent DIMACS reader, including unused declared variables."""
    header: tuple[int, int] | None = None
    clauses: list[list[int]] = []
    pending: list[int] = []
    for raw in data.splitlines():
        line = raw.strip()
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            fields = line.split()
            if header is not None or len(fields) != 4 or fields[:2] != [b"p", b"cnf"]:
                raise Reject("invalid-dimacs-header")
            try:
                header = (int(fields[2]), int(fields[3]))
            except ValueError as exc:
                raise Reject("invalid-dimacs-header") from exc
            if min(header) < 0:
                raise Reject("invalid-dimacs-header")
            continue
        if header is None:
            raise Reject("clause-before-header")
        try:
            values = [int(x) for x in line.split()]
        except ValueError as exc:
            raise Reject("invalid-dimacs-literal") from exc
        for value in values:
            if value:
                pending.append(value)
            else:
                clauses.append(pending)
                pending = []
    if header is None or pending or len(clauses) != header[1]:
        raise Reject("dimacs-count-or-termination")
    nv = header[0]
    if max((abs(x) for clause in clauses for x in clause), default=0) > nv:
        raise Reject("literal-exceeds-variable-count")
    return nv, clauses


def _digest(value: Any, field: str) -> str:
    if type(value) is not str or HEX64.fullmatch(value) is None:
        raise Reject("invalid-digest-field", field)
    return value


def _binding(receipt: Any, expected: Any, parent: bytes, plain: bytes, query: bytes) -> dict[str, Any]:
    if type(receipt) is not dict or type(expected) is not dict:
        raise Reject("receipt-not-object")
    # Type-sensitive JSON comparison prevents True from matching integer 1.
    for key, value in expected.items():
        if key not in receipt or canonical_json(receipt[key]) != canonical_json(value):
            raise Reject("wrong-parent-query-or-case", key)
    for key, data in (("parent_sha256", parent), ("plain_sha256", plain),
                      ("query_sha256", query)):
        if expected.get(key) != sha(data):
            raise Reject("expected-formula-binding", key)
        _digest(receipt.get(key), key)
        if receipt[key] != sha(data):
            raise Reject("wrong-parent-query-or-case", key)
    for key in ("id", "node", "mode"):
        if type(receipt.get(key)) is not str or not receipt[key]:
            raise Reject("invalid-case-field", key)
    for key in ("cap", "cuts", "pair_cuts"):
        if type(receipt.get(key)) is not int or receipt[key] < 0:
            raise Reject("invalid-case-field", key)
    cube = receipt.get("cube")
    if type(cube) is not list or any(type(x) is not int or x == 0 for x in cube):
        raise Reject("invalid-case-field", "cube")
    if len({abs(x) for x in cube}) != len(cube):
        raise Reject("invalid-case-field", "cube")
    return receipt


def _sibling(receipt_path: Path, name: Any, field: str) -> Path:
    if type(name) is not str or not name or Path(name).name != name:
        raise Reject("unsafe-artifact-name", field)
    path = receipt_path.parent / name
    if path.is_symlink() or not path.is_file() or path.parent.resolve() != receipt_path.parent.resolve():
        raise Reject("missing-or-unsafe-artifact", field)
    return path


def _gunzip(path: Path, maximum: int = MAX_ARTIFACT) -> bytes:
    chunks: list[bytes] = []
    total = 0
    try:
        with path.open("rb") as raw, gzip.GzipFile(fileobj=raw, mode="rb") as stream:
            while True:
                chunk = stream.read(min(1 << 20, maximum - total + 1))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > maximum:
                    raise Reject("artifact-too-large", path.name)
    except Reject:
        raise
    except (OSError, EOFError) as exc:
        raise Reject("corrupt-or-truncated-gzip", str(exc)) from exc
    return b"".join(chunks)


def _replay(checker: Path, formula: bytes, proof: bytes, work: Path) -> None:
    """Replay binary DRAT with no warning suppression and an exact verdict."""
    if not proof:
        raise Reject("empty-proof")
    if not checker.is_file() or not os.access(checker, os.X_OK):
        raise Reject("checker-unavailable")
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cached-oracle-", dir=work) as tmp:
        folder = Path(tmp)
        cnf, drat, log = folder / "target.cnf", folder / "proof.drat", folder / "checker.log"
        cnf.write_bytes(formula)
        drat.write_bytes(proof)
        try:
            with log.open("xb") as stream:
                job = subprocess.run(
                    [str(checker), str(cnf), str(drat), "-i", "-t", "10"],
                    stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                    timeout=12, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Reject("checker-inconclusive", str(exc)) from exc
        if log.stat().st_size > MAX_CHECKER_LOG:
            raise Reject("checker-log-too-large")
        output = log.read_bytes()
        verdicts = [line.strip() for line in output.replace(b"\r", b"\n").splitlines()]
        if job.returncode != 0 or b"s VERIFIED" not in verdicts:
            raise Reject("proof-replay-failed", "no exact s VERIFIED verdict")


def _model(plain: bytes, data: bytes, cube: list[int]) -> None:
    nv, clauses = read_dimacs(plain)
    model = load_json(data)
    if type(model) is not list or len(model) != nv:
        raise Reject("incomplete-model", f"expected exactly {nv} literals")
    if any(type(x) is not int or not 0 < abs(x) <= nv for x in model):
        raise Reject("invalid-model-literal")
    if {abs(x) for x in model} != set(range(1, nv + 1)):
        raise Reject("incomplete-or-duplicate-model")
    assigned = set(model)
    if any(-x in assigned for x in assigned):
        raise Reject("contradictory-model")
    if any(x not in assigned for x in cube):
        raise Reject("model-violates-cube")
    for index, clause in enumerate(clauses, 1):
        if not any(x in assigned for x in clause):
            raise Reject("model-fails-physical-parent", index)


def adjudicate(receipt_path: Path, expected: dict[str, Any], *, parent: bytes,
               plain: bytes, query: bytes, checker: Path, work: Path) -> dict[str, Any]:
    """Return cache_valid/status/terminal/reason; terminal is never guessed."""
    try:
        if not receipt_path.is_file() or receipt_path.is_symlink():
            raise Reject("missing-receipt")
        receipt = _binding(load_json(receipt_path.read_bytes()), expected, parent, plain, query)
        status = receipt.get("status")
        if status == "OPEN":
            return {"cache_valid": True, "status": "OPEN", "terminal": False,
                    "reason": "open-is-not-closure"}
        if status == "SAT_BASE":
            path = _sibling(receipt_path, receipt.get("model"), "model")
            data = _gunzip(path)
            if sha(data) != _digest(receipt.get("model_sha256"), "model_sha256"):
                raise Reject("model-hash-mismatch")
            _model(plain, data, receipt["cube"])
            return {"cache_valid": True, "status": "SAT_BASE", "terminal": True,
                    "reason": "complete-physical-model-verified"}
        if status in ("UNSAT_BASE", PENDING):
            path = _sibling(receipt_path, receipt.get("proof"), "proof")
            proof = _gunzip(path)
            if sha(proof) != _digest(receipt.get("proof_sha256"), "proof_sha256"):
                raise Reject("proof-hash-mismatch")
            # Never upgrade pending to base closure, even if the proof would
            # happen to verify against plain as well.
            target = plain if status == "UNSAT_BASE" else query
            _replay(checker, target, proof, work)
            return {"cache_valid": True, "status": status,
                    "terminal": status == "UNSAT_BASE",
                    "reason": "plain-proof-verified" if status == "UNSAT_BASE"
                              else "augmented-only-remains-pending"}
        # Raw UNSAT/SAT, UNKNOWN, TIMEOUT and every unknown status are not
        # native terminal receipts and cannot acquire terminal meaning here.
        raise Reject("nonterminal-or-unrecognized-status", repr(status))
    except (Reject, OSError) as exc:
        code = exc.args[0] if isinstance(exc, Reject) and exc.args else "io-error"
        return {"cache_valid": False, "status": "INVALID_CACHE", "terminal": False,
                "reason": code, "detail": [str(x) for x in exc.args[1:]]}
