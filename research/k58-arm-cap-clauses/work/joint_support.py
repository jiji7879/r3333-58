#!/usr/bin/env python3
"""Generate fixed-unit joint five-support exclusions for one hard1300 row.

A support gate implies every positive colour-c spoke of one compatible local
five-set. For two different root arms, a candidate pair is excluded only when
the ORIGINAL physical clauses induced on {root,sender}+both arms, together with
all ten positive support spokes, are UNSAT. OPEN and SAT are not exclusions.
The induced formula is a subset of the original parent, so every accepted
exclusion gives the original-variable clause consisting of the ten negated
spokes. With the gate implications, [-gate_p,-gate_q] is then justified.

This deliberately uses row placement/root units. It is not a template-only
universal incompatibility theorem. No historical proof bytes are used.
"""
import argparse
import collections
import itertools
import json
from pathlib import Path
import sys
import time

from pysat.formula import CNF
from pysat.solvers import Cadical195


def sha(data):
    import hashlib
    return hashlib.sha256(data).hexdigest()


def append_cnf(raw, extra, nv=None):
    head, body = raw.split(b'\n', 1)
    fields = head.split()
    assert fields[:2] == [b'p', b'cnf']
    old_nv, old_nc = int(fields[2]), int(fields[3])
    new_nv = old_nv if nv is None else max(old_nv, nv)
    out = f'p cnf {new_nv} {old_nc + len(extra)}\n'.encode() + body
    out += b''.join(' '.join(map(str, c)).encode() + b' 0\n' for c in extra)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', required=True, type=Path)
    ap.add_argument('--rank', required=True, type=int)
    ap.add_argument('--sender-color', type=int, default=3,
                    help='generate exclusions for guards of this colour; -1 means all')
    ap.add_argument('--query-conflicts', type=int, default=200000)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    assert 1 <= args.rank <= 1300 and 0 <= args.query_conflicts <= 200000
    assert -1 <= args.sender_color <= 3
    package = args.package.resolve()
    assert package.is_dir()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    # The requested output is required to be in this member's own directory.
    assert Path.cwd().resolve() in out.parents

    sys.path.insert(0, str(package))
    sys.path.insert(0, str(package / 'encoder'))
    import probe
    from cover_evidence import formula_chunks, identity

    r = probe.rows[args.rank - 1]
    row = probe.geometry[r['id']]
    assert identity(row) == r['id']
    guards = {}

    def watch(fr, event, arg):
        if event == 'call' and fr.f_code.co_name == 'atleast':
            prev = fr.f_back
            if prev.f_code.co_name == 'marked_threshold':
                v = prev.f_locals
                if fr.f_locals.get('lits') is v.get('candidates') and 'guard' in v:
                    guards[v['x']] = (v['c'], v['guard'])

    cpu0, wall0 = time.process_time(), time.perf_counter()
    for full in (True, False):
        guards.clear()
        sys.setprofile(watch)
        try:
            raw = b''.join(formula_chunks(
                row, dict(tables=True, total_critical=True, full_root=full)))
        finally:
            sys.setprofile(None)
        if sha(raw) == r['input_sha256']:
            break
    else:
        raise ValueError('full-root formula hash mismatch')
    assert full is True
    fdata = row['family'].copy()
    for k in ('root_kinds', 'profile'):
        fdata[k] = tuple(fdata[k])
    f = probe.Family(**fdata)
    fixed = {v for v, in probe.units(f, row['placement'])}
    known = {(v - 1) // 4 for v in fixed if v > 0}
    edge, _ = probe.host(58)
    edges = list(itertools.combinations(range(58), 2))
    form = CNF(from_string=raw.decode())
    assert sha(raw) == r['input_sha256']
    top = form.nv
    gates = {}
    selectors = []
    metadata = {}

    # This is the old extended construction, with gate identities retained.
    for x, (c, g) in guards.items():
        groups = []
        for b, (n, kind) in enumerate(zip(f.profile, f.root_kinds)):
            if b == c or kind == '-':
                continue
            start = 1 + sum(f.profile[:b])
            B = list(range(start, start + n))
            sp = [edge(x, start + i, c) for i in range(n)]
            must = {i for i, l in enumerate(sp) if l in fixed}
            blocked = {i for i, l in enumerate(sp)
                       if -l in fixed or ((l - 1) // 4 in known and l not in fixed)}
            full_opts = tuple(p for p in probe.catalog(n, kind, b, c)
                              if must.issubset(p) and blocked.isdisjoint(p))
            residual = tuple(tuple(i for i in p if i not in must) for p in full_opts)
            h = [tuple(sp[i] for i in idx) for idx in probe.hitting(n, residual)]
            groups.append(dict(arm=b, vertices=B, spokes=sp, must=sorted(must),
                               blocked=sorted(blocked), full_opts=full_opts,
                               residual=residual, hitting=h))
        choices = []
        for group in groups:
            opts = group['residual']
            if () in opts:
                choices.append(None)
                group['gates'] = []
                continue
            ids = []
            for opt in opts:
                lit_opt = tuple(group['spokes'][i] for i in opt)
                if lit_opt not in gates:
                    top += 1
                    gates[lit_opt] = top
                    selectors.extend([[-top, l] for l in lit_opt])
                ids.append(gates[lit_opt])
            group['gates'] = ids
            choices.append(ids)
        for i, j in itertools.combinations(range(len(groups)), 2):
            if choices[i] is not None and choices[j] is not None:
                selectors.append([-g, *choices[i], *choices[j]])
        metadata[x] = dict(color=c, guard=g, groups=groups)

    # Demand exact equality with the original old-extended implementation.
    old_raw, old_form, old_direct, old_selectors = probe.build(r)
    assert old_raw == raw and old_form.clauses == form.clauses
    if old_selectors != selectors:
        print('selector mismatch lengths', len(old_selectors), len(selectors))
        for di, (aa, bb) in enumerate(zip(old_selectors, selectors)):
            if aa != bb:
                print('first selector difference', di, aa, bb)
                break
        print('old tail', old_selectors[-3:])
        print('new tail', selectors[-3:])
        raise AssertionError('old selector reproduction failed')

    target = [(x, m) for x, m in metadata.items()
              if args.sender_color in (-1, m['color'])]
    target.sort()
    physical = [cl for cl in form.clauses
                if all(abs(l) <= 4 * len(edges) for l in cl)]
    records = []
    relation_summaries = []
    totals = collections.Counter()
    enum_cpu0, enum_wall0 = time.process_time(), time.perf_counter()

    for x, m in target:
        c = m['color']
        for gi, gj in itertools.combinations(range(len(m['groups'])), 2):
            A, B = m['groups'][gi], m['groups'][gj]
            if not A['gates'] or not B['gates']:
                continue
            vertices = {0, x, *A['vertices'], *B['vertices']}
            local_edges = set(itertools.combinations(sorted(vertices), 2))
            base = [cl for cl in physical
                    if all(edges[(abs(l) - 1) // 4] in local_edges for l in cl)]
            rel = dict(sender=x, color=c, guard=m['guard'],
                       arm_a=A['arm'], arm_b=B['arm'],
                       support_count_a=len(A['full_opts']),
                       support_count_b=len(B['full_opts']),
                       local_clauses=len(base), queries=0)
            counts = collections.Counter()
            with Cadical195(bootstrap_with=base) as sat:
                sat.configure({'seed': 0})
                sat.conf_budget(args.query_conflicts)
                for i, (p, gp) in enumerate(zip(A['full_opts'], A['gates'])):
                    for j, (q, gq) in enumerate(zip(B['full_opts'], B['gates'])):
                        positive = [A['spokes'][k] for k in p] + [B['spokes'][k] for k in q]
                        answer = sat.solve_limited(assumptions=positive)
                        rel['queries'] += 1
                        totals['queries'] += 1
                        counts[str(answer)] += 1
                        totals['answer_' + str(answer)] += 1
                        if answer is False:
                            rec = dict(sender=x, color=c, guard=m['guard'],
                                       arm_a=A['arm'], arm_b=B['arm'],
                                       support_a=i, support_b=j,
                                       indices_a=list(p), indices_b=list(q),
                                       gate_a=gp, gate_b=gq,
                                       gate_clause=[-gp, -gq],
                                       positive_spokes=positive,
                                       original_clause=[-l for l in positive])
                            records.append(rec)
                            totals['exclusions'] += 1
                        elif answer is None:
                            totals['discarded_OPEN'] += 1
                st = sat.accum_stats()
            rel['counts'] = dict(counts)
            rel['exclusions'] = counts['False']
            rel['solver_conflicts_cumulative'] = st['conflicts']
            rel['solver_propagations_cumulative'] = st['propagations']
            relation_summaries.append(rel)
            print('relation', x, c, A['arm'], B['arm'], dict(counts), flush=True)

    gate_clauses = sorted({tuple(sorted(c)) for c in
                           (z['gate_clause'] for z in records)})
    original_clauses = sorted({tuple(sorted(c)) for c in
                               (z['original_clause'] for z in records)})
    enum_wall = time.perf_counter() - enum_wall0
    enum_cpu = time.process_time() - enum_cpu0
    files = {
        'stock.cnf': raw,
        'extended.cnf': append_cnf(raw, selectors, top),
        'joint.cnf': append_cnf(raw, selectors + gate_clauses, top),
        'original-clauses.cnf': append_cnf(raw, selectors + original_clauses, top),
    }
    for name, data in files.items():
        (out / name).write_bytes(data)
    summary = dict(
        schema='fixed-unit-joint-five-support/v1',
        rank=args.rank, row_id=r['id'], profile=r['profile'], kinds=r['kinds'],
        input_sha256=r['input_sha256'], regenerated_parent_sha256=sha(raw),
        package=str(package), generator_sha256=sha(Path(__file__).read_bytes()),
        sender_color=args.sender_color, query_conflicts=args.query_conflicts,
        original_variables=form.nv, original_clauses=len(form.clauses),
        old_selector_clauses=len(selectors), extended_variables=top,
        new_gate_exclusions=len(gate_clauses),
        new_original_variable_clauses=len(original_clauses),
        query_totals=dict(totals), relation_summaries=relation_summaries,
        generation_cpu_seconds=time.process_time() - cpu0,
        generation_wall_seconds=time.perf_counter() - wall0,
        enumeration_cpu_seconds=enum_cpu, enumeration_wall_seconds=enum_wall,
        files={name: {'sha256': sha(data), 'bytes': len(data),
                      'clauses': len(form.clauses) + n}
               for (name, data), n in zip(files.items(),
                    (0, len(selectors), len(selectors) + len(gate_clauses),
                     len(selectors) + len(original_clauses)))},
        soundness_scope='Only original-parent induced physical UNSAT queries become exclusions. SAT and OPEN are discarded. Every gate clause has its ten-positive-spoke original-clause witness in exclusions.json. Row fixed units are essential premises; no template-only universality is claimed.',
        historical_proofs_used=False)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    (out / 'exclusions.json').write_text(json.dumps(records, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: summary[k] for k in
                      ('rank', 'row_id', 'old_selector_clauses',
                       'new_gate_exclusions', 'new_original_variable_clauses',
                       'query_totals', 'generation_wall_seconds',
                       'enumeration_wall_seconds')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
