# Independent finite recomputation for entry 17

Re-ran `decode_check.py` over the real `TargetSuffix.lean` from an isolated
scratch directory. It independently implements hostLexRank and hostVar, with
colour 1 (thus +2 in a DIMACS ID), rather than importing the theorem decoder.
For all k=0,...,14 it checked:
- exactly 41 atoms, bound 14; the intended edge-decoding for the sender 18+k;
- newTop-oldTop=379; guard=oldTop+1; 41 distinct IDs;
- matching support guard and first sixteen support atoms;
- support stride 112 for the emitted family.
Every line says OK. See `m7-extraction.log`.

Comparison was done against a parse of the literal table in the Lean module,
not just against itself: 15 rows × 41 integers are identically the same.
Receipt: `m7-transcription-check.json`. First and far edge decode checks also
match the arithmetic `4*((57+16))+2=294` and `4*911+2=3646`, with no reliance
on memory of those integers. Kernel claims themselves were checked by Lean,
documented separately in `13-lean.md`, not by this numerical replay.
