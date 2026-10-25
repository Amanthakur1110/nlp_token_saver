"""
app.py – Flask application factory.

Keeps the factory small: create the app, register blueprints, done.
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes.upload_routes import upload_bp
from routes.technique_routes import technique_bp
from routes.compress_routes import compress_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow requests from the Vite dev server on port 5173
    CORS(app, origins=["http://localhost:5173"])

    # Register route blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(technique_bp)
    app.register_blueprint(compress_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # Return a JSON error (not HTML) for oversized uploads
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large. Maximum is 20 MB."}), 413

    return app


# In-memory store shared across routes: doc_id -> extracted text
# Imported by upload_routes and compress_routes.
doc_store: dict[str, str] = {}

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

