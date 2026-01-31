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

# =============================================================================
# DATA SOURCE CONFIGURATION
# =============================================================================

# DEMO MODE: Use pre-built demo profiles for showcasing (takes priority)
# Set to True for hackathon demos / judge presentations
DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() == "true"
DEMO_PROFILE = os.environ.get("DEMO_PROFILE", "OVERCONCENTRATED_TECH")

# ALPACA MODE: Use real paper trading data (when DEMO_MODE is False)
USE_ALPACA = os.environ.get("USE_ALPACA", "false").lower() == "true"

# =============================================================================
# INITIALIZE DATA SOURCE
# =============================================================================

_adapter = None
_demo_data = None

if DEMO_MODE:
    # DEMO MODE: Load pre-built portfolio profiles
    print("=" * 60)
    print("🎯 [DEMO MODE ENABLED]")
    from demo.demo_profiles import (
        load_demo_profile, 
        get_demo_candidates, 
        get_demo_heatmap,
        get_profile_description,
        get_available_profiles
    )
    
    try:
        _portfolio, _positions = load_demo_profile(DEMO_PROFILE)
        _demo_data = {
            "portfolio": _portfolio,
            "positions": _positions,
            "candidates": get_demo_candidates(DEMO_PROFILE),
            "heatmap": get_demo_heatmap(DEMO_PROFILE)
        }
        print(f"   Profile: {DEMO_PROFILE}")
        print(f"   Description: {get_profile_description(DEMO_PROFILE)}")
        print(f"   Available Profiles: {', '.join(get_available_profiles())}")
    except ValueError as e:
        print(f"   ❌ Error: {e}")
        print(f"   Falling back to mock mode...")
        DEMO_MODE = False
    print("=" * 60)

if not DEMO_MODE:
    if USE_ALPACA:
        print("[Config] Data Source: ALPACA (Paper Trading)")
        from broker.alpaca_adapter import AlpacaAdapter
        _adapter = AlpacaAdapter()
    else:
        print("[Config] Data Source: MOCK (Development)")
        from broker.mock_adapter import MockAdapter
        _adapter = MockAdapter()


# =============================================================================
# DATA ACCESS LAYER
# =============================================================================

def get_portfolio_context():
    """Returns portfolio state from configured data source."""
    if DEMO_MODE and _demo_data:
        return _demo_data["portfolio"]
    return _adapter.get_portfolio()


def get_positions():
    """Returns positions from configured data source."""
    if DEMO_MODE and _demo_data:
        return _demo_data["positions"]
    return _adapter.get_positions()


def get_candidates():
    """Returns trade candidates."""
    if DEMO_MODE and _demo_data:
        return _demo_data["candidates"]
    
    candidates = _adapter.get_candidates()
    if not candidates:
        return [
            {"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 85.0},
            {"symbol": "MORE_TECH", "sector": "TECH", "projected_efficiency": 95.0}
        ]
    return candidates


def get_sector_heatmap():
    """Returns sector heat scores."""
    if DEMO_MODE and _demo_data:
        return _demo_data["heatmap"]
    return _adapter.get_sector_heatmap()


def get_market_data():
    """Returns candles and news headlines."""
    if DEMO_MODE:
        # Generate realistic mock candles for demo
        candles = [
            {"timestamp": f"2026-01-31T10:{i:02d}:00Z", "high": 100+i, "low": 98+i, "close": 99+i}
            for i in range(20)
        ]
        headlines = [
            "Tech sector shows resilience despite rate hike fears",
            "AI demand continues to outpace supply in hardware markets",
            "Market volatility expected to stabilize next quarter"
        ]
        return candles, headlines
    
    # Get candles from adapter
    candles = _adapter.get_recent_candles("SPY", 20)
    
    if not candles:
        candles = [
            {"timestamp": f"2026-01-31T10:{i:02d}:00Z", "high": 100+i, "low": 98+i, "close": 99+i}
            for i in range(20)
        ]
    
    headlines = _adapter.get_headlines()
    if not headlines:
        headlines = [
            "Tech sector shows resilience despite rate hike fears",
            "AI demand continues to outpace supply in hardware markets",
            "Utility sector stagnates as bond yields rise"
        ]
    
    return candles, headlines


# =============================================================================
# API-COMPATIBLE OUTPUT FUNCTION (NO PRINTING)
# =============================================================================

def run_demo_scenario():
    """
    Returns full system output as JSON-safe dict.
    NO printing. NO side effects.
    
    This is the function called by the Flask API.
    """
    # Mock Data (Same as demo)
    portfolio = {
        "total_capital": 1_000_000.0,
        "cash": 150_000.0,
        "risk_tolerance": "moderate"
    }
    
    positions = [
        {
            "symbol": "NVDA", 
            "sector": "TECH",
            "entry_price": 400.0, 
            "current_price": 480.0, 
            "atr": 12.0, 
            "days_held": 12, 
            "capital_allocated": 300_000.0
        },
        {
            "symbol": "SLOW_UTIL", 
            "sector": "UTILITIES", 
            "entry_price": 50.0, 
            "current_price": 51.0, 
            "atr": 1.0, 
            "days_held": 42, 
            "capital_allocated": 200_000.0
        },
        {
            "symbol": "SPEC_TECH", 
            "sector": "TECH", 
            "entry_price": 120.0, 
            "current_price": 95.0, 
            "atr": 5.0, 
            "days_held": 8, 
            "capital_allocated": 180_000.0
        }
    ]
    
    sector_heatmap = {
        "TECH": 80,
        "UTILITIES": 40,
        "BIOTECH": 70
    }
    
    candidates = [
        {"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 72.0},
        {"symbol": "MORE_TECH", "sector": "TECH", "projected_efficiency": 68.0}
    ]
    
    # Compute Phase 2 Signals
    candles = [
        {"timestamp": f"2026-01-31T10:{i:02d}:00Z", "high": 100+i, "low": 98+i, "close": 99+i}
        for i in range(20)
    ]
    headlines = [
        "Tech sector sees steady demand growth",
        "AI stocks remain resilient despite volatility",
        "Investors cautious ahead of inflation data"
    ]
    
    atr_res = volatility_metrics.compute_atr(candles)
    vol_res = volatility_metrics.classify_volatility_state(current_atr=2.0, baseline_atr=2.5)
    vol_state = vol_res["volatility_state"]
    
    news_res = news_scorer.score_tech_news(headlines)
    news_score_val = news_res["news_score"]
    
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score_val)
    confidence_val = conf_res["sector_confidence"]
    
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
        market_context=market_context
    )
    
    # Extract components
    posture = decision_report.get("market_posture", {})
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    concentration_risk = decision_report.get("concentration_risk", {})
    
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
    
    # Return JSON-safe structure for UI
    return {
        # Phase 2 Signals
        "phase2": {
            "volatility_state": vol_state,
            "volatility_explanation": "Volatility contracting, risk subsiding",
            "news_score": news_score_val,
            "news_explanation": f"Processed {news_res['headline_count']} headlines",
            "sector_confidence": confidence_val,
            "confidence_explanation": "Combined signals indicate moderate confidence"
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
        }
    }


# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_full_system_demo():
    print("\n" + "=" * 70)
    print("🧠 PORTFOLIO INTELLIGENCE SYSTEM - END-TO-END DEMO")
    print("=" * 70)
    
    if DEMO_MODE:
        print(f"📊 Running with: {DEMO_PROFILE} profile")
    
    # ---------------------------------------------------------
    # 1. PHASE 2 - SIGNAL GENERATION
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
    print(f"[Signal] Volatility State: {vol_state} (ATR: {current_atr:.2f})")
    
    # B. News
    news_res = news_scorer.score_tech_news(headlines)
    news_score = news_res["news_score"]
    print(f"[Signal] News Sentiment:   {news_score}/100 ({news_res['headline_count']} headlines)")
    
    # C. Sector Confidence
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_score)
    confidence = conf_res["sector_confidence"]
    print(f"[Signal] Sector Confidence: {confidence}/100")
    
    market_context = {
        "candles": candles,
        "news": headlines
    }

    # ---------------------------------------------------------
    # 2. PHASE 3 - DECISION MAKING
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
        market_context=market_context
    )
    
    posture = decision_report["market_posture"]
    print(f"\n🎮 [Strategy]")
    print(f"   Market Posture: {posture['market_posture']} (Risk: {posture['risk_level']})")
    for reason in posture.get('reasons', []):
        print(f"   → {reason}")

    # ---------------------------------------------------------
    # 3. DECISIONS & EXPLANATIONS
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("=== PHASE 3: DECISIONS WITH EXPLANATIONS ===")
    print("=" * 60)
    
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    
    if safe_decisions:
        print("\n✅ [Approved Actions]")
        for d in safe_decisions:
            action_color = "🟢" if d['action'] in ["MAINTAIN", "HOLD", "ALLOCATE"] else "🟡"
            if d['action'] in ["REDUCE", "TRIM_RISK", "FREE_CAPITAL"]:
                action_color = "🔴"
            
            print(f"\n   {action_color} {d['type']:<10} | {d['target']:<8} → {d['action']}")
            print(f"      Score: {d.get('score', 'N/A')}")
            
            # Show explanations
            reasons = d.get('reasons', [d.get('reason', 'No explanation')])
            if isinstance(reasons, list):
                for i, r in enumerate(reasons[:3], 1):
                    print(f"      {i}. {r}")
            else:
                print(f"      → {reasons}")

    # ---------------------------------------------------------
    # 4. SAFETY & GUARDRAILS
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
            reasons = b.get('reasons', [])
            if reasons:
                print(f"      Would-be reasons:")
                for i, r in enumerate(reasons[:2], 1):
                    print(f"        {i}. {r}")

    # ---------------------------------------------------------
    # 5. EXECUTION PLANNING
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
        plan_output = {"proposed_actions": []}
        print("\n   No actions to plan.")

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 EXECUTIVE SUMMARY")
    print("=" * 70)
    
    summary_context = {
        "primary_intent": posture["market_posture"],
        "proposed_actions": plan_output.get("proposed_actions", []),
        "blocked_actions": blocked_decisions,
        "mode": posture["risk_level"]
    }
    
    summary = execution_summary.generate_execution_summary(summary_context)
    
    print(f"""
   Decision:          {summary['decision']}
   Risk Level:        {summary['final_mode']}
   Actions Approved:  {summary['actions_proposed']}
   Actions Blocked:   {summary['actions_blocked']}
    """)
    
    # Concentration warning
    conc_risk = decision_report.get("concentration_risk", {})
    if conc_risk.get("is_concentrated"):
        print(f"   ⚠️  CONCENTRATION ALERT: {conc_risk['dominant_sector']} @ {conc_risk['exposure']:.0%}")
    
    print("=" * 70)
    
    if DEMO_MODE:
        print(f"\n💡 Try other profiles: DEMO_PROFILE=BALANCED_TECH or DEMO_PROFILE=LOSING_PORTFOLIO")


if __name__ == "__main__":
    run_full_system_demo()
