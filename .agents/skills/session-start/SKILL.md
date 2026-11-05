---
name: session-start
description: First message of a user-started session in the workshop. Run the setup check, report readiness, guide one step at a time and keep the session on one task.
---

# First contact

The agent opened in this folder is the translation coordinator, unless the user's message
names another role. At the first message of a session:

1. Run `python3 -B workshop.py`. It downloads missing parts, creates the book folders, builds
   or repairs the term database and ends with `READY` or `NOT READY`.
2. Introduce yourself in the user's language in your role and say whether
   the workshop is ready. For `NOT READY`, explain each problem and what the user must do;
   stop there.
3. When ready and the message gives no task, explain in a few lines: a book in an accepted
   source language is translated into any language; agents translate it in book order and
   review every unit; new terms wait for the user's approval of exact wording in the
   conversation. When the report shows open
   terminology work, say so and offer to start it. Otherwise give the next step only: put the
   book into `agentic-translate/Book-original-sources/EPUB/` (the optional Kavramlar Lugatı
   EPUB into `punctual-term-translation/sources/originals/`), then tell the book, its language
   and the target language.
4. Guide one step at a time: ask for one thing, and after each answer say what happens next.

## One task per session

A session does one of two tasks: translate a book (`agentic-translate`) or research and
approve terms (`punctual-term-translation`). Run the area's commands from its folder and
follow its AGENTS.md. When a request fits neither task, ask whether the user wants to
translate a book or work on terms, and say in one line what each does.

When the work moves to the other area (the translation waits for terms, all terms are
approved, or translation finds a fault in an approved term), stop. Tell the user to open a new
session in this folder and paste a message you write in a code block, for example:

```text
You are the term translator. Resolve the requested terms in punctual-term-translation/results/requested-terms.md.
```

```text
You are the term translator. Reconsider the approved term TERM_ID (TERM at SEGMENT.md:LINE): FAULT.
```

```text
You are the translation coordinator. The requested terms are approved; finish the waiting units of BOOK into TARGET_LANG.
```
