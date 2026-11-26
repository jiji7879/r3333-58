#!/usr/bin/env python3
"""Bind m6's reported augmented leaves to the literal root+cube formulas."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / '.ultramath/smwwdcyxb/m6'
O = ROOT / 'results/m6-audit-2026-11-26'
ROOT_CNF = ROOT / 'results/cc-reciprocal-0404-2026-11-25/root.cnf'
ROOT_SHA = 'aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44'


def sha(data):
    return hashlib.sha256(data).hexdigest()


manifest = {}
for line in (M / 'MANIFEST.sha256').read_text().splitlines():
    if line.strip():
        digest, name = line.split()
        manifest[name] = digest

root_bytes = ROOT_CNF.read_bytes()
assert sha(root_bytes) == ROOT_SHA
header, root_body = root_bytes.split(b'\n', 1)
words = header.split()
assert words[:2] == [b'p', b'cnf']
nv, nc = int(words[2]), int(words[3])
assert (nv, nc) == (305513, 834101)
assert root_body.count(b'\n') == nc
records = json.loads((ROOT_CNF.parent / 'continuation/tree.json').read_text())['records']
leaf_logs = {'n017': 'verify-lc2-n017.log', 'n022': 'verify-lc-n022.log',
             'n024': 'verify-lc6-n024.log'}
old_times = {'n017': '1217.502', 'n022': '643.953', 'n024': '911.043'}
metadata = {}
for ident in ('n017', 'n022', 'n024'):
    rec = next(r for r in records if r['id'] == ident)
    cube = rec['cube']
    cube_blob = b''.join(('%d 0\n' % lit).encode() for lit in cube)
    bare_formula = ('p cnf %d %d\n' % (nv, nc + len(cube))).encode() + root_body + cube_blob
    bare_name = 'leaf-' + ident + '.cnf'
    assert sha(bare_formula) == manifest[bare_name], (ident, 'root+cube hash')
    bare = (M / bare_name).read_bytes()
    assert sha(bare) == manifest[bare_name]
    ext_name = 'leaf-' + ident + ('-fam.cnf' if ident == 'n024' else '-dcap.cnf')
    augmented = (M / ext_name).read_bytes()
    ah, abody = augmented.split(b'\n', 1)
    an, acl = map(int, ah.split()[2:4])
    assert sha(augmented) == manifest[ext_name], (ident, 'augmented CNF hash')
    assert abody.startswith(root_body), (ident, 'root clause block changed')
    proof_name = {'n017': 'lc2-n017.drat', 'n022': 'lc-n022.drat',
                  'n024': 'lc6-n024.drat'}[ident]
    proof = M / proof_name
    assert sha(proof.read_bytes()) == manifest[proof_name]
    receipt = (M / leaf_logs[ident]).read_text()
    assert 's VERIFIED' in receipt
    assert old_times[ident] + ' seconds' in receipt
    metadata[ident] = dict(
        cube=cube, bare_cnf_sha256=manifest[bare_name],
        augmented_cnf=ext_name, augmented_cnf_sha256=manifest[ext_name],
        augmented_clauses=acl, augmented_variables=an,
        proof=proof_name, proof_sha256=manifest[proof_name],
        proof_bytes=proof.stat().st_size,
        retained_verified_receipt=True,
        retained_verification_seconds=float(old_times[ident]),
        root_body_unchanged=True,
        fresh_replay='Fresh n024 replay only; no redundant replay of n017/n022 here.')
fresh = (O / 'replay-n024.log').read_text()
assert 's VERIFIED' in fresh
metadata['n024']['fresh_replay'] = 's VERIFIED in independent judge replay'
metadata['n024']['fresh_replay_log'] = 'results/m6-audit-2026-11-26/replay-n024.log'
(O / 'leaf-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')

options = sorted((a, b, c, d) for a in (15, 16) for b in (15, 16)
                 for c in range(15) for d in range(15) if a+b+c+d == 57)
source = sorted(tuple(map(int, line.split(',')))
                for line in (M / 'profiles12.txt').read_text().splitlines() if line.strip())
assert options == source, (options, source)
residual = next(r['cube'] for r in records if r['id'] == 'n025')
(O / 'coverage.json').write_text(json.dumps({
    'original_13_leaves_closed': 12,
    'original_residual_id': 'n025',
    'original_residual_cube': residual,
    'twelve_profile_options_exact': True,
    'twelve_profile_options': options,
    'later_m7_tree_residual_note': 'm7 separately refined the root to three open cubes; this report does not claim to supersede it.',
    'full_rows_closed': 0,
    'full_profiles_closed': 0,
    'scope': 'Equal-kind reciprocal/inactive relaxations and three augmented leaf refutations; not the ticket-balanced, strict or mixed full-row alternatives.'}, indent=2) + '\n')
print('PASS n017,n022,n024: root+cube, augmented input and proof SHA-256 checked')
print('PASS all three retained verification receipts; fresh independent n024 replay')
print('PASS 12 exact profile options, and original residual n025 only')
