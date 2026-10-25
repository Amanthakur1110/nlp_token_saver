# Extractive Summary

## What it does
Encodes every sentence with a multilingual sentence-transformer model, computes the document centroid (mean embedding), and keeps the sentences closest to the centroid — the most "representative" ones — in original order.

## How it works
1. Split text into sentences.
2. Encode all sentences with `paraphrase-multilingual-MiniLM-L12-v2`.
3. Compute the centroid: mean of all sentence embeddings.
4. Score each sentence by cosine similarity to the centroid.
5. Keep top `keep%` sentences; re-emit in their original order.

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| keep_pct | slider | 50 | 10 | 90 | Percentage of sentences to keep. |

## Example
**Input:** `Neural networks learn features. The sky is blue. Deep learning is a subset of machine learning.`
**keep_pct=67:** `Neural networks learn features. Deep learning is a subset of machine learning.`
*(The unrelated "sky" sentence scores lowest.)*

## Pros / Cons / Where it breaks
- ✅ Semantic — keeps the most on-topic sentences, not just TF-IDF-scored ones
- ✅ Original order is preserved
- ❌ Requires sentence-transformers (~400 MB model download)
- ❌ Centroid approach treats the document as having one topic; breaks on multi-topic texts

## Typical saving
10–70% depending on keep_pct; quality higher than TF-IDF for mixed-topic documents.

