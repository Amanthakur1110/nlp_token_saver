"""
config.py – all tuneable settings in one place.
Import this anywhere via: from config import Config
"""
import os


class Config:
    # Maximum upload size (bytes). 20 MB default.
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024

    # File extensions the upload endpoint will accept.
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}

    # Where to store extracted text temporarily (keyed by doc_id).
    # We keep it in memory (a plain dict in the app). No database needed.
    # If you restart the server the doc_id is gone – that is fine for a demo.

    # Anthropic key for the abstractive_llm technique.
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Hugging Face cache directory (mapped to a Docker volume).
    HF_HOME = os.getenv("HF_HOME", "/root/.cache/huggingface")

