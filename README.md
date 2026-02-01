# 🐻📈 BuriBuri Trading

**An Explainable, Risk-Aware Portfolio Decision Engine**

> Continuous decision-making for risk-aware portfolio management.  
> _(Hackathon Prototype — Do not use with real assets.)_

---

## 📊 Project Status

| Phase | Description | Status |
|:------|:------------|:------:|
| Phase 1 | Data ingestion (Alpaca / Historical) | ✅ Complete |
| Phase 2 | Signal computation | ✅ Complete |
| Phase 3 | Decision engine | ✅ Complete |
| Phase 4 | Risk guardrails | ✅ Complete |
| Phase 5 | Execution planning (Advisory) | ✅ Complete |
| Phase 6 | Frontend dashboard | ✅ Complete |
| Phase 7 | Trade execution | ❌ Disabled (by design) |

**Completion:** ~90% — Full decision pipeline with market-aware data routing is functional.  
**Note:** Execution is intentionally disabled. This system produces *advisory decisions*, not trades.

---

## 🏁 Getting Started

### Who This MVP Is For

This prototype is designed for **hackathon judges, reviewers, and developers** who want to explore an explainable, rule-based portfolio decision engine. It demonstrates risk-aware capital allocation logic without requiring real trading credentials.

### Prerequisites

- **Python 3.8+** (tested on 3.10+)
- **pip** for installing dependencies
- A terminal/command line interface

### Quick Start (Demo Mode)

No API keys required. Run the full system with mock data:

```bash
# 1. Clone the repository
git clone https://github.com/mrhapile/BuriBuri_Trading.git
cd BuriBuri_Trading

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the full system demo
python3 full_system_demo.py
```

This runs the complete decision pipeline using cached historical data and demo profiles.

### Optional: Live Data Mode

To use live market data during market hours, set your Alpaca paper trading credentials:

```bash
export ALPACA_API_KEY=your_paper_api_key
export ALPACA_SECRET_KEY=your_paper_secret
export ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Safe fallback:** If credentials are missing or the API is unavailable, the system automatically uses historical data mode. No crashes, no errors.

### What You Will See

When you run the demo, the console will display:

1. **System Mode** — LIVE or HISTORICAL data source
2. **Market Posture** — Current risk assessment (RISK_OFF → AGGRESSIVE)
3. **Position Analysis** — Health scores for each holding (0-100)
4. **Decisions** — Recommended actions with clear explanations
5. **Blocked Actions** — Any decisions rejected by safety guardrails

Example output:
```
📊 Posture: NEUTRAL | Risk: MEDIUM
💊 Analyzing position vitals...
🛡️ Evaluating concentration limits...
✅ Final decisions ready: 3 approved

[Primary Decision]
REDUCE SLOW_UTIL (Score: 42)
Reason: Vitals critically low. Reduce exposure.
```

### Important Notes

> ⚠️ **This is an advisory-only system.** No trades are executed.  
> All recommendations are for demonstration and educational purposes only.  
> Do not use with real assets or production trading accounts.

---

## 🧠 Problem Statement

Traditional trading systems treat positions as isolated events. Once opened, they stop reasoning until a fixed exit is hit.

In reality:
- Capital gets stuck in stagnant trades  
- Risk accumulates silently (volatility, concentration)  
- Better opportunities appear while capital is locked  

**BuriBuri Trading** addresses this by treating capital as a resource that must *continuously justify its allocation*.

---

## 👥 Team

| Name | Role |
|:-----|:-----|
| Nishtha Vadhwani | Team Lead |
| Akash Anand | Tech Lead |
| Mohit Ray | UI/UX |
| Dev Jaiswal | Reviewer / Tester |

---

## 🎯 System Philosophy

| Principle | Meaning |
|:----------|:--------|
| **Portfolio-first** | Optimizes entire portfolios, not single trades |
| **Safety > Aggressiveness** | Capital preservation is more important than growth |
| **Explainability** | Every decision has human-readable reasons |
| **No Forced Action** | "Doing nothing" is often the best decision |
| **Transparency** | Data source is always clearly labeled |

> **This system is an advisor.** It generates high-fidelity recommendations but intentionally disables execution.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PORTFOLIO INTELLIGENCE SYSTEM                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│   │  PHASE 1   │───▶│  PHASE 2   │───▶│  PHASE 3   │            │
│   │  INGEST    │    │  SIGNALS   │    │  DECISIONS │            │
│   └────────────┘    └────────────┘    └────────────┘            │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│   │ Portfolio  │    │ Volatility │    │  Actions   │            │
│   │ Positions  │    │ News Score │    │ + Reasons  │            │
│   │ Candidates │    │ Confidence │    │            │            │
│   └────────────┘    └────────────┘    └────────────┘            │
│                                              │                  │
│                                              ▼                  │
│                         ┌─────────────────────────────┐         │
│                         │   PHASE 4: RISK GUARDRAILS  │         │
│                         │   (Concentration, Cash,     │         │
│                         │    Volatility Guards)       │         │
│                         └─────────────────────────────┘         │
│                                              │                  │
│                                              ▼                  │
│                         ┌─────────────────────────────┐         │
│                         │  PHASE 5: EXECUTION PLAN    │         │
│                         │  (Advisory Only - No Exec)  │         │
│                         └─────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Breakdown

| Phase | Module(s) | Input | Output |
|:------|:----------|:------|:-------|
| **Phase 1** | `data_router.py`, `broker/*.py`, `historical_data_service.py` | Market status, credentials | Portfolio, positions, candidates |
| **Phase 2** | `volatility_metrics.py`, `news_scorer.py`, `sector_confidence.py` | Candles, headlines | ATR, volatility state, news score, confidence |
| **Phase 3** | `decision_engine.py`, `position_vitals.py`, `concentration_guard.py` | Signals + positions | Proposed actions with reasons |
| **Phase 4** | `risk_guardrails.py` | Proposed actions + context | Allowed vs blocked actions |
| **Phase 5** | `execution_planner.py`, `execution_summary.py` | Safe actions | Sequential plan (advisory) |

---

## 📊 Data Sources & Operating Modes

The system automatically selects the appropriate data source based on market status:

| Market Status | Data Mode | Data Source | Symbol Selection | Time Range |
|:--------------|:----------|:------------|:-----------------|:-----------|
| **OPEN** | LIVE | Alpaca + Polygon API | From live portfolio | Disabled |
| **CLOSED** | HISTORICAL | Alpaca Historical Cache | User selectable | User selectable |

### Strict Routing Rules

- **Market OPEN → LIVE DATA ONLY**: No fallbacks, no mixing
- **Market CLOSED → HISTORICAL DATA ONLY**: Uses cached Alpaca data
- **Session Immutability**: Data mode is locked at session start

### Available Historical Data

Cached symbols for historical validation:
- **SPY** — S&P 500 ETF
- **QQQ** — NASDAQ-100 ETF
- **IWM** — Russell 2000 ETF

Time ranges: 1 Month, 4 Months, 6 Months, 1 Year

### Security Note

- **Alpaca Integration is READ-ONLY**
- Only paper trading URL allowed (`https://paper-api.alpaca.markets`)
- Credentials from environment variables only
- No write operations, no order submission

---

## 🎭 Demo Scenarios

### Behavioral Demonstrations

The system includes **5 behavioral scenarios** that demonstrate specific agent intelligence:

| Scenario | Trigger | What It Demonstrates |
|:---------|:--------|:--------------------|
| **🚨 Crash Reflex** | Volatility spike | Capital preservation overrides profit-seeking |
| **🛡️ Concentration Guard** | 75%+ sector exposure | Refuses perfect trades due to structural limits |
| **👀 Disciplined Observer** | Noisy market signals | Chooses inaction over forced action |
| **♻️ Dead Capital Rotator** | Stagnant positions | Identifies and redeploys underperforming capital |
| **🪤 Greedy Trap** | High hype + high volatility | Anti-FOMO skepticism in conflicting signals |

### Legacy Demo Profiles

For testing specific portfolio states:

| Profile | Capital | Scenario | Expected Response |
|:--------|:--------|:---------|:------------------|
| `BALANCED_TECH` | $500k | Healthy, diversified | MAINTAIN structure |
| `OVERCONCENTRATED_TECH` | $1M | 82% in TECH | TRIM_RISK, block new TECH |
| `LOSING_PORTFOLIO` | $750k | Multiple losers | RISK_OFF posture |
| `ROTATION_SCENARIO` | $800k | TECH cooling, ENERGY rising | FREE_CAPITAL → reallocate |
| `CASH_HEAVY` | $500k | 40% idle cash | WAIT (reject weak trades) |

---

## 📝 Decision Explainability

Every decision includes human-readable reasoning:

```json
{
  "action": "TRIM_RISK",
  "target": "AMD",
  "score": 31.0,
  "reasons": [
    "Position vitals critically low (Score: 31/100)",
    "Sector TECH is over-concentrated (>60%)",
    "High-confidence upgrade opportunity available in ENERGY"
  ]
}
```

This ensures a human operator can always understand **why** a recommendation was made.

---

## 🛡️ Risk & Safety Guardrails

Safety rules applied **after** decisions, **before** execution:

| Guard | Trigger | Effect |
|:------|:--------|:-------|
| **Sector Concentration** | Any sector > 60% | Block new allocations to that sector |
| **Cash Reserve** | Cash < minimum threshold | Block outflows, encourage inflows |
| **Volatility × Aggression** | High volatility + aggressive action | Scale down or block |

> **Rule:** Safety **always** overrides aggressiveness. A profitable trade will be blocked if it violates safety rules.

---

## 🧠 Agent Intelligence Features

### Agent Memory (Cross-Run Learning)

The system maintains memory between runs:
- Tracks previous market posture
- Computes risk trend (INCREASING / DECREASING / STABLE)
- Provides context for decision continuity

### Reasoning Stream

Real-time visibility into the agent's thought process:
- Step-by-step signal interpretation
- Decision rationale at each phase
- Visible in the frontend "Brain Log" panel

### Crash Simulation

Toggle to test defensive behavior:
- Forces RISK_OFF posture
- Demonstrates capital preservation logic
- Validates guardrail effectiveness

---

## ✅ Feature Status

| Feature | Status | Details |
|:--------|:------:|:--------|
| Position vitals (0–100) | ✅ | Efficiency score per position |
| Sector concentration guard | ✅ | Warning at 60%, breach at 70% |
| Capital lock-in detection | ✅ | Flags dead capital in cold sectors |
| Volatility regime | ✅ | EXPANDING / STABLE / CONTRACTING |
| News sentiment | ✅ | Keyword-based scoring (no LLM) |
| Market posture | ✅ | RISK_OFF → AGGRESSIVE spectrum |
| Decision synthesis | ✅ | Multi-factor, explainable output |
| Risk guardrails | ✅ | Concentration, cash, volatility gates |
| Demo profiles | ✅ | 5 hardcoded scenarios |
| Behavioral scenarios | ✅ | 5 intelligence demonstrations |
| Alpaca integration | ✅ | READ-ONLY paper trading |
| Market-aware routing | ✅ | Auto-switches LIVE ↔ HISTORICAL |
| Historical validation | ✅ | SPY, QQQ, IWM cached data |
| Agent memory | ✅ | Cross-run risk tracking |
| Reasoning stream | ✅ | Real-time thought log |
| Crash simulation | ✅ | Toggle for defensive testing |
| Backend API | ✅ | Flask REST endpoint |
| Frontend dashboard | ✅ | Full UI with market-aware controls |
| Unit tests | ✅ | Comprehensive test suite |
| Cloud deployment | ✅ | Render.yaml configuration |
| Broker execution | ❌ | Intentionally disabled |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/mrhapile/BuriBuri_Trading.git
cd BuriBuri_Trading
pip3 install -r requirements.txt
```

### 2. Run Backend API (Recommended)

```bash
python3 backend/app.py
```

API available at `http://localhost:10000`

### 3. Open Frontend

Open `index.html` in a browser, or serve locally:

```bash
python3 -m http.server 8080
# Open http://localhost:8080 in browser
```

### 4. Run CLI Demo

```bash
python3 full_system_demo.py
```

The system automatically detects market status and uses appropriate data source.

### 5. Run Test Suite

```bash
python3 tests/test_system.py
```

---

## 🔑 Environment Variables

Create a `.env` file (see `.env.example`):

```ini
# Alpaca Paper Trading (Optional - for live mode)
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Note:** Alpaca credentials are optional. Without them, the system operates in HISTORICAL mode only.

---

## 📦 Core Modules

| Module | Purpose |
|:-------|:--------|
| `data_router.py` | Market-aware data source routing |
| `market_mode.py` | Market status detection (OPEN/CLOSED) |
| `market_aware_runner.py` | Unified analysis runner |
| `historical_data_service.py` | Historical data access (cached Alpaca data) |
| `position_vitals.py` | Health and efficiency scoring (0-100) |
| `volatility_metrics.py` | ATR computation + regime classification |
| `capital_lock_in.py` | Dead capital detection |
| `concentration_guard.py` | Sector exposure monitoring |
| `news_scorer.py` | Keyword-based sentiment scoring |
| `sector_confidence.py` | Volatility + news → confidence |
| `opportunity_logic.py` | Weak vs. strong position comparison |
| `decision_engine.py` | Core orchestrator |
| `decision_explainer.py` | Human-readable explanations |
| `risk_guardrails.py` | Safety filtering |
| `execution_planner.py` | Action sequencing |
| `broker/alpaca_adapter.py` | READ-ONLY Alpaca client |
| `broker/mock_adapter.py` | Mock data generator |
| `demo/demo_profiles.py` | Hardcoded demo scenarios |
| `demo/trend_overlays.py` | Signal modifiers |
| `backend/app.py` | Flask REST API |
| `backend/api_routes.py` | REST endpoint definitions |
| `backend/scenarios.py` | Behavioral demo scenarios |
| `tests/test_system.py` | Comprehensive test suite |

---

## 📁 File Structure

```
.
├── full_system_demo.py        # CLI entry point
├── decision_engine.py         # Phase 3: Decision synthesis
├── risk_guardrails.py         # Phase 4: Safety gates
├── execution_planner.py       # Phase 5: Advisory planning
│
├── data_router.py             # Market-aware data routing
├── market_mode.py             # Market status detection
├── market_aware_runner.py     # Unified analysis runner
├── historical_data_service.py # Historical data access
│
├── volatility_metrics.py      # Phase 2: Volatility signals
├── news_scorer.py             # Phase 2: News sentiment
├── sector_confidence.py       # Phase 2: Confidence scoring
│
├── position_vitals.py         # Position health scoring
├── concentration_guard.py     # Concentration detection
├── capital_lock_in.py         # Capital efficiency
├── opportunity_logic.py       # Candidate evaluation
│
├── broker/
│   ├── alpaca_adapter.py      # READ-ONLY Alpaca client
│   └── mock_adapter.py        # Mock data generator
│
├── demo/
│   ├── demo_profiles.py       # Hardcoded portfolio profiles
│   └── trend_overlays.py      # Signal modifiers for demos
│
├── backend/
│   ├── app.py                 # Flask server
│   ├── api_routes.py          # REST endpoints
│   ├── scenarios.py           # Behavioral demo scenarios
│   └── market_status.py       # Market status helper
│
├── historical_cache/          # Cached Alpaca historical data
│   ├── SPY_*.json
│   ├── QQQ_*.json
│   └── IWM_*.json
│
├── tests/
│   ├── test_system.py         # Comprehensive test suite
│   ├── test_historical_mode.py
│   └── test_live_mode.py
│
├── validation/                # Validation utilities
│   ├── data_manager.py
│   ├── metrics.py
│   ├── replay.py
│   └── runner.py
│
├── index.html                 # Frontend dashboard
├── script.js                  # Frontend logic
├── styles.css                 # Frontend styling
│
├── render.yaml                # Cloud deployment config
├── Procfile                   # Heroku/Render process file
│
└── archive/                   # Deprecated files (reference only)
```

---

## 🚫 What This System Does NOT Do

- ❌ **No Order Execution** — Intentionally disabled
- ❌ **No Price Prediction** — Manages risk, not forecasts
- ❌ **No Black Box ML** — All logic is rule-based and explainable
- ❌ **No High-Frequency Trading** — Portfolio management, not scalping
- ❌ **No Live Trading** — Paper trading only
- ❌ **No LLM/AI Models** — Uses keyword-based sentiment, not neural networks

---

## 🛠️ Development Process

This system was built with **engineering maturity**:

1. **Mock First** — Validated logic with synthetic data before API integration
2. **Phased Intelligence** — Built independent signal layers
3. **Safety Integrated** — Added guardrails as first-class citizens
4. **Explainability** — Retrofitted all logic to explain itself
5. **Market-Aware Routing** — Added automatic LIVE/HISTORICAL switching
6. **Hardening** — Added demo profiles, scenarios, and regression tests

---



## 👀 For Judges

**What to look for:**

1. **Run the backend + open frontend** — See market-aware controls
2. **Select different symbols and time ranges** — Observe data source transparency
3. **Try behavioral scenarios** — See specific agent intelligence demonstrated
4. **Toggle Crash Simulation** — Watch defensive posture activate
5. **Check the Brain Log** — Real-time reasoning visibility
6. **Review decision reasons** — Each action is explained

**What this proves:**

- The system can reason about portfolio risk
- Safety is a first-class concern
- Decisions are explainable and auditable
- Market-awareness provides flexibility for demos
- The architecture is clean and maintainable

---

## 📚 Additional Documentation

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — Data contracts & module dependencies
- Inline docstrings in all modules
- Runnable tests: `python3 tests/test_system.py`

---

## 🧭 Design Principles

- Capital is finite — idle capital is hidden risk
- Portfolio management > price prediction
- Explainability > black-box models
- Safety > aggressiveness
- Deterministic logic over ML heuristics

> **This system manages the present — it does not predict the future.**

---

## ⚠️ Known Limitations

| Limitation | Reason |
|:-----------|:-------|
| Historical data limited to SPY, QQQ, IWM | Cached subset for demo purposes |
| No real-time news API | Uses keyword-based scoring on mock headlines |
| Sector inference is simplified | Basic symbol-to-sector mapping |
| No portfolio persistence | Each session starts fresh |

---



---

_Last updated: 2026-02-01_

_© 2026 BuriBuri Trading Team_