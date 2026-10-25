# TF-IDF Pruning

## What it does
Scores every sentence by the average TF-IDF weight of its words (relative to the whole document), then discards the lowest-scoring sentences. Keeps the top `keep%` sentences in their original order.

## How it works
1. Split text into sentences.
2. Fit a TF-IDF vectorizer with all sentences as the corpus (each sentence = one document).
3. Score each sentence as the mean of its non-zero TF-IDF values.
4. Rank sentences by score; select top `keep%`.
5. Re-emit selected sentences in the original order (not by score).

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| keep_pct | slider | 60 | 10 | 100 | Percentage of sentences to keep. |

## Example
**Input (3 sentences):** `TF-IDF finds important words. The quick brown fox. Results show TF-IDF works well.`
**keep_pct=67 output:** `TF-IDF finds important words. Results show TF-IDF works well.`

## Pros / Cons / Where it breaks
- ✅ No neural model needed; fast
- ✅ Keeps original sentence order — output is still readable
- ❌ Scores are document-relative; short documents give poor scores
- ❌ Ignores cross-sentence semantic relationships

## Typical saving
10–60% depending on keep_pct.

