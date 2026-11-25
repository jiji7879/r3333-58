"""Construct (or refute) an integral solution of the strengthened count model.

The count model of pilot/make_pilot_cnf.py, in integers:
  x_k >= 0 integer for every column k = (rectangle, side, signature)
  (C1) per rectangle: sum_{k side 0 in r} x_k = sum_{k side 1 in r} x_k
  (C2) sum_{k side 0} x_k = 26                            (population)
  (C3) per class: sum_{k in class} x_k <= cap
  (C4) per price class: sum_{k in price class} x_k >= lower
A solution is built unit by unit (an outsider on the left and one on the right of
the same rectangle), so (C1) and (C2) hold by construction; (C3) is maintained as
residual capacity; (C4) is repaired by local swaps and checked exactly at the end.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "work" / "k54" / "pilot"))
from implied_spokes import DATA, LIMIT, load  # noqa: E402
from price_cover import instance  # noqa: E402


class Model:
    def __init__(self, board):
        cols, classes, caps, terms = instance(board)
        self.board = board
        self.cols = cols
        self.classes = classes
        self.caps = caps
        self.terms = terms
        prices = load(DATA / "prices" / (board + ".json"))
        matrix = load(DATA / "h42.json")
        n = len(cols)
        self.ub = [26] * n
        for k, row in enumerate(terms):
            for j in row:
                self.ub[k] = min(self.ub[k], caps[j])
        self.by_rect = defaultdict(lambda: ([], []))
        for k, (rect, side, _, _) in enumerate(cols):
            self.by_rect[rect][side].append(k)
        self.by_class = defaultdict(list)
        for k, row in enumerate(terms):
            for j in row:
                self.by_class[j].append(k)
        slack = prices["cost"] - 26 * prices["scale"]
        self.lower = []
        for side, side_prices in enumerate(prices["side"]):
            for j, (code, w) in enumerate(side_prices):
                anchors = [(h, p) for h, p in enumerate(code) if p != 14]
                inside = sum(all(matrix[i][p] == h for h, p in anchors) for i in range(14))
                low = LIMIT[len(anchors)] - inside - slack // w
                if low > 0:
                    forms = [k for k, (_, s, sig, _) in enumerate(cols)
                             if s == side and sig >> j & 1 and self.ub[k] > 0]
                    self.lower.append((low, forms))

    def affordable(self, k, res):
        return all(res[j] >= 1 for j in self.terms[k]) and self.ub[k] >= 1

    def build(self, rng, tries=20000):
        rects = sorted(self.by_rect)
        for attempt in range(6):
            res = list(self.caps)
            x = [0] * len(self.cols)
            ok = True
            for u in range(26):
                order = rects[:] if attempt == 0 else rng.sample(rects, len(rects))
                placed = False
                for r in order:
                    left, right = self.by_rect[r]
                    cl = [k for k in (left if attempt < 3 else rng.sample(left, min(len(left), 200)))
                          if x[k] < self.ub[k] and all(res[j] >= 1 for j in self.terms[k])]
                    if not cl:
                        continue
                    cr = [k for k in (right if attempt < 3 else rng.sample(right, min(len(right), 200)))
                          if x[k] < self.ub[k] and all(res[j] >= 1 for j in self.terms[k])]
                    if not cr:
                        continue
                    k = cl[0] if attempt % 2 == 0 else rng.choice(cl)
                    l = cr[0] if attempt % 2 == 0 else rng.choice(cr)
                    x[k] += 1
                    x[l] += 1
                    for j in self.terms[k]:
                        res[j] -= 1
                    for j in self.terms[l]:
                        res[j] -= 1
                    placed = True
                    break
                if not placed:
                    ok = False
                    break
            if not ok:
                continue
            x = self.repair(x, res, rng)
            if self.verify(x):
                return x
        return None

    def repair(self, x, res, rng):
        """Add units inside a rectangle (one left, one right) until (C4) holds."""
        for _ in range(400):
            bad = [(low, forms) for low, forms in self.lower
                   if sum(x[k] for k in forms) < low]
            if not bad:
                return x
            low, forms = rng.choice(bad)
            cands = [k for k in forms if x[k] < self.ub[k] and all(res[j] >= 1 for j in self.terms[k])]
            if not cands:
                continue
            k = rng.choice(cands)
            _, side, _, _ = self.cols[k]
            r = self.cols[k][0]
            right = self.by_rect[r][1 - side]
            partners = [l for l in right if x[l] < self.ub[l] and all(res[j] >= 1 for j in self.terms[l])]
            if not partners:
                continue
            l = rng.choice(partners)
            x[k] += 1
            x[l] += 1
            for j in self.terms[k]:
                res[j] -= 1
            for j in self.terms[l]:
                res[j] -= 1
        return x

    def verify(self, x, detail=False):
        n = len(self.cols)
        if len(x) != n or any(v < 0 or v > self.ub[k] for k, v in enumerate(x)):
            return False
        load_ = defaultdict(int)
        for k, v in enumerate(x):
            for j in self.terms[k]:
                load_[j] += v
        if any(v > cap for j, v in load_.items() for cap in [self.caps[j]]):
            return False
        tot = [0, 0]
        for k, (rect, side, _, _) in enumerate(self.cols):
            tot[side] += x[k]
        if tot != [26, 26]:
            return False
        for r, (left, right) in self.by_rect.items():
            if sum(x[k] for k in left) != sum(x[k] for k in right):
                return False
        for low, forms in self.lower:
            if sum(x[k] for k in forms) < low:
                return False
        if detail:
            print("  population", tot, "support", sum(1 for v in x if v), "max", max(x))
        return True


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("board")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    m = Model(a.board)
    rng = random.Random(a.seed)
    x = m.build(rng)
    print(a.board, "cols", len(m.cols), "classes", len(m.classes),
          "prices", len(m.lower), "->", "FEASIBLE" if x else "not found")
    if x is not None:
        m.verify(x, detail=True)
        if a.out:
            a.out.write_text(json.dumps(dict(board=a.board, counts=x,
                                             cols=[[r, s, sig] for r, s, sig, _ in m.cols])) + "\n")
