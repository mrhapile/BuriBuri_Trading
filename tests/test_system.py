"""
tests/test_system.py

Comprehensive test suite for Portfolio Intelligence System.
Validates imports, mode matrix, profile coverage, and signal integrity.

Run: python3 tests/test_system.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with emoji."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} | {test_name}")
    if details and not passed:
        print(f"         → {details}")


# =============================================================================
# 1. IMPORT TESTS
# =============================================================================

def test_imports():
    """Test that all modules import without errors."""
    print_header("IMPORT TESTS")
    
    modules = [
        "volatility_metrics",
        "news_scorer",
        "sector_confidence",
        "decision_engine",
        "execution_planner",
        "risk_guardrails",
        "execution_summary",
        "position_vitals",
        "capital_lock_in",
        "concentration_guard",
        "opportunity_logic",
        "broker.mock_adapter",
        "broker.alpaca_adapter",
        "demo.demo_profiles",
    ]
    
    all_passed = True
    for mod in modules:
        try:
            __import__(mod)
            print_result(f"import {mod}", True)
        except Exception as e:
            print_result(f"import {mod}", False, str(e))
            all_passed = False
    
    return all_passed


# =============================================================================
# 2. MODE MATRIX TESTS
# =============================================================================

def test_mode_matrix():
    """Test all mode combinations work without crashing."""
    print_header("MODE MATRIX TESTS")
    
    # Test configurations
    configs = [
        {"DEMO_MODE": "true", "USE_ALPACA": "false", "expected": "Demo profiles work"},
        {"DEMO_MODE": "false", "USE_ALPACA": "false", "expected": "Mock adapter works"},
        # Skip Alpaca test if no credentials
        # {"DEMO_MODE": "false", "USE_ALPACA": "true", "expected": "Alpaca adapter works"},
        # {"DEMO_MODE": "true", "USE_ALPACA": "true", "expected": "Demo overrides Alpaca"},
    ]
    
    all_passed = True
    
    for config in configs:
        # Set environment
        os.environ["DEMO_MODE"] = config["DEMO_MODE"]
        os.environ["USE_ALPACA"] = config["USE_ALPACA"]
        os.environ["DEMO_PROFILE"] = "BALANCED_TECH"
        
        desc = f"DEMO={config['DEMO_MODE']}, ALPACA={config['USE_ALPACA']}"
        
        try:
            # Clear cached imports
            mods_to_clear = [k for k in sys.modules.keys() 
                           if k.startswith(('full_system_demo', 'broker.', 'demo.'))]
            for m in mods_to_clear:
                del sys.modules[m]
            
            # Quick import test only (full run tested separately)
            if config["DEMO_MODE"] == "true":
                from demo.demo_profiles import load_demo_profile
                portfolio, positions = load_demo_profile("BALANCED_TECH")
                assert len(positions) > 0, "No positions loaded"
            else:
                from broker.mock_adapter import MockAdapter
                adapter = MockAdapter()
                portfolio = adapter.get_portfolio()
                assert portfolio["total_capital"] > 0, "No capital"
            
            print_result(desc, True)
            
        except Exception as e:
            print_result(desc, False, str(e))
            all_passed = False
    
    return all_passed


# =============================================================================
# 3. DEMO PROFILE COVERAGE
# =============================================================================

def test_demo_profiles():
    """Test all demo profiles generate valid data."""
    print_header("DEMO PROFILE COVERAGE")
    
    from demo.demo_profiles import (
        get_available_profiles, 
        load_demo_profile,
        get_demo_candidates,
        get_demo_heatmap
    )
    
    all_passed = True
    
    for profile_name in get_available_profiles():
        try:
            portfolio, positions = load_demo_profile(profile_name)
            candidates = get_demo_candidates(profile_name)
            heatmap = get_demo_heatmap(profile_name)
            
            # Validate structure
            assert "total_capital" in portfolio, "Missing total_capital"
            assert "cash" in portfolio, "Missing cash"
            assert len(positions) > 0, "No positions"
            
            # Validate positions have required fields
            required_fields = ["symbol", "sector", "entry_price", "current_price", 
                              "atr", "days_held", "capital_allocated"]
            for pos in positions:
                for field in required_fields:
                    assert field in pos, f"Position missing {field}"
            
            print_result(f"Profile: {profile_name}", True)
            print(f"           Positions: {len(positions)}, Candidates: {len(candidates)}")
            
        except Exception as e:
            print_result(f"Profile: {profile_name}", False, str(e))
            all_passed = False
    
    return all_passed


# =============================================================================
# 4. SIGNAL INTEGRITY TESTS
# =============================================================================

def test_signal_integrity():
    """Test signal modules handle edge cases gracefully."""
    print_header("SIGNAL INTEGRITY TESTS")
    
    import volatility_metrics
    import news_scorer
    import sector_confidence
    
    all_passed = True
    
    # Test 1: Empty candles
    try:
        result = volatility_metrics.compute_atr([])
        assert "atr" in result, "Missing ATR in result"
        print_result("ATR with empty candles", True)
    except Exception as e:
        print_result("ATR with empty candles", False, str(e))
        all_passed = False
    
    # Test 2: Empty headlines
    try:
        result = news_scorer.score_tech_news([])
        assert "news_score" in result, "Missing news_score"
        print_result("News score with empty headlines", True)
    except Exception as e:
        print_result("News score with empty headlines", False, str(e))
        all_passed = False
    
    # Test 3: Invalid volatility state
    try:
        result = sector_confidence.compute_sector_confidence("UNKNOWN_STATE", 50)
        assert "sector_confidence" in result, "Missing confidence"
        print_result("Sector confidence with unknown state", True)
    except Exception as e:
        print_result("Sector confidence with unknown state", False, str(e))
        all_passed = False
    
    # Test 4: Volatility classification edge cases
    try:
        result = volatility_metrics.classify_volatility_state(0, 0)
        assert "volatility_state" in result
        print_result("Volatility classification with zeros", True)
    except Exception as e:
        print_result("Volatility classification with zeros", False, str(e))
        all_passed = False
    
    return all_passed


# =============================================================================
# 5. DECISION ENGINE INTEGRATION
# =============================================================================

def test_decision_engine():
    """Test decision engine produces valid output for each profile."""
    print_header("DECISION ENGINE INTEGRATION")
    
    import decision_engine
    from demo.demo_profiles import (
        get_available_profiles, 
        load_demo_profile,
        get_demo_candidates,
        get_demo_heatmap
    )
    
    all_passed = True
    
    for profile_name in get_available_profiles():
        try:
            portfolio, positions = load_demo_profile(profile_name)
            candidates = get_demo_candidates(profile_name)
            heatmap = get_demo_heatmap(profile_name)
            
            # Mock market context
            market_context = {
                "candles": [{"high": 100, "low": 98, "close": 99} for _ in range(20)],
                "news": ["Tech rally continues"]
            }
            
            # Run engine
            result = decision_engine.run_decision_engine(
                portfolio_state=portfolio,
                positions=positions,
                sector_heatmap=heatmap,
                candidates=candidates,
                market_context=market_context
            )
            
            # Validate output
            assert "decisions" in result, "Missing decisions"
            assert "market_posture" in result, "Missing market_posture"
            
            decisions = result.get("decisions", [])
            blocked = result.get("blocked_by_safety", [])
            
            print_result(f"Engine: {profile_name}", True)
            print(f"           Decisions: {len(decisions)}, Blocked: {len(blocked)}")
            
        except Exception as e:
            print_result(f"Engine: {profile_name}", False, str(e))
            all_passed = False
    
    return all_passed


# =============================================================================
# MAIN
# =============================================================================

def run_all_tests():
    """Run complete test suite."""
    print("\n" + "=" * 60)
    print("  🧪 PORTFOLIO INTELLIGENCE SYSTEM - TEST SUITE")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Mode Matrix": test_mode_matrix(),
        "Demo Profiles": test_demo_profiles(),
        "Signal Integrity": test_signal_integrity(),
        "Decision Engine": test_decision_engine(),
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print()
    print(f"  Total: {passed}/{total} test groups passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED - System is judge-ready!")
        return 0
    else:
        print("\n  ⚠️  Some tests failed - review before demo")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
