#!/usr/bin/env python3
"""Fresh sequential completed-run CaDiCaL 2.1.2 panel, without proof logging."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

REPO = Path(__file__).resolve().parents[3]
SOLVER = Path("/opt/lean/bin/cadical")
NAMES = ["stock", "armcaps", "degree-own-km", "direct", "extended"]
OUT = REPO / "research/k58-arm-cap-clauses/work/rank1300-cadical212-noproof-panel.json"
LOGDIR = REPO / "research/k58-arm-cap-clauses/work/cadical212-noproof-logs"
LOGDIR.mkdir(exist_ok=True)
results = []
for name in NAMES:
    cnf = REPO / f".scratch/arm-cap-research/rank1300-{name}.cnf"
    log = LOGDIR / f"{name}.log"
    command = [str(SOLVER), "--stats", "--seed=0", "-t", "300", str(cnf)]
    start = time.monotonic()
    with log.open("wb") as stream:
        with subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT) as child:
            _, status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
    text = log.read_text(errors="replace")
    def metric(key):
        match = re.search(rf"^c {re.escape(key)}:\s+(\d+)", text, re.MULTILINE)
        if not match:
            raise ValueError(f"missing {key} in {log}")
        return int(match.group(1))
    record = dict(
        policy=name, input=str(cnf.relative_to(REPO)),
        input_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
        command=command, exit_code=child.returncode,
        status={20: "UNSAT", 10: "SAT", 0: "OPEN"}.get(child.returncode, "ERROR"),
        wall_seconds=time.monotonic() - start,
        user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
        peak_rss_kib=usage.ru_maxrss, proof_logging=False,
        conflicts=metric("conflicts"), decisions=metric("decisions"),
        propagations=metric("propagations"), restarts=metric("restarts"),
        log=str(log.relative_to(REPO)))
    results.append(record)
    print(json.dumps(record, sort_keys=True), flush=True)
    temporary = OUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    temporary.replace(OUT)
