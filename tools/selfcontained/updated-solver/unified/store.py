"""Content-addressed, byte-checked store for unified cohort artifacts.

Store adoption indexes bytes only.  It does not admit a case, prove a clause or
promote a certificate.  Native verification precedes every 'checked' tag in the
caller.  No 64-hex row identifier is ever mistaken for a content digest.
"""
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path


class StoreError(ValueError):
    pass


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        (self.root / 'blobs').mkdir(parents=True, exist_ok=True)
        (self.root / 'index').mkdir(exist_ok=True)
        self.write_lock = threading.Lock()

    def blob(self, digest):
        return self.root / 'blobs' / digest[:2] / digest

    def _copy_source_to_blob(self, source, digest):
        target = self.blob(digest)
        if target.exists():
            if not target.is_file() or sha_file(target) != digest:
                raise StoreError('stored blob has changed content or is not a regular file')
            return False
        target.parent.mkdir(parents=True, exist_ok=True)
        candidate = target.parent / f'.{digest}.{os.getpid()}-{threading.get_ident()}.partial'
        if candidate.exists():
            raise StoreError('unclaimed partial blob; remove explicitly after inspection')
        size = 0
        with source.open('rb') as src, candidate.open('xb') as out:
            for chunk in iter(lambda: src.read(1 << 20), b''):
                out.write(chunk); size += len(chunk)
        if size == 0:
            candidate.unlink(missing_ok=True)
            raise StoreError('empty payload is not evidence')
        if sha_file(candidate) != digest:
            candidate.unlink(missing_ok=True)
            raise StoreError('source changed while copying content-addressed artifact')
        candidate.chmod(0o444)
        try:
            os.link(candidate, target)
        except FileExistsError:
            if sha_file(target) != digest:
                candidate.unlink(missing_ok=True)
                raise StoreError('conflicting blob was created concurrently')
        finally:
            candidate.unlink(missing_ok=True)
        return True

    def put_file(self, source, *, expected, domain, role, checked=False):
        """Store a nonempty source payload only after its identity is confirmed."""
        source = Path(source).resolve()
        require(domain in ('raw-bytes', 'decompressed'), f'cannot infer digest domain {domain}')
        require(source.is_file(), f'missing payload {source}')
        digest = sha_file(source)
        if domain == 'decompressed':
            try:
                with gzip.open(source, 'rb') as stream:
                    h = hashlib.sha256()
                    for chunk in iter(lambda: stream.read(1 << 20), b''):
                        h.update(chunk)
                    actual = h.hexdigest()
            except OSError as exc:
                raise StoreError('invalid compressed proof carrier') from exc
        else:
            actual = digest
        require(actual == expected, f'{role}: supplied digest {expected} != actual {actual}')
        made = self._copy_source_to_blob(source, digest)
        self._record({'domain': domain, 'role': role, 'sha256': actual,
                      'carrier_sha256': digest, 'bytes': source.stat().st_size,
                      'source_basename': source.name, 'stored': True,
                      'native_checked': bool(checked), 'new_blob': made})
        return {'sha256': actual, 'domain': domain, 'blob': str(self.blob(digest)),
                'carrier_sha256': digest, 'native_checked': bool(checked)}

    def adopt(self, source, *, expected=None):
        """Read-only byte adoption, with no proof or ledger classification."""
        source = Path(source).resolve()
        actual = sha_file(source)
        require(expected is None or actual == expected, 'adopt hash mismatch')
        self._copy_source_to_blob(source, actual)
        self._record({'domain': 'raw-bytes', 'role': 'adopted-source-bytes',
                      'sha256': actual, 'carrier_sha256': actual,
                      'bytes': source.stat().st_size, 'native_checked': False,
                      'resolution': 'stored-untyped', 'source_basename': source.name,
                      'source': str(source), 'complete_evidence': False})
        return {'sha256': actual, 'resolution': 'stored-untyped', 'blob': str(self.blob(actual))}

    def _record(self, receipt):
        line = json.dumps(receipt, sort_keys=True, separators=(',', ':')) + '\n'
        with self.write_lock:
            with (self.root / 'index' / 'events.jsonl').open('a') as stream:
                stream.write(line)

    def adopt_link(self, value):
        """Link a blob into a freshly generated job path, never over a different file."""
        dest = Path(value['blob_source']).resolve()
        blob = Path(value['blob']).resolve()
        expected = value.get('carrier_sha256', value['sha256'])
        if dest.exists() and sha_file(dest) != expected:
            raise StoreError('artifact name contains different bytes from the stored blob')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()
        os.link(blob, dest)
        return str(dest)


def capture_directory(folder, cohort_root, ref_prefix='prepared'):
    """Capture every currently validated input with explicit role/domain labels."""
    folder = Path(folder).resolve()
    plan = json.loads((folder / 'plan.json').read_text())
    store = Store(cohort_root / 'store')
    pairs = [('parent.cnf', plan['parent_sha256'], 'parent-raw-bytes', 'raw-bytes'),
             ('working.cnf', plan['working_sha256'], 'working-raw-bytes', 'raw-bytes')]
    if plan['cas'] != 'off':
        pairs.append(('cas.drat', plan['cas_proof_sha256'], 'cas-prefix-raw-bytes', 'raw-bytes'))
    else:
        require(plan['cas_proof_sha256'] == hashlib.sha256(b'').hexdigest(),
                'cas=off: only the canonical empty payload is accepted')
    results = []
    for name, expected, role, domain in pairs:
        path = folder / name
        ref = store.put_file(path, expected=expected, domain=domain, role=role)
        ref['blob_source'] = str(path)
        results.append(store.adopt_link(ref))
    for name in ('color-receipt.json', 'square-receipt.json', 'color-check.json'):
        path = folder / name
        if path.is_file():
            ref = store.put_file(path, expected=sha_file(path), domain='raw-bytes', role=name)
            ref['blob_source'] = str(path)
            results.append(store.adopt_link(ref))
    proof = folder / 'color-proof.drat.gz'
    if proof.is_file():
        with gzip.open(proof, 'rb') as stream:
            expected = hashlib.sha256(stream.read()).hexdigest()
        ref = store.put_file(proof, expected=expected, domain='decompressed',
                             role='colour-native-proof-carrier', checked=True)
        ref['blob_source'] = str(proof)
        results.append(store.adopt_link(ref))
    return {'schema': 'cohort-content-addressed-v1', 'captured': results,
            'parent_sha256': plan['parent_sha256'], 'cas_off': plan['cas'] == 'off',
            'store_root': str(store.root), 'scope': ref_prefix + ': bytes stored, no row/Ramsey claim'}


def check(store_root):
    store_root = Path(store_root)
    records = []
    for path in (store_root / 'blobs').glob('*/*'):
        if path.is_file() and not path.name.startswith('.'):
            actual = sha_file(path)
            if actual != path.name:
                raise StoreError(f'blob content changed: {path}')
            records.append({'sha256': path.name, 'bytes': path.stat().st_size})
    return {'status': 'PASS', 'store': str(store_root), 'blobs': len(records),
            'content_checks': len(records),
            'scope': 'stored byte-integrity only; not evidence sufficiency or UNSAT'}


def require(value, message):
    if not value:
        raise StoreError(message)


def main(argv):
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    adopt = sub.add_parser('adopt'); adopt.add_argument('--source', type=Path, required=True)
    adopt.add_argument('--store', type=Path, required=True)
    adopt.add_argument('--expected-sha256')
    check_parser = sub.add_parser('check'); check_parser.add_argument('--store', type=Path, required=True)
    args = p.parse_args(argv)
    store = Store(args.store)
    if args.action == 'adopt':
        result = store.adopt(args.source, expected=args.expected_sha256)
    else:
        result = check(store.root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main(__import__('sys').argv[1:])


def capture_checked_outputs(folder, cohort_root):
    """Index only already checked leaf/composed proofs and model payloads."""
    folder = Path(folder)
    store = Store(cohort_root / 'store')
    result = []
    for receipt_path in (folder / 'leaves').glob('*/receipt.json'):
        rec = json.loads(receipt_path.read_text())
        leaf = receipt_path.parent
        if rec['status'] == 'CHECKED_UNSAT':
            path = leaf / 'leaf.drat'
            result.append(store.put_file(path, expected=rec['artifact_sha256'],
                                         domain='raw-bytes', role='checked-leaf-drat', checked=True))
        elif rec['status'] == 'CHECKED_SAT':
            path = leaf / 'model.json'
            result.append(store.put_file(path, expected=rec['artifact_sha256'],
                                         domain='raw-bytes', role='checked-leaf-model', checked=True))
        else:
            # OPEN/timeout is not evidence and has no artifact to publish.
            require(rec['status'] in ('OPEN', 'PROOF_PENDING', 'CHECK_FAILED'),
                    'unknown leaf artifact/status cannot be adopted')
            continue
    proof = folder / 'composed.drat'
    if proof.is_file():
        result.append(store.put_file(proof, expected=sha_file(proof),
                                     domain='raw-bytes', role='checked-composed-drat', checked=True))
    return result
