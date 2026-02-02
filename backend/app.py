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

# Security Hardening: Environment-based CORS Configuration
env = os.environ.get("ENV", "development")
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")

if env == "production":
    if not allowed_origins_env:
        # Fail safe: Do NOT allow * in production if undefined
        print("❌ CRITICAL SECURITY ERROR: ALLOWED_ORIGINS not set in production.")
        print("   Auto-shutdown to prevent exposure.")
        exit(1)
    
    # Parse list
    allowed_origins = [
        o.strip() for o in allowed_origins_env.split(",") if o.strip()
    ]
    
    CORS(app, origins=allowed_origins, supports_credentials=True)
    print(f"🔒 CORS Restriction: Allowed Origins -> {allowed_origins}")

else:
    # Development: Allow * for convenience if not specified
    if allowed_origins_env:
        allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
        CORS(app, origins=allowed_origins, supports_credentials=True)
    else:
        CORS(app, origins="*")
        print("⚠️  CORS Warning: Allowing '*' for development convenience.")

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
