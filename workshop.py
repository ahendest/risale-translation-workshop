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


def knowledge(*args):
    """One store command through the translation area's tool; returns its parsed JSON output."""
    result = run([sys.executable, '-B', 'tools/knowledge.py', '--config', 'knowledge/config.json', *args], TRANSLATE)
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


def store():
    db = TRANSLATE / 'knowledge/knowledge.sqlite'
    if db.exists() and not knowledge('integrity')['ok']:
        # The tracked text copy holds every approved term; an old or damaged store is set aside, not deleted.
        aside = db.with_name(f'knowledge.sqlite.old-{time.strftime("%Y%m%d-%H%M%S")}')
        for suffix in ('', '-wal', '-shm'):
            part = Path(str(db) + suffix)
            if part.exists():
                part.rename(Path(str(aside) + suffix))
        notes.append(f'The old term database was set aside as {aside.name}; a new one was built')
    if not db.exists():
        # Each user's terms are their own: a new database starts empty, or from this user's local text copy.
        backup = TRANSLATE / 'knowledge/knowledge.jsonl'
        steps = [('init',), ('import-lugat', '--input', 'knowledge/sources/db_lugat.sql')]
        if backup.is_file() and backup.read_text(encoding='utf-8').strip():
            steps.insert(1, ('import-terms', '--input', 'knowledge/knowledge.jsonl'))
            notes.append('Your approved terms were restored from knowledge/knowledge.jsonl')
        for step in steps:
            result = knowledge(*step)
            if not result['ok']:
                problems.append(f'Term database setup failed at {step[0]}: {result["error"]["message"]}')
                return
    lisan()
    check = knowledge('integrity')
    if not check['ok']:
        problems.append('Term database check failed: ' + check['error']['message'])
        return
    item = check['items'][0]
    dictionaries = ', '.join(f'{name} {count}' for name, count in item['dictionaries'].items())
    notes.append(f'Term database ready: {item["terms"]} approved terms; dictionary entries: {dictionaries}')


def lisan():
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
    result = knowledge('import-lisan', '--input', LISAN_DIR.relative_to(TRANSLATE).as_posix())
    if not result['ok']:
        warnings.append('The Arabic dictionary could not be imported: ' + result['error']['message'])


def lines(path):
    return [line for line in path.read_text(encoding='utf-8').splitlines() if line.strip()] if path.is_file() else []


def work():
    config = json.loads((TRANSLATE / 'knowledge/config.json').read_text(encoding='utf-8'))
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
        store()
        work()
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
