"""
upload_routes.py – POST /api/upload

Accepts a file, extracts its text, stores it keyed by a UUID,
and returns a preview + token count to the frontend.
"""
import uuid
from flask import Blueprint, request, jsonify

from config import Config
from pipeline.extractor import extract_text
from utils.tokenizer import count_tokens

upload_bp = Blueprint("upload", __name__)


def _allowed(filename: str) -> bool:
    """Return True if the file extension is in the allowed set."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


@upload_bp.post("/api/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename."}), 400
    if not _allowed(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"}), 400

    # extract_text returns (text, error_message)
    text, err = extract_text(file)
    if err:
        return jsonify({"error": err}), 422

    doc_id = str(uuid.uuid4())

    # Lazy import to avoid circular: app.doc_store is the shared dict
    from app import doc_store
    doc_store[doc_id] = text

    preview = text[:500].strip()  # first 500 chars as a quick preview

    return jsonify({
        "doc_id": doc_id,
        "filename": file.filename,
        "char_count": len(text),
        "token_count": count_tokens(text),
        "preview": preview,
    })

