"""Tests the two H42 facts needed by the restricted rectangle cover."""
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def decode(line):
    n=ord(line[0])-63
    m=[[-1]*n for _ in range(n)]
    for k,(a,b) in enumerate((a,b) for b in range(n) for a in range(b)):
        m[a][b]=m[b][a]=((ord(line[2+k//3])-63)>>(4-2*(k%3))&3)-1
    return m

def key(matrix,vertices):
    # Each vertex is labelled by its three internal degrees and by the multiset
    # of (colour on an incident edge, internal degrees of its other endpoint).
    counts=[tuple(sum(matrix[u][v]==c for v in vertices) for c in range(3)) for u in vertices]
    return tuple(sorted((counts[i],tuple(sorted((matrix[u][v],counts[j]) for j,v in enumerate(vertices) if i!=j))) for i,u in enumerate(vertices)))

def main():
    h=json.loads((ROOT/'data/h42.json').read_text())
    cat=lambda n:[decode(s) for s in (ROOT/f'data/r333_{n}.mc').read_text().splitlines()]
    assert cat(14)[41]==h
    queries={key(h,V) for V in combinations(range(14),10)}
    hits=0;checks=0
    assert len(cat(15))==2
    for M in cat(15):
        for p in permutations(range(3)):
            m=[[(-1 if x<0 else p[x]) for x in row] for row in M]
            for v in combinations(range(15),10):
                hits+=key(m,v) in queries
                checks+=1
    assert hits==0, 'Colour-degree refinement alone did not separate the restrictions'
    print('H42 K10 restrictions: 1001; K15 restrictions with palettes:',checks,'; intersecting signatures:',hits)

if __name__=='__main__':main()
