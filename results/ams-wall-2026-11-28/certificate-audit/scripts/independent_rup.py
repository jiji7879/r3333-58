#!/usr/bin/env python3
"""From-scratch forward RUP validation of the exact retained CAS derivation.

Ignores deletion commands (which only enlarges the clause database and thus
makes each required RUP check stronger), and deliberately does NOT claim a
refutation because this prefix has no empty addition. No SAT solver or
DRAT-checker result is used by this program.
"""
import json
from pathlib import Path
from audit_prefix import dimacs, binary_proof, sha, IN, ROOT


class Propagator:
    def __init__(self, clauses, nv):
        self.clauses = [list(c) for c in clauses]
        self.nv = nv
        self.occ = [[] for _ in range(2 * nv + 2)]
        self.stamp = [0] * len(self.clauses)
        self.false_count = [0] * len(self.clauses)
        self.version = 0
        self.units = []
        self.has_empty = False
        for cid, clause in enumerate(self.clauses):
            if not clause:
                self.has_empty = True
            if len(clause) == 1:
                self.units.append(clause[0])
            for lit in clause:
                self.occ[self.idx(lit)].append(cid)

    @staticmethod
    def idx(lit):
        return 2 * lit if lit > 0 else -2 * lit + 1

    def add(self, clause):
        cid = len(self.clauses)
        self.clauses.append(list(clause))
        self.stamp.append(0)
        self.false_count.append(0)
        if not clause:
            self.has_empty = True
        if len(clause) == 1:
            self.units.append(clause[0])
        for lit in clause:
            self.occ[self.idx(lit)].append(cid)

    def rup(self, clause):
        if self.has_empty:
            return True
        self.version += 1
        version = self.version
        value = {}
        queue = []
        for lit in clause:
            val = -1 if lit > 0 else 1  # value making lit false
            var = abs(lit)
            if value.get(var) == -val:
                return True  # complementary assumptions: tautological clause
            if value.get(var, 0) == 0:
                value[var] = val
                queue.append(-lit)
        for unit in self.units:
            var = abs(unit)
            want = 1 if unit > 0 else -1
            have = value.get(var, 0)
            if have == 0:
                value[var] = want
                queue.append(unit)
            elif have != want:
                return True
        head = 0
        while head < len(queue):
            lit = queue[head]
            head += 1
            for cid in self.occ[self.idx(-lit)]:
                current = self.clauses[cid]
                if self.stamp[cid] != version:
                    self.stamp[cid] = version
                    self.false_count[cid] = 1
                else:
                    self.false_count[cid] += 1
                count = self.false_count[cid]
                if count == len(current):
                    return True
                if count != len(current) - 1:
                    continue
                rest = None
                for candidate in current:
                    want = 1 if candidate > 0 else -1
                    if value.get(abs(candidate), 0) != -want:
                        rest = candidate
                        break
                if rest is None:
                    return True
                var = abs(rest)
                want = 1 if rest > 0 else -1
                have = value.get(var, 0)
                if have == 0:
                    value[var] = want
                    queue.append(rest)
                elif have != want:
                    return True
        return False


def main():
    (nv, _), parent = dimacs(IN / "parent.cnf")
    records = binary_proof(IN / "cas.drat")
    additions = [clause for tag, clause in records if tag == "a"]
    deletions = sum(tag == "d" for tag, _ in records)
    prop = Propagator(parent, nv)
    bad = []
    for step, clause in enumerate(additions, 1):
        if not prop.rup(clause):
            bad.append({"step": step, "clause": clause})
            break
        prop.add(clause)
    # Executable RUP controls independent of the wall formula.
    toy = Propagator([(-1, 2)], 2)
    positive_control = toy.rup((2, -1))
    negative_control = toy.rup((1,))
    report = {
        "schema": "k58-independent-forward-rup/v1",
        "parent_sha256": sha(IN / "parent.cnf"),
        "cas_sha256": sha(IN / "cas.drat"),
        "additions_checked": len(additions) if not bad else bad[0]["step"],
        "additions_total": len(additions),
        "deletions_ignored": deletions,
        "non_rup": bad,
        "all_additions_rup": not bad and len(additions) == 5445,
        "empty_additions": sum(not clause for clause in additions),
        "derivation_not_refutation": not any(not clause for clause in additions),
        "toy_positive_rup_control": positive_control,
        "toy_non_rup_control_rejected": not negative_control,
    }
    (ROOT / "checks" / "independent-rup.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    assert report["all_additions_rup"] and report["empty_additions"] == 0
    assert positive_control and not negative_control


if __name__ == "__main__":
    main()
