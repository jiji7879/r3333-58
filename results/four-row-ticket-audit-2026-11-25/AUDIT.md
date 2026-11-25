# Independent audit: four-row degree solver and ticket note

Date: 2026-11-25.

## Verdict

The mathematical ticket arguments are useful and sound on inspection. The solver
package contains coherent exact-coverage code, and its scope computation reproduces
all published counts. Two independently regenerated cases produced fresh verified
UNSAT proofs. **The central whole-row bound `d_0(q) <= 14` is not yet independently
certified by this attachment:** the 518 DRAT traces are in separate proof bundles that
were not supplied. The queue inherited from an earlier campaign also has to remain
part of the eventual certification chain.

Therefore the reciprocal exclusions for the four named rows are a promising
conditional result, not accepted branch closures yet. No unrestricted row is closed.
No profile elimination or new Ramsey bound follows.

## What was actually checked

Archive:
`attachments/let-s-try-and-rbdv/K58_four_row_degree_solver.zip`, SHA-256
`ae795dd0d77b3a87659c5629aae80b00556778a62b8400b1e54e0a6e2ada9107`.
Every entry in its included `SHA256SUMS` passed after extraction to
`.scratch/attachment-audit/four-row/`.

1. `python3 verify.py --scope-only` reproduced:
   - 2,151 incoming open words per row;
   - contact layers 55 / 252 / 731 / 1,113;
   - all 611 physical contact-set groups covered for the claimed colour-0 bound;
   - nine extra three-contact exclusions, leaving 46 there;
   - 2,142 open unrestricted words per row;
   - a 518-proof cover as selected from the manifest.

   The scope-only code treats manifest entries marked `verified: true` as available
   proofs. Thus this is a coverage/table check, not a DRAT replay. Its output is
   `scope-only.log`.

2. All four native two-edge reciprocity CNFs rebuilt to their recorded hashes and
   replayed the two-byte empty-clause trace (`conditional-capstones.log`). These tests
   start after the derived degree cuts have been inserted, so they are conditional on
   precisely the missing full degree-cover verification.

3. Fresh, independent proof generation on two exact cases:
   - smallest grid case, CNF `012a513ed078238f364e83fce5609be2f292228c669078c36ff697e017768eba`,
     fresh DRAT `1d22345dba4c2eeab6b9a45fc12c4c0567eacfee1efb2ff43469ad7e10814110`;
   - the 66-entry anchored `K15` catalogue blocker, CNF
     `ac398ea169b56226da89b446a46af93226e20a53f73b834db97b78e469d4faf8`,
     fresh DRAT `963cebbe294b4c6c3d09507762573c6cfebf211891d4f2cd5dfd982608314ef8`.
   Both rebuilds matched the manifest CNF hashes; both new proofs returned
   `s VERIFIED` with an empty clause (`fresh-controls.log`). Fresh proofs need not have
   the old DRAT hashes. These validate real encoder cases, not all 518 cases.

## Evidence missing from this ZIP

`results/manifest.jsonl` has 518 records and calls for a total of
**1,861,878,149 bytes of DRAT traces**. Those traces are not included. The verifier
stops at `KeyError` on the first missing proof unless given:
- `K58_degree_certificates_1.zip`, and
- `K58_degree_certificates_2.zip`,

which unpack to the eight `K58_degree_proofs_01.zip` … `_08.zip` shards indexed in
`results/certificate-index.json`. The README also explicitly places the incoming open
queue on top of earlier DRAT archives; that inherited premise must remain explicit if
its proof archive is not in these two bundles.

The attached two-byte `results/two-edge.drat` is not itself evidence for the degree
bound. It is only the final contradiction after adding that bound.

## Mathematical checks (independent of the missing DRAT files)

### Connectivity and the common critical palette

The note correctly derives `alpha(G_c) <= 16` from `R(3,3,3)=17`. Triangle-freeness and
the same bound give every colour degree at most 16, hence at least 9 on 58 vertices.
For two vertices in different components of `G_c`, the union of their colour-`c`
neighbourhoods is independent and has at least 18 vertices, a contradiction. Every
colour graph is connected. Edgewise reciprocity makes criticality constant along an
edge of that colour, so connectivity makes each vertex's critical-colour set identical.
The sum of degrees (57) gives common palette size one, two, or three.

### Hall paths and unreciprocated tickets

For nonadjacent `r,q`, with `I=N(r) intersect N(q)`, `L=N(q)\I`, and `R=N(r)\I`,
the displayed set is independent, so
`|N_R(X)| >= |X| - (alpha(G)-d(r))`. At `d(r)=alpha(G)`, Hall gives a matching from
all of `L` into `R`, and the common neighbours supply the remaining length-2 paths.
These `d(q)` internally disjoint paths meet the critical/noncritical cut in distinct
edges. The claimed unreciprocated-ticket lower bounds and the doubled balanced-cut
bound follow; no global incoming/outgoing hypothesis is needed for the first bound.

If the complete degree-cover proof replays, the previously pinned colour-0 path
`r-b-q` also gives the short reciprocal contradiction: criticality propagates from
`r` to `b`, then to `q`, contrary to `d_0(q) <= 14`. Two-edge reciprocity suffices.

### Encoding review

The matrix selectors form one-way implications plus an exhaustive disjunction, which
is the correct direction for a catalogue cube: a selected matrix forces its edges, and
some matrix must be selected. The Hall selectors similarly force an actual matching
when a marked neighbor exists; auxiliary selectors can always be chosen from a real
matching. The imported “balanced counts” here are local degree sums at the marked
vertex, not the forbidden global perfect-balance assumption.

## Exact scope if the proof chain completes

The named rows are branches 53 and 54 at charges 7 in profiles `(16,16,14,11)` and
`(16,16,13,12)`. Only their reciprocal alternatives would be eliminated by the degree
argument. Their unrestricted rows still have 2,142 open words each in this framework;
the reported nine further exclusions are unconditional locally but likewise require
the full proof replay. The excluded `(15,14,14,14)` profile was not selected, encoded,
or solved in this audit.

## Next required action

Supply the two named certificate bundles (and identify the inherited queue proof
archive if separate), then run the package's ordinary per-case DRAT verifier over all
518 records, followed by its coverage and native-capstone checks. Do not treat this
step as satisfied by the scope-only run or by the fresh two-case controls.
