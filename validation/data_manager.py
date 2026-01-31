"""
validation/data_manager.py

Handles fetching and caching of historical market data for validation replays.
Prioritizes local cache to save API calls and enable offline testing.
"""

import os
import json
import pandas as pd
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = "historical_cache"

class HistoricalDataManager:
    def __init__(self):
        self.api_key = os.environ.get("ALPACA_API_KEY")
        self.secret_key = os.environ.get("ALPACA_SECRET_KEY")
        self.base_url = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        
        self.client = None
        if self.api_key and self.secret_key:
            try:
                self.client = tradeapi.REST(self.api_key, self.secret_key, self.base_url, api_version='v2')
            except Exception as e:
                print(f"⚠️ [DataManager] Alpaca client init failed: {e}")
                
    def _get_cache_path(self, symbol: str, start_date: str, end_date: str) -> str:
        """Generates a consistent filename for the requested data slice."""
        safe_start = start_date.split("T")[0]
        safe_end = end_date.split("T")[0]
        return os.path.join(CACHE_DIR, f"{symbol}_{safe_start}_{safe_end}.json")

    def fetch_history(self, symbol: str, start_date: str, end_date: str) -> list:
        """
        Fetches historical bars.
        1. Checks local disk cache.
        2. If missing, calls Alpaca API.
        3. Saves to cache.
        
        Returns: List of dicts (OHLCV + timestamp)
        """
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
            
        cache_path = self._get_cache_path(symbol, start_date, end_date)
        
        # 1. Try Cache
        if os.path.exists(cache_path):
            print(f"📦 [Cache] Loading {symbol} data from {cache_path}...")
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"⚠️ [Cache] Read failed: {e}. Re-fetching.")

        # 2. Fetch from Source
        if not self.client:
            print("❌ [DataManager] Online fetch required but no API client.")
            return []
            
        print(f"🌐 [API] Fetching {symbol} from Alpaca ({start_date} -> {end_date})...")
        try:
            # Fetch bars
            bars = self.client.get_bars(
                symbol,
                tradeapi.TimeFrame.Day,
                start=start_date,
                end=end_date,
                adjustment='raw'
            ).df
            
            if bars.empty:
                print(f"⚠️ [API] No data returned for {symbol}")
                return []
                
            # Convert to list of dicts for consistency
            bars.reset_index(inplace=True)
            # Standardize timestamp
            bars['timestamp'] = bars['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            records = bars.to_dict('records')
            
            # 3. Save Cache
            with open(cache_path, "w") as f:
                json.dump(records, f, indent=2)
            print(f"💾 [Cache] Saved {len(records)} bars to {cache_path}")
            
            return records
            
        except Exception as e:
            print(f"❌ [API] Fetch error: {e}")
            return []

if __name__ == "__main__":
    # Self-test
    dm = HistoricalDataManager()
    # Test with a known range
    data = dm.fetch_history("SPY", "2023-01-01", "2023-01-31")
    print(f"Test Result: Retrieved {len(data)} records.")
