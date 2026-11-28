#!/usr/bin/env python3
"""Independent, generator-free audit of the configurable-MCF DIMACS layout."""
import argparse, hashlib, itertools, json
from pathlib import Path

PARENT_SHA = '90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae'
ROW = '06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06'
PROFILE = (16, 16, 14, 11)


def parse(path):
    raw = Path(path).read_bytes(); lines = raw.splitlines()
    fields = lines[0].split(); assert fields[:2] == [b'p', b'cnf']
    nv, nc = int(fields[2]), int(fields[3]); clauses = []
    for line in lines[1:]:
        if not line or line.startswith(b'c'): continue
        c = tuple(int(x) for x in line.split()[:-1]); assert line.split()[-1] == b'0' and c
        clauses.append(c)
    assert len(clauses) == nc
    return raw, nv, clauses


def lit(u, v, c):
    assert 0 <= u < 58 and 0 <= v < 58 and u != v and 0 <= c < 4
    if u > v: u, v = v, u
    edge = u * (2 * 58 - u - 1) // 2 + (v - u - 1)
    return 4 * edge + c + 1


def expected_suffix(rules, nv):
    top = nv; clauses = []; allocation = []
    for arm, u, v in rules:
        ys = []
        for w in range(58):
            if w in (u, v): continue
            top += 1; y = top; ys.append(y)
            left, right = lit(u, w, 0), lit(v, w, 0)
            clauses.extend([(-y, left), (-y, right), (y, -left, -right)])
            allocation.append((y, arm, u, v, w, left, right))
        clauses.append(tuple([lit(u, v, 0)] + ys))
    return clauses, top, allocation


def compare(actual, expected):
    assert len(actual) == len(expected), ('suffix clause count', len(actual), len(expected))
    for i, (a, e) in enumerate(zip(actual, expected)):
        assert a == e, ('first suffix mismatch', i, a, e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', default='inputs/parent.cnf'); ap.add_argument('--cnf', required=True)
    ap.add_argument('--metadata', required=True); ap.add_argument('--report', required=True)
    args = ap.parse_args()
    praw, pnv, parent = parse(args.parent); raw, nv, clauses = parse(args.cnf)
    meta = json.loads(Path(args.metadata).read_text())
    assert hashlib.sha256(praw).hexdigest() == PARENT_SHA == meta['ordinary_parent_sha256']
    assert hashlib.sha256(raw).hexdigest() == meta['augmented_sha256']
    assert meta['row'] == ROW and tuple(meta['profile']) == PROFILE and meta['colour'] == 0
    assert pnv == 19533 and len(parent) == 184335 and clauses[:len(parent)] == parent
    # Removing the augmented header leaves the exact original parent body as a prefix.
    pbody = praw.split(b'\n', 1)[1]; abody = raw.split(b'\n', 1)[1]
    assert abody[:len(pbody)] == pbody
    # host(K58), 4 colours: edge exactly-one + four triangle obstructions/triple.
    host_clauses = 1653 * (1 + 6) + 30856 * 4
    assert host_clauses == 134995
    host = []
    for u, v in itertools.combinations(range(58), 2):
        colours = [lit(u, v, c) for c in range(4)]
        host.append(tuple(colours))
        host.extend((-colours[a], -colours[b]) for a, b in itertools.combinations(range(4), 2))
    for u, v, w in itertools.combinations(range(58), 3):
        for c in range(4):
            host.append((-lit(u, v, c), -lit(u, w, c), -lit(v, w, c)))
    assert len(host) == host_clauses and parent[:host_clauses] == host
    nonhost = parent[host_clauses:]
    used_nonhost = {abs(x) for c in nonhost for x in c}
    physical = set(range(1, 4 * 1653 + 1))
    forbidden = used_nonhost & physical
    start = 1; groups = []
    for size in PROFILE:
        groups.append(tuple(range(start, start + size))); start += size
    assert start == 58
    expected_rules = []
    for arm in meta['arms']:
        assert arm != meta['colour']
        for u, v in itertools.combinations(groups[arm], 2):
            if not ({lit(u, v, c) for c in range(4)} & forbidden):
                expected_rules.append((arm, u, v))
    actual_rules = [(r['arm'], *r['edge']) for r in meta['rules']]
    assert actual_rules == expected_rules
    suffix, top, allocation = expected_suffix(expected_rules, pnv)
    assert nv == top == meta['augmented_variables']
    compare(clauses[len(parent):], suffix)
    assert len(suffix) == meta['added_clauses']
    assert len(allocation) == 56 * len(expected_rules)
    assert len({x[0] for x in allocation}) == len(allocation)
    assert all(x[0] > pnv for x in allocation)
    # Every parent unit/threshold/support clause avoids every changing physical variable.
    changing = {lit(u, v, c) for _, u, v in expected_rules for c in range(4)}
    assert not (changing & forbidden)
    # Executable negative controls against the exact byte/clause template.
    bad = list(suffix); bad[0] = (-bad[0][0], *bad[0][1:])
    try: compare(bad, suffix); raise RuntimeError('sign-mutation control was accepted')
    except AssertionError: pass
    try: compare(suffix[:-1], suffix); raise RuntimeError('missing-clause control was accepted')
    except AssertionError: pass
    report = {
        'result': 'PASS', 'parent_sha256': PARENT_SHA,
        'augmented_sha256': meta['augmented_sha256'], 'arms': meta['arms'], 'colour': 0,
        'row': ROW, 'profile': PROFILE, 'host_clauses': host_clauses,
        'changing_edges': len(expected_rules), 'added_clauses': len(suffix),
        'fresh_path_witness_variables': len(allocation),
        'parent_body_prefix_byte_exact': True, 'all_134995_host_clauses_exact': True,
        'all_nonhost_suffixes_avoid_changing_variables': True,
        'all_tseitin_and_long_clauses_exact': True,
        'negative_controls': ['rejected one flipped witness sign', 'rejected one deleted suffix clause'],
        'scope': 'CNF schema and configurable-MCF reduction only; no proof, SAT/UNSAT status, or physical-row assembly.'
    }
    Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
