"""
compress_routes.py – POST /api/compress

Accepts a doc_id and a list of techniques (with params),
runs the pipeline, and returns the full report JSON.
"""
from flask import Blueprint, request, jsonify

from pipeline.cleaner import clean_text
from pipeline.runner import run_techniques
from pipeline.report import build_report

compress_bp = Blueprint("compress", __name__)

# Named presets so the frontend "preset buttons" need no hardcoded logic.
# Each preset is a list of {id, params} dicts.
PRESETS = {
    "safe": [
        {"id": "whitespace_cleanup", "params": {}},
        {"id": "deduplication",      "params": {"threshold": 0.95}},
        {"id": "phrase_substitution","params": {}},
    ],
    "balanced": [
        {"id": "whitespace_cleanup", "params": {}},
        {"id": "deduplication",      "params": {"threshold": 0.85}},
        {"id": "phrase_substitution","params": {}},
        {"id": "stopword_removal",   "params": {"protected_words": []}},
        {"id": "tfidf_pruning",      "params": {"keep_pct": 70}},
    ],
    "max_saver": [
        {"id": "whitespace_cleanup", "params": {}},
        {"id": "deduplication",      "params": {"threshold": 0.80}},
        {"id": "phrase_substitution","params": {}},
        {"id": "grammar_based",      "params": {"strictness": 2}},
        {"id": "tfidf_pruning",      "params": {"keep_pct": 50}},
        {"id": "extractive_summary", "params": {"keep_pct": 40}},
    ],
}


@compress_bp.post("/api/compress")
def compress():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required."}), 400

    doc_id = body.get("doc_id")
    if not doc_id:
        return jsonify({"error": "doc_id is required."}), 400

    from app import doc_store
    raw_text = doc_store.get(doc_id)
    if raw_text is None:
        return jsonify({"error": "Document not found. Please re-upload."}), 404

    # Allow a preset name in place of a techniques list
    preset_name = body.get("preset")
    if preset_name:
        techniques = PRESETS.get(preset_name)
        if techniques is None:
            return jsonify({"error": f"Unknown preset '{preset_name}'."}), 400
    else:
        techniques = body.get("techniques", [])

    if not techniques:
        return jsonify({"error": "No techniques selected."}), 400

    mode = body.get("mode", "both")  # "individual" | "chain" | "both"

    # Stage 2: basic normalization before any technique
    cleaned = clean_text(raw_text)

    # Stage 3 + 4 + 5: run, measure, diff
    results = run_techniques(cleaned, techniques, mode)

    # Stage 6: assemble final JSON
    report = build_report(doc_id, cleaned, results, mode)

    return jsonify(report)


@compress_bp.get("/api/presets")
def list_presets():
    """Return preset names and their technique lists."""
    return jsonify({name: techs for name, techs in PRESETS.items()})

