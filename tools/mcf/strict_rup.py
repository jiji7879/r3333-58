#!/usr/bin/env python3
"""Strict ordinary CAS+leaf DRAT replay for an exact augmented CNF query.

Optionally prepend an independently parsed ordinary CAS prefix.
This verifies only a CNF refutation. The configurable-normal-form reduction and
its physical-row bridge are separate obligations. No OPEN/partial trace is an
acceptable input to this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from normal_form import McfError

MAX_ARTIFACT_BYTES = 1_000_000_000


class ReplayError(McfError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size >= MAX_ARTIFACT_BYTES:
        raise ReplayError(f"artifact is not below 1 GB: {path} ({size} bytes)")
    return path.read_bytes()


def decode_binary_drat(raw: bytes, name: str) -> list[tuple[int, tuple[int, ...]]]:
    """Parse the complete stream, rejecting bad tags, truncation and literal zero."""
    records: list[tuple[int, tuple[int, ...]]] = []
    pos = 0
    while pos < len(raw):
        record_start = pos
        tag = raw[pos]
        pos += 1
        if tag not in (97, 100):
            raise ReplayError(f"{name}: invalid tag {tag} at byte {record_start}")
        lits: list[int] = []
        value = 0
        shift = 0
        partial = False
        terminated = False
        while pos < len(raw):
            byte = raw[pos]
            pos += 1
            if byte == 0:
                if partial or shift or value:
                    raise ReplayError(f"{name}: truncated literal before byte {pos - 1}")
                terminated = True
                break
            partial = True
            value |= (byte & 127) << shift
            if byte & 128:
                shift += 7
                if shift > 35:
                    raise ReplayError(f"{name}: literal overflow before byte {pos}")
            else:
                if value < 2:
                    raise ReplayError(f"{name}: literal zero before byte {pos}")
                lits.append(-(value >> 1) if value & 1 else value >> 1)
                value = 0
                shift = 0
                partial = False
        if not terminated:
            raise ReplayError(f"{name}: unterminated record at byte {record_start}")
        records.append((tag, tuple(lits)))
    return records


def encode_addition(clause: tuple[int, ...]) -> bytes:
    out = bytearray(b"a")
    for lit in clause:
        if lit == 0:
            raise ReplayError("attempted to encode literal zero")
        value = 2 * abs(lit) + int(lit < 0)
        while value >= 128:
            out.append(128 | (value & 127))
            value >>= 7
        out.append(value)
    out.append(0)
    return bytes(out)


def strict_replay(query: Path, cas: Path | None, leaf: Path, work: Path,
                  expected_query_sha256: str, checker: Path, seconds: int = 300) -> dict:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_query_sha256):
        raise ReplayError("expected query SHA-256 must be 64 lowercase hex digits")
    if seconds <= 0:
        raise ReplayError("checker seconds must be positive")
    query_raw = read_bounded(query)
    actual_query_sha = digest(query_raw)
    if actual_query_sha != expected_query_sha256:
        raise ReplayError(
            f"query SHA-256 mismatch: expected {expected_query_sha256}, got {actual_query_sha}")
    checker = checker.resolve()
    if not checker.is_file() or not os.access(checker, os.X_OK):
        raise ReplayError(f"checker is not executable: {checker}")

    # Otherwise a truncated prefix could consume bytes from the leaf and become
    # a different, seemingly valid record after concatenation.
    cas_raw = b"" if cas is None else read_bounded(cas)
    leaf_raw = read_bounded(leaf)
    if len(cas_raw) + len(leaf_raw) >= MAX_ARTIFACT_BYTES:
        raise ReplayError("joined proof is not below 1 GB")
    cas_records = decode_binary_drat(cas_raw, "CAS prefix")
    leaf_records = decode_binary_drat(leaf_raw, "leaf proof")
    records = cas_records + leaf_records
    joined_raw = cas_raw + leaf_raw
    additions = [c for tag, c in records if tag == 97]
    # drat-trim can accept an addition-free trace when the input is already
    # unit-propagation UNSAT.  An ordinary completed CaDiCaL leaf certificate
    # must nevertheless end in its derived empty clause; this also rejects a
    # record-aligned truncation that a status-only checker would miss.
    if not additions or additions[-1] != ():
        raise ReplayError("joined proof additions do not end in the empty clause")
    normalized = b"".join(encode_addition(c) for c in additions)
    if decode_binary_drat(normalized, "normalized proof") != [
            (97, c) for c in additions]:
        raise ReplayError("internal normalization round-trip mismatch")

    work.mkdir(parents=True, exist_ok=False)
    joined_path = work / "joined.drat"
    normalized_path = work / "proof-nodeletions.drat"
    log_path = work / "checker.log"
    receipt_path = work / "strict-replay.json"
    joined_path.write_bytes(joined_raw)
    normalized_path.write_bytes(normalized)
    command = [str(checker), str(query.resolve()), str(normalized_path.resolve()),
               "-i", "-U", "-W", "-t", str(seconds)]
    try:
        run = subprocess.run(command, capture_output=True, timeout=seconds + 2)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        run = None
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else b""
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
    if run is None:
        returncode = None
        raw_log = stdout + stderr + b"\nchecker wall-time limit\n"
    else:
        returncode = run.returncode
        raw_log = run.stdout + run.stderr
    log = raw_log.decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
    log_path.write_text(log)
    status_lines = [line for line in log.splitlines() if line.startswith("s ")]
    reads = [int(m.group(1)) for m in re.finditer(
        r"read (\d+) bytes from proof file", log)]
    upper = log.upper()
    checks = {
        "checker_returncode_zero": returncode == 0,
        "exactly_one_verified_status": status_lines == ["s VERIFIED"],
        "no_warning_or_error": not any(x in upper for x in (
            "WARNING", "ERROR", "NOT VERIFIED", "UNKNOWN", "DERIVATION")),
        "full_normalized_file_read_exactly_once": reads == [len(normalized)],
        "no_checker_timeout": not timed_out,
        "no_RAT_lemmas_in_core": "0 RAT lemmas in core" in log,
    }
    accepted = all(checks.values())
    receipt = {
        "schema": "k58-strict-augmented-leaf-replay/v2",
        "joined_additions_end_in_empty": True,
        "strict_accepted": accepted,
        "scope": "exact augmented CNF only; not ordinary-parent DRAT or physical-row closure",
        "query": str(query), "query_sha256": actual_query_sha,
        "expected_query_sha256": expected_query_sha256,
        "cas_sha256": digest(cas_raw), "cas_bytes": len(cas_raw),
        "leaf_proof_sha256": digest(leaf_raw), "leaf_proof_bytes": len(leaf_raw),
        "cas_records": len(cas_records), "leaf_records": len(leaf_records),
        "addition_records_retained": sum(tag == 97 for tag, _ in records),
        "deletion_records_removed": sum(tag == 100 for tag, _ in records),
        "joined_proof_sha256": digest(joined_raw), "joined_proof_bytes": len(joined_raw),
        "normalized_proof_sha256": digest(normalized), "normalized_proof_bytes": len(normalized),
        "normalization": "independently parse complete CAS and leaf binary streams; retain every valid a addition in order; remove only valid d records; canonical varint re-encoding",
        "checker": str(checker), "checker_sha256": digest(checker.read_bytes()),
        "checker_command": command, "checker_returncode": returncode,
        "status_lines": status_lines, "proof_file_bytes_read": reads,
        "checks": checks,
        "conclusion": "AUGMENTED_CNF_UNSAT_VERIFIED" if accepted else "NO_CERTIFICATE",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if not accepted:
        raise ReplayError(f"strict checker rejected proof; see {receipt_path} and {log_path}")
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--query", type=Path, required=True)
    ap.add_argument("--cas", type=Path, required=True)
    ap.add_argument("--leaf-proof", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True,
                    help="new output directory (must not already exist)")
    ap.add_argument("--expect-query-sha256", required=True)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--seconds", type=int, default=300)
    args = ap.parse_args()
    try:
        receipt = strict_replay(args.query, args.cas, args.leaf_proof, args.work,
                                args.expect_query_sha256, args.checker, args.seconds)
    except (OSError, ReplayError) as exc:
        raise SystemExit(f"REJECTED: {exc}")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
