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
from flask import Flask
from flask_cors import CORS
from api_routes import api

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for deployment

# Security Hardening: API Rate Limiting
from rate_limit import limiter, get_global_limit
limiter.init_app(app)
# Apply global default limit
limiter._default_limits = [get_global_limit()]

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
