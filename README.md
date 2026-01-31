# BuriBuri Trading: Portfolio Intelligence System

> **An explainable, risk-aware portfolio intelligence system that manages capital instead of predicting prices.**

---

## 🚀 Key Capabilities

- **Portfolio-First Intelligence:** Optimizes entire portfolios, not single trades.
- **Fail-Safe Architecture:** Five-phase pipeline with strict isolation and guardrails.
- **Human-Readable Explainability:** Every decision comes with clear reasons.
- **Safety Over Aggression:** Built-in safeguards against concentration and volatility.
- **Demo-Ready Resilience:** Runs deterministically even when markets are closed.

---

## 🧠 System Philosophy

Most trading bots fail because they optimize for **price prediction** rather than **portfolio resilience**.

We built this system on different principles:

1. **Safety First:** Capital preservation is more important than growth.
2. **Explainability:** If the system can't explain why, it shouldn't act.
3. **No Forced Action:** "Doing nothing" is often the best financial decision.
4. **Guardrails:** Hard limits on risk that cannot be bypassed.

> **Note:** This system is an **advisor**. It generates high-fidelity recommendations but intentionally disables execution.

---

## 🏗️ High-Level Architecture

The system operates as a **unidirectional pipeline** with five distinct phases:

```
┌────────────┐    ┌────────────┐    ┌────────────┐
│  PHASE 1   │───▶│  PHASE 2   │───▶│  PHASE 3   │
│  INGEST    │    │  SIGNALS   │    │  DECISIONS │
└────────────┘    └────────────┘    └────────────┘
      │                 │                 │
      ▼                 ▼                 ▼
┌────────────┐    ┌────────────┐    ┌────────────┐
│ Portfolio  │    │ Volatility │    │  Actions   │
│ Positions  │    │ News Score │    │ + Reasons  │
│ Candidates │    │ Confidence │    │            │
└────────────┘    └────────────┘    └────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────┐
                        │   PHASE 4: RISK GUARDRAILS  │
                        │   (Concentration, Cash,     │
                        │    Volatility Guards)       │
                        └─────────────────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────┐
                        │  PHASE 5: EXECUTION PLAN    │
                        │  (Advisory Only - No Exec)  │
                        └─────────────────────────────┘
```

1. **Ingestion:** Fetches data from Alpaca (paper) or Demo profiles.
2. **Signals:** Computes volatility state, news sentiment, and sector confidence.
3. **Decisions:** Synthesizes signals into portfolio actions (HOLD, TRIM, ALLOCATE).
4. **Guardrails:** Validates actions against safety rules (blocks risky moves).
5. **Planning:** Orders safe actions into a coherent execution plan.

---

## 📊 Data Sources & Operating Modes

The system adapts to available data sources while maintaining strict safety.

| Mode | `DEMO_MODE` | `USE_ALPACA` | Source | Market Data | Execution |
|------|-------------|--------------|--------|-------------|-----------|
| **DEMO** | `true` | ignored | Hardcoded | Simulated | ❌ Disabled |
| **ALPACA** | `false` | `true` | Alpaca Paper | Real | ❌ Disabled |
| **MOCK** | `false` | `false` | Mock | Simulated | ❌ Disabled |

### Security Note

- **Alpaca Integration is READ-ONLY.**
- Only `https://paper-api.alpaca.markets` is allowed.
- No write permissions, no order submission capabilities.

---

## 🧪 Demo Portfolio Profiles

Since live markets may be closed or uninteresting during a demo, we include **deterministic profiles** to showcase specific system intelligences.

| Profile | Situation | System Response |
|---------|-----------|-----------------|
| **BALANCED_TECH** | Healthy, diversified portfolio | **MAINTAIN** structure, minor rebalancing. |
| **OVERCONCENTRATED_TECH** | 82% allocation in Tech sector | **TRIM_RISK** on winners, block new Tech buys. |
| **LOSING_PORTFOLIO** | Multiple losing positions | **RISK_OFF** posture, halt buying, preserve cash. |
| **ROTATION_SCENARIO** | Tech cooling, Energy rising | **FREE_CAPITAL** form Tech, allocate to Energy. |
| **CASH_HEAVY** | 40% idle cash, weak signals | **WAIT** (inaction), rejecting mediocre trades. |

---

## 📝 Decision Explainability

Every decision produced by the system includes human-readable reasoning.

**Example Output:**

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

This ensures that a human operator can always understand **why** a recommendation was made.

---

## 🛡️ Risk & Safety Guardrails

Safety rules are applied **after** decisions are made but **before** any plan is finalized.

1. **Sector Concentration Cap:** No sector may exceed 60% of total equity.
2. **Cash Reserve Floor:** System fights to maintain 5-10% liquid cash.
3. **Volatility Gate:** Aggressive buying is blocked during expanding volatility.
4. **Loss Prevention:** Positions monitored for specific degradation patterns.

> **Rule:** Safety always overrides aggressiveness. A profitable trade will be blocked if it violates safety rules.

---

## 💻 How to Run

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Demo Mode (Recommended)

Runs the full pipeline using a pre-built profile. Best for judges.

```bash
python3 full_system_demo.py
```

### 3. Change Profile & Trend

Test adaptability by injecting different scenarios:

```bash
# Test rotation logic
DEMO_PROFILE=ROTATION_SCENARIO DEMO_TREND=TECH_COOLING python3 full_system_demo.py

# Test defensive logic
DEMO_PROFILE=LOSING_PORTFOLIO DEMO_TREND=VOLATILITY_SHOCK python3 full_system_demo.py
```

### 4. Run Backend API

Start the Flask server for the frontend UI:

```bash
python backend/app.py
```

> API available at `http://localhost:5000/run`

### 5. Run Test Suite

Validate system integrity:

```bash
python3 tests/test_system.py
```

---

## 🔑 Environment Variables

Create a `.env` file (not committed) for local config:

```ini
# Alpaca Paper Trading (Optional)
ALPACA_API_KEY=PK******************
ALPACA_SECRET_KEY=********************************
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Polygon.io (Optional - for Phase 1 data)
POLYGON_API_KEY=********************************
```

---

## 🚫 What This System Does NOT Do

To build trust, we are explicit about limitations:

- ❌ **No Order Execution:** It does not place trades.
- ❌ **No Price Prediction:** It does not forecast "price targets".
- ❌ **No Black Box ML:** All logic is rule-based and explainable.
- ❌ **No High-Frequency Trading:** It is for portfolio management, not scalping.
- ❌ **No Live Money:** It is strictly for paper trading and simulation.

---

## 🛠️ Development Process

This system was built with **engineering maturity**:

1. **Mock First:** Validated logic with synthetic data before API integration.
2. **Phased Intelligence:** Built independent signal layers (Volatility → Confidence → Decision).
3. **Safety Integrated:** Added guardrails as a first-class citizen, not an afterthought.
4. **Explainability:** Retrofitted all logic to explain itself.
5. **Hardening:** Added demo profiles and regression tests to ensure stability.

---

## 👥 Audience

- **Hackathon Judges:** Demonstrates completed, working, defensible architecture.
- **Portfolio Managers:** Shows how AI can augment (not replace) human decision-making.
- **Researchers:** Framework for testing risk management strategies.

---

*© 2026 Quantitative Portfolio Engineering Team*
