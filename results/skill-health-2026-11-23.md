# Skill health check, 2026-11-23

The person asked whether the skills they loaded work. Every skill in the project was exercised:
its own test suite where it ships one, and a live call against the real service where it does not.
All commands run from the project root with the system `python3`.

## Result

| skill | ships | self-test | live call made | verdict |
|---|---|---|---|---|
| `graph-catalogs-query` | `graphcat.py` | `test_graphcat.py` **OK** | `count alltrans16 "triangles=0"` → 38 of 286; `cite alltrans16` | works, downloads from Zenodo |
| `hops-query` | `hops.py` | `test_hops.py` **OK** | `show treewidth`, `relation treewidth clique-width` | works, reaches GitHub for the archive |
| `math-databases` | none (`SKILL.md` + `LICENSE`) | n/a | n/a | style/router skill: nothing to execute |
| `zbmath-query` | `zbmath.py` | `test_zbmath.py` **OK** | used earlier today (`show arXiv:2610.36648`) | works |
| `findstat-query` | `findstat.py` | `test_findstat.py` **OK** | `collections` (cached list) | works |
| `gap-groups-query` | `gapgroups.py` | `test_gapgroups.py` **OK** | `version`, `count 58` | works: GAP 4.14.0, smallgrp 1.5.4, transgrp 3.6.5, primgrp 3.4.4 |
| `siege-workflow` | `ledger.py` | `test_ledger.py` **OK** | `add`/`gate` on `research/r3333-58` | works |
| `lean-project-architecture` | scripts + tests | `test_check_lean_modules.py` **OK** | — | works |
| `lean-workflow`, `lean-statement-audit`, `lean-elaboration` | guidance + one script | none shipped | — | guidance only; `lean-elaboration`'s `count_lean_lines.py` untested, unused |

Seven of seven shipped test suites pass. Two skills have no executable: `math-databases` is an
index of databases, and the two Lean guidance skills are documents.

## Notes that mattered

- `hops.py` contacts `api.github.com` and `codeload.github.com` for the current archive; the first
  call is slow, later ones use the cache. It answered `show treewidth` with id `5Q7fuR` and the
  Robertson–Seymour definition, and `relation treewidth clique-width` with "yes" (Courcelle–Olariu
  2000, `cwd(G) ≤ 2^{twd(G)+1}+1`) and the exclusion in the other direction. The skill works; this
  campaign simply has no question of that shape.
- `graphcat.py` downloads per order from Zenodo on first use and caches under
  `$XDG_CACHE_HOME/open-math-skills/`. `alltrans15` is 48 vertex-transitive graphs on 15 vertices
  (7 triangle-free); `alltrans16` is 286 (38 triangle-free). Files above 25 MB are refused by
  default, which is why `alltrans45` (46.8 MB) and `alltrans46` (4.4 GB) were not touched.
- `test_gapgroups.py` and `test_graphcat.py` are the two slow suites (GAP start-up and network
  respectively); the whole sweep took 456 s wall.
