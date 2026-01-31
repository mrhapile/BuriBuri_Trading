def detect_capital_lock_in(portfolio: dict, positions: list, sector_heatmap: dict) -> dict:
    """
    Analyzes capital efficiency at the portfolio level to detect "Dead Capital"
    and missed opportunities in "Hot Sectors".
    
    Logic:
    1. Identifies positions that are both low-performing (Vitals < 50) AND inside cold sectors (Heat < 40).
    2. Calculates the ratio of this "Dead Capital" to Total Capital.
    3. Calculates an Opportunity Pressure Score to determine if reallocation is needed.
    
    Args:
        portfolio (dict): {
            "total_capital": float,
            "used_capital": float, # Reserved for future leverage logic
            "cash": float
        }
        positions (list): List of position dicts. Must contain:
            - vitals_score (float) - from Part A
            - capital_allocated (float)
            - sector (str)
        sector_heatmap (dict): Key=Sector Name, Value=Heat Score (0-100)
    
    Returns:
        dict: Assessment of capital efficiency and reallocation warnings.
    """
    
    # ---------------------------------------------------------
    # 1. Inputs & Defaults
    # ---------------------------------------------------------
    total_capital = float(portfolio.get("total_capital", 1.0))
    cash = float(portfolio.get("cash", 0.0))
    
    dead_capital = 0.0
    dead_positions_count = 0
    dead_positions = []
    
    # ---------------------------------------------------------
    # 2. Detect Dead Capital
    # ---------------------------------------------------------
    # Criteria: Vitals Score < 50 AND Sector Heat < 40
    
    for pos in positions:
        vitals = float(pos.get("vitals_score", 0.0))
        allocated = float(pos.get("capital_allocated", 0.0))
        sector = pos.get("sector", "UNKNOWN")
        
        # Get sector efficiency from heatmap (default to 50/Neutral if unknown)
        sector_heat = sector_heatmap.get(sector, 50.0)
        
        is_low_vitals = vitals < 50
        is_cold_sector = sector_heat < 40
        
        if is_low_vitals and is_cold_sector:
            dead_capital += allocated
            dead_positions_count += 1
            dead_positions.append({
                "symbol": pos.get("symbol", "UNKNOWN"),
                "sector": sector,
                "vitals_score": vitals,
                "capital_allocated": allocated
            })

    # ---------------------------------------------------------
    # 3. Compute Capital Lock-in Ratio
    # ---------------------------------------------------------
    # Avoid division by zero
    safe_total_cap = max(total_capital, 1.0)
    lock_in_ratio = dead_capital / safe_total_cap

    # ---------------------------------------------------------
    # 4. Detect Hot Sectors
    # ---------------------------------------------------------
    # Criteria: Heat >= 70
    hot_sectors = [k for k, v in sector_heatmap.items() if v >= 70]
    
    # ---------------------------------------------------------
    # 5. Compute Opportunity Pressure Score
    # ---------------------------------------------------------
    # Formula:
    # (lock_in_ratio * 100)
    # + (len(hot_sectors) * 20)
    # - ((cash / total_capital) * 50)
    
    cash_ratio = cash / safe_total_cap
    
    pressure_score = (
        (lock_in_ratio * 100.0) +
        (len(hot_sectors) * 20.0) -
        (cash_ratio * 50.0)
    )
    
    # Clamp to avoid negatives and Rounding for cleanliness
    pressure_score = max(0.0, pressure_score)
    pressure_score = round(pressure_score, 2)
    
    # ---------------------------------------------------------
    # 6. Trigger Reallocation Alert
    # ---------------------------------------------------------
    reallocation_alert = pressure_score > 50.0
    
    # ---------------------------------------------------------
    # 7. Generate Explainable Summary
    # ---------------------------------------------------------
    lock_in_pct = round(lock_in_ratio * 100, 1)
    
    summary_parts = []
    
    if reallocation_alert:
        summary_parts.append(f"REALLOCATION REQUIRED (Pressure: {pressure_score}).")
    else:
        summary_parts.append(f"No immediate action needed (Pressure: {pressure_score}).")
        
    summary_parts.append(f"{lock_in_pct}% of capital is locked in low-efficiency positions.")
    
    if hot_sectors:
        summary_parts.append(f"High-opportunity sectors ({', '.join(hot_sectors)}) are active.")
    else:
        summary_parts.append("No specific high-opportunity sectors detected.")
        
    final_summary = " ".join(summary_parts)

    return {
        "dead_capital": round(dead_capital, 2),
        "dead_positions": dead_positions,
        "lock_in_ratio": round(lock_in_ratio, 4),
        "hot_sectors": hot_sectors,
        "pressure_score": pressure_score,
        "reallocation_alert": reallocation_alert,
        "summary": final_summary
    }

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Define Portfolio
    portfolio_data = {
        "total_capital": 1_000_000.0,
        "used_capital": 900_000.0, # Reserved for future leverage logic
        "cash": 100_000.0
    }
    
    # 2. Define Positions (Simulating Part A outputs + Sector info)
    # Note: These vitals_score values would come from compute_vitals()
    current_positions = [
        {
            "symbol": "OIL_CO",
            "sector": "ENERGY",  # Hot sector
            "capital_allocated": 300_000.0,
            "vitals_score": 85.0 # Healthy
        },
        {
            "symbol": "OLD_BANK",
            "sector": "BANKING", # Cold sector
            "capital_allocated": 300_000.0,
            "vitals_score": 35.0 # Unhealthy -> DEAD CAPITAL
        },
        {
            "symbol": "SLOW_PHARMA",
            "sector": "PHARMA", # Cold sector
            "capital_allocated": 200_000.0,
            "vitals_score": 45.0 # Weak (Still < 50) -> DEAD CAPITAL
        },
        {
            "symbol": "TECH_STARTUP",
            "sector": "TECH",   # Hot sector
            "capital_allocated": 100_000.0,
            "vitals_score": 70.0 # Healthy
        }
    ]
    
    # 3. Define Sector Heatmap
    market_heatmap = {
        "TECH": 85,    # Hot
        "ENERGY": 75,  # Hot
        "BANKING": 30, # Cold
        "PHARMA": 25   # Cold
    }
    
    # 4. Run Lock-in Detector
    result = detect_capital_lock_in(portfolio_data, current_positions, market_heatmap)
    
    # 5. Print Results
    import json
    print(json.dumps(result, indent=4))
