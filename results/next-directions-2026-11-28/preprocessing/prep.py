#!/usr/bin/env python3
"""One-shot, proof-carrying CNF preprocessing for a constant hash-pinned instance.

Public contract
---------------
Input:   a DIMACS CNF (the host instance: a wall row parent, optionally with the
         cube literals already appended as unit clauses).
Output:  1. ``--out``   reduced CNF, same variable numbering, header nvars kept.
         2. ``--proof`` DRAT *prefix* (ASCII, plus binary with
            ``--proof-binary``): additions are the unit-propagation closure and
            the shortened clauses; deletions are the host clauses the reduced
            formula no longer contains.
         3. ``--receipt`` JSON: hashes, counters and an exact witness for every
            shortening and every subsumption.

Established and re-checked internally
------------------------------------
  * every derived unit is RUP with respect to the host plus earlier units;
  * every shortened clause C' = C \\ {forced literals} is RUP (its falsified
    literals are forced true, so C becomes falsified under the closure);
  * every retained clause is a subset of a host clause;
  * every deletion is of a host clause that is satisfied by the closure, is a
    duplicate, or is subsumed by a retained clause (strict-subset witness).

Therefore a model of the reduced formula, extended by the closure (and the pure
assignment when enabled), is a model of the host; and since unit propagation is
monotone in the clause set, a RUP refutation of the reduced formula is a RUP
refutation of the host once the same clauses are available.

Scope: this changes nothing about which physical problem is encoded.  It is a
one-shot pass over one constant file; it is not a search-time technique.
"""
import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

MAX_SUBSUMER_LEN = 4          # exact subsumption: subsumers up to this size
SUBSUMER_COMBO_CAP = 4096    # skip a size class for long clauses (counted, not silent)
PURE_ROUNDS = 8               # fixpoint rounds for pure-literal elimination


# --------------------------------------------------------------------------- io
def parse_dimacs(data):
    header = None
    clauses, pending = [], []
    for raw in data.splitlines():
        line = raw.strip()
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            parts = line.split()
            if header is not None or len(parts) != 4 or parts[:2] != [b"p", b"cnf"]:
                raise ValueError("invalid or repeated DIMACS header")
            header = (int(parts[2]), int(parts[3]))
            continue
        for field in line.split():
            lit = int(field)
            if lit == 0:
                clauses.append(tuple(pending))
                pending = []
            else:
                pending.append(lit)
    if pending:
        raise ValueError("unterminated clause")
    if header is None:
        raise ValueError("missing DIMACS header")
    if header[1] != len(clauses):
        raise ValueError(f"header claims {header[1]} clauses, parsed {len(clauses)}")
    return header[0], clauses


def clause_bytes(clause):
    return (" ".join(map(str, clause)) + (" " if clause else "") + "0\n").encode()


def dimacs_bytes(nvars, clauses):
    out = [b"p cnf %d %d\n" % (nvars, len(clauses))]
    out.extend(clause_bytes(c) for c in clauses)
    return b"".join(out)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# ----------------------------------------------------------------- unit closure
def unit_closure(clauses, seed_literals):
    """Return (assignment dict, conflict flag, derivation list).

    ``derivation`` is a list of (literal, reason clause index) in propagation
    order; each entry is justified by its reason clause becoming unit under the
    literals derived strictly before it.
    """
    occur = defaultdict(list)
    for index, clause in enumerate(clauses):
        for lit in clause:
            occur[lit].append(index)
    value = {}
    satisfied = bytearray(len(clauses))
    derived = []
    queue = deque((lit, None) for lit in seed_literals)
    while queue:
        lit, reason = queue.popleft()
        var = abs(lit)
        want = lit > 0
        if var in value:
            if value[var] != want:
                return value, True, derived
            continue
        value[var] = want
        if reason is not None:
            derived.append((lit, reason))
        for index in occur[-lit]:
            if satisfied[index]:
                continue
            clause = clauses[index]
            free = None
            count = 0
            for other in clause:
                current = value.get(abs(other))
                if current is None:
                    count += 1
                    free = other
                    if count > 1:
                        break
                elif current == (other > 0):
                    satisfied[index] = 1
                    count = -1
                    break
            if count == 0:
                return value, True, derived
            if count == 1:
                queue.append((free, index))
    return value, False, derived


def _combos(n, k):
    total = 1
    for i in range(k):
        total = total * (n - i) // (i + 1)
    return total


# ----------------------------------------------------------------- simplification
def close_and_simplify(nvars, clauses, subsumption=True, pure=False, with_units=True):
    units = [c[0] for c in clauses if len(c) == 1]
    value, conflict, derived = unit_closure(clauses, units)
    stats = {"conflict_at_root": conflict, "derived_units": len(derived),
             "forced_vars": len(value), "host_clauses": len(clauses)}
    if conflict:
        return None, derived, stats

    additions = [(lit,) for lit, _ in derived]
    replacements = []            # (host clause index, replacement clause)
    deletions = []               # (host clause index, clause)
    kept = []
    satisfied = shortened = 0
    host_unit_set = {c for c in clauses if len(c) == 1}
    for index, clause in enumerate(clauses):
        if len(clause) == 1:
            # A host unit is already in the reduced formula: keep it, never delete
            # it (a deleted unit would have to be re-derived for proof replay).
            kept.append((index, clause))
            continue
        if any(value.get(abs(lit)) == (lit > 0) for lit in clause):
            satisfied += 1
            deletions.append((index, clause))
            continue
        rest = tuple(lit for lit in clause if abs(lit) not in value)
        if len(rest) == len(clause):
            kept.append((index, clause))
            continue
        shortened += 1
        additions.append(rest)
        replacements.append((index, rest))
        deletions.append((index, clause))
        kept.append((index, rest))

    seen = set()
    unique = []
    duplicates = 0
    for index, clause in kept:
        key = frozenset(clause)
        if key in seen:
            duplicates += 1
            deletions.append((index, clause))
            continue
        seen.add(key)
        unique.append((index, clause))
    kept = unique

    subsumed = []
    skipped = 0
    if subsumption:
        index_of = defaultdict(list)
        for _, clause in kept:
            if len(clause) <= MAX_SUBSUMER_LEN:
                index_of[frozenset(clause)].append(clause)
        survivors = []
        for host_index, clause in kept:
            witness = None
            if len(clause) > 1:
                for size in range(1, min(len(clause) - 1, MAX_SUBSUMER_LEN) + 1):
                    if size > 2 and _combos(len(clause), size) > SUBSUMER_COMBO_CAP:
                        skipped += 1
                        continue
                    for combo in itertools.combinations(clause, size):
                        if frozenset(combo) in index_of:
                            witness = combo
                            break
                    if witness is not None:
                        break
            if witness is None:
                survivors.append((host_index, clause))
            else:
                deletions.append((host_index, clause))
                subsumed.append((host_index, list(clause), list(witness)))
        kept = survivors

    pure_assignment = []
    if pure:
        for _ in range(PURE_ROUNDS):
            positive, negative = set(), set()
            for _, clause in kept:
                for lit in clause:
                    (positive if lit > 0 else negative).add(abs(lit))
            pure_vars = positive.symmetric_difference(negative)
            if not pure_vars:
                break
            alive = []
            removed = 0
            for host_index, clause in kept:
                if any(abs(lit) in pure_vars for lit in clause):
                    removed += 1
                    deletions.append((host_index, clause))
                else:
                    alive.append((host_index, clause))
            if not removed:
                break
            for var in sorted(pure_vars):
                pure_assignment.append(var if var in positive else -var)
            kept = alive

    unit_clauses = [((var if positive else -var),) for var, positive in sorted(value.items())]
    emitted_units = [c for c in unit_clauses if c not in host_unit_set]
    if with_units:
        kept = [(None, c) for c in emitted_units] + kept
    stats.update(unit_clauses_emitted=len(emitted_units) if with_units else 0,
                 satisfied_clauses=satisfied, shortened_clauses=shortened,
                 duplicates=duplicates, subsumed_clauses=len(subsumed),
                 subsumer_size_classes_skipped=skipped,
                 pure_vars=len(pure_assignment),
                 clauses_out=len(kept), literals_in=sum(map(len, clauses)),
                 literals_out=sum(len(c) for _, c in kept),
                 additions=len(additions), deletions=len(deletions))
    reduced = dict(clauses=[c for _, c in kept], additions=additions,
                   deletions=[c for _, c in deletions], _deletions_indexed=deletions,
                   replacements=replacements,
                   subsumed=[(c, w) for _, c, w in subsumed],
                   value=value, pure_assignment=pure_assignment,
                   emitted_units=list(emitted_units) if with_units else [])
    return reduced, derived, stats


# ------------------------------------------------------------------ proof writers
def ascii_drat(additions, deletions):
    """ASCII DRAT: additions are bare clauses, deletions are prefixed with 'd'.

    There is no 'a' marker in the ASCII format; only the binary format marks
    additions with byte 0x61 ('a').  Writing 'a' here makes drat-trim
    auto-detect binary mode and parse the text as garbage, silently (measured).
    """
    out = [clause_bytes(c) for c in additions]
    out.extend(b"d " + clause_bytes(c) for c in deletions)
    return b"".join(out)


def _vbyte(value):
    out = bytearray()
    while value & ~0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def binary_drat(additions, deletions):
    def emit(tag, clause):
        body = bytearray(tag)
        for lit in clause:
            body += _vbyte((abs(lit) << 1) | (1 if lit < 0 else 0))
        body += b"\x00"
        return bytes(body)
    out = [emit(b"a", c) for c in additions]
    out.extend(emit(b"d", c) for c in deletions)
    return b"".join(out)


# ----------------------------------------------------------------- verification
def verify(host_clauses, reduced, derived, stats):
    """Re-check every claim the receipt makes, on a fresh closure computation."""
    value, conflict, _ = unit_closure(host_clauses,
                                      [c[0] for c in host_clauses if len(c) == 1])
    problems = []
    if conflict:
        problems.append("host has a root conflict; simplification was skipped")
        return problems
    if len(value) != stats["forced_vars"]:
        problems.append(f"forced_vars mismatch {len(value)} != {stats['forced_vars']}")
    for lit, reason in derived:
        clause = host_clauses[reason]
        if lit not in clause:
            problems.append(f"reason {reason} lacks derived literal {lit}")
            continue
        for other in clause:
            if other != lit and value.get(abs(other)) != (other < 0):
                problems.append(f"reason {reason} not unit for {lit}")
                break
    for host_index, clause in reduced["replacements"]:
        host_clause = host_clauses[host_index]
        if not set(clause) <= set(host_clause):
            problems.append(f"replacement not a subset of host clause {host_index}")
        removed = set(host_clause) - set(clause)
        if any(abs(lit) not in value for lit in removed):
            problems.append(f"replacement {host_index} dropped a non-forced literal")
    for clause in reduced["clauses"]:
        if len(clause) == 1 and value.get(abs(clause[0])) == (clause[0] > 0):
            continue
        if any(abs(lit) in value for lit in clause):
            problems.append(f"reduced clause keeps a forced literal: {clause}")
            break
        if not clause:
            problems.append("reduced formula contains the empty clause")
    for clause, witness in reduced["subsumed"]:
        if not set(witness) < set(clause):
            problems.append(f"subsumption witness not a strict subset: {clause} / {witness}")
    # The retained formula must be exactly the host clauses that were neither
    # dropped nor replaced, with replacements in place: an O(n) identity check.
    replacement = {index: clause for index, clause in reduced["replacements"]}
    dropped = {index for index, _ in reduced["_deletions_indexed"]} - set(replacement)
    expected = list(reduced["emitted_units"]) + [
        replacement.get(i, host_clauses[i])
        for i in range(len(host_clauses)) if i not in dropped]
    host_units = {c for c in host_clauses if len(c) == 1}
    additions = set(reduced["additions"])
    for clause in reduced["clauses"]:
        if len(clause) != 1:
            continue
        if clause not in host_units and clause not in additions:
            problems.append(f"reduced unit {clause} is neither a host clause nor a prefix addition")
            break
        if value.get(abs(clause[0])) != (clause[0] > 0):
            problems.append(f"reduced unit {clause} is not a forced literal")
            break
    expected_counter = Counter(frozenset(c) for c in expected)
    got_counter = Counter(frozenset(c) for c in reduced["clauses"])
    if expected_counter != got_counter:
        missing = list((expected_counter - got_counter).elements())[:3]
        extra = list((got_counter - expected_counter).elements())[:3]
        problems.append(f"retained formula differs from expected: missing={missing} extra={extra}")
    # Exact multiset identity: host - deletions + additions == reduced formula.
    # This is the property the DRAT prefix relies on; re-derive it from scratch.
    final = Counter(frozenset(c) for c in host_clauses)
    for clause in reduced["deletions"]:
        key = frozenset(clause)
        if final[key] == 0:
            problems.append(f"deletion of a clause that is not in the formula: {clause}")
            break
        final[key] -= 1
    for clause in reduced["additions"]:
        final[frozenset(clause)] += 1
    final = Counter({k: v for k, v in final.items() if v})
    if final != got_counter:
        missing = list((final - got_counter).elements())[:3]
        extra = list((got_counter - final).elements())[:3]
        problems.append(f"host - deletions + additions != reduced: missing={missing} extra={extra}")
    return problems


def lift_model(reduced, model):
    """Extend a reduced-CNF model to a host model (dict var -> bool)."""
    value = dict(reduced["value"])
    for lit in model:
        var, want = abs(lit), lit > 0
        if var in value and value[var] != want:
            raise ValueError(f"model contradicts a forced literal: {var}")
        value[var] = want
    for lit in reduced["pure_assignment"]:
        value[abs(lit)] = lit > 0
    return value


def model_satisfies(clauses, value):
    return all(any(value.get(abs(lit)) == (lit > 0) for lit in clause) for clause in clauses)


# ------------------------------------------------------------------------ driver
def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--proof-binary", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--no-subsumption", action="store_true")
    parser.add_argument("--pure", action="store_true",
                        help="also eliminate pure literals (off by default)")
    parser.add_argument("--expect-sha256")
    parser.add_argument("--drop-units", action="store_true",
                        help="do not emit the closure units (weaker formula; control arm)")
    args = parser.parse_args(argv)

    data = args.cnf.read_bytes()
    host_sha = sha256(data)
    if args.expect_sha256 and host_sha != args.expect_sha256:
        raise SystemExit(f"host hash mismatch: {host_sha} != {args.expect_sha256}")
    nvars, clauses = parse_dimacs(data)

    reduced, derived, stats = close_and_simplify(
        nvars, clauses, subsumption=not args.no_subsumption, pure=args.pure,
        with_units=not args.drop_units)

    receipt = {"host": {"path": str(args.cnf), "sha256": host_sha, "bytes": len(data),
                        "vars": nvars, "clauses": len(clauses)},
               "options": {"subsumption": not args.no_subsumption, "pure": args.pure,
                           "max_subsumer_len": MAX_SUBSUMER_LEN},
               "stats": stats}
    if reduced is None:
        # Root-level unit propagation already refutes the host: the prefix is a
        # complete DRAT refutation (derived units, then the empty clause, which
        # is RUP because unit propagation on host + units conflicts).
        additions = [(lit,) for lit, _ in derived] + [()]
        text_proof = ascii_drat(additions, [])
        args.proof.write_bytes(text_proof)
        binary = None
        if args.proof_binary:
            binary = binary_drat(additions, [])
            args.proof_binary.write_bytes(binary)
        args.out.write_bytes(dimacs_bytes(nvars, [()]))
        receipt.update(verdict="root_conflict", additions=additions and len(additions),
                       prefix={"path": str(args.proof), "sha256": sha256(text_proof),
                               "bytes": len(text_proof),
                               "binary_sha256": sha256(binary) if binary else None,
                               "binary_bytes": len(binary) if binary else None})
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"verdict": "root_conflict", "stats": stats}, sort_keys=True))
        return 3

    problems = verify(clauses, reduced, derived, stats)
    out = dimacs_bytes(nvars, reduced["clauses"])
    text_proof = ascii_drat(reduced["additions"], reduced["deletions"])
    args.out.write_bytes(out)
    args.proof.write_bytes(text_proof)
    binary = None
    if args.proof_binary:
        binary = binary_drat(reduced["additions"], reduced["deletions"])
        args.proof_binary.write_bytes(binary)
    receipt.update(
        verdict="ok" if not problems else "failed",
        problems=problems,
        reduced={"path": str(args.out), "sha256": sha256(out), "bytes": len(out),
                 "clauses": len(reduced["clauses"])},
        prefix={"path": str(args.proof), "sha256": sha256(text_proof),
                "bytes": len(text_proof),
                "binary_sha256": sha256(binary) if binary is not None else None,
                "binary_bytes": len(binary) if binary is not None else None},
        forced_units={str(k): (1 if v else -1) for k, v in sorted(reduced["value"].items())},
        pure_assignment=reduced["pure_assignment"],
    )
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "stats": stats,
                      "problems": problems[:5]}, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
