#!/usr/bin/env python3
"""One engine/budget, exact parent variants; explicit proof/timeout receipts."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/solver-improvement-2026-11-26'
RUN = OUT / os.environ.get('K58_BENCH_DIR', 'three-way')
RUN.mkdir(exist_ok=True)
CADICAL = Path('/opt/lean/bin/cadical')
DRAT = ROOT / '.scratch/satcheck/bin/drat-trim'
BUDGET = int(os.environ.get('K58_CONFLICTS', '100000'))
ALL = {
    'baseline': 'whole-81e8.cnf',
    'all-degree-caps': 'whole-81e8-plus-all-degree-caps.cnf',
    'unit-aware': 'whole-81e8-unit-aware-caps.cnf',
}
selected = set(os.environ.get('K58_CASES', ','.join(ALL)).split(','))
assert selected <= set(ALL)
for label, filename in ALL.items():
    if label not in selected:
        continue
    cnf = OUT / filename
    drat = RUN / (label + '.drat')
    log = RUN / (label + '.log')
    cmd = [str(CADICAL), '-q', '-c', str(BUDGET), str(cnf), str(drat)]
    wall0, time0, ru0 = time.monotonic(), time.process_time(), resource.getrusage(resource.RUSAGE_CHILDREN)
    timed_out = False
    with log.open('wb') as fh:
        try:
            run = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=120)
            rc = run.returncode
        except subprocess.TimeoutExpired:
            rc, timed_out = 124, True
    wall, cpu = time.monotonic() - wall0, time.process_time() - time0
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    verdict = {0: 'UNKNOWN', 10: 'SAT', 20: 'UNSAT'}.get(rc, 'TIMEOUT' if timed_out else 'ERROR')
    rec = dict(label=label, engine='CaDiCaL 2.1.2', engine_path=str(CADICAL),
               budget_conflicts=BUDGET, budget_wall=120, input=str(cnf.relative_to(ROOT)),
               input_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
               solver_rc=rc, verdict=verdict, wall_seconds=round(wall, 3),
               cpu_seconds=round(ru1.ru_utime + ru1.ru_stime - ru0.ru_utime - ru0.ru_stime, 3),
               process_seconds=round(cpu, 3), maximum_rss_kib=ru1.ru_maxrss,
               log=str(log.relative_to(ROOT)), command=cmd)
    if rc == 20:
        vlog = RUN / (label + '-verify.log')
        begin = time.monotonic()
        with vlog.open('wb') as fh:
            checked = subprocess.run([str(DRAT), str(cnf), str(drat), '-c'], stdout=fh, stderr=subprocess.STDOUT, timeout=600)
        text = vlog.read_text(errors='replace')
        rec.update(drat_verified=checked.returncode == 0 and 's VERIFIED' in text,
                   verify_seconds=round(time.monotonic() - begin, 3),
                   drat_sha256=hashlib.file_digest(open(drat, 'rb'), 'sha256').hexdigest())
        assert rec['drat_verified'], (label, text[-1000:])
    else:
        if drat.exists():
            drat.unlink()
        rec['drat_verified'] = False
    line = json.dumps(rec, sort_keys=True)
    with (RUN / 'benchmark.jsonl').open('a') as fh:
        fh.write(line + '\n')
    print(line, flush=True)
