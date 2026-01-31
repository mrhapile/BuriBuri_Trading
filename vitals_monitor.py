import math

def compute_vitals(position: dict) -> dict:
    """
    Computes a Vitals Score (0-100) for a trading position to evaluate its efficiency.
    
    The score reflects a weighted combination of:
    1. Volatility-Adjusted Return (Risk efficiency)
    2. Capital Efficiency (Return on Capital Usage)
    3. Time Efficiency (Penalty for stagnation)

    Args:
        position (dict): A dictionary containing:
            - symbol (str): Ticker symbol
            - entry_price (float): Average entry price
            - current_price (float): Current market price
            - atr (float): Average True Range (volatility proxy)
            - days_held (int): Number of days the position has been open
            - capital_allocated (float): Total capital invested in this position

    Returns:
        dict: Evaluation results including:
            - symbol
            - vitals_score (float)
            - health (str): HEALTHY | WEAK | UNHEALTHY
            - suggested_action (str): HOLD / SCALE | HOLD / MONITOR | REDUCE / EXIT
            - drivers (dict): Breakdown of the component metrics
            - flags (list): Special condition flags (e.g., STAGNANT)
    """
    
    # ---------------------------------------------------------
    # 1. Extract and Validate Inputs
    # ---------------------------------------------------------
    symbol = position.get("symbol", "UNKNOWN")
    entry_price = float(position.get("entry_price", 0.0))
    current_price = float(position.get("current_price", 0.0))
    atr = float(position.get("atr", 0.0))
    days_held = int(position.get("days_held", 0))
    capital_allocated = float(position.get("capital_allocated", 0.0))

    # Safety checks to prevent division by zero or invalid logic
    if entry_price <= 0:
        return {
            "symbol": symbol,
            "vitals_score": 0.0,
            "health": "UNHEALTHY",
            "suggested_action": "REDUCE / EXIT (Data Error: Invalid Entry Price)",
            "drivers": {},
            "flags": ["DATA_ERROR"]
        }
    
    # ---------------------------------------------------------
    # 2. Compute Core Metrics
    # ---------------------------------------------------------
    
    # 1. Raw PnL Percentage
    pnl_pct = ((current_price - entry_price) / entry_price) * 100.0
    
    # 2. Volatility-Adjusted Return
    safe_atr = max(atr, 0.0001)
    vol_adj_return = pnl_pct / safe_atr

    # 3. Time Efficiency Penalty
    time_penalty = days_held / 10.0

    # 4. Capital Efficiency
    safe_capital = max(capital_allocated, 1.0)
    capital_efficiency = pnl_pct / (safe_capital / 100000.0)

    # ---------------------------------------------------------
    # 3. Calculate Efficiency Score (Internal Calculation)
    # ---------------------------------------------------------
    # Weights: 0.5 * Volatility + 0.3 * Capital - 0.2 * Time
    
    raw_efficiency = (
        (0.5 * vol_adj_return) +
        (0.3 * capital_efficiency) -
        (0.2 * time_penalty)
    )

    # Normalize to 0-100
    efficiency_score = 50.0 + (raw_efficiency * 10.0)
    efficiency_score = max(0.0, min(100.0, efficiency_score))
    
    # Round for output
    vitals_score = round(efficiency_score, 2)

    # ---------------------------------------------------------
    # 4. Derivative Flags
    # ---------------------------------------------------------
    # Stagnation: < 2% return but held > 20 days
    stagnant = pnl_pct < 2.0 and days_held > 20
    flags = []
    if stagnant:
        flags.append("STAGNANT")

    # ---------------------------------------------------------
    # 5. Determine Health Classification
    # ---------------------------------------------------------
    health = ""
    action = ""

    if vitals_score < 40:
        health = "UNHEALTHY"
        action = "REDUCE / EXIT"
    elif vitals_score < 60:
        health = "WEAK"
        action = "HOLD / MONITOR"
    else:
        health = "HEALTHY"
        action = "HOLD / SCALE"

    # ---------------------------------------------------------
    # 6. Return Final Output
    # ---------------------------------------------------------
    return {
        "symbol": symbol,
        "vitals_score": vitals_score,
        "health": health,
        "suggested_action": action,
        "drivers": {
            "pnl_pct": round(pnl_pct, 2),
            "vol_adj_return": round(vol_adj_return, 2),
            "time_penalty": round(time_penalty, 2),
            "capital_efficiency": round(capital_efficiency, 2)
        },
        "flags": flags
    }

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    # Example 1: High performing efficient trade
    pos_healthy = {
        "symbol": "NVDA",
        "entry_price": 100.0,
        "current_price": 120.0,   # +20%
        "atr": 2.5,
        "days_held": 5,
        "capital_allocated": 50000.0
    }

    # Example 2: Stagnant trade (Time decay penalty + Stagnant Flag)
    pos_stagnant = {
        "symbol": "INTC",
        "entry_price": 50.0,
        "current_price": 50.5,    # +1% (Low return)
        "atr": 1.5,
        "days_held": 25,          # > 20 days (Stagnant condition)
        "capital_allocated": 100000.0
    }

    # Example 3: Capital inefficient
    pos_bloated = {
        "symbol": "GOOGL",
        "entry_price": 2000.0,
        "current_price": 2010.0,
        "atr": 20.0,
        "days_held": 10,
        "capital_allocated": 500000.0
    }

    results = [
        compute_vitals(pos_healthy),
        compute_vitals(pos_stagnant),
        compute_vitals(pos_bloated)
    ]

    print(f"{'SYMBOL':<10} | {'SCORE':<10} | {'HEALTH':<10} | {'ACTION':<20} | {'FLAGS'}")
    print("-" * 80)
    for r in results:
        flags_str = ",".join(r['flags']) if r['flags'] else "-"
        print(f"{r['symbol']:<10} | {r['vitals_score']:<10} | {r['health']:<10} | {r['suggested_action']:<20} | {flags_str}")
        print(f"   Drivers: {r['drivers']}")
