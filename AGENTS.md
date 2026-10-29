# Risalero workshop

Read the AGENTS.md in the active working area. The workshop repository holds both areas as Git
submodules; preserve every Git history and user changes.
The target language is a project variable: never write language-specific rules into tools,
schemas or instructions. The accepted source languages (Arabic, Turkish) are data in
`agentic-translate/knowledge/config.json`. Name no model or vendor; a reviewer is a fresh
agent of your own model.

## Always do

- Write instructions briefly, as what to do.
- Use the single `agentic-translate/knowledge/knowledge.sqlite`; every write refreshes
  `agentic-translate/knowledge/knowledge.jsonl`, which is the tracked text copy.
- Check existing terminology in agentic-translate before requesting it. Send missing terms
  as `term (source-segment.md:line)`; do not repeat discovery in punctual-term-translation.
- In punctual-term-translation, follow term-translator and its Voice section in
  `.agents/skills/term-translator/SKILL.md`. New translations need two alternatives, their footnotes,
  and term-reviewer. The work in progress is visible in `results/results.md`.
- Keep exact human terminology approval in punctual-term-translation and first-use notes
  and book validation in agentic-translate.
- Keep experiments disposable; preserve genuine research, sources and approved wording.

## Ask first

- Obtain explicit human approval of exact new equivalents and footnotes before publication.
- Ask for missing source identity only when the supplied location cannot be resolved.

## Never do

- Create a second active terminology store or copied glossary.
- Repeat the receiving area's internal workflow in the sending area's instructions.
- Change approved wording without exact replacement approval.
- Initialize another repository, commit, push, tag or publish without explicit instruction.
- Track books: EPUB originals, prepared sources, translations and editions stay local.

## Checks

From punctual-term-translation:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 -B tools/terms.py check
```

From agentic-translate:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py'
python3 -B tools/knowledge.py --config knowledge/config.json integrity
python3 -B tools/knowledge.py --config knowledge/config.json terms list --language ro
```
