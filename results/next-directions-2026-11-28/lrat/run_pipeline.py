#!/usr/bin/env python3
"""run_pipeline -- bounded certificate-pipeline experiment on already CLOSED cases.

Direction 5 (proof workflows, P1) of results/literature-next-2026-11-28: compare
what it costs to end up holding a *checked* refutation certificate of one exact
CNF, by three routes, on formulas that are already refuted:

  A   CaDiCaL 2.1.2 -> DRAT -> drat-trim -c verify            (incumbent)
  A'  the same DRAT -> drat-trim -L elaborate to LRAT -> lrat-trim check+trim
  B   CaDiCaL 2.1.2 --lrat -> lrat-trim check+trim -> replay

with three independent replays of route B's trimmed artifact: lrat-trim backward,
lrat-trim forward (-S), and a second, from-scratch RUP-only checker
(lrat_rup_check.py).  Route A' prices the DRAT elaboration step that native LRAT
is supposed to remove; it is measured, not assumed.

Cases are already-closed inputs only (no OPEN wall parent, no cube campaign):
  H8   a K58 0404 word-search child, query sha e8cc9784..., the case of the
       earlier native-LRAT smoke;
  R11  a certified wall leaf of a different row/profile (15,15,14,13), i.e. a
       genuinely heterogeneous second case;
  H7   a second K58 0404 word-search child (supplementary same-family repeat).

Fail-closed: an input/pin hash mismatch, a solver exit other than 20, a checker
without its exact success line, a non-identical search trajectory between the
two solver arms, or any negative control that is *not* rejected aborts the run.
A timeout/UNKNOWN is never recorded as UNSAT.  Nothing outside this member
directory is written.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # results/next-directions-2026-11-28/lrat
REPO = HERE.parents[2]                          # repository root

CADICAL = REPO / "tools/color-resolved-wallcc/bin/cadical-2.1.2"
DRATTRIM = REPO / "tools/color-resolved-wallcc/bin/drat-trim"
LRATTRIM = HERE / ".scratch/tools/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim"
LRATTRIM = Path(os.environ.get("LRAT_TRIM", str(LRATTRIM)))
LRATTRIM_SRC = LRATTRIM.parent
PYCHECK = HERE / "lrat_rup_check.py"
TIME = "/usr/bin/time"

PIN_CADICAL = "a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b"
SOLVER_ARGS = {"seed": 0, "conflicts": 50000, "wall": 20}

CASES = {
    "H8": {
        "cnf": REPO / ".scratch/k58-0404-word-search/H8-word0.cnf",
        "query_sha256": "e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229",
        "retained_drat": REPO / ".scratch/k58-0404-word-search/H8-word0.drat",
        "expect_drat_sha256": "55a3963489aad6bab8f2c3069f29045a94d88768f2529c242506f7f23c678eb2",
        "expect_lrat_sha256": "05f0d7f11d28e0a784cab3a1a737960fdc8bc5414cc246242d743bb668bd7b34",
        "wrong_cnf": REPO / ".scratch/k58-0404-word-search/H7-word0.cnf",   # same 19425/184188 shape
        "describe": "K58 0404 word-search child H=8, word 0",
    },
    "N14": {
        "cnf": REPO / "results/cc-reciprocal-0404-2026-11-25/continuation/nodes/n014.cnf",
        "query_sha256": "92be6247f37ba4d7da27df7195f03ad7cfc204d9dca0914009500e48af39e679",
        "retained_drat": REPO / "results/cc-reciprocal-0404-2026-11-25/continuation/nodes/n014.drat",
        "expect_drat_sha256": "b490208c0fda75ea03071c4244c93831df5ab44b7b991c978aaa792618b83098",
        "expect_lrat_sha256": "ec62dbf1b040f362689d8c2f77d4745f9df605086e15722eaeebcc2841833c31",
        "wrong_cnf": REPO / "results/cc-reciprocal-0404-2026-11-25/continuation/nodes/n018.cnf",
        "describe": "reciprocal-0404 continuation leaf n014, 305513 vars / 834106 clauses",
    },
    "R11": {
        "cnf": REPO / "results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/leaf.cnf",
        "query_sha256": "b3a5bded030682e02472bc1f95147efaade87c01ab88772a98967194b3e48f41",
        "retained_drat": REPO / "results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/joined.drat",
        "expect_drat_sha256": "1e605f06553a1152d358bccf16f49dcb7a4102da7ccb9d3adade9a2f662d3007",
        "expect_lrat_sha256": "5280cc4c972f33b3861ce798ae710388a0e22e49fdeb5f934c657132eebb134e",
        "wrong_cnf": REPO / "results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/original-parent.cnf",
        "describe": "certified wall leaf, profile (15,15,14,13), cube [4262,4645]",
    },
    "H7": {
        "cnf": REPO / ".scratch/k58-0404-word-search/H7-word0.cnf",
        "query_sha256": "2286ae68e1419cdbc751e1804ec9ca79b05874b759b75ed9c6cd3ebe1a31225f",
        "retained_drat": REPO / ".scratch/k58-0404-word-search/H7-word0.drat",
        "expect_drat_sha256": "1831a7b7ddaeaf822f87b13621e9275739cbfb4fd4c3b9e95e4b78a9fb6b854e",
        "expect_lrat_sha256": "1575f8bff14b2c14752735bb23e264d5ecd2463b5f8e43d5caa607396b1ff8e5",
        "wrong_cnf": REPO / ".scratch/k58-0404-word-search/H8-word0.cnf",
        "describe": "K58 0404 word-search child H=7, word 0",
    },
}


class Fail(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run_timed(cmd, tag: str, outdir: Path):
    """Run cmd under /usr/bin/time -v; return a receipt dict."""
    outdir.mkdir(parents=True, exist_ok=True)
    tfile, log, err = outdir / f"{tag}.time", outdir / f"{tag}.log", outdir / f"{tag}.err"
    with open(log, "wb") as lo, open(err, "wb") as le:
        r = subprocess.run([TIME, "-v", "-o", str(tfile), "--", *map(str, cmd)],
                           stdout=lo, stderr=le)
    rec = {"cmd": [str(c) for c in cmd], "rc": r.returncode, "log": str(log), "stderr": str(err)}
    txt = tfile.read_text() if tfile.exists() else ""
    for key, pat in (("cpu_user_s", "User time (seconds):"),
                     ("cpu_sys_s", "System time (seconds):"),
                     ("wall_s", "Elapsed (wall clock) time"),
                     ("maxrss_kb", "Maximum resident set size (kbytes):")):
        for line in txt.splitlines():
            if line.strip().startswith(pat):
                val = line.rsplit(":", 1)[1].strip()
                if key == "wall_s":
                    val = sum(float(p) * 60 ** i for i, p in enumerate(reversed(val.split(":"))))
                rec[key] = float(val)
                break
    rec["cpu_s"] = round(rec.get("cpu_user_s", 0.0) + rec.get("cpu_sys_s", 0.0), 3)
    return rec


def text_of(rec) -> str:
    return Path(rec["log"]).read_text(errors="replace")


def verified(rec, needle="s VERIFIED", rc=20) -> bool:
    return rec["rc"] == rc and needle in text_of(rec)


def require(cond, msg):
    if not cond:
        raise Fail(msg)


def solver_stats(rec) -> dict:
    out = {}
    for line in text_of(rec).splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "c" and f[1].rstrip(":") in (
                "conflicts", "decisions", "propagations", "restarts"):
            try:
                out[f[1].rstrip(":")] = int(f[2])
            except ValueError:
                pass
    return out


def solve(case, cnf: Path, proof: Path, work: Path, tag: str, lrat: bool):
    args = [CADICAL, "--seed=%d" % SOLVER_ARGS["seed"]]
    args += ["--lrat", "--binary=true"] if lrat else ["--binary=true"]
    args += ["-c", SOLVER_ARGS["conflicts"], "-t", SOLVER_ARGS["wall"], cnf, proof]
    rec = run_timed(args, tag, work)
    require(rec["rc"] == 20, f"{case}: solver exit {rec['rc']} is not a refutation "
                             f"(10=SAT/0=UNKNOWN are not UNSAT)")
    rec.update(bytes=proof.stat().st_size, sha256=sha256(proof), stats=solver_stats(rec),
               log_tail="\n".join(text_of(rec).splitlines()[-3:]))
    return rec


def elaborate(case, cnf: Path, drat: Path, out: Path, work: Path, tag: str):
    """drat-trim -L: turn a DRAT proof into an LRAT proof a second checker can replay."""
    rec = run_timed([DRATTRIM, cnf, drat, "-L", out], tag, work)
    require(rec["rc"] == 0 and "s VERIFIED" in text_of(rec),
            f"{case}: drat-trim -L elaboration failed (rc={rec['rc']})")
    rec.update(bytes=out.stat().st_size, sha256=sha256(out))
    return rec


def lrat_trim(case, cnf: Path, proof: Path, trimmed: Path, work: Path, tag: str,
              replay_tags=("replay",)):
    """lrat-trim check+trim, then independent replays of the trimmed artifact."""
    t = run_timed([LRATTRIM, cnf, proof, trimmed], tag, work)
    require(verified(t), f"{case}/{tag}: lrat-trim did not verify (rc={t['rc']})")
    out = {"trim": t, "trimmed_bytes": trimmed.stat().st_size, "trimmed_sha256": sha256(trimmed),
           "replays": {}}
    for name in replay_tags:
        if name == "replay":
            r = run_timed([LRATTRIM, cnf, trimmed], f"{tag}-replay", work)
        elif name == "forward":
            r = run_timed([LRATTRIM, "-S", cnf, trimmed], f"{tag}-replay-forward", work)
        elif name == "rup":
            r = run_timed([LRATTRIM, "--rup", cnf, proof], f"{tag}-rup-only", work)
        else:
            raise Fail("unknown replay " + name)
        require(verified(r), f"{case}/{tag}: replay '{name}' failed (rc={r['rc']})")
        out["replays"][name] = r
    return out


def ascii_encode(case, cnf: Path, proof: Path, out: Path, work: Path, tag: str):
    rec = run_timed([LRATTRIM, "-a", cnf, proof, out], tag, work)
    require(verified(rec), f"{case}/{tag}: ASCII re-encode failed (rc={rec['rc']})")
    rec.update(bytes=out.stat().st_size, sha256=sha256(out))
    return rec


def second_checker(case, cnf: Path, ascii_proof: Path, work: Path, tag: str):
    rec = run_timed([sys.executable, PYCHECK, cnf, ascii_proof], tag, work)
    require(verified(rec, needle="s VERIFIED (independent RUP-only replay)"),
            f"{case}/{tag}: the second checker rejected the proof (rc={rec['rc']})")
    return rec


def checker_selftest():
    """The pinned checker must pass its own accept and reject suites before use."""
    res = {}
    for script in ("parse", "regr", "trim", "fail", "check", "usage"):
        runner = LRATTRIM_SRC / "test" / script / "run.sh"
        if not runner.exists():
            continue
        r = subprocess.run(["sh", str(runner)], cwd=LRATTRIM_SRC, capture_output=True, text=True)
        summaries = [l for l in r.stdout.splitlines() if l.startswith("passed")]
        res[script] = {"rc": r.returncode, "summary": summaries[-1] if summaries else ""}
        require(r.returncode == 0, f"lrat-trim selftest suite '{script}' failed")
    return res


def ascii_structure(path: Path):
    """Count what the trimmed LRAT actually consists of.

    A trimmed LRAT begins by deleting every input clause outside the core, so its size
    is (core derivation) + (one id per dropped input clause).  Measuring the split
    keeps the retained-byte comparison honest on formulas with huge, empty cores.
    """
    adds = dels = del_ids = hints = 0
    for line in path.open(errors="replace"):
        t = line.split()
        if not t:
            continue
        if len(t) > 1 and t[1] == "d":
            dels += 1
            del_ids += len(t) - 2
            continue
        adds += 1
        try:
            z = t.index("0", 1)
        except ValueError:
            continue
        hs = t[z + 1:]
        hints += max(0, len(hs) - (1 if hs and hs[-1] == "0" else 0))
    return {"addition_lines": adds, "deletion_lines": dels, "deletion_ids": del_ids,
            "hint_steps": hints, "ascii_bytes": path.stat().st_size}


def check_plain(case, cnf: Path, proof: Path, work: Path, tag: str):
    """Strict lrat-trim check of a proof, no trimming, no output file."""
    rec = run_timed([LRATTRIM, cnf, proof], tag, work)
    require(verified(rec), f"{case}/{tag}: lrat-trim did not verify (rc={rec['rc']})")
    return rec


def relax_replay(case, cnf: Path, proof: Path, work: Path, tag: str):
    """Replay with --relax: documented as 'ignore deletion of clauses which were never
    added'.  This is a relaxation of the deletion discipline, so the result is flagged
    and never reported as an unqualified success."""
    rec = run_timed([LRATTRIM, "--relax", cnf, proof], tag, work)
    require(verified(rec), f"{case}/{tag}: --relax replay failed (rc={rec['rc']})")
    rec["relaxed"] = True
    return rec


def elaboration_route(case, cnf: Path, drat: Path, work: Path, tag: str):
    """DRAT -> drat-trim -L LRAT -> strict check; then the trimmed variant.

    drat-trim -L emits an LRAT proof whose deletions may mention clauses that a later
    trim removes.  The untrimmed elaborated proof replays strictly; the trimmed one
    does not, and is only replayable with --relax.  Both outcomes are recorded, and
    the strict branch is the one summarised as this route's certificate.
    """
    el = elaborate(case, cnf, drat, work / f"{tag}-elab.lrat", work, f"{tag}-elaborate")
    strict = check_plain(case, cnf, work / f"{tag}-elab.lrat", work, f"{tag}-elab-strict")
    trimmed = work / f"{tag}-elab-trimmed.lrat"
    t = run_timed([LRATTRIM, cnf, work / f"{tag}-elab.lrat", trimmed], f"{tag}-elab-trim", work)
    require(verified(t), f"{case}/{tag}: lrat-trim did not verify the elaborated proof")
    strict_replay = run_timed([LRATTRIM, cnf, trimmed], f"{tag}-elab-trim-replay", work)
    strict_ok = verified(strict_replay)
    relax = relax_replay(case, cnf, trimmed, work, f"{tag}-elab-trim-replay-relax")
    return {
        "elaborate": el,
        "strict_check": strict,
        "strict_chain_cpu_s": round(el["cpu_s"] + strict["cpu_s"], 3),
        "retained_bytes": el["bytes"],
        "trim": t,
        "trimmed_bytes": trimmed.stat().st_size,
        "trimmed_sha256": sha256(trimmed),
        "trimmed_strict_replay_ok": strict_ok,
        "trimmed_strict_replay": strict_replay,
        "trimmed_strict_replay_error": next(
            (l.strip() for l in Path(strict_replay["stderr"]).read_text(errors="replace").splitlines()
             if "error" in l.lower()), "none"),
        "trimmed_relaxed_replay": relax,
        "trimmed_variant_chain_cpu_s": round(el["cpu_s"] + t["cpu_s"] + relax["cpu_s"], 3),
        "trimmed_variant_retained_bytes": trimmed.stat().st_size,
    }


def controls(case, cnf: Path, work: Path, ascii_proof: Path, other_cnf: Path):
    """Every negative control must be rejected; otherwise the run is invalid."""
    orig, trimmed, drat = work / "b.lrat", work / "b-trimmed.lrat", work / "a.drat"
    out = {}

    def reject(tag, cmd):
        rec = run_timed(cmd, f"ctl-{tag}", work)
        text = text_of(rec)
        ok = rec["rc"] != 20 and "s VERIFIED" not in text
        reason = next((l.strip() for l in text.splitlines()
                       if "error" in l.lower() or "does not" in l.lower()
                       or "REJECTED" in l or "no empty clause" in l.lower()), "")[:220]
        out[tag] = {"cmd": rec["cmd"], "rc": rec["rc"], "rejected": ok,
                    "cpu_s": rec["cpu_s"], "reason": reason}
        require(ok, f"{case}: negative control '{tag}' was NOT rejected (rc={rec['rc']})")

    reject("drat_is_not_lrat", [LRATTRIM, cnf, drat])
    reject("wrong_cnf_same_shape_lrattrim", [LRATTRIM, other_cnf, orig])
    reject("wrong_cnf_same_shape_pycheck", [sys.executable, PYCHECK, other_cnf, ascii_proof])

    data = trimmed.read_bytes()
    trunc = work / "b-trimmed-truncated.lrat"
    trunc.write_bytes(data[: int(len(data) * 0.9)])
    reject("truncated_trimmed", [LRATTRIM, cnf, trunc])

    lines = ascii_proof.read_text().splitlines(keepends=True)

    def is_addition(t):
        return len(t) > 2 and t[1] != "d"

    idx = None
    for i in range(len(lines) - 1, -1, -1):
        t = lines[i].split()
        if is_addition(t) and t[1] == "0":
            idx = i
            break
    require(idx is not None, f"{case}: no empty-clause line found for the control")
    noempty = work / "b-trimmed-noempty.lrat"
    noempty.write_text("".join(lines[:idx] + lines[idx + 1:]))
    reject("missing_empty_clause", [LRATTRIM, cnf, noempty])
    reject("missing_empty_clause_pycheck", [sys.executable, PYCHECK, cnf, noempty])

    target = next(i for i, l in enumerate(lines)
                  if is_addition(l.split()) and l.split()[1] != "0" and len(l.split()) > 4)
    toks = lines[target].split()
    zpos = toks.index("0")
    old = int(toks[zpos + 1])
    new = 1 if old != 1 else 2
    toks[zpos + 1] = str(new)
    lines2 = list(lines)
    lines2[target] = " ".join(toks) + "\n"
    mutated = work / "b-trimmed-mutated-hint.lrat"
    mutated.write_text("".join(lines2))
    reject("altered_antecedent_id", [LRATTRIM, cnf, mutated])
    reject("altered_antecedent_id_pycheck", [sys.executable, PYCHECK, cnf, mutated])
    out["altered_antecedent_detail"] = {"line": target + 1, "old_hint": old, "new_hint": new}

    # A refutation is a derivation: only clauses that occur in a hint chain matter.
    # So mutate (i) a clause the proof actually uses -> must be rejected, and
    # (ii) a clause it never uses -> expected to verify, which documents that the
    # check is about the derivation rather than about the whole input file.
    nclauses = int(cnf.read_text().splitlines()[0].split()[3])
    used, unused_candidate = set(), None
    for l in lines:
        t = l.split()
        if not is_addition(t):
            continue
        z = t.index("0", 1)
        for h in t[z + 1:]:
            h = int(h)
            if h == 0:
                break
            if 1 <= h <= nclauses:
                used.add(h)
    require(used, f"{case}: no original clause is used by the proof; control is vacuous")
    used_id = min(used)

    ctext = cnf.read_text().splitlines()
    clause_lines = [i for i, l in enumerate(ctext)
                    if l.split() and l.split()[0] not in ("p", "c") and l.rstrip().endswith("0")]
    require(len(clause_lines) == nclauses,
            f"{case}: CNF clause-line count {len(clause_lines)} != header {nclauses}")

    def mutate(clause_id, out_name):
        line = ctext[clause_lines[clause_id - 1]].split()
        for k, tok in enumerate(line):
            if tok not in ("0",):
                line[k] = str(-int(tok))
                break
        mut_lines = list(ctext)
        mut_lines[clause_lines[clause_id - 1]] = " ".join(line)
        dest = work / out_name
        dest.write_text("\n".join(mut_lines) + "\n")
        return dest

    badcnf = mutate(used_id, "input-mutated-used.cnf")
    reject("mutated_used_cnf_literal", [LRATTRIM, badcnf, trimmed])
    reject("mutated_used_cnf_literal_pycheck", [sys.executable, PYCHECK, badcnf, ascii_proof])
    out["mutated_used_clause"] = {"clause_id": used_id,
                                  "clauses_used_by_proof": len(used),
                                  "of_clauses": nclauses}
    for cand in range(1, nclauses + 1):
        if cand not in used:
            unused_candidate = cand
            break
    if unused_candidate is not None:
        okcnf = mutate(unused_candidate, "input-mutated-unused.cnf")
        spare = run_timed([LRATTRIM, okcnf, trimmed], "ctl-mutated-unused-literal", work)
        out["mutated_unused_clause"] = {
            "clause_id": unused_candidate, "still_verifies": verified(spare),
            "expected": "verifies: the clause is outside the derivation core",
            "cpu_s": spare["cpu_s"]}
        require(verified(spare), f"{case}: an unused-clause mutation broke the proof, "
                                f"unexpected and worth explaining")

    satcnf = work / "sat.cnf"
    satcnf.write_text("p cnf 3 3\n1 2 0\n-1 2 0\n3 -2 0\n")   # satisfied by x2 = x3 = 1
    reject("satisfiable_formula", [LRATTRIM, satcnf, trimmed])
    reject("satisfiable_formula_pycheck", [sys.executable, PYCHECK, satcnf, ascii_proof])

    pos = run_timed([LRATTRIM, cnf, ascii_proof], "ctl-ascii-positive", work)
    require(verified(pos), f"{case}: the unmodified ASCII proof did not verify")
    out["ascii_positive"] = {"rc": pos["rc"], "cpu_s": pos["cpu_s"], "verified": True}
    return out


def cleanup(work: Path, keep=("input.cnf", "b-trimmed.lrat")):
    """Keep receipts and the small deliverables; delete multi-MB intermediates."""
    for p in work.iterdir():
        if p.is_file() and p.name not in keep and p.stat().st_size > 4 << 20:
            p.unlink()


BUILD_HINT = (
    "the pinned checker is missing; rebuild it from reviewed source with:\n"
    "  curl -sSL https://codeload.github.com/arminbiere/lrat-trim/tar.gz/"
    "423194927df747528d5b7364806b5b77b2660c12 -o lrat-trim.tar.gz\n"
    "  tar xzf lrat-trim.tar.gz && cd lrat-trim-423194927df747528d5b7364806b5b77b2660c12\n"
    "  ./configure && make   # -> lrat-trim, sha256 f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895"
)


def require_tools():
    missing = [str(p) for p in (CADICAL, DRATTRIM, LRATTRIM, PYCHECK) if not p.exists()]
    if missing:
        raise Fail("missing pinned tools:\n  " + "\n  ".join(missing) + "\n" + BUILD_HINT)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="H8,N14,R11,H7")
    ap.add_argument("--out", default=str(HERE / "pipeline-receipt.json"))
    a = ap.parse_args(argv)

    require_tools()
    receipt = {
        "scope": ("certificate-pipeline comparison on already closed inputs only; "
                  "no wall search, no OPEN parent, no bound change"),
        "pins": {
            "cadical": {"path": str(CADICAL.relative_to(REPO)), "sha256": sha256(CADICAL),
                        "version": "2.1.2"},
            "drat_trim": {"path": str(DRATTRIM.relative_to(REPO)), "sha256": sha256(DRATTRIM)},
            "lrat_trim": {"path": str(LRATTRIM), "sha256": sha256(LRATTRIM),
                          "source_commit": "423194927df747528d5b7364806b5b77b2660c12",
                          "source_url": "https://codeload.github.com/arminbiere/lrat-trim/tar.gz/"
                                        "423194927df747528d5b7364806b5b77b2660c12",
                          "source_tarball_sha256":
                              "e71af67672133ed0c6a0885fc2b1959682430fdd5fa8456ea692505d18f6cdd3",
                          "version": "0.2.1-rc3", "build": "gcc -Wall -O3 -DNDEBUG",
                          "build_cmd": "./configure && make (from the tarball above)"},
            "toolchain": {"gcc": subprocess.run(["gcc", "--version"], capture_output=True,
                                                text=True).stdout.splitlines()[0],
                          "python": sys.version.split()[0]},
            "second_checker": {"path": str(PYCHECK.relative_to(REPO)), "sha256": sha256(PYCHECK),
                               "semantics": "RUP-only LRAT, from scratch, unverified code",
                               "role": "second independent implementation, not a trusted checker"},
            "solver_args": SOLVER_ARGS,
        },
        "checker_selftest": checker_selftest(),
        "cases": {},
    }
    require(receipt["pins"]["cadical"]["sha256"] == PIN_CADICAL,
            "CaDiCaL binary hash differs from the pinned hash")

    scratch = HERE / ".scratch/runs"
    for name in [c for c in a.only.split(",") if c]:
        spec = CASES[name]
        work = scratch / name
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        cnf = work / "input.cnf"
        shutil.copyfile(spec["cnf"], cnf)
        got = sha256(cnf)
        if spec["query_sha256"] is None:
            spec["query_sha256"] = got   # first run records it; later runs assert it
        require(got == spec["query_sha256"], f"{name}: input CNF hash mismatch ({got})")
        rec = {"describe": spec["describe"], "source": str(spec["cnf"].relative_to(REPO)),
               "input": {"sha256": got, "expected_sha256": spec["query_sha256"], "match": True,
                         "bytes": cnf.stat().st_size,
                         "header": cnf.read_text().splitlines()[0]}}

        # route A: DRAT + verify, then the DRAT elaboration route A'
        A = solve(name, cnf, work / "a.drat", work, "a-solve", lrat=False)
        if spec["expect_drat_sha256"]:
            require(A["sha256"] == spec["expect_drat_sha256"],
                    f"{name}: regenerated DRAT hash differs from the recorded receipt")
        av = run_timed([DRATTRIM, cnf, work / "a.drat", "-c"], "a-verify", work)
        require(av["rc"] == 0 and "s VERIFIED" in text_of(av),
                f"{name}: drat-trim -c did not verify the fresh DRAT (rc={av['rc']})")
        A["verify"] = av
        A["total_cpu_s"] = round(A["cpu_s"] + av["cpu_s"], 3)
        A["elaboration"] = elaboration_route(name, cnf, work / "a.drat", work, "a")
        A["elaboration"]["total_cpu_s"] = round(
            A["cpu_s"] + A["elaboration"]["strict_chain_cpu_s"], 3)
        A["elaboration"]["trimmed_variant_cpu_s"] = round(
            A["cpu_s"] + A["elaboration"]["trimmed_variant_chain_cpu_s"], 3)

        # route B: native LRAT + trim + three independent replays
        B = solve(name, cnf, work / "b.lrat", work, "b-solve", lrat=True)
        if spec["expect_lrat_sha256"]:
            require(B["sha256"] == spec["expect_lrat_sha256"],
                    f"{name}: regenerated LRAT hash differs from the recorded receipt")
        B["check"] = lrat_trim(name, cnf, work / "b.lrat", work / "b-trimmed.lrat", work,
                               "b-trim", replay_tags=("replay", "forward", "rup"))
        B["ascii"] = ascii_encode(name, cnf, work / "b-trimmed.lrat",
                                  work / "b-trimmed.ascii.lrat", work, "b-ascii")
        B["ascii_structure"] = ascii_structure(work / "b-trimmed.ascii.lrat")
        B["second_checker"] = second_checker(name, cnf, work / "b-trimmed.ascii.lrat",
                                             work, "b-pycheck")
        B["retained_bytes"] = B["check"]["trimmed_bytes"]
        B["trim_ratio"] = round(B["retained_bytes"] / B["bytes"], 4)
        B["total_cpu_s"] = round(B["cpu_s"] + B["check"]["trim"]["cpu_s"]
                                 + B["check"]["replays"]["replay"]["cpu_s"], 3)
        B["total_cpu_s_with_second_checker"] = round(B["total_cpu_s"]
                                                     + B["second_checker"]["cpu_s"], 3)
        require(A["stats"] == B["stats"],
                f"{name}: the DRAT and LRAT arms did not run the same search trajectory")

        # route C: replay the artifact that is already retained on disk
        C = None
        if spec["retained_drat"] and spec["retained_drat"].exists():
            rp = work / "retained.drat"
            shutil.copyfile(spec["retained_drat"], rp)
            rh = sha256(rp)
            rc_rec = run_timed([DRATTRIM, cnf, rp, "-c"], "c-verify-retained", work)
            require(rc_rec["rc"] == 0 and "s VERIFIED" in text_of(rc_rec),
                    f"{name}: the retained DRAT did not verify (rc={rc_rec['rc']})")
            C = {"retained_drat": {"sha256": rh, "bytes": rp.stat().st_size},
                 "verify": rc_rec,
                 "elaboration": elaboration_route(name, cnf, rp, work, "c"),
                 "fresh_drat_matches_retained": rh == A["sha256"]}

        rec.update({"armA_drat": A, "armB_native_lrat": B, "armC_retained": C,
                    "controls": controls(name, cnf, work, work / "b-trimmed.ascii.lrat",
                                         spec["wrong_cnf"])})
        rec["comparison"] = {
            "counters": A["stats"],
            "A_total_cpu_s": A["total_cpu_s"], "A_retained_bytes": A["bytes"],
            "A_elab_total_cpu_s": A["elaboration"]["total_cpu_s"],
            "A_elab_retained_bytes": A["elaboration"]["retained_bytes"],
            "A_elab_trimmed_variant_cpu_s": A["elaboration"]["trimmed_variant_cpu_s"],
            "A_elab_trimmed_variant_bytes": A["elaboration"]["trimmed_variant_retained_bytes"],
            "A_elab_trimmed_variant_needs_relax": not A["elaboration"]["trimmed_strict_replay_ok"],
            "B_total_cpu_s": B["total_cpu_s"], "B_retained_bytes": B["retained_bytes"],
            "B_trimmed_structure": B["ascii_structure"],
            "B_total_cpu_s_with_second_checker": B["total_cpu_s_with_second_checker"],
            "retained_ratio_B_over_A": round(B["retained_bytes"] / A["bytes"], 4),
            "cpu_ratio_B_over_A": round(B["total_cpu_s"] / A["total_cpu_s"], 4),
            "cpu_ratio_B_over_A_elab": round(B["total_cpu_s"] / A["elaboration"]["total_cpu_s"], 4),
        }
        receipt["cases"][name] = rec
        c = rec["comparison"]
        print(f"[{name}] A {c['A_total_cpu_s']:.2f}s/{c['A_retained_bytes']}B  "
              f"A' {c['A_elab_total_cpu_s']:.2f}s/{c['A_elab_retained_bytes']}B  "
              f"B {c['B_total_cpu_s']:.2f}s/{c['B_retained_bytes']}B "
              f"(+2nd checker {c['B_total_cpu_s_with_second_checker']:.2f}s)  controls ok")
        cleanup(work)

    Path(a.out).write_text(json.dumps(receipt, indent=2, sort_keys=True))
    print("receipt:", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
