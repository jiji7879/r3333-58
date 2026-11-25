"""Rectangle-row-sum relaxation of the count model: cheap sound infeasibility test.

The count model asks for INTEGER counts x_k.  Its feasible set is contained in the
relaxation where x is continuous but the per-rectangle row sums n_r are integral
(this is the branching the archive used to close live-17: "the arithmetic exclusion
branches on integral counts or integral row sums").  If this relaxation is
infeasible, the count model is infeasible, hence the board is excluded by counting
alone.  If it is feasible we learn the permissible row sums, which is useful input
for a finer search.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ilp import model  # noqa: E402
from witness import Model  # noqa: E402


def relaxed(board):
    A, lo, hi, ub, info = model(board)
    M = Model(board)
    n = A.shape[1]
    rects = sorted(M.by_rect)
    rid = {r: i for i, r in enumerate(rects)}
    rows, cols_, vals = [], [], []
    for r, (L, R) in M.by_rect.items():
        for k in L:                      # sum_{k in L} x_k - n_r = 0
            rows.append(2 * rid[r]); cols_.append(k); vals.append(1.0)
        rows.append(2 * rid[r]); cols_.append(n + rid[r]); vals.append(-1.0)
        for k in R:                      # sum_{k in R} x_k - n_r = 0
            rows.append(2 * rid[r] + 1); cols_.append(k); vals.append(1.0)
        rows.append(2 * rid[r] + 1); cols_.append(n + rid[r]); vals.append(-1.0)
    E = sp.coo_matrix((vals, (rows, cols_)), shape=(2 * len(rects), n + len(rects))).tocsr()
    A2 = sp.vstack([sp.hstack([A, sp.csr_matrix((A.shape[0], len(rects)))]), E]).tocsr()
    lo2 = np.concatenate([lo, np.zeros(2 * len(rects))])
    hi2 = np.concatenate([hi, np.zeros(2 * len(rects))])
    lb = np.concatenate([np.zeros(n), np.zeros(len(rects))])
    ub2 = np.concatenate([ub, np.full(len(rects), 26.0)])
    integ = np.concatenate([np.zeros(n), np.ones(len(rects))])
    return A2, lo2, hi2, lb, ub2, integ, M, rects, info


def with_indicators(board):
    """Plus: n_r <= 26 z_r, sum z_r <= 26, sum_r n_r = 26 (all valid)."""
    A2, lo2, hi2, lb, ub2, integ, M, rects, info = relaxed(board)
    n = A2.shape[1] - len(rects)
    m = len(rects)
    rows, cols, vals = [], [], []
    for r in range(m):
        rows += [r, r]; cols += [n + r, n + m + r]; vals += [1.0, -26.0]
    rows += [m] * m; cols += [n + m + r for r in range(m)]; vals += [1.0] * m
    rows += [m + 1] * m; cols += [n + r for r in range(m)]; vals += [1.0] * m
    E = sp.coo_matrix((vals, (rows, cols)), shape=(m + 2, n + 2 * m)).tocsr()
    A3 = sp.vstack([sp.hstack([A2, sp.csr_matrix((A2.shape[0], m))]), E]).tocsr()
    lo3 = np.concatenate([lo2, np.full(m, -np.inf), [0.0], [26.0]])
    hi3 = np.concatenate([hi2, np.zeros(m), [26.0], [26.0]])
    lb3 = np.concatenate([lb, np.zeros(m)])
    ub3 = np.concatenate([ub2, np.ones(m)])
    integ3 = np.concatenate([integ, np.ones(m)])
    return A3, lo3, hi3, lb3, ub3, integ3, M, rects, info


def run(board, timelimit=120, indicators=False):
    A2, lo2, hi2, lb, ub2, integ, M, rects, info = (with_indicators(board) if indicators
                                                   else relaxed(board))
    res = milp(c=np.zeros(A2.shape[1]), constraints=LinearConstraint(A2, lo2, hi2),
               integrality=integ, bounds=Bounds(lb, ub2),
               options=dict(time_limit=timelimit))
    print(board, info, "rects", len(rects), "status", res.status,
          res.message.split("\n")[0][:60])
    if res.status == 0 and res.x is not None:
        x = res.x[:len(M.cols)]
        nr = np.rint(res.x[len(M.cols):len(M.cols) + len(rects)]).astype(int)
        frac = int((np.abs(x - np.rint(x)) > 1e-7).sum())
        print("   row sums", dict(zip(rects, nr.tolist())).__str__()[:160])
        print("   fractional count vars:", frac, "of support", int((x > 1e-7).sum()))
        return "FEASIBLE", x, nr
    if res.status == 2:
        return "INFEASIBLE", None, None
    return "OPEN", None, None


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("board")
    p.add_argument("--timelimit", type=float, default=120)
    p.add_argument("--indicators", action="store_true")
    a = p.parse_args()
    out = run(a.board, a.timelimit, a.indicators)
    (HERE / "out" / ("rowsum-" + a.board + ".json")).write_text(json.dumps(dict(
        board=a.board, verdict=out[0],
        rowsums=None if out[2] is None else [int(v) for v in out[2]])) + "\n")
