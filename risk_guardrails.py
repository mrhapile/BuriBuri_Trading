"""
Risk Guardrails - Phase 3 Final Safety Gate
=============================================
Filters proposed decisions through mandatory safety rules.

Architecture Notes:
    - NO signal recomputation
    - NO decision override (only filtering)
    - NO API calls or external dependencies
    - Crash-proof with defensive defaults

Safety Philosophy:
    - Safety ALWAYS overrides strategy
    - When uncertain, BLOCK
    - Every block includes clear reason

Author: Quantitative Portfolio Engineering Team
"""

from typing import List, Dict, Any


def apply_risk_guardrails(
    proposed_decisions: List[Dict[str, Any]],
    risk_context: Dict[str, Any],
    thought_log: List[str] = None
) -> Dict[str, Any]:
    """
    Filters proposed decisions through mandatory safety rules.
    
    This is the FINAL safety gate before execution approval.
    All inputs are pre-computed; this function performs NO calculations.
    
    Safety Rules Enforced:
        1. Sector Concentration Guard
        2. Cash Reserve Guard
        3. Volatility × Aggression Guard
    
    Args:
        proposed_decisions (list): Enriched decision dicts from decision_explainer
        risk_context (dict): Pre-computed risk signals:
            {
                "concentration": { "is_concentrated": bool, "dominant_sector": str, "severity": str },
                "cash_available": float,
                "minimum_reserve": float,
                "volatility_state": str  # "EXPANDING" | "STABLE" | "CONTRACTING"
            }
        thought_log (list): UPGRADE 3 - List to append safety reasoning
    
    Returns:
        dict: {
            "allowed_actions": List[Dict],
            "blocked_actions": List[Dict with "safety_reason" field]
        }
    """
    
    # UPGRADE 3: Initialize thought_log if not provided
    if thought_log is None:
        thought_log = []
    
    # =========================================================================
    # DEFENSIVE INPUT VALIDATION
    # =========================================================================
    if not proposed_decisions or not isinstance(proposed_decisions, list):
        return {"allowed_actions": [], "blocked_actions": []}
    
    if not risk_context or not isinstance(risk_context, dict):
        # No risk context = cannot assess safety = block all
        return {
            "allowed_actions": [],
            "blocked_actions": [
                {**d, "safety_reason": "Safety check failed: missing risk context"}
                for d in proposed_decisions
            ]
        }
    
    # Extract signals with safe defaults
    concentration = risk_context.get("concentration", {})
    is_concentrated = concentration.get("is_concentrated", False)
    dominant_sector = concentration.get("dominant_sector", "UNKNOWN")
    severity = concentration.get("severity", "NONE")
    
    cash_available = float(risk_context.get("cash_available", 0.0))
    minimum_reserve = float(risk_context.get("minimum_reserve", 50000.0))
    
    volatility_state = risk_context.get("volatility_state", "STABLE")
    
    # =========================================================================
    # APPLY SAFETY RULES
    # =========================================================================
    allowed = []
    blocked = []
    
    for decision in proposed_decisions:
        action_type = decision.get("action", "UNKNOWN")
        sector = decision.get("sector", "UNKNOWN")
        
        block_reason = None
        
        # ---------------------------------------------------------------------
        # RULE 1: Sector Concentration Guard
        # ---------------------------------------------------------------------
        if is_concentrated and sector == dominant_sector:
            increasing_actions = {
                "ALLOCATE", "ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE",
                "SCALE_UP", "DOUBLE_DOWN", "ADD_POSITION"
            }
            if action_type in increasing_actions:
                block_reason = "Sector concentration breach"
        
        if severity == "APPROACHING" and sector == dominant_sector:
            aggressive_allocs = {"ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE", "SCALE_UP"}
            if action_type in aggressive_allocs:
                block_reason = "Sector concentration breach"
        
        # ---------------------------------------------------------------------
        # RULE 2: Cash Reserve Guard
        # ---------------------------------------------------------------------
        if cash_available < minimum_reserve:
            capital_actions = {
                "ALLOCATE", "ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE",
                "ALLOCATE_CAPPED", "ALLOCATE_CAUTIOUS",
                "SCALE_UP", "ADD_POSITION", "DOUBLE_DOWN"
            }
            if action_type in capital_actions:
                block_reason = "Insufficient cash reserve"
        
        # ---------------------------------------------------------------------
        # RULE 3: Volatility × Aggression Guard
        # ---------------------------------------------------------------------
        if volatility_state == "EXPANDING":
            aggressive_actions = {"ALLOCATE_AGGRESSIVE", "SCALE_UP", "DOUBLE_DOWN"}
            if action_type in aggressive_actions:
                block_reason = "Aggressive action blocked during expanding volatility"
        
        # ---------------------------------------------------------------------
        # DECISION: ALLOW or BLOCK
        # ---------------------------------------------------------------------
        if block_reason:
            blocked_decision = decision.copy()
            blocked_decision["safety_reason"] = block_reason
            blocked.append(blocked_decision)
            # UPGRADE 3: Log blocked action
            thought_log.append(f"🚫 BLOCKED: {decision.get('target', 'N/A')} — {block_reason}")
        else:
            allowed.append(decision)
    
    return {
        "allowed_actions": allowed,
        "blocked_actions": blocked
    }


def summarize_guardrail_results(results: Dict[str, Any]) -> str:
    """
    Creates a human-readable summary of guardrail filtering.
    
    Args:
        results: Output from apply_risk_guardrails()
    
    Returns:
        str: Summary text
    """
    allowed_count = len(results.get("allowed_actions", []))
    blocked_count = len(results.get("blocked_actions", []))
    
    if blocked_count == 0:
        return f"All {allowed_count} actions passed safety checks."
    
    # Group by reason
    blocked = results.get("blocked_actions", [])
    reasons = {}
    for b in blocked:
        reason = b.get("safety_reason", "Unknown")
        reasons.setdefault(reason, []).append(b.get("target", "N/A"))
    
    parts = [f"Safety: {allowed_count} allowed, {blocked_count} blocked."]
    for reason, symbols in reasons.items():
        parts.append(f"  - {reason}: {', '.join(symbols)}")
    
    return " ".join(parts)


# =============================================================================
# STANDALONE TESTS
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RISK GUARDRAILS - Standalone Validation")
    print("=" * 70)
    
    # Test 1: Sector Concentration Block
    print("\n[Test 1] Sector Concentration Guard")
    actions_1 = [
        {"target": "TECH_A", "action": "ALLOCATE_HIGH", "type": "CANDIDATE", "sector": "TECH", "reasons": ["Hot sector"]},
        {"target": "BIO_B", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "BIOTECH", "reasons": ["Opportunity"]}
    ]
    context_1 = {
        "concentration": {"is_concentrated": True, "dominant_sector": "TECH", "severity": "BREACH"},
        "cash_available": 100000.0,
        "minimum_reserve": 50000.0,
        "volatility_state": "STABLE"
    }
    result_1 = apply_risk_guardrails(actions_1, context_1)
    print(f"  Allowed: {len(result_1['allowed_actions'])}, Blocked: {len(result_1['blocked_actions'])}")
    assert len(result_1['blocked_actions']) == 1
    print("  ✓ TECH allocation blocked")
    
    # Test 2: Cash Reserve Block
    print("\n[Test 2] Cash Reserve Guard")
    actions_2 = [
        {"target": "NEW_STOCK", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "ENERGY", "reasons": ["Opportunity"]},
        {"target": "OLD_STOCK", "action": "REDUCE", "type": "POSITION", "sector": "UTILITIES", "reasons": ["Exit"]}
    ]
    context_2 = {
        "concentration": {"is_concentrated": False},
        "cash_available": 30000.0,
        "minimum_reserve": 50000.0,
        "volatility_state": "STABLE"
    }
    result_2 = apply_risk_guardrails(actions_2, context_2)
    assert len(result_2['blocked_actions']) == 1
    assert "cash reserve" in result_2['blocked_actions'][0]['safety_reason']
    print("  ✓ Allocation blocked due to low cash")
    
    # Test 3: Volatility × Aggression Block
    print("\n[Test 3] Volatility × Aggression Guard")
    actions_3 = [
        {"target": "SAFE", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "UTIL", "reasons": ["Safe"]},
        {"target": "RISKY", "action": "ALLOCATE_AGGRESSIVE", "type": "CANDIDATE", "sector": "TECH", "reasons": ["Opportunity"]}
    ]
    context_3 = {
        "concentration": {"is_concentrated": False},
        "cash_available": 100000.0,
        "minimum_reserve": 50000.0,
        "volatility_state": "EXPANDING"
    }
    result_3 = apply_risk_guardrails(actions_3, context_3)
    assert len(result_3['blocked_actions']) == 1
    assert "volatility" in result_3['blocked_actions'][0]['safety_reason']
    print("  ✓ Aggressive action blocked during expanding volatility")
    
    # Test 4: Crash-Proof
    print("\n[Test 4] Crash-Proof Handling")
    r4a = apply_risk_guardrails([], {})
    assert r4a['allowed_actions'] == []
    print("  ✓ Empty input handled")
    
    r4b = apply_risk_guardrails([{"target": "X"}], None)
    assert len(r4b['blocked_actions']) == 1
    print("  ✓ None context blocks all")
    
    print("\n" + "=" * 70)
    print("✅ All Safety Tests Passed")
    print("=" * 70)
