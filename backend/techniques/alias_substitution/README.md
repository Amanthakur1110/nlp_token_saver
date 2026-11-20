# Alias Substitution

## What it does
Replaces long phrases that appear repeatedly with short aliases, then defines those aliases in a legend at the top of the output. `expand_aliases()` restores the original text.

## How it works
1. Finds repeated phrases of up to eight words.
2. Estimates each candidate's token savings, including the alias legend, and only replaces phrases with positive net savings.
3. Greedily replaces the best candidate, recounting candidates after each substitution.

## Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `min_occurrences` | slider | 3 | Minimum number of repetitions before considering a phrase. |
| `max_aliases` | slider | 10 | Maximum number of aliases to generate. |

## Usage notes
- Intended for repeated names, email addresses, URLs, and IDs.
- Run this technique last in a chain. Earlier techniques may alter alias symbols or the legend.
- If no candidate provides positive token savings, the input is returned unchanged.
