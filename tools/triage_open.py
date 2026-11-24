#!/usr/bin/env python3
"""Which profiles are the cases that are still OPEN in?

Reads an evidence directory (the one the runner wrote) and the frozen ledger, takes the
LAST attempt per case, and reports every case still OPEN grouped by profile and stratum.

    python3 triage_open.py --evidence /path/to/evidence --ledger /path/to/k58/case-ledger.jsonl.gz
    python3 triage_open.py --evidence ... --ledger ... --list    # also print the case ids

Reads receipts only; writes nothing.
"""
import argparse, gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path

def ledger(path):
    with gzip.open(path, 'rt') as f:
        for line in f:
            r = json.loads(line)
            fam = r.get('family') or {}
            yield r['id'], {
                'profile': ','.join(map(str, fam.get('profile', []))),
                'kinds': ''.join(fam.get('root_kinds', [])),
                'arm': fam.get('arm'),
                'charge': r.get('charge'),
                'status': r.get('status'),
            }

def attempts(ev):
    """case id -> list of (tier, path) attempts, in a stable order."""
    out = defaultdict(list)
    for d in ev.iterdir():
        if not d.is_dir() or len(d.name) != 2:
            continue
        for case in d.iterdir():
            if not case.is_dir():
                continue
            for tier in ('first', 'retry'):
                t = case / tier
                if not t.is_dir():
                    continue
                for sub in sorted(t.iterdir()):
                    if sub.is_dir():
                        out[case.name].append((tier, sub))
                    elif sub.suffix == '.jsonl':
                        out[case.name].append((tier, t))
    return out

def last_status(paths):
    """the status recorded by the final attempt"""
    best = None
    for tier, p in paths:
        files = sorted(p.glob('*.jsonl')) if p.is_dir() else [p]
        for f in files:
            try:
                rec = json.loads(f.read_text().strip().splitlines()[-1])
            except Exception:
                continue
            best = (tier, rec.get('status'))
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--ledger', type=Path, required=True)
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    meta = dict(ledger(a.ledger))
    att = attempts(a.evidence)
    open_cases, seen = [], set()
    for cid, paths in att.items():
        st = last_status(paths)
        seen.add(cid)
        if st and st[1] == 'OPEN':
            open_cases.append((cid, st[0], meta.get(cid, {})))
    print(f'cases with receipts : {len(seen)}')
    print(f'cases still OPEN    : {len(open_cases)}')
    if not open_cases:
        return
    by_prof = Counter(m.get('profile', '?') for _, _, m in open_cases)
    print('\nby profile (open / total in ledger):')
    tot = Counter(m['profile'] for m in meta.values())
    for prof, n in by_prof.most_common():
        print(f'  {prof:<16} {n:>6} open  of {tot.get(prof, 0):>6} rows')
    by_strat = Counter((m.get('profile', '?'), m.get('kinds', '?')) for _, _, m in open_cases)
    print('\nby (profile, kinds) stratum:')
    for (prof, kinds), n in by_strat.most_common(20):
        print(f'  {prof:<16} {kinds:<6} {n:>6}')
    if a.list:
        print('\ncase ids:')
        for cid, tier, m in sorted(open_cases, key=lambda z: (z[2].get('profile', ''), z[0])):
            print(f'  {cid}  {m.get("profile","?"):<16} {m.get("kinds","?"):<6} last={tier}')

if __name__ == '__main__':
    main()
