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

## Implemented Solution (MVP)

The current repository contains a fully working **Advisory Portfolio Pilot** that demonstrates agentic reasoning for capital allocation. It is not a trading bot (it does not execute trades), but rather a deterministic decision engine that monitors portfolio health and suggests actions.

### 1. Key Logic Modules

The system is composed of five specialized, independent logic modules:

- **Portfolio Vitals Monitor** (`vitals_monitor.py`)
  - **Purpose:** acts as the "health check" for individual positions.
  - **Logic:** Calculates a `Vitals Score` (0-100) based on volatility-adjusted returns, capital efficiency, and time decay (penalizing stagnation).
  - **Output:** Classifies positions as `HEALTHY`, `WEAK`, or `UNHEALTHY`.

- **Capital Lock-in Detector** (`capital_lock_in.py`)
  - **Purpose:** Identifies "Zombie Positions"—capital trapped in low-performing assets within cold sectors.
  - **Logic:** Cross-references Vitals Scores with a Sector Heatmap. If a position is weak AND the sector is cold, it is flagged as `Dead Capital`.
  - **Output:** Triggers a `REALLOCATION REQUIRED` alert if dead capital exceeds a pressure threshold.

- **Sector Concentration Guard** (`concentration_guard.py`)
  - **Purpose:** Managing risk by preventing over-exposure to a single sector.
  - **Logic:** Calculates the % of total capital in each sector.
  - **Output:** distinct warnings: `APPROACHING` (warning limit) or `SOFT_BREACH` (soft limit). _Note: This is advisory only._

- **Opportunity Scanner** (`opportunity_scanner.py`)
  - **Purpose:** Finds better uses for capital.
  - **Logic:** Compares the portfolio's "weakest link" (lowest vitals) against external market candidates (projected efficiency).
  - **Output:** Recommends a swap only if the `Efficiency Gap` > Threshold (e.g., +15 points).

- **Decision Orchestration** (`decision_engine.py`)
  - **Purpose:** The central brain that synthesizes all signals.
  - **Logic:** Runs the Vitals Monitor -> Checks Lock-ins -> Scans Opportunities -> Formulates a final Plan.
  - **Output:** A structured list of human-readable decisions (e.g., `OLD_BANK → REDUCE`).

### 2. How it Works (Flow Overview)

The system operates in discrete time steps (e.g., T0, T1, T2) to simulate evolving market conditions.

1.  **Ingest State:** Reads current portfolio holdings and market heatmaps.
2.  **Analyze Health:** Every position is scored for efficiency.
3.  **Check Constraints:** Guards check for concentration risks or dead capital.
4.  **Synthesize Advice:** The engine generates specific actions for each asset.
    - _Stable?_ → `MAINTAIN`
    - _Stagnant?_ → `REVIEW`
    - _Critical Decay?_ → `REDUCE` / `FREE_CAPITAL`
    - _Opportunity?_ → `ALLOCATE`

### 3. Current System Output

The system produces clean, CLI-based text tailored for human decision-makers. It avoids technical jargon in favor of clear reasoning.

**Example Output:**

```text
[11:00 AM | T0]
OLD_BANK → HOLD
Reason: Capital still productive

[11:05 AM | T1]
OLD_BANK → REDUCE
Reason: Low efficiency, cold sector

Portfolio Alert → REALLOCATION REQUIRED
```

## Team Members

1. Nishtha Vadhwani - Team leader
2. Akash Anand - Tech lead
3. Mohit Ray - UI/UX
4. Dev Jaiswal - Reviewer/Tester
