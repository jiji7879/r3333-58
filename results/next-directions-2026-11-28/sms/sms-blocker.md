# Native upstream SMS: prerequisite audit and exact blocker

**Verdict: native SMS cannot be built in this VM from the reviewed pinned source
and existing local prerequisites. No stock SMS binary was built, run, or claimed.
Nothing below was worked around; the experiment proceeded with an explicitly
labelled reimplementation (see `README.md`).**

## Pinned source

```
path  .ultramath/smx04thj8/m2/sources/sms-repo   (read-only use; not modified)
HEAD  63958bd09a871e484c59270a1d0f22d482dc5770   (matches the reviewed commit)
```

`src/CMakeLists.txt` requires

```
find_package(Boost 1.74.0 REQUIRED COMPONENTS program_options graph)
```

and

```
find_library(CADICAL_LIBRARY NAMES cadical
             HINTS "${CMAKE_CURRENT_SOURCE_DIR}/../cadical_sms/build/")
if (NOT CADICAL_LIBRARY) message(FATAL_ERROR "CaDiCaL not found")
```

## Blocker 1 — Boost is absent

Searched the whole filesystem (`find / -maxdepth 7`):

| probe | result |
|---|---|
| `/usr/include/boost/version.hpp` | absent |
| any `*/boost/version.hpp` | absent |
| `libboost_program_options*` | absent |
| `libboost_graph*` | absent |

Neither `program_options` nor `graph` is present, header or library. There is no
`sudo`, no package manager use is permitted, and installing Boost would be a
global package installation to obtain a performance headline, which the campaign
rules exclude. Building Boost locally would also exceed this member's 30-minute
local CPU budget on its own.

## Blocker 2 — the `cadical_sms` submodule is empty

```
$ ls -A .../sms-repo/cadical_sms | wc -l
0
$ cat .../sms-repo/.gitmodules
[submodule "cadical_sms"]
        path = cadical_sms
        url = https://github.com/markirch/cadical_sms.git
```

SMS links a *specially adapted* CaDiCaL, not the stock solver. Even with Boost
present, `libcadical.a` would have to be cloned and built from a repository that
is not in the reviewed local tree. Neither the pin nor a review of that
repository exists here.

## Toolchain that *is* available

```
cmake 4.2.3        (satisfies cmake_minimum_required 3.12)
g++ (conda-forge gcc 16.2.0-7), C++20 capable
```

So the compiler and CMake are not the blocker; Boost and `cadical_sms` are.

## Smallest approval that would unblock a real SMS run

1. Approval to install **Boost >= 1.74 with the `program_options` and `graph`
   compiled components** (system or a pinned source build under this member's
   own directory), and
2. Approval to clone and build **`github.com/markirch/cadical_sms`** at a
   reviewed commit, recorded with its SHA, into this member's scratch directory
   (no binaries committed).

Both are outside what this run may do unilaterally. Nothing in the reported
result depends on either: the substitute generator is clearly labelled, and the
A/B only ever solved the *original* parent+cube, never an SMS-emitted verdict.

## What was done instead

`gen.py` implements a bounded one-colour lex-leader certificate enumeration over
the same candidate group, with every emitted clause independently re-verified by
`verify_clauses.py`. It is described as a substitute, not as SMS: it does not
reproduce SMS's minimality search, its learned-clause policy, its
`--sym-break-clauses` witness format, or its CaDiCaL integration.
