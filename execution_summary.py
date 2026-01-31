"""
execution_summary.py

Phase 3 -> 4 Bridge (Reporting Layer).
Consolidates execution outcomes into a read-only summary object for UI/CLI consumption.
Strictly deterministic. No decision logic.

Output Contract:
{
  "decision": "DEFENSIVE",
  "actions_proposed": 3,
  "actions_blocked": 1,
  "final_mode": "CAPITAL_PRESERVATION"
}
"""

import json

def generate_execution_summary(decision_context: dict) -> dict:
    """
    Generates a read-only summary of the execution plan.

    Args:
        decision_context (dict): Pre-computed decision data.
            Expected keys (example):
            - 'primary_intent': str
            - 'proposed_actions': list
            - 'blocked_actions': list
            - 'mode': str

    Returns:
        dict: Normalized summary complying with the strict contract.
    """
    # Extract values with safe defaults (Read-Only)
    decision = decision_context.get("primary_intent", "UNKNOWN")
    proposed_count = len(decision_context.get("proposed_actions", []))
    blocked_count = len(decision_context.get("blocked_actions", []))
    mode = decision_context.get("mode", "STANDARD")

    # Construct strictly formatted outcome
    summary = {
        "decision": decision,
        "actions_proposed": proposed_count,
        "actions_blocked": blocked_count,
        "final_mode": mode
    }

    return summary

# ---------------------------------------------------------
# Standalone Demonstration
# ---------------------------------------------------------
if __name__ == "__main__":
    # Mock Input (Simulating upstream Phase 3 decision engine)
    mock_input = {
        "primary_intent": "DEFENSIVE",
        "proposed_actions": ["SELL_WEAK_HOLDING", "HEDGE_POSITION", "CANCEL_BUY_ORDER"],
        "blocked_actions": ["BUY_DIP_AGGRESSIVE"],
        "mode": "CAPITAL_PRESERVATION"
    }

    # Execute
    result = generate_execution_summary(mock_input)

    # Output as JSON (for downstream consumption)
    print(json.dumps(result, indent=2))
