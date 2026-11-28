#!/usr/bin/env python3
"""Generate an explicit triangle-witness certificate for link saturation."""
import argparse
import collections
import hashlib
import itertools
import json
from pathlib import Path

TEMPLATES = [
    ("16U", "artifacts/k16_template_U_aut160_m4.col"),
    ("16T", "artifacts/k16_template_T_aut32_m4.col"),
    ("15U", "artifacts/k15_template_Uminus_aut10_m4.col"),
    ("15T", "artifacts/k15_template_Tminus_aut2_m4.col"),
    ("16U-link", "artifacts/k16_link_U_m5.col"),
    ("16T-link", "artifacts/k16_link_T_m5.col"),
    ("15U-link", "artifacts/k15_link_Uminus_m5.col"),
    ("15T-link", "artifacts/k15_link_Tminus_m5.col"),
]
HEADER = ["key", "u", "v", "new_colour", "witness", "old_colour", "common_count"]


def read_colouring(path):
    lines = path.read_text().splitlines()
    n, k = map(int, lines[0].split())
    assert len(lines) == n + 1
    matrix = [list(map(int, line.split())) for line in lines[1:]]
    assert all(len(row) == n for row in matrix)
    return n, k, matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {"format": "link-saturation-v1", "templates": []}
    rows = []
    report = {"total_witnesses": 0, "templates": {}}
    for key, relative in TEMPLATES:
        path = args.repo / relative
        raw = path.read_bytes()
        n, k, a = read_colouring(path)
        assert k == 3 and n in (15, 16)
        # The inputs themselves must be good colourings.
        for u, v, w in itertools.combinations(range(n), 3):
            assert not (a[u][v] == a[u][w] == a[v][w]), (key, u, v, w)
        histogram = collections.Counter()
        for u, v in itertools.combinations(range(n), 2):
            old = a[u][v]
            for new in range(k):
                if new == old:
                    continue
                common = [w for w in range(n)
                          if w != u and w != v and a[u][w] == a[v][w] == new]
                assert common, ("unsaturated", key, u, v, new)
                histogram[len(common)] += 1
                rows.append([key, u, v, new, common[0], old, len(common)])
        expected = n * (n - 1) * (k - 1) // 2
        assert len(rows) >= expected
        manifest["templates"].append({
            "key": key, "path": relative, "sha256": hashlib.sha256(raw).hexdigest(),
            "order": n, "colours": k, "expected_witnesses": expected,
        })
        report["templates"][key] = {
            "path": relative, "sha256": hashlib.sha256(raw).hexdigest(),
            "witnesses": expected,
            "common_neighbour_histogram": dict(sorted(histogram.items())),
        }
        report["total_witnesses"] += expected
    assert len(rows) == report["total_witnesses"] == 1800
    with (args.out / "witnesses.tsv").open("w") as stream:
        stream.write("\t".join(HEADER) + "\n")
        for row in rows:
            stream.write("\t".join(map(str, row)) + "\n")
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.out / "generator-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
