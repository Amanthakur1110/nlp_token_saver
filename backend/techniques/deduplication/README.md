# Deduplication

## What it does
Removes repeated sentences. Works for both exact duplicates (copy-pasted text) and near-duplicates (same sentence with minor word changes). Common in reports with repeated boilerplate.

## How it works
1. Split the text into sentences on `.!?` punctuation.
2. Normalise each sentence: lowercase, strip punctuation, collapse spaces.
3. Convert each sentence to a **token set**.
4. For each sentence, compute **Jaccard similarity** with every already-kept sentence: `|A ∩ B| / |A ∪ B|`.
5. If similarity ≥ threshold, discard the sentence. Otherwise keep it.

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| threshold | slider | 0.9 | 0.5 | 1.0 | Jaccard threshold. 1.0 = exact match only. 0.5 = very aggressive. |

## Example
**Input:** `The cat sat on the mat. The cat sat on the mat.`
**Output:** `The cat sat on the mat.`

## Pros / Cons / Where it breaks
- ✅ Fast — O(n²) on sentences, not words
- ✅ Configurable aggressiveness
- ❌ Jaccard is order-insensitive, so reordered sentences still match
- ❌ Very short sentences (1–2 words) will often trigger false positives at low thresholds

## Typical saving
5–30% depending on how repetitive the source document is.

