import vitals_monitor
import capital_lock_in
import opportunity_scanner
import concentration_guard

def run_decision_engine(portfolio_state: dict, positions: list, sector_heatmap: dict, candidates: list) -> dict:
    """
    Orchestrates portfolio decisions by combining:
    1. Vitals Monitor (Position Efficiency)
    2. Capital Lock-in Detector (Portfolio Efficiency)
    3. Opportunity Scanner (Relative Value)
    4. Concentration Guard (Risk Control)

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
    opportunity_report = opportunity_scanner.scan_for_opportunities(
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
            "score": vitals
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
            "score": eff_score
        })

    # ---------------------------------------------------------
    # 6. Final Report
    # ---------------------------------------------------------
    summary_parts = [lock_in_report["summary"]]
    if conc_warning["is_concentrated"]:
        summary_parts.append(f"ALERT: {conc_warning['dominant_sector']} sector over-concentrated at {conc_warning['exposure']:.0%}.")
    elif conc_warning["severity"] == "APPROACHING":
        summary_parts.append(f"WARNING: {conc_warning['dominant_sector']} sector approaching limit ({conc_warning['exposure']:.0%}).")
        
    if better_opp_exists:
        summary_parts.append(f"Opportunity: {opportunity_report['summary']}")

    final_summary = " ".join(summary_parts)

    return {
        "portfolio_summary": final_summary,
        "pressure_score": lock_in_report["pressure_score"],
        "reallocation_trigger": reallocation_pressure,
        "concentration_risk": conc_warning,
        "opportunity_scan": opportunity_report,
        "decisions": decisions
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
    
    print(f"Summary: {report_t1['portfolio_summary']}")
    print(f"Pressure Score: {report_t1['pressure_score']}")
    conc = report_t1["concentration_risk"]
    print(f"Concentration: {conc['severity']} (Dom: {conc['dominant_sector']} @ {conc['exposure']:.0%})")
    
    print("-" * 75)
    print(f"{'TARGET':<12} | {'TYPE':<10} | {'ACTION':<18} | {'REASON'}")
    print("-" * 75)
    for d in report_t1["decisions"]:
        print(f"{d['target']:<12} | {d['type']:<10} | {d['action']:<18} | {d['reason']}")

if __name__ == "__main__":
    run_demo()
