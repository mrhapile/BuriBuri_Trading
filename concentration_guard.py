"""
Sector Concentration Guard
==========================
A risk module that detects capital over-exposure to any single sector.

This module provides ADVISORY risk signals (not hard blocks) to prevent
portfolios from becoming dangerously concentrated — even when individual
positions appear diversified by symbol.

Core Principle:
    "If reallocating capital would cause the portfolio to behave like
    a single macro bet, the system must notice — even if individual
    trades look good."

Design:
    - Pure logic: No I/O, no logging, no side effects
    - Composable: Returns clean dicts usable by any downstream system
    - Defensive: Handles empty portfolios, missing sectors, zero capital
    - Configurable: Thresholds are parameters, not hardcoded

Integration Points:
    - Decision Resolver (to block or scale new allocations)
    - Portfolio Health Dashboard
    - LLM Explanation Layer (natural language "why")

Author: Quantitative Portfolio Engineering Team
"""

from typing import TypedDict, Optional


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class Position(TypedDict):
    """
    Represents a single open position in the portfolio.
    
    Attributes:
        symbol: Ticker or identifier for the asset
        sector: Sector classification (e.g., "TECH", "ENERGY", "FINANCE")
        capital_allocated: Absolute capital in this position (not percentage)
    """
    symbol: str
    sector: str
    capital_allocated: float


class ConcentrationWarning(TypedDict):
    """
    Risk assessment for sector concentration.
    
    Attributes:
        is_concentrated: True if any sector exceeds the soft limit
        dominant_sector: The sector with highest exposure (None if empty portfolio)
        exposure: The exposure fraction of the dominant sector (0.0 to 1.0)
        threshold: The soft limit threshold that was used
        severity: Risk level - "OK", "APPROACHING", or "SOFT_BREACH"
    """
    is_concentrated: bool
    dominant_sector: Optional[str]
    exposure: float
    threshold: float
    severity: str


class ConcentrationAnalysis(TypedDict):
    """
    Complete concentration analysis result.
    
    Attributes:
        exposure_map: Dict mapping sector names to exposure fractions (0.0 to 1.0)
        warning: ConcentrationWarning with risk assessment
    """
    exposure_map: dict[str, float]
    warning: ConcentrationWarning


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

DEFAULT_THRESHOLDS = {
    "soft_limit": 0.70,      # Above this triggers SOFT_BREACH
    "warning_limit": 0.60    # Above this triggers APPROACHING
}

# Sector label used when position has missing/empty sector field
UNKNOWN_SECTOR = "UNKNOWN"


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def compute_sector_exposure(
    positions: list[dict],
    total_capital: float
) -> dict[str, float]:
    """
    Compute the normalized exposure map for all sectors.
    
    This function aggregates capital by sector and returns the fraction
    of total portfolio capital allocated to each sector.
    
    Args:
        positions: List of position dictionaries, each with 'sector' and
                   'capital_allocated' fields
        total_capital: Total portfolio capital (used as denominator)
    
    Returns:
        Dictionary mapping sector names to exposure fractions (0.0 to 1.0).
        Values are rounded to 4 decimal places for stability.
        Empty portfolio returns empty dict.
    
    Edge Cases:
        - Empty positions list: Returns {}
        - Missing sector field: Position grouped under "UNKNOWN"
        - Zero/negative capital: Position contributes 0% exposure
        - total_capital <= 0: Returns {} (cannot compute fractions)
    
    Example:
        >>> compute_sector_exposure(
        ...     [{"sector": "TECH", "capital_allocated": 70000},
        ...      {"sector": "ENERGY", "capital_allocated": 30000}],
        ...     100000
        ... )
        {"TECH": 0.70, "ENERGY": 0.30}
    """
    # Guard: Cannot compute exposure with zero or negative total capital
    if total_capital <= 0:
        return {}
    
    # Guard: Empty portfolio has no exposure
    if not positions:
        return {}
    
    # Aggregate capital by sector
    sector_capital: dict[str, float] = {}
    
    for position in positions:
        # Extract sector, defaulting to UNKNOWN if missing or empty
        sector = position.get("sector", "").strip().upper()
        if not sector:
            sector = UNKNOWN_SECTOR
        
        # Extract capital, treating zero/negative as no contribution
        capital = position.get("capital_allocated", 0.0)
        if capital <= 0:
            continue
        
        # Accumulate capital for this sector
        sector_capital[sector] = sector_capital.get(sector, 0.0) + capital
    
    # Convert absolute capital to normalized fractions
    exposure_map: dict[str, float] = {}
    
    for sector, capital in sector_capital.items():
        fraction = capital / total_capital
        # Round to 4 decimal places for deterministic output
        exposure_map[sector] = round(fraction, 4)
    
    return exposure_map


def evaluate_concentration_risk(
    exposure_map: dict[str, float],
    thresholds: Optional[dict[str, float]] = None
) -> ConcentrationWarning:
    """
    Evaluate concentration risk based on sector exposures.
    
    Determines if the portfolio is over-concentrated by checking if any
    single sector exceeds the configured thresholds.
    
    Severity Levels:
        - OK: All sectors below warning_limit (default 60%)
        - APPROACHING: Highest sector between warning_limit and soft_limit
        - SOFT_BREACH: Highest sector exceeds soft_limit (default 70%)
    
    Args:
        exposure_map: Dict mapping sector names to exposure fractions
        thresholds: Optional dict with 'soft_limit' and 'warning_limit'.
                    Uses DEFAULT_THRESHOLDS if not provided.
    
    Returns:
        ConcentrationWarning with risk assessment.
    
    Edge Cases:
        - Empty exposure_map: Returns is_concentrated=False, severity="OK"
        - All exposures are 0: Returns is_concentrated=False, severity="OK"
    
    Example:
        >>> evaluate_concentration_risk({"TECH": 0.75, "ENERGY": 0.25})
        {
            "is_concentrated": True,
            "dominant_sector": "TECH",
            "exposure": 0.75,
            "threshold": 0.70,
            "severity": "SOFT_BREACH"
        }
    """
    # Use default thresholds if not provided
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    
    soft_limit = thresholds.get("soft_limit", 0.70)
    warning_limit = thresholds.get("warning_limit", 0.60)
    
    # Guard: Empty exposure map means no concentration risk
    if not exposure_map:
        return {
            "is_concentrated": False,
            "dominant_sector": None,
            "exposure": 0.0,
            "threshold": soft_limit,
            "severity": "OK"
        }
    
    # Find the sector with maximum exposure
    # Break ties alphabetically to ensure stability
    dominant_sector = max(exposure_map, key=lambda k: (exposure_map[k], k))
    max_exposure = exposure_map[dominant_sector]
    
    # Determine severity based on thresholds
    if max_exposure > soft_limit:
        severity = "SOFT_BREACH"
        is_concentrated = True
    elif max_exposure > warning_limit:
        severity = "APPROACHING"
        is_concentrated = False  # Not yet breached, just approaching
    else:
        severity = "OK"
        is_concentrated = False
    
    return {
        "is_concentrated": is_concentrated,
        "dominant_sector": dominant_sector,
        "exposure": max_exposure,
        "threshold": soft_limit,
        "severity": severity
    }


def analyze_portfolio_concentration(
    positions: list[dict],
    total_capital: float,
    thresholds: Optional[dict[str, float]] = None
) -> ConcentrationAnalysis:
    """
    Main API: Analyze portfolio for sector concentration risk.
    
    This is the primary entry point for the concentration guard module.
    It computes sector exposures and evaluates concentration risk in a
    single call, returning both the exposure map and warning flag.
    
    Args:
        positions: List of position dictionaries with 'symbol', 'sector',
                   and 'capital_allocated' fields
        total_capital: Total portfolio capital
        thresholds: Optional dict with 'soft_limit' and 'warning_limit'
    
    Returns:
        ConcentrationAnalysis containing:
            - exposure_map: Sector -> fraction mapping
            - warning: Risk assessment with severity
    
    Usage:
        >>> from concentration_guard import analyze_portfolio_concentration
        >>> result = analyze_portfolio_concentration(positions, 100000)
        >>> if result["warning"]["is_concentrated"]:
        ...     print(f"Warning: {result['warning']['dominant_sector']} "
        ...           f"at {result['warning']['exposure']:.0%}")
    """
    # Step 1: Compute normalized sector exposures
    exposure_map = compute_sector_exposure(positions, total_capital)
    
    # Step 2: Evaluate concentration risk
    warning = evaluate_concentration_risk(exposure_map, thresholds)
    
    return {
        "exposure_map": exposure_map,
        "warning": warning
    }


# =============================================================================
# VALIDATION EXAMPLES
# =============================================================================

if __name__ == "__main__":
    """
    Sanity anchors — not unit tests, but expected behavior documentation.
    Run this file directly to verify the module behaves as expected.
    """
    
    print("=" * 65)
    print("CONCENTRATION GUARD - Validation Examples")
    print("=" * 65)
    print()
    
    # -------------------------------------------------------------------------
    # Example A: Over-concentrated in TECH (SOFT_BREACH)
    # -------------------------------------------------------------------------
    print("Example A: Over-concentrated portfolio")
    print("-" * 40)
    
    positions_a = [
        {"symbol": "AAPL", "sector": "TECH", "capital_allocated": 40000},
        {"symbol": "MSFT", "sector": "TECH", "capital_allocated": 35000},
        {"symbol": "XOM", "sector": "ENERGY", "capital_allocated": 15000},
        {"symbol": "JPM", "sector": "FINANCE", "capital_allocated": 10000},
    ]
    total_a = 100000
    
    result_a = analyze_portfolio_concentration(positions_a, total_a)
    
    print(f"  Exposure Map: {result_a['exposure_map']}")
    print(f"  Expected:     {{'TECH': 0.75, 'ENERGY': 0.15, 'FINANCE': 0.10}}")
    print()
    print(f"  Concentrated: {result_a['warning']['is_concentrated']}")
    print(f"  Expected:     True")
    print(f"  Severity:     {result_a['warning']['severity']}")
    print(f"  Expected:     SOFT_BREACH")
    print()
    
    # -------------------------------------------------------------------------
    # Example B: Well-diversified (OK)
    # -------------------------------------------------------------------------
    print("Example B: Well-diversified portfolio")
    print("-" * 40)
    
    positions_b = [
        {"symbol": "AAPL", "sector": "TECH", "capital_allocated": 30000},
        {"symbol": "XOM", "sector": "ENERGY", "capital_allocated": 35000},
        {"symbol": "JPM", "sector": "FINANCE", "capital_allocated": 35000},
    ]
    total_b = 100000
    
    result_b = analyze_portfolio_concentration(positions_b, total_b)
    
    print(f"  Exposure Map: {result_b['exposure_map']}")
    print(f"  Expected:     {{'TECH': 0.30, 'ENERGY': 0.35, 'FINANCE': 0.35}}")
    print()
    print(f"  Concentrated: {result_b['warning']['is_concentrated']}")
    print(f"  Expected:     False")
    print(f"  Severity:     {result_b['warning']['severity']}")
    print(f"  Expected:     OK")
    print()
    
    # -------------------------------------------------------------------------
    # Example C: Approaching threshold (APPROACHING)
    # -------------------------------------------------------------------------
    print("Example C: Approaching threshold")
    print("-" * 40)
    
    positions_c = [
        {"symbol": "AAPL", "sector": "TECH", "capital_allocated": 65000},
        {"symbol": "XOM", "sector": "ENERGY", "capital_allocated": 35000},
    ]
    total_c = 100000
    
    result_c = analyze_portfolio_concentration(positions_c, total_c)
    
    print(f"  Exposure Map: {result_c['exposure_map']}")
    print(f"  Expected:     {{'TECH': 0.65, 'ENERGY': 0.35}}")
    print()
    print(f"  Concentrated: {result_c['warning']['is_concentrated']}")
    print(f"  Expected:     False")
    print(f"  Severity:     {result_c['warning']['severity']}")
    print(f"  Expected:     APPROACHING")
    print()
    
    # -------------------------------------------------------------------------
    # Example D: Edge case - Empty portfolio
    # -------------------------------------------------------------------------
    print("Example D: Empty portfolio (edge case)")
    print("-" * 40)
    
    result_d = analyze_portfolio_concentration([], 100000)
    
    print(f"  Exposure Map: {result_d['exposure_map']}")
    print(f"  Expected:     {{}}")
    print(f"  Severity:     {result_d['warning']['severity']}")
    print(f"  Expected:     OK")
    print()
    
    # -------------------------------------------------------------------------
    # Example E: Edge case - Missing sector labels
    # -------------------------------------------------------------------------
    print("Example E: Missing sector labels (edge case)")
    print("-" * 40)
    
    positions_e = [
        {"symbol": "AAPL", "sector": "TECH", "capital_allocated": 50000},
        {"symbol": "XYZ", "sector": "", "capital_allocated": 30000},
        {"symbol": "ABC", "capital_allocated": 20000},  # No sector key
    ]
    total_e = 100000
    
    result_e = analyze_portfolio_concentration(positions_e, total_e)
    
    print(f"  Exposure Map: {result_e['exposure_map']}")
    print(f"  Expected:     {{'TECH': 0.50, 'UNKNOWN': 0.50}}")
    print()
    
    print("=" * 65)
    print("Validation Complete")
    print("=" * 65)
