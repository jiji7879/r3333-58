#!/usr/bin/env python3
"""Same-size unsound control: negate the last literal of every verified clause.

Purpose: separate "the verified clauses help" from "any 765 short clauses change
the CDCL trajectory".  This instance is deliberately NOT a symmetry cut and its
status must never be reported as evidence of anything except trajectory effects.
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    lines = (HERE / "parent_cube.cnf").read_text().splitlines()
    header, body = lines[0], lines[1:]
    nvars, nclauses = map(int, header.split()[2:])
    clauses = []
    for line in (HERE / "clauses.txt").read_text().splitlines():
        if not line.strip():
            continue
        clause = [int(x) for x in line.split()[:-1]]
        clause[-1] = -clause[-1]
        if len(set(clause)) != len(clause) or any(-x in clause for x in clause):
            continue
        clauses.append(clause)
    text = ("p cnf %d %d\n" % (nvars, nclauses + len(clauses))
            + "\n".join(body) + "\n"
            + "".join(" ".join(map(str, c)) + " 0\n" for c in clauses))
    (HERE / "corrupted.cnf").write_text(text)
    print("corrupted clauses:", len(clauses),
          "sha256:", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main()
