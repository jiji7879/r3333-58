"""Integer feasibility of the strengthened count model (pilot class system).

Replicates the integer core of pilot/make_pilot_cnf.py (the CNF whose sha256 we
reproduce bit for bit for local-15) as a pure integer linear feasibility problem,
so that many boards can be tested cheaply with HiGHS instead of a 5-10M-clause SAT
instance.

Variables: x_k >= 0 integer, k a "column" = (rectangle, side, signature) marginal type.
Constraints (identical to make_pilot_cnf.build):
  (C0) 0 <= x_k <= min(26, caps of the classes of k)          [bounds]
  (C1) per rectangle: sum_{k in r, side 0} x_k = sum_{k in r, side 1} x_k
  (C2) sum_{k side 0} x_k = 26
  (C3) per distinct class: sum_{k in class} x_k <= cap
  (C4) per price class (side, code, w):
       sum_{k: side, sig covers code} x_k >= LIMIT[#anchors] - inside - slack//w  (if > 0)
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "work" / "k54" / "pilot"))
from implied_spokes import DATA, LIMIT, load  # noqa: E402
from price_cover import instance  # noqa: E402


def model(board):
    cols, classes, caps, terms = instance(board)
    prices = load(DATA / "prices" / (board + ".json"))
    matrix = load(DATA / "h42.json")
    n = len(cols)
    rows, cols_, vals, lo, hi = [], [], [], [], []
    r = 0

    def add(entries, l, h):
        nonlocal r
        for k, v in entries:
            rows.append(r)
            cols_.append(k)
            vals.append(v)
        lo.append(l)
        hi.append(h)
        r += 1

    ub = [26] * n
    for k, row in enumerate(terms):
        for j in row:
            ub[k] = min(ub[k], caps[j])
    by_rect = defaultdict(lambda: defaultdict(list))
    for k, (rect, side, _, _) in enumerate(cols):
        by_rect[rect][side].append(k)
    for rect, d in by_rect.items():
        add([(k, 1) for k in d[0]] + [(k, -1) for k in d[1]], 0, 0)
    add([(k, 1) for k, (_, s, _, _) in enumerate(cols) if s == 0], 26, 26)
    distinct = {}
    by_class = defaultdict(list)
    for k, row in enumerate(terms):
        if ub[k]:
            for j in row:
                by_class[j].append(k)
    for j, ind in by_class.items():
        distinct[tuple(ind)] = min(caps[j], distinct.get(tuple(ind), caps[j]))
    for ind, cap in distinct.items():
        add([(k, 1) for k in ind], -np.inf, cap)
    slack = prices["cost"] - 26 * prices["scale"]
    nlow = 0
    for side, side_prices in enumerate(prices["side"]):
        for j, (code, w) in enumerate(side_prices):
            anchors = [(h, p) for h, p in enumerate(code) if p != 14]
            inside = sum(all(matrix[i][p] == h for h, p in anchors) for i in range(14))
            lower = LIMIT[len(anchors)] - inside - slack // w
            if lower > 0:
                nlow += 1
                forms = [k for k, (_, s, sig, _) in enumerate(cols) if s == side and sig >> j & 1]
                add([(k, 1) for k in forms], lower, np.inf)
    A = coo_matrix((vals, (rows, cols_)), shape=(r, n)).tocsr()
    info = dict(ncols=n, nclasses=len(classes), nrows=r, nlower=nlow,
                ncaps=len(distinct))
    return A, np.array(lo), np.array(hi), np.array(ub, dtype=float), info


def solve(board, timelimit=120, verbose=False):
    A, lo, hi, ub, info = model(board)
    cons = LinearConstraint(A, lo, hi)
    res = milp(c=np.zeros(A.shape[1]), constraints=cons,
               integrality=np.ones(A.shape[1]), bounds=Bounds(np.zeros(A.shape[1]), ub),
               options=dict(time_limit=timelimit, presolve=True, disp=verbose))
    x = None
    if res.x is not None:
        xi = np.rint(res.x).astype(np.int64)
        if np.all(np.abs(res.x - xi) < 1e-6) and np.all(xi >= 0) and np.all(xi <= ub):
            if np.all(A @ xi >= lo - 1e-9) and np.all(A @ xi <= hi + 1e-9):
                x = xi
    return res, x, info


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("board")
    p.add_argument("--timelimit", type=float, default=120)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    res, x, info = solve(a.board, a.timelimit)
    print(a.board, info, "status=", res.status, res.message.split("\n")[0][:70])
    if x is not None:
        print("  feasible: total", int(x.sum()), "support", int((x > 0).sum()),
              "max", int(x.max()))
        if a.out:
            a.out.write_text(json.dumps(dict(board=a.board, counts=x.tolist())) + "\n")
    elif res.status == 2:
        print("  INFEASIBLE (HiGHS)")
