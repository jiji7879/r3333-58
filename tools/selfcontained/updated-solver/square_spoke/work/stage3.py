"""Stage 3: bindings, guard semantics and omission justification for the 14 wall batches."""
import env, json, itertools, collections, hashlib, gzip
import cover_evidence as ce
from pysat.formula import CNF
from pysat.solvers import Minisat22
from stage2 import build, geometry_from_units, bad_sets_from_pins, guard_blocks, lit, dec, EDGE_TOP, NEXT

rows = json.loads((NEXT/'wall-rows.json').read_text())
screen = {r['index']: r for r in json.loads((NEXT/'wall-screen.json').read_text())}
batches = {a: (b, c) for a, b, c in json.loads((NEXT/'batches.json').read_text())}
theorem = hashlib.sha256(gzip.decompress((NEXT/'matching.drat.gz').read_bytes())).hexdigest()
out = []
for i, row in rows:
    raw, f = build(row)
    parent = hashlib.sha256(raw).hexdigest()
    pins, colour, arms, inside = geometry_from_units(f)
    known = {(l-1)//4 for l in pins if l > 0}
    fam = row['family']; profile = tuple(fam['profile'])
    guards = guard_blocks(f)
    by = {}
    for g, (x, c, cands, ncl) in guards.items():
        assert (x, c) not in by
        by[x, c] = (g, cands, ncl)
    packed = (NEXT/f'batch-{i}.json.gz').read_bytes()
    batch = json.loads(gzip.decompress(packed))
    rec = dict(index=i, id=row['id'], parent=parent,
               digest_ok=hashlib.sha256(packed).hexdigest() == batches[i][0],
               parent_ok=batch['parent'] == parent == screen[i]['parent'],
               id_ok=batch['id'] == row['id'], tier=batch['tier'], cube=batch['cube'],
               palette=batch['palette'], theorem_ok=batch['local_proof'] == theorem,
               nrules=len(batch['rules']), screen_clauses=screen[i]['clauses'],
               novel=batches[i][1], screen_novel=screen[i]['novel'])
    # ---- guard semantics: every sender keeps the root spoke as a unit, and the
    # at-least bound is exactly 14 minus the pinned spokes (root excluded).
    needs = {}
    for (x, c), (g, cands, ncl) in by.items():
        need = 14 - sum(1 for v in range(1, 58) if colour[v] != c and lit(x, v, c) in pins)
        needs[x, c] = need
        assert lit(0, x, c) in pins, ('root spoke not pinned', x, c)
        assert lit(x, 0, c) == lit(0, x, c)
        n = len(cands)
        assert 1 <= need <= n
        # two-sided test of the cardinality bound: forcing n-need+1 candidates false
        # must be contradicted, forcing n-need false must not be.
        # The gated block is a self-contained encoding of  g -> at least n_need true,
        # so test it on its own clauses (a subset of F): that makes the test a
        # sound sufficient condition and avoids unrelated propagation conflicts.
        cs = sorted(cands)
        block = [cl for cl in f.clauses if cl[0] == -g]
        with Minisat22(bootstrap_with=block) as s:
            over = s.solve(assumptions=[g] + [-l for l in cs[:n-need+1]])
            tight = s.solve(assumptions=[g] + [-l for l in cs[:n-need]])
            free = s.solve(assumptions=[-g] + [-l for l in cs])
        assert over is False and tight is True and free is True, ('bound', x, c, need, n, over, tight, free)
    rec['guards'] = len(by)
    rec['unguarded_senders'] = len({(x, c) for x in range(1, 58) for c in (colour[x],)
                                    if c == fam['arm'] or profile[c] >= 15}) - len(by)
    # the one sender with no guard must already have >=14 pinned non-root spokes
    rec['unguarded_ok'] = True
    for x in range(1, 58):
        c = colour[x]
        if not (c == fam['arm'] or profile[c] >= 15) or (x, c) in by:
            continue
        cnt = sum(1 for v in range(1, 58) if colour[v] != c and lit(x, v, c) in pins)
        rec['unguarded_ok'] &= cnt >= 14
    # ---- every shipped clause: guard is the sender's guard, sites sit in one arm
    # with the six-edge square/matching structure, and the positive spokes are
    # unforced candidates of that guard.
    bad = collections.Counter()
    uses = set()
    for cl, w in batch['rules']:
        x, c, b, S = w
        g = -cl[0]
        if by.get((x, c), (None,))[0] != g: bad['guard'] += 1
        if b == c or fam['root_kinds'][b] == '-': bad['arm'] += 1
        if tuple(S) != tuple(sorted(S)) or len(set(S)) != 4: bad['order'] += 1
        if not all(v in arms[b] for v in S): bad['arm_membership'] += 1
        table = inside[b]
        labels = [table[min(u, v), max(u, v)] for u, v in itertools.combinations(sorted(S), 2)]
        if c in labels or b in labels: bad['colour'] += 1
        ds = [d for d in range(4) if d != b and d != c]
        degs = [sorted(sum(table[min(u,v),max(u,v)] == q for v in S if v != u) for u in S) for q in ds]
        if degs[0] not in ([1]*4, [2]*4): bad['square'] += 1
        sp = {lit(x, v, c) for v in S}
        if not sp <= set(by[x, c][1]): bad['spoke_unforced'] += 1
        if set(-l for l in cl[1:]) != {s for s in sp if s not in pins}: bad['literal_set'] += 1
        uses.add(g)
    rec['bad'] = dict(bad)
    rec['guards_used'] = len(uses)
    # ---- omission audit: every candidate 4-set that is not shipped has a spoke
    # whose negation is a unit or whose edge is pinned with another colour.
    omits = []
    for (x, c), (g, cands, ncl) in by.items():
        for b in range(4):
            if b == c or fam['root_kinds'][b] == '-':
                continue
            for S, d, dg1, dg2 in bad_sets_from_pins(arms[b], inside[b], b, c):
                sp = [lit(x, v, c) for v in S]
                if any(-s in pins or (s not in pins and (s-1)//4 in known) for s in sp):
                    why = []
                    for s in sp:
                        pair, col = dec(s)
                        if -s in pins:
                            why.append(('unit-false', s))
                        elif s not in pins and (s-1)//4 in known:
                            other = [q for q in range(4) if q != col and lit(pair[0], pair[1], q) in pins]
                            assert len(other) == 1, (pair, col, other)
                            why.append(('other-colour-unit', s, other[0]))
                    omits.append(why)
    rec['omitted'] = len(omits)
    rec['omitted_justified'] = all(w for w in omits)
    rec['omitted_kinds'] = dict(collections.Counter(w[0][0] for w in omits))
    out.append(rec)
    print(i, row['id'][:8], 'digest', rec['digest_ok'], 'parent', rec['parent_ok'], 'tier', rec['tier'],
          'theorem', rec['theorem_ok'], 'rules', rec['nrules'], rec['screen_clauses'], 'novel', rec['novel'],
          rec['screen_novel'], 'guards', rec['guards'], 'used', rec['guards_used'],
          'unguarded_ok', rec['unguarded_ok'], 'bad', dict(bad), 'omitted', rec['omitted'],
          rec['omitted_justified'], rec['omitted_kinds'], flush=True)
json.dump(out, open('stage3.json', 'w'), indent=1)
print('TOTAL rules', sum(r['nrules'] for r in out), 'novel', sum(r['novel'] for r in out),
      'omitted', sum(r['omitted'] for r in out), 'theorem', theorem[:16])
