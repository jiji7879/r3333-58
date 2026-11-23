"""First-pass compact search with a deletion prefix for fully sending retry rows."""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from pysat.solvers import Minisat22
from dense import marked_threshold
from gluing import units
from profile_kernel import PHYSICAL, PROFILE, build, delete, family_of, lift


def fully_sending(row):
    f=row["family"]
    return (tuple(f["profile"])==PROFILE and row["charge"]==15 and f["arm"]==0
            and f["root_kinds"]==["T","-","-","-"])


def retry_only(row, recipe):
    f=family_of(row)
    pinned=units(f,row["placement"])
    def suffix(full):
        return Counter(tuple(cl) for cl in marked_threshold(f,pinned,15,**dict(recipe,full_root=full)))
    first,retry=suffix(False),suffix(True)
    if first-retry:
        raise ValueError("first-pass clauses are not a subset of this retry")
    return (retry-first).elements()


def build_senders(row,recipe,path,proof_prefix=None):
    if not fully_sending(row):
        raise ValueError("sender compression requires all 15 senders in the marked arm")
    first=dict(recipe,full_root=False)
    if proof_prefix is None or not recipe["full_root"]:
        return build(row,first,path,proof_prefix=proof_prefix)
    with TemporaryDirectory(dir=Path(path).parent) as tmp:
        compact=Path(tmp)/"compact.drat"
        removed=Path(tmp)/"retry-only.drat"
        with removed.open("wb") as out:
            for cl in retry_only(row,recipe):delete(out,cl)
        result=build(row,first,path,proof_prefix=compact)
        lift(removed,compact,proof_prefix)
    return result


def extend_retry(row,recipe,values):
    # All A senders already provide the 15 root tickets. Ask for, and verify,
    # an actual extension of the physical assignment in the frozen numbering.
    f=family_of(row)
    fixed=units(f,row["placement"])
    extra=marked_threshold(f,fixed,15,**recipe)
    physical=[v if values.get(v,False) else -v for v in range(1,PHYSICAL+1)]
    with Minisat22(bootstrap_with=extra) as solver:
        if not solver.solve(assumptions=physical):
            raise ValueError("physical model has no frozen ticket extension")
        return {abs(v):v>0 for v in solver.get_model()}
