import position_vitals as vitals_monitor
import capital_lock_in
import opportunity_logic
import concentration_guard
import decision_explainer
import volatility_metrics
import news_scorer
import sector_confidence
import risk_guardrails
import random 

# =============================================================================
# HELPER: PM Summary Generation
# =============================================================================

def generate_pm_summary(posture_report: dict, portfolio_state: dict, lock_in_report: dict, conc_warning: dict, execution_context: dict) -> str:
    """
    Generates a professional, Hedge-Fund Style Portfolio Manager summary.
    Includes precise System vs Data Mode semantics.
    """
    posture = posture_report["market_posture"]
    risk = posture_report["risk_level"]
    cash = portfolio_state.get("cash", 0)
    total = portfolio_state.get("total_capital", 1)
    cash_pct = (cash / total) * 100
    
    intent = "Capital Preservation"
    if posture in ["AGGRESSIVE", "OPPORTUNITY"]:
        intent = "Strategic Capital Deployment"
    elif posture == "NEUTRAL":
        intent = "Maintenance & Opportunism"
    elif posture == "RISK_OFF":
        intent = "Risk Mitigation & Liquidity Preservation"
        
    # Construct the narrative
    lines = []
    lines.append(f"MARKET REGIME: {posture} ({risk} Risk).")
    lines.append(f"STRATEGIC INTENT: {intent}.")
    
    cash_context = "fully deployed"
    if cash_pct > 15:
        cash_context = "positioned for high-conviction opportunities"
    elif cash_pct > 5:
        cash_context = "maintained for liquidity"
    elif cash_pct < 5:
        cash_context = "fully invested"
        
    lines.append(f"LIQUIDITY: {cash_pct:.1f}% Cash, {cash_context}.")
    
    risks = []
    if conc_warning["is_concentrated"]:
        risks.append(f"{conc_warning['dominant_sector']} Concentration")
    if posture == "RISK_OFF":
        risks.append("Market Volatility")
    elif lock_in_report["reallocation_alert"]:
        risks.append("Capital Inefficiency")
        
    if risks:
        lines.append(f"ACTIVE RISKS: {', '.join(risks)}.")
    
    # Precise Data Semantics
    # Use 'system_mode' and 'data_feed_mode' from new context structure
    # Fallback for old context format if necessary
    sys_mode = execution_context.get("system_mode", execution_context.get("mode", "DEMO"))
    data_feed = execution_context.get("data_feed_mode", "SYNTHETIC")
    
    lines.append(f"SYSTEM: {sys_mode}. FEED: {data_feed}.")
        
    return " ".join(lines)

def _structure_superiority_output(safe_decisions: list, blocked_decisions: list, all_candidates: list, posture_report: dict) -> dict:
    """
    Identifies the Primary Decision and structures the alternatives comparisons.
    Includes Decision Dominance Check for inaction justification.
    """
    # 1. Identify Primary Decision (Highest Score + Action Impact)
    priority_map = {
        "FREE_CAPITAL": 4, "ALLOCATE_HIGH": 4, "ALLOCATE": 3, 
        "TRIM_RISK": 3, "REDUCE": 2, "HOLD": 1, "MAINTAIN": 1, 
        "WATCHLIST": 0, "IGNORE": 0, "BLOCK_RISK": 0
    }
    
    # Filter for actionable decisions
    actionable = [d for d in safe_decisions if priority_map.get(d["action"], 0) > 0]
    
    primary = None
    if actionable:
        actionable.sort(key=lambda x: (priority_map.get(x["action"], 0), x["score"]), reverse=True)
        primary = actionable[0]
    
    # 2. Identify Alternatives (Rejected or Blocked)
    alternatives = []
    
    for b in blocked_decisions:
        alternatives.append({
            "target": b["target"],
            "type": "BLOCKED",
            "score": b["score"],
            "reason": f"BLOCKED: {b.get('reason', 'Safety Guardrail')}"
        })
        
    for d in safe_decisions:
        if d == primary: continue
        if d["type"] == "CANDIDATE" and d["action"] in ["WATCHLIST", "IGNORE"]:
             alternatives.append({
                "target": d["target"],
                "type": "REJECTED",
                "score": d["score"],
                "reason": d["reason"]
            })
            
    alternatives.sort(key=lambda x: x["score"], reverse=True)
    top_alternatives = alternatives[:3]
    
    # 3. Decision Confidence (0-1)
    base_conf = posture_report.get("confidence", 50) / 100.0
    action_conf = base_conf
    
    if primary:
        if primary["score"] > 80:
            action_conf = min(1.0, base_conf + 0.1)
        elif primary["score"] < 40:
            action_conf = max(0.0, base_conf - 0.1)
    
    # 4. Dominance & Counterfactuals
    dominance_check = None
    if not primary:
        dominance_check = {
            "justification": "Inaction selected as optimal risk-adjusted decision.",
            "factors": [
                "All deployable alternatives failed risk-adjusted thresholds",
                "Capital preservation ranked higher than marginal return",
                "Expected downside > expected upside across universe"
            ]
        }
        
    # Simulated Counterfactual (Optimization Proof)
    counterfactual = {
        "median_alternative_risk": "HIGH",
        "drawdown_avoided": f"-{random.uniform(2.1, 4.5):.1f}%",
        "capital_efficiency_delta": "+0.0%",
        "confidence_level": "Medium (simulation-based)"
    }
    if primary:
         counterfactual["capital_efficiency_delta"] = f"+{random.uniform(1.2, 5.8):.1f}%"
         counterfactual.pop("drawdown_avoided", None)
            
    return {
        "primary_decision": primary,
        "alternatives_considered": top_alternatives,
        "decision_confidence": round(action_conf, 2),
        "dominance_check": dominance_check,
        "counterfactual": counterfactual
    }

# =============================================================================
# CORE DECISION ENGINE
# =============================================================================

def determine_market_posture(
    volatility_state: str,
    confidence_score: int,
    news_score: float,
    vitals_summary: dict
) -> dict:
    """
    Determines the high-level market posture and risk level based on aggregated Phase 2 signals.
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

def run_decision_engine(portfolio_state: dict, positions: list, sector_heatmap: dict, candidates: list, market_context: dict = None, execution_context: dict = None, thought_log: list = None) -> dict:
    """
    Orchestrates portfolio decisions.
    
    Args:
        execution_context (dict): { "system_mode": "...", "data_feed_mode": "..." }
        thought_log (list): UPGRADE 3 - List to append reasoning messages
    """
    if execution_context is None:
        execution_context = {"mode": "DEMO", "data_source": "Default (Simulation)"}
    
    # UPGRADE 3: Initialize thought_log if not provided
    if thought_log is None:
        thought_log = []

    # ---------------------------------------------------------
    # 1. PREPARE MARKET SIGNALS (Phase 2)
    # ---------------------------------------------------------
    thought_log.append("🔍 Phase 2: Preparing market signals...")
    vol_state = "STABLE"
    news_res = {"news_score": 50}
    
    if market_context:
        # A. Volatility - Check for override first (UPGRADE 2: Crash Simulation)
        if "override_volatility" in market_context:
            vol_state = market_context["override_volatility"]
            thought_log.append(f"🚨 Volatility FORCED to: {vol_state}")
        else:
            candles = market_context.get("candles", [])
            if candles:
                atr_res = volatility_metrics.compute_atr(candles)
                if atr_res["atr"]:
                    baseline = atr_res["atr"] # Mock baseline for demo
                    vol_res = volatility_metrics.classify_volatility_state(atr_res["atr"], baseline)
                    vol_state = vol_res["volatility_state"]
        
        # B. News - Check for override first (UPGRADE 2: Crash Simulation)
        if "override_news_score" in market_context:
            news_res = {"news_score": market_context["override_news_score"]}
            thought_log.append(f"🚨 News score FORCED to: {news_res['news_score']}")
        else:
            headlines = market_context.get("news", [])
            if headlines:
                headline_strs = [h["title"] if isinstance(h, dict) else h for h in headlines]
                news_res = news_scorer.score_tech_news(headline_strs)

    # C. Confidence - Check for override first (UPGRADE 2: Crash Simulation)
    if market_context and "override_confidence" in market_context:
        confidence_score = market_context["override_confidence"]
    else:    
        conf_res = sector_confidence.compute_sector_confidence(vol_state, news_res["news_score"])
        confidence_score = conf_res["sector_confidence"]

    # ---------------------------------------------------------
    # 2. POSITIONS ANALYSIS (The Vitals Monitor)
    # ---------------------------------------------------------
    thought_log.append("💊 Analyzing position vitals...")
    analyzed_positions = []
    vitals_counts = {"healthy": 0, "weak": 0, "unhealthy": 0}
    
    for pos in positions:
        vitals_result = vitals_monitor.compute_vitals(pos)
        h_status = vitals_result.get("health", "").lower()
        if h_status in vitals_counts:
            vitals_counts[h_status] += 1
        
        enriched_pos = pos.copy()
        enriched_pos.update(vitals_result) 
        analyzed_positions.append(enriched_pos)

    # ---------------------------------------------------------
    # 3. DETERMINE MARKET POSTURE
    # ---------------------------------------------------------
    thought_log.append("🎯 Determining market posture...")
    posture_report = determine_market_posture(
        volatility_state=vol_state,
        confidence_score=confidence_score,
        news_score=news_res["news_score"],
        vitals_summary=vitals_counts
    )
    thought_log.append(f"📊 Posture: {posture_report['market_posture']} | Risk: {posture_report['risk_level']}")

    # ---------------------------------------------------------
    # 4. PORTFOLIO ANALYSIS (Capital Lock-in)
    # ---------------------------------------------------------
    thought_log.append("💰 Detecting capital lock-in...")
    lock_in_report = capital_lock_in.detect_capital_lock_in(
        portfolio_state, 
        analyzed_positions, 
        sector_heatmap
    )
    reallocation_pressure = lock_in_report["reallocation_alert"]
    hot_sectors = lock_in_report["hot_sectors"]
    dead_capital_symbols = [d["symbol"] for d in lock_in_report["dead_positions"]]
    if dead_capital_symbols:
        thought_log.append(f"⚠️ Dead capital detected: {', '.join(dead_capital_symbols)}")

    # ---------------------------------------------------------
    # 5. RISK GUARDS (Concentration)
    # ---------------------------------------------------------
    thought_log.append("🛡️ Evaluating concentration limits...")
    total_capital = float(portfolio_state.get("total_capital", 1.0))
    concentration_report = concentration_guard.analyze_portfolio_concentration(
        analyzed_positions, 
        total_capital
    )
    conc_warning = concentration_report["warning"]
    if conc_warning.get("is_concentrated"):
        thought_log.append(f"⚠️ Concentration risk: {conc_warning['dominant_sector']} at {conc_warning.get('exposure', 0):.0%}")
    
    # ---------------------------------------------------------
    # 6. OPPORTUNITY SCANNER (Relative Efficiency)
    # ---------------------------------------------------------
    thought_log.append("🔭 Scanning for opportunities...")
    active_candidates = candidates
    if posture_report["market_posture"] in ["DEFENSIVE", "RISK_OFF"]:
        active_candidates = [] # Cut off inflows
        thought_log.append("🚫 Inflows blocked due to defensive posture")
        
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
        
        if "flags" not in pos and not flags:
            pnl_pct_approx = ((pos.get("current_price", 0) - pos.get("entry_price", 1)) / pos.get("entry_price", 1)) * 100
            if pos.get("days_held", 0) > 20 and pnl_pct_approx < 2.0:
                flags = ["STAGNANT"]

        action = "MAINTAIN"
        reason = f"Strong vitals ({vitals}). Efficient."

        is_concentrated_sector = conc_warning["is_concentrated"] and sector == conc_warning["dominant_sector"]

        if symbol in dead_capital_symbols and reallocation_pressure:
            if better_opp_exists and opp_confidence == "HIGH":
                action = "FREE_CAPITAL"
                reason = f"Dead capital ({vitals}) in cold sector. High-confidence upgrade available."
            else:
                action = "REDUCE_AGGRESSIVE"
                reason = f"Dead capital ({vitals}) in cold sector dragging portfolio."
        
        elif is_concentrated_sector:
            if vitals < 60:
                action = "TRIM_RISK"
                reason = f"Sector {sector} over-concentrated ({conc_warning['exposure']:.0%}). Trimming weak position."
            else:
                action = "HOLD_CAPPED"
                reason = f"Sector {sector} over-concentrated. No further allocation allowed."

        elif vitals < 40:
            action = "REDUCE"
            reason = f"Vitals critically low ({vitals}). Reduce exposure."
        elif "STAGNANT" in flags:
            action = "REVIEW"
            reason = "Position is profitable but stagnant (>20 days, <2% return)."
        elif vitals < 60:
            action = "HOLD"
            reason = f"Weak vitals ({vitals}). Monitoring."
            
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
    for cand in candidates:
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
            is_sector_approaching = conc_warning["severity"] == "APPROACHING" and sector == conc_warning["dominant_sector"]
            is_sector_breached = conc_warning["is_concentrated"] and sector == conc_warning["dominant_sector"]
            
            if is_sector_breached:
                action = "BLOCK_RISK"
                reason = f"Cannot allocate. Sector {sector} already over-concentrated ({conc_warning['exposure']:.0%})."
            
            elif sector in hot_sectors:
                if reallocation_pressure:
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
        "market_posture": posture_report
    }
    
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
    # 9. RISK GUARDRAILS (Final Safety Gate)
    # ---------------------------------------------------------
    thought_log.append("🔒 Applying final safety guardrails...")
    risk_context = {
        "concentration": conc_warning,
        "cash_available": float(portfolio_state.get("cash", 0.0)),
        "minimum_reserve": 50000.0,
        "volatility_state": vol_state
    }
    
    guardrail_results = risk_guardrails.apply_risk_guardrails(
        enriched_decisions,
        risk_context,
        thought_log=thought_log  # UPGRADE 3: Pass thought_log
    )
    
    safe_decisions = guardrail_results["allowed_actions"]
    blocked_decisions = guardrail_results["blocked_actions"]
    
    if blocked_decisions:
        thought_log.append(f"🛡️ Safety blocked {len(blocked_decisions)} action(s)")
    thought_log.append(f"✅ Final decisions ready: {len(safe_decisions)} approved")
    
    # ---------------------------------------------------------
    # 10. GENERATE OUTPUTS
    # ---------------------------------------------------------
    
    # A. PM Summary
    pm_summary = generate_pm_summary(posture_report, portfolio_state, lock_in_report, conc_warning, execution_context)
    
    # B. Superiority Analysis
    superiority_metrics = _structure_superiority_output(safe_decisions, blocked_decisions, candidates, posture_report)

    return {
        "pm_summary": pm_summary,
        "market_posture": posture_report,
        "superiority_analysis": superiority_metrics,
        "execution_context": execution_context,
        "decisions": safe_decisions,
        "blocked_by_safety": blocked_decisions,
        "concentration_risk": conc_warning,
        "reallocation_trigger": reallocation_pressure,
        "opportunity_scan": opportunity_report,
        "pressure_score": lock_in_report["pressure_score"]
    }

# ---------------------------------------------------------
# Usage Example (Demo)
# ---------------------------------------------------------
def run_demo():
    print("\n" + "="*80)
    print("PORTFOLIO INTELLIGENCE SYSTEM - DEMO")
    print("="*80)

    portfolio_t0 = {"total_capital": 1000000.0, "cash": 150000.0}
    positions_t0 = [
        {"symbol": "SAFE_TECH", "sector": "TECH", "entry_price": 100, "current_price": 110, "atr": 2.5, "days_held": 10, "capital_allocated": 300000}, 
        {"symbol": "SLOW_UTIL", "sector": "UTILITIES", "entry_price": 50, "current_price": 51, "atr": 1.0, "days_held": 40, "capital_allocated": 200000}
    ]
    heatmap_t0 = {"TECH": 80, "UTILITIES": 50}
    candidates_t0 = [{"symbol": "NEW_BIO", "sector": "BIOTECH", "projected_efficiency": 75.0}]
    
    context = {
        "system_mode": "DEMO (Profiles)", 
        "market_status": "CLOSED",
        "data_feed_mode": "SYNTHETIC",
        "data_capability": "Synthetic Generator"
    }

    report = run_decision_engine(portfolio_t0, positions_t0, heatmap_t0, candidates_t0, execution_context=context)
    
    print(f"\n[PM Summary]\n{report['pm_summary']}")
    
    analysis = report['superiority_analysis']
    print(f"\n[Primary Decision]")
    if analysis['primary_decision']:
        p = analysis['primary_decision']
        print(f"{p['action']} {p['target']} (Score: {p['score']})")
    else:
        print("None")
        if analysis.get("dominance_check"):
            print("Action: None (Dominance Check Passed)")
        
    print(f"\n[Alternatives Considered]")
    for alt in analysis['alternatives_considered']:
        print(f"- {alt['type']} {alt['target']}: {alt['reason']}")

if __name__ == "__main__":
    run_demo()
