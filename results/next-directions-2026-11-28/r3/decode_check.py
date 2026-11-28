#!/usr/bin/env python3
"""Independent check of the 41-atom decode of the fifteen arm-1 counters.

Parses lean/K58/TargetSuffix.lean (the emitted suffix), finds the fifteen
`freshGuardedCounterStepAuto oldTop g 41 14 newTop (listAtoms [..])` counter
steps whose guard is read by the fifteen `emittedSupportStep` families, and
verifies, with an *independent* implementation of hostLexRank/hostVar, that

    atoms(sender 18+k) = [hostVar (1+j) (18+k) one | j < 16]
                      ++ [hostVar (18+k) (33+i) one | i < 25]

It also checks the allocation data (newTop = oldTop + 379, guard = oldTop+1,
support atoms = first sixteen counter atoms) and writes counter_literals.txt,
the list literal that R3Counter.lean transcribes.
"""
import re, sys
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[3] / 'lean' / 'K58' / 'TargetSuffix.lean')
src = open(SRC).read()

def hostLexRank(u, v):          # K58.TargetParent.hostLexRank
    return sum(57 - i for i in range(u)) + (v - u - 1)

def hostVar(u, v, c):           # K58.TargetParent.hostVar
    a, b = min(u, v), max(u, v)
    return 4 * hostLexRank(a, b) + c + 1

ONE = 1                          # K58.EmittedBridge.one : Fin 4 = <1, _>

num_list = re.compile(r'\[([0-9,\s]*)\]')
def steps(kind):
    pat = re.compile(kind + r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\(listAtoms\s+\[([0-9,\s]+)\]\)")
    return [(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)),
             int(m.group(5)), [int(x) for x in re.findall(r'\d+', m.group(6))])
            for m in pat.finditer(src)]

counters = steps("freshGuardedCounterStepAuto")
supports = steps("emittedSupportStep")
support_old = [s[0] for s in supports]
rows = [c for c in counters if c[4] in support_old]
ok = True
assert len(rows) == 15, len(rows)
for k, (oldTop, g, n, bound, newTop, atoms) in enumerate(rows):
    sender = 18 + k
    dec = ([hostVar(1 + j, sender, ONE) for j in range(16)] +
           [hostVar(sender, 33 + i, ONE) for i in range(25)])
    sup = [s for s in supports if s[0] == newTop][0]
    checks = {
        'n=41': n == 41, 'bound=14': bound == 14,
        'decode': dec == atoms,
        'newTop-oldTop=379': newTop - oldTop == 379,
        'guard=oldTop+1': g == oldTop + 1,
        'distinct': len(set(atoms)) == 41,
        'support_guard': sup[1] == g,
        'support_atoms=first16': sup[5] == atoms[:16],
        'support_stride': sup[4] == sup[0] + 112,
    }
    bad = [name for name, v in checks.items() if not v]
    ok &= not bad
    print(f"k={k:2d} sender={sender} oldTop={oldTop} newTop={newTop} "
          f"{'OK' if not bad else 'FAIL ' + ','.join(bad)}")
print("ALL CHECKS PASS:", ok)
assert ok
with open('counter_literals.txt', 'w') as f:
    f.write("[\n")
    for k, row in enumerate(rows):
        f.write("  [" + ", ".join(map(str, row[5])) + "]" + ("," if k < 14 else "") + "\n")
    f.write("]\n")
print("wrote counter_literals.txt in the current directory")
