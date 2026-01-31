"""
execution_planner.py

Phase 3 -> 4 Bridge (Planning Layer).
Converts Phase 3 decisions into specific proposed actions (NO execution).
Strictly follows the rule: Weakest positions are addressed first.

Output Contract:
{
    "proposed_actions": [
        {
            "symbol": "ABC",
            "action": "REDUCE | HOLD | MONITOR",
            "reason": "Text explanation"
        }
    ]
}
"""

import json

def generate_execution_plan(decision_output: dict, positions: list[dict]) -> dict:
    """
    Generates a list of proposed actions based on the decision mode and position vitals.

    Args:
        decision_output (dict): Output from Phase 3 (e.g., {"decision": "DEFENSIVE", ...})
        positions (list[dict]): List of position dicts with at least 'symbol' and 'vitals_score'.

    Returns:
        dict: conformant to output contract.
    """
    mode = decision_output.get("decision", "NEUTRAL")
    
    # 1. Sort positions by vitals (Weakest First)
    # Default to 100 if score missing to push reliable data to front if needed, 
    # but here we want weak ones first, so 0 is worst.
    sorted_positions = sorted(positions, key=lambda p: p.get("vitals_score", 0))

    proposed_actions = []

    for pos in sorted_positions:
        symbol = pos.get("symbol", "UNKNOWN")
        vitals = pos.get("vitals_score", 0)
        
        action = "MONITOR"
        reason = "Standard monitoring."

        # 2. Apply Mode Logic
        if mode == "RISK_OFF":
            action = "EXIT"
            reason = f"RISK_OFF trigger. Exiting all positions (Vitals: {vitals})."
            
        elif mode == "DEFENSIVE":
            if vitals < 50:
                action = "REDUCE"
                reason = f"Defensive mode + Weak vitals ({vitals}). reducing exposure."
            else:
                action = "HOLD"
                reason = f"Defensive mode. Holding strong position ({vitals})."
                
        elif mode == "OPPORTUNITY":
            action = "MONITOR"
            reason = "Opportunity mode. No forced exits."

        proposed_actions.append({
            "symbol": symbol,
            "action": action,
            "reason": reason
        })

    return {
        "proposed_actions": proposed_actions
    }

# ---------------------------------------------------------
# Standalone Demonstration
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Execution Planner Verification...")
    print("-" * 40)

    # Mock Data
    mock_positions = [
        {"symbol": "STRONG_TECH", "vitals_score": 85},
        {"symbol": "WEAK_RETAIL", "vitals_score": 30},
        {"symbol": "MID_FINANCE", "vitals_score": 60}
    ]

    scenarios = [
        {"decision": "DEFENSIVE"},
        {"decision": "RISK_OFF"},
        {"decision": "OPPORTUNITY"}
    ]

    for scenario in scenarios:
        print(f"Scenario: {scenario['decision']}")
        plan = generate_execution_plan(scenario, mock_positions)
        print(json.dumps(plan, indent=2))
        print("-" * 40)
