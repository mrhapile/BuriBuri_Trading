"""
API Routes for Portfolio Intelligence System

Market-aware data routing with historical validation support.
Returns JSON-safe output for UI consumption.

Data Source Rules (STRICT):
- Market OPEN  → LIVE DATA ONLY (Alpaca + Polygon)
- Market CLOSED → HISTORICAL DATA ONLY (from cache)
- NO demo data. NO silent fallbacks. NO mixing sources.
"""

import sys
import os

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request

# Import the market-aware data router
from data_router import (
    get_data_router,
    get_routing_config,
    reset_router
)

# Import the historical data service for metadata
from historical_data_service import (
    get_available_symbols,
    get_time_ranges,
    load_historical_data
)

# Import the decision engine runner
from market_aware_runner import run_market_aware_analysis

api = Blueprint("api", __name__)


# =============================================================================
# MARKET STATUS & DATA ROUTING
# =============================================================================

@api.route("/status", methods=["GET"])
def get_status():
    """
    Get current market status and data routing configuration.
    
    Returns:
        - market_status: OPEN or CLOSED
        - data_mode: LIVE or HISTORICAL
        - data_source: Human-readable source label
        - available_symbols: List of selectable symbols
        - available_time_ranges: Time range options
        - selected_symbol: Current symbol
        - selected_time_range: Current time range
        - controls_enabled: Which UI controls are active
    """
    try:
        config = get_routing_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/set-symbol", methods=["POST"])
def set_symbol():
    """
    Set the selected symbol for analysis.
    
    Only works when market is CLOSED (historical mode).
    When market is OPEN, symbols reflect live portfolio holdings.
    
    Request Body:
        { "symbol": "SPY" }
    
    Returns:
        Updated routing configuration
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        
        if not symbol:
            return jsonify({
                "error": "Symbol is required",
                "status": "FAILED"
            }), 400
        
        router = get_data_router()
        config = router.set_symbol(symbol)
        return jsonify(config)
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 400
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/set-time-range", methods=["POST"])
def set_time_range():
    """
    Set the selected time range for historical data.
    
    Only works when market is CLOSED (historical mode).
    Disabled when market is OPEN.
    
    Request Body:
        { "time_range": "6M" }  # Options: 1M, 4M, 6M, 1Y
    
    Returns:
        Updated routing configuration
    """
    try:
        data = request.get_json()
        time_range = data.get("time_range")
        
        if not time_range:
            return jsonify({
                "error": "Time range is required",
                "status": "FAILED"
            }), 400
        
        router = get_data_router()
        config = router.set_time_range(time_range)
        return jsonify(config)
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 400
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/available-symbols", methods=["GET"])
def available_symbols():
    """
    Get list of available symbols for historical analysis.
    
    Returns:
        { "symbols": ["SPY", "QQQ", "IWM", ...] }
    """
    try:
        symbols = get_available_symbols()
        return jsonify({
            "symbols": symbols,
            "count": len(symbols)
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


@api.route("/time-ranges", methods=["GET"])
def time_ranges():
    """
    Get available time range options.
    
    Returns:
        { "time_ranges": { "1M": {...}, "4M": {...}, ... } }
    """
    try:
        ranges = get_time_ranges()
        return jsonify({
            "time_ranges": ranges
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

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
        time_range = request.args.get("time_range")
        
        if scenario == "NORMAL" or scenario == "":
            scenario = None
            
        result = run_demo_scenario(scenario_id=scenario, symbol=symbol)
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"❌ API Execution Error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500


# =============================================================================
# HEALTH & DIAGNOSTICS
# =============================================================================

@api.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "OK",
        "service": "Portfolio Intelligence System",
        "version": "2.0.0-market-aware"
    })


@api.route("/reset", methods=["POST"])
def reset_state():
    """
    Reset the data router state.
    Useful for re-initializing after market status changes.
    """
    try:
        reset_router()
        config = get_routing_config()
        return jsonify({
            "status": "OK",
            "message": "Router reset successfully",
            "config": config
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "FAILED"
        }), 500
