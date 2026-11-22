"""Regenerate the three certified formulas from the template and the partial words."""
import json
from itertools import combinations
from pathlib import Path

from pysat.card import CardEnc
from pysat.formula import CNF, IDPool

ROOT = Path(__file__).resolve().parent
A = range(15)
COLORS = range(4)
LEAN_TO_FILE = [3, 11, 1, 9, 2, 8, 0, 10, 14, 4, 12, 6, 13, 5, 7]


def data():
    lines = (ROOT / 'template_m4.col').read_text().splitlines()[1:]
    matrix = [list(map(int, line.split())) for line in lines]
    template = [[1 + matrix[i][j] for j in LEAN_TO_FILE] for i in LEAN_TO_FILE]
    words = {}
    for line in (ROOT / 'source.wit').read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'word':
            words[int(fields[1])] = tuple(map(int, fields[2:]))
    return template, words


def exactly_one(cnf, literals):
    cnf.append(literals)
    for left, right in combinations(literals, 2):
        cnf.append([-left, -right])


def build(pattern=None, arm_color=2):
    template, words = data()
    cnf, pool = CNF(), IDPool()
    if pattern is None:
        rows = [(i, list(A)) for i in range(14)]
        extra = 6
    else:
        rows = pattern['rows']
        extra = 5
    b = len(rows)
    n = b + extra
    active = {}
    if pattern is not None:
        for i, (_, positions) in enumerate(rows):
            for a in positions:
                active[i, a] = pool.id()
        for literal in active.values():
            cnf.append([literal])

    # Unspecified letters in the partial B rows create no restrictions.
    cell = {(x, a, f): pool.id() for x in range(b, n) for a in A for f in COLORS}
    for x in range(b, n):
        for a in A:
            exactly_one(cnf, [cell[x, a, f] for f in COLORS])
        zeros = [cell[x, a, 0] for a in A]
        cnf.extend(CardEnc.equals(zeros, bound=5, vpool=pool).clauses)
        if pattern is not None:
            cnf.append([cell[x, pattern['anchor'], 0]])
        for a, d in combinations(A, 2):
            f = template[a][d]
            cnf.append([-cell[x, a, f], -cell[x, d, f]])

    q = {}
    pentagon_colors = [f for f in (1, 2, 3) if f != arm_color]
    for x, y in combinations(range(n), 2):
        if y < b:
            allowed = [0, 2, 3]
            if pattern is None:
                allowed = [f for f in allowed if not any(words[x][a] == words[y][a] == f for a in A)]
        elif x < b:
            allowed = list(COLORS)
        elif pattern is None:
            allowed = [f for f in COLORS if f != arm_color]
        else:
            cycle_edge = y - x in (1, 4)
            allowed = [pentagon_colors[0 if cycle_edge else 1]]

        literals = []
        for f in allowed:
            edge = q[x, y, f] = pool.id()
            literals.append(edge)
            if pattern is None and y < b:
                continue  # The available colors already account for both full words.
            for a in A:
                triangle = [-edge]
                for v in (x, y):
                    if v >= b:
                        triangle.append(-cell[v, a, f])
                    elif words[rows[v][0]][a] != f:
                        break
                    elif pattern is not None:
                        if (v, a) not in active:
                            break
                        triangle.append(-active[v, a])
                else:
                    cnf.append(triangle)
        exactly_one(cnf, literals)

    for x, y, z in combinations(range(n), 3):
        for f in COLORS:
            triangle = ((x, y, f), (x, z, f), (y, z, f))
            if all(key in q for key in triangle):
                cnf.append([-q[key] for key in triangle])
    return cnf


if __name__ == '__main__':
    from tempfile import TemporaryDirectory

    pattern = json.loads((ROOT / 'pattern7.json').read_text())
    with TemporaryDirectory() as tmp:
        for name, mask, arm in [('local6', None, 2), ('pattern-2', pattern, 2), ('pattern-3', pattern, 3)]:
            path = Path(tmp) / (name + '.cnf')
            build(mask, arm).to_file(str(path))
            assert path.read_bytes() == (ROOT / 'certificates' / path.name).read_bytes()
            print(path.name, 'reproduced byte for byte')
