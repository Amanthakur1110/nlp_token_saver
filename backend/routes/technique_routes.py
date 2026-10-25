"""
technique_routes.py – GET /api/techniques

Returns the list of all registered techniques so the frontend
can render their names, descriptions, and parameter controls.
"""
from flask import Blueprint, jsonify
from techniques.registry import get_all_techniques

technique_bp = Blueprint("technique", __name__)


@technique_bp.get("/api/techniques")
def list_techniques():
    techniques = []
    for t in get_all_techniques():
        available, reason = t.is_available()
        techniques.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "params_schema": t.params_schema,
            "available": available,
            "unavailable_reason": reason,
        })
    return jsonify(techniques)

