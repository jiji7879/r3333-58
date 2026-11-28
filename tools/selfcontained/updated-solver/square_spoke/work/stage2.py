"""Stage 2: independent re-derivation of the ordinary-wall square clauses from the
parent CNF alone (units give the arm partition and the internal arm colours; the
guard->sender binding is read off the cardinality block, not from the encoder hook)."""
import env, json, itertools, collections, hashlib, gzip, sys, time
import cover_evidence as ce
from pysat.formula import CNF
from pysat.solvers import Minisat22

NEXT = env.NEXT
PAIRS = list(itertools.combinations(range(58), 2))
INDEX = {p: k for k, p in enumerate(PAIRS)}
EDGE_TOP = 4*len(PAIRS)

def lit(u, v, c): return 4*INDEX[tuple(sorted((u, v)))] + 1 + c
def dec(l):
    a = abs(l)-1
    return PAIRS[a//4], a % 4

def build(row):
    raw = b''.join(ce.formula_chunks(row, dict(tables=True, total_critical=True, full_root=False)))
    return raw, CNF(from_string=raw.decode())

def geometry_from_units(f):
    """Recover the arm partition and the pinned colour of every arm-internal pair."""
    pins = {cl[0] for cl in f.clauses if len(cl) == 1}
    assert all(-p not in pins for p in pins)
    colour = {}
    for v in range(1, 58):
        cs = [c for c in range(4) if lit(0, v, c) in pins]
        assert len(cs) == 1, (v, cs)
        colour[v] = cs[0]
    arms = collections.defaultdict(list)
    for v, c in colour.items():
        arms[c].append(v)
    arms = {c: tuple(sorted(vs)) for c, vs in arms.items()}
    assert set(arms) == set(range(4))
    inside = {}
    for c, vs in arms.items():
        table = {}
        for i, j in itertools.combinations(vs, 2):
            got = [d for d in range(4) if lit(i, j, d) in pins]
            if got:
                assert len(got) == 1 and got[0] != c, (c, i, j, got)
                table[i, j] = got[0]
        inside[c] = table
    return pins, colour, arms, inside

def bad_sets_from_pins(arm_vertices, table, b, c):
    """4-subsets of one arm whose six pinned internal edges avoid c and whose third
    colour is a 4-cycle (all degrees 2) or a perfect matching (all degrees 1)."""
    out = []
    for S in itertools.combinations(arm_vertices, 4):
        labels = [table[min(i,j), max(i,j)] for i, j in itertools.combinations(S, 2)]
        if c in labels:
            continue
        ds = [d for d in range(4) if d != b and d != c]
        assert len(ds) == 2
        d = ds[0]                       # pathcuts uses the smaller of the two other colours
        degs = [sorted(sum(table[min(i,j), max(i,j)] == q for j in S if j != i) for i in S) for q in ds]
        if degs[0] in ([1]*4, [2]*4):
            # six internal edges in two colours: either one colour is a 4-cycle and
            # the other a perfect matching, or both are perfect matchings.
            assert sorted([degs[0], degs[1]], key=sum) in ([[1]*4, [1]*4], [[1]*4, [2]*4]), (S, degs)
            out.append((S, d, tuple(degs[0]), tuple(degs[1])))
    return out

def guard_blocks(f):
    """A guard is a fresh variable v>EDGE_TOP whose clauses begin with -v and whose
    positive edge literals share one common endpoint and one colour."""
    blocks = collections.defaultdict(list)
    for cl in f.clauses:
        if len(cl) > 1 and cl[0] < 0 and -cl[0] > EDGE_TOP:
            blocks[-cl[0]].append(cl)
    guards = {}
    for g, cls in blocks.items():
        negedge = [l for cl in cls for l in cl[1:] if -EDGE_TOP <= l <= -1]
        if negedge:
            continue          # support-table selector: its block carries negative spokes
        eis = [(dec(l)[0], dec(l)[1], l) for cl in cls for l in cl[1:] if 1 <= l <= EDGE_TOP]
        if not eis:
            continue
        cs = {c for _, c, _ in eis}
        common = set.intersection(*[set(e) for e, _, _ in eis])
        if len(cs) != 1 or len(common) != 1:
            continue          # auxiliary counter variable, not a sender guard
        x = common.pop(); c = cs.pop()
        guards[g] = (x, c, frozenset(l for _, _, l in eis), len(cls))
    return guards

def run(i, row):
    t0 = time.process_time()
    raw, f = build(row)
    phash = hashlib.sha256(raw).hexdigest()
    pins, colour, arms, inside = geometry_from_units(f)
    fam = row['family']
    profile = tuple(fam['profile'])
    assert tuple(len(arms[c]) for c in range(4)) == profile, (profile, {c: len(v) for c, v in arms.items()})
    known = {(l-1)//4 for l in pins if l > 0}
    negpins = {-l for l in pins if l < 0}
    guards = guard_blocks(f)
    by_sender = {}
    for g, (x, c, cands, ncl) in guards.items():
        assert (x, c) not in by_sender, ((x, c), g, by_sender.get((x, c)))
        by_sender[x, c] = (g, cands, ncl)
    # independent sender set: every vertex whose arm has >=15 sites, plus every
    # vertex of the marked arm.  (dense.marked_threshold skip rule)
    senders = set()
    for v in range(1, 58):
        c = colour[v]
        if c == fam['arm'] or profile[c] >= 15:
            senders.add((v, c))
    report = dict(index=i, id=row['id'], parent=phash, profile=profile, arm=fam['arm'],
                  root_kinds=tuple(fam['root_kinds']), npins=len(pins),
                  senders=len(senders), guarded=len(by_sender), cpu_build=round(time.process_time()-t0, 3))
    emitted = {}
    skipped = collections.Counter()
    total_pairs = 0
    for (x, c), (g, cands, ncl) in by_sender.items():
        # independent candidate set, recomputed from the units
        need = 14
        mine = set()
        for v in range(1, 58):
            if colour[v] == c:
                continue
            e = lit(x, v, c)
            if e in pins:
                need -= 1
            elif -e not in pins and (e-1)//4 not in known:
                mine.add(e)
        assert mine == set(cands), ((x, c), len(mine), len(cands), sorted(mine ^ set(cands))[:8])
        assert 1 <= need <= len(mine), ((x, c), need, len(mine))
        report.setdefault('needs', []).append((x, c, need, len(mine), ncl))
        for b in range(4):
            if b == c or fam['root_kinds'][b] == '-':
                continue
            A = arms[b]
            table = inside[b]
            assert set(table) == set(itertools.combinations(A, 2)), ('unpinned internal pair', b)
            for S, d, degs, degs2 in bad_sets_from_pins(A, table, b, c):
                total_pairs += 1
                sp = [lit(x, v, c) for v in S]
                if any(-s in pins or (s not in pins and (s-1)//4 in known) for s in sp):
                    skipped['blocked'] += 1
                    continue
                cl = (-g, *sorted(-s for s in sp if s not in pins))
                if tuple(cl) in emitted:
                    skipped['duplicate'] += 1
                    continue
                emitted[tuple(cl)] = (x, c, b, list(S), need, d, degs)
    report.update(total_pairs=total_pairs, skipped=dict(skipped), clauses=len(emitted))
    # compare with the shipped batch
    batch = json.loads(gzip.decompress((NEXT/f'batch-{i}.json.gz').read_bytes()))
    shipped = {tuple(cl): tuple(w) for cl, w in batch['rules']}
    assert len(shipped) == len(batch['rules'])
    mine_w = {cl: (w[0], w[1], w[2], tuple(w[3])) for cl, w in emitted.items()}
    report['missing_vs_shipped'] = len(set(shipped) - set(mine_w))
    report['extra_vs_shipped'] = len(set(mine_w) - set(shipped))
    report['witness_mismatch'] = sum(1 for cl in set(shipped) & set(mine_w) if tuple(shipped[cl]) != mine_w[cl])
    report['lengths'] = dict(collections.Counter(len(cl) for cl in emitted))
    # independent unit-propagation survival count
    fresh = 0
    with Minisat22(bootstrap_with=f.clauses) as s:
        for cl in sorted(emitted, key=lambda q: (len(q), q)):
            ok, _ = s.propagate(assumptions=[-l for l in cl])
            fresh += 1 if ok else 0
    report['novel'] = fresh
    report['cpu_s'] = round(time.process_time()-t0, 3)
    print(i, row['id'][:8], 'senders', len(senders), 'guarded', len(by_sender), 'pairs', total_pairs,
          'clauses', len(emitted), 'skip', dict(skipped), 'novel', fresh,
          'miss/extra/wit', report['missing_vs_shipped'], report['extra_vs_shipped'], report['witness_mismatch'],
          report['cpu_s'], flush=True)
    return report

if __name__ == '__main__':
    rows = json.loads((NEXT/'wall-rows.json').read_text())
    only = [int(v) for v in sys.argv[1].split(',')] if len(sys.argv) > 1 else None
    out = []
    for i, row in rows:
        if only and i not in only:
            continue
        out.append(run(i, row))
    tag = sys.argv[2] if len(sys.argv) > 2 else 'stage2'
    json.dump(out, open(f'{tag}.json', 'w'), indent=1)
