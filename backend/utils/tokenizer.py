"""
tokenizer.py – single function for counting tokens.

Uses tiktoken with the cl100k_base encoding (same as GPT-4).
"""
import tiktoken

# Load the encoder once at module import; it is thread-safe.
_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the number of cl100k_base tokens in text."""
    if not text:
        return 0
    return len(_enc.encode(text))

