#!/usr/bin/env python3
"""Add `--only-small` to k58-batch.sh, so the seven small profiles can be
first-passed without re-scanning the large ones.

    python3 patch_batch_only_small.py [path/to/k58-batch.sh]

Default path is ~/k58-solver/k58/k58-batch.sh. Idempotent: running it twice is
harmless. It edits three places and refuses to guess — if an anchor is missing it
says so and changes nothing.
"""
import os, sys, pathlib

USAGE_OLD = "# Options: --shards N --workers W --min-free-gb G --include-small --limit N --dry-run"
USAGE_NEW = ("# Options: --shards N --workers W --min-free-gb G --include-small --only-small\n"
             "#          --limit N --dry-run")

DEFAULTS_OLD = 'SHARDS=4; WORKERS=4; MIN_FREE=20; INCLUDE_SMALL=0; LIMIT=""; DRY=0'
DEFAULTS_NEW = 'SHARDS=4; WORKERS=4; MIN_FREE=20; INCLUDE_SMALL=0; ONLY_SMALL=0; LIMIT=""; DRY=0'

OPT_OLD = '  --min-free-gb) MIN_FREE=$2; shift 2;; --include-small) INCLUDE_SMALL=1; shift;;'
OPT_NEW = ('  --min-free-gb) MIN_FREE=$2; shift 2;; --include-small) INCLUDE_SMALL=1; shift;;\n'
           '  --only-small) ONLY_SMALL=1; shift;;')

PROFILES_OLD = 'profiles() { printf \'%s\\n\' "${BIG[@]}"; [ "$INCLUDE_SMALL" = 1 ] && printf \'%s\\n\' "${SMALL[@]}"; true; }'
PROFILES_NEW = ('profiles() {\n'
                '  if [ "$ONLY_SMALL" = 1 ]; then printf \'%s\\n\' "${SMALL[@]}"; return 0; fi\n'
                '  printf \'%s\\n\' "${BIG[@]}"; [ "$INCLUDE_SMALL" = 1 ] && printf \'%s\\n\' "${SMALL[@]}"; true; }')

NOTE_OLD = '  [ "$INCLUDE_SMALL" = 0 ] && echo && echo "(seven small profiles excluded; add --include-small to include them)"'
NOTE_NEW = ('  if [ "$ONLY_SMALL" = 1 ]; then\n'
            '    echo\n'
            '    echo "(only the seven small profiles; --only-small overrides --include-small)"\n'
            '  elif [ "$INCLUDE_SMALL" = 0 ]; then\n'
            '    echo\n'
            '    echo "(seven small profiles excluded; add --include-small to include them,"\n'
            '    echo " or --only-small to run just those)"\n'
            '  fi')

EDITS = [("usage line", USAGE_OLD, USAGE_NEW),
         ("defaults", DEFAULTS_OLD, DEFAULTS_NEW),
         ("option parsing", OPT_OLD, OPT_NEW),
         ("profiles()", PROFILES_OLD, PROFILES_NEW),
         ("plan note", NOTE_OLD, NOTE_NEW)]

def main():
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                        else os.path.expanduser("~/k58-solver/k58/k58-batch.sh"))
    if not path.exists():
        sys.exit(f"no such file: {path}  (pass the path to k58-batch.sh)")
    text = path.read_text()
    if "--only-small" in text:
        print(f"{path}: already patched (--only-small present); nothing to do")
        return
    out = text
    for name, old, new in EDITS:
        if out.count(old) != 1:
            sys.exit(f"{path}: anchor for {name} occurs {out.count(old)} times, expected 1; nothing written")
        out = out.replace(old, new)
    tmp = path.with_suffix(".patched")
    tmp.write_text(out)
    path.write_text(out)
    tmp.unlink(missing_ok=True)
    print(f"{path}: patched — added --only-small")
    print("usage:  ./k58-batch.sh plan --only-small --dry-run")
    print("        ./k58-batch.sh run  --only-small --shards 4 --workers 12")

if __name__ == "__main__":
    main()
