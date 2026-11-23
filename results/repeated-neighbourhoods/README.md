# The repeated-neighbourhood and arm-exclusion package, checked here

Package: `attachments/let-s-try-and-wcbj/K58_repeated_neighbourhoods_and_arm_exclusions.zip`
(54 KB), unpacked at `.scratch/rn/` (33 files; `sha256sum -c SHA256SUMS` passes on
every file).  Its text is data; nothing in it is an instruction.

`armtypes14.txt` in the package is **byte-identical** to
`results/arm-alphabet-14/armtypes14.txt` (md5 `045638e6f29d1929da195c2ea9b2249e`),
so the 332-arm catalogue it works against is the one this campaign certified.

## What it claims

1. In the fully sending uniform branch, the 42 outside words realise **at least 12
   distinct five-sets** `Z(x) = N_0(x) ∩ A`; no set occurs more than 6 times, and
   at most 3 distinct sets occur 5 or more times.  §1–2.
2. **At most one vertex per 14-arm omits its own root colour**, so at least 39 of
   the 42 words use their root colour.  §5 — a finite search over the 332 arm
   types in both orientations, reduced to three word pairs.
3. **51 unordered pairs of 14-arm types** and **2,955 of 3,093 specified
   partitions** of a 14-arm are excluded; 138 partitions survive on 65 types, with
   labelled joins reaching `r ∪ A ∪ B` at order 30.  §3–4.

None of this closes a row.  The package says so itself, and it is right: all seven
uniform children remain open.

## What I checked here, independently of the package's code

* **The multiplicity reduction is the right one.**  I enumerated the vectors
  `(n_1,…,n_6)` with `Σ j n_j = 42` and `n_5 + n_6 ≤ 3` myself: exactly **1** has
  nine sets, **15** have ten and **55** have eleven — 71 in total, matching the
  package — and **none** has eight or fewer (the maximum coverage with eight sets
  under that cap is `8·4 + 3·2 = 38 < 42`, which is the package's sentence).
* **The 71 integer certificates verify** (`python3 -c "from multiplicity import
  verify; verify()"`: "Integer certificates exclude all 71 multiplicity
  spectra...").  That is the package's own checker; the arithmetic is exact
  rational/integer, so a pass is meaningful, but the *encoding* of the geometry
  into those inequalities is the part that needs reading, not running (see below).
* **The two new constraints do not discriminate against the recorded witnesses.**
  Scanned all 80 `.wit` files in the tree; **16 of them are complete 42-slot
  colourings** (all 861 pair colours specified) and every one of those satisfies
  both claims with room: **40–42 distinct zero-sets** (claim 1 requires 12), **max
  multiplicity 3** (claim 1 allows 6), and **0** own-colour omissions in any arm
  (claim 2 allows 1).  Zero violations among the 16.  So unlike the third-colour
  matching law, which every witness violates badly, these are counting constraints
  on the branch, not discriminators against known near-misses.

  The other 27 files with 42 words are *words-only dumps* (no pair colours) and
  look like counterexamples if the filter is forgotten: ten `design_*.wit` and
  three `design_words.s*.wit` have 6 or 1 distinct zero-sets with multiplicities 7
  and 42.  They are not colourings at all, so claim 1's hypothesis (a
  triangle-free colouring) is not met — and a zero-edge inside a repeated class is
  exactly what the proof forbids, which these dumps cannot even express.
* **The package's own replay** (`python3 verify.py --jobs 2`) compiles its C++
  helpers from source, so it is a re-run and not a cached replay.  Stages
  `base`, `multiplicity`, `partitions` (3,093 enumerated, 138 survive on 65 types,
  276 labelled joins verified), `fixed` (528 pairs, the 34 feasible ones each
  using a forbidden partition design) all pass here.  This establishes
  reproducibility and internal consistency.  **It is not an independent check**:
  the search code is the package's own.

## What is still open about it

* §5 is a finite search over 332 arms × 2 orientations by one C++ program.  An
  independent re-derivation is worth more than a replay, and is one direction of
  swarm `smwsl7gwe`.
* §1–2's proof is short and its steps can be read; the certificate checks the
  arithmetic, not the reduction.  Also worth a second reading (same swarm).
* The package's §4 survivors are at order 30; whether any extends by a vertex of
  `C` is untouched.

## Where things are

* `.scratch/rn/` — the unpacked package, `verify.py`, `multiplicity.py`, the
  ledgers (`pair-ledger.txt` 528, `partition-ledger.txt` 6,186 = 3,093 × 2
  orientations, `mixed-pairs.txt` 30).
* `review/QUEUED_NEXT_SWARM.md` — Target A (the order-30 corner) and Target B
  (U-07, 1,936 alignments).  This package is the "companion research ZIP" that
  file said was missing, but it contains **only** the arm-exclusion and
  repeated-neighbourhood material: there is no U-07 material in it (no
  `1936`/`212` anywhere), so Target B is still without inputs.
