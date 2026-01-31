"""
validation/runner.py

Entry point for the Historical Validation Pipeline.
Orchestrates the data fetching, replay, and reporting.
"""

import sys
from datetime import datetime
from validation.replay import HistoricalReplayEngine

def run_validation():
    print("="*60)
    print("🧪 STARTING HISTORICAL VALIDATION PROTOCOL")
    print("="*60)
    print("Objective: Prove Decision Stability & Underfitting Safety")
    print("Constraint: NO Predictive Optimization Allowed")
    print("="*60)
    
    # Configuration (Could be parameterized later)
    # Defaulting to a recent volatile period for stress testing
    START_DATE = "2023-01-01"
    END_DATE = "2023-06-01"
    SYMBOLS = ["SPY", "QQQ", "IWM"]
    
    print(f"\n⚙️  Config:")
    print(f"   Period: {START_DATE} -> {END_DATE}")
    print(f"   Assets: {SYMBOLS}")
    print(f"   Mode:   Historical Replay (Cached)")
    
    try:
        engine = HistoricalReplayEngine(START_DATE, END_DATE, SYMBOLS)
        
        print("\n📥 Preloading Data...")
        engine.preload_data()
        
        print("\n▶️  Executing Replay...")
        engine.run()
        
        print("\n✅ VALIDATION SUITE COMPLETE.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Validation aborted by user.")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_validation()
