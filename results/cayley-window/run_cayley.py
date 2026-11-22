"""Driver: decide one Cayley k-colouring instance, with a certificate.

usage:  python3 run_cayley.py <outdir> <n> <groupname> <k> [--profile]

SAT  -> writes <outdir>/<tag>.model.json and re-checks the colouring exhaustively
        on all C(n,3) triangles (a checker that never sees the encoder's clauses).
UNSAT-> writes <outdir>/<tag>.drat and replays it with drat-trim on the CNF.
"""
import json
import os
import subprocess
import sys

import gy

KISSAT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat"
DRAT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/drat-trim"


def pick_groups(n, wanted=None):
    gs, complete = gy.groups_of_order(n)
    if wanted:
        gs = [g for g in gs if g.name == wanted]
        if not gs:
            raise SystemExit(f"no group named {wanted}; have "
                             f"{[g.name for g in gy.groups_of_order(n)[0]]}")
    return gs, complete


def decide(g, k, outdir, tag, timeout=600, profile=None):
    text, meta = gy.cnf(g, k, profile)
    cnf_path = os.path.join(outdir, tag + ".cnf")
    with open(cnf_path, "w") as fh:
        fh.write(text)
    proof = os.path.join(outdir, tag + ".drat")
    log = os.path.join(outdir, tag + ".kissat.log")
    with open(log, "w") as lf:
        r = subprocess.run([KISSAT, "-q", cnf_path, proof], stdout=lf,
                           stderr=subprocess.STDOUT, timeout=timeout)
    status = None
    with open(log) as lf:
        for line in lf:
            if line.startswith("s "):
                status = line.split()[1]
    res = dict(tag=tag, group=g.name, n=g.n, k=k, status=status, profile=profile,
               cnf=os.path.basename(cnf_path), n_classes=meta["n_classes"],
               n_triples=meta["n_triples"], n_clauses=meta["n_clauses"],
               n_vars=meta["n_classes"] * k)
    if status == "SATISFIABLE":
        trueset = set()
        with open(log) as lf:
            for line in lf:
                if line.startswith("v "):
                    for tok in line.split()[1:]:
                        v = int(tok)
                        if v > 0:
                            trueset.add(v)
        colour = gy.model_to_colour(g, k, trueset)
        ok, ntri, bad = gy.check_colouring(g, colour, k)
        # extra: is the colouring good?  (exhaustive, independent of the CNF)
        res.update(verified=ok, checked_triangles=ntri, violation=str(bad))
        res["colour_sizes"] = [sum(len(gy.inverse_classes(g)[0][i])
                                    for i in range(meta["n_classes"]) if colour[i] == c)
                               for c in range(k)]
        with open(os.path.join(outdir, tag + ".model.json"), "w") as fh:
            json.dump({"group": g.name, "n": g.n, "k": k,
                       "classes": gy.inverse_classes(g)[0],
                       "colour_of_class": {str(i): colour[i] for i in colour},
                       "verified": ok}, fh, indent=1)
        if os.path.exists(proof):
            os.remove(proof)
    elif status == "UNSATISFIABLE":
        vl = os.path.join(outdir, tag + ".verify.log")
        with open(vl, "w") as vf:
            r = subprocess.run([DRAT, cnf_path, proof], stdout=vf,
                               stderr=subprocess.STDOUT, timeout=timeout)
        with open(vl) as vf:
            vtext = vf.read()
        res["drat_replayed"] = "VERIFIED" in vtext
        res["drat_bytes"] = os.path.getsize(proof) if os.path.exists(proof) else 0
    return res


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    outdir = sys.argv[1]
    n = int(sys.argv[2])
    gname = sys.argv[3] if sys.argv[3] != "-" else None
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    profile = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
    os.makedirs(outdir, exist_ok=True)
    gs, complete = pick_groups(n, gname)
    print(f"# order {n}: {len(gs)} group(s) {[g.name for g in gs]}, "
          f"family complete = {complete}")
    for g in gs:
        tag = f"{g.name}_{g.n}_k{k}" + ("_prof" if profile else "")
        res = decide(g, k, outdir, tag, profile=profile)
        print(json.dumps(res))


if __name__ == "__main__":
    main()
