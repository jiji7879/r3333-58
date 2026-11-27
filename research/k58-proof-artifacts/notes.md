# Working notes

## 1. Baseline proof identity vs 5,245 vs 5,250

Initial inspection of `A0.json` found the exact coordinator-generated native CaDiCaL 2.1.2 baseline: parent SHA-256 `56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837` and raw DRAT SHA-256 `9798683a7f8b3e5ee7c77b86c005bd64aa4357490be350bafd71ea0e76ee9e89`. The supplied `A0.core` has 5,250 clauses. The earlier coordinator original core from a rebuilt stock 1.9.5 DRAT with SHA-256 `91be7183…` had 5,245 clauses.

Rerunning `drat-trim` on the raw native 2.1.2 proof with `-i -U -t 600 -c` produced **5,250 clauses, byte-for-byte identical to the packaged A0 core**, hash `5f4d62aa81757098093d988c9914ae35642d7aa9f77df4c7fef49b41043cf8e0`. The checker C source hashes all match `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`. The discrepancy is the different proof stream, not a checker bug or random nondeterminism. The full `recheck.py A0` independent LRAT replay then returned `A0 VERIFIED against 56ad…0837`.

## 2. Local 2-SAT/spoke checks already rerun

The supplied exhaustive small analysis was rerun: two-colour complete graphs through $K_5$, 600 varying-list cases, all deletions of the two-odd-cycle obstruction, and its explicit triangle-free 4-colouring of $K_{10}$. An additional 4,000 random list-constrained instances on up to ten sites and four colours were compared with independent brute-force assignment enumeration: 3,293 satisfiable and 707 unsatisfiable, with no mismatches.

`verify.py` rebuilt and warning-fatally checked both RUP steps of each of the four ordinary-wall five-literal clauses against the exact original parent, included fixed palette exclusions, and passed all four. Their local satisfiability or OPEN performance status is not altered by that semantic validity; all 16 supplied comparison runs at 40,000 conflicts remain OPEN.

## 3. Native original-parent checks already completed

With independently compiled `drat-trim`, the C `lrat-check`, and the binary-to-text converter:

* `recheck.py A0`: PASS against the unrestricted original parent.
* `recheck.py P13000`: PASS against the unrestricted original parent, after putting the supplied optional proof stream beside the verifier as it requires. The earlier missing-path failure was not a failed proof or a package defect.
* `recheck.py D0`: PASS against the unrestricted original parent.
* `recheck.py squares`: PASS on all seven square-transfer clauses at ranks 1294–1300, including each checked derivation step.
* `drat-trim A.cnf 502176.rup -I -f -U`: the checker reports `s DERIVATION` and “all lemmas preserve satisfiability”; expected `rc=1` because the slice is a derived-clause proof, **not a refutation**. `-W` correctly rejects the expected “no empty clause” warning rather than enabling a false refutation claim.
* `drat-trim A.cnf 577233.rup -I -f -U`: the same explicit derivation result, with the same non-refutation status.

DIMACS identity checks show D is the unchanged baseline body plus exactly `4687 3590 4034 4673 0` and `-5160 3282 4822 0`; the D0 whole-parent proof therefore is not simply accepting those lines as assumptions. B/C have their documented one/two additional clauses and matching hashes.

## 4. Projection semantics

All seven projections (`P1294`–`P1300`) are strict ordered subsequences of their own original parents, with only the header's clause count changed, every variable on an edge within the selected vertices, and no auxiliary clause. Bound hashes and all 30,630/33,270-clause counts reproduce exactly. The two classified other arms and the marked sender's known support account for the 35 vertices on most projections, 36 on rank 1299.

On the supplied full-model logs, the rank-1298 model satisfies all 30,630 projected clauses and the rank-1299 model all 33,270. Evaluation with the exact sign per absolute variable ID shows the same models falsify 1,318 and 1,287 full-parent clauses, respectively. These are explicitly local models on selectable 35/36-vertex subgraphs, **not $K_{58}$ colourings**. An UNSAT projection implies unrestricted parent UNSAT via subset; a projection model says nothing about full admissibility.

`P13000` refutation has independently replayed on the true original parent. The other four projection refutations (ranks 1294–1297) were left to the independent projection-direction audit rather than claimed replayed locally.

## 5. Remaining review and overheads

A related independent swarm, `smwzmjadv`, is covering local 2-SAT/spoke audits, all projection refutations, all eight comparison LRAT streams, and mined-clause transfer semantics. Their verdicts, any defects, exact non-replayed streams, and amortized solver-cost assessment remain to be incorporated. Do not describe all new files as before verification or as a general solver win merely because a receipt claims it. Proof generation/checking itself is expensive and must be included in any end-to-end claim.
