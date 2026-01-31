from typing import List, Dict, Optional

def compute_atr(candles: List[Dict], period: int = 14) -> Dict[str, Optional[float]]:
    """
    Computes Average True Range (ATR) using Simple Moving Average (SMA) logic.
    
    Formula:
        TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
        ATR = SMA(TR, period)
        
    Args:
        candles (list): List of dictionaries containing 'high', 'low', 'close', 'timestamp'.
        period (int): The lookback period (default 14).
    
    Returns:
        dict: {"atr": float} or {"atr": None} if insufficient data.
    """
    # 1. Validation & Safety Checks
    if not candles:
        print("Warning: No candles provided for ATR computation.")
        return {"atr": None}
    
    # We need at least 'period + 1' candles to compute 'period' TR values (since TR depends on prev_close)
    # Exception: TR of first candle is High-Low. If we use that, we need 'period' candles.
    # Standard practice usually skips first TR or uses H-L. We'll stick to strict TR requiring prev_close for stability.
    if len(candles) < period + 1:
        print(f"Warning: Insufficient data. Need {period + 1} candles, got {len(candles)}.")
        return {"atr": None}

    # 2. Sort Candles (Oldest -> Newest) based on ISO timestamp
    # Assuming 'timestamp' is ISO 8601 string
    try:
        sorted_candles = sorted(candles, key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        print(f"Error sorting candles: {e}")
        return {"atr": None}

    # 3. Compute True Range (TR) Series
    tr_values = []
    
    for i in range(1, len(sorted_candles)):
        current = sorted_candles[i]
        prev = sorted_candles[i-1]
        
        try:
            current_h = float(current.get("high", 0))
            current_l = float(current.get("low", 0))
            current_c = float(current.get("close", 0))
            prev_c = float(prev.get("close", 0))
            
            # TR Calculation
            hl = current_h - current_l
            h_pc = abs(current_h - prev_c)
            l_pc = abs(current_l - prev_c)
            
            tr = max(hl, h_pc, l_pc)
            tr_values.append(tr)
            
        except (ValueError, TypeError) as e:
            print(f"Error processing candle data at index {i}: {e}")
            continue

    # 4. Compute ATR (SMA of last 'period' TRs)
    if len(tr_values) < period:
        # Should be caught by initial length check, but double check after error skipping
        return {"atr": None}
        
    # We take the LAST 'period' TR values to get the current ATR
    recent_tr = tr_values[-period:]
    atr_value = sum(recent_tr) / period
    
    return {"atr": round(atr_value, 4)}

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== ATR COMPUTATION TEST ===")
    
    # Mock Data (15-min candles style)
    mock_candles = [
        {"timestamp": "2026-01-31T10:00:00Z", "high": 105, "low": 100, "close": 102},
        {"timestamp": "2026-01-31T10:15:00Z", "high": 106, "low": 101, "close": 104},
        {"timestamp": "2026-01-31T10:30:00Z", "high": 104, "low": 102, "close": 103},
        {"timestamp": "2026-01-31T10:45:00Z", "high": 107, "low": 103, "close": 106},
        {"timestamp": "2026-01-31T11:00:00Z", "high": 108, "low": 105, "close": 107},
        {"timestamp": "2026-01-31T11:15:00Z", "high": 109, "low": 106, "close": 108},
        {"timestamp": "2026-01-31T11:30:00Z", "high": 110, "low": 108, "close": 109},
        {"timestamp": "2026-01-31T11:45:00Z", "high": 111, "low": 109, "close": 110},
        {"timestamp": "2026-01-31T12:00:00Z", "high": 112, "low": 110, "close": 111},
        {"timestamp": "2026-01-31T12:15:00Z", "high": 113, "low": 111, "close": 112},
        {"timestamp": "2026-01-31T12:30:00Z", "high": 114, "low": 112, "close": 113},
        {"timestamp": "2026-01-31T12:45:00Z", "high": 115, "low": 113, "close": 114},
        {"timestamp": "2026-01-31T13:00:00Z", "high": 116, "low": 114, "close": 115},
        {"timestamp": "2026-01-31T13:15:00Z", "high": 117, "low": 115, "close": 116},
        {"timestamp": "2026-01-31T13:30:00Z", "high": 118, "low": 116, "close": 117}, # 15th candle
    ]
    
    # Test valid
    result = compute_atr(mock_candles, period=14)
    print(f"Valid Data ATR (Expected ~2.0): {result}")
    
    # Test insufficient
    short_data = mock_candles[:10]
    result_insufficient = compute_atr(short_data, period=14)
    print(f"Insufficient Data ATR (Expected None): {result_insufficient}")
    
    # Test scrambled order
    import random
    scrambled = mock_candles[:]
    random.shuffle(scrambled)
    result_scrambled = compute_atr(scrambled, period=14)
    print(f"Scrambled Data ATR (Should match Valid): {result_scrambled}")
