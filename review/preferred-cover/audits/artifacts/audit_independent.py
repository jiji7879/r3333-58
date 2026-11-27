#!/usr/bin/env python3
"""Standalone K58 artifact audit: no imports from the supplied encoder.

Rebuilds all 608 local CNFs from elementary triangle/ordering constraints,
checks their receipt hashes, and replays every RUP proof sequentially with
`drat-trim -i -U` (without `-w`). Also validates every SAT arm witness and
recomputes the roster/index totals directly from TSV/JSON inputs.
No SAT/SMT solver is called.
"""
import csv
import gzip
import hashlib
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
B = ROOT / "extracted/K58_wall_10k_batches"
R = B / "results"
SCRATCH = ROOT / ".scratch"
CHECKER = B / "tools/drat-trim"
SIZES = (11, 12, 13, 14)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value, newline=True):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return data + (b"\n" if newline else b"")


def table(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def jsonl_gz(path):
    return [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]


def dimacs(top, clauses):
    return (f"p cnf {top} {len(clauses)}\n".encode() +
            b"".join((" ".join(map(str, clause)) + " 0\n").encode()
                     for clause in clauses))


def pentagon_color(i, j):
    return 1 if (j - i) % 5 in (1, 4) else 2


PENTAGON_EDGES = tuple(combinations(range(5), 2))
WORDS = sorted("".join(map(str, word)) for word in product(range(3), repeat=5)
               if all(not (word[i] == word[j] == pentagon_color(i, j))
                      for i, j in PENTAGON_EDGES))
assert len(WORDS) == 76


def arm_base(n):
    """One of three colors per edge, no monochrome triangle, fixed pentagon."""
    edges = tuple(combinations(range(n), 2))
    ids = {edge: 3 * i + 1 for i, edge in enumerate(edges)}
    clauses = []
    for first in ids.values():
        colors = (first, first + 1, first + 2)
        clauses.append(list(colors))
        clauses.extend([[-a, -b] for a, b in combinations(colors, 2)])
    for i, j, k in combinations(range(n), 3):
        for color in range(3):
            clauses.append([-ids[i, j] - color, -ids[i, k] - color,
                            -ids[j, k] - color])
    for i, j in PENTAGON_EDGES:
        clauses.append([ids[i, j] + pentagon_color(i, j)])
    return 3 * len(edges), edges, ids, clauses


def sorted_base(n):
    """Nondecreasing outside words, using equality prefixes between neighbors."""
    top, edges, ids, old = arm_base(n)
    clauses = list(old)
    for x in range(5, n - 1):
        y = x + 1
        prefix = None
        for site in range(5):
            guard = [] if prefix is None else [-prefix]
            for low in range(3):
                for high in range(low + 1, 3):
                    clauses.append([*guard, -ids[site, x] - high,
                                    -ids[site, y] - low])
            if site == 4:
                break
            top += 1
            equal = top
            if prefix is not None:
                clauses.append([-equal, prefix])
            for color in range(3):
                a, b = ids[site, x] + color, ids[site, y] + color
                clauses.append([*guard, -a, -b, equal])
                clauses.append([-equal, -a, b])
            prefix = equal
    return top, edges, ids, clauses


def word_units(ids, vertex, word):
    return [ids[i, vertex] + int(color) for i, color in enumerate(word)]


def sorted_query(n, second, allowed):
    top, edges, ids, clauses = sorted_base(n)
    clauses = clauses + [[v] for v in word_units(ids, 6, second)]
    clauses += [[-v for v in word_units(ids, 5, first)] for first in allowed]
    return dimacs(top, clauses)


def preferred_query(n, second, preferred):
    top, edges, ids, clauses = sorted_base(n)
    site, occurrence = {}, {}
    for x in range(5, n):
        choices = []
        for word in WORDS:
            top += 1
            site[x, word] = top
            choices.append(top)
            units = word_units(ids, x, word)
            clauses.extend([[-top, unit] for unit in units])
            clauses.append([top, *[-unit for unit in units]])
        clauses.append(choices)
    for word in WORDS:
        top += 1
        occurrence[word] = top
        clauses.extend([[-site[x, word], top] for x in range(5, n)])
        clauses.append([-top, *[site[x, word] for x in range(5, n)]])
    for first, second_word in preferred:
        if first != second_word:
            clauses.append([-occurrence[first], -occurrence[second_word]])
        else:
            clauses.extend([[-site[x, first], -site[x + 1, first]]
                            for x in range(5, n - 1)])
    clauses.extend([[v] for v in word_units(ids, 6, second)])
    return dimacs(top, clauses)


def validate_witness(n, first, second, model, edges, catalogs):
    assert len(model) == len(edges) and set(model) <= set("012")
    colors = dict(zip(edges, map(int, model)))
    for i, j, k in combinations(range(n), 3):
        assert not (colors[i, j] == colors[i, k] == colors[j, k])
    for i, j in PENTAGON_EDGES:
        assert colors[i, j] == pentagon_color(i, j)
    words = tuple("".join(str(colors[i, x]) for i in range(5))
                  for x in range(5, n))
    assert words == tuple(sorted(words)) and words[:2] == (first, second)
    options = set(combinations(words, 2)) & catalogs[n]
    assert options
    return min(options)


def main():
    out = {"checker": [str(CHECKER), "QUERY", "PROOF", "-i", "-U"],
           "sat_solver_calls": 0}
    pair_index = table(B / "inputs/pair-class-index.tsv.gz")
    assert len(pair_index) == 5776
    observed_words = {r[k] for r in pair_index for k in ("word_1", "word_2")}
    assert observed_words == set(WORDS)
    assert len({(r["word_1"], r["word_2"]) for r in pair_index}) == 5776
    live = {n: {(r["word_1"], r["word_2"]) for r in pair_index
                if r[f"arm_{n}"] == "SAT"} for n in SIZES}
    raw_counts = {n: len(live[n]) for n in SIZES}
    assert raw_counts == {11: 5361, 12: 5361, 13: 5361, 14: 5190}
    out["raw_pairs_per_size"] = raw_counts

    capacity = table(R / "capacity.tsv.gz")
    capacity_keys = defaultdict(set)
    capacity_stage = {}
    for row in capacity:
        n, key = int(row["n"]), (row["w"], row["z"])
        assert key not in capacity_keys[n]
        capacity_keys[n].add(key)
        capacity_stage[n, key] = row["stage"]
    assert {n: capacity_keys[n] for n in SIZES} == live
    survivors = {n: {key for (size, key), stage in capacity_stage.items()
                     if size == n and stage == "SURVIVES"} for n in SIZES}
    survivor_counts = {n: len(survivors[n]) for n in SIZES}
    assert survivor_counts == {11: 1308, 12: 1249, 13: 743, 14: 651}
    out["capacity_survivors_per_size"] = survivor_counts

    outcomes = table(R / "sorted-outcomes.tsv.gz")
    assert len(outcomes) == sum(survivor_counts.values()) == 3951
    outcome_map = {}
    for row in outcomes:
        n, key = int(row["n"]), (row["w"], row["z"])
        assert key in survivors[n] and (n, key) not in outcome_map
        outcome_map[n, key] = row
    assert {key for key in outcome_map} == {
        (n, key) for n in SIZES for key in survivors[n]}
    sat = {n: {key for (size, key), row in outcome_map.items()
               if size == n and row["status"] == "SAT"} for n in SIZES}
    sat_counts = {n: len(sat[n]) for n in SIZES}
    assert sat_counts == {11: 1272, 12: 1049, 13: 692, 14: 317}
    assert Counter(row["status"] for row in outcomes) == {
        "SAT": 3330, "REFUTATION_CANDIDATE": 621}
    out["sorted_SAT_per_size"] = sat_counts

    catalogs = {}
    catalog_history = {}
    for n in SIZES:
        data = json.loads((R / "preferred" / f"{n}.json").read_bytes())
        pairs = [tuple(pair) for pair in data["pairs"]]
        assert pairs == sorted(set(pairs)) and set(pairs) <= sat[n]
        assert data["n"] == n and isinstance(data["history"], list)
        catalogs[n], catalog_history[n] = set(pairs), data["history"]
    preferred_counts = {n: len(catalogs[n]) for n in SIZES}
    assert preferred_counts == {11: 1214, 12: 941, 13: 530, 14: 156}
    out["preferred_pairs_per_size"] = preferred_counts
    out["catalog_discovery_rounds"] = catalog_history

    owner_seen = defaultdict(set)
    validated_models = 0
    for (n, (first, second)), row in sorted(outcome_map.items()):
        first_edges = arm_base(n)[1]
        if row["status"] == "SAT":
            owner_seen[n].add(validate_witness(
                n, first, second, row["model"], first_edges, catalogs))
            validated_models += 1
        else:
            assert row["status"] == "REFUTATION_CANDIDATE" and not row["model"]
    assert validated_models == 3330
    assert {n: owner_seen[n] for n in SIZES} == catalogs
    out["validated_complete_arm_models"] = validated_models
    out["preferred_jobs_with_independently_checked_owner_witness"] = {
        n: len(owner_seen[n]) for n in SIZES}

    # Independently regenerate each local CNF, authenticate its proof bytes,
    # and invoke the C checker directly, sequentially, in strict RUP mode.
    proof_replays = warning_receipts = 0
    proof_bytes = {"sorted": 0, "preferred": 0}
    query_bytes = {"sorted": 0, "preferred": 0}
    expected_sorted_proofs = {(n, z) for n in SIZES for z in WORDS}
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        cnf, proof = Path(tmp) / "query.cnf", Path(tmp) / "proof.rup"
        for family in ("sorted", "preferred"):
            dest = R / f"{family}-proofs"
            receipts = sorted(dest.glob("*.json"))
            proofs = sorted(dest.glob("*.rup.gz"))
            assert len(receipts) == len(proofs) == 304
            assert {p.name.removesuffix(".rup.gz") for p in proofs} == {
                p.stem for p in receipts}
            seen = set()
            for receipt_path in receipts:
                receipt = json.loads(receipt_path.read_bytes())
                n, second = int(receipt["n"]), receipt["second"]
                seen.add((n, second))
                stem = f"{n}-{second}"
                assert receipt_path.stem == stem
                raw_proof = gzip.decompress((dest / f"{stem}.rup.gz").read_bytes())
                if family == "sorted":
                    allow = receipt["covered_first_words"]
                    expected = sorted(first for first, z in sat[n] if z == second)
                    assert allow == expected
                    query = sorted_query(n, second, allow)
                    assert receipt["query_sha256"] == sha(query)
                    assert receipt["proof_sha256"] == sha(raw_proof)
                    assert receipt["proof_bytes"] == len(raw_proof)
                else:
                    query = preferred_query(
                        n, second, sorted(catalogs[n]))
                    assert receipt["query"] == sha(query)
                    assert receipt["proof"] == sha(raw_proof)
                    assert receipt["bytes"] == len(raw_proof)
                proof_bytes[family] += len(raw_proof)
                query_bytes[family] += len(query)
                cnf.write_bytes(query)
                proof.write_bytes(raw_proof)
                run = subprocess.run([str(CHECKER), str(cnf), str(proof),
                                      "-i", "-U"], stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
                assert run.returncode == 0 and b"s VERIFIED" in run.stdout, (
                    family, stem, run.returncode, run.stdout[-2000:])
                warning_receipts += int(b"WARNING" in run.stdout)
                proof_replays += 1
            assert seen == expected_sorted_proofs
    out["strict_local_RUP_replays"] = proof_replays
    out["checker_outputs_containing_WARNING"] = warning_receipts
    out["proof_bytes"] = proof_bytes
    out["regenerated_query_bytes"] = query_bytes

    # Roster identity, physical arm binding, and contiguous global job indices.
    roster_list = jsonl_gz(B / "inputs/wall.jsonl.gz")
    roster = {row["id"]: row for row in roster_list}
    roster_raw = gzip.decompress((B / "inputs/wall.jsonl.gz").read_bytes())
    assert len(roster_list) == len(roster) == 11585
    assert sha(roster_raw) == "d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc"
    for row in roster_list:
        identity = {key: row[key] for key in ("family", "placement", "charge")}
        assert sha(canonical(identity, newline=False)) == row["id"]
    campaign_rows = table(B / "inputs/campaign.tsv")
    campaign = {row["row_id"]: row for row in campaign_rows}
    bindings = {row["id"]: row for row in jsonl_gz(
        B / "inputs/physical-bindings.jsonl.gz")}
    assert len(campaign) == len(bindings) == len(roster)
    assert campaign.keys() == bindings.keys() == roster.keys()
    queue = table(R / "row-queue.tsv.gz")
    assert len(queue) == 11585
    assert [row["row_id"] for row in queue] == sorted(roster)
    d_sample = table(R / "preferred-sample.tsv.gz")
    d_counts = Counter(row["row_id"] for row in d_sample)
    assert len(d_sample) == 10000
    assert len({(r["row_id"], r["w"], r["z"]) for r in d_sample}) == 10000
    position = 0
    arms_count = Counter()
    for row in queue:
        rid, n = row["row_id"], int(row["arm"])
        source, binding = campaign[rid], bindings[rid]
        arm = binding["pentagons"][int(source["arm_index"])]
        assert arm["size"] == n == int(source["nominated_arm_size"])
        outside = [v for v in range(arm["block_start"], arm["block_start"] + n)
                   if v not in arm["pentagon"]]
        assert [row["outside_x"], row["outside_y"]] == list(map(str, outside[:2]))
        assert row["ordered_pentagon"] == ",".join(map(str, arm["pentagon"]))
        assert row["profile"] == source["profile"] and row["branch"] == source["branch"]
        assert row["root_status"] == source["root_status"] == source["ledger"] == "OPEN"
        assert int(row["unrestricted_live_pairs"]) == raw_counts[n]
        assert int(row["admitted_by_column_rule"]) == survivor_counts[n]
        assert int(row["possible_two_smallest"]) == sat_counts[n]
        assert int(row["preferred_pairs"]) == preferred_counts[n]
        assert int(row["index_begin"]) == position
        position += preferred_counts[n]
        assert int(row["index_end_exclusive"]) == position
        assert int(row["preferred_jobs_probed"]) == d_counts[rid]
        arms_count[n] += 1
    assert arms_count == {14: 7543, 13: 3374, 12: 628, 11: 40}
    totals = {
        "raw": sum(arms_count[n] * raw_counts[n] for n in SIZES),
        "capacity": sum(arms_count[n] * survivor_counts[n] for n in SIZES),
        "sorted": sum(arms_count[n] * sat_counts[n] for n in SIZES),
        "preferred": sum(arms_count[n] * preferred_counts[n] for n in SIZES),
    }
    assert totals == {"raw": 60817332, "capacity": 8254067,
                      "sorted": 5435591, "preferred": 3604436}
    assert position == totals["preferred"]
    out["wall_rows"] = dict(sorted(arms_count.items()))
    out["weighted_job_totals"] = totals
    out["all_whole_rows_OPEN"] = 11585
    out["representative_scheduling_reduction_percent"] = (
        100 * (1 - totals["preferred"] / totals["raw"]))
    summary = json.loads((R / "summary.json").read_bytes())
    assert summary["original_cells"] == totals["raw"]
    assert summary["forward_queue"] == totals["preferred"]
    assert summary["original_rows"] == 11585 and summary["physical_proofs"] == 42
    assert sha(gzip.decompress((R / "trials.tsv.gz").read_bytes())) == sha(
        (ROOT / "inputs/K58_40000_pattern_trials.tsv").read_bytes())
    out["external_TSV_equals_bundled_trials_payload"] = True

    # A negative control on a satisfiable no-blocker query. (The corresponding
    # all-blocked preferred query above is already UNSAT by unit propagation,
    # so it is not a useful negative control.)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        q, p = Path(tmp) / "q.cnf", Path(tmp) / "empty.rup"
        q.write_bytes(sorted_query(11, "00000", []))
        p.write_bytes(b"")
        negative = subprocess.run([str(CHECKER), str(q), str(p), "-i", "-U"],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert b"s VERIFIED" not in negative.stdout
        out["empty_proof_negative_control"] = {
            "returncode": negative.returncode,
            "output": negative.stdout.decode(errors="replace")[-2000:]}

    (ROOT / "independent-results.json").write_bytes(canonical(out))
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
