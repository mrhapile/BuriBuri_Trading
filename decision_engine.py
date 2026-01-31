import position_vitals as vitals_monitor
import capital_lock_in
import opportunity_logic
import concentration_guard
import decision_explainer
import volatility_metrics
import news_scorer
import sector_confidence

def determine_market_posture(
    volatility_state: str,
    confidence_score: int,
    news_score: float,
    vitals_summary: dict
) -> dict:
    """
    Determines the high-level market posture and risk level based on aggregated Phase 2 signals.
    
    Rules:
    1. RISK_OFF: If Portfolio is unhealthy (Unhealthy > Healthy positions).
    2. DEFENSIVE: EXPANDING volatility + Low Confidence (< 50).
    3. AGGRESSIVE: CONTRACTING volatility + High Confidence (> 70).
    4. OPPORTUNITY: STABLE volatility + Good Confidence (> 65).
    5. NEUTRAL: Default state.
    
    Args:
        volatility_state (str): EXPANDING | STABLE | CONTRACTING
        confidence_score (int): 0-100
        news_score (float): 0-100
        vitals_summary (dict): { "healthy": int, "weak": int, "unhealthy": int }
        
    Returns:
        dict: {
            "market_posture": str,
            "risk_level": "LOW | MEDIUM | HIGH",
            "confidence": int,
            "reasons": list[str]
        }
    """
    reasons = []
    posture = "NEUTRAL"
    risk_level = "MEDIUM"
    
    # 1. Check Internal Health (Portfolio Vitals) - HIGHEST PRIORITY
    healthy_count = vitals_summary.get("healthy", 0)
    unhealthy_count = vitals_summary.get("unhealthy", 0)
    
    if unhealthy_count > healthy_count:
        posture = "RISK_OFF"
        risk_level = "HIGH"
        reasons.append(f"Portfolio unhealthy ({unhealthy_count} > {healthy_count}). Protecting capital.")
        return {
            "market_posture": posture,
            "risk_level": risk_level,
            "confidence": confidence_score,
            "reasons": reasons
        }

    # 2. Check External Market Conditions
    reasons.append(f"Volatility is {volatility_state} (Conf: {confidence_score})")
    
    if volatility_state == "EXPANDING":
        risk_level = "HIGH"
        if confidence_score < 50:
            posture = "DEFENSIVE"
            reasons.append("High uncertainty with weak sector confidence.")
        else:
            posture = "NEUTRAL"
            reasons.append("High volatility but sector confidence holds.")
            
    elif volatility_state == "CONTRACTING":
        risk_level = "LOW"
        if confidence_score > 70:
            posture = "AGGRESSIVE"
            reasons.append("Volatility cooling + High confidence -> Trend following.")
        else:
            posture = "NEUTRAL"
            reasons.append("Volatility cooling but confidence insufficient for aggression.")
            
    elif volatility_state == "STABLE":
        risk_level = "MEDIUM"
        if confidence_score > 65:
            posture = "OPPORTUNITY"
            reasons.append("Stable market with strong signals.")
        else:
            posture = "NEUTRAL"
            reasons.append("Stable market, waiting for stronger signals.")
            
    else:
        # Unknown state
        posture = "NEUTRAL"
        reasons.append("Market state unknown.")

    return {
        "market_posture": posture,
        "risk_level": risk_level,
        "confidence": confidence_score,
        "reasons": reasons
    }

def run_decision_engine(portfolio_state: dict, positions: list, sector_heatmap: dict, candidates: list, market_context: dict = None) -> dict:
    """
    Orchestrates portfolio decisions by combining:
    1. Vitals Monitor (Position Efficiency)
    2. Capital Lock-in Detector (Portfolio Efficiency)
    3. Opportunity Scanner (Relative Value)
    4. Concentration Guard (Risk Control)
    5. Market Posture (Phase 2 Core Logic)

    Args:
        portfolio_state (dict): {total_capital, cash, ...}
        positions (dict): List of raw position dictionaries
        sector_heatmap (dict): {sector_name: heat_score}
        candidates (list): List of potential new trades {symbol, sector, projected_efficiency}
        market_context (dict, optional): { "candles": [...], "news": [...] } for Phase 2 signals.

    Returns:
        dict: Final decision report containing summary, alerts, detailed decision list, and market posture.
    """
    
    # ---------------------------------------------------------
    # 1. PREPARE MARKET SIGNALS (Phase 2)
    # ---------------------------------------------------------
    # Default values
    vol_state = "STABLE"
    news_res = {"news_score": 50}
    
    if market_context:
        # A. Volatility
        candles = market_context.get("candles", [])
        if candles:
            # Assume baseline is hardcoded or provided. For now, we compute current ATR.
            # Real implementation would track baseline. We'll use a dummy baseline for demo logic.
            atr_res = volatility_metrics.compute_atr(candles)
            if atr_res["atr"]:
                # Mock baseline: slightly lower than current to simulate slight expansion, or use avg
                # For deterministic logical testing, let's assume baseline is close to current
                baseline = atr_res["atr"] # No change
                vol_res = volatility_metrics.classify_volatility_state(atr_res["atr"], baseline)
                vol_state = vol_res["volatility_state"]
        
        # B. News
        headlines = market_context.get("news", [])
        if headlines:
            # Extract strings if dicts provided
            headline_strs = [h["title"] if isinstance(h, dict) else h for h in headlines]
            news_res = news_scorer.score_tech_news(headline_strs)

    # C. Confidence
    conf_res = sector_confidence.compute_sector_confidence(vol_state, news_res["news_score"])
    confidence_score = conf_res["sector_confidence"]

    # ---------------------------------------------------------
    # 2. POSITIONS ANALYSIS (The Vitals Monitor)
    # ---------------------------------------------------------
    analyzed_positions = []
    vitals_counts = {"healthy": 0, "weak": 0, "unhealthy": 0}
    
    for pos in positions:
        # Compute Vitals
        vitals_result = vitals_monitor.compute_vitals(pos)
        
        # Count health states for Market Posture
        h_status = vitals_result.get("health", "").lower()
        if h_status in vitals_counts:
            vitals_counts[h_status] += 1
            
        # Merge results 
        enriched_pos = pos.copy()
        enriched_pos.update(vitals_result) 
        analyzed_positions.append(enriched_pos)

    # ---------------------------------------------------------
    # 3. DETERMINE MARKET POSTURE
    # ---------------------------------------------------------
    posture_report = determine_market_posture(
        volatility_state=vol_state,
        confidence_score=confidence_score,
        news_score=news_res["news_score"],
        vitals_summary=vitals_counts
    )

    # ---------------------------------------------------------
    # 4. PORTFOLIO ANALYSIS (Capital Lock-in)
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
    # 5. RISK GUARDS (Concentration)
    # ---------------------------------------------------------
    total_capital = float(portfolio_state.get("total_capital", 1.0))
    concentration_report = concentration_guard.analyze_portfolio_concentration(
        analyzed_positions, 
        total_capital
    )
    conc_warning = concentration_report["warning"]
    
    # ---------------------------------------------------------
    # 6. OPPORTUNITY SCANNER (Relative Efficiency)
    # ---------------------------------------------------------
    
    # --- PHASE 2 ADJUSTMENT: Filter Candidates by Posture ---
    # If DEFENSIVE or RISK_OFF, ignore candidates
    active_candidates = candidates
    if posture_report["market_posture"] in ["DEFENSIVE", "RISK_OFF"]:
        active_candidates = [] # Cut off inflows
        
    opportunity_report = opportunity_logic.scan_for_opportunities(
        analyzed_positions, 
        active_candidates
    )
    better_opp_exists = opportunity_report["better_opportunity_exists"]
    opp_confidence = opportunity_report.get("confidence", "N/A")

    # ---------------------------------------------------------
    # 7. DECISION SYNTHESIS
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
            
        # --- PHASE 2 ADJUSTMENT: Posture Override ---
        # If RISK_OFF, accelerate exits
        if posture_report["market_posture"] == "RISK_OFF":
            if action in ["HOLD", "REVIEW", "MAINTAIN"]:
                action = "REDUCE_RISK"
                reason = "RISK_OFF posture triggered. Reducing exposure."

        decisions.append({
            "target": symbol,
            "type": "POSITION",
            "action": action,
            "reason": reason,
            "score": vitals
        })

    # B. Process Candidates
    for cand in candidates: # iterates original candidates to show why they were accepted/rejected
        symbol = cand["symbol"]
        sector = cand["sector"]
        eff_score = cand.get("projected_efficiency", 0)
        
        action = "IGNORE"
        reason = f"Sector {sector} not attractive."
        
        is_ignored_due_to_posture = cand not in active_candidates
        
        if is_ignored_due_to_posture:
            action = "BLOCK_POSTURE"
            reason = f"Market Posture is {posture_report['market_posture']}. inflows blocked."
        else:
            # Normal Logic
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
    # 8. EXPLANATION LAYER
    # ---------------------------------------------------------
    portfolio_signals = {
        "dead_capital_symbols": dead_capital_symbols,
        "hot_sectors": hot_sectors,
        "reallocation_pressure": reallocation_pressure,
        "pressure_score": lock_in_report["pressure_score"]
    }
    
    risk_signals = {
        "concentration_warning": conc_warning,
        "better_opp_exists": better_opp_exists,
        "opp_confidence": opp_confidence,
        "market_posture": posture_report # Add posture to explanation context
    }
    
    # Enrich decisions with structured explanations
    for i, decision in enumerate(decisions):
        if decision["type"] == "POSITION":
            matching_pos = next((p for p in analyzed_positions if p["symbol"] == decision["target"]), None)
            if matching_pos:
                decision["sector"] = matching_pos.get("sector", "UNKNOWN")
                decision["flags"] = matching_pos.get("flags", [])
        elif decision["type"] == "CANDIDATE":
            matching_cand = next((c for c in candidates if c["symbol"] == decision["target"]), None)
            if matching_cand:
                decision["sector"] = matching_cand.get("sector", "UNKNOWN")
    
    enriched_decisions = decision_explainer.enrich_decisions_with_explanations(
        decisions,
        portfolio_signals,
        risk_signals
    )

    # ---------------------------------------------------------
    # 9. Final Report
    # ---------------------------------------------------------
    summary_parts = [lock_in_report["summary"]]
    summary_parts.append(f"POSTURE: {posture_report['market_posture']} (Conf: {posture_report['confidence']}).")
    
    if conc_warning["is_concentrated"]:
        summary_parts.append(f"ALERT: {conc_warning['dominant_sector']} sector over-concentrated.")
    
    final_summary = " ".join(summary_parts)

    return {
        "portfolio_summary": final_summary,
        "pressure_score": lock_in_report["pressure_score"],
        "reallocation_trigger": reallocation_pressure,
        "concentration_risk": conc_warning,
        "opportunity_scan": opportunity_report,
        "decisions": enriched_decisions,
        "market_posture": posture_report
    }

# ---------------------------------------------------------
# Usage Example (Demo)
# ---------------------------------------------------------
def run_demo():
    print("\n" + "="*80)
    print("PORTFOLIO INTELLIGENCE SYSTEM - END-TO-END DEMO")
    print("="*80)

    # -------------------------------------------------------------------------
    # SCENARIO T0: Initial Balanced State
    # -------------------------------------------------------------------------
    print("\n--- T0: Initial Balanced State ---")
    portfolio_t0 = {"total_capital": 1000000.0, "cash": 150000.0}
    positions_t0 = [
        {"symbol": "SAFE_TECH", "sector": "TECH", "entry_price": 100, "current_price": 110, "atr": 2.5, "days_held": 10, "capital_allocated": 300000}, 
        {"symbol": "SLOW_UTIL", "sector": "UTILITIES", "entry_price": 50, "current_price": 51, "atr": 1.0, "days_held": 40, "capital_allocated": 200000}
    ]
    heatmap_t0 = {"TECH": 80, "UTILITIES": 50}
    candidates_t0 = [{"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 75.0}]

    report_t0 = run_decision_engine(portfolio_t0, positions_t0, heatmap_t0, candidates_t0)
    print(f"Summary: {report_t0['portfolio_summary']}")
    
    # -------------------------------------------------------------------------
    # SCENARIO T2: RISK_OFF (Unhealthy Portfolio)
    # -------------------------------------------------------------------------
    print("\n--- T2: Risk Off Scenario (Unhealthy Portfolio) ---")
    positions_t2 = [
        {"symbol": "BAD_STOCK_1", "sector": "TECH", "entry_price": 100, "current_price": 80, "atr": 5.0, "days_held": 5, "capital_allocated": 300000}, # Unhealthy
        {"symbol": "BAD_STOCK_2", "sector": "TECH", "entry_price": 100, "current_price": 85, "atr": 5.0, "days_held": 5, "capital_allocated": 300000}  # Unhealthy
    ]
    # Unhealthy (2) > Healthy (0) -> Should trigger RISK_OFF
    
    report_t2 = run_decision_engine(portfolio_t0, positions_t2, heatmap_t0, candidates_t0)
    print(f"Posture: {report_t2['market_posture']['market_posture']}")
    print(f"Reasons: {report_t2['market_posture']['reasons']}")
    
    # Verify Decisions (Should contain BLOCK_POSTURE or REDUCE_RISK)
    for d in report_t2["decisions"]:
        if d['type'] == 'CANDIDATE':
            print(f"Candidate Action: {d['action']} ({d['reason']})")


if __name__ == "__main__":
    run_demo()
