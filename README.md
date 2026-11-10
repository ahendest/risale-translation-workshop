# Risale translation workshop

The Risale translation workshop translates Islamic books into other languages with AI agents,
while you keep control of the religious and technical terms. It was built for the Risale-i Nur
collection and works for any Turkish or Arabic book you have as an EPUB file, translated into
any language.

## Start here

You need Git, Python 3.11 or newer, and an AI coding agent that can run commands in a folder.
It works on Linux, macOS and Windows; on Windows, install Git for Windows, which brings the
Git Bash terminal that the agent uses for the commands.

1. **Get the workshop:**

   ```bash
   git clone --recurse-submodules https://github.com/ahendest/risale-translation-workshop.git
   ```

2. **Open your agent in the `risale-translation-workshop` folder and say hello.** It
   introduces itself as your translation coordinator, prepares the workshop (folders for your
   books and the term database) and tells you whether everything is ready. You can also run
   this check yourself: `python3 workshop.py`.
3. **Put your book in `agentic-translate/Book-original-sources/EPUB/`** and tell the agent the
   book, its language and the language you want, in your own words. The agent runs everything
   and asks you only about meaning and wording.

Use a new session for each task: one for the translation, one for the terms. When it is time
to switch, the agent gives you a short message to paste into the new session; a fresh session
keeps each task clear and focused.

Books are never stored in the repositories; your EPUB files, translations and editions stay on
your computer.

The root [agent rules](AGENTS.md#harness-protection) require agents to preserve the workflow
during translation and terminology work and to bring you back to one of the two tasks. Changes
to the harness require an explicit maintenance request; a change that a target language really
needs is proposed to you and checked by an independent reviewer agent first. These are agent
instructions; they do not prevent changes by someone with write access.

## Why it exists

A good translation must not flatten a religious term into a general word, and must not burden
the reader with foreign words that the language can say. A concept with a usual word in your
language is translated. A term without one is kept as the author wrote it, with its approved
translation in parentheses and a short note at its first use in the book, and alone later. You
approve the exact wording of every term. Your approved terms stay on
your computer; the workshop starts with none. They are stored once and reused in every book
with the same source and target language: a term approved for a Turkish book is not reused for
an Arabic one.

## How a book moves through the workshop

1. **You name the book** and the two languages.
2. **The agents translate** the book in order. Quotations in another script, such as Arabic
   verses, are copied exactly. A second agent reviews each unit and keeps recurring phrases
   consistent across the book.
3. **New terms are collected.** Units that contain them wait.
4. **You approve each term.** For every new term you read two proposals with their notes and a
   reviewer's choice, then tell the agent which wording you approve.
5. **The waiting units are finished** with the approved wording and the note at the term's first
   use, then reviewed and checked.

If your book is not a clean EPUB (a PDF, a scan, or a book written entirely in Arabic), read
[Sources that are not a clean EPUB](agentic-translate/docs/source-options.md).

## The two parts

| Part | What it does |
| --- | --- |
| [agentic-translate](agentic-translate/README.md) | Prepares the EPUB, translates the book unit by unit in book order, has every unit reviewed independently, and places each term's note at its first use. |
| [punctual-term-translation](punctual-term-translation/README.md) | Researches each new term, writes two proposals with their notes, has them compared independently, and waits for your approval. |

The research can also use the *Kavramlar Lugatı* EPUB. If you have it, put it in
`punctual-term-translation/sources/originals/`.

## Licence

MIT, see [LICENSE](LICENSE). At setup the workshop downloads *Lisān al-ʿArab* (Ibn Manẓūr,
public-domain text) from
[eliyahu-freedman/arabic-lexicon](https://github.com/eliyahu-freedman/arabic-lexicon) into your
copy; it is not part of this repository. Each part has its own [CHANGELOG](agentic-translate/CHANGELOG.md).
