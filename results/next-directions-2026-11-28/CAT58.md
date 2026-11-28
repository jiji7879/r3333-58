# CAT58 and attachment bounds (verified)

Files: `lean/K58/CAT58.lean`, `lean/K58/Attachment.lean`, immediately after `DegreeCap` in `lean/order.txt`; `import K58.Attachment` in `lean/K58/Check.lean`. The integration-only import change is `import CAT58` -> `import K58.CAT58`.

Validated: full `bash lean/build.sh` (Lean 4.33.1) passed. See CAT58-build.txt.
Scope: exact structural theorem plus attachment bounds, not a census, wall-row closure, ChainReady, or Ramsey-bound change.
