#!/usr/bin/env python3
"""Build a new archive, never replacing the supplied base or source inputs.

Usage: python3 build_updated.py --base dist/k58-solver.zip \
  --square attachments/.../K58_square_spoke_wall_test.zip
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SQUARE_SHA = '08a1e2e9513ade7dffab4d8ff89fb5f2f5dc04e68d8928ff8cf54cded9093873'


def sha(path):
    hash_ = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            hash_.update(chunk)
    return hash_.hexdigest()


def safe_extract(archive, root):
    root = root.resolve()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            ref = (root / info.filename).resolve()
            if ref != root and root not in ref.parents:
                raise ValueError('unsafe ZIP member path')
            if info.is_dir() and '..' in Path(info.filename).parts:
                raise ValueError('unsafe ZIP member path')
        z.extractall(root)
        for info in z.infolist():
            if info.is_dir():
                continue
            # Python's extractall does not restore executable permissions.
            # Without these, the copied solver cannot launch its native binaries.
            mode = (info.external_attr >> 16) & 0o777
            target = root / info.filename
            if mode:
                target.chmod(mode)


def copy_tree(source, dest):
    shutil.copytree(source, dest, symlinks=True, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', '.DS_Store'))


def build(base, square, output):
    assert sha(square) == SQUARE_SHA, 'wrong square-spoke source archive'
    output = output.resolve()
    if output.exists():
        raise ValueError(f'refusing to overwrite {output}')
    workspace = REPO / '.scratch' / 'build-updated-solver'
    destination = REPO / 'dist'
    workspace.mkdir(parents=True, exist_ok=True)
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='build-', dir=workspace) as tmp:
        root = Path(tmp) / 'k58-solver'
        root.mkdir()
        safe_extract(base, root.parent)
        # The copy starts from the actual self-contained package, not from a
        # shared work tree that may contain another session's generated inputs.
        base_names = {}
        with zipfile.ZipFile(base) as z:
            assert z.testzip() is None
            for info in z.infolist():
                if not info.is_dir():
                    name = Path(info.filename)
                    assert name.parts and name.parts[0] == 'k58-solver', 'unexpected base ZIP prefix'
                    relative = name.relative_to('k58-solver').as_posix()
                    target = root / relative
                    assert target.exists(), 'base extraction missed a member'
                    base_names[relative] = hashlib.sha256(z.read(info)).hexdigest()
        safe_extract(square, root / 'square_spoke' / 'source')
        safe_extract(square, root / 'paired_arm' / 'source')
        copy_tree(REPO / 'tools/color-resolved-wallcc', root / 'color-resolved-wallcc')
        copy_tree(HERE / 'paired_arm/work', root / 'paired_arm' / 'work')
        copy_tree(HERE / 'unified', root / 'unified')
        copy_tree(HERE / 'square_spoke/tools', root / 'square_spoke')
        copy_tree(HERE / 'square_spoke/work', root / 'square_spoke' / 'work')
        shutil.copyfile(HERE / 'paired_arm/driver.py', root / 'paired_arm/driver.py')
        shutil.copyfile(HERE / 'square_spoke/driver.py', root / 'square_spoke/driver.py')
        shutil.copyfile(HERE / 'k58-updated.sh', root / 'k58.sh')
        shutil.copyfile(root / 'README.md', root / 'STOCK_README.md')
        shutil.copyfile(HERE / 'MODIFIED_README.md', root / 'README.md')
        shutil.copyfile(HERE / 'MODIFIED_README.md', root / 'MODIFIED_README.md')
        shutil.copyfile(HERE / 'UPDATES.md', root / 'UPDATES.md')
        shutil.copyfile(HERE / 'MASSIVE_VALIDATION.md', root / 'MASSIVE_VALIDATION.md')
        for script in ['k58.sh', 'square_spoke/driver.py', 'paired_arm/driver.py']:
            (root / script).chmod(0o755)
        assert (root / 'color-resolved-wallcc/tools/drat-trim').read_bytes() == (root / 'bin/drat-trim').read_bytes()
        assert (root / 'color-resolved-wallcc/bin/kissat').read_bytes() == (root / 'bin/kissat').read_bytes()
        assert 'STRENGTHENED_UNSAT_NOT_ORIGINAL_CLOSURE' in (root / 'square_spoke/driver.py').read_text()
        (root / '.scratch').mkdir(exist_ok=True)
        for script in ['square_spoke/driver.py', 'paired_arm/driver.py', 'unified/driver.py', 'unified/store.py',
                       *('paired_arm/work/' + n for n in (p.name for p in (HERE / 'paired_arm/work').glob('*.py'))),
                       *('square_spoke/' + n for n in (p.name for p in (HERE / 'square_spoke/tools').glob('*.py')))]:
            compile((root / script).read_text(), str(root / script), 'exec')
        check = subprocess.run(['bash', '-n', str(root / 'k58.sh')], capture_output=True)
        if check.returncode:
            raise RuntimeError(check.stderr.decode(errors='replace'))
        # Deliberate base changes are only the front door and the unread stock
        # manual's name; every input/checker/receipt is preserved byte-for-byte.
        for name, original_hash in base_names.items():
            if name in ('k58.sh', 'README.md'):
                continue
            assert sha(root / name) == original_hash, 'unexpected stock file modification: ' + name
        files = []
        for path in sorted(root.rglob('*')):
            if not path.is_file() or '__pycache__' in path.relative_to(root).parts or '.scratch' in path.relative_to(root).parts:
                continue
            relative = path.relative_to(root).as_posix()
            if path.stat().st_size > 100 * 1024 * 1024:
                raise ValueError('unexpected generated or large payload in source package: ' + relative)
            files.append({'path': relative, 'sha256': sha(path), 'bytes': path.stat().st_size})
        manifest = {
            'schema': 'k58-opt-in-research-solver/v1', 'version': '2026-11-28-square-color-armcap',
            'base_archive': {'file': str(base.resolve()), 'sha256': sha(base)},
            'square_archive': {'file': str(square.resolve()), 'sha256': sha(square)},
            'intentional_stock_replacements': ['k58.sh', 'README.md -> STOCK_README.md + new README.md'],
            'proof_scope': 'optional validated variants only; no wall/Ramsey/performance completion claim',
            'files': files,
        }
        (root / 'modified-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        output.parent.mkdir(parents=True, exist_ok=True)
        candidate = output.with_name(f'.{output.name}.{os.getpid()}.partial')
        assert not candidate.exists(), 'stale partial build; inspect/remove it explicitly'
        # Only a checked nonempty archive is published, atomically, at the
        # requested new path.  A failed build cannot masquerade as a solver.
        try:
            with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for path in sorted(root.rglob('*')):
                    if not path.is_file() or '.scratch' in path.relative_to(root).parts or '__pycache__' in path.relative_to(root).parts:
                        continue
                    name = (Path('k58-solver') / path.relative_to(root)).as_posix()
                    z.write(path, name)
            with zipfile.ZipFile(candidate) as z:
                assert z.testzip() is None
                assert 'k58-solver/k58.sh' in z.namelist()
                assert 'k58-solver/square_spoke/source/next/matching.drat.gz' in z.namelist()
                assert any(n.startswith('k58-solver/k58/') for n in z.namelist())
            candidate.replace(output)
        except BaseException:
            candidate.unlink(missing_ok=True)
            raise
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, default=REPO / 'dist/k58-solver.zip')
    p.add_argument('--square', type=Path, default=REPO / 'attachments/let-s-try-and-rbdv/K58_square_spoke_wall_test.zip')
    p.add_argument('--out', type=Path, default=REPO / 'dist/k58-updated-solver.zip')
    args = p.parse_args()
    archive = build(args.base, args.square, args.out)
    digest = sha(archive)
    sums = archive.with_suffix('.SHA256SUMS')
    sums.write_text(f'{digest}  {archive.name}\n')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': digest,
                      'sha256sums': str(sums), 'scope': 'opt-in research solver; no new Ramsey result'}, indent=2))


if __name__ == '__main__':
    main()
