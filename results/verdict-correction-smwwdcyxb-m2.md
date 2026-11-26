# Erratum: m2's accepted entrance scope

During the final handoff cross-check I found a **scope bookkeeping error in my
earlier m2 verdict**. It incorrectly listed all three of `TT:2`, `TT:3` and
`UT:3` as complete, and therefore stated 1,800 accepted cases. **This was my
error, caught here independently of the member's report.**

The actual manifest and residual table, rechecked in full, contain:

| family | stored and replayed | OPEN | coverage consequence |
| --- | ---: | ---: | --- |
| `TT:2:5,5,5` | 600 | 0 | complete T/T, entrance in the 13-class |
| `TT:3:5,5,5` | 443 | 157 | partial T/T, entrance in the 12-class |
| `UT:2:5,5,5` | 596 | 4 | partial U/T, entrance in the 13-class |
| `UT:3:5,5,5` | 600 | 0 | complete U/T, entrance in the 12-class |
| `UU:2:5,5,5` | 591 | 9 | partial U/U, entrance in the 13-class |
| `UU:3:5,5,5` | 0 | 600 | entirely open U/U, entrance in the 12-class |

Consequently there are **two complete families and 1,200 accepted cases**, not
three families and 1,800. The earlier statement that T/T was certified for both
small classes must be withdrawn. In particular no-entrance-with-a-16-brace is
not established for T/T in the 12-class, nor for any whole template pair at an
arbitrary root.

The accurate unchanged statement is that **2,830 distinct stored proofs**
replay successfully with matching CNF and proof hashes. That is a verification
of the stored case certificates; completeness of a *family* of 600 normalized
cases is a separate requirement and was what the earlier verdict got wrong.
The partial-family certificates remain valid data but do not enlarge the
complete theorem. Counts are pinned by
`entrance-brace-audit-2026-11-26/accepted-scope.json`, mechanically checked
against the manifest and residual table.

The original platform verdict is a recorded action, not something I can rewrite
by relabelling this note as another verdict. This explicit later erratum and the
corrected handoff supersede its scope wording for future work. No frozen row or
ticket branch is thereby closed, and no Ramsey bound changes.
