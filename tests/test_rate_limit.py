
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from backend.app import app
from backend import rate_limit

class TestRateLimiting(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Reset limiter storage (in-memory) if possible
        # For this test we assume fresh process or unique IP handling if multiple tests existed

    
    @patch.dict(os.environ, {"ENV": "production"})
    def test_run_limit_production(self):
        # /run limit is 5 per minute in production
        # We need to ensure we are "in production" according to the limit function
        
        # NOTE: Flask-Limiter limits are often evaluated at request time.
        # However, decorators might bind at import time?? 
        # No, dynamic limits (callables) are evaluated at request time.
        
        # Clear storage (Skipped to avoid AttributeError, assuming fresh run)
        # rate_limit.limiter.reset()

        # Making 5 requests should be fine
        for i in range(5):
             # Mock the run_market_aware_analysis to avoid real computation
             with patch('backend.api_routes.run_market_aware_analysis') as mock_run:
                 mock_run.return_value = {"analysis": {}}
                 with patch('backend.api_routes.load_agent_memory') as mock_mem:
                    mock_mem.return_value = {}
                    with patch('backend.api_routes.save_agent_memory'):
                         resp = self.app.get('/run')
                         self.assertEqual(resp.status_code, 200, f"Request {i+1} failed")
        
        # 6th request should fail
        with patch('backend.api_routes.run_market_aware_analysis') as mock_run:
             with patch('backend.api_routes.load_agent_memory') as mock_mem:
                 mock_mem.return_value = {}
                 resp = self.app.get('/run')
                 # If rate limiting is working and ENV is correctly mocked to production, this should be 429
                 # Note: app.py initializes limiter with ENV present at startup. 
                 # Since we cannot easily restart app, we might check if 'get_run_limit' sees the patch.
                 # Dynamic limits call function at request time, so os.environ patch SHOULD work.
                 
                 if resp.status_code != 429:
                     print(f"DEBUG: Status {resp.status_code}, Headers: {resp.headers}")
                 
                 self.assertEqual(resp.status_code, 429)

if __name__ == '__main__':
    unittest.main()
