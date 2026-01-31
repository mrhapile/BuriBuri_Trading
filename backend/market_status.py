import os
import requests
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_market_status():
    """
    Fetches market status from Alpaca Clock API.
    
    Returns:
        dict: {
            "is_open": bool,
            "next_open": str (ISO),
            "next_close": str (ISO),
            "label": "OPEN" | "CLOSED",
            "timestamp": str (ISO)
        }
    """
    api_key = os.environ.get("ALPACA_API_KEY")
    secret_key = os.environ.get("ALPACA_SECRET_KEY")
    base_url = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    try:
        url = f"{base_url}/v2/clock"
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        is_open = data.get("is_open", False)
        
        return {
            "is_open": is_open,
            "next_open": data.get("next_open"),
            "next_close": data.get("next_close"),
            "label": "OPEN" if is_open else "CLOSED",
            "timestamp": data.get("timestamp")
        }
    except Exception as e:
        # Fallback if API fails (assume closed for safety or dev)
        print(f"⚠️ Market Status Check Failed: {e}")
        return {
            "is_open": False,
            "next_open": None,
            "next_close": None,
            "label": "CLOSED (Error)",
            "timestamp": datetime.now().isoformat()
        }
