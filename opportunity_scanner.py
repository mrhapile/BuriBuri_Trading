import os
import requests
import logging
import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_tech_sector_candles(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetches 15-minute OHLC candles for the Technology sector ETF (XLK)
    using Polygon's Aggregates API.

    This module is designed to be fail-safe and deterministic.
    
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
        "limit": 5000, # Request max allowed to ensure we capture the tail
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

def scan_for_opportunities(positions: list, candidates: list, threshold: float = 15.0) -> dict:
    """
    Scans for relative efficiency opportunities by comparing the portfolio's 
    weakest link against the market's strongest candidate.
    
    Logic:
    1. Identify the 'Weakest Link': Position with the lowest Vitals Score.
    2. Identify the 'Top Prospect': Candidate with the highest Projected Efficiency.
    3. Compare: If (Top Prospect Score - Weakest Link Score) > Threshold, 
       then a significantly better opportunity exists.
       
    Args:
        positions (list): List of current positions with 'vitals_score'.
        candidates (list): List of candidate dicts with 'projected_efficiency'.
        threshold (float): Point difference required to consider the switch "significant".
                           Defaults to 15.0 to account for switching costs/friction.
                           
    Returns:
        dict: Report containing comparison metrics and boolean flag.
    """
    
    # ---------------------------------------------------------
    # 1. Analyze Current Portfolio (Find the Floor)
    # ---------------------------------------------------------
    if not positions:
        weakest_position = None
        min_vitals = 999.0 # Arbitrary high start
    else:
        # Find position with minimum vitals_score
        weakest_position = min(positions, key=lambda x: x.get("vitals_score", 0))
        min_vitals = float(weakest_position.get("vitals_score", 0))

    # For reporting purposes, we might also want the best held, 
    # but the swap logic relies on the worst.
    best_held_score = 0.0
    if positions:
        best_held_score = max([p.get("vitals_score", 0) for p in positions])

    # ---------------------------------------------------------
    # 2. Analyze External Opportunities (Find the Ceiling)
    # ---------------------------------------------------------
    if not candidates:
        top_candidate = None
        max_external_score = 0.0
    else:
        # Find candidate with maximum projected efficiency
        top_candidate = max(candidates, key=lambda x: x.get("projected_efficiency", 0))
        max_external_score = float(top_candidate.get("projected_efficiency", 0))

    # ---------------------------------------------------------
    # 3. Compute Relative Efficiency Gap
    # ---------------------------------------------------------
    # The gap that justifies a trade
    efficiency_gap = max_external_score - min_vitals
    
    better_opportunity_exists = False
    details = "No significant upgrade available."
    
    if positions and candidates:
        if efficiency_gap > threshold:
            better_opportunity_exists = True
            confidence = "HIGH" if efficiency_gap > (threshold * 2) else "MEDIUM"
            details = (
                f"Upgrade Opportunity: Swap {weakest_position['symbol']} ({min_vitals}) "
                f"for {top_candidate['symbol']} ({max_external_score}). "
                f"Efficiency Gain: +{round(efficiency_gap, 1)}"
            )
        else:
            confidence = "LOW"
            details = (
                f"Hold: Best external gap (+{round(efficiency_gap, 1)}) "
                f"does not exceed threshold ({threshold})."
            )
    elif not positions and candidates:
        # If we have no positions, any candidate is an opportunity (technically)
        better_opportunity_exists = True
        confidence = "HIGH"
        details = "Portfolio is empty. External opportunities available."
    else:
        confidence = "N/A" # No candidates or other edge cases

    # ---------------------------------------------------------
    # 4. Construct Output
    # ---------------------------------------------------------
    return {
        "weakest_held_symbol": weakest_position['symbol'] if weakest_position else "N/A",
        "weakest_held_score": min_vitals if positions else 0.0,
        "best_external_symbol": top_candidate['symbol'] if top_candidate else "N/A",
        "best_external_score": max_external_score,
        "efficiency_gap": round(efficiency_gap, 1) if positions else max_external_score,
        "better_opportunity_exists": better_opportunity_exists,
        "confidence": confidence,
        "summary": details,
        # Including best held for context, though logic focuses on weakest
        "best_held_efficiency_context": best_held_score 
    }

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    import json
    
    print("--- Opportunity Scanner Verification ---")
    
    # 1. Verify Sector Candle Fetching
    print("\n[Test] Fetching XLK Candles...")
    # NOTE: Set POLYGON_API_KEY env var to test this for real
    candles = fetch_tech_sector_candles(limit=5)
    
    if candles:
        print(f"Success: Fetched {len(candles)} candles.")
        print("Last 2 candles:")
        print(json.dumps(candles[-2:], indent=2))
    else:
        print("Result: [] (Expected if no API key or network error)")

    # 2. Verify Logic (Existing Mock Data)
    print("\n[Test] running Logic Scan...")
    current_portfolio = [
        {"symbol": "LAGGING_CO", "vitals_score": 35.0}, 
        {"symbol": "STABLE_INC", "vitals_score": 60.0},
        {"symbol": "STAR_CORP", "vitals_score": 92.0}
    ]
    
    market_candidates = [
        {"symbol": "NEW_TECH", "projected_efficiency": 85.0}, 
        {"symbol": "HOT_BIO", "projected_efficiency": 70.0},
        {"symbol": "DULL_UTIL", "projected_efficiency": 40.0}
    ]
    
    report = scan_for_opportunities(current_portfolio, market_candidates, threshold=15.0)
    print(json.dumps(report, indent=4))
