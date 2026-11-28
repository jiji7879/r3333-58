"""Independent semantics checks for the supplied pivot counting/proof scheme.

Only the reviewed counter/formula constructors are imported; every model and
threshold truth value is evaluated independently here.
"""
from itertools import product
from pathlib import Path
import gzip, hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / '.scratch/color-wall-v1/base'
sys.path.insert(0, str(ARCHIVE))
from batches import counter, miter, encoded
from catalog import formula

checks = []
for n in range(1, 9):
    ins = [10*i+3 for i in range(n)]
    defs, outs, last = counter(ins, 1_000)
    assert len(outs) == n
    for bits in product([False, True], repeat=n):
        val = {k: v for k, v in zip(ins, bits)}
        def ev(lit):
            return val[abs(lit)] == (lit > 0)
        # Independently interpret each comparator as (OR,AND), following
        # the literal IDs rather than assuming consecutive threshold IDs.
        prefix = []
        wire = 1_000
        for item in ins:
            carry = val[item]
            new_prefix = []
            for previous in prefix:
                hi, lo = wire+1, wire+2
                val[hi] = previous or carry
                val[lo] = previous and carry
                wire += 2
                new_prefix.append(val[hi])
                carry = val[lo]
            prefix = new_prefix + [carry]
            assert prefix == sorted(prefix, reverse=True)
        assert len(prefix) == n and last == 1_000 + 2*(n-1)*n//2
        assert [ev(v) for v in outs] == prefix
        assert all(any(ev(l) for l in cl) for cl in defs)
        assert [ev(v) for v in outs] == [sum(bits)>=j for j in range(1,n+1)]
        checks.append({'inputs': n, 'true': sum(bits), 'extension': True})
# The identity above means each output is determined. If a second satisfying
# extension existed its output would have to differ, contradicting determinism.
n_assignments = sum(1 << n for n in range(1, 9))
assert len(checks) == n_assignments == 510

# Tiny SAT controls for miter: an entailed target has no counterexample; a
# non-target has one. We evaluate all original assignments, not an attached log.
raw = b'p cnf 2 2\n1 0\n2 0\n'
for targets, expected_counterexamples in [([[1]], False), ([[1,2]], False), ([[-1]], True), ([[2,-1]], False), ([[-2]], True), ([], False)]:
    q, flags = miter(raw, targets)
    lines = q.decode().splitlines(); header = list(map(int, lines[0].split()[2:]))
    clauses = [list(map(int, line.split()[:-1])) for line in lines[1:]]
    assert header[0] == 2+len(flags) and header[1] == len(clauses)
    h = hashlib.sha256(q).hexdigest()
    count = 0
    # A true flag makes every literal of its target false; the positive
    # disjunction requires at least one true flag. Evaluate the actual CNF
    # over all flag assignments rather than assuming every flag is true.
    for a,b in product([False,True], repeat=2):
        val = {1:a, 2:b}
        if a and b and any(all(val[abs(l)] == (l < 0) for l in cl) for cl in targets):
            count += 1
    satisfiable = False
    for a,b in product([False,True], repeat=2):
        for fs in product([False,True], repeat=len(flags)):
            val = {1:a, 2:b, **dict(zip(flags,fs))}
            satisfiable |= all(any(val[abs(l)] == (l>0) for l in cl) for cl in clauses)
    assert satisfiable == (count>0) == expected_counterexamples, (targets, count, satisfiable)
    assert len(flags) == len(targets)
    checks.append({'miter_targets': targets, 'violating_original_assignments': count,
                   'query_sha256': h, 'interpretation': 'SAT iff at least one target is falsified'})

# Native negative/positive controls for the reviewed strict proof callee.
control = ROOT/'.scratch/color-wall-v1/control'
control.mkdir(exist_ok=True)
checker = ROOT/'.scratch/new-proofs-v1/bin/drat-trim'
native_controls = {}
for name, raw, targets, additions, expected in [
        ('bogus', b'p cnf 2 1\n1 0\n', [[2]], [[2]], 'FAIL'),
        ('implied', b'p cnf 1 1\n1 0\n', [[1]], [[1]], 'PASS')]:
    q, flags = miter(raw, targets)
    d = control/name; d.mkdir(exist_ok=True)
    (d/'query.cnf').write_bytes(q)
    trace = encoded(additions + [[-f] for f in flags] + [[]])
    (d/'trace.rup').write_bytes(trace)
    p = subprocess.run([str(checker.resolve()), str(d/'query.cnf'), str(d/'trace.rup'),
                        '-I','-f','-W','-U'], capture_output=True, timeout=120)
    log = p.stdout.replace(b'\r',b'\n')
    ok = b'c WARNING' not in log and b's VERIFIED' in log and p.returncode in (0,1)
    native_controls[name] = {'expected': expected, 'rc': p.returncode,
        'log': log.decode(), 'no_warning': b'WARNING' not in log,
        'query_sha256': hashlib.sha256(q).hexdigest(),
        'trace_sha256': hashlib.sha256(trace).hexdigest()}
    if expected == 'PASS':
        assert ok and (p.returncode == 0 or b'c trivial UNSAT' in log)
    else:
        assert p.returncode == 1 and b'RUP check failed' in log
        assert b's NOT VERIFIED' in log and b'WARNING' not in log
cases = json.loads(gzip.open(ARCHIVE/'full-wall.json.gz').read())['cases']
shapes = {}
for i,c in enumerate(cases):
    verts,F,defs,last,targets,mat,palette = formula(c)
    assert len(verts) + len(c['support']) == c['order']
    assert len(targets) == sum((b['minimum']>0)+len(b['forced'])-1 for b in c['branches'])
    assert len(c['branches']) == 3
    shapes[str(verts)] = shapes.get(str(verts), 0) + 1
out = {'status':'PASS','counter_assignments_checked': n_assignments,
       'max_exhaustive_inputs': 8, 'unique_extension_argument':'sorted-comparator induction; the tests independently instantiate each output as count >= j',
       'miter_controls':'PASS including empty target list, tautology and falsifiable targets; all actual flag assignments evaluated',
       'native_controls': native_controls,
       'catalog_cases': len(cases), 'free_site_shapes': shapes,
       'unproved_by_this_test':'row binding and transported-proof scope; handled separately'}
path = ROOT/'research/k58-color-resolved-wall-pivots/checks/counter-control.json'
path.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
