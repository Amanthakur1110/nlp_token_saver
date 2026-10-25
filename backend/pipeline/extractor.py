"""
extractor.py – Stage 1: file bytes -> plain text.

Each format has its own small function so failures are isolated.
Returns (text, error) – caller checks error before using text.
"""
import io
import re
from werkzeug.datastructures import FileStorage


# ── PDF ──────────────────────────────────────────────────────────────────────

def _extract_pdf(file_bytes: bytes) -> tuple[str, str]:
    """Use PyMuPDF (fitz) to extract text from each page."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return "", "PyMuPDF not installed."

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return "", f"Cannot open PDF: {e}"

    pages = [page.get_text() for page in doc]
    text = "\n".join(pages).strip()

    if not text:
        return "", "PDF appears to be a scanned image with no embedded text."
    return text, ""


# ── DOCX ─────────────────────────────────────────────────────────────────────

def _extract_docx(file_bytes: bytes) -> tuple[str, str]:
    """Read paragraph text from a DOCX file."""
    try:
        from docx import Document
    except ImportError:
        return "", "python-docx not installed."

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as e:
        return "", f"Cannot open DOCX: {e}"

    lines = [para.text for para in doc.paragraphs]
    text = "\n".join(lines).strip()

    if not text:
        return "", "DOCX file contains no readable text."
    return text, ""


# ── TXT / MD ─────────────────────────────────────────────────────────────────

def _extract_plain(file_bytes: bytes) -> tuple[str, str]:
    """Decode as UTF-8 (with fallback to latin-1) for TXT and MD files."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    text = text.strip()
    if not text:
        return "", "File is empty."
    return text, ""


# ── Dispatcher ────────────────────────────────────────────────────────────────

def extract_text(file: FileStorage) -> tuple[str, str]:
    """
    Read the uploaded file and return (plain_text, error_message).
    If error_message is non-empty the caller should abort with a 422.
    """
    file_bytes = file.read()

    if not file_bytes:
        return "", "Uploaded file is empty."

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext == "docx":
        return _extract_docx(file_bytes)
    elif ext in ("txt", "md"):
        return _extract_plain(file_bytes)
    else:
        return "", f"Unsupported extension: .{ext}"

