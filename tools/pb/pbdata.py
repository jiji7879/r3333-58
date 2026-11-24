"""Data for the singleton-perfect-balance codegree cases (K58).

Colours: 0 = blue, 1 = green, 2 = yellow, 3 = red.  The two 16x16 matrices
below are the arm colourings of the two triangle-free 3-colourings of K16;
their digits are 0/1/2 only (no red inside an arm).  Verified here: both
symmetric, triangle-free, and 5-regular in each of the three colours at every
vertex.  Transcribed from
attachments/see-what-you-can-yel5/K58_PB_parallel_handoff.md (h2 templates).
"""

U = [
    '.011222102010120',
    '0.11221220101002',
    '11.0212201022001',
    '110.122210200210',
    '2221.01101200201',
    '22120.1110022010',
    '212211.020010102',
    '1222110.02101020',
    '02010120.0112221',
    '201010020.112212',
    '0102200111.02122',
    '10200210110.1222',
    '012002012221.011',
    '1002201022120.11',
    '20010102212211.0',
    '021010201222110.',
]

T = [
    '.011222102010120',
    '0.11212220102001',
    '11.0221201021002',
    '110.122210200210',
    '2221.01101200201',
    '21220.1120012010',
    '221211.010020102',
    '1222110.02101020',
    '02010210.0111222',
    '201010020.112212',
    '0102200111.02122',
    '10200120110.2221',
    '021002011222.011',
    '1002201022120.11',
    '20010102212211.0',
    '012010202221110.',
]


# The four rows surviving the catalogue at M = 14: (name, template, private labels D).
# Both copies use the same template and the identification on the 14 shared labels
# is the identity, so the pins below are exactly two copies of M glued along the
# complement of D.
ROWS = [
    ('UU_d02', 'U', (0, 2)),
    ('TT_d02', 'T', (0, 2)),
    ('TT_d04', 'T', (0, 4)),
    ('TT_d12', 'T', (1, 2)),
]

# cell sizes of the 38 outside sites, keyed by (colour to u, colour to v),
# as a function of t in 1..5 (the handoff, "The 38 outside sites").
def cells(t):
    return {(0, 0): 0, (0, 1): 5, (0, 2): 5,
            (1, 0): 5, (1, 1): 9 - t, (1, 2): t,
            (2, 0): 5, (2, 1): t, (2, 2): 9 - t}
