"""Opt-in native LRAT for the cube-and-conquer leaf engine.

Scope
-----
This module is only imported by ``campaign.execute`` when the operator passes an
explicit ``--lrat-trim PATH``.  Without that flag the incumbent path (binary
DRAT leaf proof, joined with ``cas.drat`` and replayed by drat-trim against
``parent + cube``) is byte-for-byte unchanged.  Nothing here is downloaded,
nothing is looked up on ``PATH``, and no claim is made that the supplied checker
is verified.  ``lrat-trim`` is a third-party checker; the receipt records its
SHA-256 and the operator may pin it with ``--lrat-trim-sha256``.

Why the leaf check alone is not enough
--------------------------------------
The production leaf proof refutes ``working.cnf + cube`` where
``working.cnf = parent.cnf + cuts``.  The incumbent replay does not need any
statement about the cuts: ``cas.drat`` derives them inside the joined DRAT trace
that drat-trim checks against ``parent.cnf + cube``.  An LRAT leaf proof is
checked against ``working.cnf + cube`` only, so the implication
``parent + cube |- bottom`` gains one extra premise:

  (P) every clause of ``working.cnf`` outside ``parent.cnf`` is a RUP
      consequence of ``parent.cnf``.

``cut_derivation_check`` establishes (P) once per run with the production
drat-trim and the construction already used by ``selftest.audit_wall``: a fresh
flag per cut, the clause ``flags...`` and, for every literal ``v`` of cut ``i``,
the clause ``-flag_i -v``.  Any model of ``parent.cnf`` extends to a model of
that formula iff it falsifies at least one cut, so a refutation proves (P) for
all cuts at once.  Its trace is the run's own ``cas.drat`` plus unit
``-flag_i`` steps and the empty clause, so it is checked in forward, RUP-only
mode against the parent bytes.

Failure policy: every deviation raises (no status is guessed), an OPEN or
UNKNOWN solver result is never turned into a certificate, and a checker that
does not print its exact success line makes the leaf ``CHECK_FAILED``.
"""

import os
import re
import subprocess
from pathlib import Path

from problem import (digest, encode_clauses, extend_dimacs, file_hash,
                     read_dimacs, require)
from anchor_cuts import binary_prefix

LRAT_FLAG = "--lrat-trim"
SUCCESS = "s VERIFIED"


def lrat_requested(args):
    """True only when the operator supplied an explicit checker path."""
    return getattr(args, "lrat_trim", None) is not None


def require_lrat_checker(path, pinned=None):
    """Fail closed unless the supplied checker is a real, optionally pinned binary."""
    path = Path(path)
    require(path.is_file() and os.access(path, os.X_OK),
            f"missing executable LRAT checker {path}; supply a reviewed lrat-trim build")
    sha = file_hash(path)
    if pinned is not None:
        require(sha == pinned, f"LRAT checker hash {sha} does not match the pinned review hash {pinned}")
    return path.resolve(), sha


# --------------------------------------------------------------- binary LRAT
def binary_lrat_structure(path):
    """Parse a binary LRAT file written by CaDiCaL (``--lrat --binary=true``).

    The layout is the one CaDiCaL 2.1.2 actually emits: every line is tagged
    ``a`` (addition: unsigned clause id, signed literals, 0, unsigned hints, 0)
    or ``d`` (deletion: unsigned clause ids, 0), with the usual little-endian
    base-128 varints and ``2*|lit| + (lit < 0)`` literal encoding.

    The point of parsing the whole file is that the checker's acceptance is
    only as good as the artifact: this requires the file to be well formed to
    its last byte and its last addition to be the empty clause, so a truncated
    or append-only artifact cannot pass as a refutation.  Raises ValueError.
    """
    data = Path(path).read_bytes()
    end = len(data)
    at = 0
    additions = deletions = 0
    last_is_empty = False
    hints_above_id = 0
    max_id = 0

    def unsigned():
        nonlocal at
        value = shift = 0
        while True:
            if at >= end:
                raise ValueError("truncated integer")
            byte = data[at]
            at += 1
            value |= (byte & 127) << shift
            if byte < 128:
                return value
            shift += 7

    while at < end:
        tag = data[at]
        if tag == 0x64:                                  # 'd'
            at += 1
            deletions += 1
            while True:
                if unsigned() == 0:
                    break
            last_is_empty = False
        elif tag == 0x61:                                # 'a'
            at += 1
            cid = unsigned()
            literals = 0
            while True:
                encoded = unsigned()
                if encoded == 0:
                    break
                literals += 1
            while True:
                hint = unsigned()
                if hint == 0:
                    break
                if hint > cid:
                    hints_above_id += 1
            additions += 1
            last_is_empty = literals == 0
            max_id = max(max_id, cid)
        else:
            raise ValueError(f"unexpected tag {tag!r} at byte {at}")
    if additions == 0:
        raise ValueError("no LRAT addition in the artifact")
    return {"bytes": end, "additions": additions, "deletions": deletions,
            "last_is_empty_add": last_is_empty, "max_id": max_id,
            "hints_above_id": hints_above_id}


# ------------------------------------------------------------ leaf replay
def replay_lrat(run_dir, temp, cube, proof, checker, seconds, query_sha256,
                full_structure=False):
    """Check one leaf LRAT proof against exactly the bytes the solver read.

    ``query_sha256`` is the hash the solver recorded for its own input file, so
    rebuilding ``working.cnf + cube`` here and comparing hashes rules out a
    check against a different formula with the same shape.  Returns
    ``(passed, log)``; it never raises for a bad proof.

    ``full_structure`` adds ``binary_lrat_structure``: a whole-file parse that
    requires the artifact to be well formed to its last byte and to end with the
    empty clause.  It costs about 1.5 s of Python on a 15 MB proof, which on the
    measured case is more than the checker saving, so it is used by the audit
    path (``wallcc verify``) and not per leaf in ``run``/``resume``.  Without it
    the evidence that the whole artifact was parsed is the checker's own
    "parsed original proof with N added and M deleted clauses" line.
    """
    formula = temp / "lrat-check.cnf"
    extend_dimacs(run_dir / "working.cnf", formula, [(lit,) for lit in cube])
    if file_hash(formula) != query_sha256:
        return False, "the formula offered to the LRAT checker is not the solver's own input"
    structure = None
    if full_structure:
        try:
            structure = binary_lrat_structure(proof)
        except (OSError, ValueError) as exc:
            return False, f"malformed LRAT artifact: {exc}"
    command = [str(checker), str(formula), str(proof)]
    try:
        run = subprocess.run(command, capture_output=True, timeout=seconds + 2)
    except subprocess.TimeoutExpired:
        return False, "LRAT checker wall-time limit"
    log = (run.stdout + run.stderr).decode(errors="replace")
    messages = log.splitlines()
    if run.returncode != 20 or SUCCESS not in messages:
        return False, log[-1600:]
    parsed = re.search(r"parsed original proof with (\d+) added and (\d+) deleted", log)
    if parsed is None or int(parsed.group(1)) == 0:
        return False, "the checker did not report parsing the whole LRAT artifact\n" + log[-1200:]
    if structure is not None:
        if not structure["last_is_empty_add"]:
            return False, "LRAT artifact does not end with the empty clause\n" + log[-1200:]
        if structure["hints_above_id"]:
            return False, "LRAT artifact uses a clause id before it is introduced\n" + log[-1200:]
    return True, log[-1600:]


# -------------------------------------------------- cut (CAS) derivation check
def cut_derivation_check(out, temp, checker, seconds):
    """Prove every cut of ``working.cnf`` is a RUP consequence of ``parent.cnf``.

    One check per run, not per leaf.  Uses the production drat-trim binary with
    forward, RUP-only checking (``-f -U``) and forces binary proof parsing.
    Returns a small receipt that the leaf receipts bind by hash.
    """
    parent_bytes = (out / "parent.cnf").read_bytes()
    nv, base = read_dimacs(parent_bytes)
    _, working = read_dimacs((out / "working.cnf").read_bytes())
    require(working[:len(base)] == base, "the working CNF is not the parent plus appended cuts")
    cuts = working[len(base):]
    receipt = {"parent_sha256": digest(parent_bytes),
               "working_sha256": file_hash(out / "working.cnf"),
               "cas_sha256": file_hash(out / "cas.drat"),
               "checker_sha256": file_hash(checker),
               "cuts": len(cuts)}
    if not cuts:
        return dict(receipt, status="VACUOUS_NO_CUTS")
    seconds = max(1, int(seconds))
    flags = [nv + i + 1 for i in range(len(cuts))]
    select = [flags] + [[-flag, -literal] for flag, cut in zip(flags, cuts) for literal in cut]
    formula = temp / "cut-derivation.cnf"
    formula.write_bytes(f"p cnf {nv + len(cuts)} {len(base) + len(select)}\n".encode()
                        + parent_bytes.split(b"\n", 1)[1] + encode_clauses(select))
    trace = temp / "cut-derivation.drat"
    trace.write_bytes((out / "cas.drat").read_bytes()
                      + binary_prefix([[-flag] for flag in flags] + [[]]))
    command = [str(checker), str(formula), str(trace), "-f", "-U", "-i", "-t", str(seconds)]
    try:
        run = subprocess.run(command, capture_output=True, timeout=seconds + 2)
    except subprocess.TimeoutExpired:
        raise RuntimeError("the CAS cut-derivation check exceeded its wall-time limit")
    log = (run.stdout + run.stderr).decode(errors="replace")
    require(run.returncode == 0 and SUCCESS in log.splitlines(),
            "CAS cuts are not derived from the parent formula: " + log[-1200:])
    consumed = re.search(r"finished parsing, read (\d+) bytes from proof file", log)
    require(consumed is not None and int(consumed.group(1)) == trace.stat().st_size,
            "the CAS checker accepted a prefix without consuming the complete trace")
    # The receipt below is deterministic -- it holds no timing, log tail or path,
    # so a fresh check in `wallcc verify` reconstructs it byte for byte and the
    # hash recorded in each leaf receipt really does pin the premise.
    return dict(receipt, status="PASS_CUT_DERIVATION", formula_sha256=file_hash(formula),
                trace_sha256=file_hash(trace))
