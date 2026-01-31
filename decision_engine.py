import position_vitals as vitals_monitor
import capital_lock_in
import opportunity_scanner
import opportunity_logic
import concentration_guard
import decision_explainer
import risk_guardrails

def run_decision_engine(portfolio_state: dict, positions: list, sector_heatmap: dict, candidates: list) -> dict:
    """
    Orchestrates portfolio decisions by combining:
    1. Vitals Monitor (Position Efficiency)
    2. Capital Lock-in Detector (Portfolio Efficiency)
    3. Opportunity Scanner (Relative Value)
    4. Concentration Guard (Risk Control)
    5. Decision Explainability (Human-Readable Reasons)
    6. Risk Guardrails (Final Safety Gate)

    Args:
        portfolio_state (dict): {total_capital, cash, ...}
        positions (dict): List of raw position dictionaries
        sector_heatmap (dict): {sector_name: heat_score}
        candidates (list): List of potential new trades {symbol, sector, projected_efficiency}

    Returns:
        dict: Final decision report containing summary, alerts, and detailed decision list.
    """
    
    # ---------------------------------------------------------
    # 1. POSITIONS ANALYSIS (The Vitals Monitor)
    # ---------------------------------------------------------
    analyzed_positions = []
    for pos in positions:
        # Compute Vitals
        vitals_result = vitals_monitor.compute_vitals(pos)
        
        # Merge results without mutating original
        enriched_pos = pos.copy()
        enriched_pos.update(vitals_result) 
        analyzed_positions.append(enriched_pos)

    # ---------------------------------------------------------
    # 2. PORTFOLIO ANALYSIS (Capital Lock-in)
    # ---------------------------------------------------------
    lock_in_report = capital_lock_in.detect_capital_lock_in(
        portfolio_state, 
        analyzed_positions, 
        sector_heatmap
    )
    reallocation_pressure = lock_in_report["reallocation_alert"]
    hot_sectors = lock_in_report["hot_sectors"]
    dead_capital_symbols = [d["symbol"] for d in lock_in_report["dead_positions"]]

    # ---------------------------------------------------------
    # 3. RISK GUARDS (Concentration)
    # ---------------------------------------------------------
    total_capital = float(portfolio_state.get("total_capital", 1.0))
    concentration_report = concentration_guard.analyze_portfolio_concentration(
        analyzed_positions, 
        total_capital
    )
    conc_warning = concentration_report["warning"]
    
    # ---------------------------------------------------------
    # 4. OPPORTUNITY SCANNER (Relative Efficiency)
    # ---------------------------------------------------------
    opportunity_report = opportunity_logic.scan_for_opportunities(
        analyzed_positions, 
        candidates
    )
    better_opp_exists = opportunity_report["better_opportunity_exists"]
    opp_confidence = opportunity_report.get("confidence", "N/A")

    # ---------------------------------------------------------
    # 5. DECISION SYNTHESIS
    # ---------------------------------------------------------
    decisions = []
    
    # A. Process Existing Positions
    for pos in analyzed_positions:
        symbol = pos["symbol"]
        vitals = pos["vitals_score"]
        sector = pos.get("sector", "UNKNOWN")
        flags = pos.get("flags", [])
        
        # Fallback stagnation check
        if "flags" not in pos and not flags:
            pnl_pct_approx = ((pos.get("current_price", 0) - pos.get("entry_price", 1)) / pos.get("entry_price", 1)) * 100
            if pos.get("days_held", 0) > 20 and pnl_pct_approx < 2.0:
                flags = ["STAGNANT"]

        action = "MAINTAIN"
        reason = f"Strong vitals ({vitals}). Efficient."

        # Risk-Based overrides
        is_concentrated_sector = conc_warning["is_concentrated"] and sector == conc_warning["dominant_sector"]

        # 1. Dead Capital (Highest Priority for Exit)
        if symbol in dead_capital_symbols and reallocation_pressure:
            if better_opp_exists and opp_confidence == "HIGH":
                action = "FREE_CAPITAL"
                reason = f"Dead capital ({vitals}) in cold sector. High-confidence upgrade available."
            else:
                action = "REDUCE_AGGRESSIVE"
                reason = f"Dead capital ({vitals}) in cold sector dragging portfolio."
        
        # 2. Risk Reduction (Concentration)
        elif is_concentrated_sector:
            if vitals < 60:
                action = "TRIM_RISK"
                reason = f"Sector {sector} over-concentrated ({conc_warning['exposure']:.0%}). Trimming weak position."
            else:
                action = "HOLD_CAPPED"
                reason = f"Sector {sector} over-concentrated. No further allocation allowed."

        # 3. Standard Performance Logic
        elif vitals < 40:
            action = "REDUCE"
            reason = f"Vitals critically low ({vitals}). Reduce exposure."
        elif "STAGNANT" in flags:
            action = "REVIEW"
            reason = "Position is profitable but stagnant (>20 days, <2% return)."
        elif vitals < 60:
            action = "HOLD"
            reason = f"Weak vitals ({vitals}). Monitoring."
            
        decisions.append({
            "target": symbol,
            "type": "POSITION",
            "action": action,
            "reason": reason,
            "score": vitals,
            "sector": sector
        })

    # B. Process Candidates
    for cand in candidates:
        symbol = cand["symbol"]
        sector = cand["sector"]
        eff_score = cand.get("projected_efficiency", 0)
        
        action = "IGNORE"
        reason = f"Sector {sector} not attractive."
        
        # Guards
        is_sector_approaching = conc_warning["severity"] == "APPROACHING" and sector == conc_warning["dominant_sector"]
        is_sector_breached = conc_warning["is_concentrated"] and sector == conc_warning["dominant_sector"]
        
        if is_sector_breached:
            action = "BLOCK_RISK"
            reason = f"Cannot allocate. Sector {sector} already over-concentrated ({conc_warning['exposure']:.0%})."
        
        elif sector in hot_sectors:
            if reallocation_pressure:
                # Differentiate based on concentration nearness
                if is_sector_approaching:
                    action = "ALLOCATE_CAPPED"
                    reason = f"Hot sector ({sector}), but nearing concentration limit."
                else:
                    action = "ALLOCATE_HIGH"
                    reason = f"Hot sector ({sector}). Deploying freed capital."
            
            elif portfolio_state["cash"] > 100000:
                if is_sector_approaching:
                    action = "ALLOCATE_CAUTIOUS"
                    reason = f"Hot sector, but nearing concentration limit."
                else:
                    action = "ALLOCATE"
                    reason = f"Hot sector. Sufficient liquidity."
            else:
                action = "WATCHLIST"
                reason = "Hot sector, but limited capital."
            
        decisions.append({
            "target": symbol,
            "type": "CANDIDATE",
            "action": action,
            "reason": reason,
            "score": eff_score,
            "sector": sector
        })

    # ---------------------------------------------------------
    # 6. EXPLANATION LAYER (Phase 2 → Human-Readable)
    # ---------------------------------------------------------
    # Collect signals for explainer (NO recomputation)
    portfolio_signals = {
        "dead_capital_symbols": dead_capital_symbols,
        "hot_sectors": hot_sectors,
        "reallocation_pressure": reallocation_pressure,
        "pressure_score": lock_in_report["pressure_score"]
    }
    
    risk_signals = {
        "concentration_warning": conc_warning,
        "better_opp_exists": better_opp_exists,
        "opp_confidence": opp_confidence
    }
    
    # Enrich decisions with structured explanations
    # Note: sector already added in step 5, but ensure flags are present
    for decision in decisions:
        if decision["type"] == "POSITION":
            matching_pos = next((p for p in analyzed_positions if p["symbol"] == decision["target"]), None)
            if matching_pos:
                decision["flags"] = matching_pos.get("flags", [])
    
    enriched_decisions = decision_explainer.enrich_decisions_with_explanations(
        decisions,
        portfolio_signals,
        risk_signals
    )

    # ---------------------------------------------------------
    # 7. RISK GUARDRAILS (Final Safety Gate)
    # ---------------------------------------------------------
    # Build risk context from already-computed signals
    risk_context = {
        "concentration": conc_warning,
        "cash_available": float(portfolio_state.get("cash", 0.0)),
        "minimum_reserve": 50000.0,  # Configurable threshold
        "volatility_state": portfolio_state.get("volatility_state", "STABLE")  # Optional signal
    }
    
    # Apply safety filters to enriched decisions
    guardrail_results = risk_guardrails.apply_risk_guardrails(
        enriched_decisions,
        risk_context
    )
    
    # Extract filtered decisions
    safe_decisions = guardrail_results["allowed_actions"]
    blocked_decisions = guardrail_results["blocked_actions"]
    
    # Update summary if actions were blocked
    guardrail_summary = risk_guardrails.summarize_guardrail_results(guardrail_results)

    # ---------------------------------------------------------
    # 8. Final Report
    # ---------------------------------------------------------
    summary_parts = [lock_in_report["summary"]]
    if conc_warning["is_concentrated"]:
        summary_parts.append(f"ALERT: {conc_warning['dominant_sector']} sector over-concentrated at {conc_warning['exposure']:.0%}.")
    elif conc_warning["severity"] == "APPROACHING":
        summary_parts.append(f"WARNING: {conc_warning['dominant_sector']} sector approaching limit ({conc_warning['exposure']:.0%}).")
        
    if better_opp_exists:
        summary_parts.append(f"Opportunity: {opportunity_report['summary']}")
    
    # Add guardrail summary if actions were blocked
    if blocked_decisions:
        summary_parts.append(f"SAFETY: {guardrail_summary}")

    final_summary = " ".join(summary_parts)

    return {
        "portfolio_summary": final_summary,
        "pressure_score": lock_in_report["pressure_score"],
        "reallocation_trigger": reallocation_pressure,
        "concentration_risk": conc_warning,
        "opportunity_scan": opportunity_report,
        "decisions": safe_decisions,
        "blocked_by_safety": blocked_decisions
    }

# ---------------------------------------------------------
# Usage Example (Demo)
# ---------------------------------------------------------
def run_demo():
    print("\n" + "="*80)
    print("PORTFOLIO INTELLIGENCE SYSTEM - END-TO-END DEMO")
    print("="*80)

    # -------------------------------------------------------------------------
    # SCENARIO T0: Initial State - Balanced
    # -------------------------------------------------------------------------
    print("\n--- T0: Initial Balanced State ---")
    portfolio_t0 = {"total_capital": 1000000.0, "cash": 150000.0}
    positions_t0 = [
        {"symbol": "SAFE_TECH", "sector": "TECH", "entry_price": 100, "current_price": 110, "atr": 2.5, "days_held": 10, "capital_allocated": 300000}, # Healthy
        {"symbol": "SLOW_UTIL", "sector": "UTILITIES", "entry_price": 50, "current_price": 51, "atr": 1.0, "days_held": 40, "capital_allocated": 200000}  # Stagnant
    ]
    heatmap_t0 = {"TECH": 80, "UTILITIES": 50, "BIOTECH": 60}
    candidates_t0 = [{"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 75.0}]

    report_t0 = run_decision_engine(portfolio_t0, positions_t0, heatmap_t0, candidates_t0)
    print(f"Summary: {report_t0['portfolio_summary']}")
    
    # -------------------------------------------------------------------------
    # SCENARIO T1: Capital Lock-in + Concentration Risk Emerging
    # -------------------------------------------------------------------------
    print("\n--- T1: Stress Scenario (Lock-in + Concentration Risk) ---")
    portfolio_t1 = {"total_capital": 1000000.0, "cash": 40000.0} # Low cash
    positions_t1 = [
        # Dead Capital Candidate
        {
            "symbol": "OLD_STEEL", "sector": "MATERIALS",
            "entry_price": 100, "current_price": 95, "atr": 2.0, 
            "days_held": 45, "capital_allocated": 300000 
        },
        # Concentration Cluster (Tech)
        {
            "symbol": "BIG_TECH_A", "sector": "TECH",
            "entry_price": 150, "current_price": 180, "atr": 3.0, 
            "days_held": 10, "capital_allocated": 400000 
        },
        {
            "symbol": "BIG_TECH_B", "sector": "TECH",
            "entry_price": 200, "current_price": 210, "atr": 4.0, 
            "days_held": 20, "capital_allocated": 260000 
        }
        # Total Tech = 66% (Approaching 70% Limit)
    ]
    
    heatmap_t1 = {"TECH": 90, "MATERIALS": 20, "BIOTECH": 80}
    
    candidates_t1 = [
        {"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 85.0},
        {"symbol": "MORE_TECH", "sector": "TECH", "projected_efficiency": 95.0} # Should be CAPPED
    ]

    report_t1 = run_decision_engine(portfolio_t1, positions_t1, heatmap_t1, candidates_t1)
    
    print(f"\nSummary: {report_t1['portfolio_summary']}")
    print(f"Pressure Score: {report_t1['pressure_score']}")
    conc = report_t1["concentration_risk"]
    print(f"Concentration: {conc['severity']} (Dom: {conc['dominant_sector']} @ {conc['exposure']:.0%})")
    
    # Display approved decisions with explanations
    print("\n" + "=" * 80)
    print("✅ APPROVED ACTIONS (WITH EXPLANATIONS)")
    print("=" * 80)
    for d in report_t1["decisions"]:
        print(f"\n[{d['type']}] {d['target']} → {d['action']}")
        print(f"  Structured Reasons:")
        reasons = d.get('reasons', [d.get('reason', 'No explanation')])
        for i, reason in enumerate(reasons, 1):
            print(f"    {i}. {reason}")
    
    # Display blocked actions with explanations
    if report_t1.get("blocked_by_safety"):
        print("\n" + "=" * 80)
        print("🛡️  BLOCKED BY SAFETY GUARDRAILS")
        print("=" * 80)
        for b in report_t1["blocked_by_safety"]:
            print(f"\n[{b['type']}] {b['target']} → {b['action']} ❌")
            print(f"  🚫 Safety Block: {b['reason']}")
            if b.get('reasons'):
                print(f"  Would-be Explanations:")
                for i, reason in enumerate(b['reasons'], 1):
                    print(f"    {i}. {reason}")

if __name__ == "__main__":
    run_demo()
