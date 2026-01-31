"""
Flask Backend for Portfolio Intelligence System

READ-ONLY API that exposes Python engine output to the web UI.
No state. No mutations. No execution. Pure intelligence relay.
"""

from flask import Flask
from flask_cors import CORS
from api_routes import api

app = Flask(__name__)
CORS(app)
app.register_blueprint(api)

if __name__ == "__main__":
    print("=" * 60)
    print("Portfolio Intelligence System - Backend API")
    print("=" * 60)
    print("Endpoint: http://localhost:5000/run")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, port=5000)
