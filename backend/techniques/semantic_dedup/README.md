# Semantic Deduplication

## What it does
Encodes sentences with a sentence-transformer and removes any sentence that is too semantically similar to one already kept. More powerful than token-overlap deduplication because it catches paraphrases.

## How it works
1. Split text into sentences.
2. Encode all sentences.
3. Iterate sentences in order. For each sentence, compute cosine similarity to every already-kept sentence.
4. If the maximum similarity ≥ threshold, discard the sentence. Otherwise keep it and add its embedding to the kept list.

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| threshold | slider | 0.85 | 0.5 | 1.0 | Cosine similarity cutoff. Lower = more aggressive. |

## Example
**Input:** `The model achieved 95% accuracy. The neural network reached 95 percent accuracy. Training took 10 hours.`
**threshold=0.80 output:** `The model achieved 95% accuracy. Training took 10 hours.`
*(Second sentence is a paraphrase of the first — removed.)*

## Pros / Cons / Where it breaks
- ✅ Catches paraphrases that exact-match dedup misses
- ✅ Same model as extractive_summary (loaded once, shared)
- ❌ O(n²) similarity comparisons — slow on very long documents
- ❌ Requires sentence-transformers model

## Typical saving
5–25% on documents with paraphrased or repeated ideas (e.g. meeting transcripts, reports).

