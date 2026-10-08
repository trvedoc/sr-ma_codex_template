"""Freeze allowed inputs/code and hash referenced local source documents."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil


def archive(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    schema = json.loads((root / 'data/schema.json').read_text())
    paths = set(schema) | {'review.json','data/schema.json','renv.lock','AGENTS.md',
                           'extraction/codebook.md','TEMPLATE_VERSION',
                           'analysis/run.R','.Rprofile','renv/activate.R','renv/settings.json'}
    for directory in ('protocol', 'analysis/R', 'scripts', 'search/strategies', 'search/exports'):
        paths.update(str(p.relative_to(root)) for p in (root / directory).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    hashes = {}
    snapshot = destination / 'inputs'
    for relative in sorted(paths):
        source = root / relative
        if not source.is_file():
            continue
        data = source.read_bytes()
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        hashes[relative] = hashlib.sha256(data).hexdigest()
    source_hashes = {}
    with (root / 'studies/reports.csv').open(newline='', encoding='utf-8') as handle:
        for row in csv.DictReader(handle):
            filename = row.get('local_filename', '').strip()
            if not filename:
                continue
            source = (root / 'fulltext' / filename).resolve()
            if source.is_relative_to(root / 'fulltext') and source.is_file():
                source_hashes[row['report_id']] = {
                    'filename':filename, 'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'input-manifest.json').write_text(json.dumps({
        'algorithm':'SHA-256','snapshot_files':hashes,
        'local_source_hashes':source_hashes,
        'note':'Local report files are hashed when present, not copied. Retain source access separately.'
    }, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    archive(args.root, args.destination)
