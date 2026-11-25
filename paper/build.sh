#!/usr/bin/env bash
# Build the manuscript outside the source directory, then publish only its PDF.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
BUILD="$ROOT/.scratch/manuscript/latex"
mkdir -p "$BUILD" "$ROOT/.scratch/manuscript/tmp"
export TMPDIR="$ROOT/.scratch/manuscript/tmp"
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$BUILD" main.tex
cp "$BUILD/main.pdf" main.pdf
printf 'Built %s\n' "$PWD/main.pdf"
