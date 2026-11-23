---
name: gap-groups-query
description: "Identify a finite group from permutation generators or a GAP constructor, or look up and filter GAP's small, transitive and primitive groups."
metadata:
  display_name: "GAP Groups: Identify Finite Groups"
  category: "Databases"
  logo: "logos/gap.png"
  long_description: |-
    Identify a finite group from permutation generators or a name, look up any group of the Small
    Groups library (every group of order at most 2000 except 1024, and many more), count and
    filter the groups of an order, and look up transitive and primitive permutation groups.
    GAP's transitive labels are also used for LMFDB Galois groups. GAP runs locally through Sage.

    Data from the [SmallGrp](https://gap-packages.github.io/smallgrp/),
    [TransGrp](https://www.math.colostate.edu/~hulpke/transgrp) and
    [PrimGrp](https://gap-packages.github.io/primgrp/) libraries of
    [GAP](https://www.gap-system.org/) (open source; see each package's licence). Not affiliated
    with the GAP project.
---

# Identify and look up finite groups

Run `scripts/gapgroups.py` from this skill's directory (typically
`.skill/gap-groups-query/scripts/gapgroups.py` from the project root; use the directory returned
by `skills_load` if different), referred to as `gapgroups.py` below. It runs GAP through the
libgap of Sage or passagemath. Use a `python3` with that libgap and the SmallGrp, TransGrp and
PrimGrp data installed. Each invocation starts GAP.

```sh
python3 .skill/gap-groups-query/scripts/gapgroups.py identify "(1,2,3,4,5,6,7,8)" "(1,3)"   # one generator per argument
python3 .skill/gap-groups-query/scripts/gapgroups.py identify --group "PSL(2,7)"            # a named group
python3 .skill/gap-groups-query/scripts/gapgroups.py small 24 12                  # SmallGroup(24,12): structure and invariants
python3 .skill/gap-groups-query/scripts/gapgroups.py count 1024                   # how many groups of order 1024
python3 .skill/gap-groups-query/scripts/gapgroups.py list 64 center=4 nilpotency_class=3   # first 50 matches; --all for every one
python3 .skill/gap-groups-query/scripts/gapgroups.py transitive 8 48              # the transitive group 8T48
python3 .skill/gap-groups-query/scripts/gapgroups.py transitive 6 abelian=no solvable
python3 .skill/gap-groups-query/scripts/gapgroups.py primitive 8                  # the primitive groups of degree 8
python3 .skill/gap-groups-query/scripts/gapgroups.py version                      # GAP, the libraries, coverage and authors
```

Generators are permutations in cycle notation, each a product of disjoint cycles, one per
argument (`"(1,2)(3,4)" "(5,6)"`, or one argument `"[(1,2,3),(1,2)]"`). Separate points with
commas, omit fixed points, and write `()` for the identity. `--group` takes one of
SymmetricGroup, AlternatingGroup, CyclicGroup, DihedralGroup (GAP's argument is the order),
QuaternionGroup, ElementaryAbelianGroup, MathieuGroup, SL, GL, PSL, PGL, SU, PSU, GU, Sp, PSp,
SmallGroup, TransitiveGroup or PrimitiveGroup with integer arguments; give any other group by
generators. A filter is a property, optionally `=no` (`abelian`, `cyclic`, `nilpotent`,
`solvable`, `supersolvable`, `simple`, `perfect`, and `primitive` for transitive groups), or a
number (`center=`, `exponent=`, `classes=` for conjugacy classes, `derived_length=`,
`nilpotency_class=`, and `order=` for transitive and primitive groups).

## Look something up

1. To name a group you have, use `identify`. It gives the order, the invariants, and the
   SmallGroup id whenever the script prints one (GAP's IdGroup covers every order up to 2000
   except 512, 1024 and 1536). For a permutation group, the command checks the action on its
   moved points and reports a transitive label `nTk` and a primitive group number when
   applicable and available. Look up `8T48` with `transitive 8 48`.
   LMFDB is a separate question: its abstract group label `n.i` equals the SmallGroup id
   `[n, i]` for orders up to 2000 except 512, 1024, 1152, 1536 and 1920; the script prints the
   LMFDB link only then, and it works when LMFDB holds the group. A missing LMFDB link does not
   make the SmallGroup id less valid.
2. Different groups can share a readable GAP StructureDescription such as `(C4 x C2) : C2`.
   The symbols `:` and `.` stand for split and non-split extensions. Use the SmallGroup id for
   the abstract group. Use `nTk` or `PrimitiveGroup(n, k)` for the permutation action.
3. Use `count ORDER` for the total and `list ORDER FILTER ...` for a count and list of matches.
   Filtering examines every group of the order or degree. With over 60,000 groups only the
   unfiltered preview is available. `--all` is limited to library entries of at most 60,000 groups.
4. An empty filtered list in a covered order or degree means no group has those properties.
   Check `version` for SmallGroup and IdGroup availability through order 2000, transitive
   degrees, and standard primitive coverage. For larger SmallGroup orders, try the order
   directly or read the SmallGrp manual.

## Report

Name each group by its SmallGroup id, `nTk` label or primitive group number, with the order and
the invariants you used, and the GAP and library versions (`version`). Cite GAP (The GAP Group,
GAP – Groups, Algorithms, and Programming, with the version) and the library used. For TransGrp,
also use the upstream README's credit for the degree queried, including Cannon and Holt for
degree 32 and Holt and Royle for degrees 34–48.

Everything runs locally; nothing about your question leaves the project.

If a shell with `python3` is unavailable, report what is missing and stop. If libgap, a GAP
package, or data for an order or degree is unavailable, report the missing dependency or
coverage. The libgap error names the passagemath packages. Ask before installing them. For an
LMFDB record or a Galois group attached to a number field, use `lmfdb-query`.
