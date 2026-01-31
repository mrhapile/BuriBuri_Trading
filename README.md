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
