"""
API Routes for Portfolio Intelligence System

Market-aware data routing with historical validation support.
Returns JSON-safe output for UI consumption.

Data Source Rules (STRICT):
- Market OPEN  → LIVE DATA ONLY (Alpaca + Polygon)
- Market CLOSED → HISTORICAL DATA ONLY (from cache)
- NO demo data. NO silent fallbacks. NO mixing sources.

Living AI Agent Features:
- Agent Memory: Remembers previous runs for continuity
- Market Crash Toggle: Simulate extreme conditions
- Brain Log: Expose internal reasoning
"""

import sys
import os
import json
from datetime import datetime

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

# Security Hardening: Rate Limiting
from rate_limit import limiter, get_run_limit

api = Blueprint("api", __name__)

# =============================================================================
# AGENT MEMORY (UPGRADE 1)
# =============================================================================

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_memory.json")

# Default memory structure
DEFAULT_MEMORY = {"last_run": None}


def ensure_memory_file():
    """Ensure memory file exists with valid structure."""
    if not os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(DEFAULT_MEMORY, f, indent=2)
            print(f"✅ Created agent memory file: {MEMORY_FILE}")
        except Exception as e:
            print(f"⚠️ Could not create memory file: {e}")


def load_agent_memory() -> dict:
    """Load previous run memory from persistent storage."""
    ensure_memory_file()
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            # Validate structure
            if "last_run" not in data:
                return DEFAULT_MEMORY
            return data
    except Exception as e:
        print(f"⚠️ Failed to load agent memory: {e}")
    return DEFAULT_MEMORY


def save_agent_memory(memory: dict):
    """Persist current run to memory file."""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save agent memory: {e}")


def compute_risk_trend(previous_risk: str, current_risk: str) -> str:
    """
    Compute risk trend based on previous and current risk levels.
    
    Returns:
        RISK_INCREASING, RISK_DECREASING, or STABLE
    """
    risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    prev_val = risk_order.get(previous_risk, 1)
    curr_val = risk_order.get(current_risk, 1)
    
    if curr_val > prev_val:
        return "RISK_INCREASING"
    elif curr_val < prev_val:
        return "RISK_DECREASING"
    return "STABLE"


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

@api.route("/run", methods=["GET", "POST"])
@limiter.limit(get_run_limit)
def run_agent():
    """
    Executes Phase 2 → Phase 4 pipeline.
    Returns JSON only.
    
    Living AI Agent features:
    - Reads previous run from memory
    - Computes risk trend
    - Supports crash simulation override
    - Returns thought log for transparency
    
    Query Params (GET) or JSON Body (POST):
        scenario: Optional scenario override
        symbol: Symbol to analyze
        time_range: Time range for historical data
        simulate_crash: If true, forces defensive posture
    """
    try:
        # Parse parameters from GET or POST
        if request.method == "POST":
            data = request.get_json() or {}
            scenario = data.get("scenario")
            symbol = data.get("symbol")
            time_range = data.get("time_range")
            simulate_crash = data.get("simulate_crash", False)
        else:
            scenario = request.args.get("scenario")
            symbol = request.args.get("symbol")
            time_range = request.args.get("time_range")
            simulate_crash = request.args.get("simulate_crash", "false").lower() == "true"
        
        if scenario == "NORMAL" or scenario == "":
            scenario = None
        
        # =================================================================
        # UPGRADE 1: Load Agent Memory
        # =================================================================
        memory = load_agent_memory()
        previous_run = memory.get("last_run")
        
        previous_posture = previous_run.get("market_posture") if previous_run else None
        previous_risk = previous_run.get("risk_level") if previous_run else None
        
        # =================================================================
        # UPGRADE 2: Crash Simulation Override
        # =================================================================
        crash_context = None
        if simulate_crash:
            crash_context = {
                "force_volatility_state": "EXPANDING",
                "force_news_score": 10,
                "force_sector_confidence": 20  # Force low confidence -> DEFENSIVE posture
            }
            print("🚨 [CRASH SIMULATION] Volatility override engaged")
        
        # =================================================================
        # Run Market-Aware Analysis
        # =================================================================
        result = run_market_aware_analysis(
            scenario_id=scenario, 
            symbol=symbol, 
            time_range=time_range,
            crash_override=crash_context
        )
        
        # =================================================================
        # UPGRADE 1: Compute Memory Insights
        # =================================================================
        current_posture = result.get("analysis", {}).get("market_posture", {}).get("market_posture", "NEUTRAL")
        current_risk = result.get("analysis", {}).get("market_posture", {}).get("risk_level", "MEDIUM")
        
        # Compute trend
        if previous_risk:
            trend = compute_risk_trend(previous_risk, current_risk)
        else:
            trend = "FIRST_RUN"
        
        # Add memory insights to response
        result["memory"] = {
            "previous_posture": previous_posture,
            "previous_risk": previous_risk,
            "current_posture": current_posture,
            "current_risk": current_risk,
            "trend": trend
        }
        
        # =================================================================
        # UPGRADE 2: Add crash simulation flag to response
        # =================================================================
        if simulate_crash:
            result["crash_simulation_active"] = True
            # Inject crash explanation into warnings
            if "analysis" in result:
                if "warnings" not in result["analysis"]:
                    result["analysis"]["warnings"] = []
                result["analysis"]["warnings"].insert(0, {
                    "type": "danger",
                    "message": "🚨 Market Crash Simulation Active — Volatility override engaged. All aggressive allocations blocked."
                })
        
        # =================================================================
        # UPGRADE 1: Persist Current Run to Memory
        # =================================================================
        memory["last_run"] = {
            "timestamp": datetime.now().isoformat(),
            "market_posture": current_posture,
            "risk_level": current_risk
        }
        save_agent_memory(memory)
        
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
    """
    Health check endpoint for deployment monitoring.
    
    Returns agent status, memory state, and timestamp.
    This endpoint must NEVER fail.
    """
    try:
        memory = load_agent_memory()
        memory_enabled = os.path.exists(MEMORY_FILE)
        last_run = memory.get("last_run")
        
        return jsonify({
            "status": "OK",
            "service": "Portfolio Intelligence System",
            "version": "2.0.0-market-aware",
            "agent": {
                "memory_enabled": memory_enabled,
                "has_previous_run": last_run is not None,
                "last_posture": last_run.get("market_posture") if last_run else None,
                "last_risk": last_run.get("risk_level") if last_run else None
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        # Health endpoint must NEVER fail
        return jsonify({
            "status": "OK",
            "service": "Portfolio Intelligence System",
            "version": "2.0.0-market-aware",
            "agent": {
                "memory_enabled": False,
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
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
