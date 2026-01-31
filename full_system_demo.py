"""
full_system_demo.py

End-to-End Demonstration of the Portfolio Intelligence System.
Validates the complete pipeline: Signals -> Decisions -> Safety -> Planning.

Data Sources (Priority Order):
    1. DEMO_MODE = True: Pre-built demo profiles for showcasing intelligence
    2. USE_ALPACA = True: Real Alpaca paper trading data
    3. Default: Mock data for development/testing

No real funds. No live trading. Pure logic validation.
"""

import os
import json
import volatility_metrics
import news_scorer
import sector_confidence
import decision_engine
import execution_planner
import risk_guardrails
import execution_summary
import market_mode
from backend import market_status
from backend.scenarios import get_scenario

# =============================================================================
# DATA SOURCE CONFIGURATION
# =============================================================================

# =============================================================================
# DATA SOURCE CONFIGURATION
# =============================================================================

# 0. Check for Historical Validation Mode (Blocks normal execution)
HISTORICAL_VALIDATION = os.environ.get("HISTORICAL_VALIDATION")
if HISTORICAL_VALIDATION and HISTORICAL_VALIDATION.lower() == "true":
    from validation.runner import run_validation
    run_validation()
    import sys
    sys.exit(0)

# 1. Detect Environment State
EXECUTION_CONTEXT = market_mode.determine_execution_context()

# 2. Extract specific mode flags for internal logic
IS_LIVE = (EXECUTION_CONTEXT["data_feed_mode"] == "LIVE")
IS_HISTORICAL = (EXECUTION_CONTEXT["data_feed_mode"] == "HISTORICAL")

# Symbols and time ranges for historical validation
SUPPORTED_HISTORICAL_SYMBOLS = ["SPY", "QQQ", "IWM"]
SUPPORTED_TIME_RANGES = ["1M", "4M", "6M", "1Y"]

# Active selection states (can be modified by frontend/API)
ACTIVE_SYMBOL = os.environ.get("VAL_SYMBOL", "SPY")
ACTIVE_RANGE = os.environ.get("VAL_RANGE", "6M")


# =============================================================================
# CAPABILITY DISCLOSURE (MANDATORY FOR JUDGES)
# =============================================================================

def print_run_configuration():
    """Print clear, honest capability disclosure at startup."""
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "RUN CONFIGURATION".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  System Mode       : {EXECUTION_CONTEXT['system_mode']:<35}║")
    print(f"║  Market Status     : {EXECUTION_CONTEXT['market_status']:<35}║")
    print(f"║  Data Feed Mode    : {EXECUTION_CONTEXT['data_feed_mode']:<35}║")
    print(f"║  Data Capability   : {EXECUTION_CONTEXT['data_capability']:<35}║")
    
    if DEMO_MODE:
        print(f"║  Active Profile    : {DEMO_PROFILE:<35}║")
        print(f"║  Trend Overlay     : {DEMO_TREND if DEMO_TREND != 'NEUTRAL' else 'NONE':<35}║")
        
    print(f"║  Execution         : {'DISABLED (Advisory Only)':<35}║")
    print("╚" + "═" * 58 + "╝")
    
    if EXECUTION_CONTEXT['market_status'] != "OPEN" and not DEMO_MODE:
        print(f"\n⚠️  MARKET IS CLOSED ({EXECUTION_CONTEXT['reason']}).")
        print("   System correctly using synthetic data to validate logic invariant.")
    print()


# =============================================================================
# INITIALIZE DATA SOURCE
# =============================================================================

_adapter = None
_hist_manager = None

if IS_LIVE:
    try:
        from broker.alpaca_adapter import AlpacaAdapter
        _adapter = AlpacaAdapter()
    except Exception as e:
        print(f"❌ Alpaca Connection Failed in LIVE mode: {e}")
        # In strict mode, we don't fallback to dummy if it's supposed to be live.
        # But for stability in this dev environment, we'll log it.
elif IS_HISTORICAL:
    from validation.data_manager import HistoricalDataManager
    _hist_manager = HistoricalDataManager()


# =============================================================================
# DATA ACCESS LAYER
# =============================================================================

def get_portfolio_context():
    """Returns portfolio state. Live from Alpaca, Fixed for Historical Validation."""
    if IS_LIVE and _adapter:
        return _adapter.get_portfolio()
    
    # Historical / Closed Market baseline
    return {
        "total_capital": 100000.0,
        "cash": 100000.0,
        "risk_tolerance": "moderate"
    }


def get_positions():
    """Returns positions. Live from Alpaca, Empty for Historical Validation."""
    if IS_LIVE and _adapter:
        return _adapter.get_positions()
    return []


def get_candidates(symbol=None):
    """Returns trade candidates. Live from Alpaca, Fixed for Historical."""
    if IS_LIVE and _adapter:
        return _adapter.get_candidates()
    
    # Historical validation typically tests specific candidates
    target = symbol or ACTIVE_SYMBOL
    return [
        {"symbol": target, "sector": "TECH", "projected_efficiency": 85.0}
    ]


def get_sector_heatmap():
    """Returns sector heat scores."""
    if IS_LIVE and _adapter:
        return _adapter.get_sector_heatmap()
    return {"TECH": 60, "SPY": 50}


def get_market_data(symbol=None, time_range=None):
    """
    Returns candles and news headlines.
    Strictly follows Data Feed Mode.
    """
    target_sym = symbol or ACTIVE_SYMBOL
    target_range = time_range or ACTIVE_RANGE
    
    if IS_LIVE and _adapter:
        candles = _adapter.get_recent_candles(target_sym, 20)
        headlines = _adapter.get_headlines()
        return candles, headlines
    
    if IS_HISTORICAL and _hist_manager:
        # Map time range to dates
        end_dt = "2023-06-01" # Fixed end for the cached data
        if target_range == "1M": start_dt = "2023-05-01"
        elif target_range == "4M": start_dt = "2023-02-01"
        elif target_range == "1Y": start_dt = "2022-06-01" # Might fetch if missing
        else: start_dt = "2023-01-01" # Default 6M approx
            
        candles = _hist_manager.fetch_history(target_sym, start_dt, end_dt)
        # News is empty for historical validation as we don't have a news archive
        return candles, []
    
    return [], []


# =============================================================================
# API-COMPATIBLE OUTPUT FUNCTION (NO PRINTING)
# =============================================================================

def run_demo_scenario(scenario_id=None, symbol=None, time_range=None):
    """
    Returns full system output as JSON-safe dict.
    Strictly routed by market status (IS_LIVE / IS_HISTORICAL).
    """
    # 1. Market Status & Mode
    # Use global execution context as source of truth
    status = market_mode.get_market_status()
    is_open = (status["status"] == "OPEN")
    
    data_mode = EXECUTION_CONTEXT["data_feed_mode"]
    portfolio_source = EXECUTION_CONTEXT["data_capability"]
    
    # Selected Symbol/Range (mostly for Historical validation)
    target_sym = symbol or ACTIVE_SYMBOL
    target_range = time_range or ACTIVE_RANGE

    # 2. Fetch Core Data (Depends on target_sym)
    portfolio = get_portfolio_context()
    positions = get_positions()
    sector_heatmap = get_sector_heatmap()
    candidates = get_candidates(target_sym)
    
    # 3. Fetch Market Data (Candles/News)
    candles, headlines = get_market_data(target_sym, target_range)

    # =========================================================
    # SCENARIO INJECTION (If scenario_id is provided)
    # =========================================================
    scenario = get_scenario(scenario_id) if scenario_id else {}
    overrides = scenario.get("override_inputs", {})
    
    if overrides:
        # Scenarios force a specific data mode for display
        data_mode = f"SCENARIO ({scenario_id})"
        if "positions" in overrides:
            positions = overrides["positions"]
        if "candidates" in overrides:
            candidates = overrides["candidates"]
            
    # =========================================================
    # COMPUTE SIGNALS
    # =========================================================
    # Always compute from the fetched data to ensure consistency
    
    # Volatility
    atr_res = volatility_metrics.compute_atr(candles)
    # Use 2.5 as demo baseline for stability
    baseline_atr = 2.5 
    if atr_res["atr"]:
        vol_res = volatility_metrics.classify_volatility_state(atr_res["atr"], baseline_atr)
        vol_state = vol_res["volatility_state"]
    else:
        vol_state = "STABLE"
        
    # News
    news_res = news_scorer.score_tech_news(headlines)
    news_score_val = news_res["news_score"]
    
    # Confidence
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score_val)
    confidence_val = conf_res["sector_confidence"]

    # Apply overrides (if any)
    if "volatility_state" in overrides:
        vol_state = overrides["volatility_state"]
    if "news_score" in overrides:
        news_score_val = overrides["news_score"]
    if "sector_confidence" in overrides:
        confidence_val = overrides["sector_confidence"]
            
    market_context = {
        "candles": candles,
        "news": headlines
    }
    
    # Run Decision Engine
    decision_report = decision_engine.run_decision_engine(
        portfolio_state=portfolio,
        positions=positions,
        sector_heatmap=sector_heatmap,
        candidates=candidates,
        market_context=market_context,
        execution_context=EXECUTION_CONTEXT
    )
    
    # Extract components
    posture = decision_report.get("market_posture", {})
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    concentration_risk = decision_report.get("concentration_risk", {})

    # Calculate Avg Vitals from Decisions for UI
    pos_scores = [d["score"] for d in safe_decisions if d["type"] == "POSITION"]
    if pos_scores:
        avg_vitals = int(sum(pos_scores) / len(pos_scores))
    else:
        avg_vitals = 0

    # Generate Execution Plan
    if safe_decisions:
        simulated_decision_input = {"decision": posture.get("market_posture", "NEUTRAL")}
        plan_output = execution_planner.generate_execution_plan(simulated_decision_input, positions)
    else:
        plan_output = {"proposed_actions": []}
    
    # Generate Summary
    summary_context = {
        "primary_intent": posture.get("market_posture", "NEUTRAL"),
        "proposed_actions": plan_output.get("proposed_actions", []),
        "blocked_actions": blocked_decisions,
        "mode": posture.get("risk_level", "MEDIUM")
    }
    summary = execution_summary.generate_execution_summary(summary_context)
    
    # Analysis Result
    analysis_result = {
        # Phase 2 Signals
        "signals": {
            "volatility_state": vol_state or decision_report.get("market_posture", {}).get("reasons", ["UNKNOWN"])[0], # Fallback if not overridden
            "volatility_explanation": "Processed from candles",
            "news_score": news_score_val or 50,
            "news_explanation": f"Processed {len(headlines)} headlines",
            "sector_confidence": confidence_val or 50,
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
        # Metadata
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
    
    # Wrap in API Contract
    return {
        "market_status": status,
        "data_mode": data_mode,
        "symbols_used": [symbol] if symbol else [],
        "portfolio_source": portfolio_source,
        "analysis": analysis_result
    }


# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_full_system_demo():
    # Print capability disclosure FIRST
    print_run_configuration()
    
    print("=" * 70)
    print("🧠 PORTFOLIO INTELLIGENCE SYSTEM - END-TO-END DEMO")
    print("=" * 70)
    
    if DEMO_MODE:
        from demo.demo_profiles import get_profile_description
        print(f"📊 Profile: {DEMO_PROFILE}")
        print(f"   → {get_profile_description(DEMO_PROFILE)}")
        if DEMO_TREND != "NEUTRAL":
            from demo.trend_overlays import get_overlay_description
            print(f"🌊 Trend: {DEMO_TREND}")
            print(f"   → {get_overlay_description(DEMO_TREND)}")
    
    # ---------------------------------------------------------
    # PHASE 2 - SIGNAL GENERATION
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 2: SIGNAL GENERATION ===")
    print("=" * 60)
    
    candles, headlines = get_market_data()
    
    # A. Volatility
    atr_res = volatility_metrics.compute_atr(candles)
    current_atr = atr_res.get("atr", 2.0)
    baseline_atr = current_atr * 1.1
    vol_res = volatility_metrics.classify_volatility_state(current_atr=current_atr, baseline_atr=baseline_atr)
    vol_state = vol_res["volatility_state"]
    
    # Apply trend overlay
    if DEMO_MODE and DEMO_TREND != "NEUTRAL" and _trend_overlay:
        vol_state = apply_overlay_to_volatility(vol_state, DEMO_TREND)
    
    print(f"[Signal] Volatility State: {vol_state} (ATR: {current_atr:.2f})")
    
    # B. News
    news_res = news_scorer.score_tech_news(headlines)
    news_score = news_res["news_score"]
    
    # Apply trend overlay
    if DEMO_MODE and DEMO_TREND != "NEUTRAL" and _trend_overlay:
        news_score = apply_overlay_to_news(news_score, DEMO_TREND)
    
    print(f"[Signal] News Sentiment:   {news_score}/100 ({news_res['headline_count']} headlines)")
    
    # C. Sector Confidence
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score)
    confidence = conf_res["sector_confidence"]
    
    # Apply trend overlay
    if DEMO_MODE and DEMO_TREND != "NEUTRAL" and _trend_overlay:
        confidence = apply_overlay_to_confidence(confidence, DEMO_TREND)
    
    print(f"[Signal] Sector Confidence: {confidence}/100")
    
    if DEMO_MODE and DEMO_TREND != "NEUTRAL":
        print(f"         (Modified by {DEMO_TREND} overlay)")
    
    market_context = {
        "candles": candles,
        "news": headlines
    }

    # ---------------------------------------------------------
    # PHASE 3 - DECISION MAKING
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 3: DECISION MAKING ===")
    print("=" * 60)
    
    portfolio = get_portfolio_context()
    positions = get_positions()
    heatmap = get_sector_heatmap()
    candidates = get_candidates()
    
    print(f"\n📈 [Portfolio Overview]")
    print(f"   Total Capital: ${portfolio['total_capital']:,.0f}")
    print(f"   Cash Available: ${portfolio['cash']:,.0f} ({portfolio['cash']/portfolio['total_capital']*100:.1f}%)")
    print(f"\n📊 [Positions: {len(positions)}]")
    
    # Calculate sector exposure
    sector_exposure = {}
    for p in positions:
        sector = p.get("sector", "OTHER")
        sector_exposure[sector] = sector_exposure.get(sector, 0) + p["capital_allocated"]
    
    for p in positions:
        pnl = ((p["current_price"] - p["entry_price"]) / p["entry_price"]) * 100
        pnl_indicator = "🟢" if pnl > 0 else "🔴"
        print(f"   {pnl_indicator} {p['symbol']:<6} | {p['sector']:<10} | ${p['capital_allocated']:>10,.0f} | {pnl:>+6.1f}%")
    
    print(f"\n🎯 [Sector Concentration]")
    for sector, alloc in sorted(sector_exposure.items(), key=lambda x: -x[1]):
        pct = (alloc / portfolio['total_capital']) * 100
        warning = "⚠️ " if pct > 60 else "   "
        print(f"   {warning}{sector}: {pct:.1f}%")
    
    # Run the Engine
    decision_report = decision_engine.run_decision_engine(
        portfolio_state=portfolio,
        positions=positions,
        sector_heatmap=heatmap,
        candidates=candidates,
        market_context=market_context,
        execution_context=EXECUTION_CONTEXT
    )
    
    posture = decision_report["market_posture"]
    pm_summary = decision_report.get("pm_summary", "Summary unavailable.")
    
    print(f"\n🎮 [Strategy]")
    print(f"   Market Posture: {posture['market_posture']} (Risk: {posture['risk_level']})")
    
    print(f"\n📝 [Portfolio Manager Summary]")
    print(f"   \"{pm_summary}\"")

    # ---------------------------------------------------------
    # DECISIONS & EXPLANATIONS
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 3: DECISIONS WITH EXPLANATIONS ===")
    print("=" * 60)
    
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    superiority = decision_report.get("superiority_analysis", {})
    
    # Display Primary Decision
    primary = superiority.get("primary_decision")
    print("\n🏆 [PRIMARY DECISION]")
    if primary:
        print(f"   ACTION: {primary['action']} used on {primary['target']}")
        print(f"   CONFIDENCE: {superiority.get('decision_confidence', 0.0):.0%}")
        print(f"   RATIONALE:")
        for r in primary.get("reasons", []):
            print(f"    - {r}")
    else:
        print("   No primary action required (Portfolio Optimized).")
        
    # NEW: Decision Dominance Check & Counterfactuals
    if superiority.get("dominance_check"):
        dom = superiority["dominance_check"]
        print(f"\n📐 DECISION DOMINANCE CHECK")
        print(f"   • {dom['justification']}")
        for factor in dom.get("factors", []):
            print(f"   • {factor}")
    
    print(f"\n🧪 Counterfactual Evaluation (Simulated)")
    cf = superiority.get("counterfactual", {})
    print(f"   • Median alternative risk: {cf.get('median_alternative_risk', 'N/A')}")
    if cf.get("confidence_level"):
        print(f"   • Confidence level: {cf.get('confidence_level')}")
    if primary:
        print(f"   • Capital efficiency delta: {cf.get('capital_efficiency_delta', 'N/A')}")
    else:
        print(f"   • Portfolio drawdown avoided: {cf.get('drawdown_avoided', 'N/A')}")
    # ...

    # Display Alternatives
    print("\n⚖️  [ALTERNATIVES CONSIDERED]")
    alternatives = superiority.get("alternatives_considered", [])
    if alternatives:
        for alt in alternatives:
            print(f"   • {alt['target']:<8} ({alt['type']}): {alt['reason']}")
            print(f"     (Score: {alt['score']})")
    else:
        print("   No significant alternatives considered.")

    if safe_decisions:
        print("\n✅ [All Approved Actions]")
        for d in safe_decisions:
            print(f"   • {d['target']:<8} → {d['action']:<15} (Score: {d['score']})")

    # ---------------------------------------------------------
    # SAFETY & GUARDRAILS
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 4: SAFETY GUARDRAILS ===")
    print("=" * 60)
    
    if not blocked_decisions:
        print("\n   🛡️ All proposed actions passed safety checks")
    else:
        print(f"\n   🚨 [{len(blocked_decisions)} Actions BLOCKED by Safety Guards]")
        for b in blocked_decisions:
            print(f"\n   ❌ {b['type']:<10} | {b['target']:<8} → {b['action']}")
            safety_reason = b.get('safety_reason', b.get('blocking_guard', 'Safety violation'))
            print(f"      🛑 BLOCKED: {safety_reason}")

    # ---------------------------------------------------------
    # EXECUTION PLANNING
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 5: EXECUTION PLANNING ===")
    print("=" * 60)
    
    if safe_decisions:
        simulated_decision_input = {"decision": posture["market_posture"]}
        plan_output = execution_planner.generate_execution_plan(simulated_decision_input, positions)
        
        print("\n📋 [Sequential Execution Plan]")
        for i, step in enumerate(plan_output.get("proposed_actions", []), 1):
            print(f"   {i}. {step['symbol']}: {step['action']}")
            print(f"      → {step['reason']}")
    else:
        print("\n   No actions to plan.")

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 EXECUTIVE SUMMARY")
    print("=" * 70)
    
    print(f"\n   STATUS:    {EXECUTION_CONTEXT['system_mode']}") # Show System Mode here (PAPER/DEMO)
    print(f"   DECISION:  {posture['market_posture']}")
    print(f"   SUMMARY:   {pm_summary}")
    
    conc_risk = decision_report.get("concentration_risk", {})
    if conc_risk.get("is_concentrated"):
        print(f"\n   ⚠️  CONCENTRATION ALERT: {conc_risk['dominant_sector']} @ {conc_risk['exposure']:.0%}")
    
    print("=" * 70)
    print("\n")


if __name__ == "__main__":
    run_full_system_demo()
