#!/usr/bin/env python3
"""Export an exact historical full-root stock parent, without productive rules."""
import argparse
import hashlib
from pathlib import Path
import two5_encoder


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rank', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert 1 <= args.rank <= 1300
    record, row, raw = two5_encoder.original(args.rank)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as stream:
        stream.write(raw)
    assert hashlib.sha256(raw).hexdigest() == record['input_sha256']
    print('{'+'"rank": %d, "id": "%s", "input_sha256": "%s"}' %
          (args.rank, record['id'], record['input_sha256']))


if __name__ == '__main__':
    main()
