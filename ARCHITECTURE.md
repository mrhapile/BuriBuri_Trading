# Data Contracts & Architecture

This document defines the **exact internal data formats** used by every module in the Portfolio Intelligence System. All team members (Dev, Mohit) should reference this file when passing data between components.

---

## 1. Position (Core Entity)

A **Position** represents a single open trade. This is consumed by `vitals_monitor.py`, `capital_lock_in.py`, and `concentration_guard.py`.

> **NOTE (Phase Availability):**  
> In Phase 1–2, only a subset of fields may be populated.  
> Fields like `atr` and `days_held` are optional until later phases.

```python
{
    "symbol": str,              # Required. Ticker symbol (e.g., "AAPL", "NVDA")
    "sector": str,              # Required. Sector classification (e.g., "TECH", "ENERGY")
    "entry_price": float,       # Required. Average entry price
    "current_price": float,     # Required. Live market price
    "atr": float,               # Required. Average True Range (volatility proxy)
    "days_held": int,           # Required. Number of calendar days since entry
    "capital_allocated": float  # Required. Absolute capital in this position (USD)
}
```

### Fallback Behavior
| Field           | If Missing                  | Effect                                  |
|-----------------|-----------------------------|-----------------------------------------|
| `symbol`        | Default: `"UNKNOWN"`        | Logged but continues                    |
| `sector`        | Default: `"UNKNOWN"`        | Excluded from concentration checks      |
| `entry_price`   | Default: `0.0`              | **Error**: Cannot compute PnL           |
| `atr`           | Default: `0.0001`           | Prevents division-by-zero               |
| `days_held`     | Default: `0`                | No time penalty applied                 |
| `capital_allocated` | Default: `1.0`          | Prevents division-by-zero               |

---

## 2. Portfolio Snapshot

A **Portfolio** represents the overall account state. Consumed by `capital_lock_in.py` and `decision_engine.py`.

```python
{
    "total_capital": float,     # Required. Total account value (USD)
    "used_capital": float,      # Reserved for future leverage logic
    "cash": float               # Required. Available cash (USD)
}
```

### Fallback Behavior
| Field           | If Missing       | Effect                        |
|-----------------|------------------|-------------------------------|
| `total_capital` | Default: `1.0`   | Prevents division-by-zero     |
| `cash`          | Default: `0.0`   | Assumes fully invested        |

---

## 3. Market Candle (Future Integration)

A **Candle** represents OHLCV data for a single time period. This will be used for computing ATR and trend signals.

```python
{
    "timestamp": str,           # ISO 8601 format (e.g., "2026-01-31T09:30:00Z")
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": int
}
```

### Notes
- ATR Calculation: `ATR = SMA(TR, 14)` where `TR = max(high - low, abs(high - prev_close), abs(low - prev_close))`
- Candles should be passed as a list, sorted oldest-first.

---

## 4. Sector Heatmap (Phase 3+ / Optional)

A **Sector Heatmap** is a dictionary mapping sector names to "opportunity intensity" scores. Consumed by `capital_lock_in.py` and `decision_engine.py`.

```python
{
    "TECH": int,        # 0-100. Higher = more attractive
    "ENERGY": int,
    "BANKING": int,
    ...
}
```

### Interpretation
| Score Range | Label   | Meaning                               |
|-------------|---------|---------------------------------------|
| ≥ 70        | Hot     | High opportunity, prioritize buys    |
| 40 – 69     | Neutral | No strong signal                      |
| < 40        | Cold    | Low opportunity, avoid or exit       |

### Fallback Behavior
- If a sector is missing from the heatmap, it defaults to `50` (Neutral).

---

## 5. Candidate Opportunity

A **Candidate** represents a potential new trade to evaluate. Consumed by `opportunity_scanner.py` and `decision_engine.py`.

> **NOTE:**  
> Candidate entities are not used in Phase 1–2 and are reserved for future multi-asset expansion.

```python
{
    "symbol": str,                  # Required. Ticker symbol
    "sector": str,                  # Required. Sector classification
    "projected_efficiency": float   # Required. Expected Vitals Score (0-100)
}
```

### Notes
- `projected_efficiency` is a **simulated or estimated** score. In production, this could come from a screening model or backtested signals.
- If `projected_efficiency` is missing, the candidate is ignored.

---

## 6. News Headline (Future Integration)

A **News Headline** represents a single news item for sentiment analysis.

```python
{
    "timestamp": str,       # ISO 8601 format
    "headline": str,        # Short text (max 300 chars recommended)
    "source": str,          # E.g., "Bloomberg", "Reuters"
    "symbols": list[str],   # List of affected tickers (e.g., ["AAPL", "MSFT"])
    "sentiment_score": float # Optional. Pre-computed score (-1.0 to 1.0)
}
```

### Fallback Behavior
| Field            | If Missing        | Effect                                   |
|------------------|-------------------|------------------------------------------|
| `symbols`        | Default: `[]`     | Headline not linked to any position      |
| `sentiment_score`| Compute on-the-fly| Use rule-based sentiment scoring (LLM optional in future versions) |

---

## Module Dependency Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      full_system_demo.py                         │
│         (Entry Point: Runs complete pipeline)                    │
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ broker/       │ │ demo/         │ │decision_engine│ │risk_guardrails│
│ alpaca_adapter│ │ demo_profiles │ │    .py        │ │    .py        │
│ mock_adapter  │ │ trend_overlays│ │               │ │               │
└───────────────┘ └───────────────┘ └───────┬───────┘ └───────────────┘
                                            │
        ┌───────────────────────────────────┤
        ▼             ▼             ▼       ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│position_vitals│ │capital_lock_in│ │opportunity_   │ │concentration_ │
│     .py       │ │    .py        │ │ logic.py      │ │   guard.py    │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
        │
        ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│volatility_    │ │ news_scorer   │ │sector_        │
│ metrics.py    │ │    .py        │ │ confidence.py │
└───────────────┘ └───────────────┘ └───────────────┘
```

### New Modules (v2.0)

| Module | Purpose |
|--------|---------|
| `broker/alpaca_adapter.py` | READ-ONLY Alpaca paper trading client |
| `broker/mock_adapter.py` | Mock data generator for testing |
| `demo/demo_profiles.py` | Hardcoded portfolio profiles for demos |
| `demo/trend_overlays.py` | Signal modifiers (TECH_COOLING, VOLATILITY_SHOCK) |
| `risk_guardrails.py` | Safety filtering (concentration, cash, volatility) |
| `execution_planner.py` | Converts decisions to sequential plan |
| `execution_summary.py` | Final reporting layer |
| `backend/app.py` | Flask REST API |
| `tests/test_system.py` | Comprehensive test suite |

---

## Quick Reference: All Required Fields

| Data Type       | Required Fields                                                                 |
|-----------------|---------------------------------------------------------------------------------|
| Position        | `symbol`, `sector`, `entry_price`, `current_price`, `atr`, `days_held`, `capital_allocated` |
| Portfolio       | `total_capital`, `cash`                                                         |
| Sector Heatmap  | At least one sector key-value pair                                              |
| Candidate       | `symbol`, `sector`, `projected_efficiency`                                      |
| Market Candle   | `timestamp`, `open`, `high`, `low`, `close`, `volume`                           |
| News Headline   | `timestamp`, `headline`, `source`, `symbols`                                    |

---

## Versioning

- **v1.0** (2026-01-31): Initial data contracts defined.
