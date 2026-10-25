# Whitespace Cleanup

## What it does
Collapses extra blank lines, removes standalone page numbers, and joins lines that were broken mid-sentence by PDF column wrapping. No words are removed — purely structural cleanup.

## How it works
1. Scan each line; drop lines that are **only** a number (page numbers like `42`).
2. Walk lines in order; if a line doesn't end with `.!?:` and the next starts with a lowercase letter, join them (PDF line-break fix).
3. Collapse runs of 2+ spaces to one space.
4. Collapse 3+ blank lines to 2.

## Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| *(none)* | – | – | This technique has no parameters. |

## Example
**Input:**
```
The quick brown fox jumps over the
lazy dog.     Page numbers waste space.

42

Another paragraph here.
```
**Output:**
```
The quick brown fox jumps over the lazy dog.     Page numbers waste space.

Another paragraph here.
```

## Pros / Cons / Where it breaks
- ✅ Lossless — no semantic content removed
- ✅ Always safe to run first in a pipeline
- ❌ Won't fix tables or multi-column PDFs
- ❌ Heuristic join may incorrectly merge headings that don't end with punctuation

## Typical saving
2–8% token reduction on PDF-extracted text; near 0% on clean TXT/MD files.

