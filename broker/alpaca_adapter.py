"""
broker/alpaca_adapter.py

READ-ONLY Alpaca paper trading adapter.
Fetches real portfolio data from Alpaca's paper trading API.

SECURITY:
    - API keys from environment variables ONLY
    - Paper trading URL ONLY (no live trading)
    - READ-ONLY endpoints ONLY (no orders)

Author: Quantitative Portfolio Engineering Team
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional if env vars set externally

import requests


class AlpacaAdapter:
    """
    READ-ONLY Alpaca paper trading adapter.
    
    Provides the same interface as MockAdapter but fetches real data
    from Alpaca's paper trading API.
    
    Environment Variables Required:
        ALPACA_API_KEY: Your paper trading API key
        ALPACA_SECRET_KEY: Your paper trading secret key
        ALPACA_BASE_URL: https://paper-api.alpaca.markets (optional)
    """
    
    # Allowed base URLs (paper only - no live trading)
    ALLOWED_URLS = [
        "https://paper-api.alpaca.markets",
        "https://data.alpaca.markets"
    ]
    
    def __init__(self):
        """
        Initialize the Alpaca adapter with credentials from environment.
        
        Raises:
            RuntimeError: If required environment variables are missing
        """
        self.api_key = os.environ.get("ALPACA_API_KEY")
        self.secret_key = os.environ.get("ALPACA_SECRET_KEY")
        self.base_url = os.environ.get(
            "ALPACA_BASE_URL", 
            "https://paper-api.alpaca.markets"
        )
        self.data_url = "https://data.alpaca.markets"
        
        # Validate credentials
        if not self.api_key:
            raise RuntimeError(
                "ALPACA_API_KEY environment variable not set. "
                "Copy .env.example to .env and add your paper trading credentials."
            )
        
        if not self.secret_key:
            raise RuntimeError(
                "ALPACA_SECRET_KEY environment variable not set. "
                "Copy .env.example to .env and add your paper trading credentials."
            )
        
        # Security: Ensure we're using paper trading only
        if "paper" not in self.base_url:
            raise RuntimeError(
                f"SECURITY ERROR: Only paper trading URLs allowed. "
                f"Got: {self.base_url}"
            )
        
        # Build headers
        self._headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json"
        }
        
        self._initialized = True
    
    def _request(self, endpoint: str, base: str = None) -> Dict[str, Any]:
        """
        Make authenticated GET request to Alpaca API.
        
        Args:
            endpoint: API endpoint path
            base: Base URL (defaults to account API)
            
        Returns:
            dict: JSON response
            
        Raises:
            RuntimeError: On API error
        """
        base_url = base or self.base_url
        url = f"{base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self._headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Alpaca API error: {e}")
    
    def get_portfolio(self) -> Dict[str, Any]:
        """
        Fetch portfolio state from Alpaca account.
        
        Returns:
            dict: {
                "total_capital": float,  # equity
                "cash": float
            }
        """
        account = self._request("/v2/account")
        
        return {
            "total_capital": float(account.get("equity", 0)),
            "cash": float(account.get("cash", 0)),
            "buying_power": float(account.get("buying_power", 0)),
            "risk_tolerance": "moderate"  # Default
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Fetch open positions from Alpaca.
        
        Returns:
            list: Position dicts matching internal schema:
                {
                    "symbol": str,
                    "sector": str,
                    "entry_price": float,
                    "current_price": float,
                    "atr": float,
                    "days_held": int,
                    "capital_allocated": float
                }
        """
        raw_positions = self._request("/v2/positions")
        
        if not raw_positions:
            return []
        
        positions = []
        for pos in raw_positions:
            symbol = pos.get("symbol", "UNKNOWN")
            
            # Calculate days held
            entry_time = pos.get("avg_entry_price_timestamp")
            days_held = 1
            if entry_time:
                try:
                    entry_date = datetime.fromisoformat(entry_time.replace("Z", "+00:00"))
                    days_held = max(1, (datetime.now(entry_date.tzinfo) - entry_date).days)
                except (ValueError, TypeError):
                    days_held = 1
            
            # Get ATR from recent candles
            try:
                candles = self.get_recent_candles(symbol, limit=14)
                atr = self._compute_simple_atr(candles)
            except Exception:
                atr = 1.0  # Fallback
            
            positions.append({
                "symbol": symbol,
                "sector": self._infer_sector(symbol),  # Simple inference
                "entry_price": float(pos.get("avg_entry_price", 0)),
                "current_price": float(pos.get("current_price", 0)),
                "atr": atr,
                "days_held": days_held,
                "capital_allocated": float(pos.get("market_value", 0)),
                "qty": float(pos.get("qty", 0)),
                "unrealized_pl": float(pos.get("unrealized_pl", 0))
            })
        
        return positions
    
    def get_recent_candles(self, symbol: str = "SPY", limit: int = 20, timeframe: str = "1Day") -> List[Dict[str, Any]]:
        """
        Fetch recent OHLCV bars for ATR calculation.
        
        Args:
            symbol: Stock symbol
            limit: Number of bars
            timeframe: '1Day', '1Hour', '1Min'
            
        Returns:
            list: Candle dicts with timestamp, high, low, close
        """
        # Calculate date range
        end = datetime.now()
        start = end - timedelta(days=limit + 5)  # Extra buffer for weekends
        
        endpoint = (
            f"/v2/stocks/{symbol}/bars"
            f"?timeframe={timeframe}"
            f"&start={start.strftime('%Y-%m-%d')}"
            f"&end={end.strftime('%Y-%m-%d')}"
            f"&limit={limit}"
        )
        
        try:
            response = self._request(endpoint, base=self.data_url)
            bars = response.get("bars", [])
            
            candles = []
            for bar in bars[-limit:]:  # Take most recent
                candles.append({
                    "timestamp": bar.get("t"),
                    "open": float(bar.get("o", 0)),
                    "high": float(bar.get("h", 0)),
                    "low": float(bar.get("l", 0)),
                    "close": float(bar.get("c", 0)),
                    "volume": int(bar.get("v", 0))
                })
            
            return candles
            
        except RuntimeError as e:
            # _request wraps HTTP errors in RuntimeError. Check string for 403.
            if "403" in str(e):
                print(f"[Alpaca] Note: Real-time market data access restricted (403). Trying Polygon.io fallback...")
                polygon_candles = self._fetch_polygon_fallback(symbol, limit)
                if polygon_candles:
                    print(f"[Alpaca] Success: Retrieved {len(polygon_candles)} candles from Polygon.io")
                    return polygon_candles
                
                print(f"[Alpaca] Warning: Polygon fallback failed or no key. Using synthetic fallback.")
                return []
            
            print(f"[Alpaca] Warning: Could not fetch candles for {symbol}: {e}")
            return []
        except Exception as e:
            print(f"[Alpaca] Error: Unexpected error fetching candles: {e}")
            return []
    
    def _fetch_polygon_fallback(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """
        Attempts to fetch candles from Polygon.io as a backup.
        """
        api_key = os.environ.get("POLYGON_API_KEY")
        if not api_key:
            return []
            
        # Calculate date range
        end = datetime.now()
        start = end - timedelta(days=limit + 5)
        
        # Polygon API
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
        params = {"adjusted": "true", "sort": "asc", "limit": limit, "apiKey": api_key}
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                return []
                
            data = response.json()
            results = data.get("results", [])
            
            candles = []
            for r in results:
                if all(k in r for k in ("t", "o", "h", "l", "c")):
                    candles.append({
                        "timestamp": r["t"], # Ms timestamp usually fine, or convert if needed
                        "open": float(r["o"]),
                        "high": float(r["h"]),
                        "low": float(r["l"]),
                        "close": float(r["c"]),
                        "volume": int(r.get("v", 0))
                    })
            return candles[-limit:]
            
        except Exception:
            return []

    def _compute_simple_atr(self, candles: List[Dict], period: int = 14) -> float:
        """
        Compute simple ATR from candles.
        
        Args:
            candles: List of OHLCV dicts
            period: ATR period
            
        Returns:
            float: Average True Range
        """
        if len(candles) < 2:
            return 1.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i].get("high", 0)
            low = candles[i].get("low", 0)
            prev_close = candles[i-1].get("close", 0)
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        if not true_ranges:
            return 1.0
        
        return sum(true_ranges[-period:]) / min(len(true_ranges), period)
    
    def _infer_sector(self, symbol: str) -> str:
        """
        Simple sector inference from symbol.
        In production, use a proper sector lookup.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            str: Inferred sector
        """
        # Basic symbol-to-sector mapping
        tech_symbols = {"AAPL", "MSFT", "GOOGL", "GOOG", "NVDA", "AMD", "INTC", "META", "AMZN", "TSLA"}
        finance_symbols = {"JPM", "BAC", "GS", "MS", "WFC", "C"}
        healthcare_symbols = {"JNJ", "PFE", "UNH", "MRK", "ABBV"}
        
        sym_upper = symbol.upper()
        
        if sym_upper in tech_symbols:
            return "TECH"
        elif sym_upper in finance_symbols:
            return "FINANCE"
        elif sym_upper in healthcare_symbols:
            return "HEALTHCARE"
        else:
            return "OTHER"
    
    def get_candidates(self) -> List[Dict[str, Any]]:
        """
        Returns empty candidates (Alpaca doesn't provide trade ideas).
        Use mock or external source for candidates.
        
        Returns:
            list: Empty list
        """
        return []
    
    def get_sector_heatmap(self) -> Dict[str, int]:
        """
        Returns default sector heatmap.
        In production, fetch from market data source.
        
        Returns:
            dict: {sector: heat_score}
        """
        return {
            "TECH": 75,
            "FINANCE": 60,
            "HEALTHCARE": 65,
            "OTHER": 50
        }
    
    def get_headlines(self) -> List[str]:
        """
        Returns empty headlines (requires separate news API).
        
        Returns:
            list: Empty list
        """
        return []


# Standalone validation
if __name__ == "__main__":
    print("=" * 60)
    print("ALPACA ADAPTER - Validation")
    print("=" * 60)
    
    try:
        adapter = AlpacaAdapter()
        print("✅ Adapter initialized successfully")
        
        # Test portfolio
        portfolio = adapter.get_portfolio()
        print(f"\n[Portfolio]")
        print(f"  Total Capital: ${portfolio['total_capital']:,.2f}")
        print(f"  Cash: ${portfolio['cash']:,.2f}")
        
        # Test positions
        positions = adapter.get_positions()
        print(f"\n[Positions] {len(positions)} open positions:")
        for p in positions:
            print(f"  - {p['symbol']}: ${p['capital_allocated']:,.2f} ({p['sector']})")
        
        # Test candles
        candles = adapter.get_recent_candles("SPY", 5)
        print(f"\n[Candles] {len(candles)} SPY bars fetched")
        if candles:
            print(f"  Latest close: ${candles[-1]['close']:.2f}")
        
        print("\n" + "=" * 60)
        print("✅ All Alpaca API tests passed")
        print("=" * 60)
        
    except RuntimeError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTo fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your Alpaca paper trading credentials")
        print("  3. Run this script again")
