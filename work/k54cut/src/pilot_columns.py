"""Check implied-spoke capacity inequalities on an archived K54 count assignment."""
import argparse
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "checkpoints" / "counted" / "results"
ALL = (1 << 14) - 1
LIMIT = {1: 16, 2: 5, 3: 2, 4: 1}


def load(path):
    return json.loads(path.read_text())


def maximal_rectangles(rows):
    rights = {ALL}
    for row in rows:
        rights.update(row & s for s in list(rights))
    rectangles = []
    for right in sorted(rights - {0}):
        left = sum(1 << i for i, row in enumerate(rows) if row & right == right)
        if left:
            rectangles.append((left, right))
    return rectangles


def projected_words(matrix, prices, omitted):
    """For each signature intersect the colored spoke masks of every word that gives it."""
    active = [i for i in range(14) if not omitted >> i & 1]
    neighbors = [[sum(1 << j for j, h in enumerate(matrix[i]) if h == c)
                  for c in range(3)] for i in range(14)]
    initial = (1 << len(prices)) - 1
    allowed = [[initial] * 3 for _ in range(14)]
    for index, (code, _) in enumerate(prices):
        for color, anchor in enumerate(code):
            if anchor == 14:
                continue
            if omitted >> anchor & 1:
                initial &= ~(1 << index)
            for choice in range(3):
                if choice != color:
                    allowed[anchor][choice] &= ~(1 << index)
    forced = {}
    spoke = [0, 0, 0]

    def visit(depth, signature):
        if depth == len(active):
            if signature not in forced:
                forced[signature] = spoke.copy()
            else:
                for color in range(3):
                    forced[signature][color] &= spoke[color]
            return
        anchor = active[depth]
        bit = 1 << anchor
        for color in range(3):
            if neighbors[anchor][color] & spoke[color]:
                continue
            spoke[color] |= bit
            visit(depth + 1, signature & allowed[anchor][color])
            spoke[color] ^= bit
    visit(0, initial)
    return forced


def columns_for(board):
    matrix = load(DATA / "h42.json")
    pins = load(DATA / "boards.json")[board]
    prices = load(DATA / "prices" / (board + ".json"))
    if any(prices["mux"]):
        raise ValueError("This indexing routine requires zero pole-pair prices.")

    @lru_cache(None)
    def table(side, omitted):
        masks = projected_words(matrix, prices["side"][side], omitted)
        weights = [w for _, w in prices["side"][side]]
        costs = {sig: sum(w for i, w in enumerate(weights) if sig >> i & 1) for sig in masks}
        return masks, costs, min(costs.values())

    assert not projected_words(matrix, [], 0), "H42 nonextendibility implies nonempty c-support"
    total = 0
    for side_prices in prices["side"]:
        for code, weight in side_prices:
            anchors = [(h, p) for h, p in enumerate(code) if p != 14]
            assert 1 <= len(anchors) <= 3 and len({p for _, p in anchors}) == len(anchors)
            assert type(weight) == int and weight > 0
            inside = sum(all(matrix[i][p] == h for h, p in anchors) for i in range(14))
            total += weight * (LIMIT[len(anchors)] - inside)
    assert total == prices["cost"]
    cutoff = total - 25 * prices["scale"]
    columns = []
    for rect in maximal_rectangles(pins["rows"]):
        sides = [table(side, rect[side]) for side in (0, 1)]
        assert sides[0][2] + sides[1][2] >= prices["scale"]
        if sides[0][2] + sides[1][2] > cutoff:
            continue
        for side, (masks, costs, _) in enumerate(sides):
            for sig in sorted(masks):
                if costs[sig] + sides[1 - side][2] <= cutoff:
                    # All outside vertices assigned here must use c somewhere on this side.
                    forced_c = rect[side] if rect[side].bit_count() == 1 else 0
                    columns.append((rect, side, sig, [*masks[sig], forced_c]))
    return columns


