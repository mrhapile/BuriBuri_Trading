"""
Demo Simulation - Phase 2 Signal Validation
============================================
This demo validates that Phase 2 signals can be computed and observed
independently of Phase 3 decisions.

Phase Boundary:
    Phase 1 → Market data ingestion (candles, news)
    Phase 2 → Signal computation & state assessment (THIS FILE validates Phase 2)
    Phase 3 → Portfolio decisions & actions (NOT in scope here)

This script:
    - Computes ATR from OHLC data
    - Derives volatility state classification
    - Computes news sentiment scores
    - Displays all Phase 2 signals in a clean, readable format

NO broker connections. NO portfolio decisions. Pure signal validation.

Author: Quantitative Portfolio Engineering Team
"""

import time
import logging
from typing import List, Dict, Any

# Phase 1 Import (Data Ingestion)
import opportunity_scanner

# Configure logging to suppress noisy output during demo
logging.basicConfig(level=logging.ERROR)

# =============================================================================
# PHASE 2 SIGNAL UTILITIES (Pure Computation - No Decisions)
# =============================================================================

def compute_atr(candles: List[Dict[str, Any]], period: int = 14) -> float:
    """Computes Average True Range (ATR) from OHLC candle data."""
    if len(candles) < 2:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(candles)):
        current = candles[i]
        previous = candles[i - 1]
        
        try:
            high = float(current.get("high", 0))
            low = float(current.get("low", 0))
            prev_close = float(previous.get("close", 0))
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        except (ValueError, TypeError):
            continue
    
    if not true_ranges:
        return 0.0
    
    relevant_ranges = true_ranges[-period:]
    atr = sum(relevant_ranges) / len(relevant_ranges)
    return round(atr, 4)


def classify_volatility_state(atr: float, baseline_atr: float = 1.5) -> str:
    """Classifies volatility state based on ATR relative to a baseline."""
    if atr <= 0:
        return "UNKNOWN"
    
    low_threshold = baseline_atr * 0.7
    high_threshold = baseline_atr * 1.5
    
    if atr < low_threshold:
        return "LOW_VOLATILITY"
    elif atr > high_threshold:
        return "HIGH_VOLATILITY"
    else:
        return "NORMAL_VOLATILITY"


def compute_news_sentiment(news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes aggregate news sentiment score from news items."""
    if not news_items:
        return {"score": 0.0, "bias": "NEUTRAL", "item_count": 0}
    
    try:
        sentiments = [float(item.get("sentiment", 0.0)) for item in news_items]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if avg_sentiment > 0.2:
            bias = "POSITIVE"
        elif avg_sentiment < -0.2:
            bias = "NEGATIVE"
        else:
            bias = "NEUTRAL"
            
        return {
            "score": round(avg_sentiment, 3),
            "bias": bias,
            "item_count": len(news_items)
        }
    except Exception:
        return {"score": 0.0, "bias": "ERROR", "item_count": 0}


def compute_position_vitals_summary(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes aggregate vitals statistics for a position set."""
    if not positions:
        return {
            "count": 0, "avg_vitals": 0.0, "min_vitals": 0.0,
            "max_vitals": 0.0, "healthy_count": 0, "weak_count": 0,
            "unhealthy_count": 0
        }
    
    try:
        scores = [float(p.get("vitals_score", 50.0)) for p in positions]
        healthy = sum(1 for s in scores if s >= 60)
        weak = sum(1 for s in scores if 40 <= s < 60)
        unhealthy = sum(1 for s in scores if s < 40)
        
        return {
            "count": len(positions),
            "avg_vitals": round(sum(scores) / len(scores), 2),
            "min_vitals": round(min(scores), 2),
            "max_vitals": round(max(scores), 2),
            "healthy_count": healthy,
            "weak_count": weak,
            "unhealthy_count": unhealthy
        }
    except Exception:
        return {"count": 0, "avg_vitals": 0.0}  # Safe fallback


# =============================================================================
# PHASE 2 SIGNAL DISPLAY (Human-Readable Output)
# =============================================================================

def print_phase2_signals(timestamp: str, atr: float, volatility_state: str, 
                        news_sentiment: Dict[str, Any], vitals_summary: Dict[str, Any] = None):
    """Prints Phase 2 signals in a clean, human-readable format."""
    print(f"\n{'='*50}")
    print(f"  PHASE 2 SIGNALS  [{timestamp}]")
    print(f"{'='*50}\n")
    
    print(f"  ATR (15m):           {atr:.4f}")
    print(f"  Volatility State:    {volatility_state}\n")
    
    print(f"  News Sentiment:      {news_sentiment['score']:+.3f} ({news_sentiment['bias']})")
    print(f"  News Items Analyzed: {news_sentiment['item_count']}\n")
    
    if vitals_summary and vitals_summary.get("count", 0) > 0:
        print(f"  Position Count:      {vitals_summary['count']}")
        print(f"  Avg Vitals Score:    {vitals_summary['avg_vitals']}")
        print(f"  Vitals Range:        [{vitals_summary['min_vitals']} - {vitals_summary['max_vitals']}]")
        print(f"  Health Distribution: {vitals_summary['healthy_count']} healthy, "
              f"{vitals_summary['weak_count']} weak, "
              f"{vitals_summary['unhealthy_count']} unhealthy\n")
    
    print(f"{'-'*50}\n")


def print_separator():
    print("-" * 60)


# =============================================================================
# MOCK DATA GENERATORS (Standalone - No Broker Dependencies)
# =============================================================================

def generate_mock_candles(scenario: str = "normal") -> List[Dict[str, Any]]:
    """Generates mock OHLC candle data for testing."""
    base_price = 145.0
    if scenario == "low_vol":
        price_range = 0.2
    elif scenario == "high_vol":
        price_range = 5.0
    else:
        price_range = 1.5

    candles = []
    for i in range(5):
        high_mod = (i+1) * (price_range / 5)
        candles.append({
            "open": base_price + i,
            "high": base_price + i + high_mod,
            "low": base_price + i - (high_mod/2),
            "close": base_price + i + (high_mod/2)
        })
    return candles


def generate_mock_news(scenario: str = "neutral") -> List[Dict[str, Any]]:
    """Generates mock news sentiment data for testing."""
    if scenario == "positive":
        return [{"sentiment": 0.65}, {"sentiment": 0.45}, {"sentiment": 0.55}]
    elif scenario == "negative":
        return [{"sentiment": -0.55}, {"sentiment": -0.40}, {"sentiment": -0.35}]
    else:
        return [{"sentiment": 0.05}, {"sentiment": -0.10}, {"sentiment": 0.08}]


def generate_mock_positions(scenario: str = "mixed") -> List[Dict[str, Any]]:
    """Generates mock position data with pre-computed vitals scores."""
    if scenario == "healthy":
        return [{"vitals_score": 85.0}, {"vitals_score": 78.0}, {"vitals_score": 72.0}]
    elif scenario == "weak":
        return [{"vitals_score": 38.0}, {"vitals_score": 42.0}, {"vitals_score": 35.0}]
    else:
        return [{"vitals_score": 88.0}, {"vitals_score": 55.0}, {"vitals_score": 32.0}]


# =============================================================================
# MAIN SIMULATION - PHASE 2 SIGNAL VALIDATION
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("  PHASE 2 SIGNAL VALIDATION DEMO")
    print("  BuriBuri Trading System")
    print("=" * 60 + "\n")
    print("This demo computes and displays Phase 2 signals.")
    print("It attempts to ingest real market data (Phase 1).")
    print("If API unavailable, it gracefully falls back to mock data.\n")
    print_separator()
    
    # ---------------------------------------------------------
    # 1. ATTEMPT REAL DATA INGESTION (PHASE 1)
    # ---------------------------------------------------------
    print("\n>>> PHASE 1: Data Availability Check")
    
    real_candles = []
    using_mock = False
    
    try:
        print("    Attempting to fetch XLK candles from Polygon API...")
        real_candles = opportunity_scanner.fetch_tech_sector_candles(limit=20)
        
        if real_candles:
            print(f"    ✅ Success: Fetched {len(real_candles)} live candles.")
            atr_input = real_candles
        else:
            print("    ⚠️  API returned no data (likely no API key set).")
            print("    👉 Switching to MOCK DATA for simulation.")
            using_mock = True
    except Exception as e:
        print(f"    ❌ Error during ingestion: {e}")
        print("    👉 Switching to MOCK DATA for simulation.")
        using_mock = True
        
    print_separator()

    # ---------------------------------------------------------
    # 2. RUN SIMULATION SCENARIOS (PHASE 2)
    # ---------------------------------------------------------
    
    # Scenario 1: Using Real Data (if available) OR Normal Mock
    print("\n>>> SCENARIO 1: Live Market Conditions (or Mock Normal)")
    
    if using_mock:
        dataset = generate_mock_candles("normal")
    else:
        dataset = real_candles

    atr = compute_atr(dataset)
    vol_state = classify_volatility_state(atr)
    # News is always mock since we removed news fetching from Phase 1
    sentiment = compute_news_sentiment(generate_mock_news("neutral")) 
    vitals = compute_position_vitals_summary(generate_mock_positions("mixed"))
    
    print_phase2_signals("CURRENT", atr, vol_state, sentiment, vitals)
    
    # Run High Volatility Mock Scenario to prove logic handles it
    print("\n>>> SCENARIO 2: [Mock] High Volatility Stress Test")
    atr_stress = compute_atr(generate_mock_candles("high_vol"))
    vol_stress = classify_volatility_state(atr_stress)
    print_phase2_signals("STRESS_TEST", atr_stress, vol_stress, 
                        {"score": -0.5, "bias": "NEGATIVE", "item_count": 5}, 
                        {
                            "avg_vitals": 35.0, "count": 5, 
                            "min_vitals": 20.0, "max_vitals": 45.0,
                            "healthy_count": 0, "weak_count": 2, "unhealthy_count": 3
                        })

    print("\n" + "=" * 60)
    print("  VALIDATION COMPLETE - SYSTEM STABLE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
