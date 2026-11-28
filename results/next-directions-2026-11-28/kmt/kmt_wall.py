"""Private, experimental KMT replacement for the retained K58 parent.

This module is a *copy* of `frozen/dense.py::marked_threshold` with two
additions, and it imports nothing that it mutates:

  * a `sender_encoding` choice applied to the 31 guarded sender counters
    (`AtLeast(30,10)` x4 and `AtLeast(41,14)` x27) only;
  * a logical-block transcript so that every emitted literal can be labelled
    by the logical object it belongs to (physical edge, sender guard ordinal,
    support selector ordinal, final counter).

Stock mode must reproduce the production clause list exactly; every caller
checks that before using KMT mode.
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FROZEN = REPO / "tools/color-resolved-wallcc/frozen"
sys.path.insert(0, str(REPO / "tools/color-resolved-wallcc"))
sys.path.insert(0, str(FROZEN))

from pysat.card import CardEnc, EncType  # noqa: E402

import audit_campaign  # noqa: E402
import dense as production_dense  # noqa: E402
import problem  # noqa: E402
from gluing import Family, host, units  # noqa: E402
from support_tables import support_clauses  # noqa: E402

ROW_PREFIX = "06861a3df60c"
PARENT_SHA = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
PARENT_VARS = 19533
PARENT_CLAUSES = 184335
KMT_VARS = 13364
KMT_CLAUSES = 176660
CUBE = (-1413, 1014)
PHYSICAL_MAX = 4 * (58 * 57 // 2)  # 6612

SENDER_SHAPES = {(30, 10): 4, (41, 14): 27}

ENCODINGS = {"stock": EncType.seqcounter, "kmt": EncType.kmtotalizer}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def row():
    return problem.lookup(ROW_PREFIX)


def family_of(item):
    family, _ = problem.family_and_pins(item)
    return family


def build_blocks(family, fixed, bound, *, tables, total_critical, full_root, mode):
    """Faithful copy of marked_threshold, with an encoding knob and transcript."""
    assert mode in ENCODINGS
    encoding = ENCODINGS[mode]
    p = family.profile
    n = sum(p) + 1
    lit, _ = host(n)
    highest = 4 * (n * (n - 1) // 2)
    positive = {clause[0] for clause in fixed if clause[0] > 0}
    negative = {-clause[0] for clause in fixed if clause[0] < 0}
    known = {(literal - 1) // 4 for literal in positive}
    colors = [c for c, d in enumerate(p) for _ in range(d)]
    extra, selectors, all_selectors, root_selectors = [], [], [], []
    blocks = []
    critical_mass = sum(d for d in p if d >= 15)
    total = 2 * critical_mass - sum(p) if total_critical else 0
    root_goal = critical_mass if full_root else 0
    a = family.arm
    sender_ordinal = 0
    for x, c in enumerate(colors, 1):
        if c != a and not full_root and (not total_critical or p[c] < 15):
            continue
        candidates = []
        needed = 14
        for y, b in enumerate(colors, 1):
            if b == c:
                continue
            e = lit(x, y, c)
            if e in positive:
                needed -= 1
            elif e not in negative and (e - 1) // 4 not in known:
                candidates.append(e)
        if needed <= 0:
            root_goal -= 1
            if c == a:
                bound -= 1
            if p[c] >= 15:
                total -= 1
        elif needed <= len(candidates):
            highest += 1
            guard = highest
            root_selectors.append(guard)
            if p[c] >= 15:
                all_selectors.append(guard)
            if c == a:
                selectors.append(guard)
            counter = CardEnc.atleast(candidates, bound=needed, top_id=highest,
                                      encoding=encoding)
            assert counter.nv >= guard
            blocks.append(dict(
                kind="sender", ordinal=sender_ordinal, color=c, vertex=x,
                guard=guard, guard_label=("g", sender_ordinal),
                candidates=candidates, needed=needed,
                aux_base=guard + 1, aux_top=counter.nv,
                clauses=counter.clauses))
            highest = max(highest, counter.nv)
            extra.extend([-guard, *clause] for clause in counter.clauses)
            sender_ordinal += 1
            if tables and c == a:
                before = highest
                highest, support = support_clauses(
                    family, x, guard, highest, positive, negative, known)
                blocks.append(dict(
                    kind="support", ordinal=len(blocks), color=c, vertex=x,
                    guard=guard, guard_label=("g", sender_ordinal - 1),
                    aux_base=before + 1, aux_top=highest, clauses=support))
                extra.extend(support)
    finals = (
        ("arm-senders", selectors, bound),
        ("critical-senders", all_selectors, total),
        ("root-senders", root_selectors, root_goal),
    )
    for label, limits, minimum in finals:
        if minimum > len(limits):
            return [[]], blocks, dict(family=f"{label} bound exceeds limit count")
        if minimum > 0:
            counter = CardEnc.atleast(limits, bound=minimum, top_id=highest,
                                      encoding=EncType.seqcounter)
            blocks.append(dict(
                kind="final", ordinal=len(blocks), label=label,
                limits=limits, bound=minimum, aux_base=highest + 1,
                aux_top=counter.nv, clauses=counter.clauses))
            highest = max(highest, counter.nv)
            extra.extend(counter.clauses)
    blocks_stats = dict(highest=highest, clauses=len(extra))
    return extra, blocks, blocks_stats


def label_clause(clause, guard_ids, block):
    """Map one emitted clause to a list of logical labels (order preserved)."""
    out = []
    for literal in clause:
        value = abs(literal)
        sign = 1 if literal > 0 else -1
        if value <= PHYSICAL_MAX:
            out.append((sign, "p", value))
        elif value in guard_ids:
            out.append((sign, "g", guard_ids[value]))
        elif block["aux_base"] <= value <= block["aux_top"]:
            out.append((sign, "a", value - block["aux_base"]))
        else:
            raise ValueError(f"unlabelled literal {literal}")
    return out


def transcript(blocks):
    """Label every block; requires the per-run guard id -> ordinal map."""
    guard_ids = {b["guard"]: b["ordinal"] for b in blocks if b["kind"] == "sender"}
    out = []
    for block in blocks:
        entry = {key: block[key] for key in block if key not in ("clauses", "guard", "guard_label")}
        entry["clauses"] = [label_clause(clause, guard_ids, block) for clause in block["clauses"]]
        entry["aux_count"] = max(0, block["aux_top"] - block["aux_base"] + 1)
        entry["clause_count"] = len(block["clauses"])
        if block["kind"] == "sender":
            entry["candidate_labels"] = [("p" if abs(e) <= PHYSICAL_MAX else "?", abs(e))
                                        for e in block["candidates"]]
        if block["kind"] == "final":
            entry["limit_labels"] = [("g", guard_ids[v]) for v in block["limits"]]
        out.append(entry)
    return out


def parent_bytes(family, item, mode):
    """Bit-identical construction path to frozen/cover_evidence.formula_chunks."""
    fixed = units(family, item["placement"])
    extra, blocks, stats = build_blocks(family, fixed, item["charge"], tables=True,
                                        total_critical=True, full_root=False, mode=mode)
    base, count, top = audit_campaign.body()
    assert extra != [[]], "counter bound exceeds its limit list"
    maximum = max(top, max((abs(lit) for clause in fixed + extra for lit in clause), default=0))
    suffix = fixed + extra
    header = f"p cnf {maximum} {count + len(suffix)}\n".encode()
    payload = header + base + audit_campaign.lines(suffix)
    return payload, fixed, extra, blocks, stats


def with_cube(payload, cube=CUBE):
    """Append the retained cube as unit clauses and fix the DIMACS header."""
    first, rest = payload.split(b"\n", 1)
    parts = first.split()
    assert parts[:2] == [b"p", b"cnf"], first
    variables, clauses = int(parts[2]), int(parts[3])
    assert max(map(abs, cube)) <= variables
    header = f"p cnf {variables} {clauses + len(cube)}\n".encode()
    return header + rest + b"".join(f"{lit} 0\n".encode() for lit in cube)


def comparisons(stock_blocks, kmt_blocks):
    """Exact logical comparison of the two transcripts."""
    a = transcript(stock_blocks)
    b = transcript(kmt_blocks)
    problems = []
    if [x["kind"] for x in a] != [x["kind"] for x in b]:
        problems.append("block kind sequence differs")
    if len(a) != len(b):
        problems.append(f"block count {len(a)} != {len(b)}")
        return dict(ok=False, problems=problems)
    preserved = {"support": 0, "final": 0}
    sender = []
    physical = set()
    for left, right in zip(a, b):
        if left["kind"] != right["kind"]:
            problems.append(f"block {left['ordinal']} kind mismatch")
            continue
        if left["kind"] == "sender":
            if left["candidate_labels"] != right["candidate_labels"]:
                problems.append(f"sender {left['ordinal']} candidate list differs")
            if left["needed"] != right["needed"]:
                problems.append(f"sender {left['ordinal']} bound differs")
            sender.append(dict(ordinal=left["ordinal"], candidates=len(left["candidate_labels"]),
                               needed=left["needed"], color=left["color"], vertex=left["vertex"],
                               stock_aux=left["aux_count"], kmt_aux=right["aux_count"],
                               stock_clauses=left["clause_count"], kmt_clauses=right["clause_count"]))
            for entry in (left, right):
                for clause in entry["clauses"]:
                    physical |= {value for sign, family_name, value in clause if family_name == "p"}
        else:
            if left["clauses"] != right["clauses"]:
                problems.append(f"{left['kind']} {left['ordinal']} clauses differ under labels")
            else:
                preserved[left["kind"]] += 1
            if left["kind"] == "final":
                if left["limit_labels"] != right["limit_labels"]:
                    problems.append(f"final {left['ordinal']} guard list differs")
                if left["bound"] != right["bound"]:
                    problems.append(f"final {left['ordinal']} bound differs")
            for clause in left["clauses"]:
                physical |= {value for sign, family_name, value in clause if family_name == "p"}
    return dict(ok=not problems, problems=problems, preserved=preserved,
                sender=sender, physical_literals=len(physical),
                stock_blocks=len(a), kmt_blocks=len(b))


def allocation_map(stock_blocks, kmt_blocks):
    """Old -> new DIMACS ids for guards, support selectors and final auxiliaries."""
    guards = []
    for old, new in zip([b for b in stock_blocks if b["kind"] == "sender"],
                        [b for b in kmt_blocks if b["kind"] == "sender"]):
        guards.append(dict(ordinal=old["ordinal"], color=old["color"], vertex=old["vertex"],
                           old_guard=old["guard"], new_guard=new["guard"],
                           old_aux_top=old["aux_top"], new_aux_top=new["aux_top"]))
    auxiliary = []
    for old, new in zip([b for b in stock_blocks if b["kind"] != "sender"],
                        [b for b in kmt_blocks if b["kind"] != "sender"]):
        auxiliary.append(dict(kind=old["kind"], ordinal=old["ordinal"],
                              old_base=old["aux_base"], old_top=old["aux_top"],
                              new_base=new["aux_base"], new_top=new["aux_top"],
                              shift=new["aux_base"] - old["aux_base"],
                              count=max(0, old["aux_top"] - old["aux_base"] + 1)))
        assert old["aux_top"] - old["aux_base"] == new["aux_top"] - new["aux_base"], old
    return dict(guards=guards, auxiliary_blocks=auxiliary)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("stock", "kmt"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--transcript", type=Path)
    args = parser.parse_args()
    item = row()
    family = family_of(item)
    payload, fixed, extra, blocks, stats = parent_bytes(family, item, args.mode)
    args.out.write_bytes(payload)
    if args.transcript:
        args.transcript.write_text(json.dumps(
            dict(mode=args.mode, sha256=sha(payload), bytes=len(payload),
                 stats=stats, blocks=transcript(blocks)), sort_keys=True) + "\n")
    print(json.dumps(dict(mode=args.mode, sha256=sha(payload), variables=stats["highest"],
                          clauses=len(extra) + len(fixed) + 134995), sort_keys=True))


if __name__ == "__main__":
    main()
