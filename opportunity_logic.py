"""
Opportunity Logic - Phase 2
===========================
Pure decision logic for evaluating portfolio opportunities.

This module contains ONLY evaluation logic.
- No API calls
- No market data fetching
- No external dependencies

Phase Boundary:
    Phase 1 (opportunity_scanner.py) → Market data ingestion
    Phase 2 (THIS FILE) → Opportunity evaluation logic
    Phase 3 (decision_engine.py) → Portfolio decisions & actions

Author: Quantitative Portfolio Engineering Team
"""


def scan_for_opportunities(positions: list, candidates: list, threshold: float = 15.0) -> dict:
    """
    Scans for relative efficiency opportunities by comparing the portfolio's 
    weakest link against the market's strongest candidate.
    
    Logic:
    1. Identify the 'Weakest Link': Position with the lowest Vitals Score.
    2. Identify the 'Top Prospect': Candidate with the highest Projected Efficiency.
    3. Compare: If (Top Prospect Score - Weakest Link Score) > Threshold, 
       then a significantly better opportunity exists.
       
    Args:
        positions (list): List of current positions with 'vitals_score'.
        candidates (list): List of candidate dicts with 'projected_efficiency'.
        threshold (float): Point difference required to consider the switch "significant".
                           Defaults to 15.0 to account for switching costs/friction.
                           
    Returns:
        dict: Report containing comparison metrics and boolean flag.
    """
    
    # ---------------------------------------------------------
    # 1. Analyze Current Portfolio (Find the Floor)
    # ---------------------------------------------------------
    if not positions:
        weakest_position = None
        min_vitals = 999.0  # Arbitrary high start
    else:
        # Find position with minimum vitals_score
        weakest_position = min(positions, key=lambda x: x.get("vitals_score", 0))
        min_vitals = float(weakest_position.get("vitals_score", 0))

    # For reporting purposes, we might also want the best held, 
    # but the swap logic relies on the worst.
    best_held_score = 0.0
    if positions:
        best_held_score = max([p.get("vitals_score", 0) for p in positions])

    # ---------------------------------------------------------
    # 2. Analyze External Opportunities (Find the Ceiling)
    # ---------------------------------------------------------
    if not candidates:
        top_candidate = None
        max_external_score = 0.0
    else:
        # Find candidate with maximum projected efficiency
        top_candidate = max(candidates, key=lambda x: x.get("projected_efficiency", 0))
        max_external_score = float(top_candidate.get("projected_efficiency", 0))

    # ---------------------------------------------------------
    # 3. Compute Relative Efficiency Gap
    # ---------------------------------------------------------
    # The gap that justifies a trade
    efficiency_gap = max_external_score - min_vitals
    
    better_opportunity_exists = False
    details = "No significant upgrade available."
    
    if positions and candidates:
        if efficiency_gap > threshold:
            better_opportunity_exists = True
            confidence = "HIGH" if efficiency_gap > (threshold * 2) else "MEDIUM"
            details = (
                f"Upgrade Opportunity: Swap {weakest_position['symbol']} ({min_vitals}) "
                f"for {top_candidate['symbol']} ({max_external_score}). "
                f"Efficiency Gain: +{round(efficiency_gap, 1)}"
            )
        else:
            confidence = "LOW"
            details = (
                f"Hold: Best external gap (+{round(efficiency_gap, 1)}) "
                f"does not exceed threshold ({threshold})."
            )
    elif not positions and candidates:
        # If we have no positions, any candidate is an opportunity (technically)
        better_opportunity_exists = True
        confidence = "HIGH"
        details = "Portfolio is empty. External opportunities available."
    else:
        confidence = "N/A"  # No candidates or other edge cases

    # ---------------------------------------------------------
    # 4. Construct Output
    # ---------------------------------------------------------
    return {
        "weakest_held_symbol": weakest_position['symbol'] if weakest_position else "N/A",
        "weakest_held_score": min_vitals if positions else 0.0,
        "best_external_symbol": top_candidate['symbol'] if top_candidate else "N/A",
        "best_external_score": max_external_score,
        "efficiency_gap": round(efficiency_gap, 1) if positions else max_external_score,
        "better_opportunity_exists": better_opportunity_exists,
        "confidence": confidence,
        "summary": details,
        # Including best held for context, though logic focuses on weakest
        "best_held_efficiency_context": best_held_score 
    }


# =============================================================================
# VALIDATION EXAMPLES
# =============================================================================
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("OPPORTUNITY LOGIC - Phase 2 Validation")
    print("=" * 60)
    
    # Test Case 1: Clear upgrade opportunity
    print("\n[Test 1] Clear Upgrade Opportunity")
    print("-" * 40)
    
    positions = [
        {"symbol": "LAGGING_CO", "vitals_score": 35.0},
        {"symbol": "STABLE_INC", "vitals_score": 60.0},
        {"symbol": "STAR_CORP", "vitals_score": 92.0}
    ]
    
    candidates = [
        {"symbol": "NEW_TECH", "projected_efficiency": 85.0},
        {"symbol": "HOT_BIO", "projected_efficiency": 70.0},
        {"symbol": "DULL_UTIL", "projected_efficiency": 40.0}
    ]
    
    result = scan_for_opportunities(positions, candidates, threshold=15.0)
    print(json.dumps(result, indent=2))
    print(f"Expected: better_opportunity_exists = True (gap = 50.0 > 15.0)")
    
    # Test Case 2: No significant opportunity
    print("\n[Test 2] No Significant Opportunity")
    print("-" * 40)
    
    positions_2 = [
        {"symbol": "STRONG_A", "vitals_score": 75.0},
        {"symbol": "STRONG_B", "vitals_score": 80.0}
    ]
    
    candidates_2 = [
        {"symbol": "MARKET_X", "projected_efficiency": 82.0}
    ]
    
    result_2 = scan_for_opportunities(positions_2, candidates_2, threshold=15.0)
    print(json.dumps(result_2, indent=2))
    print(f"Expected: better_opportunity_exists = False (gap = 7.0 < 15.0)")
    
    # Test Case 3: Empty portfolio
    print("\n[Test 3] Empty Portfolio")
    print("-" * 40)
    
    result_3 = scan_for_opportunities([], candidates, threshold=15.0)
    print(json.dumps(result_3, indent=2))
    print(f"Expected: better_opportunity_exists = True (portfolio empty)")
    
    print("\n" + "=" * 60)
    print("Validation Complete")
    print("=" * 60)
