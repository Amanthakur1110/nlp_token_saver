# Phrase Substitution

## What it does
Replaces common verbose multi-word phrases with shorter synonyms. For example, "in order to" → "to". No information is lost; only the wording changes.

## How it works
1. Maintain a dictionary of ~40 wordy phrases → short replacements (see `PHRASE_MAP` in the code).
2. Sort phrases longest-first so longer matches take priority over shorter overlapping ones.
3. Apply each substitution with a case-insensitive regex, preserving word boundaries.
4. Clean up any double spaces left by empty replacements (e.g. removing "it is important to note that").

## Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| *(none)* | – | – | The phrase list is hardcoded; no runtime parameters. |

## Example
**Input:** `In order to effectively utilize resources, it is important to note that we must conduct an investigation.`
**Output:** `To effectively use resources, we must investigate.`

## Pros / Cons / Where it breaks
- ✅ Lossless in meaning; very safe
- ✅ Phrase list is readable and easy to extend
- ❌ Only handles known patterns; won't catch novel verbose constructions
- ❌ Context-blind: "utilize" → "use" always, even if the author meant formal register

## Typical saving
3–12% on academic or business writing; less on conversational text.

