"""
Opportunity Scanner - Phase 1
=============================
Market data ingestion module for the Technology sector.

This module contains ONLY data fetching logic.
- Fetches 15-minute OHLC candles from Polygon API
- Returns clean, normalized data
- Handles all failure modes gracefully

Phase Boundary:
    Phase 1 (THIS FILE) → Market data ingestion ONLY
    Phase 2 (opportunity_logic.py) → Opportunity evaluation logic
    Phase 3 (decision_engine.py) → Portfolio decisions & actions

IMPORTANT:
    This module must NOT contain any portfolio analysis, candidate
    comparison, or decision logic. Those belong in Phase 2/3.

Author: Quantitative Portfolio Engineering Team
"""

import os
import requests
import logging
import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_tech_sector_candles(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetches 15-minute OHLC candles for the Technology sector ETF (XLK)
    using Polygon's Aggregates API.

    This function is designed to be fail-safe and deterministic.
    
    Args:
        limit (int): Approximate number of most recent candles to return.
                     Defaults to 50.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing:
            - open (float)
            - high (float)
            - low (float)
            - close (float)
            - timestamp (str: ISO-8601 UTC)
            
        Returns an empty list [] on any error or failure.
        The list is sorted in ascending order (oldest -> newest).
        
    Error Handling:
        - Missing API key: Logs error, returns []
        - Network failure: Logs error, returns []
        - Invalid response: Logs error, returns []
        - Malformed data: Skips record, continues processing
    """
    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        logger.error("POLYGON_API_KEY environment variable is not set.")
        return []

    ticker = "XLK"
    multiplier = 15
    timespan = "minute"
    
    # Calculate date range
    # We request a generous buffer (last 5 days) to ensure we get enough 15-min candles
    # even over weekends or holidays.
    end_date = datetime.datetime.now(datetime.timezone.utc)
    start_date = end_date - datetime.timedelta(days=5)

    from_str = start_date.strftime("%Y-%m-%d")
    to_str = end_date.strftime("%Y-%m-%d")

    # Construct URL
    # Polygon API Format: /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_str}/{to_str}"
    
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 5000,  # Request max allowed to ensure we capture the tail
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Polygon API failed with status {response.status_code}: {response.text}")
            return []
            
        data = response.json()
        
        # Defensive check for list results
        results = data.get("results", [])
        if not isinstance(results, list) or not results:
            logger.warning(f"Polygon API returned no results for {ticker}")
            return []

        parsed_candles = []
        for r in results:
            # Defensive check for required fields
            # 'o' = Open, 'h' = High, 'l' = Low, 'c' = Close, 't' = Timestamp (ms)
            if not all(k in r for k in ("o", "h", "l", "c", "t")):
                continue
                
            try:
                # Convert timestamp (ms) to ISO UTC string
                ts_ms = r["t"]
                # Enforce float conversion for prices
                candle = {
                    "open": float(r["o"]),
                    "high": float(r["h"]),
                    "low": float(r["l"]),
                    "close": float(r["c"]),
                    "timestamp": datetime.datetime.fromtimestamp(
                        ts_ms / 1000.0, tz=datetime.timezone.utc
                    ).isoformat()
                }
                parsed_candles.append(candle)
            except (ValueError, TypeError) as e:
                # Skip individual malformed records but keep processing valid ones
                logger.warning(f"Skipping malformed candle data: {r} - Error: {e}")
                continue
        
        # Ensure sorting: Oldest -> Newest
        parsed_candles.sort(key=lambda x: x["timestamp"])

        # Return the most recent 'limit' candles
        # If we have fewer than limit, return all we have
        return parsed_candles[-limit:]

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching Polygon data for {ticker}: {e}")
        return []
    except ValueError as e:
        logger.error(f"JSON decoding failed for {ticker}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_tech_sector_candles: {e}")
        return []


# =============================================================================
# VALIDATION (Phase 1 Only - Market Data Ingestion)
# =============================================================================
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("OPPORTUNITY SCANNER - Phase 1 Validation")
    print("=" * 60)
    print("\nThis module handles ONLY market data ingestion.")
    print("For opportunity logic, see: opportunity_logic.py")
    print()
    
    print("[Test] Fetching XLK 15-minute candles...")
    candles = fetch_tech_sector_candles(limit=5)
    
    if candles:
        print(f"✅ Success: Fetched {len(candles)} candles.")
        print("\nLatest 2 candles:")
        print(json.dumps(candles[-2:], indent=2))
    else:
        print("❌ Result: [] (Check POLYGON_API_KEY or network)")
    
    print("\n" + "=" * 60)
    print("Phase 1 Validation Complete")
    print("=" * 60)
