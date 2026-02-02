"""
market_aware_runner.py

Market-Aware Analysis Runner.
Integrates the data router with the decision engine for market-aware analysis.

STRICT DATA SOURCE RULES:
- Market OPEN  → LIVE DATA ONLY (Alpaca + Polygon)
- Market CLOSED → HISTORICAL DATA ONLY (from cache)
- NO demo data
- NO silent fallbacks
- NO mixing sources
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Ensure backend directory is in path for imports
_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Core decision engine modules
import volatility_metrics
import news_scorer
import sector_confidence
import decision_engine
import execution_planner
import execution_summary

# Market-aware data routing
from data_router import (
    get_data_router,
    get_routing_config,
    DATA_MODE_LIVE,
    DATA_MODE_HISTORICAL
)

# Scenario support (for testing only)
from scenarios import get_scenario

# Security Hardening: Log Safety
import backend.log_safety as log_safety


def run_market_aware_analysis(
    scenario_id: Optional[str] = None,
    symbol: Optional[str] = None,
    time_range: Optional[str] = None,
    crash_override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run the full decision pipeline using market-aware data routing.
    
    STRICT behavior:
    - Market OPEN: Uses live Alpaca + Polygon data
    - Market CLOSED: Uses historical cache data ONLY
    
    Args:
        scenario_id: Optional scenario override (for testing)
        symbol: Optional symbol override (historical mode only)
        time_range: Optional time range (historical mode only)
        crash_override: Optional crash simulation context (UPGRADE 2)
    
    Returns:
        Complete analysis result with:
        - market_status
        - data_mode
        - data_source
        - routing_config
        - analysis
        - thought_log (UPGRADE 3)
    """
    # =================================================================
    # UPGRADE 3: Initialize Thought Log
    # =================================================================
    thought_log = []
    thought_log.append("🧠 Agent initializing analysis pipeline...")
    
    # Initialize data router
    router = get_data_router()
    thought_log.append(f"📡 Data router initialized")
    
    # Apply symbol/time_range if provided (only works in historical mode)
    if symbol:
        try:
            router.set_symbol(symbol)
            thought_log.append(f"🎯 Symbol set to {symbol}")
        except ValueError as e:
            log_safety.safe_log(f"⚠️ Symbol override ignored: {e}", level="WARNING")
    
    if time_range:
        try:
            router.set_time_range(time_range)
            thought_log.append(f"📅 Time range set to {time_range}")
        except ValueError as e:
            log_safety.safe_log(f"⚠️ Time range override ignored: {e}", level="WARNING")
    
    # Get routing configuration
    routing_config = router.get_routing_config()
    data_mode = routing_config["data_mode"]
    is_open = routing_config["is_open"]
    thought_log.append(f"📊 Market Status: {'OPEN' if is_open else 'CLOSED'} | Mode: {data_mode}")
    
    # Get data from appropriate source
    market_data = router.get_market_data()
    portfolio_data = router.get_portfolio_data()
    sector_heatmap = router.get_sector_heatmap()
    candidates = router.get_candidates()
    thought_log.append(f"📦 Data loaded from {routing_config['data_source']}")
    
    # Extract data components
    candles = market_data.get("candles", [])
    headlines = market_data.get("headlines", [])
    portfolio = portfolio_data.get("portfolio", {})
    positions = portfolio_data.get("positions", [])
    thought_log.append(f"📈 Processing {len(candles)} candles, {len(positions)} positions")
    
    # Handle scenario overrides (for testing)
    scenario = get_scenario(scenario_id) if scenario_id else {}
    overrides = scenario.get("override_inputs", {})
    
    if overrides:
        if "positions" in overrides:
            positions = overrides["positions"]
        if "candidates" in overrides:
            candidates = overrides["candidates"]
    
    # =================================================================
    # UPGRADE 2: Apply Crash Simulation Override
    # =================================================================
    if crash_override:
        thought_log.append("🚨 CRASH SIMULATION ACTIVE — Volatility override engaged")
        if "force_volatility_state" in crash_override:
            overrides["volatility_state"] = crash_override["force_volatility_state"]
        if "force_news_score" in crash_override:
            overrides["news_score"] = crash_override["force_news_score"]
        if "force_sector_confidence" in crash_override:
            overrides["sector_confidence"] = crash_override["force_sector_confidence"]
    
    # Compute signals from data
    thought_log.append("📊 Analyzing volatility regime...")
    if candles:
        atr_res = volatility_metrics.compute_atr(candles)
        baseline_atr = 2.5
        if atr_res.get("atr"):
            vol_res = volatility_metrics.classify_volatility_state(atr_res["atr"], baseline_atr)
            vol_state = vol_res.get("volatility_state", "STABLE")
        else:
            vol_state = "STABLE"
    else:
        vol_state = "STABLE"
    
    thought_log.append(f"📉 Volatility state: {vol_state}")
    
    thought_log.append("📰 Processing news sentiment...")
    if headlines:
        news_res = news_scorer.score_tech_news(headlines)
        news_score_val = news_res.get("news_score", 50)
    else:
        news_score_val = 50  # Neutral when no headlines
    
    thought_log.append(f"📰 News score: {news_score_val}/100")
    
    thought_log.append("🎯 Computing sector confidence...")
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score_val)
    confidence_val = conf_res.get("sector_confidence", 50)
    thought_log.append(f"🎯 Sector confidence: {confidence_val}/100")
    
    # Apply scenario overrides to signals
    if "volatility_state" in overrides:
        vol_state = overrides["volatility_state"]
        thought_log.append(f"⚡ Volatility OVERRIDE: {vol_state}")
    if "news_score" in overrides:
        news_score_val = overrides["news_score"]
        thought_log.append(f"⚡ News score OVERRIDE: {news_score_val}")
    if "sector_confidence" in overrides:
        confidence_val = overrides["sector_confidence"]
    
    # Build market context for decision engine
    market_context = {
        "candles": candles,
        "news": headlines
    }
    
    if "volatility_state" in overrides:
        market_context["override_volatility"] = overrides["volatility_state"]
    if "news_score" in overrides:
        market_context["override_news_score"] = overrides["news_score"]
    if "sector_confidence" in overrides:
        market_context["override_confidence"] = overrides["sector_confidence"]
    
    # Build execution context
    execution_context = {
        "system_mode": "PAPER (Advisory)" if is_open else "VALIDATION (Historical)",
        "market_status": routing_config["market_status"],
        "data_feed_mode": data_mode,
        "data_capability": routing_config["data_source"]
    }
    
    # Run decision engine
    thought_log.append("🧠 Running decision engine...")
    decision_report = decision_engine.run_decision_engine(
        portfolio_state=portfolio,
        positions=positions,
        sector_heatmap=sector_heatmap,
        candidates=candidates,
        market_context=market_context,
        execution_context=execution_context,
        thought_log=thought_log  # UPGRADE 3: Pass thought_log
    )
    
    # Extract components
    posture = decision_report.get("market_posture", {})
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    concentration_risk = decision_report.get("concentration_risk", {})
    
    thought_log.append(f"📋 Market posture determined: {posture.get('market_posture', 'N/A')}")
    thought_log.append(f"⚠️ Risk level: {posture.get('risk_level', 'N/A')}")
    thought_log.append(f"✅ Allowed decisions: {len(safe_decisions)}")
    if blocked_decisions:
        thought_log.append(f"🛡️ Blocked by safety: {len(blocked_decisions)} actions")
    
    # Calculate average vitals
    pos_scores = [d["score"] for d in safe_decisions if d["type"] == "POSITION"]
    avg_vitals = int(sum(pos_scores) / len(pos_scores)) if pos_scores else 0
    
    # Generate execution plan
    if safe_decisions:
        simulated_decision_input = {"decision": posture.get("market_posture", "NEUTRAL")}
        plan_output = execution_planner.generate_execution_plan(simulated_decision_input, positions)
    else:
        plan_output = {"proposed_actions": []}
    
    # Generate summary
    summary_context = {
        "primary_intent": posture.get("market_posture", "NEUTRAL"),
        "proposed_actions": plan_output.get("proposed_actions", []),
        "blocked_actions": blocked_decisions,
        "mode": posture.get("risk_level", "MEDIUM")
    }
    summary = execution_summary.generate_execution_summary(summary_context)
    
    # Build analysis result
    thought_log.append("📝 Generating final analysis report...")
    analysis_result = {
        # Phase 2 Signals
        "signals": {
            "volatility_state": vol_state,
            "volatility_explanation": f"Computed from {len(candles)} candles",
            "news_score": news_score_val,
            "news_explanation": f"Processed {len(headlines)} headlines" if headlines else "No headlines (neutral)",
            "sector_confidence": confidence_val,
            "confidence_explanation": "Combined signals"
        },
        # Phase 3 Decisions
        "market_posture": posture,
        "decisions": safe_decisions,
        "blocked_by_safety": blocked_decisions,
        "concentration_risk": concentration_risk,
        # Phase 4 Planning
        "execution_plan": plan_output.get("proposed_actions", []),
        "execution_summary": summary,
        # Input Statistics
        "input_stats": {
            "positions": len(positions),
            "candles": len(candles),
            "headlines": len(headlines)
        },
        "scenario_meta": scenario,
        # Portfolio Health
        "portfolio": {
            "position_count": len(positions),
            "avg_vitals": avg_vitals,
            "capital_lockin": "DETECTED" if decision_report.get("reallocation_trigger") else "NONE",
            "concentration_risk": "HIGH" if concentration_risk.get("is_concentrated") else "LOW"
        }
    }
    
    # Build full response
    return {
        # Market Status & Routing
        "market_status": {
            "label": routing_config["market_status"],
            "is_open": is_open,
            "timestamp": datetime.now().isoformat()
        },
        "data_mode": data_mode,
        "data_source": routing_config["data_source"],
        "portfolio_source": data_mode,
        "symbols_used": [routing_config["selected_symbol"]],
        
        # Routing Configuration (for frontend controls)
        "routing_config": {
            "selected_symbol": routing_config["selected_symbol"],
            "selected_time_range": routing_config.get("selected_time_range"),
            "available_symbols": routing_config.get("available_symbols", []),
            "available_time_ranges": routing_config.get("available_time_ranges", {}),
            "controls_enabled": routing_config.get("controls_enabled", {})
        },
        
        # Data Metadata
        "data_metadata": market_data.get("metadata"),
        
        # Status Message for UI
        "status_message": routing_config.get("status_message", ""),
        
        # UPGRADE 3: Thought Log
        "thought_log": thought_log,
        
        # Analysis Results
        "analysis": analysis_result
    }


def print_run_configuration(routing_config: Dict[str, Any]):
    """Print clear, honest capability disclosure at startup."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "MARKET-AWARE RUN CONFIGURATION".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Market Status     : {routing_config['market_status']:<35}║")
    print(f"║  Data Mode         : {routing_config['data_mode']:<35}║")
    print(f"║  Data Source       : {routing_config['data_source']:<35}║")
    print(f"║  Selected Symbol   : {routing_config['selected_symbol']:<35}║")
    
    if routing_config.get('selected_time_range'):
        print(f"║  Time Range        : {routing_config['selected_time_range']:<35}║")
    
    print(f"║  Execution         : {'DISABLED (Advisory Only)':<35}║")
    print("╚" + "═" * 58 + "╝")
    
    if not routing_config['is_open']:
        print(f"\n📊 HISTORICAL VALIDATION MODE")
        print("   Market is closed. System is operating on Alpaca historical")
        print("   market data to validate decision logic over extended periods.")
    else:
        print(f"\n🔴 LIVE MODE")
        print("   Market is open. Using live data from Alpaca + Polygon.")
    print()


if __name__ == "__main__":
    # Self-test
    print("Testing Market-Aware Runner...")
    
    result = run_market_aware_analysis()
    
    print(f"\nResult Summary:")
    print(f"  Market Status: {result['market_status']['label']}")
    print(f"  Data Mode: {result['data_mode']}")
    print(f"  Data Source: {result['data_source']}")
    print(f"  Symbol: {result['symbols_used']}")
    print(f"  Decisions: {len(result['analysis']['decisions'])}")
    print(f"  Market Posture: {result['analysis']['market_posture'].get('market_posture', 'N/A')}")
