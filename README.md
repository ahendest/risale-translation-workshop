# Risalero workshop

The Risalero workshop translates Islamic books into other languages with AI agents, while a
person keeps control of the religious and technical terms. It was built for the Risale-i Nur
collection and works for any book you have as an EPUB file, in any pair of languages.

## Why it exists

A good translation must not flatten words such as *namaz*, *nefs* or *abdest* into a general
word. The workshop keeps such a term as the author wrote it, adds its approved translation in
parentheses, and explains it once, in a short note at its first use in the book. You approve
the exact wording of every term. Approved terms are stored once and reused in every book of the
same language.

## The two parts

| Part | What it does |
| --- | --- |
| [agentic-translate](agentic-translate/README.md) | Prepares the EPUB, translates the book unit by unit in book order, has every unit reviewed independently, and places each term's note at its first use. |
| [punctual-term-translation](punctual-term-translation/README.md) | Researches each new term, writes two proposals with their notes, has them compared independently, and waits for your approval. |

## How a book moves through the workshop

1. **You start a request** in agentic-translate with the EPUB, the source language and the
   target language:

   ```text
   çeviri istegi, kaynak dil: tr, hedef dil: ro, kitabin directory'si: path/to/book.epub
   ```

2. **The agents translate** the book in order. Quotations in another script, such as Arabic
   verses, are copied exactly. A second agent reviews each unit and keeps recurring phrases
   consistent across the book.
3. **New terms are collected** into a short list, each with its place in the book. Units that
   contain them wait.
4. **You take the list** to punctual-term-translation. For each term you read two proposals in
   `results/results.md` and approve the exact wording.
5. **The waiting units are finished** with the approved wording and the note at the term's first
   use, then reviewed and checked.

If your book is not a clean EPUB (a PDF, a scan, or a book written entirely in Arabic), read
[Sources that are not a clean EPUB](agentic-translate/docs/source-options.md).

## Getting the workshop

The workshop is one repository that holds the two parts as Git submodules, so they always sit
side by side:

```bash
git clone --recurse-submodules https://github.com/ahendest/risalero-workshop.git
```

Books are never stored in the repositories; your EPUB files, translations and editions stay on
your computer.

## Licence

MIT, see [LICENSE](LICENSE). Each part has its own [CHANGELOG](agentic-translate/CHANGELOG.md).
