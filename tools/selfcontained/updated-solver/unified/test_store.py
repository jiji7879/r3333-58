#!/usr/bin/env python3
"""Small negative/positive storage controls; all mutable files are new fixtures."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from store import Store, StoreError, sha_file, check


def main():
    with tempfile.TemporaryDirectory(prefix='k58-store-test-', dir=sys.argv[1]) as name:
        root = Path(name); store = Store(root / 'store')
        a = root / 'a.dat'; a.write_bytes(b'abc')
        b = root / 'b.dat'; b.write_bytes(b'abc')
        first = store.adopt(a); second = store.adopt(b)
        assert first['sha256'] == second['sha256']
        assert sum(p.stat().st_size for p in (store.root / 'blobs').rglob('*') if p.is_file()) == 3
        empty = root / 'empty.drat'; empty.write_bytes(b'')
        try: store.adopt(empty)
        except StoreError: pass
        else: raise AssertionError('empty artifact admitted')
        packed = root / 'proof.drat.gz'
        packed.write_bytes(gzip.compress(b'abc', mtime=0))
        ref = store.put_file(packed, expected=hashlib.sha256(b'abc').hexdigest(),
                             domain='decompressed', role='test-payload-carrier', checked=True)
        assert ref['carrier_sha256'] != ref['sha256']
        assert Path(ref['blob']).name == ref['carrier_sha256']
        ref['blob_source'] = str(packed)
        store.adopt_link(ref)
        assert check(store.root)['status'] == 'PASS'
        source_blob = next(p for p in (store.root / 'blobs').rglob('*') if p.is_file())
        original = source_blob.read_bytes(); assert source_blob.chmod(0o600) is None
        source_blob.write_bytes(b'X' + original[1:])
        assert source_blob.read_bytes() != original
        try: check(store.root)
        except StoreError: pass
        else: raise AssertionError('tampered blob accepted')
        result = {'status': 'PASS', 'duplicate_bytes_stored_once': 3,
                  'logical_decompressed_hash_differs_from_carrier': True,
                  'empty_rejected': True, 'tamper_rejected': True,
                  'scope': 'storage identity only, no case or proof promotions'}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
