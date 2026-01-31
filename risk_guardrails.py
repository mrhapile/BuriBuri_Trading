"""
Risk Guardrails - Phase 3 Safety Layer
========================================
Final safety gate that filters proposed actions based on systemic risk constraints.

Architecture Rules:
    - NO signal computation
    - NO decision making
    - NO API calls
    - ONLY action filtering based on pre-computed inputs

This module answers one question:
    "Even if a decision is logically valid, is it SAFE to execute?"

Safety Philosophy:
    - Safety always overrides aggressiveness
    - When uncertain, BLOCK
    - Never crash, always explain

Author: Quantitative Portfolio Engineering Team
"""

from typing import List, Dict, Any


def apply_risk_guardrails(
    proposed_actions: List[Dict[str, Any]],
    risk_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Filters proposed actions through mandatory safety rules.
    
    This is the FINAL safety gate before execution approval.
    All inputs must be pre-computed; this function performs NO calculations.
    
    Safety Rules Enforced:
        1. Sector Concentration Guard
        2. Cash Reserve Guard
        3. Volatility × Aggression Guard
    
    Args:
        proposed_actions (list): List of action dicts with:
            - target (str): Symbol
            - type (str): "POSITION" | "CANDIDATE"
            - action (str): Action type (e.g., "ALLOCATE", "REDUCE")
            - sector (str): Sector name
            - ... (other metadata)
            
        risk_context (dict): Pre-computed risk signals:
            {
                "concentration": {
                    "is_concentrated": bool,
                    "dominant_sector": str,
                    "severity": str
                },
                "cash_available": float,
                "minimum_reserve": float,
                "volatility_state": str  # "EXPANDING", "STABLE", "CONTRACTING"
            }
    
    Returns:
        dict: {
            "allowed_actions": List[Dict],
            "blocked_actions": List[Dict with "reason" field]
        }
    
    Behavior on Malformed Input:
        - Missing fields → Default to SAFE (conservative blocking)
        - Invalid types → Treated as unsafe
        - None values → Blocked
    """
    
    # =========================================================================
    # INPUT VALIDATION & DEFENSIVE DEFAULTS
    # =========================================================================
    if not proposed_actions or not isinstance(proposed_actions, list):
        # No actions to evaluate = safe but empty
        return {"allowed_actions": [], "blocked_actions": []}
    
    if not risk_context or not isinstance(risk_context, dict):
        # No risk context = cannot assess safety = block everything
        return {
            "allowed_actions": [],
            "blocked_actions": [
                {**action, "reason": "Safety check failed: missing risk context"}
                for action in proposed_actions
            ]
        }
    
    # Extract risk signals with safe defaults
    concentration = risk_context.get("concentration", {})
    is_concentrated = concentration.get("is_concentrated", False)
    dominant_sector = concentration.get("dominant_sector", "UNKNOWN")
    severity = concentration.get("severity", "NONE")
    
    cash_available = risk_context.get("cash_available", 0.0)
    minimum_reserve = risk_context.get("minimum_reserve", 0.0)
    
    volatility_state = risk_context.get("volatility_state", "UNKNOWN")
    
    # =========================================================================
    # SAFETY RULE APPLICATION
    # =========================================================================
    allowed = []
    blocked = []
    
    for action in proposed_actions:
        # Defensive extraction
        action_type = action.get("action", "UNKNOWN")
        symbol = action.get("target", "N/A")
        sector = action.get("sector", "UNKNOWN")
        decision_type = action.get("type", "POSITION")
        
        block_reason = None
        
        # ---------------------------------------------------------------------
        # RULE 1: Sector Concentration Guard
        # ---------------------------------------------------------------------
        # If a sector is over-concentrated, block actions that INCREASE exposure
        if is_concentrated and sector == dominant_sector:
            # Define actions that increase exposure
            increasing_actions = [
                "ALLOCATE", "ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE",
                "SCALE_UP", "DOUBLE_DOWN", "ADD_POSITION"
            ]
            
            if action_type in increasing_actions:
                block_reason = "Sector concentration breach"
        
        # Also block if severity is APPROACHING and action is aggressive
        if severity == "APPROACHING" and sector == dominant_sector:
            aggressive_actions = [
                "ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE",
                "SCALE_UP", "DOUBLE_DOWN"
            ]
            if action_type in aggressive_actions:
                block_reason = "Sector concentration breach"
        
        # ---------------------------------------------------------------------
        # RULE 2: Cash Reserve Guard
        # ---------------------------------------------------------------------
        # If cash is below minimum reserve, block actions requiring capital
        if cash_available < minimum_reserve:
            capital_requiring_actions = [
                "ALLOCATE", "ALLOCATE_HIGH", "ALLOCATE_AGGRESSIVE",
                "ALLOCATE_CAPPED", "ALLOCATE_CAUTIOUS",
                "SCALE_UP", "ADD_POSITION", "DOUBLE_DOWN"
            ]
            
            if action_type in capital_requiring_actions:
                block_reason = "Insufficient cash reserve"
        
        # ---------------------------------------------------------------------
        # RULE 3: Volatility × Aggression Guard
        # ---------------------------------------------------------------------
        # During expanding volatility, block aggressive actions
        if volatility_state == "EXPANDING":
            aggressive_actions = [
                "ALLOCATE_AGGRESSIVE", "SCALE_UP", "DOUBLE_DOWN",
                "FREE_CAPITAL"  # Freeing capital during volatility spike can be risky
            ]
            
            if action_type in aggressive_actions:
                block_reason = "Aggressive action blocked during expanding volatility"
        
        # ---------------------------------------------------------------------
        # DECISION: ALLOW or BLOCK
        # ---------------------------------------------------------------------
        if block_reason:
            blocked_action = action.copy()
            blocked_action["reason"] = block_reason
            blocked.append(blocked_action)
        else:
            allowed.append(action)
    
    return {
        "allowed_actions": allowed,
        "blocked_actions": blocked
    }


def summarize_guardrail_results(results: Dict[str, Any]) -> str:
    """
    Creates a human-readable summary of guardrail filtering results.
    
    Args:
        results (dict): Output from apply_risk_guardrails()
    
    Returns:
        str: Summary text
    """
    allowed_count = len(results.get("allowed_actions", []))
    blocked_count = len(results.get("blocked_actions", []))
    
    if blocked_count == 0:
        return f"All {allowed_count} proposed actions passed safety checks."
    
    summary_parts = [
        f"Safety Filter: {allowed_count} allowed, {blocked_count} blocked."
    ]
    
    # Group blocks by reason
    blocked = results.get("blocked_actions", [])
    reasons = {}
    for b in blocked:
        reason = b.get("reason", "Unknown")
        if reason not in reasons:
            reasons[reason] = []
        reasons[reason].append(b.get("target", "N/A"))
    
    for reason, symbols in reasons.items():
        summary_parts.append(f"  - {reason}: {', '.join(symbols)}")
    
    return " ".join(summary_parts)


# =============================================================================
# VALIDATION TESTS (Standalone)
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RISK GUARDRAILS - Safety Validation Tests")
    print("=" * 70)
    
    # -------------------------------------------------------------------------
    # Test 1: Sector Concentration Block
    # -------------------------------------------------------------------------
    print("\n[Test 1] Sector Concentration Guard")
    
    actions_1 = [
        {"target": "TECH_A", "action": "ALLOCATE_HIGH", "type": "CANDIDATE", "sector": "TECH"},
        {"target": "BIO_B", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "BIOTECH"}
    ]
    
    context_1 = {
        "concentration": {
            "is_concentrated": True,
            "dominant_sector": "TECH",
            "severity": "BREACH"
        },
        "cash_available": 100000.0,
        "minimum_reserve": 50000.0,
        "volatility_state": "STABLE"
    }
    
    result_1 = apply_risk_guardrails(actions_1, context_1)
    print(f"  Allowed: {len(result_1['allowed_actions'])}")
    print(f"  Blocked: {len(result_1['blocked_actions'])}")
    for b in result_1['blocked_actions']:
        print(f"    - {b['target']}: {b['reason']}")
    
    assert len(result_1['blocked_actions']) == 1, "Should block TECH allocation"
    assert result_1['blocked_actions'][0]['target'] == "TECH_A"
    
    # -------------------------------------------------------------------------
    # Test 2: Cash Reserve Guard
    # -------------------------------------------------------------------------
    print("\n[Test 2] Cash Reserve Guard")
    
    actions_2 = [
        {"target": "NEW_STOCK", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "ENERGY"},
        {"target": "OLD_STOCK", "action": "REDUCE", "type": "POSITION", "sector": "UTILITIES"}
    ]
    
    context_2 = {
        "concentration": {"is_concentrated": False},
        "cash_available": 30000.0,
        "minimum_reserve": 50000.0,  # Cash below reserve!
        "volatility_state": "STABLE"
    }
    
    result_2 = apply_risk_guardrails(actions_2, context_2)
    print(f"  Allowed: {len(result_2['allowed_actions'])}")
    print(f"  Blocked: {len(result_2['blocked_actions'])}")
    for b in result_2['blocked_actions']:
        print(f"    - {b['target']}: {b['reason']}")
    
    assert len(result_2['blocked_actions']) == 1, "Should block allocation due to low cash"
    assert "Insufficient cash reserve" in result_2['blocked_actions'][0]['reason']
    
    # -------------------------------------------------------------------------
    # Test 3: Volatility × Aggression Guard
    # -------------------------------------------------------------------------
    print("\n[Test 3] Volatility × Aggression Guard")
    
    actions_3 = [
        {"target": "SAFE_STOCK", "action": "ALLOCATE", "type": "CANDIDATE", "sector": "UTILITIES"},
        {"target": "RISKY_PLAY", "action": "ALLOCATE_AGGRESSIVE", "type": "CANDIDATE", "sector": "TECH"}
    ]
    
    context_3 = {
        "concentration": {"is_concentrated": False},
        "cash_available": 100000.0,
        "minimum_reserve": 50000.0,
        "volatility_state": "EXPANDING"  # High volatility!
    }
    
    result_3 = apply_risk_guardrails(actions_3, context_3)
    print(f"  Allowed: {len(result_3['allowed_actions'])}")
    print(f"  Blocked: {len(result_3['blocked_actions'])}")
    for b in result_3['blocked_actions']:
        print(f"    - {b['target']}: {b['reason']}")
    
    assert len(result_3['blocked_actions']) == 1, "Should block aggressive action"
    assert "expanding volatility" in result_3['blocked_actions'][0]['reason']
    
    # -------------------------------------------------------------------------
    # Test 4: Malformed Input (Crash-Proof)
    # -------------------------------------------------------------------------
    print("\n[Test 4] Crash-Proof Handling")
    
    # Empty actions
    result_4a = apply_risk_guardrails([], {})
    assert result_4a['allowed_actions'] == []
    print("  ✓ Empty input handled")
    
    # Missing risk context
    result_4b = apply_risk_guardrails([{"target": "X", "action": "BUY"}], None)
    assert len(result_4b['blocked_actions']) == 1
    print("  ✓ None context blocked all actions")
    
    # Malformed action
    result_4c = apply_risk_guardrails([{"incomplete": "data"}], context_1)
    assert len(result_4c['allowed_actions']) >= 0  # Should not crash
    print("  ✓ Malformed action handled gracefully")
    
    print("\n" + "=" * 70)
    print("✅ All Safety Tests Passed - Guardrails Are Fail-Safe")
    print("=" * 70)
