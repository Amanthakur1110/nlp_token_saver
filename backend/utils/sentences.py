"""Shared text helpers so every technique cuts and checks text the same way."""
import pysbd

_seg = pysbd.Segmenter(language="en", clean=False)

_QUOTES = ('"', "“", "”")


def split_sentences(line: str) -> list[str]:
    """Split one line/paragraph into sentences (handles Dr., quotes, etc.)."""
    return [s.strip() for s in _seg.segment(line) if s.strip()]


def is_heading(line: str) -> bool:
    """Short line with no sentence-ending punctuation = heading."""
    line = line.strip()
    return len(line.split()) <= 8 and not line.endswith((".", "!", "?", '"'))


def is_protected(sentence: str) -> bool:
    """Sentences with numbers or quotes carry facts, so they are never dropped."""
    has_number = any(c.isdigit() for c in sentence)
    has_quote = any(q in sentence for q in _QUOTES)
    return has_number or has_quote