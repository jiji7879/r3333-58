"""Path bootstrap for the extracted package (read-only use of its modules)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INP = HERE.parent / 'source'
NEXT = INP / 'next'
HS = INP / 'hard-study'
HM = INP / 'hard-more'
for p in (str(NEXT), str(HS), str(HM), str(HS / 'encoder')):
    if p not in sys.path:
        sys.path.insert(0, p)
