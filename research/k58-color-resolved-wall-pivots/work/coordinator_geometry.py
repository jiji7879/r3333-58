#!/usr/bin/env python3
"""Check physical template edges and exact sender domains on every frozen row."""
import gzip, itertools, json, time
from pathlib import Path
from audit_bindings import edge_literal, template
from audit_transport import physical_units, premises, encode


def main():
    base = Path(__file__).resolve().parents[3] / ".scratch/color-wall-v1/base"
    started = time.monotonic()
    wall = {r["id"]: r for r in map(json.loads, gzip.open(base / "wall.jsonl.gz", "rt"))}
    catalog = json.load(gzip.open(base / "full-wall.json.gz"))
    checked = domains = 0
    support_sites = free_sites = 0
    for binding in catalog["bindings"]:
        rid, case_index = binding[:2]
        if case_index is None:
            continue
        _, _, sender, offset, pivot_literal = binding
        case = catalog["cases"][case_index]
        units = physical_units(wall[rid])
        raw = b"p cnf 6612 0\n" + encode(units)
        pins, denied = premises(raw)
        escape, marked = case["arm_color"], case["marked_color"]
        order = case["order"]
        group = list(range(offset, offset + order))
        graph = template(order, case["kind"], escape)
        pivot = offset + case["pivot"]
        assert pivot_literal == edge_literal(sender, pivot, escape)
        assert pins[0, sender] == marked
        assert all(pins[0, v] == escape for v in group)
        for u, v in itertools.combinations(group, 2):
            assert pins[u, v] == graph[u - offset][v - offset]
        palette = set(range(4)) - {marked}
        for v in group:
            key = tuple(sorted((sender, v)))
            actual = {color for color in range(4) if (*key, color) not in denied}
            if v - offset in case["support"]:
                assert actual == {marked}
                support_sites += 1
            else:
                assert actual == palette
                free_sites += 1
            domains += 1
        checked += 1
    receipt = {"status": "PASS", "pivot_rows_checked": checked,
               "arm_sites_checked": domains, "support_sites_exact_singleton": support_sites,
               "free_sites_exact_three_color_domain": free_sites,
               "physical_units_independently_reconstructed": True,
               "template_edges_and_sender_domains": "all matched on every non-null binding",
               "wall_clock_seconds": round(time.monotonic() - started, 6)}
    (Path(__file__).resolve().parents[1] / "checks/geometry-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
