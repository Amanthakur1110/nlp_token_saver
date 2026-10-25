"""
diff.py – Stage 5: produce original-text segments for the UI.

Compare word and punctuation tokens so the UI can highlight only removed
content while preserving the complete original text and its whitespace.
"""
import difflib
import re

_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def _append_segment(segments: list[dict], text: str, status: str) -> None:
    """Append text while merging adjacent segments with the same status."""
    if not text:
        return
    if segments and segments[-1]["status"] == status:
        segments[-1]["text"] += text
    else:
        segments.append({"text": text, "status": status})


def build_diff(original: str, compressed: str) -> dict:
    """
    Compare original and compressed text at the word/punctuation level.
    Returns original-text segments marked as kept or removed and contiguous
    removed phrases for the UI.
    """
    original_tokens = list(_TOKEN_RE.finditer(original))
    compressed_tokens = list(_TOKEN_RE.finditer(compressed))
    original_keys = [match.group().casefold() for match in original_tokens]
    compressed_keys = [match.group().casefold() for match in compressed_tokens]
    kept = [False] * len(original_tokens)

    matcher = difflib.SequenceMatcher(a=original_keys, b=compressed_keys)
    for tag, start, end, _, _ in matcher.get_opcodes():
        if tag == "equal":
            kept[start:end] = [True] * (end - start)

    segments = []
    previous_end = 0
    for index, match in enumerate(original_tokens):
        gap = original[previous_end:match.start()]
        gap_status = (
            "removed"
            if (
                index > 0
                and not kept[index - 1]
                and not kept[index]
                and original_tokens[index - 1].group() not in {".", "!", "?"}
            )
            else "kept"
        )
        _append_segment(segments, gap, gap_status)
        _append_segment(
            segments,
            match.group(),
            "kept" if kept[index] else "removed",
        )
        previous_end = match.end()
    _append_segment(segments, original[previous_end:], "kept")

    removed_list = [
        segment["text"]
        for segment in segments
        if segment["status"] == "removed"
    ]

    return {
        "segments": segments,
        "removed_list": removed_list,
    }
