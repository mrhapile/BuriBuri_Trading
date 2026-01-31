"""
scenarios.py

Pure data source for Behavioral Demo Scenarios.
Zero logic. Zero dependencies.

Defines exact inputs to force specific agent behaviors:
1. Refusal (Safety > Profit)
2. Inaction (Noise Filtering)
3. Defense (Volatility Response)
4. Efficiency (Capital Rotation)
"""

SCENARIOS = {
    "crash_reflex": {
        "label": "🚨 The Crash Reflex",
        "header_emoji": "🚨",
        "description": "Rapid volatility spike forces capital preservation",
        "badges": ["Safety Dominance", "Volatility Override", "Capital Preservation"],
        "override_inputs": {
            "volatility_state": "EXPANDING",
            "news_score": 85,
            "sector_confidence": 30,
            "positions": [
                {
                    "symbol": "NVDA", "sector": "TECH", "entry_price": 400.0, "current_price": 580.0,
                     "atr": 15.0, "days_held": 20, "capital_allocated": 150_000.0
                },
                {
                    "symbol": "AMD", "sector": "TECH", "entry_price": 140.0, "current_price": 123.0,
                    "atr": 5.0, "days_held": 10, "capital_allocated": 100_000.0
                }
            ],
            "candidates": [
                {"symbol": "TSLA", "sector": "TECH", "projected_efficiency": 95.0}
            ]
        }
    },
    
    "concentration_guard": {
        "label": "🛡️ The Concentration Guard",
        "header_emoji": "🛡️",
        "description": "Refuses perfect trade due to risk exposure limits",
        "badges": ["Refusal is Intelligence", "Structural Limits", "Safety > Profit"],
        "override_inputs": {
            "volatility_state": "CONTRACTING",
            "news_score": 75,
            "sector_confidence": 80,
            "positions": [
                {"symbol": "GOOGL", "sector": "TECH", "entry_price": 100, "current_price": 110, "atr": 2, "days_held": 10, "capital_allocated": 250_000},
                {"symbol": "MSFT", "sector": "TECH", "entry_price": 300, "current_price": 310, "atr": 5, "days_held": 10, "capital_allocated": 250_000},
                {"symbol": "NVDA", "sector": "TECH", "entry_price": 400, "current_price": 450, "atr": 8, "days_held": 10, "capital_allocated": 250_000}
            ],
            "candidates": [
                {"symbol": "AAPL", "sector": "TECH", "projected_efficiency": 99.0}
            ]
        }
    },

    "disciplined_observer": {
        "label": "👀 The Disciplined Observer",
        "header_emoji": "👀",
        "description": "Recognizes market noise and chooses inaction",
        "badges": ["Inaction is Decision", "Noise Filtering", "Patience"],
        "override_inputs": {
            "volatility_state": "STABLE",
            "news_score": 50,
            "sector_confidence": 45,
            "positions": [
                {"symbol": "JPM", "sector": "FINANCE", "entry_price": 150, "current_price": 153, "atr": 2, "days_held": 30, "capital_allocated": 200_000}
            ],
            "candidates": [
                {"symbol": "COIN", "sector": "FINANCE", "projected_efficiency": 62.0},
                {"symbol": "XOM", "sector": "ENERGY", "projected_efficiency": 58.0}
            ]
        }
    },

    "dead_capital": {
        "label": "♻️ The Dead Capital Rotator",
        "header_emoji": "♻️",
        "description": "Identifies stagnant money and redeploys it",
        "badges": ["Capital Efficiency", "Opportunity Cost", "Active Management"],
        "override_inputs": {
            "volatility_state": "CONTRACTING",
            "news_score": 60,
            "sector_confidence": 75,
            "positions": [
                {"symbol": "T", "sector": "TELECOM", "entry_price": 20.0, "current_price": 20.1, "atr": 0.2, "days_held": 60, "capital_allocated": 100_000}
            ],
            "candidates": [
                {"symbol": "LILLY", "sector": "HEALTH", "projected_efficiency": 88.0}
            ]
        }
    },

    "greedy_trap": {
        "label": "🪤 The Greedy Trap",
        "header_emoji": "🪤",
        "description": "High news sentiment vs. Expanding volatility",
        "badges": ["Skepticism", "Signal Conflict", "Anti-FOMO"],
        "override_inputs": {
            "volatility_state": "EXPANDING",
            "news_score": 90,
            "sector_confidence": 40,
            "positions": [],
            "candidates": [
                {"symbol": "MEME", "sector": "TECH", "projected_efficiency": 85.0}
            ]
        }
    }
}

def get_scenario(scenario_id):
    """Safe accessor with default fallback"""
    return SCENARIOS.get(scenario_id, {})
