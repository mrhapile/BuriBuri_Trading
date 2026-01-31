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
from typing import Dict, Any, Optional
from datetime import datetime

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
from backend.scenarios import get_scenario


def run_market_aware_analysis(
    scenario_id: Optional[str] = None,
    symbol: Optional[str] = None,
    time_range: Optional[str] = None
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
    
    Returns:
        Complete analysis result with:
        - market_status
        - data_mode
        - data_source
        - routing_config
        - analysis
    """
    # Initialize data router
    router = get_data_router()
    
    # Apply symbol/time_range if provided (only works in historical mode)
    if symbol:
        try:
            router.set_symbol(symbol)
        except ValueError as e:
            print(f"⚠️ Symbol override ignored: {e}")
    
    if time_range:
        try:
            router.set_time_range(time_range)
        except ValueError as e:
            print(f"⚠️ Time range override ignored: {e}")
    
    # Get routing configuration
    routing_config = router.get_routing_config()
    data_mode = routing_config["data_mode"]
    is_open = routing_config["is_open"]
    
    # Get data from appropriate source
    market_data = router.get_market_data()
    portfolio_data = router.get_portfolio_data()
    sector_heatmap = router.get_sector_heatmap()
    candidates = router.get_candidates()
    
    # Extract data components
    candles = market_data.get("candles", [])
    headlines = market_data.get("headlines", [])
    portfolio = portfolio_data.get("portfolio", {})
    positions = portfolio_data.get("positions", [])
    
    # Handle scenario overrides (for testing)
    scenario = get_scenario(scenario_id) if scenario_id else {}
    overrides = scenario.get("override_inputs", {})
    
    if overrides:
        if "positions" in overrides:
            positions = overrides["positions"]
        if "candidates" in overrides:
            candidates = overrides["candidates"]
    
    # Compute signals from data
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
    
    if headlines:
        news_res = news_scorer.score_tech_news(headlines)
        news_score_val = news_res.get("news_score", 50)
    else:
        news_score_val = 50  # Neutral when no headlines
    
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score_val)
    confidence_val = conf_res.get("sector_confidence", 50)
    
    # Apply scenario overrides to signals
    if "volatility_state" in overrides:
        vol_state = overrides["volatility_state"]
    if "news_score" in overrides:
        news_score_val = overrides["news_score"]
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
    decision_report = decision_engine.run_decision_engine(
        portfolio_state=portfolio,
        positions=positions,
        sector_heatmap=sector_heatmap,
        candidates=candidates,
        market_context=market_context,
        execution_context=execution_context
    )
    
    # Extract components
    posture = decision_report.get("market_posture", {})
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    concentration_risk = decision_report.get("concentration_risk", {})
    
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
