# Grammar-Based Compression

## What it does
Uses spaCy's part-of-speech (POS) tagger to remove words that carry little meaning. Three strictness levels let you control the aggressiveness. Negations, numbers, and named entities are always kept.

## How it works
1. Run spaCy's pipeline on the text to get POS tags and dependency labels.
2. At **level 1**: remove filler words ("very", "basically", "actually", etc.) by a fixed word list.
3. At **level 2**: also remove words tagged as `DET` (articles), `AUX` (auxiliary verbs), and `ADV` (adverbs) — except negation adverbs.
4. At **level 3**: keep only `NOUN`, `PROPN`, `VERB`, `NUM`; drop everything else.
5. At all levels: protect tokens where `dep_ == "neg"`, `pos_ == "NUM"`, or `ent_type_` is set (named entity).

## Parameters
| Name | Type | Default | Options |
|------|------|---------|---------|
| strictness | select | 1 | 1 – fillers, 2 – +articles/adverbs, 3 – nouns+verbs only |

## Example
**Input:** `The results were very clearly quite significant.`
**Level 1 output:** `The results were clearly significant.`
**Level 2 output:** `results significant.`
**Level 3 output:** `results significant.`

## Pros / Cons / Where it breaks
- ✅ Rules are visible and explainable — great for a viva
- ✅ Always protects negations and numbers
- ❌ Requires spaCy `en_core_web_sm` — unavailable if model fails to load
- ❌ Level 3 output is often not grammatical; use for keyword extraction only

## Typical saving
Level 1: 5–15%. Level 2: 20–35%. Level 3: 40–60%.

