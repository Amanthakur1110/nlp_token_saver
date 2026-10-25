"""
cleaner.py – Stage 2: basic normalisation applied BEFORE any technique.

Keeps only changes that are universally safe (Unicode fixes, line endings,
trailing spaces, re-joining lines that the PDF wrapped). Heavier cleanup
(headers, footers, page numbers) is left to the whitespace_cleanup technique
so users can see what it does.
"""
import re
import unicodedata

# A line starting like this is a bullet or numbered item, never a wrapped line
_BULLET = re.compile(r"^\s*([-•*]|\d+[.)])\s")

# Characters that normally end a sentence (a closing quote counts too)
_SENTENCE_END = (".", "!", "?", ":", '"', "”")

# PDF lines are cut by page width, so a wrapped line is usually long
_MIN_WRAPPED_LEN = 60


def join_wrapped_lines(text: str) -> str:
    """
    Join hard-wrapped PDF lines inside a paragraph into one line.

    A line is joined to the previous one only if the previous line looks
    cut by the page width: it is long and does not end a sentence.
    Headings, bullets and short lines stay on their own line.
    This is a heuristic, so it can be wrong on unusual layouts.
    """
    paragraphs = []
    for para in text.split("\n\n"):
        merged = []
        for line in para.split("\n"):
            line = line.strip()
            if not line:
                continue
            prev = merged[-1] if merged else ""
            wrapped = (
                prev
                and len(prev) >= _MIN_WRAPPED_LEN
                and not prev.endswith(_SENTENCE_END)
                and not _BULLET.match(line)
            )
            if wrapped:
                merged[-1] = prev + " " + line
            else:
                merged.append(line)
        paragraphs.append("\n".join(merged))
    return "\n\n".join(paragraphs)


def clean_text(text: str) -> str:
    """
    Minimal normalisation:
    1. Normalise Unicode to NFC (fixes broken accents from PDF extraction).
    2. Replace Windows/old Mac line endings with Unix.
    3. Strip trailing whitespace from every line.
    4. Collapse runs of 3+ blank lines to 2 (preserve paragraph breaks).
    5. Join hard-wrapped lines inside paragraphs.
    """
    # 1. Fix unicode artefacts from PDF text extraction
    text = unicodedata.normalize("NFC", text)

    # 2. Unify line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Strip trailing spaces from each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # 4. Max 2 consecutive newlines (keeps paragraph gaps readable)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Re-join lines that the PDF cut in the middle of a sentence
    text = join_wrapped_lines(text)

    return text.strip()