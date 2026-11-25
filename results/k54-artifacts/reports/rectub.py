"""Certified upper bounds U_r on the number of tokens a single rectangle can hold.

For rectangle r, n_r = sum_{k in L_r} x_k = sum_{k in R_r} x_k.  Dropping every
column outside L_r leaves a relaxation of the count model, so the maximum of
sum_{k in L_r} x_k over that relaxation is an upper bound on n_r.  The maximum is
an LP optimum, certified by its dual (printed for the record).  U_r is the min of
the left and right maxima, floored, and of |L_r|, |R_r|.
"""
import json
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import CountModel  # noqa: E402


def bounds(board, verbose=True):
    M = CountModel(board)
    out = []
    for r in range(len(M.rects)):
        vals = []
        for side, ks0 in ((0, M.L[r]), (1, M.R[r])):
            ks = ks0
            keep = {int(k): i for i, k in enumerate(ks)}
            rows, cs, vv = [], [], []
            rr = 0
            for j in set(j for k in ks for j in M.terms[k]):
                mem = [keep[k] for k in ks if j in M.terms[k]]
                for i in mem:
                    rows.append(rr); cs.append(i); vv.append(1.0)
                rr += 1
            A = sp.coo_matrix((vv, (rows, cs)), shape=(rr, len(ks))).tocsr()
            caps = np.array([M.caps[j] for j in sorted(set(j for k in ks for j in M.terms[k]))],
                            dtype=float)
            ub = np.minimum(M.ub[ks].astype(float), 26.0)
            res = linprog(-np.ones(len(ks)), A_ub=A, b_ub=caps,
                          bounds=list(zip(np.zeros(len(ks)), ub)), method="highs")
            vals.append(-res.fun if res.status == 0 else 0.0)
        U = int(min(np.floor(vals[0] + 1e-9), np.floor(vals[1] + 1e-9), 26))
        out.append((int(U), float(vals[0]), float(vals[1]), len(M.L[r]), len(M.R[r])))
    if verbose:
        import collections
        print(board, "U_r histogram:", sorted(collections.Counter(u[0] for u in out).items()))
        print("  total U_r:", sum(u[0] for u in out), " max", max(u[0] for u in out))
    return out


if __name__ == "__main__":
    b = bounds(sys.argv[1] if len(sys.argv) > 1 else "fresh-07")
    Path(HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / ("rectub-" + (sys.argv[1] if len(sys.argv) > 1 else "fresh-07") + ".json")
     ).write_text(json.dumps(b) + "\n")
