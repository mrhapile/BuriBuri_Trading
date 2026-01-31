"""
demo_simulation.py

A simple runner to validate Phase 1 data sources.
Mocks data fetching for Candles, Portfolio, and News to ensure data contract compliance.
"""

import time
import json
from datetime import datetime

# =============================================================================
# MOCK DATA FETCHING FUNCTIONS (Simulating APIs/DBs)
# =============================================================================

# NOTE: These mocks will be replaced by Polygon, Alpaca, and RSS integrations in Phase 1 implementation.

def fetch_sector_candles(sector: str, limit: int = 5):
    """
    Simulates fetching OHLCV candles for a given sector.
    Returns a list of candle dictionaries adhering to the project data contracts.
    """
    print(f"[*] Fetching candles for sector: {sector}...")
    
    # Mock data generation
    base_price = 100.0 if sector == "TECH" else 50.0
    candles = []
    
    for i in range(limit):
        # Simulating time progression
        ts = f"2026-01-31T{10+i}:00:00Z"
        candles.append({
            "timestamp": ts,
            "open": base_price + i,
            "high": base_price + i + 1.0,
            "low": base_price + i - 0.5,
            "close": base_price + i + 0.2,
            "volume": 1000000 + (i * 5000)
        })
    
    return candles

def fetch_portfolio_snapshot():
    """
    Simulates fetching the current portfolio state.
    Returns a dictionary adhering to the project data contracts.
    """
    print("[*] Fetching portfolio snapshot...")
    
    return {
        "total_capital": 1000000.0,
        "used_capital": 850000.0,  # Note: Reserved usage
        "cash": 150000.0
    }

def fetch_sector_news(sector: str):
    """
    Simulates fetching news headlines for a sector.
    Returns a list of newsletter items adhering to the project data contracts.
    """
    print(f"[*] Fetching news for sector: {sector}...")
    
    # Mock news items
    if sector == "TECH":
        return [
            {
                "timestamp": "2026-01-31T09:15:00Z",
                "headline": "Tech Sector Rally Continues as AI Demand Soars",
                "source": "Bloomberg",
                "symbols": ["NVDA", "AMD", "MSFT"]
                # sentiment_score is optional/future, omitting here or adding mock
            },
            {
                "timestamp": "2026-01-31T11:00:00Z",
                "headline": "Analyst Warns of Potential Overvaluation in Chip Stocks",
                "source": "Reuters",
                "symbols": ["INTC", "QCOM"],
                "sentiment_score": -0.2
            }
        ]
    else:
        return [
            {
                "timestamp": "2026-01-31T08:30:00Z",
                "headline": f"Quiet trading day expected for {sector}",
                "source": "MarketWatch",
                "symbols": []
            }
        ]

# =============================================================================
# MAIN RUNNER
# =============================================================================

if __name__ == "__main__":
    print("============================================================")
    print("PHASE 1 DATA VALIDATION RUNNER")
    print("PHASE: 1 (DATA INGESTION ONLY)")
    print("============================================================")
    
    # 1. Validate Sector Candles
    try:
        tech_candles = fetch_sector_candles("TECH")
        print(f"  -> Successfully fetched {len(tech_candles)} candles.")
        print(f"  -> Sample: {json.dumps(tech_candles[0], indent=2)}")
    except Exception as e:
        print(f"  [!] Failed to fetch candles: {e}")
    print("-" * 60)

    # 2. Validate Portfolio Snapshot
    try:
        snapshot = fetch_portfolio_snapshot()
        print(f"  -> Successfully fetched snapshot.")
        print(f"  -> Total Capital: ${snapshot['total_capital']:,.2f}")
        print(f"  -> Cash: ${snapshot['cash']:,.2f}")
    except Exception as e:
        print(f"  [!] Failed to fetch portfolio snapshot: {e}")
    print("-" * 60)

    # 3. Validate Sector News
    try:
        tech_news = fetch_sector_news("TECH")
        print(f"  -> Successfully fetched {len(tech_news)} headlines.")
        print(f"  -> Sample: {json.dumps(tech_news[0], indent=2)}")
    except Exception as e:
        print(f"  [!] Failed to fetch news: {e}")
    
    print("============================================================")
    print("VALIDATION COMPLETE")
