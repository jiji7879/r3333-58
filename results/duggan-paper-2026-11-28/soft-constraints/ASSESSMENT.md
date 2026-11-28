# Soft-constraint transfer from Duggan (2024) to the K51 search

## Verdict

**A sound transfer is implementable, but these pilots do not demonstrate material K51 benefit.** Unit soft constraints based on the repository's one-defect colouring generated nontrivial nested relaxations; one corrupted-K50 control found and independently checked a valid model. On K51, however, the informative softened instance stayed UNKNOWN at 50,003 conflicts, and the literal multicolour zebra/Toeplitz initializer also stayed UNKNOWN at its 50,000-conflict cap. No K51 colouring was found. The accepted status remains $51\le R_4(3)\le62$.

The useful new outcome is therefore a concrete implementation, exact scope, controls, and a measured obstacle—not a solver speedup or nonexistence claim.

## What the paper actually supplies

Chapter 10 of Duggan's paper discusses SCSat as **related work** (Fujita, Koshimura, Hasegawa, 2013), not as a component of his R(3,8)/R(3,9) proofs. After UNSAT, soft constraints are scored by their direct/indirect conflicts and a high-scoring proportion is removed (20% reported as a reasonable default). Duggan describes:

* U-SC: unit clauses from a known partial colouring;
* Z-SC: $e_{ij}\leftrightarrow z_{j-i}$, giving striped matrices. With four one-hot colours per edge this becomes the Toeplitz form below.

He also explicitly warns that the search is not exhaustive unless all soft constraints are removed. Thus this is relevant to **(iii) finding K51**, not by itself to wall-row UNSAT or Lemma L.

My U-SC deletion score is **UNSAT-core incidence**, not the original direct/indirect-conflict score. It must not be reported as a reproduction of SCSat's running time.

## Exact encoding and deletion rule

For each $e=(i,j)$, $i<j$, and $c\in\{0,1,2,3\}$, introduce $x_{e,c}$. The hard K51 formula $H_{51}$ consists of
$$\bigvee_c x_{e,c},\qquad \neg x_{e,c}\lor\neg x_{e,d}\quad(c<d),$$
and, for every $i<j<k$ and every colour $c$,
$$\neg x_{(i,j),c}\lor\neg x_{(i,k),c}\lor\neg x_{(j,k),c}.$$
This has 1,275 edges, **5,100 variables and 92,225 clauses**. The K50 control uses 4,900 variables and 86,975 clauses.

Given a guide colouring $g$, an active pin set $A$ imposes the assumptions $U(A)=\{x_{e,g_e}:e\in A\}$. CaDiCaL solves $H_{51}\land U(A)$ incrementally. On an assumption-level UNSAT result, let $C$ be the failed-assumption core. Increment $s_q$ for each $q\in C$, sort $C$ by decreasing $s_q$ (lexicographic ties), and remove
$$\max(1,\lceil\rho|C|\rceil)$$
constraints from $A$. I tested $\rho=0.2$ and the one-pin control $\rho=0$.

Two consequences define the soundness boundary:

1. Active sets only shrink, so the permitted solution sets can only grow. A SAT model under **any** remaining assumptions satisfies the untouched hard formula $H_{51}$ and is a genuine K51 witness, independently of the guide.
2. UNSAT under assumptions refutes only that pinned branch. UNKNOWN proves nothing. Even deleting every pin and obtaining UNSAT would require a DRAT-checked proof of $H_{51}$; nothing like that happened here.

Source: `scsat_pilot.cpp` (CaDiCaL 3.0.1 static API, signature `cadical-3.0.1-fa13863`).

## What is new relative to the repository

`results/summary.md` records the one-defect K51 artifact, exact Hamming exclusions through distance 5, local repair, and about 14,700 DRAT exclusions. It does not give a core-scored incremental soft-pin implementation. I found no SCSat/MaxSAT implementation in current tracked `tools/` or `results/`.

The guide used here is `artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col`, SHA-256
`f9f5b5cb2070b1a92611e100a1c1b669ef12fe63d0fa41c34cd490055721b5dc`.
The preparation script independently rechecks that its unique triangle is $(48,49,50)$ in colour 1. The new artifacts are the concrete deletion trajectories, their exact cores/pin counts, an independently regenerated conditional proof, and a literal Toeplitz zebra control. These are not the old Hamming-sphere certificate and do not supersede it.

## Validated pilots

### Encoding and positive controls

* Exact solution enumeration of the base encoder gave **3,156** models for $(n,k)=(4,4)$ and **12** for $(5,2)$, both equal to independent brute force. Its $(6,2)$ base was UNSAT, as required by $R(3,3)=6$.
* Deleting vertex 50 from the defective K51 guide gives a valid K50 base. Recolouring edge $(0,1)$ from colour 1 to 2 creates exactly four bad triangles, with third vertices 10, 11, 38, 39.
* With all 1,225 K50 guide pins active, CaDiCaL reported UNSAT with core $\{x_{(0,1),2},x_{(0,10),2},x_{(1,10),2}\}$. Removing the one corrupt pin gave SAT on the next call. `tools/verify_coloring.py` independently returned: **VALID: 50 vertices, 4 colours, no monochromatic triangle**.

This validates model fidelity and shows that the deletion mechanism can repair an actually satisfiable corrupted guide. It says nothing about K51 scaling.

### K51 U-SC results

For $\rho=0.2$, CaDiCaL reported 21 assumption-level UNSAT calls, followed by UNKNOWN on the 22nd:

| measurement | result |
|---|---:|
| first failed core / pins released | 321 / 65 |
| failed-core sizes before UNKNOWN | 3–393 |
| active pins before UNKNOWN | 485 |
| released pins before UNKNOWN | 790 |
| final conflict count | 50,003 |
| whole pilot wall / CPU | 1.66 / 1.62 s |
| K51 model | none |

An earlier independent run of the same deterministic trajectory was UNKNOWN at 5,001 conflicts; all corresponding preceding UNSAT-round metadata agree.

The **one-pin** control reported 80 assumption-level UNSAT calls, all with zero conflicts, ending with 1,195 active pins and 80 released pins. Only the final branch was independently DRAT-replayed (below); the other 79 solver reports were used only as deletion heuristics and are not advertised as certified exclusions.

The precise obstacle is that failed cores are not defect-local. The first 321-literal core makes the 20% rule release **65 edges**, although the repository's exact local repair result concerns at most five changes. Nonminimal-core cardinality, rather than useful conflict information, can therefore control the relaxation scale. The one-pin policy avoids this jump but does not itself show better model finding.

### Strict conditional proof check

I regenerated the 80-release CNF independently in Python: 5,100 variables, 92,225 hard clauses and 1,195 unit pins (**93,420 clauses total**). CaDiCaL 2.1.2 returned UNSAT and a 21,112-byte binary DRAT proof. The raw checker exposed the known pseudo-unit deletion warnings, so it was not accepted under the warning-fatal policy. Dropping only 814 deletion records while preserving all 4,470 additions byte-for-byte produced a 17,856-byte proof. The command

```sh
drat-trim one_pin_round80.cnf one_pin_round80_additions.drat -i -U -W -t 60
```

read the complete proof and returned one `s VERIFIED`, zero warnings/errors and zero RAT lemmas. A satisfiable wrong-parent CNF with the same declared variable bound was rejected with `s NOT VERIFIED`, exit 1.

This certifies only the particular 1,195-pin branch in `one_pin_round80.cnf`: no valid K51 agrees with all those guide pins, with the 80 logged edge positions left free. It is a small conditional exclusion, possibly overlapping historical exclusions; **it is not K51 UNSAT and is not claimed as a new Ramsey result**.

### Literal Z-SC: Toeplitz, not automatically Cayley

For $d=1,\dots,50$, add four one-hot $z_{d,c}$ variables and the equivalences
$$x_{(i,j),c}\leftrightarrow z_{j-i,c}.$$
Together with $H_{51}$ this has **5,300 variables and 102,775 clauses**: 350 clauses enforce one-hot $z_d$ values and 10,200 enforce edge/stripe equivalences. At $n=4,k=4$, exhaustive SAT enumeration and independent brute force both found 48 valid Toeplitz assignments.

At K51, CaDiCaL hit the 50,000-conflict cap in 1.02 s wall / 0.98 s CPU, **UNKNOWN**, with no model and no zebra-family exclusion. No adaptive deletion was scored because the all-active initializer did not return UNSAT.

A structural caution: literal $j-i$ stripes are Toeplitz constraints. Replacing them by cyclic distance $\min(j-i,51-(j-i))$ would instead force a circulant colouring, to which existing Cayley/Cayley-family exclusions could apply. Those are different families; the latter closure cannot be used to reject the literal formula tested here.

## Applicability and next experiments

* **K51 model finding:** potentially useful as a cheap instance generator, but not yet shown to help. Do not launch a production sweep from these results.
* **Small-wall UNSAT / Lemma L:** no direct transfer. A soft, deleting search is non-exhaustive by design. It cannot close a wall row or reduce profiles unless a complete cover and proof composition are supplied. It supplies no new incidence identity for Lemma L.
* **Certificates:** returned failed cores are heuristic metadata, not proof artifacts. Each claimed branch exclusion needs its own exact parent CNF and strict DRAT/LRAT replay, as in the one retained control. SAT witnesses need independent physical verification (and kernel verification if a K51 witness ever appears).

The next small U-SC experiment should **record every removal**, export the exact 485-pin CNF, and compare a fresh solver with the incremental trajectory at the same fixed 50,000-conflict budget. Only then test a deletion-minimised/small-core scorer. This separates the value of learned incremental state from the value of the remaining pins and directly addresses the observed nonminimal-core problem. Larger undirected conflict budgets are not the informative next step.

For literal Z-SC, a bounded four-leaf control is well defined: fix $z_1=0$ by global colour renaming, split $z_2$ over its four colours, and retain each query/proof separately. This is exhaustive up to colour renaming only for the **Toeplitz** model class, not for K51. Every timed-out leaf stays OPEN. I did not run this follow-up.

## Reproduction

Run from this directory (`.ultramath/smwzxq4fl/m7/`):

```sh
ROOT=$(git rev-parse --show-toplevel)
g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  -I"$ROOT/work/k54/build/cadical/src" scsat_pilot.cpp \
  "$ROOT/work/k54/build/cadical/build/libcadical.a" -o scsat_pilot
./scsat_pilot selftest | tee selftest.jsonl
python3 prepare_k50_control.py
./scsat_pilot search k50_corrupt_guide.col k50_control.jsonl 2000 5 10 20 k50_control_model.col
python3 "$ROOT/tools/verify_coloring.py" k50_control_model.col
./scsat_pilot search "$ROOT/artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col" \
  k51_core20_50k.jsonl 50000 15 40 20 k51_candidate.col
./scsat_pilot search "$ROOT/artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col" \
  k51_one_pin_80.jsonl 50000 15 80 0 k51_one_pin_candidate.col
python3 replay_one_pin.py
python3 zebra_pilot.py selftest | tee zebra_selftest.jsonl
python3 zebra_pilot.py run51
python3 validate_results.py
```

`pilot_summary.json` collects the checked numbers. `toeplitz_k51_result.json`, `one_pin_round80_replay.json`, and the JSONL trajectories retain the exact statuses. No repository files outside this member directory were modified.

## Limitations

Only single deterministic trajectories and small caps were run. I did not obtain the original SCSat implementation, reproduce indirect-conflict scoring, minimise every core, run MaxSAT, compare multiple guides/seeds, or prove a speedup. The 50,003- and 50,000-conflict UNKNOWNs support no absence claim in either family. In particular, these experiments do not show that soft constraints cannot ever help; they show that the tested direct transfers have not yet earned production compute.
