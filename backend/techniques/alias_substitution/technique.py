
import re
from collections import Counter

from techniques.base import BaseTechnique
from utils.tokenizer import count_tokens


_WORD = re.compile(r"\w(?:[\w@.\-/:]*\w)?")
_ALIAS_FORMATS = ["§{}", "¤{}", "@{}", "#{}", "${}", "^{}"]
_MAX_NGRAM = 8
_SHORTLIST = 150


def _find_candidates(text: str, min_occ: int) -> Counter:
    """Count phrases of 1.._MAX_NGRAM words joined by single spaces."""
    words = list(_WORD.finditer(text))
    counts = Counter()
    for i in range(len(words)):
        for n in range(1, _MAX_NGRAM + 1):
            j = i + n - 1
            if j >= len(words):
                break
            if n > 1 and text[words[j - 1].end():words[j].start()] != " ":
                break
            phrase = text[words[i].start():words[j].end()]
            if len(phrase) >= 6:
                counts[phrase] += 1
    return Counter({phrase: count for phrase, count in counts.items() if count >= min_occ})


def _make_aliases(text: str, how_many: int) -> list[str]:
    """Pick cheap aliases that do not already occur in the input."""
    pool = []
    for fmt in _ALIAS_FORMATS:
        for i in range(1, how_many + 1):
            alias = fmt.format(i)
            if alias not in text:
                pool.append((count_tokens(alias), alias))
    pool.sort(key=lambda item: item[0])
    return [alias for _, alias in pool[:how_many]]


def _replacement_pattern(phrase: str) -> re.Pattern:
    return re.compile(r"(?<![\w@./:-])" + re.escape(phrase) + r"(?![\w@/:-])")


def _replace(text: str, phrase: str, alias: str) -> tuple[str, int]:
    """Replace whole, non-overlapping occurrences and return their count."""
    return _replacement_pattern(phrase).subn(lambda _: alias, text)


def expand_aliases(text: str) -> str:
    """Expand aliases from the leading legend back to their original phrases."""
    match = re.match(r"\[Legend: (.*?)\]\n\n", text, flags=re.S)
    if not match:
        return text

    aliases = {}
    for entry in match.group(1).split(" | "):
        alias, phrase = entry.split(" = ", 1)
        aliases[alias] = phrase

    body = text[match.end():]
    pattern = re.compile("|".join(
        re.escape(alias) for alias in sorted(aliases, key=len, reverse=True)
    ))
    return pattern.sub(lambda found: aliases[found.group()], body)


class AliasSubstitution(BaseTechnique):
    id = "alias_substitution"
    name = "Alias Substitution"
    description = (
        "Replaces long repeated phrases (emails, URLs, names, IDs) with short "
        "aliases defined once in a legend. Lossless. Only replaces when the "
        "net token saving, including the legend, is positive. Use last in a chain."
    )
    params_schema = [
        {"name": "min_occurrences", "type": "slider", "label": "Minimum repeats",
         "default": 3, "min": 2, "max": 10, "step": 1},
        {"name": "max_aliases", "type": "slider", "label": "Maximum aliases",
         "default": 10, "min": 1, "max": 30, "step": 1},
    ]

    def apply(self, text: str, params: dict) -> str:
        min_occ = int(params.get("min_occurrences", 3))
        max_aliases = int(params.get("max_aliases", 10))
        aliases = _make_aliases(text, max_aliases)

        body = text
        legend = []

        for alias in aliases:
            counts = _find_candidates(body, min_occ)
            if not counts:
                break

            shortlist = sorted(
                counts, key=lambda phrase: counts[phrase] * len(phrase), reverse=True
            )[:_SHORTLIST]
            alias_tokens = count_tokens(alias)
            best_phrase, best_gain = None, 0
            for phrase in shortlist:
                phrase_tokens = count_tokens(phrase)
                _, occurrence_count = _replace(body, phrase, alias)
                gain = (
                    occurrence_count * (phrase_tokens - alias_tokens)
                    - (phrase_tokens + alias_tokens + 2)
                )
                if gain > best_gain:
                    best_phrase, best_gain = phrase, gain

            if best_phrase is None:
                break

            body, _ = _replace(body, best_phrase, alias)
            legend.append((alias, best_phrase))

        if not legend:
            return text

        header = "[Legend: " + " | ".join(
            f"{alias} = {phrase}" for alias, phrase in legend
        ) + "]\n\n"
        return header + body
