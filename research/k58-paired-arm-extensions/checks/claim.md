# Paired-arm sender rules for ordinary K58

## The original ternary clause

Let the root be r. Let a belong to its color-c arm, and let g denote the exact encoder guard requiring at least 14 color-c neighbors of a in the other three arms. For shorthand write E(v) for the event that av has color c.

For an arm B of root color b different from c, put S(B) = {v in B : E(v)}. Edges inside S(B) avoid b because all vertices belong to B, and avoid c because they are c-neighbors of a. Thus |S(B)| ≤ 5 by the two-color triangle Ramsey bound R(3,3)=6. At size five, each remaining color forms a five-cycle. When g holds the three sizes are 5,5,4 in some order or 5,5,5.

For any two distinct other arms B,D, let H and J meet every compatible five-set in B and D respectively. Enumerating all five-subsets that avoid internal c edges and respect frozen signed spokes supplies a sound list for each classified arm. If g holds, B or D supplies five, hence at least one of its hitting-set spokes has color c. This gives the clause

    ¬g ∨ ⋁_{u∈H} E(u) ∨ ⋁_{v∈J} E(v).

Singletons H={u} and J={v} give the three-literal rule. If B has no compatible five-set, H may be empty. Then D must supply five. If both lists are empty the consequence is ¬g. For a catalog filtered using additional cube literals Q, add their negations to the clause when returning to the parent. Rebind the guard, edge variables, color, geometry and input hash for each target.

## A two-vertex hitting set

Take H={u,v} such that every compatible five-set contains u or v, while neither vertex is common to all five-sets. If every compatible five-set of D contains w, the clause is

    ¬g ∨ E(u) ∨ E(v) ∨ E(w).

At hard-list rank 8 the sender is 46, its color is 3, the pair is {4,11}, and the singleton is 40. Six compatible five-sets in the first arm meet the pair. The second arm has one compatible five-set and it contains 40. Its DIMACS clause is -24663 1056 2428 6024 0. The original parent with this clause falsified took 105 conflicts to refute and the stored DRAT proof passed independent replay.

The 1,300-row census lists 176,136 row-specific four-literal clauses, with matches in every row. On 13 selected ranks there were 1,747 candidates. All their falsifying assignments survived unit propagation with the original ternary clauses. Of these, 939 also survived the earlier direct encoding, which had already used up to three minimum hitting sets per arm. Each new clause immediately rejects its falsifying cube.

One of those 939 examples per panel row was tested on the unstrengthened original full-root input under the exact falsifying assignments. Ranks 8 and 340 have native proofs. The other eleven queries reached 40,000 conflicts. A separate finite checker matched each input hash, enumerated five-subsets directly from signed parent pins, and verified the hitting condition for all 13 examples. The native solver timeouts leave those eleven without individual DRAT certificates in this package.

## Signed variants and negative results

A literal negative E(u), meaning ¬E(u), is true on every compatible five-set when u belongs to none of them. A signed singleton on each of two arms therefore gives mixed or double-negative ternary clauses by the same counting argument. The census found 26,224 mixed and 10,136 double-negative instances after discarding the obvious single-spoke triangle exclusions. On the 13-row screen, all tested signed instances were already rejected by propagation with the earlier positive ternaries. Fourteen sampled falsifying cubes also have direct full-parent refutations. Keep the four-literal additions separate when measuring incremental propagation.

The search for forced single spokes from pairs of compatible four/five supports found no further literal beyond frozen triangle exclusions. The single-arm search for nontrivial signed two-spoke clauses in these relaxed support tables also found none. These statements concern the named-arm relaxations tested here.

## Whole-parent performance and reproduction

On six ranks, the earlier direct plus positive ternary clauses and the same input augmented with all candidate four-literal clauses each completed 0/6 unrestricted searches within 60,000 conflicts at seed zero. The candidate counts and local refutations establish a propagation gain. Completion time remains unmeasured.

The archive includes the predecessor encoder and signed inputs. On x86-64 Linux with Python 3.12 and a C compiler, from the extracted top directory run

    sh hard-study/setup.sh
    hard-study/.venv/bin/python hard-more/check_supports.py
    hard-study/.venv/bin/python hard-more/widereplay.py verify hard-study/tools/drat-trim
    hard-study/.venv/bin/python hard-more/replay.py verify hard-study/tools/drat-trim
    hard-study/.venv/bin/python hard-more/export.py 8 rank8-augmented.cnf

The verifier replays the retained traces and preserves the OPEN status of native timeouts. The export contains the prior direct and ternary clauses plus the new four-literal clauses passing the propagation screen. It includes mathematically derived clauses beyond the individually replayed examples.
