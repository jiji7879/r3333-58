"""Check the two graph witnesses and the ten-row match using the standard library."""
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_matrix(path):
    lines = path.read_text().splitlines()
    n, colors = map(int, lines[0].split())
    matrix = [list(map(int, line.split())) for line in lines[1:]]
    assert len(matrix) == n and all(len(row) == n for row in matrix)
    for i, j in combinations(range(n), 2):
        assert matrix[i][j] == matrix[j][i] and 0 <= matrix[i][j] < colors
    return matrix


def matches_pattern(observed, mask, words):
    """Each specified letter must already be assigned. Use None for unknown cells."""
    candidates = [
        [j for j, row in enumerate(observed) if all(row[a] == words[i][a] for a in columns)]
        for i, columns in mask
    ]
    matched = {}

    def augment(i, seen):
        for j in candidates[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in matched or augment(matched[j], seen):
                matched[j] = i
                return True
        return False

    return all(augment(i, set()) for i in range(len(candidates)))


def verify():
    words = {}
    for line in (ROOT / 'source.wit').read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'word':
            words[int(fields[1])] = list(map(int, fields[2:]))
    pattern = json.loads((ROOT / 'pattern7.json').read_text())
    mask = pattern['rows']
    assert pattern['anchor'] == 7
    assert len({i for i, _ in mask}) == len(mask) == 10
    assert sum(len(set(columns)) for _, columns in mask) == 116
    original = [words[i] for i in range(14)]
    assert matches_pattern(original, mask, words)
    profile = [sum(row[a] == 0 for row in original) for a in range(15)]
    assert [a for a, count in enumerate(profile) if count == 4] == [0, 1, 3, 8, 10]
    assert set(profile) == {4, 5}

    template = read_matrix(ROOT / 'template_m4.col')
    mapping = [3, 11, 1, 9, 2, 8, 0, 10, 14, 4, 12, 6, 13, 5, 7]
    assert sorted(mapping) == list(range(15))
    for filename, n in [('five.col', 35), ('same_zeros_six.col', 36)]:
        matrix = read_matrix(ROOT / filename)
        assert len(matrix) == n
        triangles = 0
        for i, j, k in combinations(range(n), 3):
            assert not matrix[i][j] == matrix[i][k] == matrix[j][k]
            triangles += 1
        for a, b in combinations(range(15), 2):
            assert matrix[1 + a][1 + b] == 1 + template[mapping[a]][mapping[b]]
        assert matrix[0][1:] == [0] * 15 + [1] * 14 + [2] * (n - 30)
        rows = [matrix[i][1:16] for i in range(16, n)]
        assert all(row.count(0) == 5 for row in rows)
        for i, row in enumerate(rows[:14]):
            assert all((row[a] == 0) == (words[i][a] == 0) for a in range(15))
        differences = sum(row[a] != words[i][a] for i, row in enumerate(rows[:14]) for a in range(15))
        assert differences == (0 if n == 35 else 51)
        print(filename, n, 'vertices,', triangles, 'triangles checked,', differences, 'letters changed')
    print('Verified the original arm matches all 116 specified cells on ten distinct rows.')


if __name__ == '__main__':
    verify()
