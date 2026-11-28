"""Check that the Lean literal `sender18Atoms` equals the emitted atom list of
the first arm-1 support event in lean/K58/TargetSuffix.lean."""
import ast, json, pathlib, re
REPO = pathlib.Path(__file__).resolve().parents[3]
suf = (REPO / "lean/K58/TargetSuffix.lean").read_text()
tail = suf.split("emittedSupportStep\n    12343 11965 16 112 12455 (listAtoms ", 1)[1]
emitted = ast.literal_eval(tail.split(")", 1)[0].replace(" ", ","))
body = (REPO / "lean/K58/SupportTransport.lean").read_text()
lits = re.findall(r"sender18Atoms : Nat → Nat :=\s*listAtoms \[([^\]]*)\]", body, re.S)
lean = [int(x) for x in lits[0].replace(",", " ").split()] if lits else []
res = {"emitter_atoms": emitted, "lean_literal": lean,
       "match": emitted == lean,
       "guard_of_first_event": 11965, "n": 16, "k": 112}
print(json.dumps(res, indent=2))
(pathlib.Path(__file__).resolve().parent / "sender18-transcription.json").write_text(
    json.dumps(res, indent=2) + "\n")
assert res["match"], "transcription mismatch"
