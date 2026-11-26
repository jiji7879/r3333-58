#!/usr/bin/env python3
"""Replay-gated learning from exact UNSAT children.

An input child is exactly parent + unit assumptions; drat-trim supplies a
core/trace; assumption deletion is reproved; and transport is a total signed
rename of the core/trace followed by exact-target inclusion and replay.
No solver or bundle status is imported as a closure claim.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Sequence

SCHEMA = "k58-exact-child-learning/v1"
Clause = tuple[int, ...]


class LearningError(Exception):
    pass


class ProofOpen(LearningError):
    pass


class ProofRejected(LearningError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def blob_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_cube(path: Path) -> list[int]:
    value = json.loads(path.read_text())
    if isinstance(value, dict):
        value = value.get("cube")
    if not isinstance(value, list) or any(type(x) is not int or x == 0 for x in value):
        raise LearningError("cube must be a JSON list of nonzero integers")
    variables = [abs(x) for x in value]
    if len(set(variables)) != len(variables):
        raise LearningError("cube repeats a variable (including opposite signs)")
    return value


def read_dimacs(path: Path) -> tuple[int, list[Clause]]:
    header = None
    clauses: list[Clause] = []
    pending: list[int] = []
    for raw in path.read_bytes().splitlines():
        line = raw.strip()
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            fields = line.split()
            if header is not None or len(fields) != 4 or fields[:2] != [b"p", b"cnf"]:
                raise LearningError(f"invalid DIMACS header in {path}")
            try:
                nv, nc = int(fields[2]), int(fields[3])
            except ValueError as e:
                raise LearningError(f"noninteger DIMACS header in {path}") from e
            if nv < 0 or nc < 0:
                raise LearningError("negative DIMACS count")
            header = (nv, nc)
            continue
        if header is None:
            raise LearningError("clause before DIMACS header")
        try:
            values = [int(x) for x in line.split()]
        except ValueError as e:
            raise LearningError(f"noninteger DIMACS clause in {path}") from e
        for lit in values:
            if lit:
                pending.append(lit)
            else:
                clauses.append(tuple(pending))
                pending = []
    if header is None or pending or len(clauses) != header[1]:
        raise LearningError("DIMACS header, clause count, or termination mismatch")
    nv = header[0]
    if any(abs(lit) > nv for clause in clauses for lit in clause):
        raise LearningError("DIMACS literal exceeds declared variable count")
    return nv, clauses


def dimacs_bytes(nv: int, clauses: Iterable[Sequence[int]]) -> bytes:
    clauses = list(clauses)
    lines = [f"p cnf {nv} {len(clauses)}\n"]
    lines.extend(" ".join(map(str, clause)) + (" " if clause else "") + "0\n"
                 for clause in clauses)
    return "".join(lines).encode()


def freeze_bytes(parent: Path, cube: Sequence[int]) -> bytes:
    nv, clauses = read_dimacs(parent)
    if any(abs(lit) > nv for lit in cube):
        raise LearningError("cube literal outside parent variable range")
    return dimacs_bytes(nv, [*clauses, *((lit,) for lit in cube)])


def locate_core(child_clauses: Sequence[Clause], parent_size: int,
                core_clauses: Sequence[Clause]) -> tuple[list[int], list[int]]:
    """Return a clause-multiset embedding, preferring parent copies.

    drat-trim does not promise to preserve input order in its core file.
    Literal order inside a disjunction is immaterial; literal multiplicities
    and duplicate-clause counts are not. Parent-copy preference makes a unit
    duplicated by the parent and cube an obligation of the parent, not an
    unnecessary learned assumption. The selected indices are a representative
    embedding; the checked proof/core bytes remain the primary evidence.
    """
    positions: dict[Clause, list[int]] = {}
    for index, clause in enumerate(child_clauses):
        positions.setdefault(tuple(sorted(clause)), []).append(index)
    unused = {key: collections.deque(value) for key, value in positions.items()}
    selected: list[int] = []
    for clause in core_clauses:
        key = tuple(sorted(clause))
        choices = unused.get(key)
        if not choices:
            raise LearningError("core is not a literal-exact clause multiset contained in the child")
        # The child layout is all parent clauses followed by all cube units.
        # Deque order therefore implements parent-copy preference.
        selected.append(choices.popleft())
    parent_indices = sorted(i for i in selected if i < parent_size)
    cube_indices = sorted(i - parent_size for i in selected if i >= parent_size)
    return parent_indices, cube_indices


@dataclass
class CheckResult:
    status: str
    seconds: float
    returncode: int | None
    log: str
    command: list[str]

    def receipt(self) -> dict:
        return {"status": self.status, "seconds": round(self.seconds, 6),
                "returncode": self.returncode, "log_tail": self.log[-4000:],
                "command": self.command}


def run_checker(checker: Path, cnf: Path, proof: Path, seconds: float,
                *, binary: bool = False, ascii_proof: bool = False,
                derivation: bool = False, rup_only: bool = False,
                extra: Sequence[str] = ()) -> CheckResult:
    if binary and ascii_proof:
        raise LearningError("proof cannot be both ASCII and binary")
    command = [str(checker), str(cnf), str(proof), "-w"]
    if binary:
        command.append("-i")
    if ascii_proof:
        command.append("-I")
    if derivation:
        command.append("-f")
    if rup_only:
        command.append("-U")
    command.extend(extra)
    start = time.monotonic()
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=seconds)
    except subprocess.TimeoutExpired as e:
        data = e.stdout or b""
        if isinstance(data, str):
            data = data.encode(errors="replace")
        return CheckResult("OPEN", time.monotonic() - start, None,
                           data.decode(errors="replace") + "\nCHECKER TIMEOUT", command)
    elapsed = time.monotonic() - start
    log = result.stdout.decode(errors="replace")
    if derivation:
        # This drat-trim build's main returns (sts != UNSAT), so its successful
        # DERIVATION verdict exits 1. This exception is only for forward
        # derivation checking, never for the refutation API below/elsewhere.
        verified = (result.returncode in (0, 1) and b"s DERIVATION" in result.stdout
                    and b"s NOT VERIFIED" not in result.stdout)
        if result.returncode == 0 and b"s VERIFIED" in result.stdout:
            verified = True
    else:
        verified = result.returncode == 0 and b"s VERIFIED" in result.stdout
    return CheckResult("VERIFIED" if verified else "REJECTED", elapsed,
                       result.returncode, log, command)


def require_verified(result: CheckResult, purpose: str) -> None:
    if result.status == "OPEN":
        raise ProofOpen(f"{purpose}: checker timeout (OPEN)")
    if result.status != "VERIFIED":
        raise ProofRejected(f"{purpose}: {result.log[-1800:]}")


def binary_steps(path: Path) -> list[tuple[int, Clause]]:
    data = path.read_bytes()
    at = 0
    steps: list[tuple[int, Clause]] = []
    tag: int | None = None
    clause: list[int] = []

    def integer() -> int:
        nonlocal at
        value = shift = 0
        while True:
            if at >= len(data) or shift > 35:
                raise LearningError("truncated or overflowing binary DRAT integer")
            byte = data[at]
            at += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                return value
            shift += 7

    while at < len(data):
        byte = data[at]
        if tag is None:
            if byte in (97, 100):
                tag = byte
                at += 1
                clause = []
                continue
            tag = 97
        value = integer()
        if value == 0:
            steps.append((tag, tuple(clause)))
            tag = None
            clause = []
            continue
        if value < 2:
            raise LearningError("invalid binary DRAT literal")
        magnitude = value >> 1
        clause.append(-magnitude if value & 1 else magnitude)
    if tag is not None:
        raise LearningError("unterminated binary DRAT clause")
    return steps


def put_binary(path: Path, steps: Iterable[tuple[int, Sequence[int]]]) -> None:
    def integer(value: int) -> bytes:
        out = bytearray()
        while value & ~127:
            out.append((value & 127) | 128)
            value >>= 7
        out.append(value)
        return bytes(out)

    with path.open("wb") as f:
        for tag, clause in steps:
            if tag not in (97, 100):
                raise LearningError("invalid DRAT step tag")
            f.write(b"a" if tag == 97 else b"d")
            for lit in clause:
                if not lit:
                    raise LearningError("zero literal in proof")
                f.write(integer((abs(lit) << 1) | (lit < 0)))
            f.write(b"\0")


def ascii_steps(path: Path) -> list[tuple[int, Clause]]:
    steps: list[tuple[int, Clause]] = []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.strip().split()
        if not fields:
            continue
        tag = 97
        if fields[0] in ("a", "d"):
            tag = 97 if fields.pop(0) == "a" else 100
        try:
            values = [int(x) for x in fields]
        except ValueError as e:
            raise LearningError("invalid ASCII DRAT integer") from e
        if not values or values[-1] != 0 or 0 in values[:-1]:
            raise LearningError("ASCII DRAT line is not exactly one zero-terminated clause")
        steps.append((tag, tuple(values[:-1])))
    return steps


def read_proof_steps(path: Path) -> tuple[list[tuple[int, Clause]], str]:
    """Accept ordinary ASCII/binary DRAT, including drat-trim's ASCII 0\\n corner case."""
    data = path.read_bytes()
    allowed = set(b" \t\r\n0123456789-ad")
    if data and all(x in allowed for x in data) and any(x in b" \t\r\n" for x in data):
        try:
            return ascii_steps(path), "ascii-drat"
        except (LearningError, UnicodeDecodeError):
            pass
    return binary_steps(path), "binary-drat"


def prepare_output(out: Path) -> None:
    if out.exists():
        raise LearningError(f"refusing to overwrite existing output: {out}")
    out.mkdir(parents=True)


def _copy_rule_inputs(parent: Path, child: Path, core: Path, trimmed: Path,
                      out: Path) -> None:
    for source, name in ((parent, "parent.cnf"), (child, "child.cnf"),
                         (core, "core.cnf"), (trimmed, "trim.drat")):
        shutil.copyfile(source, out / name)


def bind_rule(parent: Path, cube_path: Path, proof: Path, core: Path,
              checker: Path, out: Path, seconds: float) -> dict:
    """Normalize and bind a proof/core after fresh core and exact-child replays."""
    cube = read_cube(cube_path)
    parent_nv, parent_clauses = read_dimacs(parent)
    child_bytes = freeze_bytes(parent, cube)
    child = out.with_name(out.name + ".bind-child.tmp")
    normalized = out.with_name(out.name + ".bind-proof.tmp")
    if child.exists() or normalized.exists():
        raise LearningError(f"temporary path exists beside {out}")
    child.write_bytes(child_bytes)
    try:
        _, child_clauses = read_dimacs(child)
        _, core_clauses = read_dimacs(core)
        parent_indices, cube_indices = locate_core(child_clauses, len(parent_clauses), core_clauses)
        steps, input_format = read_proof_steps(proof)
        if not steps or not any(tag == 97 and not clause for tag, clause in steps):
            raise LearningError("trace has no empty addition; it is not a refutation")
        put_binary(normalized, steps)
        checks = [run_checker(checker, core, normalized, seconds, binary=True),
                  run_checker(checker, child, normalized, seconds, binary=True)]
        require_verified(checks[0], "core replay")
        require_verified(checks[1], "exact-child replay")
        prepare_output(out)
        _copy_rule_inputs(parent, child, core, normalized, out)
        core_cube = [cube[i] for i in cube_indices]
        proof_variables = sorted({abs(lit) for _, clause in steps for lit in clause})
        manifest = {
            "schema": SCHEMA,
            "kind": "exact_unsat_refutation",
            "parent": {"file": "parent.cnf", "sha256": sha256(parent),
                       "variables": parent_nv, "clauses": len(parent_clauses)},
            "child": {"file": "child.cnf", "sha256": sha256(child),
                      "relation": "parent clauses followed by exactly the cube units"},
            "cube": cube,
            "cube_sha256": blob_hash(json.dumps(cube, separators=(",", ":")).encode()),
            "core": {"file": "core.cnf", "sha256": sha256(core),
                     "clauses": len(core_clauses),
                     "selection": "literal-exact clause multiset; parent-copy-preferred representative",
                     "selected_parent_indices": parent_indices,
                     "selected_cube_indices": cube_indices},
            "proof": {"file": "trim.drat", "sha256": sha256(normalized),
                      "source_sha256": sha256(proof), "source_format": input_format,
                      "format": "binary-drat", "steps": len(steps),
                      "variables": proof_variables},
            "cube_core": core_cube,
            "learned_clause": [-lit for lit in core_cube],
            "logical_scope": ("The verified refutation proves the child unsatisfiable. If cube_core "
                              "is nonempty, the exact parent entails its negation; if empty, it proves "
                              "the exact parent unsatisfiable. No individual generic DRAT/RAT lemma "
                              "is asserted to be parent-entailed."),
            "validation": {"checker_sha256": sha256(checker),
                           "core_replay": checks[0].receipt(),
                           "exact_child_replay": checks[1].receipt()},
        }
        write_json(out / "rule.json", manifest)
        return manifest
    finally:
        child.unlink(missing_ok=True)
        normalized.unlink(missing_ok=True)


def extract_rule(parent: Path, cube_path: Path, proof: Path, checker: Path,
                 out: Path, seconds: float) -> dict:
    """Core-trim a raw proof, then independently replay core and exact child."""
    cube = read_cube(cube_path)
    child = out.with_name(out.name + ".child.tmp")
    core = out.with_name(out.name + ".core.tmp")
    trimmed = out.with_name(out.name + ".trim.tmp")
    for path in (child, core, trimmed, out):
        if path.exists():
            raise LearningError(f"refusing to overwrite {path}")
    child.write_bytes(freeze_bytes(parent, cube))
    try:
        result = run_checker(checker, child, proof, seconds,
                             extra=("-c", str(core), "-l", str(trimmed), "-C"))
        require_verified(result, "raw exact-child replay/core extraction")
        if not core.is_file() or not trimmed.is_file():
            raise LearningError("checker did not emit both core and binary trimmed proof")
        return bind_rule(parent, cube_path, trimmed, core, checker, out, seconds)
    finally:
        for path in (child, core, trimmed):
            path.unlink(missing_ok=True)


def load_rule(rule_dir: Path) -> dict:
    manifest = json.loads((rule_dir / "rule.json").read_text())
    if manifest.get("schema") != SCHEMA or manifest.get("kind") != "exact_unsat_refutation":
        raise LearningError("unsupported rule schema")
    for section, filename in ((manifest["parent"], "parent.cnf"),
                              (manifest["child"], "child.cnf"),
                              (manifest["core"], "core.cnf"),
                              (manifest["proof"], "trim.drat")):
        if section["file"] != filename or sha256(rule_dir / filename) != section["sha256"]:
            raise LearningError(f"rule artifact hash mismatch: {filename}")
    return manifest


def _model_from_kissat(text: str, nv: int, clauses: Sequence[Clause],
                       cube: Sequence[int]) -> list[int]:
    model: list[int] = []
    for line in text.splitlines():
        if line.startswith("v "):
            model.extend(int(x) for x in line.split()[1:] if x != "0")
    assignment = set(model)
    if any(-x in assignment for x in assignment) or any(abs(x) > nv or x == 0 for x in model):
        raise LearningError("invalid solver model")
    if any(lit not in assignment for lit in cube):
        raise LearningError("model violates cube")
    for index, clause in enumerate(clauses):
        if not any(lit in assignment for lit in clause):
            raise LearningError(f"model fails exact query clause {index}")
    return model


def solve_kissat(solver: Path, cnf: Path, proof: Path, seconds: float,
                 conflicts: int) -> tuple[str, str]:
    command = [str(solver), f"--time={seconds}", f"--conflicts={conflicts}", str(cnf), str(proof)]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=seconds + 2)
    except subprocess.TimeoutExpired:
        return "OPEN", "solver process timeout"
    log = result.stdout.decode(errors="replace")
    if result.returncode == 20:
        return "UNSAT", log
    if result.returncode == 10:
        return "SAT", log
    return "OPEN", f"solver returned {result.returncode} (not a verdict)\n{log[-2000:]}"


def minimize_rule(rule_dir: Path, solver: Path, checker: Path, out: Path,
                  seconds: float, conflicts: int, max_attempts: int) -> dict:
    """Delete whole assumptions only after a fresh exact-parent UNSAT replay."""
    rule = load_rule(rule_dir)
    prepare_output(out)
    attempts_dir = out / "attempts"
    attempts_dir.mkdir()
    parent = rule_dir / "parent.cnf"
    parent_nv, parent_clauses = read_dimacs(parent)
    current = list(rule["cube_core"])
    current_proof = rule_dir / "trim.drat"
    attempts: list[dict] = []
    necessary: dict[int, str] = {}
    unknown: dict[int, str] = {}
    attempt_count = 0
    for lit in list(current):
        if lit not in current:
            continue
        if attempt_count >= max_attempts:
            unknown[lit] = "attempt cap reached"
            continue
        candidate = [x for x in current if x != lit]
        attempt_count += 1
        folder = attempts_dir / f"{attempt_count:04d}"
        folder.mkdir()
        query = folder / "query.cnf"
        proof = folder / "search.drat"
        query.write_bytes(freeze_bytes(parent, candidate))
        write_json(folder / "cube.json", candidate)
        verdict, log = solve_kissat(solver, query, proof, seconds, conflicts)
        receipt: dict = {"removed_candidate": lit, "candidate_cube": candidate,
                         "solver_verdict": verdict, "solver_log_tail": log[-2000:]}
        if verdict == "UNSAT":
            if not proof.is_file():
                receipt["acceptance"] = "OPEN: missing proof"
                unknown[lit] = "missing proof"
            else:
                checked = run_checker(checker, query, proof, seconds)
                receipt["exact_query_replay"] = checked.receipt()
                if checked.status == "VERIFIED":
                    current = candidate
                    current_proof = proof
                    receipt["acceptance"] = "ACCEPTED: exact reduced child refuted"
                    unknown.pop(lit, None)
                else:
                    receipt["acceptance"] = "OPEN: solver UNSAT was not independently certified"
                    unknown[lit] = checked.status
        elif verdict == "SAT":
            _, query_clauses = read_dimacs(query)
            model = _model_from_kissat(log, parent_nv, query_clauses, candidate)
            write_json(folder / "model.json", model)
            necessary[lit] = "independently checked SAT model after deleting this assumption"
            receipt["acceptance"] = "REJECTED: deletion has a checked model"
        else:
            receipt["acceptance"] = "OPEN: no conclusion about this deletion"
            unknown[lit] = "solver UNKNOWN"
        write_json(folder / "receipt.json", receipt)
        attempts.append(receipt)
    for lit in current:
        if lit not in necessary:
            unknown.setdefault(lit, "not tested")
    cube_file = out / "final-cube.json"
    write_json(cube_file, current)
    final_rule_dir = out / "rule"
    final_rule = extract_rule(parent, cube_file, current_proof, checker, final_rule_dir, seconds)
    pending = [lit for lit in current if lit not in necessary]
    summary = {
        "schema": SCHEMA,
        "operation": "single-assumption-deletion",
        "source_rule_sha256": sha256(rule_dir / "rule.json"),
        "final_rule_sha256": sha256(final_rule_dir / "rule.json"),
        "initial_cube_core": rule["cube_core"],
        "final_cube_core": final_rule["cube_core"],
        "attempts": attempts,
        "deletion_minimality": "TESTED_MINIMAL" if not pending else "UNKNOWN",
        "unresolved_literals": pending,
        "note": ("Deleting an assumption unit weakens the query and strengthens the learned blocking "
                 "clause, so every deletion requires a new proof. No literal was deleted from an "
                 "ordinary clause or from a proof lemma."),
    }
    write_json(out / "minimization.json", summary)
    return summary


def _signed_map(map_path: Path | None, variables: set[int]) -> dict[int, int]:
    if map_path is None:
        mapping = {v: v for v in variables}
    else:
        raw = json.loads(map_path.read_text())
        if raw.get("identity") is True:
            mapping = {v: v for v in variables}
        else:
            entries = raw.get("variables")
            if not isinstance(entries, dict):
                raise LearningError("map JSON needs identity:true or a variables object")
            try:
                supplied = {int(k): int(v) for k, v in entries.items()}
            except (TypeError, ValueError) as e:
                raise LearningError("noninteger signed map") from e
            if any(k <= 0 or v == 0 for k, v in supplied.items()):
                raise LearningError("map domain uses positive variables and nonzero signed images")
            if len({abs(v) for v in supplied.values()}) != len(supplied):
                raise LearningError("signed map is not injective on target variables")
            missing = variables - supplied.keys()
            if missing:
                raise LearningError(f"map omits proof/core variables: {sorted(missing)[:20]}")
            mapping = {v: supplied[v] for v in variables}
    if len({abs(image) for image in mapping.values()}) != len(mapping):
        raise LearningError("signed map is not injective on used variables")
    return mapping


def transport_rule(rule_dir: Path, target: Path, map_path: Path | None,
                   checker: Path, out: Path, seconds: float) -> dict:
    rule = load_rule(rule_dir)
    target_nv, target_clauses = read_dimacs(target)
    source_steps = binary_steps(rule_dir / "trim.drat")
    _, source_core = read_dimacs(rule_dir / "core.cnf")
    core_variables = {abs(lit) for clause in source_core for lit in clause}
    variables = set(core_variables)
    variables.update(abs(lit) for _, clause in source_steps for lit in clause)
    mapping = _signed_map(map_path, variables)
    if any(abs(mapping[v]) > target_nv for v in core_variables):
        raise LearningError("mapped core literal outside exact target variable range")
    # Proof-only DRAT extension variables may legally exceed the CNF header.
    # They remain in the total injective signed map and are replayed, not ignored.

    def image(lit: int) -> int:
        target_lit = mapping[abs(lit)]
        return target_lit if lit > 0 else -target_lit

    mapped_core = [tuple(image(lit) for lit in clause) for clause in source_core]
    mapped_steps = [(tag, tuple(image(lit) for lit in clause)) for tag, clause in source_steps]
    prepare_output(out)
    mapped_core_path = out / "transported-core.cnf"
    mapped_proof_path = out / "transported.drat"
    mapped_core_path.write_bytes(dimacs_bytes(target_nv, mapped_core))
    put_binary(mapped_proof_path, mapped_steps)
    base = {
        "schema": SCHEMA,
        "operation": "signed-map-transport",
        "source_rule_sha256": sha256(rule_dir / "rule.json"),
        "target": {"file": str(target), "sha256": sha256(target),
                   "variables": target_nv, "clauses": len(target_clauses)},
        "map": {str(k): v for k, v in sorted(mapping.items())},
        "map_sha256": sha256(map_path) if map_path else None,
        "transported_core_sha256": sha256(mapped_core_path),
        "transported_proof_sha256": sha256(mapped_proof_path),
        "checker_sha256": sha256(checker),
        "target_status": "OPEN",
    }
    available = collections.Counter(tuple(sorted(clause)) for clause in target_clauses)
    needed = collections.Counter(tuple(sorted(clause)) for clause in mapped_core)
    missing = list((needed - available).elements())
    if missing:
        base.update(status="NOT_APPLICABLE", reason="mapped core is not contained in exact target",
                    missing_clause_count=sum((needed - available).values()),
                    missing_clauses_preview=[list(x) for x in missing[:10]])
        write_json(out / "transport.json", base)
        return base
    core_check = run_checker(checker, mapped_core_path, mapped_proof_path, seconds, binary=True)
    base["transported_core_replay"] = core_check.receipt()
    if core_check.status != "VERIFIED":
        base.update(status=core_check.status if core_check.status == "OPEN" else "PROOF_REJECTED",
                    reason="signed transported trace did not replay on its mapped core")
        write_json(out / "transport.json", base)
        return base
    target_check = run_checker(checker, target, mapped_proof_path, seconds, binary=True)
    base["exact_target_replay"] = target_check.receipt()
    if target_check.status == "VERIFIED":
        base.update(status="VERIFIED_UNSAT", target_status="CLOSED_UNSAT", reason=None)
    else:
        base.update(status=target_check.status if target_check.status == "OPEN" else "PROOF_REJECTED",
                    reason="exact target did not accept the transported trace; target remains OPEN")
    write_json(out / "transport.json", base)
    return base


def derivation_control(cnf: Path, proof: Path, checker: Path,
                       seconds: float, rup_only: bool, *, ascii_proof: bool = True) -> CheckResult:
    """Forward-check a derivation prefix; this is intentionally not a refutation API."""
    return run_checker(checker, cnf, proof, seconds, ascii_proof=ascii_proof,
                       derivation=True, rup_only=rup_only)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checker", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("extract", "bind"):
        p = sub.add_parser(name)
        p.add_argument("--parent", type=Path, required=True)
        p.add_argument("--cube", type=Path, required=True)
        p.add_argument("--proof", type=Path, required=True)
        if name == "bind":
            p.add_argument("--core", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--seconds", type=float, default=30)
    p = sub.add_parser("minimize")
    p.add_argument("rule", type=Path)
    p.add_argument("--solver", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=5)
    p.add_argument("--conflicts", type=int, default=2000)
    p.add_argument("--max-attempts", type=int, default=32)
    p = sub.add_parser("transport")
    p.add_argument("rule", type=Path)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--map", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=30)
    args = parser.parse_args(argv)
    if hasattr(args, "seconds") and args.seconds <= 0:
        parser.error("seconds must be positive")
    try:
        if args.command == "extract":
            result = extract_rule(args.parent, args.cube, args.proof, args.checker, args.out, args.seconds)
        elif args.command == "bind":
            result = bind_rule(args.parent, args.cube, args.proof, args.core,
                               args.checker, args.out, args.seconds)
        elif args.command == "minimize":
            if args.conflicts <= 0 or args.max_attempts < 0:
                parser.error("conflicts must be positive and max-attempts nonnegative")
            result = minimize_rule(args.rule, args.solver, args.checker, args.out,
                                   args.seconds, args.conflicts, args.max_attempts)
        else:
            result = transport_rule(args.rule, args.target, args.map, args.checker, args.out, args.seconds)
        print(json.dumps({"status": result.get("status", result.get("kind")), "out": str(args.out)}, sort_keys=True))
        return 0 if result.get("status") in (None, "VERIFIED_UNSAT") else 2
    except ProofOpen as e:
        print(json.dumps({"status": "OPEN", "reason": str(e)}))
        return 2
    except (LearningError, OSError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "ERROR", "reason": str(e)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
