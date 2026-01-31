"""
phase3_demo.py

Standalone demonstration of Phase 3 Decision Making Logic.
Uses mock Phase 2 inputs to produce advisory Phase 3 decisions.
Designed for clarity and demo purposes only.

Scenarios:
1. Bullish: Low Volatility + Positive News + High Confidence
2. Neutral: Moderate Volatility + Neutral News + Medium Confidence
3. Defensive: High Volatility + Negative News + Low Confidence
"""

def generate_decision(volatility: str, news_score: str, confidence: str) -> dict:
    """
    Applies deterministic decision rules based on inputs.
    Returns a dictionary with 'decision' and 'reason'.
    """
    # 1. DEFENSIVE SCENARIO
    if volatility == "HIGH" or news_score == "NEGATIVE":
        return {
            "decision": "FREEZE / REDUCE RISK",
            "reason": "High uncertainty detected. Preserving capital is priority."
        }
    
    # 2. BULLISH SCENARIO
    if volatility == "LOW" and news_score == "POSITIVE" and confidence == "HIGH":
        return {
            "decision": "DEPLOY CAPITAL / AGGRESSIVE",
            "reason": "Green light across all signals. Market conditions optimal."
        }
    
    # 3. NEUTRAL SCENARIO (Default)
    return {
        "decision": "HOLD / ACCUMULATE CAUTIOUSLY",
        "reason": "Conditions stable but not exciting. Standard size only."
    }

def run_demo():
    print("="*60)
    print("PHASE 3: DECISION LOGIC DEMO (STANDALONE)")
    print("="*60)
    print("")

    scenarios = [
        {
            "name": "Bullish",
            "inputs": {"vol": "LOW", "news": "POSITIVE", "conf": "HIGH"}
        },
        {
            "name": "Neutral",
            "inputs": {"vol": "MODERATE", "news": "NEUTRAL", "conf": "MEDIUM"}
        },
        {
            "name": "Defensive",
            "inputs": {"vol": "HIGH", "news": "NEGATIVE", "conf": "LOW"}
        }
    ]

    for scenario in scenarios:
        name = scenario["name"]
        inputs = scenario["inputs"]
        
        # Calculate Decision
        result = generate_decision(inputs["vol"], inputs["news"], inputs["conf"])
        
        # Print Output
        print(f"[Scenario: {name}]")
        print(f"Volatility:        {inputs['vol']}")
        print(f"News Score:        {inputs['news']}")
        print(f"Sector Confidence: {inputs['conf']}")
        print("-" * 30)
        print(f"Decision: {result['decision']}")
        print(f"Reason:   {result['reason']}")
        print("")
        print("="*60)
        print("")

if __name__ == "__main__":
    run_demo()
