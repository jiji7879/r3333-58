#!/usr/bin/env python3
"""Independent exact-parent clause-family audit for the retained K58 wall row.

No solver is called. The script reconstructs the parent, traces every auxiliary
allocation, compares a separately written Sinz clause stream in order, and
emits exact semantic obligations. Paths are confined to this member directory.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "inputs" / "frozen"))
from pysat.card import CardEnc, EncType
from gluing import Family, host, units, named_template
from dense import marked_threshold
from support_tables import allowed_supports

RID = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
PARENT_SHA = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
WORKING_SHA = "39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38"
CAS_SHA = "dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3"
PHYSICAL = 4 * (58 * 57 // 2)
OUT = HERE / "results"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(clauses):
    return b"".join((" ".join(map(str, c)) + (" " if c else "") + "0\n").encode()
                    for c in clauses)


def digest_clauses(clauses):
    return sha(encode(clauses))


def parse_canonical(raw):
    """Strict whole-byte parser for the canonical one-clause-per-line inputs."""
    lines = raw.splitlines(keepends=True)
    assert lines and all(line.endswith(b"\n") for line in lines)
    head = lines[0].split()
    assert len(head) == 4 and head[:2] == [b"p", b"cnf"]
    nv, nc = map(int, head[2:])
    clauses = []
    for line in lines[1:]:
        body = line[:-1]
        assert body and not body.startswith((b"c", b"p"))
        fields = body.split()
        assert fields[-1] == b"0" and fields.count(b"0") == 1
        clause = list(map(int, fields[:-1]))
        assert all(x and abs(x) <= nv for x in clause)
        clauses.append(clause)
    assert len(clauses) == nc
    canonical = f"p cnf {nv} {nc}\n".encode() + encode(clauses)
    assert canonical == raw, "non-canonical whitespace or clause order"
    return nv, clauses


def row_identity(row):
    data = {key: row[key] for key in ("family", "placement", "charge")}
    return sha(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


def family_of(row):
    fields = dict(row["family"])
    for key in ("profile", "root_kinds"):
        fields[key] = tuple(fields[key])
    return Family(**fields)


def sinz_atleast_ordered(lits, bound, top):
    """Native PySAT/Lean clause order, tagged recurrence versus overflow.

    This is written from the staggered sequential-counter definition, not by
    filtering the library's output. Each item is (clause, role, local_detail).
    """
    x = list(lits)
    n = len(x)
    if bound <= 0:
        return [], top
    assert bound <= n
    if bound == n:
        return [([v], "overflow", {"case": "atleast_n", "input": i})
                for i, v in enumerate(x)], top
    if bound == 1:
        return [(x, "overflow", {"case": "atleast_1"})], top
    m = n - bound
    assert 0 < m < n - 1

    def cell(d, j):
        index = 2 * j if d == 0 else 2 * j + 1 if d == 1 else d * m + j
        return top + 1 + index

    # Native at-least complements only its physical inputs to the at-most
    # counter: y[d] = -x[d]. Counter-cell signs are left unchanged.
    y = [-v for v in x]
    answer = []
    for d in range(n - m):
        for j in range(m):
            if j == 0:
                main = [-y[d + j], cell(d, j)]
            else:
                main = [-y[d + j], -cell(d, j - 1), cell(d, j)]
            answer.append((main, "recurrence", {"d": d, "j": j, "kind": "main"}))
            if d + 1 < n - m:
                answer.append(([-cell(d, j), cell(d + 1, j)], "recurrence",
                               {"d": d, "j": j, "kind": "forward"}))
        answer.append(([-y[d + m], -cell(d, m - 1)], "overflow",
                       {"d": d, "kind": "cap"}))
    return answer, top + (n - m) * m


def graph_shape(matrix, pts, colour):
    """Direct connectivity/edge test for an induced P4 or C5."""
    n = len(pts)
    adj = {u: [] for u in pts}
    for u, v in combinations(pts, 2):
        if matrix[u][v] == colour:
            adj[u].append(v)
            adj[v].append(u)
    edges = sum(map(len, adj.values())) // 2
    seen = set()
    stack = [pts[0]]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(adj[u])
    if len(seen) != n:
        return None
    degrees = sorted(map(len, adj.values()))
    if n == 4 and edges == 3 and degrees == [1, 1, 2, 2]:
        return "P4"
    if n == 5 and edges == 5 and degrees == [2, 2, 2, 2, 2]:
        return "C5"
    return None


class Builder:
    def __init__(self, family, fixed, charge, host_count):
        self.family = family
        self.fixed = fixed
        self.charge = charge
        self.host_count = host_count
        self.extra = []
        self.blocks = []
        self.counters = []
        self.supports = []
        self.allocations = []
        self.sender_records = []
        self.skipped_senders = []
        self.maximum = PHYSICAL

    def alloc(self, first, last, kind, owner):
        if last < first:
            return
        assert first == self.maximum + 1, (first, self.maximum, kind, owner)
        self.maximum = last
        self.allocations.append({"first": first, "last": last, "kind": kind,
                                 "owner": owner})

    def block(self, kind, clauses, owner, **metadata):
        start = self.host_count + len(self.fixed) + len(self.extra) + 1
        self.extra.extend(clauses)
        end = self.host_count + len(self.fixed) + len(self.extra)
        record = {"kind": kind, "owner": owner, "first_clause": start,
                  "last_clause": end, "clause_count": len(clauses),
                  "sha256": digest_clauses(clauses), **metadata}
        assert (end >= start) if clauses else (end == start - 1)
        self.blocks.append(record)
        return start

    def counter(self, lits, bound, guard, kind, owner):
        before = self.maximum
        enc = CardEnc.atleast(list(lits), bound=bound, top_id=before,
                              encoding=EncType.seqcounter)
        tagged, independent_top = sinz_atleast_ordered(lits, bound, before)
        hard = [c for c, _, _ in tagged]
        assert independent_top == enc.nv, (owner, independent_top, enc.nv)
        assert hard == enc.clauses, (owner, "ordered native Sinz mismatch")
        raw_start = before + 1
        if enc.nv > before:
            self.alloc(raw_start, enc.nv, kind + "_cells", owner)
        clauses = ([[-guard, *c] for c in hard] if guard is not None else hard)
        absolute_first = self.host_count + len(self.fixed) + len(self.extra) + 1
        start = self.block(kind, clauses, owner, guard=guard,
                           inputs=list(lits), bound=bound,
                           allocation_first=raw_start if enc.nv > before else None,
                           allocation_last=enc.nv if enc.nv > before else None,
                           recurrence_count=sum(role == "recurrence" for _, role, _ in tagged),
                           overflow_count=sum(role == "overflow" for _, role, _ in tagged))
        local = []
        for i, (_, role, detail) in enumerate(tagged):
            local.append({"parent_clause": absolute_first + i, "role": role,
                          **detail})
        record = {"kind": kind, "owner": owner, "guard": guard,
                  "first_clause": start, "last_clause": start + len(clauses) - 1,
                  "inputs": list(lits), "bound": bound, "top_before": before,
                  "top_after": enc.nv, "clauses": local,
                  "hard_sha256": digest_clauses(hard),
                  "emitted_sha256": digest_clauses(clauses)}
        self.counters.append(record)
        return record

    def support(self, x, guard, catalogue, catalog_index, positive, negative, known, lit):
        a = self.family.arm
        for b, (size, kind) in enumerate(zip(self.family.profile, self.family.root_kinds)):
            if b == a or kind == "-":
                continue
            start_vertex = sum(self.family.profile[:b]) + 1
            adjacent = [lit(x, start_vertex + j, a) for j in range(size)]
            must = {j for j, v in enumerate(adjacent) if v in positive}
            cannot = {j for j, v in enumerate(adjacent)
                      if v not in positive and (v in negative or (v - 1) // 4 in known)}
            clauses = []
            selectors = []
            for possible in catalogue:
                if not must <= possible or cannot & possible:
                    continue
                selector = self.maximum + 1
                self.alloc(selector, selector, "support_selector",
                           {"sender": x, "target_arm": b,
                            "catalog_index": catalog_index[possible]})
                selectors.append(selector)
                before = len(clauses)
                clauses.extend([-selector, v if j in possible else -v]
                               for j, v in enumerate(adjacent)
                               if j not in must and j not in cannot)
                self.supports.append({
                    "sender": x, "color": a, "guard": guard, "target_arm": b,
                    "selector": selector, "catalog_index": catalog_index[possible],
                    "support": sorted(possible),
                    "implication_first_local": before,
                    "implication_count": len(clauses) - before})
            main_index = len(clauses)
            clauses.append([-guard, *selectors])
            owner = {"sender": x, "color": a, "target_arm": b}
            first = self.block("guarded_support_family", clauses, owner,
                               guard=guard, selector_count=len(selectors),
                               must=sorted(must), cannot=sorted(cannot),
                               main_disjunction_parent_clause=
                                   self.host_count + len(self.fixed) + len(self.extra) + 1 + main_index)
            for rec in self.supports:
                if (rec["sender"] == x and rec["target_arm"] == b
                        and "implication_first_parent_clause" not in rec):
                    rec["implication_first_parent_clause"] = first + rec.pop("implication_first_local")
                    rec["main_disjunction_parent_clause"] = first + main_index

    def run(self):
        f = self.family
        lit, _ = host(sum(f.profile) + 1)
        p = f.profile
        positive = {c[0] for c in self.fixed if c[0] > 0}
        negative = {-c[0] for c in self.fixed if c[0] < 0}
        known = {(v - 1) // 4 for v in positive}
        colors = [c for c, d in enumerate(p) for _ in range(d)]
        critical_mass = sum(d for d in p if d >= 15)
        total = 2 * critical_mass - sum(p)
        bound = self.charge
        root_goal = 0
        a = f.arm
        selectors, all_selectors, root_selectors = [], [], []
        # In this retained row a=1 and the unique classified non-host arm is b=0.
        assert a == 1 and f.root_kinds == ("T", "U", "-", "-")
        catalogue = allowed_supports(f.profile[0], f.root_kinds[0], 0, a)
        catalog_index = {s: i for i, s in enumerate(catalogue)}
        for x, c in enumerate(colors, 1):
            if c != a and p[c] < 15:
                self.skipped_senders.append({"sender": x, "color": c,
                                             "reason": "noncritical_and_not_marked_arm"})
                continue
            candidates = []
            needed = 14
            pinned_hits = []
            omitted = []
            for y, b in enumerate(colors, 1):
                if b == c:
                    continue
                e = lit(x, y, c)
                if e in positive:
                    needed -= 1
                    pinned_hits.append(e)
                elif e not in negative and (e - 1) // 4 not in known:
                    candidates.append(e)
                else:
                    omitted.append(e)
            owner = {"sender": x, "color": c}
            base = {"sender": x, "color": c, "pinned_hits": pinned_hits,
                    "omitted": omitted, "initial_needed": 14,
                    "needed_after_pins": needed, "candidates": candidates}
            if needed <= 0:
                if c == a:
                    bound -= 1
                if p[c] >= 15:
                    total -= 1
                root_goal -= 1
                self.sender_records.append({**base, "guard": None,
                                            "automatic_sender": True})
                continue
            if needed > len(candidates):
                self.sender_records.append({**base, "guard": None,
                                            "impossible_candidates": True})
                continue
            guard = self.maximum + 1
            self.alloc(guard, guard, "sender_guard", owner)
            root_selectors.append(guard)
            if p[c] >= 15:
                all_selectors.append(guard)
            if c == a:
                selectors.append(guard)
            self.counter(candidates, needed, guard, "guarded_sender_atleast", owner)
            sender = {**base, "guard": guard}
            if c == a:
                self.support(x, guard, catalogue, catalog_index,
                             positive, negative, known, lit)
                sender["support_blocks"] = [b for b in self.blocks
                    if b["kind"] == "guarded_support_family"
                    and b["owner"].get("sender") == x]
            self.sender_records.append(sender)
        goals = (("marked_floor", selectors, bound),
                 ("total_critical_floor", all_selectors, total),
                 ("full_root_floor", root_selectors, root_goal))
        self.floor_parameters = []
        for name, lits, minimum in goals:
            self.floor_parameters.append({"kind": name, "minimum_after_automatic": minimum,
                                          "available_guards": len(lits), "guards": lits})
            if minimum > len(lits):
                self.block(name + "_impossible", [[]], {"kind": name})
            elif minimum > 0:
                self.counter(lits, minimum, None, name, {"kind": name})
        return self.extra


def traced_units(family, indices, lit):
    """Re-emit frozen units with a complete provenance label per literal."""
    order = sum(family.profile) + 1
    labels = {}
    groups = []
    start = 1
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size

    def add(v, label):
        labels.setdefault(v, []).append(label)

    for c, block in enumerate(groups):
        for x in block:
            add(lit(0, x, c), {"family": "root_profile", "root_arm": c, "vertex": x})

    def fix_template(vertices, kind, forbidden, source):
        matrix = named_template(len(vertices), kind, forbidden)
        for i, j in combinations(range(len(vertices)), 2):
            add(lit(vertices[i], vertices[j], matrix[i][j]),
                {"family": source, "kind": kind, "forbidden_color": forbidden,
                 "template_indices": [i, j], "vertices": [vertices[i], vertices[j]]})

    for c, (block, kind) in enumerate(zip(groups, family.root_kinds)):
        if kind != "-":
            fix_template(block, kind, c, "classified_root_template")

    # Duplicate the generator's orbit-data binding only to label its exact
    # output; the resulting signed-unit list is compared below with units().
    from gluing import data
    supports, options, _ = data(family)
    marked = [None] * family.marked_size
    marked[family.root_position] = 0
    for (c, source), choices, i in zip(supports, options, indices):
        for u, p in zip(source, choices[i]):
            marked[u] = groups[c][p]
    assert None not in marked and len(marked) == len(set(marked))
    fix_template(marked, family.marked_kind, family.arm, "marked_template")
    q = groups[family.arm][family.mark_position]
    for x in range(1, order):
        if x != q:
            add((1 if x in marked else -1) * lit(q, x, family.arm),
                {"family": "marked_neighbourhood", "q": q, "vertex": x,
                 "in_marked_template": x in marked})
    assert all(-v not in labels for v in labels)
    result = [[v] for v in sorted(labels)]
    return result, labels, marked


def main():
    OUT.mkdir(exist_ok=True)
    row = json.loads((HERE / "inputs" / "row.json").read_text())
    assert row_identity(row) == row["id"] == RID
    parent_raw = (HERE / "inputs" / "parent.cnf").read_bytes()
    assert sha(parent_raw) == PARENT_SHA
    assert sha((HERE / "inputs" / "working.cnf").read_bytes()) == WORKING_SHA
    assert sha((HERE / "inputs" / "cas.drat").read_bytes()) == CAS_SHA
    nv, parent = parse_canonical(parent_raw)
    wnv, working = parse_canonical((HERE / "inputs" / "working.cnf").read_bytes())
    assert wnv == nv and working[:len(parent)] == parent
    f = family_of(row)
    assert f.profile == (16, 16, 14, 11) and row["charge"] == 7
    lit, base = host(58)
    fixed = units(f, row["placement"])
    labeled_fixed, unit_labels, marked_vertices = traced_units(f, row["placement"], lit)
    assert labeled_fixed == fixed
    edge_count = 58 * 57 // 2
    exactly_one_count = 7 * edge_count
    triangle_count = 4 * len(list(combinations(range(58), 3)))
    assert len(base) == exactly_one_count + triangle_count
    assert [c for c in base[:exactly_one_count] if len(c) == 4] == \
           [list(range(4 * i + 1, 4 * i + 5)) for i in range(edge_count)]
    builder = Builder(f, fixed, row["charge"], len(base))
    traced_extra = builder.run()
    source_extra = marked_threshold(f, fixed, row["charge"], tables=True,
                                    total_critical=True, full_root=False)
    assert traced_extra == source_extra
    all_clauses = base + fixed + traced_extra
    rebuilt = f"p cnf {builder.maximum} {len(all_clauses)}\n".encode() + encode(all_clauses)
    assert rebuilt == parent_raw
    assert nv == builder.maximum == PHYSICAL + sum(
        a["last"] - a["first"] + 1 for a in builder.allocations)
    assert parent == all_clauses
    working_suffix = working[len(parent):]
    plan = json.loads((HERE / "inputs" / "plan.json").read_text())
    assert len(working_suffix) == plan["cuts"] == 315

    # Recompute the sole actual support catalogue by direct connectivity tests.
    size, kind, target_arm, marked_color = 16, "T", 0, f.arm
    matrix = named_template(size, kind, target_arm)
    palette = [c for c in range(4) if c not in (target_arm, marked_color)]
    direct_catalog = []
    direct_counts = Counter()
    for order in (4, 5):
        for pts in combinations(range(size), order):
            if any(matrix[u][v] == marked_color for u, v in combinations(pts, 2)):
                continue
            shape = graph_shape(matrix, pts, palette[0])
            if shape:
                direct_catalog.append(frozenset(pts))
                direct_counts[shape] += 1
    source_catalog = list(allowed_supports(size, kind, target_arm, marked_color))
    assert direct_catalog == source_catalog
    catalog_serial = [sorted(s) for s in source_catalog]
    catalog_hash = sha(json.dumps(catalog_serial, separators=(",", ":")).encode())

    cursor = PHYSICAL
    allocation_seen = {}
    for a in builder.allocations:
        assert a["first"] == cursor + 1
        cursor = a["last"]
        for v in range(a["first"], a["last"] + 1):
            assert v not in allocation_seen
            allocation_seen[v] = {"kind": a["kind"], "owner": a["owner"]}
    assert cursor == nv
    guards = [r["guard"] for r in builder.sender_records if r.get("guard")]
    selectors = [r["selector"] for r in builder.supports]
    assert len(guards) == len(set(guards)) and len(selectors) == len(set(selectors))
    assert not set(guards) & set(selectors)
    assert all(v > PHYSICAL for v in guards + selectors)

    # Independently check the exact configurable-MCF premise used on this row.
    # The 126 selected edges are unfixed internal edges of small arms 2 and 3;
    # none of their four physical variables occurs in the non-host suffix.
    groups = []
    group_start = 1
    for size0 in f.profile:
        groups.append(tuple(range(group_start, group_start + size0)))
        group_start += size0
    fixed_edges = {(abs(c[0]) - 1) // 4 for c in fixed}
    mcf_edges = []
    mcf_excluded = []
    for arm in (2, 3):
        for u, v in combinations(groups[arm], 2):
            eid = (lit(u, v, 0) - 1) // 4
            variables = [lit(u, v, colour) for colour in range(4)]
            if eid in fixed_edges:
                pins = [c[0] for c in fixed if (abs(c[0]) - 1) // 4 == eid]
                mcf_excluded.append({"arm": arm, "edge": [u, v], "edge_id": eid,
                                     "fixed_unit_literals": pins})
            else:
                mcf_edges.append({"arm": arm, "edge": [u, v], "edge_id": eid,
                                  "physical_variables": variables})
    mcf_variables = {v for rec in mcf_edges for v in rec["physical_variables"]}
    assert len(mcf_edges) == 126 and len(mcf_excluded) == 20
    assert len(mcf_variables) == 4 * 126
    assert not any(abs(v) in mcf_variables for c in fixed + traced_extra for v in c)
    mcf_summary = {
        "arms": [2, 3], "target_colour": 0,
        "configurable_edges": len(mcf_edges), "excluded_fixed_edges": len(mcf_excluded),
        "suffix_disjoint_variables": len(mcf_variables),
        "witnesses_per_edge": 56, "auxiliary_variables_for_augmentation": 7056,
        "added_clauses_for_augmentation": 21294,
        "formula": "126*(56*3+1) clauses and 126*56 fresh conjunction witnesses",
        "scope": "Exact configurability premise only. The safe-recolouring normal form is equisatisfiability, not DRAT implication; no new performance run or full/pinned MCF extension is claimed."
    }

    edges = list(combinations(range(58), 2))
    unit_records = []
    source_counts = Counter()
    for v, in fixed:
        labels = unit_labels[v]
        eid = (abs(v) - 1) // 4
        u, w = edges[eid]
        colour = (abs(v) - 1) % 4
        for label in labels:
            source_counts[label["family"]] += 1
        unit_records.append({"clause": len(base) + len(unit_records) + 1,
                             "literal": v, "edge": [u, w], "color": colour,
                             "value": v > 0, "provenance": labels})
    unit_hash = sha(json.dumps(unit_records, sort_keys=True, separators=(",", ":")).encode())

    sender_counters = [c for c in builder.counters if c["kind"] == "guarded_sender_atleast"]
    recurrence = sum(item["role"] == "recurrence"
                     for c in sender_counters for item in c["clauses"])
    overflow = sum(item["role"] == "overflow"
                   for c in sender_counters for item in c["clauses"])
    assert recurrence + overflow == sum(len(c["clauses"]) for c in sender_counters)
    checks = {
        "row_identity": True,
        "parent_strict_whole_byte_reconstruction": True,
        "fixed_unit_provenance_reconstruction": True,
        "copied_generator_suffix_identity": True,
        "ordered_native_sinz_identity_for_every_actual_counter": True,
        "support_catalogue_direct_graph_identity": True,
        "fresh_allocation_total_and_disjoint": True,
        "configurable_mcf_suffix_disjointness": True,
        "working_parent_prefix_and_315_clause_suffix": True,
        "solver_calls": 0,
        "sat_or_unsat_verdicts": 0,
        "proof_replays": 0,
    }
    summary = {
        "schema": "k58-exact-parent-semantic-clause-map/v1",
        "row": RID, "profile": list(f.profile), "charge": row["charge"],
        "family": dict(row["family"]), "placement": row["placement"],
        "recipe": {"tables": True, "total_critical": True, "full_root": False},
        "hashes": {"parent_sha256": PARENT_SHA, "working_sha256": WORKING_SHA,
                   "rup_cas_prefix_sha256": CAS_SHA,
                   "plan_sha256": sha((HERE / "inputs" / "plan.json").read_bytes()),
                   "row_json_sha256": sha((HERE / "inputs" / "row.json").read_bytes()),
                   "frozen_units_manifest_sha256": unit_hash,
                   "actual_support_catalogue_sha256": catalog_hash},
        "sizes": {"physical_variables": PHYSICAL, "variables": nv,
                  "auxiliary_variables": nv - PHYSICAL,
                  "clauses": len(parent), "host_clauses": len(base),
                  "host_exactly_one_clauses": exactly_one_count,
                  "host_triangle_clauses": triangle_count,
                  "frozen_unit_clauses": len(fixed),
                  "threshold_support_clauses": len(traced_extra),
                  "working_extra_clauses": len(working_suffix)},
        "unit_source_label_occurrences": dict(source_counts),
        "marked_vertices_by_marked_template_index": marked_vertices,
        "sender_counts": {"emitted_guards": len(guards),
                          "selector_supports": len(selectors),
                          "sender_counters": len(sender_counters),
                          "skipped_noncritical": len(builder.skipped_senders),
                          "automatic_pinned_senders": sum(bool(r.get("automatic_sender")) for r in builder.sender_records),
                          "impossible_candidate_senders": sum(bool(r.get("impossible_candidates")) for r in builder.sender_records)},
        "conditional_counter_map": {"naive_guarded_clauses": recurrence + overflow,
                                    "recurrence_clauses": recurrence,
                                    "overflow_clauses": overflow,
                                    "guard_occurrences_removable_by_boundary_encoding": recurrence,
                                    "guard_occurrences_retained_by_boundary_encoding": overflow,
                                    "note": "Encoding inventory only; no wall A/B or parent UNSAT claim."},
        "support_catalogue": {"size": size, "kind": kind, "target_arm": target_arm,
                              "marked_color": marked_color, "palette": palette,
                              "tested_path_cycle_color": palette[0],
                              "count": len(source_catalog), "shapes": dict(direct_counts)},
        "floor_parameters": builder.floor_parameters,
        "configurable_mcf": mcf_summary,
        "checks": checks,
        "semantic_scope": {
            "ordinary_parent": "Relaxation of the physical semantic row: a CNF refutation would exclude the physical row only after the extension obligations are proved; a model or timeout does not establish a physical colouring.",
            "completed_here": "Exact emitted Boolean families, native counter stream, support catalogue contents and row-specific fresh allocation.",
            "not_completed_here": ["Physical realization of every frozen unit",
                "criticality-to-guard premises and inside-root degree threshold 14",
                "marked/total floor guard selection from w(r)<=H(r)",
                "criticality-to-membership in this exact P4/C5 catalogue",
                "Lean list equality and DIMACS byte serialization assembly",
                "ordinary leaf or parent UNSAT certificates"],
            "no_inference": "No SAT/UNSAT verdict, profile exclusion, row closure, Ramsey bound, or proof from OPEN status."}
    }
    outputs = {
        "summary.json": summary,
        "frozen-units.json": unit_records,
        "allocations.json": builder.allocations,
        "counters.json": builder.counters,
        "support-selectors.json": builder.supports,
        "clause-blocks.json": builder.blocks,
        "senders.json": builder.sender_records,
        "skipped-senders.json": builder.skipped_senders,
        "support-catalogue.json": catalog_serial,
        "mcf-config.json": {"summary": mcf_summary, "configurable": mcf_edges,
                            "excluded_fixed": mcf_excluded},
    }
    for name, value in outputs.items():
        (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    (OUT / "reconstructed-parent.cnf").write_bytes(rebuilt)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
