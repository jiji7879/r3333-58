#!/usr/bin/env python3
"""Degree-profile facts at n = 58, for the seven wall profiles.

At a vertex v of a triangle-free 4-colouring, d_c(v) = |N_c(v)| <= 16 (N_c(v)
is 3-coloured by the other three colours and R(3,3,3) = 17) and the four
degrees sum to n-1.  So the sorted profile is a partition of 57 into four
parts <= 16, equivalently of the deficit 64-57 = 7.

A colour is *critical* at v when d_c(v) >= 15.  The campaign's ticket argument
needs a root r with H(r) >= w(r), where w(r) is the sum of the critical
degrees: w(r) is the number of neighbours joined to r in a colour that is
critical **at r**.  The seven profiles with two or more non-critical colours
are the ones no SAT budget has closed.

Usage: python3 tools/profile_table.py
"""
import itertools

N = 58
CAP = 16            # R(3,3,3) - 1
WALL = {"15,15,14,13", "16,15,14,12", "16,15,13,13", "15,14,14,14",
        "16,16,14,11", "16,16,13,12", "16,14,14,13"}
CASES = {"15,15,15,12": (83440, 20166), "16,15,15,11": (16173, 0),
         "15,15,14,13": (7732, 7732), "16,15,14,12": (2058, 2058),
         "16,16,15,10": (1767, 0), "16,15,13,13": (1046, 1046),
         "15,14,14,14": (381, 381), "16,16,16,9": (214, 0),
         "16,16,14,11": (140, 140), "16,16,13,12": (140, 140),
         "16,14,14,13": (88, 88)}


def profiles():
    out = []
    for a in range(CAP + 1):
        for b in range(a, CAP + 1):
            for c in range(b, CAP + 1):
                d = N - 1 - a - b - c
                if c <= d <= CAP:
                    out.append((d, c, b, a))
    return out


def main():
    rows = profiles()
    assert len(rows) == 11, rows
    assert sum(CASES[",".join(map(str, p))][0] for p in rows) == 113179
    head = ("profile", "critical", "w(v)", "open", "total", "wall")
    print("%-14s %8s %5s %7s %7s %5s" % head)
    open_wall = 0
    for p in rows:
        key = ",".join(map(str, p))
        crit = sum(1 for x in p if x >= 15)
        w = sum(x for x in p if x >= 15)
        total, opened = CASES[key]
        wall = key in WALL
        if wall:
            open_wall += opened
        print("%-14s %8d %5d %7d %7d %5s" % (key, crit, w, opened, total,
                                             "yes" if wall else ""))
    print("\ncritical colours -> profiles")
    for k in (1, 2, 3):
        print("  %d: %s" % (k, "  ".join(
            ",".join(map(str, p)) for p in rows
            if sum(1 for x in p if x >= 15) == k)))
    assert open_wall == 11585, open_wall
    print("\nwall total open = %d;  open elsewhere = %d" %
          (open_wall, 31751 - open_wall))
    for k in (1, 2, 3):
        ws = [sum(x for x in p if x >= 15) for p in rows
              if sum(1 for x in p if x >= 15) == k]
        print("w(v) for %d critical colour%s: %d..%d" %
              (k, "" if k == 1 else "s", min(ws), max(ws)))
    print("\nAt n = 60 the same construction with deficit 5 has w >= 31, so "
          "w(u)+w(v) > 60\nfor every pair; at n = 58 the same step needs "
          "w(u)+w(v) > 58 and holds only\nfor the two-critical profiles "
          "(w = 30..32), not the one-critical ones (15, 16).")


if __name__ == "__main__":
    main()
