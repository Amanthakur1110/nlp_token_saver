# LLMLingua-2

## What it does
Uses Microsoft's LLMLingua-2 token-classification model to predict which tokens are important and drops the rest. Unlike the other techniques, it works at the **token** level (not sentence or word level), enabling finer-grained compression.

## How it works
1. The `llmlingua` library loads the `microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank` model.
2. Each token in the input is classified as "keep" or "drop" by the model.
3. Tokens marked "drop" are removed; remaining tokens are joined back into text.
4. The `rate` parameter controls the target fraction of tokens to keep.

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| rate | slider | 0.5 | 0.1 | 0.9 | Target compression rate (0.5 = keep ~50% of tokens). |

## Example
**Input:** `Could you please help me understand how this process works in detail?`
**rate=0.5 output:** `help understand process works`
*(Token-level; output may not be fully grammatical.)*

## Pros / Cons / Where it breaks
- ✅ Strongest single-technique compression
- ✅ Gracefully unavailable — shows as greyed out if model fails to load
- ❌ ~700 MB model download on first use
- ❌ Output is not always grammatically correct
- ❌ Works best on meeting transcripts (the model's training domain)

## Typical saving
40–80% depending on rate. Most aggressive technique available.

