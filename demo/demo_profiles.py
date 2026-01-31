"""
demo/demo_profiles.py

Demo Portfolio Profiles for showcasing system intelligence.
These profiles allow the system to demonstrate full decision-making
capabilities when markets are closed or no real positions exist.

PROFILES:
    1. BALANCED_TECH - Healthy portfolio, mostly HOLD actions
    2. OVERCONCENTRATED_TECH - Triggers concentration guards (DEFAULT)
    3. LOSING_PORTFOLIO - Triggers RISK_OFF defensive posture

Author: Quantitative Portfolio Engineering Team
"""

from typing import Dict, List, Any, Tuple


# =============================================================================
# PROFILE DEFINITIONS
# =============================================================================

PROFILES = {
    
    # -------------------------------------------------------------------------
    # PROFILE 1: BALANCED_TECH
    # A healthy, well-diversified tech-focused portfolio
    # Expected: Mostly HOLD/MAINTAIN actions, no major alerts
    # -------------------------------------------------------------------------
    "BALANCED_TECH": {
        "description": "Healthy tech portfolio with good diversification",
        "portfolio_state": {
            "total_capital": 500_000.0,
            "cash": 75_000.0,  # 15% liquid
            "risk_tolerance": "moderate"
        },
        "positions": [
            {
                "symbol": "NVDA",
                "sector": "TECH",
                "entry_price": 450.0,
                "current_price": 520.0,  # +15.5% gain
                "atr": 12.0,
                "days_held": 45,
                "capital_allocated": 130_000.0  # 26%
            },
            {
                "symbol": "AAPL",
                "sector": "TECH",
                "entry_price": 175.0,
                "current_price": 185.0,  # +5.7% gain
                "atr": 3.5,
                "days_held": 30,
                "capital_allocated": 95_000.0  # 19%
            },
            {
                "symbol": "JPM",
                "sector": "FINANCE",
                "entry_price": 180.0,
                "current_price": 195.0,  # +8.3% gain
                "atr": 4.0,
                "days_held": 60,
                "capital_allocated": 100_000.0  # 20%
            },
            {
                "symbol": "JNJ",
                "sector": "HEALTHCARE",
                "entry_price": 155.0,
                "current_price": 160.0,  # +3.2% gain
                "atr": 2.0,
                "days_held": 90,
                "capital_allocated": 100_000.0  # 20%
            }
        ],
        "sector_heatmap": {
            "TECH": 80,
            "FINANCE": 70,
            "HEALTHCARE": 65,
            "UTILITIES": 40
        },
        "candidates": [
            {"symbol": "MSFT", "sector": "TECH", "projected_efficiency": 75.0},
            {"symbol": "UNH", "sector": "HEALTHCARE", "projected_efficiency": 70.0}
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROFILE 2: OVERCONCENTRATED_TECH (DEFAULT FOR JUDGES)
    # Heavy tech concentration that triggers safety guards
    # Expected: TRIM_RISK, BLOCK_RISK, concentration warnings
    # -------------------------------------------------------------------------
    "OVERCONCENTRATED_TECH": {
        "description": "Over-concentrated tech portfolio triggering risk guards",
        "portfolio_state": {
            "total_capital": 1_000_000.0,
            "cash": 35_000.0,  # Low cash - triggers cash reserve guard
            "risk_tolerance": "aggressive"
        },
        "positions": [
            # Strong performer but huge allocation
            {
                "symbol": "NVDA",
                "sector": "TECH",
                "entry_price": 400.0,
                "current_price": 580.0,  # +45% gain
                "atr": 15.0,
                "days_held": 120,
                "capital_allocated": 350_000.0  # 35% - massive single position
            },
            # Moderate performer
            {
                "symbol": "AAPL",
                "sector": "TECH",
                "entry_price": 170.0,
                "current_price": 188.0,  # +10.6% gain
                "atr": 4.0,
                "days_held": 60,
                "capital_allocated": 200_000.0  # 20%
            },
            # Weak performer in same sector
            {
                "symbol": "AMD",
                "sector": "TECH",
                "entry_price": 150.0,
                "current_price": 142.0,  # -5.3% loss
                "atr": 8.0,
                "days_held": 25,
                "capital_allocated": 150_000.0  # 15%
            },
            # Stagnant tech position
            {
                "symbol": "INTC",
                "sector": "TECH",
                "entry_price": 45.0,
                "current_price": 46.0,  # +2.2% stagnant
                "atr": 1.5,
                "days_held": 90,
                "capital_allocated": 120_000.0  # 12%
            },
            # Small non-tech diversifier
            {
                "symbol": "XOM",
                "sector": "ENERGY",
                "entry_price": 105.0,
                "current_price": 112.0,  # +6.7% gain
                "atr": 2.5,
                "days_held": 40,
                "capital_allocated": 145_000.0  # 14.5%
            }
        ],
        # Total TECH = 35% + 20% + 15% + 12% = 82% CONCENTRATION!
        "sector_heatmap": {
            "TECH": 90,  # Hot sector
            "ENERGY": 60,
            "FINANCE": 55,
            "BIOTECH": 75
        },
        "candidates": [
            {"symbol": "META", "sector": "TECH", "projected_efficiency": 95.0},  # Should be BLOCKED
            {"symbol": "MRNA", "sector": "BIOTECH", "projected_efficiency": 80.0},
            {"symbol": "GS", "sector": "FINANCE", "projected_efficiency": 65.0}
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROFILE 3: LOSING_PORTFOLIO
    # Multiple losing positions triggering defensive posture
    # Expected: RISK_OFF, REDUCE actions, blocked inflows
    # -------------------------------------------------------------------------
    "LOSING_PORTFOLIO": {
        "description": "Portfolio with multiple losses triggering defensive mode",
        "portfolio_state": {
            "total_capital": 750_000.0,
            "cash": 50_000.0,
            "risk_tolerance": "conservative"
        },
        "positions": [
            # Major loser
            {
                "symbol": "TSLA",
                "sector": "TECH",
                "entry_price": 280.0,
                "current_price": 195.0,  # -30.4% loss
                "atr": 12.0,
                "days_held": 45,
                "capital_allocated": 180_000.0
            },
            # Another loser
            {
                "symbol": "COIN",
                "sector": "FINANCE",
                "entry_price": 250.0,
                "current_price": 175.0,  # -30% loss
                "atr": 18.0,
                "days_held": 30,
                "capital_allocated": 150_000.0
            },
            # Slight loser
            {
                "symbol": "PYPL",
                "sector": "TECH",
                "entry_price": 75.0,
                "current_price": 65.0,  # -13.3% loss
                "atr": 4.0,
                "days_held": 60,
                "capital_allocated": 120_000.0
            },
            # Stagnant underwater
            {
                "symbol": "DIS",
                "sector": "MEDIA",
                "entry_price": 100.0,
                "current_price": 92.0,  # -8% loss
                "atr": 3.0,
                "days_held": 120,
                "capital_allocated": 130_000.0
            },
            # Only winner (small)
            {
                "symbol": "COST",
                "sector": "RETAIL",
                "entry_price": 700.0,
                "current_price": 750.0,  # +7.1% gain
                "atr": 10.0,
                "days_held": 90,
                "capital_allocated": 120_000.0
            }
        ],
        # 4 losers vs 1 winner -> Should trigger RISK_OFF
        "sector_heatmap": {
            "TECH": 40,  # Cold sector
            "FINANCE": 35,
            "MEDIA": 30,
            "RETAIL": 65
        },
        "candidates": [
            {"symbol": "AMZN", "sector": "TECH", "projected_efficiency": 70.0},
            {"symbol": "WMT", "sector": "RETAIL", "projected_efficiency": 60.0}
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROFILE 4: ROTATION_SCENARIO
    # TECH weakening, ENERGY rising - forces capital reallocation
    # Expected: FREE_CAPITAL from weak TECH, ALLOCATE to rising ENERGY
    # -------------------------------------------------------------------------
    "ROTATION_SCENARIO": {
        "description": "Sector rotation: TECH cooling, ENERGY rising - forces reallocation",
        "portfolio_state": {
            "total_capital": 800_000.0,
            "cash": 120_000.0,  # 15% available for rotation
            "risk_tolerance": "moderate"
        },
        "positions": [
            # TECH - weakening
            {
                "symbol": "NVDA",
                "sector": "TECH",
                "entry_price": 500.0,
                "current_price": 480.0,  # -4% declining
                "atr": 15.0,
                "days_held": 60,
                "capital_allocated": 200_000.0
            },
            {
                "symbol": "META",
                "sector": "TECH",
                "entry_price": 400.0,
                "current_price": 385.0,  # -3.75% declining
                "atr": 12.0,
                "days_held": 45,
                "capital_allocated": 150_000.0
            },
            # ENERGY - rising strongly
            {
                "symbol": "XOM",
                "sector": "ENERGY",
                "entry_price": 100.0,
                "current_price": 118.0,  # +18% gain
                "atr": 3.0,
                "days_held": 90,
                "capital_allocated": 120_000.0
            },
            {
                "symbol": "CVX",
                "sector": "ENERGY",
                "entry_price": 150.0,
                "current_price": 172.0,  # +14.7% gain
                "atr": 4.0,
                "days_held": 75,
                "capital_allocated": 110_000.0
            },
            # Steady FINANCE position
            {
                "symbol": "JPM",
                "sector": "FINANCE",
                "entry_price": 175.0,
                "current_price": 185.0,  # +5.7% gain
                "atr": 3.5,
                "days_held": 120,
                "capital_allocated": 100_000.0
            }
        ],
        "sector_heatmap": {
            "TECH": 45,      # Cooling down
            "ENERGY": 90,    # HOT - rising
            "FINANCE": 65,
            "HEALTHCARE": 55
        },
        "candidates": [
            {"symbol": "OXY", "sector": "ENERGY", "projected_efficiency": 88.0},  # Hot sector
            {"symbol": "AAPL", "sector": "TECH", "projected_efficiency": 72.0},   # Cool sector
            {"symbol": "SLB", "sector": "ENERGY", "projected_efficiency": 82.0}
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROFILE 5: CASH_HEAVY
    # High idle cash, waiting for opportunities
    # Expected: Shows "why we did NOT deploy capital" (waiting for signals)
    # -------------------------------------------------------------------------
    "CASH_HEAVY": {
        "description": "High idle cash (40%) - demonstrates capital discipline",
        "portfolio_state": {
            "total_capital": 500_000.0,
            "cash": 200_000.0,  # 40% cash - unusually high
            "risk_tolerance": "conservative"
        },
        "positions": [
            # Only 3 small, stable positions
            {
                "symbol": "AAPL",
                "sector": "TECH",
                "entry_price": 175.0,
                "current_price": 180.0,  # +2.9% modest gain
                "atr": 3.0,
                "days_held": 180,
                "capital_allocated": 100_000.0
            },
            {
                "symbol": "JNJ",
                "sector": "HEALTHCARE",
                "entry_price": 158.0,
                "current_price": 162.0,  # +2.5% modest gain
                "atr": 2.0,
                "days_held": 200,
                "capital_allocated": 100_000.0
            },
            {
                "symbol": "PG",
                "sector": "CONSUMER",
                "entry_price": 155.0,
                "current_price": 160.0,  # +3.2% modest gain
                "atr": 1.8,
                "days_held": 150,
                "capital_allocated": 100_000.0
            }
        ],
        # All sectors mediocre - no compelling opportunities
        "sector_heatmap": {
            "TECH": 50,       # Neutral
            "HEALTHCARE": 55,
            "CONSUMER": 52,
            "FINANCE": 48,
            "ENERGY": 45
        },
        "candidates": [
            {"symbol": "MSFT", "sector": "TECH", "projected_efficiency": 55.0},     # Mediocre
            {"symbol": "BAC", "sector": "FINANCE", "projected_efficiency": 48.0},   # Below threshold
            {"symbol": "XOM", "sector": "ENERGY", "projected_efficiency": 52.0}
        ]
    }
}


# =============================================================================
# PUBLIC API
# =============================================================================

def get_available_profiles() -> List[str]:
    """Returns list of available demo profile names."""
    return list(PROFILES.keys())


def load_demo_profile(profile_name: str = "OVERCONCENTRATED_TECH") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Load a demo portfolio profile.
    
    Args:
        profile_name: Name of profile to load (default: OVERCONCENTRATED_TECH)
        
    Returns:
        Tuple of (portfolio_state, positions)
        
    Raises:
        ValueError: If profile not found
    """
    if profile_name not in PROFILES:
        available = ", ".join(PROFILES.keys())
        raise ValueError(f"Unknown profile '{profile_name}'. Available: {available}")
    
    profile = PROFILES[profile_name]
    return profile["portfolio_state"], profile["positions"]


def get_demo_candidates(profile_name: str = "OVERCONCENTRATED_TECH") -> List[Dict[str, Any]]:
    """Get trade candidates for a demo profile."""
    if profile_name not in PROFILES:
        return []
    return PROFILES[profile_name].get("candidates", [])


def get_demo_heatmap(profile_name: str = "OVERCONCENTRATED_TECH") -> Dict[str, int]:
    """Get sector heatmap for a demo profile."""
    if profile_name not in PROFILES:
        return {"TECH": 70, "FINANCE": 60}
    return PROFILES[profile_name].get("sector_heatmap", {})


def get_profile_description(profile_name: str) -> str:
    """Get human-readable description of a profile."""
    if profile_name not in PROFILES:
        return "Unknown profile"
    return PROFILES[profile_name].get("description", "No description")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DEMO PORTFOLIO PROFILES - Validation")
    print("=" * 70)
    
    for name in get_available_profiles():
        print(f"\n[Profile: {name}]")
        print(f"  Description: {get_profile_description(name)}")
        
        portfolio, positions = load_demo_profile(name)
        print(f"  Capital: ${portfolio['total_capital']:,.0f}")
        print(f"  Cash: ${portfolio['cash']:,.0f}")
        print(f"  Positions: {len(positions)}")
        
        # Calculate sector concentration
        sectors = {}
        for p in positions:
            sector = p["sector"]
            sectors[sector] = sectors.get(sector, 0) + p["capital_allocated"]
        
        total = portfolio["total_capital"]
        print(f"  Sector Breakdown:")
        for sector, alloc in sorted(sectors.items(), key=lambda x: -x[1]):
            pct = (alloc / total) * 100
            print(f"    - {sector}: {pct:.1f}%")
        
        candidates = get_demo_candidates(name)
        print(f"  Candidates: {len(candidates)}")
    
    print("\n" + "=" * 70)
    print("✅ All profiles valid")
    print("=" * 70)
