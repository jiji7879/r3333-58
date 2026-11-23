"""Check the registered declarations against the axiom output of the build."""
from pathlib import Path
import argparse
import re

ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("lean_dir", type=Path)
parser.add_argument("build_log", type=Path)
args = parser.parse_args()
source = args.lean_dir / "K58"
expected = re.findall(r"^#print axioms (K58\.[\w.']+)$", (source / "Check.lean").read_text(), re.M)
log = args.build_log.read_text()
if re.search(r"\berror(?:\([^)]+\))?:|sorryAx", log):
    raise SystemExit("build error or placeholder in transcript")
records = re.findall(r"'([\w.']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", log)
seen = set()
for decl, axioms in records:
    found = {name.strip() for name in axioms.split(",") if name.strip()}
    if found - ALLOWED:
        raise SystemExit(f"unexpected axioms for {decl}: {found - ALLOWED}")
    seen.add(decl)
if missing := set(expected) - seen:
    raise SystemExit(f"missing declarations: {sorted(missing)}")
def strip_comments_and_strings(text):
    """Remove Lean comments and string literals, keeping line structure.

    The eight-character scan below must see proof tokens, not prose: this tree
    documents in comment headers that it uses neither `sorry` nor
    `native_decide`, and a substring scan over the raw file rejects it for it.
    Nesting of `/- -/` blocks is honoured; `--` runs to end of line; string
    literals are dropped whole.
    """
    out = []
    i, depth, n = 0, 0, len(text)
    while i < n:
        c = text[i]
        if depth:
            if text.startswith("/-", i):
                depth += 1; i += 2; continue
            if text.startswith("-/", i):
                depth -= 1; i += 2; continue
            out.append("\n" if c == "\n" else " ")
            i += 1; continue
        if text.startswith("/-", i):
            depth = 1; i += 2; continue
        if text.startswith("--", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1
            continue
        out.append(c); i += 1
    if depth:
        raise SystemExit("unterminated block comment")
    return "".join(out)

TOKEN = re.compile(r"\b(sorry|native_decide|admit)\b")
for path in sorted(source.glob("*.lean")):
    if TOKEN.search(strip_comments_and_strings(path.read_text())):
        raise SystemExit(f"unpermitted proof token in {path}")
print(f"{len(expected)} registered K58 declarations checked")
print(f"{len(seen)} distinct declarations with axiom records in the supplied log")
print("Every reported axiom list is a subset of [propext, Classical.choice, Quot.sound].")
print("The K58 sources passed the placeholder scan.")
