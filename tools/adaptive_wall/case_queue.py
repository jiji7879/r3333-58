#!/usr/bin/env python3
"""Conservative, shared open-case queue for proof-producing SAT workflows.

Only an independently checked refutation of a case's ROOT formula closes a
case. Solver UNKNOWN/TIMEOUT and imported receipts do not change case state.
A checked child cover creates composition work, not an implicit root proof.

The module is deliberately solver-agnostic. Proof checking and candidate
signed-map discovery are injected; every candidate map is revalidated here.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sqlite3
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Protocol, Sequence

SCHEMA = 1
ATTEMPT_STATES = {
    "RUNNING", "COMPLETED", "TIMEOUT", "CONFLICT_LIMIT", "UNKNOWN", "FAILED",
    "RAW_SAT", "RAW_UNSAT",  # observations, never certificates
}
H_CONTEXTS = {
    "forward_H": "forward",
    "reverse_H": "reverse",
    "root_ticket_H": "root-ticket",
    "contact_statistic_H": "contact-statistic",
}


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def object_hash(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class VerificationError(ValueError):
    """Proof/model invalid, or the configured verifier cannot check it."""


@dataclass(frozen=True)
class Artifact:
    sha256: str
    bytes: int


class ArtifactStore:
    """Content-addressed artifacts, checked again whenever they are read."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, digest: str) -> Path:
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                "invalid SHA-256")
        return self.root / digest[:2] / digest[2:]

    def put(self, data: bytes) -> Artifact:
        desc = Artifact(sha256(data), len(data))
        path = self.path(desc.sha256)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            temporary = path.with_name(path.name + f".tmp-{os.getpid()}-{uuid.uuid4().hex}")
            try:
                with temporary.open("xb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                temporary.replace(path)  # same digest: concurrent replacement is harmless
            finally:
                temporary.unlink(missing_ok=True)
        actual = path.read_bytes()
        require(sha256(actual) == desc.sha256 and len(actual) == desc.bytes,
                f"artifact changed at commit: {desc.sha256}")
        return desc

    def get(self, desc: Artifact | Mapping[str, object]) -> bytes:
        if not isinstance(desc, Artifact):
            desc = Artifact(str(desc["sha256"]), int(desc["bytes"]))
        data = self.path(desc.sha256).read_bytes()
        require(len(data) == desc.bytes and sha256(data) == desc.sha256,
                f"artifact hash/size mismatch: {desc.sha256}")
        return data


def parse_dimacs(data: bytes) -> tuple[int, tuple[tuple[int, ...], ...]]:
    """Strict DIMACS parser; permits multiline clauses but rejects extra tokens."""
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("DIMACS is not ASCII") from exc
    lines = [line for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith("c")]
    require(lines, "empty DIMACS")
    header = lines[0].split()
    require(len(header) == 4 and header[:2] == ["p", "cnf"], "invalid DIMACS header")
    try:
        nv, expected = int(header[2]), int(header[3])
        tokens = [int(token) for line in lines[1:] for token in line.split()]
    except ValueError as exc:
        raise ValueError("non-integer DIMACS field") from exc
    require(nv >= 0 and expected >= 0, "negative DIMACS count")
    clauses, current = [], []
    for token in tokens:
        require(abs(token) <= nv, f"literal {token} exceeds declared variables")
        if token == 0:
            clauses.append(tuple(current))
            current = []
        else:
            current.append(token)
    require(not current, "unterminated final DIMACS clause")
    require(len(clauses) == expected,
            f"header declares {expected} clauses, found {len(clauses)}")
    return nv, tuple(clauses)


def encode_dimacs(nv: int, clauses: Iterable[Sequence[int]]) -> bytes:
    require(type(nv) is int and nv >= 0, "invalid DIMACS variable count")
    clauses = tuple(tuple(int(v) for v in clause) for clause in clauses)
    for clause in clauses:
        require(all(0 < abs(v) <= nv for v in clause), "literal outside DIMACS header")
    body = "".join(" ".join(map(str, clause)) + " 0\n" for clause in clauses)
    return f"p cnf {nv} {len(clauses)}\n".encode() + body.encode("ascii")


def clause_key(clause: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(set(clause), key=lambda v: (abs(v), v < 0)))


def formula_keys(data: bytes) -> tuple[int, frozenset[tuple[int, ...]]]:
    nv, clauses = parse_dimacs(data)
    return nv, frozenset(clause_key(clause) for clause in clauses)


def validate_context(context: Mapping[str, object]) -> None:
    """Namespace H-like quantities; provenance is mandatory for H statements."""
    for key, value in context.items():
        if key not in H_CONTEXTS:
            require(key != "H" and not key.endswith("_H"),
                    f"unnamespaced H-like context {key}")
            continue
        require(isinstance(value, dict), f"{key} must be an object")
        require(value.get("dimension") == H_CONTEXTS[key],
                f"{key} has a mixed/missing dimension")
        require(value.get("relation") in {">=", "=", "<=", ">", "<"},
                f"{key} needs an explicit relation")
        require(type(value.get("value")) in {int, float} and
                math.isfinite(float(value["value"])), f"{key} needs a finite value")
        require(isinstance(value.get("source"), str) and value["source"],
                f"{key} needs a source receipt/assumption name")


def validate_assumptions(formula: bytes, assumptions: Sequence[Mapping[str, object]]) -> None:
    _, keys = formula_keys(formula)
    units = {clause[0] for clause in keys if len(clause) == 1}
    seen = set()
    for item in assumptions:
        require(isinstance(item, dict) and type(item.get("literal")) is int and
                item["literal"] != 0, "signed assumption needs a nonzero literal")
        literal = int(item["literal"])
        require(literal in units, f"assumption {literal} is not an exact formula unit")
        require(isinstance(item.get("kind"), str) and item["kind"],
                "signed assumption needs a kind")
        require(isinstance(item.get("label"), str) and item["label"],
                "signed assumption needs a label")
        fingerprint = (literal, item["kind"], item["label"])
        require(fingerprint not in seen, "duplicate signed assumption")
        seen.add(fingerprint)


class Verifier(Protocol):
    def unsat(self, formula: bytes, proof: bytes, checker: Mapping[str, object]) -> str: ...
    def entailment(self, formula: bytes, additions: Sequence[Sequence[int]],
                   proof: bytes, checker: Mapping[str, object]) -> str: ...
    def model(self, formula: bytes, model: bytes, checker: Mapping[str, object]) -> str: ...


class BruteForceVerifier:
    """Independent semantic verifier for tiny test fixtures only (default <=16 vars)."""

    def __init__(self, max_vars: int = 16):
        self.max_vars = max_vars

    def _assignments(self, nv: int):
        require(nv <= self.max_vars, f"brute-force verifier limited to {self.max_vars} variables")
        return itertools.product((False, True), repeat=nv)

    @staticmethod
    def _satisfies(clauses, bits) -> bool:
        return all(any((bits[abs(v) - 1] == (v > 0)) for v in clause)
                   for clause in clauses)

    def unsat(self, formula, proof, checker) -> str:
        nv, clauses = parse_dimacs(formula)
        for bits in self._assignments(nv):
            if self._satisfies(clauses, bits):
                raise VerificationError(f"not UNSAT; counterexample {bits}")
        return f"VERIFIED exhaustive {2 ** nv} assignments; proof_sha256={sha256(proof)}"

    def entailment(self, formula, additions, proof, checker) -> str:
        nv, clauses = parse_dimacs(formula)
        require(all(0 < abs(v) <= nv for c in additions for v in c),
                "addition exceeds target variables")
        for bits in self._assignments(nv):
            if self._satisfies(clauses, bits) and not self._satisfies(additions, bits):
                raise VerificationError(f"non-entailed addition; counterexample {bits}")
        return f"VERIFIED entailment over {2 ** nv} assignments; proof_sha256={sha256(proof)}"

    def model(self, formula, model, checker) -> str:
        nv, clauses = parse_dimacs(formula)
        try:
            literals = json.loads(model)
            require(isinstance(literals, list) and
                    all(type(v) is int and v != 0 for v in literals), "invalid model JSON")
            require(len(literals) == nv, "model has missing or duplicate literals")
            assignment = {abs(v): v > 0 for v in literals}
            require(set(assignment) == set(range(1, nv + 1)), "model is not total")
            bits = tuple(assignment[v] for v in range(1, nv + 1))
        except (json.JSONDecodeError, ValueError) as exc:
            raise VerificationError(str(exc)) from exc
        if not self._satisfies(clauses, bits):
            raise VerificationError("model does not satisfy exact formula")
        return "VERIFIED model on exact formula"


class RupVerifier:
    """Independent ASCII RUP replay (additions only, one clause per line).

    RUP establishes logical entailment for each added clause. RAT/non-RUP DRAT
    steps are rejected here: they generally preserve satisfiability, not models.
    """

    @staticmethod
    def _parse_proof(proof: bytes) -> list[tuple[int, ...]]:
        try:
            text = proof.decode("ascii")
        except UnicodeDecodeError as exc:
            raise VerificationError("RUP proof is not ASCII (binary DRAT needs drat-trim)") from exc
        steps = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("d"):
                raise VerificationError("deletion/RAT syntax is outside the RUP proof fragment")
            try:
                fields = [int(v) for v in line.split()]
            except ValueError as exc:
                raise VerificationError("non-integer RUP proof line") from exc
            require(fields and fields[-1] == 0 and 0 not in fields[:-1],
                    "each RUP line must contain exactly one 0-terminated clause")
            steps.append(tuple(fields[:-1]))
        return steps

    @staticmethod
    def _unit_propagate(clauses) -> bool:
        """Return True exactly when BCP reaches a conflict."""
        values = {}
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                unassigned = []
                satisfied = False
                for literal in clause:
                    if abs(literal) in values:
                        if values[abs(literal)] == (literal > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(literal)
                if satisfied:
                    continue
                if not unassigned:
                    return True
                if len(unassigned) == 1:
                    literal = unassigned[0]
                    values[abs(literal)] = literal > 0
                    changed = True
        return False

    def _check_steps(self, formula: bytes, steps) -> int:
        nv, clauses = parse_dimacs(formula)
        current = [tuple(c) for c in clauses]
        for clause in steps:
            require(all(0 < abs(v) <= nv for v in clause),
                    "RUP step exceeds the exact formula's declared variables")
            if not self._unit_propagate(current + [(-v,) for v in clause]):
                raise VerificationError(f"clause is not RUP on the exact formula: {clause}")
            current.append(tuple(clause))
        return nv

    def unsat(self, formula, proof, checker) -> str:
        steps = self._parse_proof(proof)
        require(steps and steps[-1] == (), "RUP refutation must end in the empty clause")
        self._check_steps(formula, steps)
        return f"VERIFIED independent RUP refutation, {len(steps)} steps"

    def entailment(self, formula, additions, proof, checker) -> str:
        steps = self._parse_proof(proof)
        require(len(steps) == len(additions) and
                all(clause_key(c) == clause_key(a) for c, a in zip(steps, additions)),
                "RUP proof bytes do not bind exactly to claimed additions")
        self._check_steps(formula, steps)
        return f"VERIFIED independent RUP entailment, {len(steps)} additions"

    def model(self, formula, model, checker) -> str:
        return BruteForceVerifier(max_vars=0).model(formula, model, checker)


class DratTrimVerifier:
    """Generic whole-formula DRAT replay, plus strict RUP-only cut entailment."""

    def __init__(self, executable: str | Path, timeout_seconds: int = 300):
        self.executable = str(Path(executable).resolve())
        self.timeout_seconds = timeout_seconds

    def _checker(self, checker):
        actual = sha256(Path(self.executable).read_bytes())
        if checker.get("sha256") not in {None, actual}:
            raise VerificationError("checker binary hash differs from receipt")
        return {"name": "drat-trim", "sha256": actual}

    def unsat(self, formula, proof, checker) -> str:
        checker = self._checker(checker)
        with tempfile.TemporaryDirectory(prefix="open-case-drat-") as name:
            cnf, drat = Path(name, "exact.cnf"), Path(name, "proof.drat")
            cnf.write_bytes(formula)
            drat.write_bytes(proof)
            run = subprocess.run([self.executable, str(cnf), str(drat), "-i", "-w"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=self.timeout_seconds)
            log = run.stdout.decode("utf-8", "replace")
        if run.returncode != 0 or "s VERIFIED" not in log.splitlines():
            raise VerificationError("exact DRAT replay failed: " + log[-1000:])
        return log

    def entailment(self, formula, additions, proof, checker) -> str:
        # Only the RUP fragment is upgraded to an entailment claim. A generic
        # DRAT/RAT prefix may merely preserve satisfiability and is rejected.
        return RupVerifier().entailment(formula, additions, proof, checker)

    def model(self, formula, model, checker) -> str:
        return BruteForceVerifier(max_vars=0).model(formula, model, checker)


@dataclass(frozen=True)
class TransportCandidate:
    # Source variable (decimal string) -> target SIGNED literal.
    mapping: Mapping[str, int]
    # Required for non-identity maps; the target replay remains mandatory.
    target_proof: bytes | None = None


@dataclass(frozen=True)
class SplitEvidence:
    metric: str
    direct_remaining_estimate: float
    children_total_estimate: float
    measured_attempt_ids: tuple[str, ...]
    rationale: str


Matcher = Callable[[sqlite3.Row, sqlite3.Row, bytes, bytes], Iterable[TransportCandidate]]

SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cases(
 case_id TEXT PRIMARY KEY, source_id TEXT, identity_json TEXT NOT NULL,
 root_parent_id TEXT NOT NULL UNIQUE, created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS parents(
 parent_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id),
 formula_sha256 TEXT NOT NULL, formula_bytes INTEGER NOT NULL,
 assumptions_json TEXT NOT NULL, context_json TEXT NOT NULL,
 is_root INTEGER NOT NULL CHECK(is_root IN (0,1)), created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS links(
 link_id TEXT PRIMARY KEY, parent_id TEXT NOT NULL REFERENCES parents(parent_id),
 child_id TEXT NOT NULL REFERENCES parents(parent_id), kind TEXT NOT NULL,
 split_id TEXT, certificate_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS splits(
 split_id TEXT PRIMARY KEY, parent_id TEXT NOT NULL REFERENCES parents(parent_id),
 variable INTEGER NOT NULL, evidence_json TEXT NOT NULL, kind TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rules(
 rule_id TEXT PRIMARY KEY, kind TEXT NOT NULL,
 source_sha256 TEXT NOT NULL, source_bytes INTEGER NOT NULL,
 proof_sha256 TEXT NOT NULL, proof_bytes INTEGER NOT NULL,
 additions_json TEXT NOT NULL, context_json TEXT NOT NULL,
 checker_json TEXT NOT NULL, signature TEXT NOT NULL,
 source_log_sha256 TEXT NOT NULL, created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS rule_scans(
 rule_id TEXT NOT NULL REFERENCES rules(rule_id),
 parent_id TEXT NOT NULL REFERENCES parents(parent_id),
 matcher_signature TEXT NOT NULL, created_ns INTEGER NOT NULL,
 PRIMARY KEY(rule_id,parent_id,matcher_signature));
CREATE TABLE IF NOT EXISTS rule_matches(
 signature TEXT PRIMARY KEY, rule_id TEXT NOT NULL REFERENCES rules(rule_id),
 parent_id TEXT NOT NULL REFERENCES parents(parent_id), mapping_json TEXT NOT NULL,
 proof_sha256 TEXT, proof_bytes INTEGER, status TEXT NOT NULL,
 receipt_json TEXT NOT NULL, created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS closures(
 closure_id TEXT PRIMARY KEY, parent_id TEXT NOT NULL REFERENCES parents(parent_id),
 proof_sha256 TEXT NOT NULL, proof_bytes INTEGER NOT NULL,
 checker_json TEXT NOT NULL, log_sha256 TEXT NOT NULL,
 created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS attempts(
 attempt_id TEXT PRIMARY KEY, parent_id TEXT NOT NULL REFERENCES parents(parent_id),
 kind TEXT NOT NULL, status TEXT NOT NULL, budgets_json TEXT NOT NULL,
 metrics_json TEXT NOT NULL, artifacts_json TEXT NOT NULL,
 receipt_json TEXT NOT NULL, created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS leases(
 parent_id TEXT PRIMARY KEY REFERENCES parents(parent_id), worker TEXT NOT NULL,
 expires REAL NOT NULL);
CREATE INDEX IF NOT EXISTS links_child ON links(child_id);
CREATE INDEX IF NOT EXISTS links_parent ON links(parent_id);
CREATE INDEX IF NOT EXISTS attempts_parent ON attempts(parent_id);
CREATE TRIGGER IF NOT EXISTS cases_immutable BEFORE UPDATE ON cases BEGIN
 SELECT RAISE(ABORT,'cases are append-only'); END;
CREATE TRIGGER IF NOT EXISTS parents_immutable BEFORE UPDATE ON parents BEGIN
 SELECT RAISE(ABORT,'parents are append-only'); END;
CREATE TRIGGER IF NOT EXISTS rules_immutable BEFORE UPDATE ON rules BEGIN
 SELECT RAISE(ABORT,'rules are append-only'); END;
CREATE TRIGGER IF NOT EXISTS links_immutable BEFORE UPDATE ON links BEGIN
 SELECT RAISE(ABORT,'links are append-only'); END;
CREATE TRIGGER IF NOT EXISTS splits_immutable BEFORE UPDATE ON splits BEGIN
 SELECT RAISE(ABORT,'splits are append-only'); END;
CREATE TRIGGER IF NOT EXISTS closures_immutable BEFORE UPDATE ON closures BEGIN
 SELECT RAISE(ABORT,'closures are append-only'); END;
"""


class CaseQueue:
    """SQLite-backed queue. Each writer uses one short transaction per operation."""

    def __init__(self, database: str | Path, artifacts: str | Path,
                 verifier: Verifier, matcher: Matcher | None = None,
                 matcher_signature: str = "none", candidate_cap: int = 64,
                 rule_work_budget: int = 100):
        require(type(candidate_cap) is int and candidate_cap > 0,
                "candidate_cap must be a positive finite integer")
        require(type(rule_work_budget) is int and rule_work_budget > 0,
                "rule_work_budget must be a positive finite integer")
        self.database = str(database)
        self.candidate_cap = candidate_cap
        self.rule_work_budget = rule_work_budget
        self.store = ArtifactStore(artifacts)
        self.verifier = verifier
        self.matcher = matcher
        self.matcher_signature = matcher_signature
        self.db = sqlite3.connect(self.database, timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA_SQL)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=30000")
        current = self.db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
        if current is None:
            self.db.execute("INSERT INTO meta VALUES('schema',?)", (str(SCHEMA),))
        require(int(current[0]) == SCHEMA if current else True, "unsupported queue schema")

    def close(self):
        self.db.close()

    def _artifact(self, row: sqlite3.Row, stem: str) -> Artifact:
        return Artifact(row[stem + "_sha256"], row[stem + "_bytes"])

    def _formula(self, parent: str | sqlite3.Row) -> tuple[sqlite3.Row, bytes]:
        row = self._parent(parent) if isinstance(parent, str) else parent
        return row, self.store.get(self._artifact(row, "formula"))

    def _parent(self, parent_id: str) -> sqlite3.Row:
        row = self.db.execute("SELECT * FROM parents WHERE parent_id=?", (parent_id,)).fetchone()
        require(row is not None, f"unknown parent {parent_id}")
        return row

    def _case(self, case_id: str) -> sqlite3.Row:
        row = self.db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        require(row is not None, f"unknown case {case_id}")
        return row

    @staticmethod
    def _new_parent_id(case_id: str, formula: Artifact,
                       assumptions, context) -> str:
        return object_hash({"schema": SCHEMA, "case_id": case_id,
                            "formula": vars(formula), "assumptions": assumptions,
                            "context": context})

    def register_case(self, identity: Mapping[str, object], formula: bytes,
                      source_id: str | None = None,
                      assumptions: Sequence[Mapping[str, object]] | None = None,
                      context: Mapping[str, object] | None = None) -> tuple[str, str]:
        # Default ingestion does not discard signed units: make every exact unit
        # explicit. Callers may replace these labels with richer signed-pin data.
        if assumptions is None:
            _, keys = formula_keys(formula)
            literals = sorted({c[0] for c in keys if len(c) == 1})
            assumptions = [{"literal": v, "kind": "original-signed-unit",
                            "label": f"original-unit:{v}"} for v in literals]
        else:
            assumptions = list(assumptions)
        validate_assumptions(formula, assumptions)
        context = dict(context or {})
        validate_context(context)
        case_id = object_hash({"schema": SCHEMA, "kind": "independent-original-case",
                               "identity": identity})
        artifact = self.store.put(formula)
        parent_id = self._new_parent_id(case_id, artifact, list(assumptions), context)
        now = time.time_ns()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
            if existing:
                require(existing["identity_json"] == canonical(identity).decode() and
                        existing["root_parent_id"] == parent_id and
                        existing["source_id"] == source_id, "case identity collision/redefinition")
                self.db.execute("COMMIT")
                return case_id, parent_id
            self.db.execute("INSERT INTO cases VALUES(?,?,?,?,?)",
                            (case_id, source_id, canonical(identity).decode(), parent_id, now))
            self.db.execute("INSERT INTO parents VALUES(?,?,?,?,?,?,?,?)",
                            (parent_id, case_id, artifact.sha256, artifact.bytes,
                             canonical(list(assumptions)).decode(), canonical(context).decode(), 1, now))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        return case_id, parent_id

    @staticmethod
    def k58_identity(row: Mapping[str, object], tier: str) -> tuple[dict, str]:
        """Compute both immutable queue identity and the generator's row ID."""
        require(tier in {"first", "retry"}, "unknown K58 formula tier")
        core = {key: row[key] for key in ("family", "placement", "charge")}
        source_id = object_hash(core)
        if "id" in row:
            require(row["id"] == source_id, "K58 row ID does not hash its signed generator data")
        return {"kind": "K58-wall-original", "tier": tier, "row": core}, source_id

    def register_k58_case(self, row: Mapping[str, object], tier: str, formula: bytes,
                          original_formula_validator: Callable[[Mapping[str, object], str, bytes],
                                                             Mapping[str, object]],
                          assumptions=None, context=None) -> tuple[str, str]:
        """Register only with an external check of the original formula bytes.

        A real validator should regenerate the declared tier with the frozen
        encoder and compare every byte. A hash-only plan check is provenance,
        not proof of K58 geometry, and must be labeled as such in its receipt.
        """
        receipt = dict(original_formula_validator(row, tier, formula))
        require(receipt.get("formula_sha256") == sha256(formula),
                "original-formula validator did not bind the exact bytes")
        require(isinstance(receipt.get("validator"), str) and receipt["validator"],
                "original-formula validator needs a versioned identity")
        identity, source_id = self.k58_identity(row, tier)
        identity = dict(identity, original_formula_validation=receipt)
        return self.register_case(identity, formula, source_id, assumptions, context)

    def _insert_parent(self, case_id: str, formula: bytes,
                       assumptions, context) -> tuple[str, Artifact, sqlite3.Row]:
        artifact = self.store.put(formula)
        validate_assumptions(formula, assumptions)
        validate_context(context)
        parent_id = self._new_parent_id(case_id, artifact, assumptions, context)
        existing = self.db.execute("SELECT * FROM parents WHERE parent_id=?", (parent_id,)).fetchone()
        if existing is None:
            self.db.execute("INSERT INTO parents VALUES(?,?,?,?,?,?,0,?)",
                            (parent_id, case_id, artifact.sha256, artifact.bytes,
                             canonical(assumptions).decode(), canonical(context).decode(), time.time_ns()))
        else:
            require(existing["case_id"] == case_id, "parent hash collision")
            artifact = self._artifact(existing, "formula")
        return parent_id, artifact, self._parent(parent_id)

    def record_attempt(self, parent_id: str, kind: str, status: str,
                       budgets: Mapping[str, object] | None = None,
                       metrics: Mapping[str, object] | None = None,
                       artifacts: Sequence[Mapping[str, object]] = (),
                       receipt: Mapping[str, object] | None = None) -> str:
        self._parent(parent_id)
        require(status in ATTEMPT_STATES, "invalid attempt state")
        metrics = dict(metrics or {})
        for key, value in metrics.items():
            require(key in {"wall_seconds", "cpu_seconds", "solver_conflicts",
                            "total_child_conflicts", "replay_seconds", "proof_bytes"},
                    f"unrecognized/mixed cost metric {key}")
            require(type(value) in {int, float} and math.isfinite(float(value)) and value >= 0,
                    f"invalid cost {key}")
        attempt_id = uuid.uuid4().hex
        self.db.execute("INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?,?)",
                        (attempt_id, parent_id, kind, status, canonical(dict(budgets or {})).decode(),
                         canonical(metrics).decode(), canonical(list(artifacts)).decode(),
                         canonical(dict(receipt or {})).decode(), time.time_ns()))
        return attempt_id

    def close_parent(self, parent_id: str, proof: bytes,
                     checker: Mapping[str, object]) -> str:
        row, formula = self._formula(parent_id)
        proof_desc = self.store.put(proof)
        # The verifier reads the bytes back from CAS, not a claimed formula hash.
        log = self.verifier.unsat(formula, self.store.get(proof_desc), checker)
        log_desc = self.store.put(log.encode())
        closure_id = object_hash({"parent_id": parent_id, "proof": vars(proof_desc),
                                  "checker": checker, "log_sha256": log_desc.sha256})
        existing = self.db.execute("SELECT 1 FROM closures WHERE closure_id=?", (closure_id,)).fetchone()
        if existing:
            return closure_id
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute("INSERT INTO closures VALUES(?,?,?,?,?,?,?)",
                            (closure_id, parent_id, proof_desc.sha256, proof_desc.bytes,
                             canonical(dict(checker)).decode(), log_desc.sha256, time.time_ns()))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        return closure_id

    def close_original(self, case_id: str, proof: bytes,
                       checker: Mapping[str, object]) -> str:
        case = self._case(case_id)
        # This is the only operation that closes an original case directly.
        return self.close_parent(case["root_parent_id"], proof, checker)

    def case_status(self, case_id: str) -> str:
        root = self._case(case_id)["root_parent_id"]
        closed = self.db.execute("SELECT 1 FROM closures WHERE parent_id=?", (root,)).fetchone()
        return "VERIFIED_UNSAT" if closed else "OPEN"

    def _blocked(self, parent_id: str) -> bool:
        # Any exact refutation of an ancestor prunes the whole descendant branch.
        row = self.db.execute("""
          WITH RECURSIVE ancestors(id) AS (
            SELECT ? UNION ALL SELECT l.parent_id FROM links l JOIN ancestors a ON l.child_id=a.id)
          SELECT 1 FROM closures c JOIN ancestors a ON c.parent_id=a.id LIMIT 1
        """, (parent_id,)).fetchone()
        return row is not None

    def _is_live_leaf(self, parent_id: str) -> bool:
        if self._blocked(parent_id):
            return False
        outgoing = self.db.execute("SELECT 1 FROM links WHERE parent_id=? LIMIT 1", (parent_id,)).fetchone()
        return outgoing is None

    def register_rule(self, kind: str, source: bytes, proof: bytes,
                      additions: Sequence[Sequence[int]] = (),
                      required_context: Mapping[str, object] | None = None,
                      checker: Mapping[str, object] | None = None) -> str:
        require(kind in {"REFUTATION", "ENTAILED_CUT"}, "unknown rule kind")
        require((kind == "REFUTATION") == (len(additions) == 0),
                "REFUTATION has no additions; ENTAILED_CUT needs additions")
        checker = dict(checker or {"name": type(self.verifier).__name__})
        context = dict(required_context or {})
        validate_context(context)
        source_desc = self.store.put(source)
        proof_desc = self.store.put(proof)
        if kind == "REFUTATION":
            log = self.verifier.unsat(source, proof, checker)
        else:
            log = self.verifier.entailment(source, additions, proof, checker)
        log_desc = self.store.put(log.encode())
        signature = object_hash({"kind": kind, "source": vars(source_desc),
                                 "additions": [list(c) for c in additions], "context": context})
        # Checker timing/log text is a receipt, not rule identity. Identical
        # source/proof/checker bytes therefore yield a stable ID across runs.
        rule_id = object_hash({"schema": SCHEMA, "signature": signature,
                               "proof": vars(proof_desc), "checker": checker})
        existing = self.db.execute("SELECT 1 FROM rules WHERE rule_id=?", (rule_id,)).fetchone()
        if existing:
            return rule_id
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute("INSERT INTO rules VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                            (rule_id, kind, source_desc.sha256, source_desc.bytes,
                             proof_desc.sha256, proof_desc.bytes,
                             canonical([list(c) for c in additions]).decode(), canonical(context).decode(),
                             canonical(checker).decode(), signature, log_desc.sha256, time.time_ns()))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        return rule_id

    def _map_source(self, source: bytes, target: bytes,
                    mapping: Mapping[str, int]) -> tuple[list[tuple[int, ...]], bool]:
        nv, source_clauses = parse_dimacs(source)
        target_nv, target_keys = formula_keys(target)
        used = sorted({abs(v) for c in source_clauses for v in c})
        require(all(str(v) in mapping for v in used), "map omits a used source variable")
        require(all(type(mapping[str(v)]) is int and mapping[str(v)] != 0 and
                    abs(mapping[str(v)]) <= target_nv for v in used), "map has invalid signed literal")
        images = [abs(int(mapping[str(v)])) for v in used]
        require(len(images) == len(set(images)), "map identifies distinct source variables")
        def image(v: int) -> int:
            mapped = int(mapping[str(abs(v))])
            return mapped if v > 0 else -mapped
        mapped = [clause_key([image(v) for v in c]) for c in source_clauses]
        require(all(c in target_keys for c in mapped),
                "mapped signed source clause is absent from target parent")
        identity = all(int(mapping[str(v)]) == v for v in used)
        return mapped, identity

    def _validate_candidate(self, rule, parent, source, target,
                            candidate: TransportCandidate):
        target_context = json.loads(parent["context_json"])
        required = json.loads(rule["context_json"])
        require(all(target_context.get(key) == value for key, value in required.items()),
                "signed rule context mismatch (including H direction/receipt)")
        mapped, identity = self._map_source(source, target, candidate.mapping)
        proof = candidate.target_proof
        if proof is None:
            require(identity, "nonidentity signed map needs transformed target proof bytes")
            proof = self.store.get(self._artifact(rule, "proof"))
        proof_desc = self.store.put(proof)
        additions = json.loads(rule["additions_json"])
        def image(v):
            result = int(candidate.mapping[str(abs(v))])
            return result if v > 0 else -result
        target_nv, _ = parse_dimacs(target)
        def image_addition(v):
            require(str(abs(v)) in candidate.mapping,
                    "map omits a variable used by an addition")
            mapped_literal = image(v)
            require(abs(mapped_literal) <= target_nv,
                    "mapped addition exceeds target variables")
            return mapped_literal
        mapped_additions = [clause_key(image_addition(v) for v in c) for c in additions]
        return proof_desc, mapped_additions, mapped

    def _sync_rules(self):
        require(self.matcher is not None or
                self.db.execute("SELECT 1 FROM rules LIMIT 1").fetchone() is None,
                "rules exist but no signed matcher is configured")
        parents = self.db.execute("SELECT * FROM parents ORDER BY created_ns,parent_id").fetchall()
        rules = self.db.execute("SELECT * FROM rules ORDER BY rule_id").fetchall()
        for parent in parents:
            if self._blocked(parent["parent_id"]):
                continue
            _, target = self._formula(parent)
            for rule in rules:
                # New contradictions also target already-split ancestors so a
                # successful broad match can prune all their descendants.
                # Cuts materialize only at frontier leaves, avoiding duplicate
                # alternative split trees under an already-branched parent.
                if rule["kind"] != "REFUTATION" and not self._is_live_leaf(parent["parent_id"]):
                    continue
                if self.db.execute("""SELECT 1 FROM rule_scans
                                      WHERE rule_id=? AND parent_id=? AND matcher_signature=?""",
                                   (rule["rule_id"], parent["parent_id"],
                                    self.matcher_signature)).fetchone():
                    continue
                _, source = self._formula_like(rule, "source")
                candidates = list(itertools.islice(
                    self.matcher(rule, parent, source, target), self.candidate_cap + 1))
                require(len(candidates) <= self.candidate_cap,
                        f"more than {self.candidate_cap} candidate maps; raise the explicit cap")
                for candidate in candidates:
                    mapping_json = canonical(dict(candidate.mapping)).decode()
                    # Alternative transformed proofs for one map are distinct candidates;
                    # an earlier missing/invalid proof must not mask a later valid one.
                    signature = object_hash({"rule_id": rule["rule_id"],
                                             "parent_id": parent["parent_id"],
                                             "mapping": dict(candidate.mapping),
                                             "offered_proof_sha256": (sha256(candidate.target_proof)
                                                if candidate.target_proof is not None else None)})
                    if self.db.execute("SELECT 1 FROM rule_matches WHERE signature=?",
                                       (signature,)).fetchone():
                        continue
                    try:
                        proof_desc, additions, _ = self._validate_candidate(
                            rule, parent, source, target, candidate)
                        receipt = {"additions": additions, "matcher_signature": self.matcher_signature}
                        status, proof_sha, proof_bytes = "MATCHED", proof_desc.sha256, proof_desc.bytes
                    except (ValueError, VerificationError) as exc:
                        receipt = {"error": str(exc), "matcher_signature": self.matcher_signature}
                        status, proof_sha, proof_bytes = "REJECTED", None, None
                    self.db.execute("INSERT INTO rule_matches VALUES(?,?,?,?,?,?,?,?,?)",
                                    (signature, rule["rule_id"], parent["parent_id"], mapping_json,
                                     proof_sha, proof_bytes, status, canonical(receipt).decode(), time.time_ns()))
                # Parent/rule bytes are immutable. A matcher implementation or
                # completeness change MUST use a new signature to force rescan.
                self.db.execute("INSERT INTO rule_scans VALUES(?,?,?,?)",
                                (rule["rule_id"], parent["parent_id"],
                                 self.matcher_signature, time.time_ns()))

    def _formula_like(self, row, stem):
        return row, self.store.get(self._artifact(row, stem))

    def apply_rules(self, work_budget: int | None = None) -> int:
        """Apply the rule backlog to a fixed point before any new split.

        Verification work is bounded by the configured/requested budget. Rejected maps remain audit
        records and cannot close/materialize anything. Existing additions are
        redundant, preventing infinite re-materialization on strengthened nodes.
        """
        if work_budget is None:
            work_budget = self.rule_work_budget
        require(type(work_budget) is int and work_budget > 0,
                "work_budget must be a positive finite integer")
        applied = 0
        while True:
            self._sync_rules()
            pending = self.db.execute("""
              SELECT m.*,r.kind,r.additions_json,r.checker_json
              FROM rule_matches m JOIN rules r ON m.rule_id=r.rule_id
              WHERE m.status='MATCHED' ORDER BY m.created_ns,m.signature LIMIT 1
            """).fetchone()
            if pending is None:
                return applied
            require(applied < work_budget, "rule application budget exhausted; queue still pending")
            rule = self.db.execute("SELECT * FROM rules WHERE rule_id=?", (pending["rule_id"],)).fetchone()
            parent = self._parent(pending["parent_id"])
            if self._blocked(parent["parent_id"]):
                self.db.execute("UPDATE rule_matches SET status='STALE' WHERE signature=?",
                                (pending["signature"],))
                continue
            if pending["kind"] != "REFUTATION" and not self._is_live_leaf(parent["parent_id"]):
                self.db.execute("UPDATE rule_matches SET status='STALE' WHERE signature=?",
                                (pending["signature"],))
                continue
            _, target = self._formula(parent)
            proof = self.store.get(Artifact(pending["proof_sha256"], pending["proof_bytes"]))
            checker = json.loads(pending["checker_json"])
            # The match receipt, not the source rule, holds mapped target clauses.
            additions = [clause_key(c) for c in json.loads(pending["receipt_json"])["additions"]]
            _, target_keys = formula_keys(target)
            try:
                if pending["kind"] == "REFUTATION":
                    closure = self.close_parent(parent["parent_id"], proof, checker)
                    receipt = {"closure_id": closure, "target_parent_id": parent["parent_id"]}
                elif all(c in target_keys for c in additions):
                    receipt = {"redundant": True}
                else:
                    self.verifier.entailment(target, additions, proof, checker)
                    nv, raw_clauses = parse_dimacs(target)
                    new_formula = encode_dimacs(nv, list(raw_clauses) + additions)
                    assumptions = json.loads(parent["assumptions_json"])
                    context = json.loads(parent["context_json"])
                    child_id, _, _ = self._insert_parent(parent["case_id"], new_formula,
                                                        assumptions, context)
                    certificate = {"kind": "independently-verified-entailed-strengthening",
                                   "rule_match": pending["signature"],
                                   "proof_sha256": pending["proof_sha256"],
                                   "additions": additions}
                    link_id = object_hash({"parent": parent["parent_id"], "child": child_id,
                                           "certificate": certificate})
                    self.db.execute("INSERT INTO links VALUES(?,?,?,?,NULL,?)",
                                    (link_id, parent["parent_id"], child_id, "ENTAILED_CUT",
                                     canonical(certificate).decode()))
                    receipt = {"derived_parent_id": child_id, "link_id": link_id}
                status = "APPLIED"
            except (ValueError, VerificationError) as exc:
                receipt, status = {"error": str(exc)}, "REJECTED"
            self.db.execute("UPDATE rule_matches SET status=?,receipt_json=? WHERE signature=?",
                            (status, canonical(receipt).decode(), pending["signature"]))
            applied += 1

    def _live_leaf_ids(self) -> list[str]:
        rows = self.db.execute("""
          SELECT p.* FROM parents p WHERE NOT EXISTS(SELECT 1 FROM links l WHERE l.parent_id=p.parent_id)
          ORDER BY p.created_ns,p.parent_id
        """).fetchall()
        return [r["parent_id"] for r in rows if not self._blocked(r["parent_id"])]

    def _compose_parents(self) -> list[str]:
        result = []
        rows = self.db.execute("SELECT DISTINCT parent_id FROM links ORDER BY parent_id").fetchall()
        for row in rows:
            parent_id = row[0]
            if self._blocked(parent_id):
                continue
            children = self.db.execute("SELECT child_id FROM links WHERE parent_id=?", (parent_id,)).fetchall()
            if children and all(self.db.execute("SELECT 1 FROM closures WHERE parent_id=?",
                                                (c[0],)).fetchone() for c in children):
                result.append(parent_id)
        return result

    def open_tasks(self, apply_first: bool = True) -> list[dict]:
        if apply_first:
            self.apply_rules()
        tasks = [{"task": "COMPOSE", "parent_id": p,
                  "case_id": self._parent(p)["case_id"]} for p in self._compose_parents()]
        tasks += [{"task": "SOLVE", "parent_id": p,
                   "case_id": self._parent(p)["case_id"]} for p in self._live_leaf_ids()]
        now = time.time()
        for task in tasks:
            lease = self.db.execute("SELECT worker,expires FROM leases WHERE parent_id=?",
                                    (task["parent_id"],)).fetchone()
            task["leased_to"] = lease["worker"] if lease and lease["expires"] > now else None
            task["available"] = task["leased_to"] is None
        tasks.sort(key=lambda t: (t["task"] != "COMPOSE", t["case_id"], t["parent_id"]))
        return tasks

    def claim_next(self, worker: str, lease_seconds: float = 900) -> dict | None:
        require(worker and lease_seconds > 0, "worker and positive lease required")
        self.apply_rules()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            candidate = next((t for t in self.open_tasks(apply_first=False) if t["available"]), None)
            if candidate is None:
                self.db.execute("COMMIT")
                return None
            self.db.execute("INSERT INTO leases VALUES(?,?,?) ON CONFLICT(parent_id) DO UPDATE SET "
                            "worker=excluded.worker,expires=excluded.expires",
                            (candidate["parent_id"], worker, time.time() + lease_seconds))
            candidate.update(leased_to=worker, available=False)
            self.db.execute("COMMIT")
            return candidate
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def release(self, parent_id: str, worker: str):
        changed = self.db.execute("DELETE FROM leases WHERE parent_id=? AND worker=?",
                                  (parent_id, worker)).rowcount
        require(changed == 1, "lease not held by this worker")

    def split(self, parent_id: str, variable: int, evidence: SplitEvidence) -> tuple[str, str, str]:
        self.apply_rules()
        parent = self._parent(parent_id)
        require(self._is_live_leaf(parent_id), "parent is closed, pruned, or superseded after rule flush")
        require(type(variable) is int, "split variable must be int")
        formula = self.store.get(self._artifact(parent, "formula"))
        nv, clauses = parse_dimacs(formula)
        require(0 < variable <= nv, "split variable outside formula")
        _, keys = formula_keys(formula)
        require((variable,) not in keys and (-variable,) not in keys,
                "split variable already fixed by an explicit unit")
        require(evidence.metric in {"solver_conflicts", "cpu_seconds", "replay_seconds"},
                "split comparison needs one named metric")
        require(math.isfinite(evidence.direct_remaining_estimate) and
                math.isfinite(evidence.children_total_estimate) and
                0 <= evidence.children_total_estimate < evidence.direct_remaining_estimate,
                "measurements do not estimate a same-metric split improvement")
        require(evidence.rationale.strip() and evidence.measured_attempt_ids,
                "split needs measurements and rationale")
        for attempt_id in evidence.measured_attempt_ids:
            attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            require(attempt is not None and attempt["parent_id"] == parent_id and
                    attempt["status"] == "COMPLETED" and
                    evidence.metric in json.loads(attempt["metrics_json"]),
                    "split evidence must reference completed measurements on this exact parent")
        decision = {"metric": evidence.metric,
                    "direct_remaining_estimate": evidence.direct_remaining_estimate,
                    "children_total_estimate": evidence.children_total_estimate,
                    "measured_attempt_ids": list(evidence.measured_attempt_ids),
                    "rationale": evidence.rationale}
        split_id = object_hash({"parent_id": parent_id, "variable": variable,
                                "kind": "exact-complementary-two-way-cover", "decision": decision})
        assumptions = json.loads(parent["assumptions_json"])
        context = json.loads(parent["context_json"])
        children = []
        self.db.execute("BEGIN IMMEDIATE")
        try:
            for literal in (variable, -variable):
                child_formula = encode_dimacs(nv, list(clauses) + [(literal,)])
                child_assumptions = assumptions + [{"literal": literal, "kind": "split",
                                                   "label": f"split:{split_id}"}]
                child_id, _, _ = self._insert_parent(parent["case_id"], child_formula,
                                                    child_assumptions, context)
                children.append(child_id)
                certificate = {"kind": "exact-complementary-two-way-cover",
                               "split_id": split_id, "literal": literal}
                link_id = object_hash({"parent": parent_id, "child": child_id,
                                       "certificate": certificate})
                self.db.execute("INSERT INTO links VALUES(?,?,?,?,?,?)",
                                (link_id, parent_id, child_id, "SPLIT", split_id,
                                 canonical(certificate).decode()))
            self.db.execute("INSERT INTO splits VALUES(?,?,?,?,?)",
                            (split_id, parent_id, variable, canonical(decision).decode(),
                             "exact-complementary-two-way-cover"))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        return split_id, children[0], children[1]

    def work_summary(self, case_id: str | None = None) -> dict:
        if case_id is None:
            rows = self.db.execute("SELECT a.* FROM attempts a").fetchall()
        else:
            rows = self.db.execute("""SELECT a.* FROM attempts a JOIN parents p USING(parent_id)
                                      WHERE p.case_id=?""", (case_id,)).fetchall()
        totals, by_status = {}, {}
        for row in rows:
            for metric, value in json.loads(row["metrics_json"]).items():
                totals[metric] = totals.get(metric, 0) + value
                key = row["status"]
                by_status.setdefault(key, {})
                by_status[key][metric] = by_status[key].get(metric, 0) + value
        closure_query = "SELECT c.* FROM closures c JOIN parents p USING(parent_id)"
        params = ()
        if case_id is not None:
            closure_query += " WHERE p.case_id=?"
            params = (case_id,)
        closures = self.db.execute(closure_query, params).fetchall()
        return {"cost_totals_do_not_mix_units": totals, "cost_by_attempt_status": by_status,
                "independently_replayed_parent_closures": len(closures),
                "proof_bytes_replayed": sum(c["proof_bytes"] for c in closures)}

    def snapshot(self, case_id: str) -> dict:
        case = self._case(case_id)
        rows = self.db.execute("SELECT * FROM parents WHERE case_id=? ORDER BY created_ns,parent_id",
                               (case_id,)).fetchall()
        composing = set(self._compose_parents())
        parents = []
        for row in rows:
            state = "CLOSED_VERIFIED_UNSAT" if self.db.execute(
                "SELECT 1 FROM closures WHERE parent_id=?", (row["parent_id"],)).fetchone() else (
                "PRUNED_BY_ANCESTOR" if self._blocked(row["parent_id"]) else
                "COMPOSE" if row["parent_id"] in composing else
                "OPEN" if self._is_live_leaf(row["parent_id"]) else "WAITING_ON_CHILDREN")
            parents.append({"parent_id": row["parent_id"],
                            "formula": {"sha256": row["formula_sha256"], "bytes": row["formula_bytes"]},
                            "signed_assumptions": json.loads(row["assumptions_json"]),
                            "context": json.loads(row["context_json"]), "state": state})
        return {"case_id": case_id, "source_id": case["source_id"],
                "identity": json.loads(case["identity_json"]), "status": self.case_status(case_id),
                "root_parent_id": case["root_parent_id"], "parents": parents,
                "open_tasks": [t for t in self.open_tasks(apply_first=False) if t["case_id"] == case_id],
                "work": self.work_summary(case_id)}


def identity_matcher(rule, parent, source: bytes, target: bytes) -> Iterable[TransportCandidate]:
    """Only proposes identity maps. Discovery of symmetries belongs to a checked plugin."""
    nv, _ = parse_dimacs(source)
    yield TransportCandidate({str(v): v for v in range(1, nv + 1)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("snapshot", "tasks", "work"):
        p = sub.add_parser(name)
        p.add_argument("database")
        if name == "snapshot":
            p.add_argument("case_id")
    args = parser.parse_args()
    if args.command == "snapshot":
        q = CaseQueue(args.database, Path(args.database).with_suffix(".artifacts"), BruteForceVerifier())
        print(json.dumps(q.snapshot(args.case_id), indent=2, sort_keys=True))
    elif args.command == "tasks":
        q = CaseQueue(args.database, Path(args.database).with_suffix(".artifacts"), BruteForceVerifier())
        print(json.dumps(q.open_tasks(apply_first=False), indent=2, sort_keys=True))
    else:
        q = CaseQueue(args.database, Path(args.database).with_suffix(".artifacts"), BruteForceVerifier())
        print(json.dumps(q.work_summary(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
