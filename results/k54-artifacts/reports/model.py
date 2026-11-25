"""The integer count model of a K54 board, in the form used by all my solvers.

Reproduces pilot/price_cover.instance + the integer core of pilot/make_pilot_cnf.py:

  x_k >= 0 integer, k a column = (maximal rectangle, side, spoke signature)
  (C1) per rectangle r:  sum_{k side 0 in r} x_k = sum_{k side 1 in r} x_k
  (C2) sum_{k side 0} x_k = 26
  (C3) per anchor class j:  sum_{k in j} x_k <= caps[j]
  (C4) per price row:  sum_{k covered} x_k >= lower
  (C0) x_k <= ub[k] (implied by C3 when k is in a class of small cap)

Every column of fresh-07 lies in some class, all class caps are >= 1, so no
column is killed outright.  Columns with no implied class have ub = 26.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "arc" / "pilot"))
from price_cover import instance  # noqa: E402
from implied_spokes import DATA, LIMIT, load  # noqa: E402


class CountModel:
    def __init__(self, board):
        self.board = board
        cols, classes, caps, terms = instance(board)
        self.cols = cols
        self.classes = classes
        self.caps = np.array(caps, dtype=np.int64)
        prices = load(DATA / "prices" / (board + ".json"))
        matrix = load(DATA / "h42.json")
        n, m = len(cols), len(classes)
        # ---- CSR of column -> classes
        lens = np.array([len(t) for t in terms], dtype=np.int64)
        self.off = np.zeros(n + 1, dtype=np.int64)
        np.cumsum(lens, out=self.off[1:])
        flat = np.fromiter((j for t in terms for j in t), dtype=np.int64,
                           count=int(self.off[-1]))
        self.nbr = flat
        self.terms = terms
        # ---- per column upper bound from C3
        ub = np.full(n, 26, dtype=np.int64)
        for k, t in enumerate(terms):
            if t:
                ub[k] = min(int(self.caps[j]) for j in t)
        self.ub = ub
        # ---- rectangles
        self.rects = sorted({c[0] for c in cols})
        self.rid = {r: i for i, r in enumerate(self.rects)}
        self.L = [[] for _ in self.rects]
        self.R = [[] for _ in self.rects]
        for k, (rect, side, sig, forced) in enumerate(cols):
            (self.L if side == 0 else self.R)[self.rid[rect]].append(k)
        self.L = [np.array(x, dtype=np.int64) for x in self.L]
        self.R = [np.array(x, dtype=np.int64) for x in self.R]
        self.side = np.array([c[1] for c in cols])
        self.sig = np.array([c[2] for c in cols], dtype=object)
        # ---- C4 price rows: (lower, boolean mask over columns)
        slack = prices["cost"] - 26 * prices["scale"]
        self.lower = []
        for side, side_prices in enumerate(prices["side"]):
            for j, (code, w) in enumerate(side_prices):
                anchors = [(h, p) for h, p in enumerate(code) if p != 14]
                inside = sum(all(matrix[i][p] == h for h, p in anchors)
                             for i in range(14))
                low = LIMIT[len(anchors)] - inside - slack // w
                if low > 0:
                    mask = np.array([(s == side and (sig >> j) & 1)
                                     for _, s, sig, _ in cols], dtype=bool)
                    self.lower.append((low, np.nonzero(mask)[0]))
        self.n, self.m = n, m

    # ------------------------------------------------------------------ check
    def verify(self, x, verbose=True):
        """Independent-ish check of C0..C4 from a plain integer vector."""
        x = np.asarray(x, dtype=np.int64)
        bad = []
        if x.shape != (self.n,) or (x < 0).any():
            bad.append("shape/negativity")
        if (x > self.ub).any():
            bad.append("C0 ub")
        loads = np.zeros(self.m, dtype=np.int64)
        for k in np.nonzero(x)[0]:
            a, b = self.off[k], self.off[k + 1]
            loads[self.nbr[a:b]] += x[k]
        if (loads > self.caps).any():
            bad.append("C3 class cap (%d classes)" % int((loads > self.caps).sum()))
        tot = int(x[self.side == 0].sum())
        if tot != 26:
            bad.append("C2 population left = %d" % tot)
        bal = 0
        for r in range(len(self.rects)):
            if int(x[self.L[r]].sum()) != int(x[self.R[r]].sum()):
                bal += 1
        if bal:
            bad.append("C1 balance (%d rects)" % bal)
        for low, forms in self.lower:
            if int(x[forms].sum()) < low:
                bad.append("C4 price")
        if verbose:
            print("verify", self.board, "OK" if not bad else "FAIL " + "; ".join(bad))
        return not bad


if __name__ == "__main__":
    m = CountModel(sys.argv[1] if len(sys.argv) > 1 else "fresh-07")
    print(m.board, "columns", m.n, "classes", m.m, "rects", len(m.rects),
          "price rows", len(m.lower), "nnz", int(m.off[-1]))
    print("ub histogram", np.bincount(m.ub).nonzero()[0].tolist(),
          np.bincount(m.ub)[np.bincount(m.ub).nonzero()[0]].tolist())
    for low, forms in m.lower:
        print("C4 lower", low, "over", len(forms), "columns")
