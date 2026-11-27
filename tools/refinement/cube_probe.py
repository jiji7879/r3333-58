#!/usr/bin/env python3
"""Small proof-carrying refinement prototype; bounded local C&C probes."""
import argparse
import collections
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class Prototype:
    def __init__(self, base: Path, checker: Path, output: Path, max_calls: int):
        self.base = base.resolve()
        self.checker = checker.resolve()
        self.check_sequence = 0
        self.output = output.resolve()
        self.output.mkdir(parents=True, exist_ok=False)
        sys.path.insert(0, str(self.base))
        import common
        from arm_pairs import base as arm_base
        from arm_catalog import decode
        import campaign_solver
        import edge_domains
        import propagate_rules
        import revised
        self.arm_base = arm_base
        self.decode = decode
        self.cs = campaign_solver
        self.common = common
        self.edge_domains = edge_domains
        self.propagate_rules = propagate_rules
        self.revised = revised
        self.counter = 0
        self.max_calls = max_calls
        self.records = []
        self.rules = []
        self.checked_stock = []

    def initial(self):
        from new_names import labels
        chosen = []
        for n in (11, 12, 13, 14):
            candidates = []
            for pair in labels(n, "revised"):
                doc = self.cs.rule(n, pair)
                if "empty" in doc or not doc["pivot"]:
                    continue
                live = tuple(sorted(map(int, doc["branches"])))
                if len(live) != 2 or not all(doc["branches"][str(c)]["forbidden"] for c in live):
                    continue
                h = sha((self.base.name + ":" + str(n) + ":" + "-".join(pair)).encode())
                candidates.append((h, n, pair))
            if not candidates:
                raise ValueError("no nonempty binary candidate for arm " + str(n))
            _, n, pair = min(candidates)
            records = list(self.base.glob("campaign/physical-rules/" + str(n) + "/*.json"))
            rids = [json.loads(p.read_bytes()) for p in records]
            matches = [r["row_id"] for r in rids if tuple(r["pair"]) == pair]
            if len(matches) != 1:
                raise ValueError((n, pair, matches))
            chosen.append({"n": n, "pair": list(pair), "rid": matches[0]})
        return chosen

    def rec(self, n, pair):
        return self.cs.rule(n, tuple(pair))

    def full_base(self, rid, pair):
        return self.revised.export(rid, tuple(pair))[0]

    def append_negative(self, clauses, ids, excluded):
        for u, v, c in excluded:
            clauses.append([-ids[u, v] - c])

    def source_query(self, n, pair, branch_color, edge, color, extra_cube=()):
        top, clauses = self.edge_domains.parent(n, tuple(pair), "revised")
        ids = self.arm_base(n)[1]
        rec = self.rec(n, pair)
        self.append_negative(clauses, ids, rec["root"]["forbidden"])
        # Preserve the established root-negative, pivot, child-negative order.
        clauses.append([ids[tuple(rec["pivot"])] + int(branch_color)])
        branch = rec["branches"][str(branch_color)]
        self.append_negative(clauses, ids, branch["forbidden"])
        assigned = [] if edge is None else [(edge, color)]
        extra_assignment = [[ids[tuple(e)] + int(c)] for e, c in (*assigned, *extra_cube)]
        return self.encode_query(top, clauses + extra_assignment)

    def encode_query(self, top, clauses):
        from problem import encode_clauses
        return f"p cnf {top} {len(clauses)}\n".encode() + encode_clauses(clauses)

    def get_units(self, rid, n, pair, branch_color, edge, color, extra_cube=()):
        rec = self.rec(n, pair)
        edge_fn, _, _, _ = self.cs.mapping(rid, n)
        units = []
        for u, v, c in rec["root"]["forbidden"]:
            units.append([-edge_fn(u, v, c)])
        rec_branch = rec["branches"][str(branch_color)]
        units.append([edge_fn(*rec["pivot"], int(branch_color))])
        for u, v, c in rec_branch["forbidden"]:
            units.append([-edge_fn(u, v, c)])
        if edge is not None:
            units.append([edge_fn(*edge, int(color))])
        for e, c in extra_cube:
            units.append([edge_fn(*e, int(c))])
        return units

    def solve_local(self, rid, n, pair, branch_color, edge, color, extra_cube=()):
        self.counter += 1
        if self.counter > self.max_calls:
            raise RuntimeError("local C&C call budget exceeded")
        raw = self.source_query(n, pair, branch_color, edge, color, extra_cube)
        tmp = self.output / "tmp"
        tmp.mkdir(exist_ok=True)
        q = tmp / f"local-{self.counter}.cnf"
        pf = tmp / f"local-{self.counter}.drat"
        q.write_bytes(raw)
        started = time.monotonic()
        try:
            run = subprocess.run([str(self.base / "tools/kissat"), "--plain", "-q", str(q), str(pf)],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        except subprocess.TimeoutExpired:
            return {"status": "OPEN", "reason": "local timeout", "query_sha256": sha(raw)}
        rec = {"local_call": self.counter, "seconds": time.monotonic() - started,
               "query_sha256": sha(raw), "returncode": run.returncode}
        if run.returncode == 20:
            proof = pf.read_bytes()
            rec.update(status="UNSAT_LOCAL_QUERY", proof_sha256=sha(proof), proof_bytes=len(proof))
            return rec, raw, proof
        if run.returncode == 10:
            model_text = b"\n".join(x for x in run.stdout.splitlines() if x.startswith(b"v "))
            values = [int(x) for line in model_text.splitlines() for x in line.split()[1:] if int(x)]
            model = self.decode(n, values)
            self.edge_domains.valid(n, tuple(pair), "revised", model)
            rec["status"] = "SAT_LOCAL_WITNESS"
            rec["model"] = model
            return rec, model
        return {"status": "OPEN", "reason": f"solver rc={run.returncode}", "query_sha256": sha(raw)}

    def lift_and_check(self, rid, n, local_proof, local_units, target_units, expected=None):
        from compile import append
        full = self.full_base(rid, self.current_pair)
        _, image, prefix, root_sha = self.cs.mapping(rid, n)
        assert len(set(image)) == len(image) and image[0] == 0 and len(image) > 1
        raw = append(full, target_units)[1]
        temp = self.output / "tmp"
        temp.mkdir(exist_ok=True)
        m = temp / "map"
        source = temp / "source.drat"
        lifted = temp / "lifted.drat"
        m.write_text(str(len(image) - 1) + "\n" + " ".join(map(str, image[1:])) + "\n")
        source.write_bytes(local_proof)
        run = subprocess.run([str(self.base / "tools/relabel"), str(m), str(source), str(lifted)],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        if run.returncode:
            raise RuntimeError(run.stdout)
        proof = prefix + lifted.read_bytes()
        self.check_sequence += 1
        case_dir = self.output / "full" / str(self.check_sequence)
        case_dir.mkdir(parents=True, exist_ok=True)
        raw_path = case_dir / "query.cnf"
        proof_path = case_dir / "proof.drat"
        log_path = case_dir / "check.log"
        raw_path.write_bytes(raw)
        proof_path.write_bytes(proof)
        cmd = [str(self.checker), str(raw_path), str(proof_path), "-i", "-U", "-t", "300"]
        started = time.monotonic()
        call = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
        log_path.write_bytes(call.stdout)
        good = call.returncode == 0 and call.stdout.count(b"s VERIFIED") == 1 and b"WARNING" not in call.stdout.upper()
        receipt = {"query": sha(raw), "proof": sha(proof), "bytes": len(proof),
                   "returncode": call.returncode, "warnings": b"WARNING" in call.stdout.upper(),
                   "flags": ["-i", "-U", "-t", "300"], "check_seconds": time.monotonic() - started,
                   "original_parent": root_sha, "verified": good, "log": str(log_path.relative_to(self.output))}
        if expected is not None:
            assert receipt["query"] == expected
        if not good:
            raise RuntimeError(receipt)
        return raw, proof, receipt

    def validate_stock(self, rid, n, pair):
        """Verify all pre-existing root/branch premises before learning new rules."""
        record = self.rec(n, pair)
        memo = json.loads((self.base / f"campaign/physical-rules/{n}/{'-'.join(pair)}.json").read_text())
        from compile import append
        from common import host, physical, sha as csha
        from arm_pairs import base
        _, image, prefix, parent_sha = self.cs.mapping(rid, n)
        full = self.full_base(rid, pair)
        assert len(set(image)) == len(image)
        _, arm, _, outside = self.common.source(rid)
        edge_fn, _, _, _ = self.cs.mapping(rid, n)
        out = []
        for name, state, pivot in [("root", record["root"], None)] + [
            (color, record["branches"][color], [*record["pivot"], int(color)]) for color in sorted(record["branches"])
        ]:
            chosen = None if pivot is None else int(pivot[-1])
            units = [[edge_fn(*pivot)]] if pivot is not None else []
            units.append([edge_fn(*v) for v in state["forbidden"]])
            local = gzip.decompress((self.base / "campaign/propagated/revised" / str(n) /
                 ("-".join(pair) + "." + name + ".rup.gz")).read_bytes())
            assert csha(local) == state["proof"]["proof"]
            raw = append(full, units)[1]
            _, raw_image, raw_prefix, _ = self.cs.mapping(rid, n)
            # Map the local proof with the exact same source as the established physical transport.
            lifted = self.lift_and_check(rid, n, local, None, units,
                                         expected=next(c["query"] for c in memo["checks"] if c["case"] == name)
            )
            expected = next(c for c in memo["checks"] if c["case"] == name)
            assert lifted[2]["proof"] == expected["lifted"] and lifted[2]["bytes"] == expected["bytes"]
            out.append({"case": name, "query": expected["query"], "proof": expected["lifted"]})
        self.checked_stock.append({"rid": rid, "n": n, "pair": list(pair), "checks": out})
        return out

    def candidates(self, rec, branch_color):
        # Compute domains from the supplied checked phase, not from a fast heuristic.
        from arm_pairs import base
        es = base(rec["n"])[0]
        inherited = self.propagate_rules.check_phase(rec["n"], tuple(self.current_pair), "revised", rec["root"], None, None,
            {e: {0, 1, 2} for e in self.propagate_rules.candidates(rec["n"])}, True)
        child = rec["branches"][str(branch_color)]
        pivot = tuple(rec["pivot"])
        current = self.propagate_rules.check_phase(rec["n"], tuple(self.current_pair), "revised", child, pivot, branch_color, inherited, True)
        rec_pivot = tuple(rec["pivot"])
        return [(e, sorted(current[e])) for e in self.propagate_rules.candidates(rec["n"])
                if e != rec_pivot and len(current[e]) == 2]

    def probe_label(self, chosen):
        n, pair, rid = chosen["n"], tuple(chosen["pair"]), chosen["rid"]
        self.current_n, self.current_pair, self.current_rid = n, pair, rid
        rec = self.rec(n, pair)
        print("stock", n, pair, rid[:12], flush=True)
        self.validate_stock(rid, n, pair)
        full = self.full_base(rid, pair)
        out = {"n": n, "pair": list(pair), "rid": rid, "base_representative": sha(full), "outcomes": []}
        for color in sorted(map(int, rec["branches"])):
            branch = rec["branches"][str(color)]
            extra = self.get_units(rid, n, pair, color, None, None)
            from compile import append
            raw = append(full, extra)[1]
            expected, info = self.cs.strengthened(rid, pair, color)
            assert raw == expected
            found = self.candidates(rec, color)
            result = {"branch_color": color, "binary_candidates": len(found), "rules": []}
            for edge, colors in found[:1]:
                # Candidate refinement: refute each member of the two-valued domain.
                outcomes = []
                poses = []
                for candidate_color in colors:
                    raw_local = self.source_query(n, pair, color, edge, candidate_color)
                    sat = self.solve_local(rid, n, pair, color, edge, candidate_color)
                    if sat[0]["status"] == "UNSAT_LOCAL_QUERY":
                        units = self.get_units(rid, n, pair, color, edge, candidate_color)
                        full2 = self.lift_and_check(rid, n, sat[2], None, units)
                        outcomes.append({"color": candidate_color, "sat": False, "check": full2[2]})
                    elif sat[0]["status"] == "SAT_LOCAL_WITNESS":
                        poses.append(candidate_color)
                        outcomes.append({"color": candidate_color, "sat": True, "model": sat[1]})
                    else:
                        raise RuntimeError(sat[0])
                if len(poses) == 1:
                    forced = poses[0]
                    rule = {"kind": "conditional-forced-value", "source_cube": [n, pair, color, list(edge)],
                            "branch_color": color, "edge": list(edge), "forced_color": forced, "excluded": []}
                    # Recheck both second-pivot alternatives as explicit full query obligations.
                    for candidate_color in colors:
                        if candidate_color == forced:
                            continue
                        raw_local = self.source_query(n, pair, color, edge, candidate_color)
                        solver_result = self.solve_local(rid, n, pair, color, edge, candidate_color)
                        assert solver_result[0]["status"] == "UNSAT_LOCAL_QUERY"
                        target = self.get_units(rid, n, pair, color, edge, candidate_color)
                        rule["excluded"].append({"edge": list(edge), "color": candidate_color,
                                                 "local_result": solver_result[0]})
                    result["rules"].append({"edge": list(edge), "forced": forced,
                                             "excluded": [c for c in colors if c != forced],
                                             "full_checks": outcomes,
                                             "refinement": "replace only after every excluded sibling is refuted"})
                    print("  learned", color, edge, "=>", forced, flush=True)
                elif len(poses) == 0:
                    result["rules"].append({"edge": list(edge), "forced": None, "meaning": "all candidate children refuted"})
                else:
                    result["rules"].append({"edge": list(edge), "forced": None, "meaning": "two unresolved children remain"})
            out["outcomes"].append(result)
        return out


    def probe_ternary(self, chosen):
        n, pair, rid = chosen["n"], tuple(chosen["pair"]), chosen["rid"]
        self.current_n, self.current_pair, self.current_rid = n, pair, rid
        rec = self.rec(n, pair)
        output = {"n": n, "pair": list(pair), "rid": rid, "outcomes": []}
        for branch_color in sorted(map(int, rec["branches"])):
            candidates = self.candidates(rec, branch_color)
            if len(candidates) < 3:
                output["outcomes"].append({"branch_color": branch_color, "skipped": "fewer than three second-pivot candidates"})
                continue
            first, second, third = candidates[:3]
            for c1 in first[1][:2]:
                for c2 in second[1][:2]:
                    outcomes = []
                    for c3 in third[1]:
                        cube = [(first[0], c1), (second[0], c2), (third[0], c3)]
                        result = self.solve_local(rid, n, pair, branch_color, None, None, cube)
                        if result[0]["status"] == "UNSAT_LOCAL_QUERY":
                            target = self.get_units(rid, n, pair, branch_color, None, None, cube)
                            lifted = self.lift_and_check(rid, n, result[2], None, target)
                            outcomes.append({"cube": [list(x) for x in cube], "sat": False, "check": lifted[2]})
                        elif result[0]["status"] == "SAT_LOCAL_WITNESS":
                            outcomes.append({"cube": [list(x) for x in cube], "sat": True})
                        else:
                            raise RuntimeError(result[0])
                    feasible = [t["cube"][2][1] for t in outcomes if t["sat"]]
                    outcome_record = {"n": n, "pair": list(pair), "rid": rid,
                        "branch_color": branch_color,
                        "guard": [[list(first[0]), c1], [list(second[0]), c2]],
                        "third_edge": list(third[0]), "tests": outcomes}
                    if len(feasible) == 1:
                        target = feasible[0]
                        extra = self.get_units(rid, n, pair, branch_color, None, None,
                                               [(first[0], c1), (second[0], c2), (third[0], target)])
                        from compile import append
                        refined = append(self.full_base(rid, pair), extra)[1]
                        refinement = {"kind": "CONDITIONAL_VALUE_REFINEMENT",
                            "parent": {"n": n, "pair": list(pair), "rid": rid,
                                       "representative": self.common.sha(self.full_base(rid, pair))},
                            "branch_color": branch_color,
                            "guard": [[list(first[0]), c1], [list(second[0]), c2]],
                            "forced_value": target,
                            "refined_query": self.common.sha(refined),
                            "excluded_checks": [t["check"] for t in outcomes if not t["sat"]],
                            "remaining_status": "OPEN_UNKNOWN",
                            "not_parent_or_row_closure": True}
                        self.rules.append(refinement)
                        outcome_record["refinement"] = refinement
                    outcome_record["locally_feasible_values"] = feasible
                    output["outcomes"].append(outcome_record)
        return output["outcomes"]

    def run(self):
        chosen = self.initial()
        print(json.dumps(chosen), flush=True)
        reports = []
        for item in chosen:
            reports.append(self.probe_label(item))
        ternary = []
        for item in chosen:
            ternary.extend(self.probe_ternary(item))
        summary = {"schema": "refinement-cube-and-conquer-pilot/v2", "local_solver_calls": self.counter,
                   "selected": chosen, "rules": self.rules, "reports": reports, "ternary_outcomes": ternary}
        (self.output / "summary.json").write_bytes(canonical(summary))
        print(json.dumps({"local_solver_calls": self.counter, "rules": self.rules}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("campaign", type=Path)
    p.add_argument("--checker", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-calls", type=int, default=48)
    args = p.parse_args()
    proto = Prototype(args.campaign, args.checker, args.out, args.max_calls)
    proto.run()


if __name__ == "__main__":
    main()
