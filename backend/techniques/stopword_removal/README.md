# Stopword Removal

## What it does
Removes common English stopwords (the, is, in, of, …) using NLTK's stopword list. Negations (not, no, never) and numbers are always protected so the meaning is not accidentally reversed.

## How it works
1. Load NLTK's English stopword list (~179 words).
2. Remove negation words and any user-supplied protected words from the effective stopword list.
3. Split text on spaces; for each word, strip punctuation for lookup but keep the original form.
4. Drop the word if it matches an effective stopword.

## Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| protected_words | text | `""` | Comma-separated words to keep even if they are stopwords. |

## Example
**Input:** `The cat sat on the mat and it was not happy.`
**Output:** `cat sat mat happy.` *(negation "not" is kept)*

Wait — "not" is always in ALWAYS_PROTECT, so: `cat sat mat not happy.`

## Pros / Cons / Where it breaks
- ✅ Fast; no model required
- ✅ Protects negations — won't flip the meaning of "not safe"
- ❌ Removes grammatical structure; output is keyword-soup at high density
- ❌ English only (NLTK list is English)

## Typical saving
20–40% token reduction on normal prose.

