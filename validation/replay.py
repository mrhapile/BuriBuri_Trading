"""
validation/replay.py

The Time Machine. 
Iterates through historical data day-by-day, reconstructing the market context
as it would have appeared at that moment, and feeding it to the Decision Engine.
"""

from datetime import datetime, timedelta
import pandas as pd
import decision_engine
from validation.data_manager import HistoricalDataManager
from validation.metrics import ValidationMetrics
from market_mode import determine_execution_context

class HistoricalReplayEngine:
    def __init__(self, start_date: str, end_date: str, symbols: list):
        self.start_date = start_date
        self.end_date = end_date
        self.symbols = symbols
        self.data_manager = HistoricalDataManager()
        self.metrics = ValidationMetrics()
        
        # State
        self.market_data = {} # {symbol: [records]}
        self.portfolio = {
            "total_capital": 100000.0,
            "cash": 100000.0,
            "risk_tolerance": "moderate"
        }
        self.positions = [] # Track simulated positions if we wanted to (keeping simple for now)
        
    def preload_data(self):
        """Fetches all necessary data before starting replay."""
        for sym in self.symbols:
            # Add lookback buffer (e.g. 30 days) for indicators
            buffer_start = (datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(days=60)).strftime("%Y-%m-%d")
            data = self.data_manager.fetch_history(sym, buffer_start, self.end_date)
            
            # Index by date string for O(1) lookup
            # But simpler: just keep list and slice
            self.market_data[sym] = sorted(data, key=lambda x: x['timestamp'])
            
    def run(self):
        """Executes the replay loop."""
        print(f"\n⏳ Starting Replay ({self.start_date} to {self.end_date})...")
        
        current_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 1. Build Context for THIS day
            market_context = self._build_daily_context(current_date)
            
            if not market_context["candles"]:
                # Market closed or no data
                current_date += timedelta(days=1)
                continue
                
            # 2. Run Engine (Unmodified)
            # Create a "Replay" execution context
            exec_ctx = {
                "system_mode": "VALIDATION (Replay)",
                "market_status": "OPEN", # Assuming data exists = open
                "data_feed_mode": "HISTORICAL",
                "data_capability": "Alpaca History (Cached)"
            }
            
            # Mock candidate scan (since we don't have universe data for candidates easily)
            candidates = self._generate_mock_candidates(current_date)
            
            try:
                report = decision_engine.run_decision_engine(
                    portfolio_state=self.portfolio,
                    positions=self.positions,
                    sector_heatmap={"TECH": 50, "SPY": 50}, # Neutral baseline
                    candidates=candidates,
                    market_context=market_context,
                    execution_context=exec_ctx
                )
                
                # 3. Track Metrics
                self.metrics.record_cycle(report["decisions"], self.portfolio)
                
                # Optional: Visualization / Progress
                if self.metrics.total_cycles % 10 == 0:
                    print(f"   Now: {date_str} | Decisions: {len(report['decisions'])} | Posture: {report['market_posture']['market_posture']}")
                    
            except Exception as e:
                print(f"❌ Error on {date_str}: {e}")
                
            current_date += timedelta(days=1)
            
        print("✅ Replay Complete.")
        self.metrics.print_summary()

    def _build_daily_context(self, current_dt: datetime) -> dict:
        """Slices the historical data to simulate 'now'."""
        # Use SPY as the primary market proxy
        ref_symbol = "SPY" if "SPY" in self.symbols else self.symbols[0]
        data = self.market_data.get(ref_symbol, [])
        
        # Find index of current date
        # This linear search is slow for huge datasets but fine for demo scale
        cutoff_str = current_dt.strftime("%Y-%m-%d")
        
        # Get last 20 candles UP TO current_dt
        # Simple string comparison works for ISO dates
        past_candles = [c for c in data if c['timestamp'] < cutoff_str]
        
        if not past_candles: 
            return {"candles": [], "news": []}
            
        # Check if "today" exists (market open) - actually we are simulating decision BEFORE open or AFTER close?
        # Let's assume we run AFTER close of 'past' candles
        
        recent_20 = past_candles[-20:]
        
        return {
            "candles": recent_20,
            "news": [] # No news archive yet, engine handles empty news gracefully (50/50 score)
        }

    def _generate_mock_candidates(self, current_dt: datetime) -> list:
        """Generates dummy candidates so the engine has something to chew on."""
        return [
            {"symbol": "TEST_A", "sector": "TECH", "projected_efficiency": 75.0},
            {"symbol": "TEST_B", "sector": "BIO", "projected_efficiency": 60.0}
        ]

if __name__ == "__main__":
    # Self-test
    engine = HistoricalReplayEngine("2023-01-01", "2023-02-01", ["SPY"])
    engine.preload_data()
    engine.run()
