#!/usr/bin/env python3
"""Strict proxy for untrusted package calls to drat-trim.
Remove any -w, preserve the real checker output, fail on a warning or any
exact-status/exit-code mismatch. Record query/proof hashes for each invocation.
"""
from pathlib import Path
import fcntl, hashlib, json, os, subprocess, sys, time

ROOT = Path(os.environ['AUDIT_ROOT']).resolve()
REAL = os.environ['AUDIT_REAL_DRAT_TRIM']
ARGS = [a for a in sys.argv[1:] if a != '-w']
if '-t' not in ARGS:
    ARGS += ['-t', '300']
qhash = None
for i, arg in enumerate(ARGS[:-1]):
    candidate = Path(arg)
    if i == 0 and candidate.is_file():
        qhash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        break
proof_hash = None
if len(ARGS) > 1 and Path(ARGS[1]).is_file():
    proof_hash = hashlib.sha256(Path(ARGS[1]).read_bytes()).hexdigest()
started = time.perf_counter()
try:
    result = subprocess.run([REAL, *ARGS], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
    output = result.stdout
    rc = result.returncode
except subprocess.TimeoutExpired as exc:
    output = (exc.stdout or b'') + (exc.stderr or b'') + b'\nc AUDIT PROXY TIMEOUT\n'
    rc = None
accepted = rc == 0 and [line for line in output.splitlines() if line.startswith(b's ')] == [b's VERIFIED'] and b'WARNING' not in output.upper()
receipt = {'argv': ARGS, 'seconds': time.perf_counter()-started, 'accepted': bool(accepted), 'exit': rc,
           'output_sha256': hashlib.sha256(output).hexdigest(), 'query_sha256': qhash, 'proof_sha256': proof_hash,
           'flags_have_warning_suppression_removed': True}
seq = f'{os.getpid()}-{time.time_ns()}'
(ROOT/'strict-logs'/f'{seq}.out').write_bytes(output)
(ROOT/'strict-logs'/f'{seq}.json').write_text(json.dumps(receipt, indent=2)+'\n')
with (ROOT/'strict-receipts.jsonl').open('a') as stream:
    fcntl.flock(stream, fcntl.LOCK_EX)
    stream.write(json.dumps(receipt, sort_keys=True)+'\n')
sys.stdout.buffer.write(output)
sys.exit(0 if accepted else 2)
