"""Depth-first branch and bound on the rectangle row sums n_r.

The count model's integer variables x_k only enter through narrow classes; the
archive closed live-17 by branching on *integral row sums* n_r (the number of
outsiders a rectangle carries).  Here the same branching is done explicitly:

  node = partial fixing of some n_r;
  LP   = the count model with x >= 0 continuous and the fixed n_r;
  prune if the LP is infeasible  (this is the certificate direction: it proves the
          count model has no integer solution, hence the board is excluded);
  branch on a fractional n_r otherwise.

Since sum_r n_r = 26, at most 26 rectangles can be non-zero, so the tree is small.
A completed integral node gives a relaxation-feasible point (row sums only).
"""
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ilp import model as build_model  # noqa: E402
from witness import Model  # noqa: E402


class BB:
    def __init__(self, board):
        self.A, self.lo, self.hi, self.ub, self.info = build_model(board)
        self.M = Model(board)
        n = self.A.shape[1]
        self.n = n
        self.rects = sorted(self.M.by_rect)
        self.rid = {r: i for i, r in enumerate(self.rects)}
        rows, cols, vals = [], [], []
        m = len(self.rects)
        for r, (L, R) in self.M.by_rect.items():
            for k in L:
                rows.append(2 * self.rid[r]); cols.append(k); vals.append(1.0)
            rows.append(2 * self.rid[r]); cols.append(n + self.rid[r]); vals.append(-1.0)
            for k in R:
                rows.append(2 * self.rid[r] + 1); cols.append(k); vals.append(1.0)
            rows.append(2 * self.rid[r] + 1); cols.append(n + self.rid[r]); vals.append(-1.0)
        E = sp.coo_matrix((vals, (rows, cols)), shape=(2 * m, n + m)).tocsr()
        self.A2 = sp.vstack([sp.hstack([self.A, sp.csr_matrix((self.A.shape[0], m))]), E]).tocsr()
        self.base_lo = np.concatenate([self.lo, np.zeros(2 * m)])
        self.base_hi = np.concatenate([self.hi, np.zeros(2 * m)])
        self.bounds = list(zip(np.zeros(n + m), np.concatenate([self.ub, np.full(m, 26.0)])))
        eq = np.isfinite(self.base_lo) & np.isfinite(self.base_hi) & (self.base_lo == self.base_hi)
        up = np.isfinite(self.base_hi) & ~eq
        dn = np.isfinite(self.base_lo) & ~np.isfinite(self.base_hi) & ~eq
        self.Aeq, self.beq = self.A2[eq], self.base_lo[eq]
        self.Aub = sp.vstack([self.A2[up], -self.A2[dn]]).tocsr()
        self.bub = np.concatenate([self.base_hi[up], -self.base_lo[dn]])
        self.nodes = 0
        self.leaves = 0

    def lp(self, fixed):
        bounds = list(self.bounds)
        for i, (lo, hi) in fixed.items():
            j = self.n + i
            a, b = bounds[j]
            bounds[j] = (max(a, lo), min(b, hi))
            if bounds[j][0] > bounds[j][1]:
                return None, None
        res = linprog(np.zeros(self.A2.shape[1]), A_ub=self.Aub, b_ub=self.bub,
                      A_eq=self.Aeq, b_eq=self.beq, bounds=bounds, method="highs")
        if res.status != 0:
            return None, None
        return res.status, res.x

    def solve(self, deadline):
        stack = [dict()]
        best = None
        while stack:
            if time.time() > deadline:
                return "OPEN", None, None
            fixed = stack.pop()
            self.nodes += 1
            st, x = self.lp(fixed)
            if st is None:
                self.leaves += 1
                continue
            n = self.n
            fr = [i for i in range(len(self.rects)) if abs(x[n + i] - round(x[n + i])) > 1e-6]
            if not fr:
                return "FEASIBLE", x, fixed
            i = max(fr, key=lambda i: min(x[n + i] - np.floor(x[n + i]), np.ceil(x[n + i]) - x[n + i]))
            v = x[n + i]
            stack.append({**fixed, i: (int(np.floor(v)), int(np.floor(v)))})
            stack.append({**fixed, i: (int(np.ceil(v)), 26)})
            if len(stack) > 4000:
                return "OPEN", None, None
        return "INFEASIBLE", None, None


if __name__ == "__main__":
    import argparse
    import json
    p = argparse.ArgumentParser()
    p.add_argument("board")
    p.add_argument("--seconds", type=float, default=150)
    a = p.parse_args()
    bb = BB(a.board)
    st, x, fixed = bb.solve(time.time() + a.seconds)
    print(a.board, bb.info, "rects", len(bb.rects), "nodes", bb.nodes,
          "infeasible leaves", bb.leaves, "->", st)
    if st == "FEASIBLE":
        n = bb.n
        nr = [int(round(x[n + i])) for i in range(len(bb.rects))]
        frac = int((np.abs(x[:n] - np.rint(x[:n])) > 1e-6).sum())
        xi = np.rint(x[:n]).astype(np.int64)
        ok = bb.M.verify(xi)
        print("   row sums sum", sum(nr), "nonzero", sum(1 for v in nr if v),
              "fractional count vars", frac, "of", int((x[:n] > 1e-7).sum()),
              "counts verified:", ok)
        (HERE / "out" / ("bb-" + a.board + ".json")).write_text(json.dumps(dict(
            board=a.board, rowsums=nr, verified=bool(ok),
            rects=[[list(r), v] for r, v in zip(bb.rects, nr)],
            counts=xi.tolist())) + "\n")
