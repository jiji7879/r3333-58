#!/usr/bin/env python3
"""Deletion-only binary DRAT normalisation and fail-closed strict replay."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from normal_form import McfError, digest, file_digest, require


def normalize_additions(source, target):
    """Copy every addition command byte-for-byte; drop only deletion commands."""
    raw = Path(source).read_bytes()
    output = bytearray()
    counts = {op: {"commands": 0, "literals": 0, "bytes": 0} for op in (b"a", b"d")}
    empty_additions = 0
    pos = 0
    while pos < len(raw):
        op = raw[pos:pos + 1]
        require(op in counts, f"bad binary DRAT opcode at byte {pos}")
        end = pos + 1
        literals = 0
        while True:
            require(end < len(raw), "truncated binary DRAT varint/command")
            value = 0
            terminated = False
            for shift in range(0, 35, 7):
                require(end < len(raw), "truncated binary DRAT varint")
                byte = raw[end]
                end += 1
                value |= (byte & 127) << shift
                if byte < 128:
                    terminated = True
                    break
            require(terminated, "overlong binary DRAT varint")
            if value == 0:
                break
            literals += 1
        command = raw[pos:end]
        counts[op]["commands"] += 1
        counts[op]["literals"] += literals
        counts[op]["bytes"] += len(command)
        if op == b"a":
            output.extend(command)
            empty_additions += literals == 0
        pos = end
    require(pos == len(raw), "binary DRAT parser did not consume complete stream")
    require(counts[b"a"]["bytes"] + counts[b"d"]["bytes"] == len(raw),
            "binary DRAT byte accounting mismatch")
    Path(target).write_bytes(output)
    receipt = {
        "schema": "k58-mcf-deletion-only-normalization/v1",
        "input_bytes": len(raw), "input_sha256": digest(raw),
        "output_bytes": len(output), "output_sha256": digest(output),
        "commands": {key.decode(): value for key, value in counts.items()},
        "empty_additions": empty_additions,
        "complete_parse": True,
        "transformation": "drop d commands; copy a commands byte-for-byte including order",
    }
    require(receipt["output_bytes"] == counts[b"a"]["bytes"],
            "normalization output is not exactly its addition bytes")
    return receipt


def _attempt(checker, cnf, proof, seconds):
    command = [str(checker), str(cnf), str(proof), "-i", "-U", "-W", "-t", str(seconds)]
    try:
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=seconds + 2, check=False)
        output = run.stdout.decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
        returncode = run.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode("latin1")
        returncode = None
        timed_out = True
    status = [line for line in output.splitlines() if line.startswith("s ")]
    reads = [int(match.group(1)) for match in
             re.finditer(r"read (\d+) bytes from proof file", output)]
    accepted = (not timed_out and returncode == 0 and status == ["s VERIFIED"] and
                "WARNING" not in output.upper() and "ERROR" not in output.upper() and
                "NOT VERIFIED" not in output and "UNKNOWN" not in output and
                "DERIVATION" not in output and reads == [Path(proof).stat().st_size] and
                "0 RAT lemmas in core" in output)
    return {
        "command": command, "returncode": returncode, "timed_out": timed_out,
        "status_lines": status, "proof_file_bytes_read": reads,
        "normalized_proof_bytes": Path(proof).stat().st_size,
        "zero_RAT_in_core": "0 RAT lemmas in core" in output,
        "zero_warning_or_error_output": ("WARNING" not in output.upper() and
                                         "ERROR" not in output.upper()),
        "strict_accepted": accepted,
    }, output


def strict_replay(checker, cnf, proof, seconds, log_path, negative_control=True):
    """Full-byte warning-fatal RUP replay, with an independent truncation control."""
    require(type(seconds) is int and seconds > 0, "checker seconds must be positive")
    checker, cnf, proof = Path(checker), Path(cnf), Path(proof)
    require(checker.is_file(), f"missing DRAT checker {checker}")
    require(cnf.is_file() and proof.is_file(), "missing strict replay input")
    receipt, log = _attempt(checker, cnf, proof, seconds)
    Path(log_path).write_text(log)
    receipt.update({
        "schema": "k58-mcf-strict-rup-replay/v1",
        "query_sha256": file_digest(cnf), "proof_sha256": file_digest(proof),
        "checker_sha256": file_digest(checker),
        "checker_flags": ["-i", "-U", "-W", "-t", str(seconds)],
        "full_proof_byte_read_required": True,
    })
    if negative_control:
        raw = proof.read_bytes()
        require(raw, "empty normalized proof cannot establish UNSAT")
        # Empty proof must not validate a non-BCP-contradictory formula.
        # (Dropping only the last empty addition can still be enough when
        # earlier lemmas give a propagation contradiction.)
        bad = proof.with_name(proof.name + ".empty-negative-control")
        bad.write_bytes(b"")
        control, control_log = _attempt(checker, cnf, bad, seconds)
        bad.with_suffix(bad.suffix + ".log").write_text(control_log)
        receipt["negative_control"] = {
            "kind": "remove all additions: empty proof negative control",
            "path": bad.name, "strict_accepted": control["strict_accepted"],
            "returncode": control["returncode"], "status_lines": control["status_lines"],
            "rejected": not control["strict_accepted"],
        }
        require(receipt["negative_control"]["rejected"],
                "empty-proof negative control unexpectedly passed strict replay")
    return receipt


def check_model(clauses, model):
    require(isinstance(model, list) and model, "SAT model is empty or not a list")
    assignment = {}
    for literal in model:
        require(type(literal) is int and literal != 0, "invalid model literal")
        variable = abs(literal)
        require(variable not in assignment or assignment[variable] == (literal > 0),
                "contradictory SAT model")
        assignment[variable] = literal > 0
    for index, clause in enumerate(clauses):
        require(any(assignment.get(abs(lit)) == (lit > 0) for lit in clause),
                f"returned model fails query clause {index}")
    return {str(variable): value for variable, value in sorted(assignment.items())}
