#!/usr/bin/env python3
"""Hash-bound factored encodings of the guarded paired-arm support theorem.

Reads the published hard-study sources without writing there. All outputs go
beneath an explicitly selected directory in this member's workspace.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from pysat.card import CardEnc, EncType


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_probe(source):
    source = source.resolve()
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source.parent / "hard-more"))
    import probe
    return probe


def serialize(raw, extra):
    """Preserve the original body byte-for-byte; replace only its header."""
    end = raw.index(b"\n")
    fields = raw[:end].decode().split()
    assert fields[:2] == ["p", "cnf"]
    old_nv, old_ncl = map(int, fields[2:4])
    maximum = old_nv
    for clause in extra:
        assert clause and 0 not in clause
        maximum = max(maximum, *(abs(x) for x in clause))
    header = f"p cnf {maximum} {old_ncl + len(extra)}\n".encode()
    body = b"".join((" ".join(map(str, clause)) + " 0\n").encode()
                    for clause in extra)
    return header + raw[end + 1:] + body


def grouped(probe, row, form, guards, exact=False, sequential=False):
    """Factor the published support DNF through arm-existence variables.

    s_p -> each spoke in p (and conversely too when exact=True);
    A_i <-> OR_p s_p; and guard -> at least (m-1) of m classified A_i.
    The last bound is max(0, 2-u), u = 3-m.
    """
    import itertools
    from gluing import Family, units, host

    row = probe.geometry[row["id"]]
    fdata = row["family"].copy()
    for key in ("root_kinds", "profile"):
        fdata[key] = tuple(fdata[key])
    family = Family(**fdata)
    fixed = {v for v, in units(family, row["placement"])}
    known = {(v - 1) // 4 for v in fixed if v > 0}
    edge, _ = host(58)
    top = form.nv
    gate = {}
    extra = []
    records = []

    def support_var(opt):
        nonlocal top
        if opt not in gate:
            top += 1
            gate[opt] = top
            extra.extend([-top, lit] for lit in opt)
            if exact and opt:
                extra.append([top, *[-lit for lit in opt]])
            # An empty residual conjunction is true in either variant.
            if not opt:
                extra.append([top])
        return gate[opt]

    for x in sorted(guards):
        color, guard = guards[x]
        arms = []
        arm_records = []
        for b, (n, kind) in enumerate(zip(family.profile, family.root_kinds)):
            if b == color or kind == "-":
                continue
            start = 1 + sum(family.profile[:b])
            spokes = [edge(x, start + i, color) for i in range(n)]
            must = {i for i, lit in enumerate(spokes) if lit in fixed}
            blocked = {i for i, lit in enumerate(spokes)
                       if -lit in fixed or
                       ((lit - 1) // 4 in known and lit not in fixed)}
            opts = tuple(tuple(spokes[i] for i in p if i not in must)
                         for p in probe.catalog(n, kind, b, color)
                         if must.issubset(p) and blocked.isdisjoint(p))
            selectors = [support_var(opt) for opt in opts]
            top += 1
            arm = top
            # Arm variable is exactly the OR of its support certificates.
            extra.extend([-s, arm] for s in selectors)
            extra.append([-arm, *selectors])
            arms.append(arm)
            arm_records.append({"arm": b, "indicator": arm,
                                "supports": len(selectors),
                                "residual_support_sizes": sorted({len(x) for x in opts})})
        # At most one of three arms can have count <=4. Unclassified arms can
        # absorb at most u of the at-least-two 5-counts.
        required = max(0, len(arms) - 1)
        before = len(extra)
        if required:
            if sequential:
                enc = CardEnc.atleast(arms, bound=required, top_id=top,
                                      encoding=EncType.seqcounter)
                top = max(top, enc.nv)
                counter = [[-guard, *clause] for clause in enc.clauses]
            else:
                # m=2,k=1 gives one pair; m=3,k=2 gives three pairs. This is
                # minimal CNF; sequential counters are a separate cost control.
                counter = [[-guard, *pair]
                           for pair in itertools.combinations(arms, required + 1)]
                assert ((len(arms) == 3 and required == 2) or
                        (len(arms) == 2 and required == 1))
            extra.extend(counter)
        records.append({"sender": x, "color": color, "guard": guard,
                        "arms": arm_records, "required": required,
                        "conditional_counter_clauses": len(extra) - before})
    return extra, {"variables": top - form.nv, "top_variable": top,
                   "support_selectors": len(gate), "senders": records}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ranks", default="1200,1300")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    probe = load_probe(args.source)
    summary = []
    for rank in map(int, args.ranks.split(",")):
        row = probe.rows[rank - 1]
        guards = {}
        begin = time.process_time()
        raw, form, direct, old = probe.build(row, guards)
        parent_cpu = time.process_time() - begin
        assert sha(raw) == row["input_sha256"]
        rank_dir = args.out / str(rank)
        rank_dir.mkdir()
        (rank_dir / "stock.cnf").write_bytes(raw)
        policies = {"direct": direct, "old-selectors": old}
        metadata = {"rank": rank, "id": row["id"],
                    "input_sha256": row["input_sha256"],
                    "parent_bytes": len(raw), "parent_variables": form.nv,
                    "parent_clauses": len(form.clauses),
                    "generation_cpu_probe": parent_cpu,
                    "guards": len(guards), "policies": {}}
        details = {}
        for name in ("factored", "factored-exact", "factored-seq"):
            begin = time.process_time()
            extra, info = grouped(probe, row, form, guards,
                                  exact=name == "factored-exact",
                                  sequential=name == "factored-seq")
            policies[name] = extra
            cpu = time.process_time() - begin
            details[name] = info["senders"]
            metadata["policies"][name] = {
                "auxiliary_variables": info["variables"],
                "support_selectors": info["support_selectors"],
                "generation_cpu": cpu,
                "senders_with_requirement": sum(x["required"] > 0 for x in info["senders"]),
                "required_histogram": {str(k): sum(x["required"] == k for x in info["senders"])
                                       for k in (0, 1, 2)},
                "support_count": sum(a["supports"] for x in info["senders"] for a in x["arms"])}
        (rank_dir / "grouped-details.json").write_text(
            json.dumps(details, indent=2, sort_keys=True) + "\n")
        for name, extra in policies.items():
            begin = time.process_time()
            data = serialize(raw, extra)
            cpu = time.process_time() - begin
            path = rank_dir / (name + ".cnf")
            path.write_bytes(data)
            rec = {"clauses_added": len(extra), "bytes": len(data),
                   "sha256": sha(data), "serialization_cpu": cpu}
            metadata["policies"].setdefault(name, {}).update(rec)
        (rank_dir / "build.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        summary.append(metadata)
        print(json.dumps({"rank": rank, "parent": row["input_sha256"],
                          "policies": {k: {q: v[q] for q in
                                           ("clauses_added", "bytes", "sha256")}
                                       for k, v in metadata["policies"].items()}}),
              flush=True)
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
