"""
broker/mock_adapter.py

Mock data adapter for development and testing.
Provides the same interface as AlpacaAdapter but with static test data.

This is the DEFAULT data source.
"""

from typing import List, Dict, Any


class MockAdapter:
    """
    Mock broker adapter for testing and development.
    Returns static data matching the internal schema.
    """
    
    def __init__(self):
        """Initialize mock adapter (no credentials needed)."""
        self._initialized = True
    
    def get_portfolio(self) -> Dict[str, Any]:
        """
        Returns mock portfolio state.
        
        Returns:
            dict: {
                "total_capital": float,
                "cash": float
            }
        """
        return {
            "total_capital": 1_000_000.0,
            "cash": 45_000.0,  # Low cash to trigger constraints
            "risk_tolerance": "moderate"
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Returns mock positions with varied health states.
        
        Returns:
            list: Position dicts matching internal schema
        """
        return [
            # 1. Healthy Tech Leader (Keep)
            {
                "symbol": "NVDA", 
                "sector": "TECH",
                "entry_price": 400.0, 
                "current_price": 500.0, 
                "atr": 10.0, 
                "days_held": 15, 
                "capital_allocated": 300_000.0
            },
            # 2. Stagnant Utility (Candidate for Exit)
            {
                "symbol": "SLOW_UTIL", 
                "sector": "UTILITIES", 
                "entry_price": 50.0, 
                "current_price": 50.5, 
                "atr": 0.5, 
                "days_held": 45,
                "capital_allocated": 150_000.0
            },
            # 3. Risky Tech Speculation
            {
                "symbol": "SPEC_TECH", 
                "sector": "TECH", 
                "entry_price": 100.0, 
                "current_price": 95.0, 
                "atr": 5.0, 
                "days_held": 5, 
                "capital_allocated": 250_000.0
            }
        ]
    
    def get_recent_candles(self, symbol: str = "SPY", limit: int = 20, timeframe: str = "1Day") -> List[Dict[str, Any]]:
        """
        Returns mock OHLCV candles for ATR calculation.
        
        Args:
            symbol: Stock symbol (ignored in mock)
            limit: Number of candles
            timeframe: Timeframe (ignored in mock)
            limit: Number of candles
            
        Returns:
            list: Candle dicts with high, low, close
        """
        # Generate synthetic candles with realistic volatility
        candles = []
        base_price = 100.0
        
        for i in range(limit):
            high = base_price + i + 2
            low = base_price + i - 1
            close = base_price + i + 0.5
            
            candles.append({
                "timestamp": f"2026-01-31T10:{i:02d}:00Z",
                "open": base_price + i,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1000000 + i * 10000
            })
        
        return candles
    
    def get_candidates(self) -> List[Dict[str, Any]]:
        """
        Returns mock trade candidates.
        
        Returns:
            list: Candidate dicts
        """
        return [
            {
                "symbol": "NEW_BIO", 
                "sector": "BIOTECH", 
                "projected_efficiency": 85.0
            },
            {
                "symbol": "MORE_TECH", 
                "sector": "TECH", 
                "projected_efficiency": 95.0
            }
        ]
    
    def get_sector_heatmap(self) -> Dict[str, int]:
        """
        Returns mock sector heat scores.
        
        Returns:
            dict: {sector: heat_score}
        """
        return {
            "TECH": 80,
            "BIOTECH": 70,
            "UTILITIES": 30
        }
    
    def get_headlines(self) -> List[str]:
        """
        Returns mock news headlines.
        
        Returns:
            list: Headline strings
        """
        return [
            "Tech sector shows resilience despite rate hike fears",
            "AI demand continues to outpace supply in hardware markets",
            "Utility sector stagnates as bond yields rise"
        ]


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("MOCK ADAPTER - Validation")
    print("=" * 60)
    
    adapter = MockAdapter()
    
    portfolio = adapter.get_portfolio()
    print(f"\n[Portfolio] Capital: ${portfolio['total_capital']:,.0f}, Cash: ${portfolio['cash']:,.0f}")
    
    positions = adapter.get_positions()
    print(f"\n[Positions] {len(positions)} positions:")
    for p in positions:
        print(f"  - {p['symbol']}: ${p['capital_allocated']:,.0f}")
    
    candles = adapter.get_recent_candles("SPY", 5)
    print(f"\n[Candles] {len(candles)} bars fetched")
    
    print("\n✅ Mock adapter working correctly")
