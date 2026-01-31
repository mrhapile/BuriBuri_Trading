"""
full_system_demo.py

End-to-End Demonstration of the Portfolio Intelligence System.
Validates the complete pipeline: Signals -> Decisions -> Safety -> Planning.

No real funds. No live APIs. Pure logic validation.
"""

import json
import volatility_metrics
import news_scorer
import sector_confidence
import decision_engine
import execution_planner
import risk_guardrails
import execution_summary

# =============================================================================
# MOCK DATA GENERATORS
# =============================================================================

def get_mock_portfolio_context():
    """Returns a mock portfolio state."""
    return {
        "total_capital": 1_000_000.0,
        "cash": 45_000.0,  # Low cash -> Should trigger specific constraints
        "risk_tolerance": "moderate"
    }

def get_mock_positions():
    """Returns a list of mock positions with mixed health states."""
    return [
        # 1. Healthy Tech Leader (Keep)
        {
            "symbol": "NVDA", 
            "sector": "TECH",
            "entry_price": 400.0, 
            "current_price": 500.0, 
            "atr": 10.0, 
            "days_held": 15, 
            "capital_allocated": 300_000.0 # 30% Allocation
        },
        # 2. Stagnant Utility (Candidate for Exit)
        {
            "symbol": "SLOW_UTIL", 
            "sector": "UTILITIES", 
            "entry_price": 50.0, 
            "current_price": 50.5, 
            "atr": 0.5, 
            "days_held": 45, # > 20 days -> Stagnant
            "capital_allocated": 150_000.0
        },
        # 3. Risky Tech Speculation (Candidate for Risk Trim)
        {
            "symbol": "SPEC_TECH", 
            "sector": "TECH", 
            "entry_price": 100.0, 
            "current_price": 95.0, 
            "atr": 5.0, 
            "days_held": 5, 
            "capital_allocated": 250_000.0 # Creates Concentration Issue (Total Tech > 55%)
        }
    ]

def get_mock_candidates():
    """Returns potential new trades."""
    return [
        {
            "symbol": "NEW_BIO", 
            "sector": "BIOTECH", 
            "projected_efficiency": 85.0 # Attractive
        },
        {
            "symbol": "MORE_TECH", 
            "sector": "TECH", 
            "projected_efficiency": 95.0 # Very attractive, but Tech is full
        }
    ]

def get_mock_market_data():
    """Returns mock candles and news headlines."""
    # 1. Candles (Simulate Stabilizing Volatility)
    candles = [
        {"timestamp": f"2026-01-31T10:{i:02d}:00Z", "high": 100+i, "low": 98+i, "close": 99+i}
        for i in range(20)
    ]
    
    # 2. Headlines (Mixed/Positive)
    headlines = [
        "Tech sector shows resilience despite rate hike fears",
        "AI demand continues to outpace supply in hardware markets",
        "Utility sector stagnates as bond yields rise"
    ]
    
    return candles, headlines

# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_full_system_demo():
    print("================================================================")
    print("PORTFOLIO INTELLIGENCE SYSTEM - END-TO-END DEMO")
    print("================================================================")
    
    # ---------------------------------------------------------
    # 1. PHASE 2 - SIGNAL GENERATION
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("=== PHASE 2: SIGNAL GENERATION ===")
    print("="*50)
    
    candles, headlines = get_mock_market_data()
    
    # A. Volatility
    atr_res = volatility_metrics.compute_atr(candles)
    # Assume baseline was 2.5, current mock is ~2.0
    vol_res = volatility_metrics.classify_volatility_state(current_atr=2.0, baseline_atr=2.5)
    vol_state = vol_res["volatility_state"]
    print(f"[Signal] Volatility State: {vol_state} (ATR: {atr_res.get('atr', 'N/A')})")
    
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
    print("\n" + "="*50)
    print("=== PHASE 3: DECISION MAKING ===")
    print("="*50)
    
    portfolio = get_mock_portfolio_context()
    positions = get_mock_positions()
    heatmap = {"TECH": 80, "BIOTECH": 70, "UTILITIES": 30}
    candidates = get_mock_candidates()
    
    # Run the Engine
    decision_report = decision_engine.run_decision_engine(
        portfolio_state=portfolio,
        positions=positions,
        sector_heatmap=heatmap,
        candidates=candidates,
        market_context=market_context
    )
    
    posture = decision_report["market_posture"]
    print(f"[Strategy] Market Posture: {posture['market_posture']} (Risk: {posture['risk_level']})")
    print(f"[Strategy] Posture Reason: {posture['reasons'][0]}")
    
    print("\n[Strategy] Initial Decisions (Before Safety):")
    decisions = decision_report.get("decisions", []) # Using raw decisions if blocked split handled elsewhere, 
                                                     # typically decision_engine splits them, let's look at raw output structure
    
    # Note: decision_engine returns safe/blocked lists split. 
    # But for demo flow clarity, we assume we might want to see what was proposed.
    # The current decision_engine returns "decisions" (=safe) and "blocked_by_safety". 
    
    safe_decisions = decision_report.get("decisions", [])
    blocked_decisions = decision_report.get("blocked_by_safety", [])
    
    all_decisions = safe_decisions + blocked_decisions
    
    if not all_decisions:
        print("  - No actions proposed.")
    else:
        for d in all_decisions:
            print(f"  > {d['type']:<10} | {d['target']:<10} -> {d['action']}")
            print(f"    Reason: {d['reason']}")

    # ---------------------------------------------------------
    # 3. PHASE 4 - SAFETY & EXECUTION PLANNING
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("=== PHASE 4: SAFETY & EXECUTION PLANNING ===")
    print("="*50)

    # Note: decision_engine calls safety internally now (as per recent update).
    # But for explicit demonstration, we can simulate the planning step on safe decisions.
    
    if safe_decisions:
        # Note: execution_planner normally takes (input_decision, positions). 
        # But our demo has 'decisions' list from phase 3.
        # However, the prompt asked to use execution_planner.generate_execution_plan(safe_decisions, portfolio).
        # WAIT: execution_planner.py code shows: def generate_execution_plan(decision_output: dict, positions: list[dict]) -> dict:
        # decision_output expects {"decision": "MODE"}
        # This mismatch suggests execution_planner might need a different input or I simulate the input it expects.
        
        # Let's map our Phase 3 'posture' to what execution_planner expects
        simulated_decision_input = {"decision": posture["market_posture"]}
        
        # And pass positions (which we have)
        plan_output = execution_planner.generate_execution_plan(simulated_decision_input, positions)
        
        print("\n[Plan] Execution Plan (Sequential):")
        for step in plan_output.get("proposed_actions", []):
            print(f"  - {step['symbol']}: {step['action']}")
            print(f"    Reason: {step['reason']}")
    
    print("\n[Safety] Blocked Actions Report:")
    if not blocked_decisions:
        print("  - No actions were blocked by safety guards.")
    else:
        for b in blocked_decisions:
            print(f"  X BLOCKED: {b['target']} ({b['action']})")
            print(f"    Guard: {b.get('blocking_guard', 'Unknown')}")
            print(f"    Reason: {b.get('reason_blocked', 'Safety violation')}")

    # Final Summary
    print("\n" + "-"*60)
    print("FINAL EXECUTION SUMMARY")
    print("-" * 60)
    # Prepare context for summary
    summary_context = {
        "primary_intent": posture["market_posture"],
        "proposed_actions": plan_output.get("proposed_actions", []) if safe_decisions else [],
        "blocked_actions": blocked_decisions,
        "mode": posture["risk_level"]
    }
    
    summary = execution_summary.generate_execution_summary(summary_context)
    
    # Nicely formatted print
    print(f"Decision:         {summary['decision']}")
    print(f"Actions Proposed: {summary['actions_proposed']}")
    print(f"Actions Blocked:  {summary['actions_blocked']}")
    print(f"Final Mode:       {summary['final_mode']}")
    print("================================================================")

if __name__ == "__main__":
    run_full_system_demo()
