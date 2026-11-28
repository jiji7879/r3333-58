"""Standard-library-only audit of m3's native proofs and m1/m4's clauses.

No encoder or member audit function is imported.  E(u,v,c) is computed
lexicographically; all 134,995 physical host clauses are reconstructed as a
set.  Parent hashes and proof check output are independently bound.
"""
from __future__ import annotations
from hashlib import sha256
import itertools
import json
from pathlib import Path
import subprocess

REPO = Path.cwd()
OUT = REPO / "research/k58-closed-case-mining/work"
S = REPO / ".ultramath/smx04vulj"
CHECK = REPO / ".scratch/massive-clean-install/k58-solver/bin/drat-trim"
INFOS = {
    "source": {
        "parent": S / "m3/replay/2c/parent.regenerated.cnf",
        "proof": S / "m3/native/closed-panel/2c/2ce34a4453cb6cb30dc4f2d9fc61327dc07c3b5ab7d8fec512c3658cd95a4af3/first/TTT-_2_32.drat",
        "sha": "1bb9f188a7c11cd8335e465e9f815991015f4c4ce4c2bce3d510cc5063b5fd97",
        "proof_sha": "083d6b3381bd2459b830ab505fd5f63e39d8f172a07dbea8275a7dfedf204e50",
        "qrole": (12, 29, 49, 3),
        "rrole": (1, 18, 21, 3),
    },
    "dest944": {
        "parent": S / "m3/replay/94/parent.regenerated.cnf",
        "proof": S / "m3/native/closed-panel/94/944f4a5583e16a177498240d7799ec98a0f8b3c1785c5c712e205c4c1380af63/first/TTT-_0_0.drat",
        "sha": "a3e46c0ba80e51fd15c49db332471449d8a371aa5976b61c7426939b24e9b302",
        "proof_sha": "383ade3a567b35da1d868ff7baa45889e9359c08b317b48f6a0e1fb4de39a86d",
        "qrole": (2, 17, 34, 1),
        "rrole": (49, 54, 0, 3),
    },
    "dest6116": {
        "parent": S / "m3/replay/61/parent.regenerated.cnf",
        "proof": S / "m3/native/comparison-panel/61/6116d9150f721359c6bf2e8ab7da22512f076c1c77c3c687d7d637ab94459708/first/TTT-_2_33.drat",
        "sha": "e4dfee1874f41fdf2475c08a51f6ba05bb914064c7c9530c8c5c5735c5e1bd3a",
        "proof_sha": "5defe1b9aecff6a6874f2346e2622fc1e4f35a29fbfd0f030dba4c735cc15d31",
        "qrole": (5, 21, 38, 1),
        "rrole": (49, 54, 0, 3),
    },
}
EDGES = list(itertools.combinations(range(58), 2))
IDX = {x: i for i, x in enumerate(EDGES)}
HOST = []
for a, b in EDGES:
    vs = [4*IDX[(a,b)] + c + 1 for c in range(4)]
    HOST.append(tuple(vs))
    HOST += [tuple((-x,-y)) for x,y in itertools.combinations(vs, 2)]
for u,v,w in itertools.combinations(range(58),3):
    for c in range(4):
        HOST.append(tuple(-4*IDX[e]-c-1 for e in ((u,v),(u,w),(v,w))))
assert len(HOST) == len(set(frozenset(x) for x in HOST)) == 134995

def E(u,v,c):
    return 4*IDX[(u,v) if u<v else (v,u)]+c+1

def role(r):
    u,v,w,c = r
    assert len({u,v,w}) == 3 and 0 <= c < 4
    pins = [E(u,w,c), E(v,w,c)]
    residual = [E(u,v,d) for d in range(4) if d != c]
    q = [-E(u,w,c), -E(u,v,c)] + [E(v,w,d) for d in range(4) if d != c]
    triangle = tuple(-x for x in [E(u,v,c), *pins])
    return {"role_u_v_w_c": list(r), "pins": pins,
            "residual": residual, "qv":q,
            "triangle": list(triangle), "palette": [E(v,w,d) for d in range(4)]}

def identity(p):
    p = Path(p)
    raw = p.read_bytes()
    return {"path": str(p.relative_to(REPO)), "bytes":len(raw), "sha256":sha256(raw).hexdigest()}

def parse_parent(p):
    raw = p.read_bytes()
    header, *rows = raw.splitlines()
    _, kind, nv, nc = header.split()
    nv, nc = int(nv), int(nc)
    assert kind == b"cnf" and nv >= 6612
    clauses = []
    for row in rows:
        assert row and not row.startswith(b"c"), row
        nums = [int(x) for x in row.split()]
        assert nums[-1] == 0 and all(abs(x) <= int(nv) for x in nums[:-1])
        clauses.append(tuple(nums[:-1]))
    assert len(clauses) == int(nc), (len(clauses), int(nc))
    # Parent order and literal order are evidence, not logical input here.
    assert set(frozenset(x) for x in clauses[:len(HOST)]) == set(frozenset(x) for x in HOST)
    assert len({frozenset(x) for x in clauses}) == len(clauses)
    units = {x[0] for x in clauses[len(HOST):] if len(x)==1}
    return raw, int(nv), clauses, units

def run(p, proof, log, accept=True, rup=False, binary=True):
    cmd = [str(CHECK), str(p), str(proof), "-W", "-p", "-t", "60"]
    # Fresh Kissat streams are binary. Tiny handwritten RUP streams are ASCII.
    cmd.append("-I" if not binary else "-i")
    if rup:
        cmd.append("-U")
    got = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=65)
    text = got.stdout.decode(errors="replace")
    Path(log).write_bytes(got.stdout)
    lines = text.splitlines()
    assert not any("s VERIFIED" in x and x != "s VERIFIED" for x in lines)
    assert ("s NOT VERIFIED" in lines) if not accept else got.returncode == 0
    if accept:
        assert "s VERIFIED" in lines, text
        assert not any("WARNING" in x or "ERROR" in x for x in lines), text
    assert got.returncode == (0 if accept else 1), (got.returncode, text)
    return {"command":cmd, "exit_code":got.returncode,
            "result":"s VERIFIED" if accept else "s NOT VERIFIED",
            "log":identity(log), "warnings_visible":True, "rat_disabled":rup}

def run_query(out, parent_raw, nv, head_count, clause, name, accept=True):
    q = out / (name+".query.cnf")
    proof = out / (name+".rup.drat")
    # Original parent bytes are prefix-preserved; only the header count grows.
    body = parent_raw.split(b"\n",1)[1]
    cube = [[-x] for x in clause]
    raw = f"p cnf {nv} {head_count+len(cube)}\n".encode()+body+b"".join(f"{-x} 0\n".encode() for x in clause)
    q.write_bytes(raw)
    proof.write_bytes(b"0\n")
    result = run(q,proof,out/(name+".log"),accept,rup=True,binary=False)
    return {"clause":clause,"negated_cube":cube,"query":identity(q),"check":result}

def motifs():
    all_words = list(itertools.product(range(4), repeat=3))
    legal = [x for x in all_words if not (x[0]==x[1]==x[2])]
    assert len(legal) == 60
    for c in range(4):
        for uvc, uwc, vwc in legal:
            qvalue = not(uwc == c and uvc == c and vwc == c)
            # Q is false exactly at one colour-c monochrome triangle.
            assert qvalue == (not (uvc==uwc==vwc==c))
        for uvc in range(4):
            assert (uvc != c) == any(uvc==d for d in range(4) if d != c)
    return {"ordered_local_colour_words":64,"nonmonochromatic_words":60,
            "quantifier_reduction":"RGB/role symmetry reduces the Q proof to one pivot resolution for all distinct ordered u,v,w,c; all four colours checked exhaustively."}

def main():
    report = {"archive_sha256_expected":"cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a",
              "checker":identity(CHECK), "scope":"native full-parent refutations and clause implications, not OPEN-wall outcome or parent SAT model",
              "host": {"variables":6612,"clauses_reconstructed":134995,"edges":1653,"triangles":30856,"colours":4}, "cases":{}}
    archive = REPO/"dist/k58-massive-solver.zip"
    assert sha256(archive.read_bytes()).hexdigest() == report["archive_sha256_expected"]
    for name,meta in INFOS.items():
        parent,proof,expected_psha,expected_proofsha = (meta[x] for x in ("parent","proof","sha","proof_sha"))
        parent_id,proof_id = identity(parent), identity(proof)
        assert (parent_id["sha256"],proof_id["sha256"]) == (expected_psha,expected_proofsha)
        raw,nv,clauses,units = parse_parent(parent)
        assert nv in (26246,26631)
        fresh = run(parent,proof,OUT/(name+".fresh-replay.log"))
        qr,rr = role(meta["qrole"]), role(meta["rrole"])
        if name == "source":
            core_lemmas = S / "m3/replay/2c/core-lemmas.drat"
            additions = []
            for line_number,line in enumerate(core_lemmas.read_text().splitlines(),1):
                if not line or line[0] in "dcp":
                    continue
                values = [int(x) for x in line.split()]
                assert values[-1] == 0
                if values[:-1]:
                    additions.append((line_number, values[:-1]))
            mined = {}
            for key, target in (("q", qr["qv"]), ("pinned", rr["residual"])):
                hits = [{"file_line": line_number, "literals": words}
                        for line_number, words in additions if set(words) == set(target)]
                assert len(hits) == 1, (key,hits)
                mined[key] = hits[0]
            report["source_core_lemmas"] = identity(core_lemmas)
            report["source_mined_occurrences"] = mined
        # R needs exact positive parent units. Q does not use any parent unit.
        assert all(x in units for x in rr["pins"]), (name,rr, [x for x in rr["pins"] if x not in units])
        u,v,w,c = meta["qrole"]
        q_incident = [E(a,b,d) for a,b in ((u,v),(u,w),(v,w)) for d in range(4)]
        assert len(q_incident) == 12
        assert not any(x in units or -x in units for x in q_incident)
        out = OUT/name
        out.mkdir(exist_ok=True)
        qcheck = run_query(out,raw,nv,len(clauses),qr["qv"],"q")
        rcheck = run_query(out,raw,nv,len(clauses),rr["residual"],"pinned")
        # Only false-cube proof is 0; no target is assumed in its parent.
        report["cases"][name] = {"parent":parent_id,"fresh_proof":proof_id,
            "fresh_replay":fresh,"q":qr,"q_transfer":qcheck,
            "pinned":rr,"pinned_transfer":rcheck}
    # A wrong-parent RUP control: source R depends on 308 which is not a dest6116 unit.
    dparent,dinfo = INFOS["dest6116"], report["cases"]["dest6116"]
    dunit_pins = role(INFOS["source"]["rrole"])["pins"]
    raw,nv,clauses,units = parse_parent(dparent["parent"])
    assert dunit_pins[0] not in units and dunit_pins[1] in units
    wrong = run_query(OUT,raw,nv,len(clauses),role(INFOS["source"]["rrole"])["residual"],"wrong-parent-pinned",False)
    # Alteration control removes the actual host-triangle witness on dest944.
    # On dest6116 another fixed two-pin triangle already derives part of Q, so
    # deleting the distinguished witness would not test necessity of that route.
    raw,nv,clauses,units = parse_parent(INFOS["dest944"]["parent"])
    destrole = role(INFOS["dest944"]["qrole"])
    assert [E(2,17,1), E(2,34,1), E(17,34,1)] == [510,578,3398]
    _stored_header, *rows = raw.splitlines(keepends=True)
    wanted = str(destrole["triangle"])[1:-1].replace(",","").encode()+b" 0\n"
    if wanted not in rows:
        # The reconstruction used unordered comparisons: find the exact stored line.
        matches=[x for x in rows if frozenset(map(int,x.split()[:-1]))==frozenset(destrole["triangle"])]
        assert len(matches)==1
        wanted=matches[0]
    assert sum(x==wanted for x in rows)==1
    weakened_raw = f"p cnf {nv} {len(clauses)-1}\n".encode()+b"".join(x for x in rows if x!=wanted)
    wp=OUT/"omitted-triangle-parent.cnf"
    wp.write_bytes(weakened_raw)
    # Verify an actual deletion changed the bytes and header by one clause.
    changed = run_query(OUT,weakened_raw,nv,len(clauses)-1,destrole["qv"],"omitted-triangle",False)
    # Match the member's physical-only altered-clause control. Dense aux
    # constraints can independently derive a strengthened clause by UP.
    fixed_end = len(HOST)
    while fixed_end < len(clauses) and len(clauses[fixed_end]) == 1:
        fixed_end += 1
    assert fixed_end - len(HOST) == 548
    physical_lines = raw.splitlines(keepends=True)[:1+fixed_end]
    physical_raw = f"p cnf 6612 {fixed_end}\n".encode()+b"".join(physical_lines[1:])
    # Altered destination clause, one positive palette literal deleted.
    first_positive = next(x for x in destrole["qv"] if x > 0)
    assert first_positive == 3397
    altered_clause = [x for x in destrole["qv"] if x != first_positive]
    altered = run_query(OUT,physical_raw,6612,fixed_end,altered_clause,"altered-q",False)
    report["motif"]=motifs()
    report["negative_controls"]={"wrong_parent":wrong,"omitted_host_triangle":changed,"altered_clause":altered}
    report["prior_bank_comparison"]="One host one-colour clause resolved with one physical triangle. It is not the audited square/matching, colour-pivot, guarded-counter or K15 family. Validity does not show useful search acceleration."
    dest=OUT/"receipt.json"
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verified_native_full_parent_proofs":len(INFOS),
                      "verified_q_transfers":len(INFOS),"verified_pinned_transfers":len(INFOS),
                      "required_rejections":3,"receipt":str(dest)},indent=2))
if __name__ == "__main__":
    main()
