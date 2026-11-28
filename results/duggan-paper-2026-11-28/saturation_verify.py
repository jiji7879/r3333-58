#!/usr/bin/env python3
"""Strict independent checker for saturation_certify.py's output."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path


class VerificationFailure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationFailure(message)


def load_source(path):
    lines = path.read_text().splitlines()
    require(len(lines) >= 2, f"truncated source: {path}")
    n, k = map(int, lines[0].split())
    require(len(lines) == n + 1, f"wrong row count: {path}")
    a = [list(map(int, line.split())) for line in lines[1:]]
    require(all(len(row) == n for row in a), f"wrong column count: {path}")
    for u in range(n):
        for v in range(n):
            require(0 <= a[u][v] < k, f"bad colour at {u},{v}: {path}")
            require(a[u][v] == a[v][u], f"asymmetry at {u},{v}: {path}")
    return n, k, a


def verify_certificate(repo, out):
    manifest = json.loads((out / "manifest.json").read_text())
    require(manifest.get("format") == "link-saturation-v1", "unknown format")
    require(len(manifest["templates"]) == 8, "manifest must contain eight templates")
    sources = {}
    expected = set()
    for record in manifest["templates"]:
        key = record["key"]
        require(key not in sources, f"duplicate manifest key {key}")
        path = repo / record["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                f"source hash mismatch: {path}")
        n, k, a = load_source(path)
        require((n, k) == (record["order"], record["colours"]) and k == 3,
                f"manifest parameters mismatch: {key}")
        # Independent all-triangles check of every input.
        for u, v, w in itertools.combinations(range(n), 3):
            require(not (a[u][v] == a[u][w] == a[v][w]),
                    f"input has monochromatic triangle: {key} {u,v,w}")
        sources[key] = (n, k, a)
        for u, v in itertools.combinations(range(n), 2):
            for new in range(k):
                if new != a[u][v]:
                    expected.add((key, u, v, new))
        require(len(expected) >= record["expected_witnesses"], "invalid expected count")
    require(len(expected) == 1800, f"expected 1800 obligations, got {len(expected)}")
    seen = {}
    with (out / "witnesses.tsv").open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames == ["key", "u", "v", "new_colour", "witness",
                                      "old_colour", "common_count"], "bad TSV header")
        for line_number, row in enumerate(reader, 2):
            require(None not in row and all(value is not None for value in row.values()),
                    f"malformed row {line_number}")
            key = row["key"]
            require(key in sources, f"unknown key at row {line_number}")
            n, k, a = sources[key]
            u, v, new, w, old, claimed_count = (int(row[name]) for name in
                ["u", "v", "new_colour", "witness", "old_colour", "common_count"])
            require(0 <= u < v < n and 0 <= w < n and w != u and w != v,
                    f"bad vertices at row {line_number}")
            require(0 <= new < k and new != old and a[u][v] == old,
                    f"bad recolouring at row {line_number}")
            obligation = (key, u, v, new)
            require(obligation not in seen, f"duplicate obligation at row {line_number}")
            require(obligation in expected, f"unexpected obligation at row {line_number}")
            require(a[u][w] == a[v][w] == new,
                    f"witness does not close a triangle at row {line_number}")
            common = [x for x in range(n)
                      if x != u and x != v and a[u][x] == a[v][x] == new]
            require(len(common) == claimed_count, f"wrong common_count at row {line_number}")
            seen[obligation] = w
    missing = expected - seen.keys()
    require(not missing, f"missing {len(missing)} obligations; first={sorted(missing)[:1]}")
    require(not (seen.keys() - expected), "extra obligations")
    # Independently record the diameter-two and SRG consequences from the sources.
    summary = {"status": "PASS", "checked_obligations": len(seen), "templates": {}}
    for key, (n, k, a) in sources.items():
        distances = {}
        histogram = collections.Counter()
        for colour in range(k):
            worst = 0
            for source in range(n):
                distance = [-1] * n
                distance[source] = 0
                queue = [source]
                for u in queue:
                    for v in range(n):
                        if v != u and a[u][v] == colour and distance[v] < 0:
                            distance[v] = distance[u] + 1
                            queue.append(v)
                require(all(d >= 0 for d in distance), f"disconnected colour class {key}/{colour}")
                worst = max(worst, max(distance))
            distances[str(colour)] = worst
            require(worst <= 2, f"colour class not diameter-two: {key}/{colour}")
        for (row_key, u, v, new), w in seen.items():
            if row_key == key:
                common_count = sum(x != u and x != v and a[u][x] == a[v][x] == new
                                   for x in range(n))
                histogram[common_count] += 1
        summary["templates"][key] = {
            "diameter_by_colour": distances,
            "common_neighbour_histogram": dict(sorted(histogram.items())),
        }
        if n == 16:
            # All nonedges in each class must have exactly two common neighbours (mu=2).
            for colour in range(k):
                for u, v in itertools.combinations(range(n), 2):
                    if a[u][v] != colour:
                        require(sum(x != u and x != v and a[u][x] == a[v][x] == colour
                                    for x in range(n)) == 2,
                                f"SRG mu=2 failure: {key}/{colour}/{u,v}")
            require(set(histogram) == {2}, f"unexpected K16 histogram: {key}")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        summary = verify_certificate(args.repo, args.out)
    except (VerificationFailure, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
    text = json.dumps(summary, indent=2) + "\n"
    if args.report:
        args.report.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
