#!/usr/bin/env python3
"""Run the independent branch checker on witness files."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Template, Witness, check_witness, report

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))


def resolve(p, witdir):
    if os.path.isabs(p):
        return p
    for base in (witdir, REPO, os.path.join(REPO, ".scratch/pkg/witnesses")):
        cand = os.path.normpath(os.path.join(base, p))
        if os.path.exists(cand):
            return cand
    stripped = p.lstrip("./")
    cand = os.path.normpath(os.path.join(REPO, stripped))
    if os.path.exists(cand):
        return cand
    raise FileNotFoundError(p)


def main(paths):
    cache = {}
    for p in paths:
        w = Witness(p)
        tp = resolve(w.template_path, os.path.dirname(os.path.abspath(p))) if w.template_path \
            else os.path.join(REPO, "artifacts/k15_template_Tminus_aut2_m4.col")
        if tp not in cache:
            cache[tp] = Template(tp)
        rep = check_witness(w, cache[tp])
        print(report(w, cache[tp], rep, name=os.path.relpath(p, REPO)))
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
