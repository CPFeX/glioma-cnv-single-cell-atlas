"""Verify the frozen patient sensitivity package without writing or running analysis."""
import argparse
import csv
import hashlib
import io
from pathlib import Path, PurePosixPath
import sys
import zipfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative_name(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and ':' not in name
            and '\\' not in name and bool(p.parts), f'Unsafe relative path: {name}')
    return p


def verify(root, package):
    checksum = (package / 'SHA256SUMS.txt').read_text(encoding='utf-8').strip()
    expected_hash, archive_name = checksum.split(maxsplit=1)
    archive_name = archive_name.strip()
    require(len(relative_name(archive_name).parts) == 1, 'Archive must be a local filename')
    archive = package / archive_name
    require(digest(archive.read_bytes()) == expected_hash, 'Archive SHA256 mismatch')
    manifest = (package / 'FILE_MANIFEST.tsv').read_bytes()
    entries = list(csv.DictReader(io.StringIO(manifest.decode('utf-8')), delimiter='\t'))
    require(len(entries) == 39, 'Expected 39 authoritative result files')
    expected_names = [e['archive_relative_path'] for e in entries]
    require(len(set(expected_names)) == len(expected_names), 'Duplicate manifest paths')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP members')
        require(set(names) == set(expected_names) | {'README.txt', 'FILE_MANIFEST.tsv'},
                'Unexpected or missing ZIP members')
        require(z.read('FILE_MANIFEST.tsv').replace(b'\r\n', b'\n') ==
                manifest.replace(b'\r\n', b'\n'), 'Internal/external manifests differ')
        for entry in entries:
            name = entry['archive_relative_path']
            relative_name(name)
            data = z.read(name)
            require(len(data) == int(entry['bytes']), f'Size mismatch: {name}')
            require(digest(data) == entry['sha256'], f'Hash mismatch: {name}')
    with (package / 'INPUT_CODE_MANIFEST.tsv').open(encoding='utf-8', newline='') as f:
        inputs = list(csv.DictReader(f, delimiter='\t'))
    require(len(inputs) == 17, 'Expected 13 upstream inputs and four notebooks')
    for entry in inputs:
        rel = relative_name(entry['relative_path'])
        path = (root / str(rel)).resolve()
        require(path.is_relative_to(root), f'Input is outside repository: {rel}')
        data = path.read_bytes()
        mode = entry['hash_mode']
        require(mode in ('bytes', 'lf_text'), f'Unknown hash mode: {mode}')
        if mode == 'lf_text':
            data = data.replace(b'\r\n', b'\n')
        require(len(data) == int(entry['bytes']) and digest(data) == entry['sha256'],
                f'Recorded input/code changed: {rel}')
    print('PASS: 39 archived results, complete ZIP integrity, 13 upstream inputs and four notebooks.')
    print('Verification only: no files written and no scientific analyses executed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--package', type=Path, help='Alternative package directory for verification')
    args = parser.parse_args()
    root = args.root.resolve()
    package = args.package or root / 'supplementary/patient_level_sensitivity'
    try:
        verify(root, package)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
