#!/usr/bin/env python3
"""Compare the 775 exact-11 high masks with the attached 210 four-low masks.

This is a coding/identity comparison only. It does not certify the newer
exclusions or raise a directional bound. Paths may be relative to the repo.
"""
import argparse
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h5', type=Path,
                        default=Path('.ultramath/smwxbvh79/m1/source/K58_wall_H5'))
    parser.add_argument('--rise', type=Path,
                        default=Path('.scratch/hrise-audit/K58_wall_H_rise'))
    parser.add_argument('--receipt', type=Path,
                        default=Path('.ultramath/smwxbvh79/m1/h11-link-receipt.json'))
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.h5.resolve()))
    from layer import use_base
    use_base(args.h5 / 'base')
    from portable import image, identify
    from gluing import automorphisms

    frontier = args.rise / 'results/next-low-orbits.tsv.gz'
    with gzip.open(frontier, 'rt') as stream:
        rows = [r for r in csv.DictReader(stream, delimiter='\t')
                if r['row_id'].startswith('0404')]
    assert len(rows) == 26
    low = {int(m) for row in rows for m in row['low_template_masks'].split(',')}
    assert len(low) == 210
    old = json.loads(args.receipt.read_text())
    partial = old['exact11_partial']
    actions = [g for g in automorphisms(16, 'U') if g[0] == 0]
    assert len(actions) == 10

    # The bit positions are source indices 1..15, not Python array positions
    # 0..14. In particular, never use (1<<15)-1 for this complement.
    complement = sum(1 << i for i in range(1, 16))
    assert complement == 65534
    assert all(m & 1 == 0 and m.bit_count() == 4 for m in low)
    assert all({image(m, g) for g in actions} <= low for m in low)
    rho = partial['rows'][0]['row_id']
    key, _, _, _, _, masks = identify(args.h5 / 'base', rho, weight=11)
    assert key == 'a9ed9506b66e66226d295a874f3502b06b72ec7997b7af925edfd3e436bc1cd3'
    assert len(masks) == 1365
    assert low <= {complement ^ m for m in masks}
    new_high = {complement ^ m for m in low}
    new_high_reps = {min({complement ^ image(m, g) for g in actions})
                     for m in low}
    assert len(new_high_reps) == 26

    result = {
        'scope': '0404 exact-11 remaining high masks versus attached four-low frontier',
        'unverified': 'No new exclusion is replayed or raised to a bound by this comparison.',
        'normalized_spec': key,
        'inputs': {'frontier': str(frontier), 'frontier_sha256': sha(frontier),
                   'receipt': str(args.receipt), 'receipt_sha256': sha(args.receipt)},
        'bit_positions': 'source vertices 1..15; bit 0 unused',
        'relation': 'low_mask = 65534 xor high_mask',
        'old_unresolved_masks_per_row': 775,
        'new_low_masks': len(low), 'new_low_orbits': len(rows),
        'new_complement_contained_old': True,
        'older_masks_no_longer_remaining_given_new_exclusions': 565,
        'remaining_if_new_exclusions_are_verified': 210,
        'old_representatives_remaining_if_new_exclusions_are_verified': 63,
        'rows': {},
    }
    targets = [r for r in partial['rows'] if r['row_id'].startswith('0404')]
    assert len(targets) == 1
    for row in targets:
        high = set(row['unresolved_masks'])
        assert len(high) == 775
        assert new_high < high
        old_reps = {min({image(m, g) for g in actions}) for m in high}
        assert len(old_reps - new_high_reps) == 63
        result['rows'][row['row_id']] = {
            'new_complement_contained_old': True,
            'mask_difference': 565,
            'orbit_representative_difference': 63,
        }
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    print(text, end='')
    if args.out:
        args.out.write_text(text)


if __name__ == '__main__':
    main()
