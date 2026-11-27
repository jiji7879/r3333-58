# The 1,300 hard rows of the K58 cover, isolated

These are the rows that were still OPEN after the 98,142-row release and closed in the
2026-11-27 tail pass. They are not wall rows — they are in the two big profiles, and every
one of them is **proved** (certificate replayed). They are listed here because they are the
hardest rows in the cover that anyone has actually decided, and someone may want to look at
why.

`hard1300.tsv`: rank, id, profile, kinds, marked_size, charge, proof bytes, proof sha256,
input (CNF) sha256, hardest first.

## What they cost

| measure | value |
| --- | --- |
| rows | 1,300 (1,280 in `15,15,15,12`, 20 in `16,15,15,11`) |
| recipe | `full_root=true` on all 1,300 — the retry tier |
| DRAT per row | min 60 MB, median 120 MB, p90 225 MB, max 394 MB |
| DRAT in total | **177.9 GB** |
| by charge | 11 → 1,009 rows, 9 → 241, 10 → 11, 3 → 30, 4 → 6, 5 → 3 |
| by root kinds | TTT- 1,017, TTU- 247, TUU- 33, UUU- 3 |
| by marked size | 15 → 1,295, 16 → 5 |

Compare the first-tier budget: 12 s / 400k conflicts. These rows needed the `full_root`
strengthening and, judging by certificate size at ~1.9 MB of DRAT per second of solve time,
minutes each.

## What "looking into them" can and cannot yield

They are UNSAT, so every clause is a consequence and nothing is added by mining clauses.
What carries content is the **core**: the subset of clauses `drat-trim -c` says the proof
needed. If a core is small relative to the 3.5 MB formula, it names a local reason for that
row, and that reason is a candidate lemma. If the cores are large, the technique buys
nothing here.

A cheap way to find out, without shipping 178 GB: take the ten rows with the *smallest*
proofs in this table (60–70 MB) and the ten largest (350–394 MB), extract cores from both
groups, and compare. Cores from big-proof rows are themselves large, so start with the small
ones.

## How to hand a subset to someone

On the machine that holds `evidence/`:

    # the ids are column 2; take the first N (hardest first)
    awk -F'\t' 'NR>1 && NR<=21 {print $2}' hard1300.tsv > subset.txt
    mkdir -p handoff && for id in $(cat subset.txt); do
      cp -r "evidence/${id:0:2}/$id" "handoff/"
    done
    du -sh handoff                      # ~15 GB for the top 20, certificates included
    zip -r hard20.zip handoff

Each case directory holds `verified.json` (with the recipe and both hashes) and
`certificate.drat.gz`. The CNF is not stored; it is rebuilt from the frozen ledger row and
the recorded recipe, and `input_sha256` in the table is what it must hash to.

If the goal is a solver benchmark rather than a study, the CNFs alone are the right
artefact — 3.5 MB each, and the generator in the solver package regenerates them exactly.
