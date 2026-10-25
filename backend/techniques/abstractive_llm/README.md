# Abstractive LLM Compression (optional)

## What it does
Sends the text to Anthropic's Claude API and asks it to rewrite the content concisely at a target word ratio. Unlike all other techniques this one **generates new text**, not a subset of the original.

> ⚠ **This technique spends API tokens from your Anthropic quota.**

## How it works
1. Calculate target word count = `len(original.split()) × target_ratio`.
2. Send a prompt to `claude-3-haiku-20240307` (the cheapest Claude model) with the text and the target word count.
3. Return the model's response as the compressed text.

## Parameters
| Name | Type | Default | Min | Max | Description |
|------|------|---------|-----|-----|-------------|
| target_ratio | slider | 0.4 | 0.1 | 0.8 | Target length as a fraction of original word count. |

## Example
**Input:** `In order to effectively utilize the available resources, the team conducted a thorough investigation into the matter.`
**target_ratio=0.4 output:** `The team investigated resource utilization.`

## Pros / Cons / Where it breaks
- ✅ Highest quality compression — LLM understands meaning
- ✅ Can rewrite, not just extract, so output is fluent
- ❌ Requires ANTHROPIC_API_KEY; shows as unavailable without it
- ❌ Costs money per run; latency depends on API
- ❌ Hallucination risk: model may subtly change facts

## Typical saving
40–70% token reduction with high semantic fidelity.

