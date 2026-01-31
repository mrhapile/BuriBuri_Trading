"""
market_mode.py

Handles automatic detection of market status and data mode selection.
Live vs Demo logic:
- LIVE: Market is OPEN (9:30 AM - 4:00 PM ET, Mon-Fri) AND Alpaca credentials exist.
- DEMO: Market is CLOSED OR Alpaca credentials missing.

This ensures the system never fails when the market is closed, but seamlessly 
upgrades to live data when available.
"""

import os
import datetime
from typing import Dict, Tuple

# Try to import zoneinfo or pytz for timezones
try:
    import zoneinfo
    eastern_tz = zoneinfo.ZoneInfo("America/New_York")
except ImportError:
    try:
        import pytz
        eastern_tz = pytz.timezone("America/New_York")
    except ImportError:
        # Fallback for systems without timezone lib (not ideal but functional)
        eastern_tz = None

def get_market_status() -> Dict[str, str]:
    """
    Determines if the US stock market is currently open.
    
    Returns:
        dict: {
            "status": "OPEN" | "CLOSED",
            "reason": Description of why (e.g., "After hours", "Weekend", "Market Open"),
            "timestamp": ISO timestamp
        }
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    # Check if Alpaca API is available to get authoritative clock
    api_key = os.environ.get("ALPACA_API_KEY")
    secret_key = os.environ.get("ALPACA_SECRET_KEY")
    
    if api_key and secret_key:
        try:
            import alpaca_trade_api as tradeapi
            base_url = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
            api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
            clock = api.get_clock()
            
            status = "OPEN" if clock.is_open else "CLOSED"
            reason = "Market is Open" if clock.is_open else "Market is Closed (Alpaca Clock)"
            
            return {
                "status": status,
                "reason": reason,
                "timestamp": now_utc.isoformat()
            }
        except Exception as e:
            # Fallback to local calculation if API fails
            pass

    # Local Fallback Calculation
    if eastern_tz:
        now_et = now_utc.astimezone(eastern_tz)
    else:
        # Rough adjustment if no TZ lib (UTC-5/4) is tricky, assume UTC-5 for safety or just valid hours
        now_et = now_utc - datetime.timedelta(hours=5) 

    # 1. Check Weekend
    if now_et.weekday() >= 5: # 5=Sat, 6=Sun
        return {
            "status": "CLOSED",
            "reason": "Weekend",
            "timestamp": now_utc.isoformat()
        }
        
    # 2. Check Hours (09:30 - 16:00 ET)
    current_time = now_et.time()
    market_open = datetime.time(9, 30)
    market_close = datetime.time(16, 0)
    
    if current_time < market_open:
        return {
            "status": "CLOSED",
            "reason": "Pre-market",
            "timestamp": now_utc.isoformat()
        }
    elif current_time > market_close:
        return {
            "status": "CLOSED",
            "reason": "After hours",
            "timestamp": now_utc.isoformat()
        }
        
    return {
        "status": "OPEN",
        "reason": "Market Open (Local Time)",
        "timestamp": now_utc.isoformat()
    }

def determine_execution_context() -> Dict[str, str]:
    """
    Decides the precise execution context.
    Differentiates between System Deployment Mode and actual Data Connectivity.
    
    Concepts:
    - system_mode:     PAPER (Advisory) vs DEMO (Profiles)
    - market_status:   OPEN vs CLOSED
    - data_feed_mode:  LIVE (Real-time) vs SYNTHETIC (Failover/Closed)
    """
    market_info = get_market_status()
    market_status = market_info["status"]
    
    # Check Credentials
    has_creds = bool(os.environ.get("ALPACA_API_KEY") and os.environ.get("ALPACA_SECRET_KEY"))
    
    # SYSTEM MODE: Deployment Intention
    # Defaults to PAPER if creds exist, else DEMO
    system_mode = "PAPER (Advisory)" if has_creds else "DEMO (Profiles)"
    
    # DATA FEED MODE: Actual Integrity
    if market_status == "OPEN" and has_creds:
        data_feed_mode = "LIVE"
        data_capability = "Alpaca + Polygon"
        description = "Real-time market data enabled."
    elif market_status == "OPEN" and not has_creds:
        data_feed_mode = "SYNTHETIC"
        data_capability = "Synthetic Generator"
        description = "Market is open but missing keys. Using synthetic data."
    else:
        # Market Closed
        data_feed_mode = "SYNTHETIC"
        data_capability = "Synthetic Generator"
        description = "Market Closed. Using synthetic data for validation."
        
    return {
        "system_mode": system_mode,
        "market_status": market_status,
        "data_feed_mode": data_feed_mode,
        "data_capability": data_capability,
        "reason": market_info["reason"],
        "description": description,
        "timestamp": market_info["timestamp"]
    }

if __name__ == "__main__":
    # Test
    mode, context = determine_data_mode()
    print(f"Detected Mode: {mode}")
    print(f"Context: {context}")
