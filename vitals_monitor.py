import feedparser
from datetime import datetime, timezone, timedelta

def fetch_sector_news() -> list[dict]:
    """
    Fetches recent Technology sector news headlines using Google News RSS.
    
    Returns:
        list[dict]: A list of dictionaries with 'title' and 'published' keys.
                    Returns empty list on failure. 
                    Includes only headlines from the last 24 hours.
    """
    # Hardcoded URL for Technology Sector (India Region)
    rss_url = "https://news.google.com/rss/search?q=technology+sector&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        # Parse RSS Feed
        feed = feedparser.parse(rss_url)
        
        # Check for parsing failure or empty feed
        if not feed.entries: 
            print("Error: Empty feed or parsing failure (check network).")
            return []

        headlines = []
        now_utc = datetime.now(timezone.utc)
        one_day_ago = now_utc - timedelta(hours=24)

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            
            # Title Validation
            if not title:
                continue
            
            # Time Handling
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    # published_parsed is a struct_time tuple in UTC
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass
            
            # If date is missing or invalid, we skip it (Strict 24h rule)
            if not pub_date:
                continue

            # Time Filter (Last 24 hours)
            if pub_date < one_day_ago:
                continue
            
            # Add valid headline
            headlines.append({
                "title": title,
                "published": pub_date.isoformat()
            })
            
        return headlines

    except Exception as e:
        # Catch-all for any other runtime errors to ensure no crashes
        print(f"Error fetching news: {e}")
        return []

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== VITALS MONITOR: News Validation (Phase 1) ===")
    print("\n[Test] Fetching Technology Sector News (Last 24h)...")
    try:
        news = fetch_sector_news()
        print(f"Fetched {len(news)} headlines.")
        if news:
            print("Sample Headline:")
            print(f" - Title: {news[0]['title']}")
            print(f" - Published: {news[0]['published']}")
        else:
            print("No news found (or network error).")
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
