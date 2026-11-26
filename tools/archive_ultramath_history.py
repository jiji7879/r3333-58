#!/usr/bin/env python3
"""Archive bounded text/witness material from completed Ultramath workspaces.

This command READS workspaces and writes a checked archive plus inventories.
It never deletes workspaces. Files with explicit DRAT/LRAT suffixes are
excluded by name; their paths and sizes remain in the raw-file index. This is
not a claim to recognize every possible proof-bearing format.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import tarfile

TEXT_SUFFIXES = {
    ".md", ".py", ".lean", ".c", ".cc", ".cpp", ".h", ".sh", ".json",
    ".jsonl", ".txt", ".tsv", ".csv", ".yaml", ".yml", ".toml", ".col",
    ".g6", ".graph6", ".proof", ".cert", ".log", ".model", ".cnf",
    ".dimacs", ".tex", ".bib", ".m", ".gap", ".gp", ".sage", ".sql",
}
RAW_SUFFIXES = (".drat", ".drat.gz", ".lrat", ".lrat.gz", ".lrat.xz")
MAX_BYTES = 4 * 1024 * 1024


def kind(name):
    low = name.lower()
    for suffix, label in [(".drat.gz", "drat.gz"), (".drat", "drat"),
                          (".lrat.xz", "lrat.xz"), (".lrat.gz", "lrat.gz"),
                          (".lrat", "lrat"), (".cnf", "cnf"),
                          (".olean", "oleans"), (".pyc", "pyc")]:
        if low.endswith(suffix):
            return label
    return Path(low).suffix or "<no suffix>"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.ultramath')
    parser.add_argument('--out', required=True)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--exclude', action='append', default=[], metavar='SWARM',
                        help='live or otherwise retained swarm directory (repeatable)')
    args = parser.parse_args()
    root = Path(args.root)
    assert root == Path('.ultramath'), 'this tool only scans the project Ultramath root'
    out, archive = Path(args.out), Path(args.archive)
    out.mkdir(parents=True, exist_ok=True)
    if archive.exists() or Path(str(archive) + '.next').exists():
        raise SystemExit(f'refusing to overwrite {archive}')
    swarms = sorted(p for p in root.iterdir()
                    if p.is_dir() and not p.is_symlink() and p.name.startswith('smw')
                    and p.name not in set(args.exclude))
    selected, records, summaries = [], [], []
    for swarm in swarms:
        size = allocated = 0
        kinds = {}
        for directory, dirs, files in os.walk(swarm, followlinks=False):
            for filename in files:
                p = Path(directory, filename)
                if p.is_symlink() or not p.is_file():
                    continue
                st = p.stat()
                entry = {'swarm': swarm.name, 'path': str(p), 'bytes': st.st_size,
                         'allocated_bytes': st.st_blocks * 512,
                         'mtime_ns': st.st_mtime_ns, 'kind': kind(filename)}
                size += st.st_size
                allocated += entry['allocated_bytes']
                fam = kinds.setdefault(entry['kind'], [0, 0])
                fam[0] += 1
                fam[1] += st.st_size
                data = p.open('rb')
                prefix = data.read(4096)
                data.close()
                is_text = (p.suffix.lower() in TEXT_SUFFIXES
                           and b'\0' not in prefix and not filename.lower().endswith(RAW_SUFFIXES))
                selected_this = is_text and st.st_size <= MAX_BYTES
                entry['preserved_in_archive'] = selected_this
                if selected_this:
                    entry['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
                    selected.append(p)
                records.append(entry)
        summaries.append({'swarm': swarm.name, 'bytes': size, 'allocated_bytes': allocated,
                          'families': dict(sorted(kinds.items()))})
    with gzip.open(str(out / 'raw-file-index.jsonl.gz.next'), 'wt', encoding='utf-8') as f:
        for entry in records:
            f.write(json.dumps(entry, sort_keys=True) + '\n')
    selected.sort(key=str)
    records_by_path = {entry['path']: entry for entry in records}
    next_archive = Path(str(archive) + '.next')
    with tarfile.open(next_archive, 'w:gz', compresslevel=6) as tf:
        for p in selected:
            data = p.read_bytes()
            stored = hashlib.sha256(data).hexdigest()
            entry = records_by_path[str(p)]
            assert entry['sha256'] == stored, p
            info = tf.gettarinfo(str(p), arcname=str(p))
            from io import BytesIO
            tf.addfile(info, BytesIO(data))
    checked = 0
    selected_by_path = {entry['path']: entry for entry in records}
    with tarfile.open(next_archive, 'r:gz') as tf:
        for member in tf:
            if not member.isfile():
                continue
            record = selected_by_path[member.name]
            assert hashlib.sha256(tf.extractfile(member).read()).hexdigest() == record['sha256']
            checked += 1
    assert checked == len(selected)
    digest = hashlib.sha256(next_archive.read_bytes()).hexdigest()
    os.replace(next_archive, archive)
    os.replace(str(out / 'raw-file-index.jsonl.gz.next'), out / 'raw-file-index.jsonl.gz')
    metadata = {
        'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'excluded_live_or_retained_swarms': sorted(args.exclude),
        'archive': str(archive), 'archive_sha256': digest,
        'archive_bytes': archive.stat().st_size,
        'files_archived': checked, 'raw_file_records': len(records),
        'includes_raw_drat_or_lrat': False,
        'selection': {'suffixes': sorted(TEXT_SUFFIXES), 'maximum_bytes_per_file': MAX_BYTES},
        'note': 'Archive is bounded source/text evidence, not raw-proof preservation. Index paths show original locations, not surviving local paths.',
    }
    (out / 'preservation.json').write_text(json.dumps(metadata, indent=2) + '\n')
    (out / 'inventory.json').write_text(json.dumps(summaries, indent=2) + '\n')
    rows = ['# Ultramath storage inventory', '',
            'This is an inventory, not a mathematical acceptance table. See the audited swarm reports for scope.', '',
            '| Swarm | File bytes (du -sb) | Allocated bytes | DRAT bytes |', '| --- | ---: | ---: | ---: |']
    for row in summaries:
        drat = sum(v[1] for k, v in row['families'].items() if k.startswith('drat'))
        rows.append(f"| `{row['swarm']}` | {row['bytes']:,} | {row['allocated_bytes']:,} | {drat:,} |")
    (out / 'INVENTORY.md').write_text('\n'.join(rows) + '\n')
    print(json.dumps(metadata, indent=2))
    print(f'{len(summaries)} old swarms inventoried; {checked} text/witness files archived and verified.')


if __name__ == '__main__':
    main()
