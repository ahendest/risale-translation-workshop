#!/usr/bin/env python3
"""Prepare the workshop and report whether it is ready. Safe to run again at any time."""
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRANSLATE = ROOT / 'agentic-translate'
TERMS = ROOT / 'punctual-term-translation'
FOLDERS = (TRANSLATE / 'Book-original-sources/EPUB', TERMS / 'sources/originals')
# Lisan al-Arab (Ibn Manzur), public-domain text, from a fixed commit of
# https://github.com/eliyahu-freedman/arabic-lexicon; downloaded, never tracked here.
LISAN_URL = ('https://raw.githubusercontent.com/eliyahu-freedman/arabic-lexicon/'
             'cc7ee70b34594ac112843b2da1753146d04006ad/lisan-text/lisan-{:02d}.txt')
LISAN_FILES = 26
LISAN_DIR = TRANSLATE / 'knowledge/sources/downloads/lisan-al-arab'
problems, warnings, notes = [], [], []


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8')


def knowledge(source, *args):
    """One command on the store of a source language through the translation area's tool; returns its parsed JSON."""
    result = run([sys.executable, '-B', 'tools/knowledge.py', '--config', 'knowledge/config.json',
                  '--source-language', source, *args], TRANSLATE)
    try:
        return json.loads(result.stdout)
    except ValueError:
        return {'ok': False, 'error': {'message': (result.stderr or result.stdout).strip()[-300:]}}


def areas():
    missing = [area for area in (TRANSLATE, TERMS) if not (area / 'AGENTS.md').is_file()]
    if missing:
        # Only missing areas: an update of an existing area would move it to the pinned commit.
        if not shutil.which('git'):
            problems.append('Git is not installed; install Git and run this again')
            return False
        result = run(['git', 'submodule', 'update', '--init', *(a.name for a in missing)], ROOT)
        if result.returncode:
            problems.append('Could not download the workshop parts: ' + result.stderr.strip()[-300:])
            return False
    return True


def set_aside(db):
    """Move a store and its SQLite side files out of use; nothing is deleted."""
    aside = db.with_name(f'{db.name}.old-{time.strftime("%Y%m%d-%H%M%S")}')
    for suffix in ('', '-wal', '-shm'):
        part = Path(str(db) + suffix)
        if part.exists():
            part.rename(Path(str(aside) + suffix))
    return aside.name


def split_single_store(config):
    """Once: the earlier single store becomes one store per source language; its text copy is split by language."""
    folder = TRANSLATE / 'knowledge'
    old = folder / 'knowledge.jsonl'
    if old.is_file():
        records = [json.loads(line) for line in lines(old)]
        for source in config['source_languages']:
            own = [line for line, r in zip(lines(old), records) if r.get('source_language') == source]
            target = folder / f'{source}.jsonl'
            if own and not target.exists():
                target.write_text(''.join(line + '\n' for line in own), encoding='utf-8')
        old.rename(folder / 'knowledge.jsonl.old')
        notes.append('Your approved terms moved into one store per source language; the old text copy is knowledge.jsonl.old')
    if (folder / 'knowledge.sqlite').exists():
        set_aside(folder / 'knowledge.sqlite')


def store(source, dictionaries):
    db = TRANSLATE / f'knowledge/{source}.sqlite'
    if db.exists() and not knowledge(source, 'integrity')['ok']:
        notes.append(f'The {source} term database was set aside as {set_aside(db)}; a new one was built')
    if not db.exists():
        # Each user's terms are their own: a new database starts empty, or from this user's local text copy.
        steps = [('init',)]
        if lines(TRANSLATE / f'knowledge/{source}.jsonl'):
            steps.append(('import-terms', '--input', f'knowledge/{source}.jsonl'))
            notes.append(f'Your approved terms for {source} books were restored from knowledge/{source}.jsonl')
        if 'lugat' in dictionaries:
            steps.append(('import-lugat', '--input', 'knowledge/sources/db_lugat.sql'))
        for step in steps:
            result = knowledge(source, *step)
            if not result['ok']:
                problems.append(f'The {source} term database setup failed at {step[0]}: {result["error"]["message"]}')
                return
    if 'lisan-al-arab' in dictionaries:
        lisan(source)
    check = knowledge(source, 'integrity')
    if not check['ok']:
        problems.append(f'The {source} term database check failed: ' + check['error']['message'])
        return
    item = check['items'][0]
    found = ', '.join(f'{name} {count}' for name, count in item['dictionaries'].items()) or 'none'
    notes.append(f'{source} books: {item["terms"]} approved terms; dictionary entries: {found}')


def lisan(source):
    """Download the Arabic dictionary once and import it; research works without it, so a failure is a warning."""
    LISAN_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for n in range(1, LISAN_FILES + 1):
            target = LISAN_DIR / f'lisan-{n:02d}.txt'
            if not target.is_file():
                partial = target.with_name(target.name + '.part')
                with urllib.request.urlopen(LISAN_URL.format(n), timeout=60) as response:
                    partial.write_bytes(response.read())
                partial.replace(target)
    except OSError as error:
        warnings.append(f'The Arabic dictionary (Lisan al-Arab) could not be downloaded ({error}); '
                        'term research works without it. Run this again with an internet connection.')
        return
    result = knowledge(source, 'import-lisan', '--input', LISAN_DIR.relative_to(TRANSLATE).as_posix())
    if not result['ok']:
        warnings.append('The Arabic dictionary could not be imported: ' + result['error']['message'])


def lines(path):
    return [line for line in path.read_text(encoding='utf-8').splitlines() if line.strip()] if path.is_file() else []


def work(config):
    notes.append('Accepted source languages: ' + ', '.join(config['source_languages']) + '; any target language')
    books = sorted(p.name for p in (TRANSLATE / 'Book-original-sources/EPUB').rglob('*.epub'))
    notes.append('Books in Book-original-sources/EPUB: ' + (', '.join(books) if books else 'none yet'))
    projects = sorted(p.parent.relative_to(TRANSLATE / 'translations').as_posix()
                      for p in (TRANSLATE / 'translations').glob('*/*/project.json'))
    if projects:
        notes.append('Translation projects: ' + ', '.join(projects))
    requested, job = lines(TERMS / 'results/requested-terms.md'), lines(TERMS / 'results/current-job.md')
    runs = list((TERMS / 'data/runs').glob('*.json'))
    if requested or job or runs:
        notes.append(f'Open terminology work: {len(requested)} new requests, {len(job)} in the current job, '
                     f'{len(runs)} terms in research or waiting for approval')


def main():
    if sys.version_info < (3, 11):
        problems.append('Python 3.11 or newer is required; this is ' + sys.version.split()[0])
    elif areas():
        for folder in FOLDERS:
            folder.mkdir(parents=True, exist_ok=True)
        config = json.loads((TRANSLATE / 'knowledge/config.json').read_text(encoding='utf-8'))
        split_single_store(config)
        for source in config['source_languages']:
            store(source, config.get('dictionaries', {}).get(source, []))
        work(config)
    for note in notes:
        print('- ' + note)
    for warning in warnings:
        print('WARNING: ' + warning)
    for problem in problems:
        print('PROBLEM: ' + problem)
    print('NOT READY' if problems else 'READY')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
