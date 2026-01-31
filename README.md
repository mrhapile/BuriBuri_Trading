# 🐻📈 BuriBuri Trading

**An Explainable, Risk-Aware Portfolio Decision Engine**

> Continuous decision-making for risk-aware portfolio management.  
> _(Hackathon Prototype — Do not use with real assets.)_

---

## 📊 Project Status

| Phase | Description | Status |
|:------|:------------|:------:|
| Phase 1 | Data ingestion (Alpaca / Demo) | ✅ Complete |
| Phase 2 | Signal computation | ✅ Complete |
| Phase 3 | Decision engine | ✅ Complete |
| Phase 4 | Risk guardrails | ✅ Complete |
| Phase 5 | Execution planning (Advisory) | ✅ Complete |
| Phase 6 | Frontend dashboard | ✅ Complete |
| Phase 7 | Trade execution | ❌ Disabled (by design) |

**Completion:** ~85% — Full decision pipeline is functional.  
**Note:** Execution is intentionally disabled. This system produces *advisory decisions*, not trades.

---

## 🧠 Problem Statement

Traditional trading systems treat positions as isolated events. Once opened, they stop reasoning until a fixed exit is hit.

In reality:
- Capital gets stuck in stagnant trades  
- Risk accumulates silently (volatility, concentration)  
- Better opportunities appear while capital is locked  

**BuriBuri Trading** addresses this by treating capital as a resource that must *continuously justify its allocation*.

---

## 🎯 System Philosophy

| Principle | Meaning |
|:----------|:--------|
| **Portfolio-first** | Optimizes entire portfolios, not single trades |
| **Safety > Aggressiveness** | Capital preservation is more important than growth |
| **Explainability** | Every decision has human-readable reasons |
| **No Forced Action** | "Doing nothing" is often the best decision |
| **Transparency** | Demo behavior is always clearly labeled |

> **This system is an advisor.** It generates high-fidelity recommendations but intentionally disables execution.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PORTFOLIO INTELLIGENCE SYSTEM                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│   │  PHASE 1   │───▶│  PHASE 2   │───▶│  PHASE 3   │            │
│   │  INGEST    │    │  SIGNALS   │    │  DECISIONS │            │
│   └────────────┘    └────────────┘    └────────────┘            │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│   │ Portfolio  │    │ Volatility │    │  Actions   │            │
│   │ Positions  │    │ News Score │    │ + Reasons  │            │
│   │ Candidates │    │ Confidence │    │            │            │
│   └────────────┘    └────────────┘    └────────────┘            │
│                                              │                    │
│                                              ▼                    │
│                         ┌─────────────────────────────┐          │
│                         │   PHASE 4: RISK GUARDRAILS  │          │
│                         │   (Concentration, Cash,     │          │
│                         │    Volatility Guards)       │          │
│                         └─────────────────────────────┘          │
│                                              │                    │
│                                              ▼                    │
│                         ┌─────────────────────────────┐          │
│                         │  PHASE 5: EXECUTION PLAN    │          │
│                         │  (Advisory Only - No Exec)  │          │
│                         └─────────────────────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Breakdown

| Phase | Module(s) | Input | Output |
|:------|:----------|:------|:-------|
| **Phase 1** | `broker/*.py`, `demo/demo_profiles.py` | API credentials, profile name | Portfolio, positions, candidates |
| **Phase 2** | `volatility_metrics.py`, `news_scorer.py`, `sector_confidence.py` | Candles, headlines | ATR, volatility state, news score, confidence |
| **Phase 3** | `decision_engine.py`, `position_vitals.py`, `concentration_guard.py` | Signals + positions | Proposed actions with reasons |
| **Phase 4** | `risk_guardrails.py` | Proposed actions + context | Allowed vs blocked actions |
| **Phase 5** | `execution_planner.py`, `execution_summary.py` | Safe actions | Sequential plan (advisory) |

---

## 📊 Data Sources & Operating Modes

| Mode | `DEMO_MODE` | `USE_ALPACA` | Source | Market Data | Execution |
|:-----|:-----------:|:------------:|:-------|:------------|:---------:|
| **DEMO** | `true` | ignored | Hardcoded profiles | Simulated | ❌ Disabled |
| **ALPACA** | `false` | `true` | Alpaca Paper API | Real | ❌ Disabled |
| **MOCK** | `false` | `false` | Mock adapter | Simulated | ❌ Disabled |

### Security Note

- **Alpaca Integration is READ-ONLY**
- Only paper trading URL allowed (`https://paper-api.alpaca.markets`)
- Credentials from environment variables only
- No write operations, no order submission

---

## 🧪 Demo Profiles

Since live markets may be closed during a demo, we include **deterministic profiles** to showcase specific system intelligence:

| Profile | Capital | Scenario | Expected Response |
|:--------|:--------|:---------|:------------------|
| `BALANCED_TECH` | $500k | Healthy, diversified | MAINTAIN structure |
| `OVERCONCENTRATED_TECH` | $1M | 82% in TECH | TRIM_RISK, block new TECH |
| `LOSING_PORTFOLIO` | $750k | Multiple losers | RISK_OFF posture |
| `ROTATION_SCENARIO` | $800k | TECH cooling, ENERGY rising | FREE_CAPITAL → reallocate |
| `CASH_HEAVY` | $500k | 40% idle cash | WAIT (reject weak trades) |

### Key Insight

Each profile answers a question:
- **OVERCONCENTRATED_TECH** → Can the system recognize concentration risk?
- **LOSING_PORTFOLIO** → Can the system protect capital during losses?
- **ROTATION_SCENARIO** → Can the system identify sector rotation?
- **CASH_HEAVY** → Can the system resist deploying capital when conditions don't justify it?

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
| Alpaca integration | ✅ | READ-ONLY paper trading |
| Backend API | ✅ | Flask REST endpoint |
| Frontend dashboard | ✅ | Full UI with animations |
| Unit tests | ✅ | Comprehensive test suite |
| Broker execution | ❌ | Intentionally disabled |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/mrhapile/BuriBuri_Trading.git
cd BuriBuri_Trading
pip3 install -r requirements.txt
```

### 2. Run Demo (Recommended for Judges)

```bash
python3 full_system_demo.py
```

Runs with **demo profiles** — deterministic, no API key required.

### 3. Test Different Scenarios

```bash
# Default: Over-concentrated portfolio
python3 full_system_demo.py

# Losing portfolio with volatility shock
DEMO_PROFILE=LOSING_PORTFOLIO DEMO_TREND=VOLATILITY_SHOCK python3 full_system_demo.py

# Sector rotation scenario
DEMO_PROFILE=ROTATION_SCENARIO DEMO_TREND=TECH_COOLING python3 full_system_demo.py

# Cash-heavy portfolio
DEMO_PROFILE=CASH_HEAVY python3 full_system_demo.py
```

### 4. Run Backend API

```bash
python3 backend/app.py
```

API available at `http://localhost:5000/run`

### 5. Run Test Suite

```bash
python3 tests/test_system.py
```

---

## 🔑 Environment Variables

Create a `.env` file (see `.env.example`):

```ini
# Alpaca Paper Trading (Optional)
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Demo Mode Configuration
DEMO_MODE=true
DEMO_PROFILE=OVERCONCENTRATED_TECH
DEMO_TREND=NEUTRAL
```

---

## 📦 Core Modules

| Module | Purpose |
|:-------|:--------|
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
| `tests/test_system.py` | Comprehensive test suite |

---

## 📁 File Structure

```
.
├── full_system_demo.py     # Main entry point
├── decision_engine.py      # Phase 3: Decision synthesis
├── risk_guardrails.py      # Phase 4: Safety gates
├── execution_planner.py    # Phase 5: Advisory planning
│
├── volatility_metrics.py   # Phase 2: Volatility signals
├── news_scorer.py          # Phase 2: News sentiment
├── sector_confidence.py    # Phase 2: Confidence scoring
│
├── position_vitals.py      # Position health scoring
├── concentration_guard.py  # Concentration detection
├── capital_lock_in.py      # Capital efficiency
├── opportunity_logic.py    # Candidate evaluation
│
├── broker/
│   ├── alpaca_adapter.py   # READ-ONLY Alpaca client
│   └── mock_adapter.py     # Mock data generator
│
├── demo/
│   ├── demo_profiles.py    # Hardcoded portfolio profiles
│   └── trend_overlays.py   # Signal modifiers for demos
│
├── backend/
│   ├── app.py              # Flask server
│   └── api_routes.py       # REST endpoints
│
├── tests/
│   └── test_system.py      # Comprehensive test suite
│
├── index.html              # Frontend dashboard
├── script.js               # Frontend logic
├── styles.css              # Frontend styling
│
└── archive/                # Deprecated files (reference only)
```

---

## 🚫 What This System Does NOT Do

- ❌ **No Order Execution** — Intentionally disabled
- ❌ **No Price Prediction** — Manages risk, not forecasts
- ❌ **No Black Box ML** — All logic is rule-based and explainable
- ❌ **No High-Frequency Trading** — Portfolio management, not scalping
- ❌ **No Live Trading** — Paper trading only

---

## 🛠️ Development Process

This system was built with **engineering maturity**:

1. **Mock First** — Validated logic with synthetic data before API integration
2. **Phased Intelligence** — Built independent signal layers
3. **Safety Integrated** — Added guardrails as first-class citizens
4. **Explainability** — Retrofitted all logic to explain itself
5. **Hardening** — Added demo profiles and regression tests

---

## 👥 Team

| Name | Role |
|:-----|:-----|
| Nishtha Vadhwani | Team Lead |
| Akash Anand | Tech Lead |
| Mohit Ray | UI/UX |
| Dev Jaiswal | Reviewer / Tester |

---

## 👀 For Judges

**What to look for:**

1. **Run the default demo** — Observe concentration alerts and TRIM recommendations
2. **Try LOSING_PORTFOLIO** — See RISK_OFF posture activate
3. **Check the RUN CONFIGURATION block** — Notice the transparency
4. **Review decision reasons** — Each action is explained
5. **Note what's NOT happening** — No orders, no predictions, no magic

**What this proves:**

- The system can reason about portfolio risk
- Safety is a first-class concern
- Decisions are explainable and auditable
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

_Last updated: 2026-02-01_

_© 2026 BuriBuri Trading Team_