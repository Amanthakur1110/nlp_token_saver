
import re

import pysbd

from techniques.base import BaseTechnique

# pysbd handles abbreviations (Dr., Rs.) and quotes better than a regex
_segmenter = pysbd.Segmenter(language="en", clean=False)


def split_sentences(line: str) -> list[str]:
    """Split one line into sentences. Odd input is kept as one sentence."""
    try:
        return [s.strip() for s in _segmenter.segment(line) if s.strip()]
    except Exception:
        return [line.strip()] if line.strip() else []


_NEGATIONS = {"not", "no", "never", "cannot", "nor", "none", "without"}

# Labels that show a line is a list item / option / question number
_STARTS_WITH_MARKER = re.compile(
    r"^\s*(?:"
    r"[(\[](?:[A-Za-z]{1,5}|\d{1,3})[)\]]"        # (A) (i) (iv) [1] (10)
    r"|(?:[A-Za-z]|\d{1,3}|[ivxIVX]{2,5})[.)]\s"  # 1. a) A. iv)
    r"|[-•●○▪*–—]\s"                              # bullets
    r"|Q\.?\s*\d+"                                # Q3  Q.3
    r"|Question\s+\d+"
    r")"
)
_ENDS_WITH_MARKER = re.compile(r"[(\[](?:[A-Za-z]{1,5}|\d{1,3})[)\]]\s*$")


def _normalise(sentence: str) -> str:
    """Lowercase, expand n't, strip punctuation, collapse spaces."""
    s = sentence.lower().replace("’", "'").replace("n't", " not")
    s = re.sub(r"[^\w\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _word_count(sentence: str) -> int:
    """Words that contain at least one letter (works for Hindi etc. too)."""
    return sum(1 for w in sentence.split() if any(ch.isalpha() for ch in w))


def _letter_ratio(sentence: str) -> float:
    chars = [c for c in sentence if not c.isspace()]
    return sum(c.isalpha() for c in chars) / len(chars) if chars else 0.0


def _is_comparable(sentence: str, min_words: int) -> bool:
    """True only for real sentences that are safe to compare for duplicates."""
    s = sentence.strip()
    if _STARTS_WITH_MARKER.match(s):
        return False                       # list item / option / question label
    if s.endswith(":") or _ENDS_WITH_MARKER.search(s):
        return False                       # lead-in to a list
    if _word_count(s) < min_words:
        return False                       # too short: meaning depends on position
    if _letter_ratio(s) < 0.6:
        return False                       # mostly digits/symbols: a code
    return True


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _numbers(tokens: set) -> set:
    return {t for t in tokens if any(c.isdigit() for c in t)}


def _negations(tokens: set) -> set:
    return tokens & _NEGATIONS


def _is_near_duplicate(tokens: set, kept_sets: list, threshold: float) -> bool:
    """Similar enough AND same numbers AND same negations."""
    for other in kept_sets:
        if (_jaccard(tokens, other) >= threshold
                and _numbers(tokens) == _numbers(other)
                and _negations(tokens) == _negations(other)):
            return True
    return False


class Deduplication(BaseTechnique):
    id = "deduplication"
    name = "Deduplication"
    description = (
        "Removes exact and near-duplicate sentences. Short fragments, list "
        "items, options (A)(B)(i)(ii), numbers and page codes are never removed. "
        "Sentences with different numbers or negations are always kept."
    )
    params_schema = [
        {"name": "threshold", "type": "slider",
         "label": "Similarity threshold (1.0 = exact only)",
         "default": 0.9, "min": 0.5, "max": 1.0, "step": 0.05},
        {"name": "min_words", "type": "slider",
         "label": "Ignore sentences shorter than N words",
         "default": 8, "min": 3, "max": 20, "step": 1},
    ]

    def apply(self, text: str, params: dict) -> str:
        threshold = float(params.get("threshold", 0.9))
        min_words = int(params.get("min_words", 8))

        seen_exact = set()   # normalised sentences, for the fast exact check
        kept_sets = []       # token sets of kept sentences, for the near check
        out_lines = []

        for line in text.split("\n"):            # line by line: keeps the layout
            if not line.strip():
                out_lines.append("")
                continue
            kept = []
            for sentence in split_sentences(line):
                if not _is_comparable(sentence, min_words):
                    kept.append(sentence)        # protected: always kept
                    continue
                norm = _normalise(sentence)
                if norm in seen_exact:
                    continue                     # exact duplicate
                tokens = set(norm.split())
                if _is_near_duplicate(tokens, kept_sets, threshold):
                    continue
                seen_exact.add(norm)
                kept_sets.append(tokens)
                kept.append(sentence)
            if kept:                             # a line with nothing left vanishes
                out_lines.append(" ".join(kept))

        return re.sub(r"\n{3,}", "\n\n", "\n".join(out_lines)).strip()