"""
demo/trend_overlays.py

Trend overlays for modifying market signals in demos.
These allow demonstrating adaptive intelligence by simulating
different market conditions WITHOUT changing portfolio composition.

OVERLAYS:
    - TECH_COOLING: Tech sector weakening, Energy rising
    - RISK_ON: High confidence, low volatility
    - VOLATILITY_SHOCK: Expanding volatility, defensive posture

Usage:
    DEMO_TREND=TECH_COOLING python3 full_system_demo.py

Author: Quantitative Portfolio Engineering Team
"""

from typing import Dict, Any, Optional


# =============================================================================
# TREND OVERLAY DEFINITIONS
# =============================================================================

TREND_OVERLAYS = {
    
    "TECH_COOLING": {
        "description": "Tech sector losing momentum, Energy gaining",
        "volatility_state": "STABLE",
        "confidence_modifier": -10,      # Lower overall confidence
        "sector_adjustments": {
            "TECH": -25,      # Cool down tech
            "ENERGY": +20,    # Heat up energy
            "FINANCE": +5
        },
        "news_bias": -10  # Slightly negative sentiment
    },
    
    "RISK_ON": {
        "description": "Strong risk appetite, bullish market conditions",
        "volatility_state": "CONTRACTING",
        "confidence_modifier": +15,
        "sector_adjustments": {
            "TECH": +10,
            "FINANCE": +10,
            "BIOTECH": +15
        },
        "news_bias": +20  # Positive sentiment
    },
    
    "VOLATILITY_SHOCK": {
        "description": "Sudden volatility spike, defensive posture",
        "volatility_state": "EXPANDING",
        "confidence_modifier": -25,
        "sector_adjustments": {
            "TECH": -20,
            "FINANCE": -15,
            "UTILITIES": +10,    # Safe haven
            "HEALTHCARE": +5
        },
        "news_bias": -25  # Fear sentiment
    },
    
    "NEUTRAL": {
        "description": "No overlay - use default signals",
        "volatility_state": None,  # Use computed
        "confidence_modifier": 0,
        "sector_adjustments": {},
        "news_bias": 0
    }
}


# =============================================================================
# PUBLIC API
# =============================================================================

def get_available_overlays() -> list:
    """Get list of available trend overlay names."""
    return list(TREND_OVERLAYS.keys())


def get_overlay(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a trend overlay by name.
    
    Args:
        name: Overlay name (case-insensitive)
        
    Returns:
        Overlay dict or None if not found
    """
    return TREND_OVERLAYS.get(name.upper())


def get_overlay_description(name: str) -> str:
    """Get human-readable description of an overlay."""
    overlay = get_overlay(name)
    if overlay:
        return overlay.get("description", "No description")
    return "Unknown overlay"


def apply_overlay_to_volatility(base_state: str, overlay_name: str) -> str:
    """
    Apply trend overlay to volatility state.
    
    Args:
        base_state: Computed volatility state
        overlay_name: Trend overlay name
        
    Returns:
        Modified volatility state
    """
    overlay = get_overlay(overlay_name)
    if not overlay or not overlay.get("volatility_state"):
        return base_state
    return overlay["volatility_state"]


def apply_overlay_to_confidence(base_confidence: int, overlay_name: str) -> int:
    """
    Apply trend overlay to sector confidence.
    
    Args:
        base_confidence: Computed confidence (0-100)
        overlay_name: Trend overlay name
        
    Returns:
        Modified confidence (clamped 0-100)
    """
    overlay = get_overlay(overlay_name)
    if not overlay:
        return base_confidence
    
    modifier = overlay.get("confidence_modifier", 0)
    return max(0, min(100, base_confidence + modifier))


def apply_overlay_to_news(base_score: int, overlay_name: str) -> int:
    """
    Apply trend overlay to news sentiment.
    
    Args:
        base_score: Computed news score (0-100)
        overlay_name: Trend overlay name
        
    Returns:
        Modified score (clamped 0-100)
    """
    overlay = get_overlay(overlay_name)
    if not overlay:
        return base_score
    
    bias = overlay.get("news_bias", 0)
    return max(0, min(100, base_score + bias))


def apply_overlay_to_heatmap(base_heatmap: Dict[str, int], overlay_name: str) -> Dict[str, int]:
    """
    Apply trend overlay to sector heatmap.
    
    Args:
        base_heatmap: Sector heat scores
        overlay_name: Trend overlay name
        
    Returns:
        Modified heatmap (values clamped 0-100)
    """
    overlay = get_overlay(overlay_name)
    if not overlay:
        return base_heatmap
    
    adjustments = overlay.get("sector_adjustments", {})
    result = base_heatmap.copy()
    
    for sector, adjustment in adjustments.items():
        if sector in result:
            result[sector] = max(0, min(100, result[sector] + adjustment))
        else:
            result[sector] = max(0, min(100, 50 + adjustment))  # Default 50 if new
    
    return result


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TREND OVERLAYS - Validation")
    print("=" * 60)
    
    for name in get_available_overlays():
        overlay = get_overlay(name)
        print(f"\n[{name}]")
        print(f"  Description: {get_overlay_description(name)}")
        print(f"  Volatility Override: {overlay.get('volatility_state', 'None')}")
        print(f"  Confidence Modifier: {overlay.get('confidence_modifier', 0):+d}")
        print(f"  News Bias: {overlay.get('news_bias', 0):+d}")
        
        adjustments = overlay.get("sector_adjustments", {})
        if adjustments:
            print(f"  Sector Adjustments:")
            for sector, adj in adjustments.items():
                print(f"    - {sector}: {adj:+d}")
    
    print("\n" + "=" * 60)
    print("✅ All overlays valid")
    print("=" * 60)
