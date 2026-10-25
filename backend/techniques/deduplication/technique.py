"""
technique.py – Deduplication

Removes exact and near-duplicate sentences.
Near-duplicates use Jaccard token overlap, but two sentences are never
treated as duplicates if their numbers or negations differ.
"""
import re
import pysbd
from techniques.base import BaseTechnique

# pysbd handles abbreviations (Dr., etc.) and quotes better than a regex
_segmenter = pysbd.Segmenter(language="en", clean=False)

_NEGATIONS = {"not", "no", "never", "cannot", "nor", "none", "without"}


def _normalise(sentence: str) -> str:
    """Lowercase, expand n't, strip punctuation, collapse spaces."""
    s = sentence.lower().replace("’", "'").replace("n't", " not")
    s = re.sub(r"[^\w\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


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
        "Removes exact and near-duplicate sentences. "
        "Jaccard token similarity controls how aggressive the dedup is. "
        "Sentences with different numbers or negations are always kept."
    )
    params_schema = [
        {
            "name": "threshold",
            "type": "slider",
            "label": "Similarity threshold (1.0 = exact only)",
            "default": 0.9,
            "min": 0.5,
            "max": 1.0,
            "step": 0.05,
        }
    ]

    def apply(self, text: str, params: dict) -> str:
        threshold = float(params.get("threshold", 0.9))

        seen_exact = set()   # normalised sentences, for the fast exact check
        kept_sets = []       # token sets of kept sentences, for near-dup check
        out_paragraphs = []

        # work paragraph by paragraph so line structure survives
        for paragraph in re.split(r"\n\s*\n", text.strip()):
            kept = []
            for sentence in _segmenter.segment(paragraph):
                sentence = sentence.strip()
                norm = _normalise(sentence)
                if not norm:                       # punctuation-only, keep as is
                    kept.append(sentence)
                    continue
                if norm in seen_exact:             # exact duplicate
                    continue
                tokens = set(norm.split())
                if _is_near_duplicate(tokens, kept_sets, threshold):
                    continue
                seen_exact.add(norm)
                kept_sets.append(tokens)
                kept.append(sentence)
            if kept:                               # drop paragraphs that became empty
                out_paragraphs.append(" ".join(kept))

        return "\n\n".join(out_paragraphs)