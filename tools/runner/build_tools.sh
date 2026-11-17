#!/usr/bin/env bash
# Build the pinned solvers into ./bin.
set -euo pipefail
cd "$(dirname "$0")"
KISSAT_COMMIT=8af8e56f174b778aef3aa45af9f739b2a5f492c2
DRAT_COMMIT=2e3b2dc0ecf938addbd779d42877b6ed69d9a985
mkdir -p bin src
if [ ! -x bin/kissat ]; then
  [ -d src/kissat ] || git clone -q https://github.com/arminbiere/kissat.git src/kissat
  git -C src/kissat checkout -q "$KISSAT_COMMIT"
  ( cd src/kissat && ./configure >/dev/null && make -j"$(nproc)" >/dev/null )
  cp src/kissat/build/kissat bin/kissat
fi
if [ ! -x bin/drat-trim ]; then
  [ -d src/drat-trim ] || git clone -q https://github.com/marijnheule/drat-trim.git src/drat-trim
  git -C src/drat-trim checkout -q "$DRAT_COMMIT"
  # the shipped Makefile does not build with modern gcc; these flags do
  cc -std=c99 -D_GNU_SOURCE -O2 -o bin/drat-trim src/drat-trim/drat-trim.c
fi
echo "kissat:    $(bin/kissat --version)"
echo "drat-trim: $(realpath bin/drat-trim)"
