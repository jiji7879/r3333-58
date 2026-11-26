"""Fail-closed validation of cached receipts for the supplied K58 campaign.

The campaign computes the expected parent/plain/query identities before calling
this module.  This module validates only reuse of an existing receipt; it never
launches a solver, promotes an augmented refutation, or writes over bad cache
bytes.  A malformed or semantically invalid cache returns ``CACHE_INVALID``.
"""
from __future__ import annotations

import gzip
import json
import math
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

CACHE_INVALID = "CACHE_INVALID"
TERMINAL_STATUSES = {"UNSAT_BASE", "SAT_BASE", "AUGMENTED_UNSAT_PENDING_BASE"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_total_model(plain, cube, model, read_dimacs, check_model):
    """Require a total satisfying assignment on the exact plain parent+cube."""
    nv, clauses = read_dimacs(plain)
    _require(type(model) is list and all(type(x) is int for x in model),
             "model must be a list of integer literals")
    _require(len(model) == nv and all(0 < abs(x) <= nv for x in model),
             f"model must contain exactly {nv} in-range nonzero literals")
    _require({abs(x) for x in model} == set(range(1, nv + 1)),
             "model has a missing or duplicate variable")
    check_model(clauses, cube, model, nv)


def strict_check_drat(executable, cnf, proof):
    """Replay binary DRAT without warning suppression.

    In the supplied drat-trim, ``-w`` also bypasses the break on an invalid
    binary prefix and can accept a corrupted tag.  Cached evidence therefore
    uses ``-i`` only and requires an explicit successful verdict line.
    """
    job = subprocess.run([str(executable), str(cnf), str(proof), "-i"],
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    if job.returncode or b"s VERIFIED" not in job.stdout.splitlines():
        raise ValueError(job.stdout[-1000:])


def _safe_artifact(folder, name, field):
    _require(type(name) is str and name and name not in (".", "..") and
             Path(name).name == name, f"{field} must be a basename")
    path = folder / name
    _require(path.is_file() and not path.is_symlink(),
             f"{field} must name a regular artifact in the receipt directory")
    compressed = path.read_bytes()
    data = gzip.decompress(compressed)
    return path, data


class NativeCacheValidator:
    """Dependency-injected binding to the campaign's checked CNF utilities."""

    def __init__(self, sha, read_dimacs, check_model, check_drat):
        self.sha = sha
        self.read_dimacs = read_dimacs
        self.check_model = check_model
        self.check_drat = check_drat

    def _invalid(self, path, expected, cached_status, exc, receipt_bytes=None):
        result = dict(expected)
        result.update(status=CACHE_INVALID,
                      cached_status=cached_status,
                      cache_error_type=type(exc).__name__,
                      cache_error=str(exc)[-1000:],
                      cache_receipt_path=str(path))
        if receipt_bytes is not None:
            result["cached_receipt_sha256"] = self.sha(receipt_bytes)
        return result

    def _validate(self, old, plain, query, cube, folder):
        status = old.get("status")
        _require(status in TERMINAL_STATUSES | {"OPEN"}, "unknown cached status")
        _require(type(old.get("cap")) is int and old["cap"] > 0,
                 "invalid cached conflict cap")
        # Timing/work metadata are useful for measurement but are not proof
        # evidence.  Older valid terminal receipts may omit them; validate any
        # values that are present without making them prerequisites for replay.
        if "conflicts" in old:
            _require(type(old["conflicts"]) is int and old["conflicts"] >= 0,
                     "invalid cached conflict count")
        if "seconds" in old:
            seconds = old["seconds"]
            _require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
                     "invalid cached solver time")
        if status == "OPEN":
            _require("conflicts" not in old or old["conflicts"] >= old["cap"],
                     "under-cap cached OPEN receipt")
            return
        if status == "SAT_BASE":
            _, data = _safe_artifact(folder, old.get("model"), "model")
            _require(self.sha(data) == old.get("model_sha256"), "model hash mismatch")
            model = json.loads(data)
            validate_total_model(plain, cube, model, self.read_dimacs, self.check_model)
            return
        _, proof = _safe_artifact(folder, old.get("proof"), "proof")
        _require(self.sha(proof) == old.get("proof_sha256"), "proof hash mismatch")
        # A base refutation proves the plain parent.  Pending augmented evidence
        # remains pending even after its proof against the query has replayed.
        formula = plain if status == "UNSAT_BASE" else query
        with TemporaryDirectory(dir=folder) as tmp:
            q, p = Path(tmp) / "cached.cnf", Path(tmp) / "cached.drat"
            q.write_bytes(formula)
            p.write_bytes(proof)
            self.check_drat(q, p)

    def load(self, path, expected, plain, query, cube, *, mismatch_is_invalid=False):
        """Return a validated cached receipt, an invalid outcome, or ``None``.

        ``None`` means that the ordinary receipt was absent or belonged to a
        different rule wave, so the caller may try its query-suffixed filename.
        Parse, identity and artifact failures never fall through to a solve.
        """
        path = Path(path)
        try:
            receipt_bytes = path.read_bytes()
        except FileNotFoundError:
            return None
        old = None
        try:
            old = json.loads(receipt_bytes)
            _require(type(old) is dict, "cached receipt is not a JSON object")
            matches = all(old.get(k) == v for k, v in expected.items())
            if not matches:
                if mismatch_is_invalid:
                    raise ValueError("query-suffixed cache identity mismatch")
                return None
            self._validate(old, plain, query, cube, path.parent)
            return old
        except Exception as exc:
            # Deliberately do not rewrite or delete the bad receipt: retaining
            # it makes the failure auditable, and CACHE_INVALID keeps the case
            # nonterminal without triggering an unbounded implicit re-solve.
            cached_status = old.get("status") if type(old) is dict else None
            return self._invalid(path, expected, cached_status, exc, receipt_bytes)
