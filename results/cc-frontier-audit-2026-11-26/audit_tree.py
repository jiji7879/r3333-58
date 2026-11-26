#!/usr/bin/env python3
"""Independent structural/artifact audit for smwwdcyxb/m7's merged C&C tree."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CC = ROOT / '.ultramath/smwwdcyxb/m7/cc'
PARENT = ROOT / 'results/cc-reciprocal-0404-2026-11-25/root.cnf'
OUT = ROOT / 'results/cc-frontier-audit-2026-11-26'
SHA_ROOT = 'aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(16 << 20), b''):
            h.update(b)
    return h.hexdigest()


def raw(gz):
    h = hashlib.sha256()
    with gzip.open(gz, 'rb') as fh:
        for b in iter(lambda: fh.read(16 << 20), b''):
            h.update(b)
    return h.hexdigest()


def leaf_hash(cube, lines):
    h = hashlib.sha256()
    h.update(('p cnf %d %d\n' % (lines[0], lines[1] + len(cube))).encode())
    h.update(lines[2])
    h.update(''.join('%s 0\n' % lit for lit in cube).encode())
    return h.hexdigest()


def receipt(worker, ident):
    r = None
    for line in open(CC / worker / 'receipts.jsonl'):
        x = json.loads(line)
        if x['id'] == ident:
            r = x
    assert r is not None, (worker, ident)
    return r


with PARENT.open('rb') as fh:
    head = fh.readline().split()
    assert head[:2] == [b'p', b'cnf']
    vals = (int(head[2]), int(head[3]), fh.read())
assert (vals[0], vals[1]) == (305513, 834101)
assert sha(PARENT) == SHA_ROOT

obj = json.loads((CC / 'merged-tree.json').read_text())
nodes = obj['nodes']
byid = {n['id']: n for n in nodes}
leaves = {l['id']: l for l in obj['leaves']}
assert len(byid) == len(nodes) == 343 and len(leaves) == 172
seen = set()
children_ids = set()
for n in nodes:
    ident = n['id']
    assert ident not in seen
    seen.add(ident)
    cube = n['cube']
    assert len({abs(x) for x in cube}) == len(cube), ident
    assert all(abs(x) in range(305482, 305514) for x in cube), ident
    kids = n.get('children') or []
    if not kids:
        assert ident in leaves
        continue
    assert len(kids) == 2
    x = n['split_variable']
    # split_literal is inherited from this node's own parent and must not be
    # confused with the new choice x at this node.
    for child_id, expected in zip(kids, [cube+[x], cube+[-x]]):
        c = byid[child_id]
        assert c['cube'] == expected
        assert c.get('parent_id') == ident
        assert c.get('split_literal') == expected[-1]
        children_ids.add(child_id)
    assert ident not in leaves
assert children_ids == set(byid)-{'n001'}
assert byid['n001']['cube'] == []
assert byid['n001'].get('parent_id') is None
CounterLeaves = Counter(l['verdict'] for l in leaves.values())
assert CounterLeaves == Counter({'UNSAT_VERIFIED': 169, 'UNKNOWN': 1, 'OPEN_NO_BUDGET': 2})
for open_leaf in obj['open_leaves']:
    assert leaves[open_leaf['id']]['cube'] == open_leaf['cube']
    assert leaves[open_leaf['id']]['verdict'] != 'UNSAT_VERIFIED'
    assert leaf_hash(open_leaf['cube'], vals) == open_leaf['cnf_sha256'] == leaves[open_leaf['id']]['cnf_sha256']

base = {x['id']: x for x in json.loads((PARENT.parent / 'continuation/tree.json').read_text())['records']}
ext = {tuple(map(int, key.split(','))): rec for key, rec in json.loads((CC/'external_verifications.json').read_text()).items()}
used_ext = set()
audit = []
for leaf in leaves.values():
    cube = leaf['cube']
    assert leaf_hash(cube, vals) == leaf['cnf_sha256'], leaf['id']
    if leaf['verdict'] != 'UNSAT_VERIFIED':
        assert leaf.get('drat_sha256') is None
        audit.append({'id': leaf['id'], 'verdict': leaf['verdict'], 'proof': False})
        continue
    if leaf['source'] == 'continuation':
        r = base[leaf['id']]
        assert r['cube'] == cube
        a = r['verified_artifacts']
        cg = PARENT.parent / 'continuation' / a['cnf_gzip']
        dg = PARENT.parent / 'continuation' / a['drat_gzip']
        assert sha(cg) == a['cnf_gzip_sha256']
        assert sha(dg) == a['drat_gzip_sha256']
        assert raw(cg) == leaf['cnf_sha256']
        assert raw(dg) == leaf['drat_sha256'] == r['drat_sha256']
        kind = 'pilot'
    else:
        key = tuple(cube)
        if key in ext:
            used_ext.add(key)
            r = receipt(leaf['source'], leaf['id'])
            cnf, drat = CC/ext[key]['cnf'], CC/ext[key]['drat']
            assert sha(cnf) == leaf['cnf_sha256'] == r['cnf_sha256']
            assert sha(drat) == leaf['drat_sha256'] == ext[key]['drat_sha256'] == r['drat_sha256']
            log = (CC/ext[key]['log']).read_text(errors='replace')
            assert 's VERIFIED' in log and ext[key]['verification_time'] in log
            kind = 'external'
            assert len(cube) == ext[key]['cube_len']
        else:
            r = receipt(leaf['source'], leaf['id'])
            assert r['cube'] == cube
            a = r['verified_artifacts']
            cg, dg = CC/leaf['source']/a['cnf_gzip'], CC/leaf['source']/a['drat_gzip']
            assert sha(cg) == a['cnf_gzip_sha256']
            assert sha(dg) == a['drat_gzip_sha256']
            assert raw(cg) == leaf['cnf_sha256']
            assert raw(dg) == leaf['drat_sha256'] == r['drat_sha256']
            kind = 'inline'
            assert leaf['source'].startswith('run')
    audit.append({'id': leaf['id'], 'verdict': 'certificate_files_and_hashes_ok',
                  'proof': kind, 'source': leaf['source'], 'drat_sha256': leaf['drat_sha256']})
assert used_ext == set(ext), (len(used_ext), len(ext))
assert Counter(x['proof'] for x in audit) == Counter({'inline':155, 'pilot':9, 'external':5, False:3})
summary = dict(root_sha256=SHA_ROOT, nodes=343, leaves=172,
               verdicts=dict(CounterLeaves),
               proof_artifacts=dict(Counter(x['proof'] for x in audit if x['proof'])),
               open_leaves=obj['open_leaves'],
               all_leaf_cnfs_rebuilt=True,
               all_pilot_and_inline_compressed_proof_hashes_checked=True,
               all_external_uncompressed_cnf_and_proof_hashes_checked=True,
               all_external_verification_logs_contain_verified=True,
               fresh_replays='Separate: pilot fresh replays and selected out-of-band replay',
               scope='Exact disjunction for the named augmented reciprocal CNF only; no whole-row closure.')
(OUT/'artifacts-audit.json').write_text(json.dumps(summary, indent=2)+'\n')
(OUT/'leaf-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
print(json.dumps(summary, indent=2))
print('PASS: exact 343-node binary tree, 169 identified proof artifacts, 3 open cubes')
