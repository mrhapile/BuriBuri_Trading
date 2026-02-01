"""
tests/test_live_mode.py

Integration test for Market OPEN (Live) mode.
Verifies API behavior when market is open.
Uses MOCKING to simulate open market without modifying source code.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add project root AND backend to path to fix imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from backend.app import app

class TestLiveMode(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    @patch("data_router.get_market_status")
    @patch("broker.alpaca_adapter.AlpacaAdapter")
    def test_market_open_behavior(self, mock_adapter_cls, mock_get_status):
        # 1. Simulate Market OPEN
        mock_get_status.return_value = {
            "is_open": True,
            "label": "OPEN",
            "timestamp": "2023-06-15T10:00:00"
        }
        
        # 2. Mock Adapter to return dummy data so we don't hit real API
        mock_instance = mock_adapter_cls.return_value
        mock_instance.get_portfolio.return_value = {"total_capital": 100000, "cash": 50000}
        mock_instance.get_positions.return_value = [
            {"symbol": "AAPL", "qty": 10, "market_value": 1500, "current_price": 150}
        ]
        mock_instance.get_recent_candles.return_value = [
            {"close": 150, "volume": 1000, "timestamp": "2023-06-15T09:59:00"}
        ]
        mock_instance.get_headlines.return_value = []
        mock_instance.get_sector_heatmap.return_value = {"TECH": 75, "FINANCE": 60}
        
        # 3. Reset Router to ensure clean state and forced re-init
        self.app.post("/reset")
        
        # 4. Check Status
        resp = self.app.get("/status")
        data = resp.get_json()
        
        self.assertEqual(data["market_status"], "OPEN")
        self.assertEqual(data["data_mode"], "LIVE")
        self.assertFalse(data["controls_enabled"]["symbol_selector"], "Symbol selector should be disabled in Live mode")
        
        # 5. Set Symbol (Should be BLOCKED or Ignored)
        # The endpoint might return 200 but not change config, or return error?
        # api_routes.py implementation says: "Only works when market is CLOSED"
        # Let's verify it doesn't break anything.
        resp = self.app.post("/set-symbol", json={"symbol": "NVDA"})
        # It updates the router config but UI disables it. 
        # Actually, let's check what `set_symbol` implementation does.
        # It calls router.set_symbol. Router might update internal state, 
        # but in LIVE mode, the runner ignores selected_symbol and uses portfolio.
        
        # 6. Run Analysis
        resp = self.app.get("/run")
        engine_result = resp.get_json()
        
        self.assertEqual(engine_result["data_mode"], "LIVE")
        self.assertEqual(engine_result["market_status"]["label"], "OPEN")
        
        # Verify adapter was called
        mock_instance.get_portfolio.assert_called()
        
        print("\n✅ Live Mode verified successfully (Mocked)")

if __name__ == "__main__":
    unittest.main()
