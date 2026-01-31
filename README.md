# BuriBuri_Trading

## Continuous Decision-Making for Risk-Aware Trading

_(Disclaimer: Do not try with real assets)_

### Problem

Stock trading is often treated as a sequence of isolated buy and sell decisions. Once a position is opened, many systems stop reasoning until a fixed exit condition is reached. In reality, market prices move continuously, risk levels change, capital may get locked, and new opportunities appear while existing positions are still active. Decisions made too late or based on static rules lead to overexposure, emotional exits, missed rotations, and idle capital that drags down overall portfolio performance.

### Background (Trader Reality)

For traders and portfolio managers, the challenge is not just picking entries, but managing positions over time. A profitable trade can quickly turn risky due to market volatility, news, or broader trends. Capital tied up in one stock can prevent participation in better opportunities elsewhere. Handling multiple positions while respecting risk limits, capital availability, and changing conditions is extremely difficult manually or with rigid rule-based systems.

### What We Expect

We expect teams to design an agentic system that actively manages open positions as market conditions and risk profiles evolve over time.
The system should:

- Continuously assess risk, capital, and potential returns for open positions
- Recommend actions like holding, reducing, exiting, or reallocating capital as new opportunities arise
- Manage multiple positions together to balance risk and maximize long-term portfolio performance.

Focus is on reasoning and adaptability, not fixed strategies, single indicators, or simple buy/sell bots.

### How to Start (Suggested Features)

Teams may begin with a small set of core ideas, such as:

- Tracking open positions and estimating their current risk and potential return
- Deciding whether to hold, reduce, exit, or reallocate capital as new opportunities emerge
- Managing capital and risk across multiple positions rather than treating each trade independently

These are starting points only. Teams are encouraged to expand, refine, or rethink the approach to better reflect real trading behavior.

## Team Members

1. Nishtha Vadhwani - Team leader
2. Akash Anand - Tech lead
3. Mohit Ray - UI/UX
4. Dev Jaiswal - Reviewer/Tester

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd BuriBuri_Trading
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Set API Key

Get your free API key from: **<https://polygon.io/>**

#### For Current Terminal Session

```bash
export POLYGON_API_KEY='your_api_key_here'
```

#### For Permanent Setup (Recommended)

Add to your `~/.zshrc` file:

```bash
echo 'export POLYGON_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Test the API Integration

```bash
python3 opportunity_scanner.py
```

You should see:

```
Success! Fetched X candles
```

---

## 🌐 Deployment (Heroku, Railway, Render, AWS, etc.)

1. Push your code to GitHub
2. In your hosting platform's dashboard, add environment variable:
   - **Key**: `POLYGON_API_KEY`
   - **Value**: `your_actual_api_key`
3. Deploy

The code reads from `os.environ.get("POLYGON_API_KEY")` automatically.

---

## 📦 Core Modules

### 1. Vitals Monitor (`vitals_monitor.py`)

Computes a **Vitals Score (0-100)** for each position based on:

- Volatility-adjusted returns
- Capital efficiency
- Time decay penalty

**Output**: Position health (HEALTHY / WEAK / UNHEALTHY)

### 2. Concentration Guard (`concentration_guard.py`)

Detects capital over-exposure to any single sector.

**Output**: Sector exposure map + risk warnings (OK / APPROACHING / SOFT_BREACH)

### 3. Opportunity Scanner (`opportunity_scanner.py`)

- Fetches real-time market data (XLK - Technology Sector ETF)
- Compares portfolio positions vs. market candidates
- Identifies efficiency upgrade opportunities

---

## Phase 2 — Signal Layer (No Decisions Yet)

This phase introduces market signals to assist in monitoring, but **no trading decisions are made in Phase 2.** All signals are descriptive and designed to provide context for future decision-making stages.

### 1. ATR (Average True Range)

ATR measures how much an asset's price typically moves in a given period. It is a pure volatility metric.

- **Purpose**: Helps quantify "normal" movement vs. "abnormal" movement.
- **Usage**: A higher ATR signals higher recent volatility. It is **not** a buy or sell signal.

### 2. Volatility State

Derived from ATR and price structure, this classifies the current market environment into simple states:

- **LOW**: Calm market, standard risks apply.
- **MODERATE**: Normalizing volatility, standard caution.
- **HIGH**: Elevated uncertainty, higher risk awareness required.
- **Status**: Used strictly for risk awareness, not for timing entries or exits.

### 3. News Score

A high-level numeric representation (0–100) of news sentiment for a specific sector.

- **50**: Neutral (no significant news or mixed signals).
- **>50**: Positive sentiment (growth, demand, upgrades).
- **<50**: Negative sentiment (slowdown, risks, warnings).
- **Status**: Descriptive only. A low score does **not** trigger an automatic exit, and a high score does **not** trigger an automatic entry.
