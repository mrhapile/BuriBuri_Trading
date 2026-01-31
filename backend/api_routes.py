"""
API Routes for Portfolio Intelligence System

Single endpoint that executes the full decision pipeline.
Returns JSON-safe output for UI consumption.
"""

import sys
import os

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request
from full_system_demo import run_demo_scenario

api = Blueprint("api", __name__)


@api.route("/run", methods=["GET"])
def run_agent():
    """
    Executes Phase 2 → Phase 4 pipeline.
    Routed by Market Status.
    Returns JSON only.
    """
    try:
        # Get parameters from query string
        scenario = request.args.get("scenario")
        symbol = request.args.get("symbol")
        time_range = request.args.get("time_range")
        
        if scenario == "NORMAL" or scenario == "":
            scenario = None
            
        # Execute Pipeline
        result = run_demo_scenario(
            scenario_id=scenario, 
            symbol=symbol, 
            time_range=time_range
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"❌ API Execution Error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "OK", "service": "Portfolio Intelligence System"})
