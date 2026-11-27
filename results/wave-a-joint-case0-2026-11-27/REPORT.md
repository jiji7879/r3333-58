# Two second-arm vertices, case 0

## Outcome

**Two vertices can be realized together in many local models, but there is also
a meaningful joint incompatibility on the exact full signed-parent formula.**
This is one controlled case-0 pair, not a proof about the whole wall and not a
new Ramsey bound.

The case is live-cover representative index 0, row
`00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`,
owner words `00000/01022`. The pivot is physical edge $(u,v)=(31,42)$.
Its two local-pivot branches 1 and 2 map to physical colours **0 and 3**.
Because the original 28-parent run's source was not supplied here, this is a
**new explicit controlled cohort**, not a claimed rerun of those 28 branches.

The complete second arm is vertices $B=\{1,\ldots,15\}$. The projection is
root 0, the nominated 14-arm (31–44, in pentagon order), and all of B: 30
vertices and 435 edges. I tested two particular second-arm vertices
$w_1=1,w_2=2$. A tuple $(a,b,c,d)$ means

$$c(uw_1)=a,\quad c(vw_1)=b,\quad c(uw_2)=c,\quad c(vw_2)=d.$$

## Complete paired local enumeration

For each of the two branches, all $4^4=256$ tuples were tested. The final panel
has **no UNKNOWNs**:

| branch | physical pivot colour | checked complete local models | strict local UNSAT proofs |
| --- | ---: | ---: | ---: |
| 1 | 0 | 56/256 | 200/256 |
| 2 | 3 | 56/256 | 200/256 |

Every model is one complete assignment on the selected 30 vertices, with no
monochromatic triangle, the projected physical pins, the exact mapped owner CNF,
existing signed-rule additions, and the degree-16 cap. The arm projection was
also checked through `edge_domains.valid`; this is not a collection of unrelated
spoke choices. Every UNSAT has binary RUP replay with `-i -U`, no warning
suppression, exact `s VERIFIED`, and zero warnings.

There are **52 tuples jointly realizable in both branches**. Eight outcomes
differ: for each local colour $b=0,1,2,3$, the branch-specific assignment
$(2,b,p,p)$ flips exactly when $p$ is the branch's physical pivot colour. That
is the known monochromatic triangle at $w_2$, not a new global discriminator.

The final panel ran with a one-second cap per query. An earlier quarter-second
pilot contributed 129 unchanged, hash-checked, already-replayed UNSAT leaves;
every UNKNOWN and SAT case was rerun. In particular tuple $(2,0,2,1)$ was an
OPEN at the short cap but became a checked local model at the larger cap.
The final ledger includes 512 four-edge calls and two separate base models.
`fresh_local_solver_calls=385` counts the two base calls; another 129 calls
are strict UNSAT replays reused after byte/hash checks. No solver status was
changed by reuse alone. See [local-outcomes.tsv](local-outcomes.tsv),
[local-analysis.json](local-analysis.json), and the full preserved receipt in
the archive.

## The important joint condition

Take one particular ordered pair at the first vertex:

$$\bigl(c(uw_1),c(vw_1)\bigr)=(2,1).$$

That choice is locally realizable (for example with $(2,0)$ at $w_2$).
Individually, at the other vertex, each choice $(c,1)$ for $c=0,1,2,3$ is also
locally realizable (for example with $(2,2)$ at $w_1$).
But **none of the four combinations is jointly realizable**:

$$(2,1)\text{ at }w_1,\qquad(c,1)\text{ at }w_2,\quad c=0,1,2,3.$$

This holds in both branches and is not a monochromatic triangle involving the
pivot. Projected onto the observed independent choices, each branch has
$4\times15=60$ combinations available separately; exactly these **four joint
obstructions** reduce its 60 possibilities to the observed 56. There are no
other product-level gaps in this fixed two-vertex panel. This is precisely the
wanted distinction between individually allowed and jointly allowed choices.

### What follows on the exact full branch formulas

I then tested precisely these four combinations in **both** physical-colour
branches, without the local projection. Every query was the full case-0 signed
branch formula plus the named four colour units.

For physical colour 0, the base full-branch SHA-256 is
`f7e6f5b2cb5a95bf65c16c730f7c4e10bd359b3d413d031bcbf9dd180dd5ff8d`.
For physical colour 3 it is
`e85234ab42705601f1b83a2e6127ecb89dea669ba78865f35ea57e47815ece7a`.

**All eight full-parent joint queries are VERIFIED_UNSAT.** Their native DRATs
were normalized by dropping only complete deletion records, leaving every
addition byte unchanged, and re-replayed against the exact full queries with
`-i -U -t 300`, exit 0, exact `s VERIFIED`, and zero warnings. Native solver
statistics recorded **zero conflicts in every one of the eight calls** and
0.0316251514 s of search altogether. These are real proof-backed consequences
for the exact full case-0 branch, not merely local assertions.

In literal form, with $u=31,v=42,w_1=1,w_2=2$,

$$E_{u,w_1,2}\land E_{v,w_1,1}\land E_{u,w_2,c}\land E_{v,w_2,1}$$

is impossible for every $c\in\{0,1,2,3\}$ and for each of the two exact branch
formulas. The implication is not asserted as an unguarded universal Wave A rule;
its full branch and edge hypotheses are part of every proof.

### Individual-choice controls

For each branch, I separately tested:

- $(2,1)$ at $w_1$ only;
- $(c,1)$ at $w_2$ only, for each $c=0,1,2,3$.

All **10 full-parent individual-choice calls remained UNKNOWN at two seconds**,
with a total of 516,774 conflicts. By contrast, supplying the other vertex's
spokes made every joint query immediately proof-solvable. These UNKNOWNs do
**not** prove the individual branches SAT. They show that the limit is a genuine
joint interaction at the tested budget, not a restatement of one chosen side.
The eight cutoff certificates and all ten control receipts are in
[full-parent-controls.json](full-parent-controls.json).

No query closes either whole pivot branch, case 0 as a whole, a wall row, or
the wall. The individual and full children remain unresolved except for the
named four-edge agreements. No full $K_{58}$ model is claimed or supplied.

## How Wave A enters—and does not enter

The attached six rows were separately audited. Under the documented bare-arm
reading, all six displayed patterns are UNSAT at the stated minimum arm size,
with independently replayed DRAT, and all six are SAT one vertex smaller with
checked models. The dihedral group of order 10 gives the listed relative
placements, with a $Z_2$ palette factor for the 20 relabelings. See
[wave-audit/REPORT.md](wave-audit/REPORT.md).

**The physical Wave A JSON conditions, source maps and replay digests were not
supplied here.** No generator or ledger row tying those names to the current
physical parent was found. Therefore this experiment does not claim to reuse
those proof digests or to have injected all six patterns into every wall parent.
The present joint queries use the existing physical rule bank and owner map.
The separate bare-arm audit must not be confused with a physical transfer proof,
and the four exclusions above are a new, scoped joint result, not a claimed
consequence of a missing Wave A JSON file.

## Evidence and replay

The evidence archive is [k58-joint-case0-evidence.zip](k58-joint-case0-evidence.zip)
(supplied in chat; not committed to Git). It contains:

- both local base CNFs and every exact four-unit reconstruction manifest;
- all 400 binary local UNSAT proofs and all 112 local model files;
- the eight complete full-parent query CNFs and their deletion-free DRAT proofs;
- native control receipts, strict proof-check logs, original runner sources,
  extracted physical mapping, and the accepted bare-arm audit.

After extracting the archive in a fresh directory:

```sh
cc -std=c99 -D_GNU_SOURCE -O2 tools/drat-trim.c -o tools/drat-trim
python3 verify_archive.py
# Optional, in this project, also checks the original owner convention for all models:
python3 verify_archive.py --runtime /path/to/audited-K58
# Optional, independently replay all 400 local UNSAT proofs:
python3 verify_archive.py --all
```

The global reduction's semantic Lean proof is not supplied by this experiment.
No production ledger was modified and no production sweep was restarted.
