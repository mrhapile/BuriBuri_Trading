"""
news_scorer.py

Implements deterministic, keyword-based scoring for sector news.
Phase 2.2: Technology Sector Focus.

Rules:
- Score starts at 50 (Neutral).
- No NLP / LLM usage.
- Simple keyword matching.
- Output normalized to 0-100.
"""

def score_tech_news(headlines: list[str]) -> dict:
    """
    Scores a list of Technology sector headlines based on fixed keywords.

    Args:
        headlines (list[str]): List of news headline strings.

    Returns:
        dict: {
            "news_score": int,      # 0-100
            "headline_count": int   # Number of headlines processed
        }
    """
    if not headlines:
        return {
            "news_score": 50,
            "headline_count": 0
        }

    # Configuration (Refinable)
    STARTING_SCORE = 50
    POINT_WEIGHT = 5
    MAX_SCORE = 100
    MIN_SCORE = 0

    # Keyword Definitions (Tech Focused)
    POSITIVE_KEYWORDS = {
        "growth", "demand", "beats", "rally", "soar", "surge", 
        "upgrade", "strong", "record", "bullish", "profit", 
        "innovation", "breakthrough", "high", "jump"
    }

    NEGATIVE_KEYWORDS = {
        "slowdown", "risk", "regulation", "crash", "slump", 
        "downgrade", "weak", "miss", "volatility", "concern",
        "inflation", "drop", "bearish", "loss", "decline", "warns"
    }

    current_score = STARTING_SCORE

    for headline in headlines:
        # Normalize text for matching
        text = headline.lower()
        
        # Scoring Logic
        for word in POSITIVE_KEYWORDS:
            if word in text:
                current_score += POINT_WEIGHT
        
        for word in NEGATIVE_KEYWORDS:
            if word in text:
                current_score -= POINT_WEIGHT

    # Clamping
    final_score = max(MIN_SCORE, min(MAX_SCORE, current_score))

    return {
        "news_score": final_score,
        "headline_count": len(headlines)
    }

# ---------------------------------------------------------
# Simple Verification Runner (If run directly)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Running News Scorer Verification...")
    
    # Test Cases
    test_cases = [
        [],
        ["Tech Sector Rally Continues as AI Demand Soars"],
        ["Analyst Warns of Potential Overvaluation and Crash"],
        [
            "Tech Sector Rally Continues as AI Demand Soars",
            "Analyst Warns of Potential Overvaluation in Chip Stocks"
        ]
    ]

    for i, case in enumerate(test_cases):
        result = score_tech_news(case)
        print(f"Case {i+1}: {len(case)} headlines -> Score: {result['news_score']}")
        print(f"  Result: {result}")
        print("-" * 30)
