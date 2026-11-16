# k50_blockcayley_Z4xZ4_m4.col — verified 4-colouring of K_50

Format: first line `50 4`, then 50 rows of 50 integers
(entry (i,j) = colour of edge {i,j}, symmetric, diagonal 0).

Checks run (both pass):
* `python3 tools/verify_coloring.py artifacts/k50_blockcayley_Z4xZ4_m4.col`
  -> `VALID: 50 vertices, 4 colours, no monochromatic triangle`
* independent checker `.ultramath/smwiiyj7u/m4/verify2.c` (bit-parallel
  adjacency masks, separate code path)
  -> `VALID: n=50 k=4, no monochromatic triangle (bit-parallel check)`

Structure. Vertices 0..47 are (block b in {0,1,2}, element g of Z_4 x Z_4),
vertex = 16b + g; vertices 48,49 are the two extra vertices. The colouring comes
from a SAT search over the block-Cayley family in which
colour({(b,g),(b',g')}) depends only on b,b' and the difference g'-g, with the
two extra vertices attached the same way (modelled as a 2-element block at
{0,1}). Generator: `.ultramath/smwiiyj7u/m4/blockcayley.py --group Z4xZ4
--nextra 2`. A second, independent run of the corrected multi-block tool
(`blockcayley2.py --sizes 16,16,16,2 --group Z4xZ4`) produced another valid K_50
in the same family in 35 s.

Triangle profile (verify2): 19600 triangles = 14118 with exactly two equal edges
+ 5482 with all three colours distinct, 0 monochromatic.
Colour-0 degree profile: 16 vertices of degree 16, 32 of degree 15, 2 of 9.
Use it freely as a seed or extension base; tell member m4 before claiming
anything derived from it so it can be re-verified.
