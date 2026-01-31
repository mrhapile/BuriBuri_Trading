import vitals_monitor
import capital_lock_in

def run_decision_engine(portfolio_state: dict, positions: list, sector_heatmap: dict, candidates: list) -> dict:
    """
    Orchestrates portfolio decisions by combining Vitals Monitoring (Part A) 
    and Capital Lock-in Detection (Part B).

    Args:
        portfolio_state (dict): {total_capital, cash, ...}
        positions (dict): List of raw position dictionaries
        sector_heatmap (dict): {sector_name: heat_score}
        candidates (list): List of potential new trades {symbol, sector, conviction}

    Returns:
        dict: Final decision report containing:
            - portfolio_health (summary from Part B)
            - actions (list of specific actions per position/candidate)
            - reallocation_needed (bool)
    """
    
    # ---------------------------------------------------------
    # 1. POSITIONS ANALYSIS (The Vitals Monitor)
    # ---------------------------------------------------------
    analyzed_positions = []
    
    for pos in positions:
        # Compute Vitals Score
        vitals_result = vitals_monitor.compute_vitals(pos)
        
        # Merge results back into position object for Part B consumption
        # We need sector and allocated capital for Part B
        enriched_pos = pos.copy()
        enriched_pos.update(vitals_result) # adds vitals_score, health, etc.
        analyzed_positions.append(enriched_pos)

    # ---------------------------------------------------------
    # 2. PORTFOLIO ANALYSIS (Capital Lock-in Detector)
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
    # 3. DECISION SYNTHESIS
    # ---------------------------------------------------------
    decisions = []
    
    # A. Process Existing Positions
    for pos in analyzed_positions:
        symbol = pos["symbol"]
        vitals = pos["vitals_score"]
        flags = pos.get("flags", [])
        
        # Robust Logic: Fallback stagnation check if flags missing
        if "flags" not in pos and not flags:
            pnl_pct_approx = ((pos.get("current_price", 0) - pos.get("entry_price", 1)) / pos.get("entry_price", 1)) * 100
            if pos.get("days_held", 0) > 20 and pnl_pct_approx < 2.0:
                flags = ["STAGNANT"]
        
        reason = ""
        action = ""
        
        # Case 1: Dead Capital in a Reallocation Scenario (CRITICAL)
        if symbol in dead_capital_symbols and reallocation_pressure:
            action = "FREE_CAPITAL" # Previously EXIT_NOW
            reason = f"Dead capital ({vitals} score) in cold sector; urgent reallocation needed."
        
        # Case 2: Unhealthy but no portfolio-wide pressure yet
        elif vitals < 40:
            action = "REDUCE"
            reason = f"Vitals critically low ({vitals}). Reduce exposure."
            
        # Case 3: Stagnant
        elif "STAGNANT" in flags:
            action = "REVIEW"
            reason = f"Position is profitable but stagnant (>20 days, <2% return)."
            
        # Case 4: Weak/Mediocre
        elif vitals < 60:
            action = "HOLD"
            reason = f"Weak vitals ({vitals}), monitoring for improvement."
            
        # Case 5: Healthy
        else:
            action = "MAINTAIN" 
            reason = f"Strong vitals ({vitals}). Efficient use of capital."
            
        decisions.append({
            "target": symbol,
            "type": "POSITION",
            "action": action,
            "reason": reason,
            "score": vitals
        })

    # B. Process New Candidates (Opportunity matching)
    for cand in candidates:
        symbol = cand["symbol"]
        sector = cand["sector"]
        
        # Only interested if sector is HOT or we have high conviction
        if sector in hot_sectors:
            if reallocation_pressure:
                action = "ALLOCATE_HIGH" # Previously BUY_AGGRESSIVE
                reason = f"Hot sector ({sector}) opportunity. Deploying freed-up capital."
            # Simple liquidity heuristic for MVP demo
            elif portfolio_state["cash"] > 100000: 
                action = "ALLOCATE" # Previously BUY
                reason = f"Hot sector ({sector}). Sufficient cash available."
            else:
                action = "WATCHLIST"
                reason = f"Hot sector ({sector}) but limited capital availability."
        else:
            action = "IGNORE"
            reason = f"Sector ({sector}) is not currently attractive."
            
        decisions.append({
            "target": symbol,
            "type": "CANDIDATE",
            "action": action,
            "reason": reason,
            "score": "N/A"
        })

    # ---------------------------------------------------------
    # 4. Final Output Construction
    # ---------------------------------------------------------
    return {
        "portfolio_summary": lock_in_report["summary"],
        "pressure_score": lock_in_report["pressure_score"],
        "reallocation_trigger": reallocation_pressure,
        "decisions": decisions
    }

# ---------------------------------------------------------
# Usage Example (Demo)
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Setup Data
    portfolio = {
        "total_capital": 1000000.0,
        "cash": 50000.0 # Low cash, high pressure if locks exist
    }
    
    # Current Positions (Mix of good, bad, and stagnant)
    positions = [
        # Dead Capital Candidate (Cold sector, low vitals)
        {
            "symbol": "OLD_STEEL",
            "sector": "MATERIALS", # Cold
            "entry_price": 100, "current_price": 95, "atr": 2.0,
            "days_held": 45, "capital_allocated": 300000
        },
        # Stagnant Candidate
        {
            "symbol": "BIG_TELCO",
            "sector": "TELECOM", # Neutral
            "entry_price": 50, "current_price": 50.5, "atr": 0.5,
            "days_held": 30, "capital_allocated": 200000
        },
        # Star Performer
        {
            "symbol": "AI_CHIP",
            "sector": "TECH", # Hot
            "entry_price": 200, "current_price": 280, "atr": 5.0,
            "days_held": 15, "capital_allocated": 200000
        }
    ]
    
    # Market State
    heatmap = {
        "TECH": 90,       # Very Hot
        "MATERIALS": 20,  # Cold
        "TELECOM": 50,    # Neutral
        "BIOTECH": 80     # Hot
    }
    
    # New Opportunities
    candidates = [
        {"symbol": "NEW_BIO", "sector": "BIOTECH"},
        {"symbol": "CEMENT_CO", "sector": "MATERIALS"}
    ]

    # 2. Run Engine
    report = run_decision_engine(portfolio, positions, heatmap, candidates)
    
    # 3. Print Report
    print("\n=== PORTFOLIO DECISION REPORT ===")
    print(f"Summary: {report['portfolio_summary']}")
    print(f"Reallocation Triggered: {report['reallocation_trigger']} (Score: {report['pressure_score']})")
    print("-" * 60)
    print(f"{'TARGET':<12} | {'TYPE':<10} | {'ACTION':<15} | {'REASON'}")
    print("-" * 60)
    for d in report["decisions"]:
        print(f"{d['target']:<12} | {d['type']:<10} | {d['action']:<15} | {d['reason']}")
