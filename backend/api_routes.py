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
    Executes Phase 2 → Phase 4 pipeline using mock inputs.
    Returns JSON only.
    
    This is a READ-ONLY endpoint. No side effects.
    """
    try:
        # Get scenario from query param (default None)
        scenario = request.args.get("scenario")
        symbol = request.args.get("symbol")
        
        if scenario == "NORMAL" or scenario == "":
            scenario = None
            
        result = run_demo_scenario(scenario_id=scenario, symbol=symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "OK", "service": "Portfolio Intelligence System"})
