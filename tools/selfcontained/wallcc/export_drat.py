"""Discharge cube literals and replay a single DRAT against the original parent."""
from itertools import chain
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from campaign import check_binding, check_trace, inspect, validate_artifact
from problem import file_hash, require
from anchor_cuts import binary_prefix


def binary_steps(path):
    tag, value, shift = None, 0, 0
    clause = []
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            for ch in block:
                if tag is None:
                    require(ch in (97, 100), f"invalid binary DRAT tag in {path.name}")
                    tag = ch
                elif ch == 0 and shift == 0:
                    yield tag, clause
                    tag, clause = None, []
                else:
                    value |= (ch & 127) << shift
                    if ch & 128:
                        shift += 7
                        require(shift <= 35, "DRAT literal overflow")
                    else:
                        require(value >= 2, "invalid DRAT literal")
                        clause.append(-(value >> 1) if value & 1 else value >> 1)
                        value, shift = 0, 0
    require(tag is None, f"truncated binary DRAT in {path.name}")


def put(out, clause, tag=97):
    data = binary_prefix([clause])
    out.write(data if tag == 97 else b"d" + data[1:])


def compact_leaf(out, steps, guard):
    blocked = set(guard)
    for tag, clause in steps:
        if tag == 100 or any(-v in blocked for v in clause):
            continue
        put(out, [*clause, *(v for v in guard if v not in clause)])
    put(out, guard)


def isolated_leaf(out, clauses, cube, steps, nv, offset):
    # All guarded clauses use private variables Y. The link clauses let us copy
    # input clauses by RUP. Removing the links isolates every subsequent RAT pivot.
    guard = [-v for v in cube]
    def rename(v):
        return v + offset if v > 0 else v - offset

    def links(tag):
        for v in range(1, nv + 1):
            y = rename(v)
            put(out, [y, -v], tag)
            put(out, [-y, v], tag)

    links(97)
    for clause in chain(clauses, ([v] for v in cube)):
        put(out, [*map(rename, clause), *guard])
    links(100)
    highest = nv
    for tag, clause in steps:
        highest = max(highest, max(map(abs, clause), default=0))
        put(out, [*map(rename, clause), *guard], tag)
    put(out, guard)
    return offset + highest


def export(out, target, method, checker, seconds):
    plan, plan_id, leaves, clauses = inspect(out)
    target = target.resolve()
    require(not target.exists(), "DRAT output already exists")
    proofs = {}
    for node, cube in leaves:
        folder = out / "leaves" / node
        rec = json.loads((folder / "receipt.json").read_bytes())
        check_binding(rec, plan_id, node, cube)
        require(rec["status"] == "CHECKED_UNSAT", f"leaf {node} has no checked refutation")
        proofs[node] = validate_artifact(folder, rec)
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="wallcc-export-", dir=target.parent) as d:
        candidate = Path(d) / "candidate.drat"
        with candidate.open("wb") as dest:
            offset = plan["variables"]
            for node, cube in leaves:
                steps = chain(binary_steps(out / "cas.drat"), binary_steps(proofs[node]))
                if method == "compact":
                    compact_leaf(dest, steps, [-v for v in cube])
                else:
                    offset = isolated_leaf(dest, clauses, cube, steps, plan["variables"], offset)
            # Once both child blocking clauses exist, their parent is a RUP resolvent.
            for node in sorted(plan["splits"], key=len, reverse=True):
                guard = []
                prefix = "r"
                for bit in node[1:]:
                    v = plan["splits"][prefix]
                    guard.append(-v if bit == "1" else v)
                    prefix += bit
                put(dest, guard)
        options = ("-U",) if method == "compact" else ()
        ok, log = check_trace(out / "parent.cnf", candidate, checker, seconds, *options)
        require(ok, f"parent DRAT did not replay ({method}): {log}")
        os.link(candidate, target)  # Atomic publication without replacing an existing file.
    return {"status": "VERIFIED_UNSAT", "origin": plan["origin"],
            "parent_sha256": plan["parent_sha256"], "drat_sha256": file_hash(target),
            "drat_bytes": target.stat().st_size, "method": method}
