"""
Flask Backend for Portfolio Intelligence System

READ-ONLY API that exposes Python engine output to the web UI.
No state. No mutations. No execution. Pure intelligence relay.

DEPLOYMENT:
    - Binds to 0.0.0.0 for cloud environments
    - Port from PORT env var (default: 10000 for Render)
    - CORS enabled for cross-origin requests
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from api_routes import api

app = Flask(__name__)

# Security Hardening: Enforce 2MB request size limit to prevent DoS
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB

# Security Hardening: Graceful handling of oversized payloads
@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_error(e):
    return jsonify({"error": "Request payload too large"}), 413

CORS(app, origins="*")  # Allow all origins for deployment
app.register_blueprint(api)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("Portfolio Intelligence System - Backend API")
    print("=" * 60)
    print(f"Binding to: {host}:{port}")
    print("Endpoint: /run")
    print("Health: /health")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host=host, port=port, debug=False)
