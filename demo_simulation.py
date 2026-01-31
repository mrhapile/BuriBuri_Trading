import time
import decision_engine

def print_separator():
    print("-" * 60)

def print_decision(timestamp, step_label, decisions, reallocation_alert):
    print(f"\n[{timestamp} | {step_label}]")
    
    # Filter for relevant decisions to display (just to keep it clean)
    # in this demo, we'll show all that generated a specific action other than IGNORE/WATCHLIST for positions
    # or specifically highlight changes.
    
    has_activity = False
    
    for d in decisions:
        target = d['target']
        action = d['action']
        reason = d['reason']
        type_ = d['type']
        
        # Formatting specific logic for presentation
        if type_ == "POSITION":
            print(f"{target} → {action}")
            print(f"Reason: {reason}")
            print("")
            has_activity = True
        elif type_ == "CANDIDATE" and action not in ["IGNORE", "WATCHLIST"]:
             print(f"{target} → {action}")
             print(f"Reason: {reason}")
             print("")
             has_activity = True
             
    if reallocation_alert:
        print(">>> Portfolio Alert → REALLOCATION REQUIRED <<<")
    elif not has_activity:
         print("(No major actions required)")

    print_separator()

def main():
    print("Initializing Portfolio Pilot Simulation...")
    print_separator()

    # --- SIMULATION CONFIGURATION ---
    # We will simulate 3 steps: T0, T1, T2
    
    # Shared State
    heatmap = {
        "TECH": 85,
        "MATERIALS": 40,
        "FINANCE": 60
    }
    
    candidates = [
        {"symbol": "NEW_AI_TECH", "sector": "TECH"},
        {"symbol": "RUSTY_CORP", "sector": "MATERIALS"}
    ]

    # --- T0: BASELINE (10:00 AM) ---
    # Scenario: Everything is relatively stable. 
    # OLD_BANK is mediocre but holding.
    
    t0_portfolio = {"total_capital": 1000000.0, "cash": 50000.0}
    t0_positions = [
        {
            "symbol": "OLD_BANK", 
            "sector": "FINANCE",
            "entry_price": 100, "current_price": 105, "atr": 1.5, 
            "days_held": 25, "capital_allocated": 300000,
            "flags": [] 
        },
        {
            "symbol": "HYPER_TECH",
            "sector": "TECH",
            "entry_price": 200, "current_price": 250, "atr": 4.0,
            "days_held": 10, "capital_allocated": 200000
        }
    ]
    
    # Run T0
    report_t0 = decision_engine.run_decision_engine(t0_portfolio, t0_positions, heatmap, candidates)
    print_decision("10:00 AM", "T0", report_t0["decisions"], report_t0["reallocation_trigger"])
    
    # Sleep for effect
    time.sleep(1.5)


    # --- T1: DETERIORATION (10:05 AM) ---
    # Scenario: OLD_BANK sector cools slightly, price drops, becomes stagnant/inefficient.
    # Vitals score drops below 40 -> REDUCE/EXIT.
    
    t1_portfolio = t0_portfolio.copy() 
    t1_positions = [
        {
            "symbol": "OLD_BANK", 
            "sector": "FINANCE",
            "entry_price": 100, "current_price": 101, # Price dropped, profit eroded
            "atr": 1.0, 
            "days_held": 40, # Held longer
            "capital_allocated": 300000,
            #"flags": ["STAGNANT"] # Implicitly detected or forced
        },
        t0_positions[1] # HYPER_TECH unchanged
    ]
    
    # We force the vitals to look bad by context or let the engine decide.
    # In this mock, we assume the engine sees low vitals.
    
    report_t1 = decision_engine.run_decision_engine(t1_portfolio, t1_positions, heatmap, candidates)
    print_decision("10:05 AM", "T1", report_t1["decisions"], report_t1["reallocation_trigger"])
    
    time.sleep(1.5)

    # --- T2: REALLOCATION (10:10 AM) ---
    # Scenario: Capital freed from OLD_BANK (simulated).
    # Cash increases. T1 logic likely triggered "FREE_CAPITAL" or "REDUCE".
    # Now we have cash to deploy into NEW_AI_TECH.
    
    t2_portfolio = {"total_capital": 1000000.0, "cash": 350000.0} # +300k from OLD_BANK
    t2_positions = [
        # OLD_BANK removed
        t0_positions[1] # HYPER_TECH remains
    ]
    
    # Heatmap update: TECH is Very Hot
    heatmap["TECH"] = 95
    
    # Decision engine should see high cash + hot sector candidate -> ALLOCATE
    report_t2 = decision_engine.run_decision_engine(t2_portfolio, t2_positions, heatmap, candidates)
    print_decision("10:10 AM", "T2", report_t2["decisions"], report_t2["reallocation_trigger"])

    print("Simulation Complete.")

if __name__ == "__main__":
    main()
