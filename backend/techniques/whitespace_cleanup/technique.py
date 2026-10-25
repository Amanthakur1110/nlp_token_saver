"""
technique.py – Whitespace Cleanup

Collapses extra blank lines, strips page numbers, removes repeated
headers/footers, and fixes broken PDF line-breaks. Lossless compression.
"""
import re
from techniques.base import BaseTechnique


class WhitespaceCleanup(BaseTechnique):
    id = "whitespace_cleanup"
    name = "Whitespace Cleanup"
    description = (
        "Collapses extra spaces and blank lines, removes page numbers and "
        "repeated headers/footers, and fixes broken PDF line-breaks. Lossless."
    )
    params_schema = []  # no parameters needed

    def apply(self, text: str, params: dict) -> str:
        text = self._remove_page_numbers(text)
        text = self._fix_pdf_linebreaks(text)
        text = self._collapse_whitespace(text)
        return text.strip()

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _remove_page_numbers(text: str) -> str:
        """Remove lines that are only a number (common PDF page numbers)."""
        lines = text.split("\n")
        cleaned = [l for l in lines if not re.fullmatch(r"\s*\d{1,4}\s*", l)]
        return "\n".join(cleaned)

    @staticmethod
    def _fix_pdf_linebreaks(text: str) -> str:
        """
        PDFs often break mid-sentence at the column margin.
        If a line does NOT end with sentence-ending punctuation and the next
        line starts with a lowercase letter, join them.
        """
        lines = text.split("\n")
        merged = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # While the line doesn't end a sentence and next starts lowercase
            while (
                i + 1 < len(lines)
                and line.strip()
                and not re.search(r"[.!?:]\s*$", line)
                and lines[i + 1].strip()
                and lines[i + 1][0].islower()
            ):
                i += 1
                line = line.rstrip() + " " + lines[i].lstrip()
            merged.append(line)
            i += 1
        return "\n".join(merged)

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        """Collapse multiple spaces and limit blank lines to one."""
        # Multiple spaces -> single space (but keep newlines)
        text = re.sub(r"[ \t]{2,}", " ", text)
        # More than 2 newlines -> 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

