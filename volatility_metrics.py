from typing import List, Dict, Optional

def compute_atr(candles: List[Dict], period: int = 14) -> Dict[str, Optional[float]]:
    """
    Computes Average True Range (ATR) using Simple Moving Average (SMA) logic.
    
    Formula:
        TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
        ATR = SMA(TR, period)
        
    Args:
        candles (list): List of dictionary candles.
        period (int): The lookback period (default 14).
    
    Returns:
        dict: {"atr": float} or {"atr": None}
    """
    # 1. Validation & Safety Checks
    if not candles:
        print("Warning: No candles provided for ATR computation.")
        return {"atr": None}
    
    # Need period+1 candles for period TRs
    if len(candles) < period + 1:
        print(f"Warning: Insufficient data. Need {period + 1} candles, got {len(candles)}.")
        return {"atr": None}

    # 2. Sort Candles (Oldest -> Newest)
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
            
            tr = max(
                current_h - current_l,
                abs(current_h - prev_c),
                abs(current_l - prev_c)
            )
            tr_values.append(tr)
        except (ValueError, TypeError):
            continue

    # 4. Compute ATR (SMA)
    if len(tr_values) < period:
        return {"atr": None}
        
    recent_tr = tr_values[-period:]
    atr_value = sum(recent_tr) / period
    
    return {"atr": round(atr_value, 4)}


def classify_volatility_state(current_atr: float, baseline_atr: float, threshold_pct: float = 10.0) -> Dict[str, str]:
    """
    Classifies the volatility regime by comparing current ATR against a baseline.
    
    Logic:
        Diff % = ((Current - Baseline) / Baseline) * 100
        - If Diff > Threshold: EXPANDING
        - If Diff < -Threshold: CONTRACTING
        - Else: STABLE
        
    Args:
        current_atr (float): Most recent ATR value.
        baseline_atr (float): Historical average ATR (e.g., 10-period SMA of ATR).
        threshold_pct (float): Percentage change required to trigger state change (default 10.0).
        
    Returns:
        dict: {"volatility_state": "EXPANDING | STABLE | CONTRACTING"}
    """
    # Safety
    if baseline_atr <= 0:
        return {"volatility_state": "STABLE"} # Fallback on invalid baseline
    
    pct_change = ((current_atr - baseline_atr) / baseline_atr) * 100.0
    
    state = "STABLE"
    if pct_change > threshold_pct:
        state = "EXPANDING"
    elif pct_change < -threshold_pct:
        state = "CONTRACTING"
        
    return {"volatility_state": state}


# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== VOLATILITY METRICS TEST ===")
    
    # 1. Test ATR Computation
    mock_candles = [
        {"timestamp": f"2026-01-31T10:{i:02d}:00Z", "high": 105+i, "low": 100+i, "close": 102+i}
        for i in range(20)
    ]
    atr_res = compute_atr(mock_candles, 14)
    print(f"ATR Result: {atr_res}")
    
    # 2. Test Regime Classification
    print("\n--- Regime Classification Tests ---")
    
    # Case A: Expanding (2.5 vs 2.0 -> +25%)
    res_exp = classify_volatility_state(2.5, 2.0, threshold_pct=10)
    print(f"Current=2.5, Base=2.0 -> {res_exp['volatility_state']} (Expected: EXPANDING)")
    
    # Case B: Stable (2.05 vs 2.0 -> +2.5%)
    res_stable = classify_volatility_state(2.05, 2.0, threshold_pct=10)
    print(f"Current=2.05, Base=2.0 -> {res_stable['volatility_state']} (Expected: STABLE)")
    
    # Case C: Contracting (1.5 vs 2.0 -> -25%)
    res_cont = classify_volatility_state(1.5, 2.0, threshold_pct=10)
    print(f"Current=1.5, Base=2.0 -> {res_cont['volatility_state']} (Expected: CONTRACTING)")
    
    # Case D: Safety
    res_err = classify_volatility_state(1.5, 0.0)
    print(f"Baseline=0.0 -> {res_err['volatility_state']} (Expected: STABLE)")
