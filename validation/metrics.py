"""
validation/metrics.py

Tracks safety and stability metrics during historical replay.
Focuses on proving underfitting (safety) rather than maximizing returns.
"""

from collections import Counter

class ValidationMetrics:
    def __init__(self):
        self.total_cycles = 0
        self.inaction_count = 0
        self.decision_history = {} # {symbol: [actions...]}
        self.flips = 0 # Number of times decision flipped (Buy->Sell or Sell->Buy)
        self.capital_history = [] # Track simulated equity curve (simplistic)
        self.drawdown_max = 0.0
        
    def record_cycle(self, decisions: list, portfolio_state: dict):
        """
        Ingests the output of one decision cycle.
        """
        self.total_cycles += 1
        
        # 1. Action Tracking
        has_action = False
        for d in decisions:
            symbol = d["target"]
            action = d["action"]
            
            # Init history if needed
            if symbol not in self.decision_history:
                self.decision_history[symbol] = []
            
            # Detect Action vs Inaction
            if action not in ["MAINTAIN", "HOLD", "IGNORE", "WATCHLIST"]:
                has_action = True
                
            # Detect Flips (Churn) based on previous action for this symbol
            if self.decision_history[symbol]:
                prev = self.decision_history[symbol][-1]
                if self._is_flip(prev, action):
                    self.flips += 1
            
            self.decision_history[symbol].append(action)
            
        if not has_action:
            self.inaction_count += 1
            
        # 2. Capital Tracking (Mock Equity Curve for now, or real if engine updates portfolio)
        # For validation, we might just track the "Cash" stability if system is advisory
        self.capital_history.append(portfolio_state.get("total_capital", 100000))
        
    def _is_flip(self, prev: str, curr: str) -> bool:
        """
        Returns True if action changed drastically (e.g., BUY -> SELL).
        Ignores subtle shifts (HOLD -> MAINTAIN).
        """
        bullish = ["ALLOCATE", "ALLOCATE_HIGH", "BUY"]
        bearish = ["REDUCE", "TRIM_RISK", "SELL", "FREE_CAPITAL"]
        
        was_bull = any(b in prev for b in bullish)
        is_bear = any(b in curr for b in bearish)
        
        was_bear = any(b in prev for b in bearish)
        is_bull = any(b in curr for b in bullish)
        
        return (was_bull and is_bear) or (was_bear and is_bull)

    def get_report(self) -> dict:
        """Returns the final scorecard."""
        inaction_rate = (self.inaction_count / self.total_cycles * 100) if self.total_cycles > 0 else 0
        
        return {
            "total_decision_cycles": self.total_cycles,
            "inaction_rate_pct": round(inaction_rate, 1),
            "decision_churn_count": self.flips,
            "churn_per_cycle": round(self.flips / self.total_cycles, 3) if self.total_cycles > 0 else 0
        }

    def print_summary(self):
        r = self.get_report()
        print("\n" + "="*60)
        print("🛡️ VALIDATION METRICS (SAFETY CHECK)")
        print("="*60)
        print(f"Cycles Processed:      {r['total_decision_cycles']}")
        print(f"Inaction Ratio:        {r['inaction_rate_pct']}% (Target: >70% in noise)")
        print(f"Decision Churn (Flip): {r['decision_churn_count']} events")
        print(f"Stability Score:       {1.0 - r['churn_per_cycle']:.2f} (1.0 = Perfect Stability)")
        print("="*60)
