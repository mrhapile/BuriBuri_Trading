"""
tests/test_historical_mode.py

Integration test for Market CLOSED (Historical) mode.
Verifies API behavior when market is closed.
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

class TestHistoricalMode(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    @patch("data_router.get_market_status")
    def test_market_closed_behavior(self, mock_get_status):
        # 1. Simulate Market CLOSED
        mock_get_status.return_value = {
            "is_open": False,
            "label": "CLOSED",
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # 2. Reset Router to ensure clean state
        self.app.post("/reset")
        
        # 3. Check Status
        resp = self.app.get("/status")
        data = resp.get_json()
        
        self.assertEqual(data["market_status"], "CLOSED")
        self.assertEqual(data["data_mode"], "HISTORICAL")
        self.assertIn("Historical", data["data_source"])
        self.assertTrue(data["controls_enabled"]["symbol_selector"])
        
        # 4. Set Symbol (Should be allowed)
        resp = self.app.post("/set-symbol", json={"symbol": "QQQ"})
        data = resp.get_json()
        self.assertEqual(data["selected_symbol"], "QQQ")
        
        # 5. Set Time Range (Should be allowed)
        resp = self.app.post("/set-time-range", json={"time_range": "1M"})
        data = resp.get_json()
        self.assertEqual(data["selected_time_range"], "1M")
        
        # 6. Run Analysis
        # Mocking the runner to avoid full computation, but we want to verify routing.
        # Ideally we let it run if it's fast enough. Historical mode is fast.
        # But let's verify inputs to the runner if possible. 
        # For this test, we run it end-to-end.
        
        resp = self.app.get("/run?symbol=QQQ&time_range=1M")
        engine_result = resp.get_json()
        
        self.assertEqual(engine_result["data_mode"], "HISTORICAL")
        self.assertEqual(engine_result["market_status"]["label"], "CLOSED")
        self.assertEqual(engine_result["routing_config"]["selected_symbol"], "QQQ")
        
        print("\n✅ Historical Mode verified successfully")

if __name__ == "__main__":
    unittest.main()
