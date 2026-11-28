#!/usr/bin/env python3
"""One bounded, resumable frontend for K58 stock/colour/square engines.

A cohort is a list of independently checked subproblems, not a Ramsey cover
solver.  It does not run finalise or promote an augmented result to an original
parent closure.  Every leaf run has positive finite seconds/conflicts limits;
workers run one leaf solver each.  No cohort-wide SAT/UNSAT claim is inferred
from per-job capped statuses.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import threading
import sys
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PYTHON = sys.executable
VARIANTS = ('original', 'counter', 'escape', 'color', 'square',
            'square-counter', 'square-escape', 'square-color')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


def json_bytes(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def atomic_json(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.partial')
    require(not temp.exists(), f'stale temporary file: {temp}')
    temp.write_bytes(json.dumps(data, indent=2, sort_keys=True).encode() + b'\n')
    temp.replace(path)


def package_sources():
    paths = ['unified/driver.py', 'unified/store.py', 'color-resolved-wallcc/wallcc.py',
             'color-resolved-wallcc/campaign.py', 'color-resolved-wallcc/color_pivot.py',
             'color-resolved-wallcc/square_merge.py', 'color-resolved-wallcc/native_leaf.py',
             'color-resolved-wallcc/bin/cadical-2.1.2']
    return {p: file_hash(ROOT / p) for p in paths}


def dimensions(depth, workers, seconds, conflicts, shards, shard):
    require(depth >= 1, 'use a positive leaf depth; no implicit whole-parent unbounded solve')
    require(1 <= workers <= 16, 'workers must be in 1..16 (per-leaf search concurrency, not nested jobs)')
    require(seconds >= 1 and conflicts >= 1, 'both --seconds and --conflicts must be positive')
    require(shards >= 1 and 0 <= shard < shards, 'need 0 <= --shard < --shards')
    return {'depth': depth, 'workers': workers, 'seconds_per_leaf': seconds,
            'conflicts_per_leaf': conflicts, 'shards': shards, 'shard': shard}


@contextlib.contextmanager
def cohort_lock(out):
    with (Path(out) / '.cohort.lock').open('a+b') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def square_rows():
    path = ROOT / 'square_spoke/source/next/wall-rows.json'
    return {row['id']: index for index, row in json.loads(path.read_text())}


def init_color_modules():
    if getattr(local_lookup, '_imported', False):
        return
    for name in ['color-resolved-wallcc', 'color-resolved-wallcc/frozen',
                 'square_spoke/work', 'square_spoke/source/hard-study',
                 'square_spoke/source/hard-more', 'square_spoke/source/next']:
        sys.path.insert(0, str(ROOT / name))
    local_lookup._imported = True


def local_lookup(spec):
    spec = spec.lower()
    if spec.startswith('square:'):
        arg = spec.split(':', 1)[1]
        require(arg.isdigit(), 'square index must be a decimal integer')
        indices = {str(index): row_id for row_id, index in square_rows().items()}
        require(arg in indices, f'unknown square index {arg}; use `square rows`')
        return indices[arg]
    require(len(spec) >= 12 and all(c in '0123456789abcdef' for c in spec),
            'wall row selector must be a >=12 hexadecimal prefix')
    init_color_modules()
    from problem import lookup
    return lookup(spec)['id']


def available_rows(profiles):
    if not getattr(local_lookup, '_imported', False):
        # Import once for both enumerate and lookup; never change input files.
        local_lookup('square:0')
    from problem import roster
    profiles = set(profiles or ())
    selected = [row for row in roster().values() if not profiles or
                ','.join(map(str, row['family']['profile'])) in profiles]
    return sorted(row['id'] for row in selected)


def make_plan(args, out):
    # Initialise the read-only color/problem modules before either row lookup
    # or canonical external-CNF import, including --external-only invocations.
    init_color_modules()
    require(args.depth >= 1 and args.lookahead >= 1 and args.seconds >= 1 and args.conflicts >= 1,
            'finite positive per-leaf budgets are mandatory even for dry-run')
    require(args.check_seconds >= 1 and args.max_total_conflicts >= 1,
            'positive finite total/check budgets are required')
    require(args.wall_seconds >= 2 * args.seconds + args.check_seconds + 2,
            'wall clock must cover a full bounded search+proof workflow')
    if args.external:
        require(not args.rows and not args.profiles, 'external CNFs cannot be combined with wall row selectors')
        require(args.variants == 'external', '--external requires --variants external')
        jobs = []
        from problem import external_formula
        for source in map(lambda p: p.resolve(), args.external):
            raw, origin = external_formula(source)
            jobs.append({'id': sha(source.as_posix().encode() + b':' + sha(raw).encode())[:20],
                         'kind': 'external', 'variant': 'external',
                         'name': Path(source).name, 'source': str(source),
                         'source_sha256': origin['source_sha256']})
    else:
        require(args.rows or args.profiles,
                'choose explicit --rows or --profiles; external is a separate selector')
        ids = [local_lookup(s) for s in args.rows.split(',')] if args.rows else available_rows(args.profiles.split(','))
        require(len(ids) == len(set(ids)), 'duplicate selected wall row after normalization')
        require(ids, 'no wall rows match the requested selection')
        variants = args.variants.split(',')
        allowed = set(VARIANTS)
        require(all(v in allowed for v in variants), 'unsupported frontend variant')
        require(len(variants) == len(set(variants)), 'duplicate variant')
        if any(v.startswith('square') for v in variants):
            supported = square_rows()
            for row in ids:
                require(row in supported, f'row {row} lacks an audited square batch')
        jobs = []
        for row in sorted(ids):
            for variant in variants:
                jobs.append({'id': sha(f'{row}:{variant}'.encode())[:20],
                             'kind': 'wall', 'variant': variant, 'row': row,
                             'square_index': square_rows().get(row)})
    if args.limit is not None:
        require(args.limit >= 1, '--limit must be positive; zero is not a special unbounded mode')
        jobs = jobs[:args.limit]
    selected_before_sharding = len(jobs)
    jobs = [job for i, job in enumerate(sorted(jobs, key=lambda j: (j.get('row', j.get('name', j['id'])), j['variant'])))
            if i % args.shards == args.shard]
    require(jobs, 'the selected shard has no jobs')
    stored = {'schema': 'k58-unified-research-cohort/v1',
              'jobs': jobs, 'selected_before_sharding': selected_before_sharding,
              'split': {'depth': args.depth, 'lookahead': args.lookahead},
              'shards': args.shards, 'shard': args.shard,
              'limits': {'seconds_per_leaf': args.seconds, 'conflicts_per_leaf': args.conflicts,
                         'wall_seconds_per_call': args.wall_seconds, 'check_seconds': args.check_seconds,
                         'max_total_conflicts': args.max_total_conflicts},
              'sources': package_sources(),
              'scope': 'independently verified subproblems; augmented/strengthened results are not original-parent closures'}
    atomic_json(out / 'cohort.json', stored)
    return stored


def read_plan(out):
    path = Path(out) / 'cohort.json'
    require(path.is_file(), 'no cohort plan; use `unified run --rows ... --out NEW`')
    plan = json.loads(path.read_text())
    require(plan['schema'] == 'k58-unified-research-cohort/v1', 'unknown cohort schema')
    validate_stored_plan(plan)
    plan['source_warning'] = [{'file': name, 'planned_sha256': old, 'current_sha256': file_hash(ROOT / name)}
                               for name, old in plan['sources'].items()
                               if old != file_hash(ROOT / name)]
    return plan


def validate_stored_plan(plan):
    init_color_modules()
    ids = set()
    for job in plan['jobs']:
        require(job['variant'] in (*VARIANTS, 'external'), 'unsupported stored job variant')
        require(job['id'] not in ids, 'duplicate stored job id')
        ids.add(job['id'])
        if job['kind'] == 'external':
            require(job['variant'] == 'external', 'stored external job used a row variant')
            from problem import external_formula
            _, origin = external_formula(Path(job['source']))
            require(origin['source_sha256'] == job['source_sha256'], 'external source changed since planning')
        else:
            require(job['kind'] == 'wall' and job['variant'] in VARIANTS, 'bad stored wall job')
            require(job['row'] == local_lookup(job['row']), 'stored wall row cannot be rebound exactly')
            require(job['id'] == sha(f"{job['row']}:{job['variant']}".encode())[:20],
                    'stored job ID differs from its row and variant')
            if job['variant'].startswith('square'):
                require(job['row'] in square_rows(), 'stored job lacks checked square data')
    require(isinstance(plan.get('limits'), dict), 'plan must include finite limits')
    for name in ('seconds_per_leaf', 'conflicts_per_leaf', 'wall_seconds_per_call',
                 'check_seconds', 'max_total_conflicts'):
        require(isinstance(plan['limits'][name], int) and plan['limits'][name] > 0,
                'cohort limits must be finite positive integers')
    return plan


def attempt_key(job, plan):
    return sha(json_bytes({'job': job, 'split': plan['split'], 'limits': plan['limits'],
                           'sources': plan['sources']})).hexdigest()[:16]


def engine(job, plan, action, limits, again=False):
    """Invoke the existing proof-checking engine; don't merge its auxiliaries manually."""
    args = [SYSTEM_PYTHON, str(ROOT / 'color-resolved-wallcc/wallcc.py'), action]
    folder = Path(limits['out']) / 'jobs' / job['id']
    if action in ('prepare', 'run'):
        args += ['--out', str(folder), '--depth', str(plan['split']['depth']),
                 '--lookahead', str(plan['split']['lookahead'])]
    else:
        args.append(str(folder))
    if job['kind'] == 'external':
        if action in ('prepare', 'run'):
            args += ['--cnf', job['source']]
    else:
        variant = job['variant']
        pivot = 'off' if variant in ('original', 'square') else 'color' if variant == 'square-color' else \
                'counter' if variant == 'square-counter' else 'escape' if variant == 'square-escape' else variant
        square = variant.startswith('square')
        if action in ('prepare', 'run') and job['kind'] == 'wall':
            args += ['--row', job['row'], '--tier', 'first']
        if action in ('prepare', 'run'):
            args += ['--cas', 'pentagon', '--pivot-color', pivot]
            if square:
                args.append('--square-spokes')
    if action == 'export-drat':
        args.append(str(folder / 'composed.drat'))
        args += ['--method', 'compact', '--checker', str(ROOT / 'bin/drat-trim'),
                 '--check-seconds', str(limits['check_seconds'])]
    elif action != 'prepare':
        args += ['--jobs', '1', '--checker', str(ROOT / 'bin/drat-trim')]
        if action == 'run':
            args += ['--conflicts', str(limits['conflicts_per_leaf']),
                     '--seconds', str(limits['seconds_per_leaf'])]
    else:
        args += ['--checker', str(ROOT / 'bin/drat-trim')]
    if action == 'prepare':
        args += ['--check-seconds', str(limits['check_seconds'])]
    if action == 'verify':
        expected = json.loads((folder / 'plan.json').read_text())['parent_sha256']
        args += ['--expect-sha256', expected]
    if action == 'run' and again:
        args.append('--again')
    if action == 'export-drat' and (folder / 'composed.drat').exists():
        from campaign import check_trace
        passed, log = check_trace(Path(folder) / 'parent.cnf', folder / 'composed.drat',
                                  ROOT / 'bin/drat-trim', limits['check_seconds'], '-U')
        if not passed:
            raise ValueError('existing composed DRAT does not replay')
        stored = json.loads((folder / 'plan.json').read_text())
        reply = {'status': 'VERIFIED_UNSAT', 'parent_sha256': stored['parent_sha256'],
                 'drat_sha256': file_hash(folder / 'composed.drat'), 'origin': stored['origin'],
                 'method': 'compact', 'reused': True, 'checker_log': log}
        return {'command': action, 'exit_code': 0, 'elapsed_seconds': 0.0,
                'timeout': False, 'result': reply}

    env = dict(os.environ)
    env['K58_SQUARE_ROOT'] = str(ROOT / 'square_spoke')
    env['PYTHONPATH'] = ':'.join([str(ROOT / 'color-resolved-wallcc'),
                                  str(ROOT / 'color-resolved-wallcc/frozen')])
    scratch = Path(limits['out']) / '.scratch'
    scratch.mkdir(exist_ok=True)
    env['TMPDIR'] = str(scratch)
    started = time.monotonic()
    # The CPU-safe cap kills only the process group owned by this one bounded
    # invocation.  It is never detached as a daemon and is always reaped.
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=env, text=True, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=limits['wall_seconds_per_call'])
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=5)
    except BaseException:
        # A malformed receipt, bad CLI construction or verifier exception must
        # not leave its solver children running after the frontend has failed.
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=5)
        raise
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'{action}.log').write_text(stdout + '\n[stderr]\n' + stderr)
    reply = None
    for line in reversed(stdout.splitlines()):
        if line.startswith('{'):
            try:
                reply = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(reply, dict):
                break
    return {'command': action, 'exit_code': process.returncode, 'timeout': timed_out, 'elapsed_seconds': time.monotonic() - started,
            'result': reply, 'command_argv': [str(x) for x in args]}


def scope(job):
    if job['kind'] == 'external':
        return 'caller-supplied DIMACS only; no original-parent or K58 row claim'
    variant = job['variant']
    if variant == 'original':
        return 'ordinary first-tier parent; a complete verified UNSAT cover remains row-specific'
    if variant == 'square':
        return 'original parent + checked local K15 rules; no original-parent DRAT lift asserted'
    if variant.startswith('square-'):
        return 'square-strengthened aux-extended parent; colour derivation and K15 rules are separate evidence'
    return 'aux-extended parent with native original-plus-counter derivation, not a monolithic original proof'


def check_case_model(job, folder):
    """Project a checked leaf model to original variables and recheck all clauses."""
    from pysat.formula import CNF
    if job['kind'] == 'wall':
        from problem import row_formula, lookup
        raw = row_formula(lookup(job['row']), 'first')
    else:
        # An external model is verified against its exact caller-supplied
        # parent; it never fabricates a stock K58 parent for this purpose.
        raw = (Path(folder) / 'parent.cnf').read_bytes()
    original_hash = sha(raw)
    base = CNF(from_string=raw.decode())
    cases = []
    for receipt_path in sorted((Path(folder) / 'leaves').glob('*/receipt.json')):
        receipt = json.loads(receipt_path.read_text())
        if receipt['status'] != 'CHECKED_SAT':
            continue
        model = json.loads((receipt_path.parent / 'model.json').read_text())
        require(isinstance(model, list) and all(type(x) is int and 0 < abs(x) for x in model),
                'case model has an invalid literal')
        # Auxiliary variables above the original header top are a valid colour
        # extension; evaluate the original first-tier parent on their projection.
        model = [lit for lit in model if abs(lit) <= base.nv]
        assigned = set(model)
        require(not any(-lit in assigned for lit in assigned), 'model has complementary assignments')
        for clause in receipt['cube']:
            require(clause in assigned, 'the model does not contain its leaf cube')
        require(all(any(lit in assigned for lit in clause) for clause in base.clauses),
                'restricted model fails the regenerated original parent')
        cases.append({'leaf': receipt_path.parent.name, 'original_parent_sha256': original_hash,
                      'model_artifact_sha256': receipt['artifact_sha256'],
                      'model_file': str(receipt_path.parent / 'model.json'),
                      'restriction_to_original_variables': True,
                      'kind': 'CASE_SAT' if job['kind'] == 'wall' else 'EXTERNAL_MODEL_VERIFIED_LEAF'})
        require(len({abs(l) for l in assigned}) == base.nv,
                'original-variable projection is not a total assignment')
    require(cases, 'VERIFIED_SAT has no validated leaf model to project')
    return cases


def run_one(job, plan, limits, again):
    folder = Path(limits['out']) / 'jobs' / job['id']
    folder.mkdir(parents=True, exist_ok=True)
    report = {'job': job, 'scope': scope(job), 'stock_finalise_eligible': False,
              'events': []}
    try:
        with limits['allocation_lock']:
            require(limits['allocated_conflicts'][0] < limits['max_total_conflicts'],
                    'total conflict budget exhausted before preparing this job')
        preparation = engine(job, plan, 'prepare', limits)
        report['events'].append(preparation)
        if preparation.get('timeout') or preparation['exit_code'] != 0:
            raise RuntimeError('prepare failed; see prepare.log')
        from store import capture_directory
        report['artifact_store'] = capture_directory(folder, Path(limits['cohort_root']))
        require(shutil.disk_usage(folder.parent).free >= limits['min_free_bytes'],
                'disk guard: insufficient free space before bounded solver generation')
        child_plan = json.loads((folder / 'plan.json').read_text())
        estimated_conflicts = 2 * child_plan['leaf_count'] * limits['conflicts_per_leaf']
        with limits['allocation_lock']:
            require(limits['allocated_conflicts'][0] + estimated_conflicts <= limits['max_total_conflicts'],
                    'total conflict budget exhausted before this bounded leaf search')
            limits['allocated_conflicts'][0] += estimated_conflicts
        bounded = engine(job, plan, 'run', limits, again)
        report['_allocated'] = limits['allocated_conflicts'][0]
        report['events'].append(bounded)
        if bounded.get('timeout') or bounded['exit_code'] != 0:
            raise RuntimeError('bounded leaf run failed; see run.log')
        checked = engine(job, plan, 'verify', limits)
        report['events'].append(checked)
        if checked.get('result') is None:
            raise RuntimeError('verification returned no receipt')
        if checked['result'].get('status') == 'CHECK_FAILED' or checked['exit_code'] == 1:
            raise RuntimeError('verification failed; see verify.log')
        if checked['exit_code'] == 1 or (checked['result'] or {}).get('status') == 'CHECK_FAILED':
            raise RuntimeError('parent/leaf verification failed')
        # OPEN is an expected bounded result.  Exit 2 comes from the verifier
        # precisely for that outcome and cannot be silently neutralized as SAT.
        require(checked['exit_code'] in (0, 2), 'unexpected verifier status')
        report['verified_stage'] = checked
        report['status'] = checked['result']['status']
        parent = json.loads((folder / 'plan.json').read_text())
        require(parent['origin'] == checked['result']['origin'], 'verification origin changed')
        require(parent['parent_sha256'] == checked['result']['parent_sha256'], 'verification parent changed')
        report['parent_sha256'] = parent['parent_sha256']
        if report['status'] == 'VERIFIED_UNSAT':
            exported = engine(job, plan, 'export-drat', limits)
            report['events'].append(exported)
            require(not exported.get('timeout') and exported['exit_code'] == 0,
                    'a leaf cover is not closed until export-drat succeeds')
            export_result = exported.get('result') or {}
            require(export_result.get('status') == 'VERIFIED_UNSAT' and
                    export_result.get('parent_sha256') == checked['result']['parent_sha256'],
                    'composed certificate does not match the verified parent or complete case')
            report['export_drat'] = export_result
        if report['status'] == 'VERIFIED_SAT':
            report['case_model'] = check_case_model(job, folder)
        if report['status'] in ('VERIFIED_SAT', 'VERIFIED_UNSAT'):
            from store import capture_checked_outputs
            report['checked_artifact_refs'] = capture_checked_outputs(folder, Path(limits['cohort_root']))
        report['stock_finalise_eligible'] = (job['kind'] == 'wall' and job['variant'] == 'original'
                                               and report['status'] == 'VERIFIED_UNSAT')
    except Exception as exc:
        report['status'] = 'ERROR'
        report['error'] = str(exc)
    if any(event.get('timeout') for event in report['events']):
        report['status'] = 'OPEN_TIMEOUT'
    if 'total conflict budget' in report.get('error', ''):
        report['status'] = 'OPEN_BUDGET_EXHAUSTED'
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (folder / 'unified-result.json').write_bytes(json.dumps(report, indent=2, sort_keys=True).encode() + b'\n')
    return report


def attempt_key(job, plan):
    return sha(json_bytes({'job': job, 'split': plan['split'], 'limits': plan['limits'],
                           'sources': plan['sources']}))[:16]


def run_cohort(args, out):
    require(args.min_free_gb >= 0, '--min-free-gb cannot be negative')
    dimensions(args.depth, args.workers, args.seconds, args.conflicts, args.shards, args.shard)
    out = Path(out).resolve()
    for key in ('check_seconds', 'max_total_conflicts'):
        require(getattr(args, key) >= 1, f'--{key.replace("_", "-")} must be positive')
    require(args.wall_seconds >= 2 * args.seconds + args.check_seconds + 2,
            'wall clock must cover the full search, deferred proof and strict checker')

    def one_attempt(job, plan, root, retry):
        key = attempt_key(job, plan)
        parent = root / f'{key}-retry-{retry}' if retry else root / key
        folder = parent / 'jobs' / job['id']
        record = folder / 'unified-result.json'
        reused = False
        if record.exists():
            old = json.loads(record.read_text())
            require(old.get('job') == job and old.get('attempt_id') == parent.name,
                    'record does not bind exactly this job and attempt')
            # The directory and native leaf receipts are only cache inputs:
            # run_one verifies parent/model/proof artifacts again.
            reused = True
        options = dict(limits, out=str(parent), cohort_root=plan['out'],
                       allocated_conflicts=plan['allocated_conflicts'],
                       allocation_lock=plan['allocation_lock'])
        result = run_one(job, plan, options, retry > 0)
        result['attempt_id'] = parent.name
        result['reused'] = reused
        result['attempt_relative_dir'] = str(parent.relative_to(plan['out']))
        atomic_json(record, result)
        return result

    with cohort_lock(out):
        if (out / 'cohort.json').exists():
            frozen = ('--rows', '--profiles', '--external', '--variants', '--limit',
                      '--depth', '--lookahead', '--seconds', '--conflicts',
                      '--shards', '--shard', '--wall-seconds', '--check-seconds',
                      '--max-total-conflicts')
            if any(flag in sys.argv for flag in frozen):
                raise ValueError('cannot alter selection/tier/budget when resuming; use a new cohort directory')
            plan = read_plan(out)
            limits = {'out': str(out), 'seconds_per_leaf': plan['limits']['seconds_per_leaf'],
                      'conflicts_per_leaf': plan['limits']['conflicts_per_leaf'],
                      'wall_seconds_per_call': plan['limits']['wall_seconds_per_call'],
                      'check_seconds': plan['limits']['check_seconds'],
                      'max_total_conflicts': plan['limits']['max_total_conflicts'],
                      'min_free_bytes': max(args.min_free_gb, plan.get('min_free_gb', 0)) * 1024**3}
        else:
            require(not any(p.name != '.cohort.lock' for p in out.iterdir()),
                    'new cohort output must be empty (or an existing cohort)')
            require(shutil.disk_usage(out).free >= args.min_free_gb * 1024**3,
                    f"disk guard: less than {args.min_free_gb} GB available")
            plan = make_plan(args, out)
            plan['min_free_gb'] = args.min_free_gb
            # Persist the disk floor with the static recipe without overwriting a plan.
            raw = json.loads((out / 'cohort.json').read_text())
            raw['min_free_gb'] = args.min_free_gb
            atomic_json(out / 'cohort.json', raw)
            limits = {'out': str(out), 'seconds_per_leaf': args.seconds,
                      'conflicts_per_leaf': args.conflicts, 'wall_seconds_per_call': args.wall_seconds,
                      'check_seconds': args.check_seconds, 'max_total_conflicts': args.max_total_conflicts,
                      'min_free_bytes': args.min_free_gb * 1024**3}
        if args.dry_run:
            print(json.dumps({'plan_sha256': file_hash(out / 'cohort.json'), 'jobs': plan['jobs'],
                              'split': plan['split'], 'limits': limits,
                              'selected_shard': [args.shard, args.shards],
                              'note': 'no formulas generated and no search launched'}, indent=2))
            return 0
        # allocation_lock protects conservative total-conflict reservations
        # across concurrent per-job preparation/completion, not a cohort claim.
        allocation_lock = threading.Lock()
        allocated = [0]
        plan = dict(plan, limits=limits,
                    min_free_gb=max(args.min_free_gb, plan.get('min_free_gb', 0)),
                    allocated_conflicts=allocated, allocation_lock=allocation_lock, out=out)
        reports = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for job, report in zip(plan['jobs'], pool.map(lambda j: one_attempt(
                    j, plan, out / 'jobs',
                    sum(p.name.startswith(attempt_key(j, plan) + '-retry-')
                        for p in (out / 'jobs').glob('*'))
                    if args.again and (out / 'jobs').exists() else 0), plan['jobs'])):
                reports.append(report); allocated[0] = report.get('_allocated', allocated[0])
                print(json.dumps({'job': report['job']['id'], 'attempt': report['attempt_id'],
                                  'variant': report['job']['variant'], 'status': report['status'],
                                  'reused': report.get('reused', False), 'scope': report['scope'],
                                  'error': report.get('error')}), flush=True)
        from collections import Counter
        counts = Counter(report['status'] for report in reports)
        remaining_open = any(counts[k] for k in ('OPEN', 'OPEN_TIMEOUT', 'OPEN_BUDGET_EXHAUSTED'))
        summary = {'planned': len(plan['jobs']), 'reports': counts,
                   'stock_finalise_eligible': sum(report['stock_finalise_eligible'] for report in reports),
                   'verified_case_models': sum(any(x['kind'] == 'CASE_SAT' for x in report.get('case_model', [])) for report in reports),
                   'allocated_conflicts_ceiling': allocated[0],
                   'limits': limits, 'time_utc': datetime.now(timezone.utc).isoformat(),
                   'status': 'ERROR' if counts['ERROR'] else ('OPEN' if remaining_open else 'COMPLETED'),
                   'scope': 'independent bounded checks; OPEN/TIMEOUT/BUDGET is not SAT/UNSAT; results are not a Ramsey cover'}
        summary['source_warning'] = plan.get('source_warning', [])
        atomic_json(out / 'cohort-summary.json', summary)
        print(json.dumps(summary, indent=2, default=dict, sort_keys=True))
        return 1 if counts['ERROR'] else (2 if remaining_open else 0)


def status(args, out, verify):
    out = Path(out).resolve()
    plan = read_plan(out)
    if verify:
        limits = dict(plan['limits'], out=str(out), min_free_bytes=0)
        reports = []
        with cohort_lock(out):
            for attempt in sorted(out.glob('jobs/*/jobs/*')):
                if not (attempt / 'plan.json').exists():
                    reports.append({'job': 'incomplete-attempt', 'status': 'OPEN', 'scope': 'attempt has no completed parent plan'})
                    continue
                limit_dict = dict(limits, out=str(attempt.parent.parent))
                attempt_id = attempt.parent.name
                job = next((j for j in plan['jobs'] if j['id'] == attempt.name), None)
                if job is None:
                    reports.append({'job': attempt_id, 'status': 'ERROR', 'exit_code': 1,
                                    'scope': 'unknown saved job, not adopted'})
                    continue
                result = engine(job, plan, 'verify', limit_dict)
                export_report = None
                if result['exit_code'] == 0 and (result.get('result') or {}).get('status') == 'VERIFIED_UNSAT':
                    try:
                        export_report = engine(job, plan, 'export-drat', limit_dict)['result']
                        require(export_report and export_report.get('status') == 'VERIFIED_UNSAT' and
                                export_report.get('parent_sha256') == result['result']['parent_sha256'],
                                'no matching composed parent proof')
                    except Exception as exc:
                        result = dict(result, exit_code=1, error=str(exc))
                reports.append({'job': job, 'attempt_id': attempt_id,
                                'export_drat': export_report,
                                'status': (result.get('result') or {}).get('status', 'ERROR'),
                                'exit_code': result['exit_code'], 'scope': scope(job)})
        from collections import Counter
        require(reports, 'cohort has no attempts it can verify; an empty set is not a closed cover')
        counts = Counter(r['status'] for r in reports)
        print(json.dumps({'verification': counts, 'source_warning': plan['source_warning'],
                          'scope': 'replay/model/parent checks, never infer original UNSAT from OPEN'}, indent=2, default=dict))
        return 1 if counts['ERROR'] or any(r.get('exit_code') == 1 for r in reports) else (2 if len(reports) != counts['VERIFIED_UNSAT'] else 0)
    reports = []
    for path in sorted(out.glob('jobs/*/jobs/*/unified-result.json')):
        report = json.loads(path.read_text())
        reports.append(report)
    for job in plan['jobs']:
        if not (out / 'jobs' / attempt_key(job, plan) / 'jobs' / job['id'] / 'unified-result.json').exists():
            if not any(report['job'] == job for report in reports):
                reports.append({'job': job, 'status': 'UNSTARTED'})
    from collections import Counter
    print(json.dumps({'sources': plan['sources'], 'source_warning': plan['source_warning'],
                      'jobs': [{'id': r['job']['id'], 'variant': r['job']['variant'],
                                'status': r['status'], 'scope': r['scope'] if 'scope' in r else scope(job)}
                               for r, job in zip(reports, plan['jobs'])],
                      'counts': Counter(r['status'] for r in reports)}, indent=2, default=dict))
    return 0


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='command', required=True)
    r = commands.add_parser('run', help='plan/resume a bounded variant cohort')
    r.add_argument('--out', type=Path, required=True)
    r.add_argument('--rows', help='comma-separated wall row prefixes or square:INDEX')
    r.add_argument('--profiles', help='comma-separated exact degree profiles (explicit large cohort)')
    r.add_argument('--external', type=Path, action='append', help='external DIMACS; repeat option for files')
    r.add_argument('--variants', default='original,color,square,square-color')
    r.add_argument('--limit', type=int)
    r.add_argument('--depth', type=int, default=1)
    r.add_argument('--lookahead', type=int, default=12)
    r.add_argument('--workers', type=int, default=2)
    r.add_argument('--min-free-gb', type=int, default=10)
    r.add_argument('--seconds', type=int, default=5)
    r.add_argument('--conflicts', type=int, default=1000)
    r.add_argument('--wall-seconds', type=int, default=900)
    r.add_argument('--check-seconds', type=int, default=300)
    r.add_argument('--max-total-conflicts', type=int, default=1000000)
    r.add_argument('--shards', type=int, default=1)
    r.add_argument('--shard', type=int, default=0)
    r.add_argument('--dry-run', action='store_true')
    r.add_argument('--again', action='store_true', help='retry identical leaf budgets deliberately')
    for name in ('status', 'verify'):
        c = commands.add_parser(name)
        c.add_argument('--out', type=Path, required=True)
    return p


def main():
    args = parser().parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.command == 'run':
        return run_cohort(args, out)
    return status(args, out, args.command == 'verify')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'unified: {exc}', file=sys.stderr)
        sys.exit(1)
