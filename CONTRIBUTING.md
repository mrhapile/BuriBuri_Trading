# Contributing to BuriBuri Trading

Thank you for your interest in contributing to BuriBuri Trading! This guide will help you get started.

## Table of Contents

1. [Introduction](#introduction)
2. [How to Fork and Clone](#how-to-fork-and-clone)
3. [Branch Naming Conventions](#branch-naming-conventions)
4. [Running the Project Locally](#running-the-project-locally)
5. [Running Tests](#running-tests)
6. [Code Style & Expectations](#code-style--expectations)
7. [Submitting a Pull Request](#submitting-a-pull-request)

---

## Introduction

BuriBuri Trading is an AI-powered portfolio intelligence system that provides advisory recommendations (no real trades are executed). We welcome contributions of all kinds:

- 🐛 Bug fixes
- 📖 Documentation improvements
- ✨ New features
- 🧪 Test coverage improvements
- 🎨 UI/UX enhancements

This is a hackathon project, so we value clarity and working code over perfection. Don't hesitate to ask questions!

---

## How to Fork and Clone

### Step 1: Fork the Repository

1. Go to [https://github.com/mrhapile/BuriBuri_Trading](https://github.com/mrhapile/BuriBuri_Trading)
2. Click the **Fork** button in the top-right corner
3. This creates a copy of the repo under your GitHub account

### Step 2: Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/BuriBuri_Trading.git
cd BuriBuri_Trading
```

### Step 3: Add the Upstream Remote

```bash
git remote add upstream https://github.com/mrhapile/BuriBuri_Trading.git
```

This lets you sync your fork with the original repository.

### Step 4: Keep Your Fork Updated

Before starting new work, sync with upstream:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Branch Naming Conventions

Use clear, descriptive branch names. This helps reviewers understand your changes at a glance.

### Format

```
<type>/<short-description>
```

### Types

| Type | Use For | Example |
|:-----|:--------|:--------|
| `feature/` | New features | `feature/add-crypto-support` |
| `fix/` | Bug fixes | `fix/calculation-error` |
| `docs/` | Documentation changes | `docs/update-readme` |
| `refactor/` | Code refactoring | `refactor/decision-engine` |
| `test/` | Test additions/fixes | `test/add-unit-tests` |

### Examples

```bash
# Good branch names
git checkout -b feature/sector-heatmap
git checkout -b fix/volatility-calculation
git checkout -b docs/api-reference
git checkout -b fix/issue-42

# Avoid
git checkout -b my-changes        # Too vague
git checkout -b update            # Not descriptive
git checkout -b john-work         # Personal names
```

### Why This Matters

- Clear names speed up code review
- Makes git history easier to navigate
- Helps identify related commits when debugging

---

## Running the Project Locally

### Prerequisites

- **Python 3.8+** (3.11 recommended, 3.12 also works)
- **pip** (comes with Python)
- A web browser

### Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 2: Start the Backend

```bash
python3 backend/app.py
```

You should see:
```
============================================================
Portfolio Intelligence System - Backend API
============================================================
Binding to: 0.0.0.0:10000
```

### Step 3: Start the Frontend

Open a **new terminal** in the project folder:

```bash
python3 -m http.server 8080
```

### Step 4: Open in Browser

Go to: **http://localhost:8080**

Click **"Run Analysis"** to verify everything works.

> 📖 For full deployment instructions, see [`DEPLOYMENT.md`](./DEPLOYMENT.md)

---

## Running Tests

### Test Suite

The project has a comprehensive test suite in the `tests/` directory:

```
tests/
├── test_system.py          # Main test suite (imports, modes, signals)
├── test_historical_mode.py # Historical data mode tests
└── test_live_mode.py       # Live data mode tests (requires Alpaca credentials)
```

### Running All Tests

```bash
python3 tests/test_system.py
```

Expected output:
```
============================================================
  🧪 PORTFOLIO INTELLIGENCE SYSTEM - TEST SUITE
============================================================

  ✅ PASS | import volatility_metrics
  ✅ PASS | import news_scorer
  ...

  Total: 5/5 test groups passed

  🎉 ALL TESTS PASSED - System is judge-ready!
```

### Running Individual Test Files

```bash
# Historical mode tests
python3 tests/test_historical_mode.py

# Live mode tests (requires ALPACA_API_KEY)
python3 tests/test_live_mode.py
```

### Before Submitting a PR

Always run the full test suite:

```bash
python3 tests/test_system.py
```

If any tests fail, fix them before submitting your PR.

---

## Code Style & Expectations

### Python Version

- **Minimum:** Python 3.8
- **Recommended:** Python 3.11+
- The project uses no version-specific syntax, so all modern Python versions work.

### Code Style

We follow **PEP 8** with some flexibility for readability:

| Rule | Example |
|:-----|:--------|
| 4-space indentation | `    if condition:` |
| snake_case for functions/variables | `compute_atr()`, `sector_heatmap` |
| PascalCase for classes | `DataRouter`, `AlpacaAdapter` |
| UPPER_SNAKE_CASE for constants | `DATA_MODE_LIVE`, `DEFAULT_PORT` |

### Type Hints

We use type hints for function signatures. Please follow this pattern:

```python
from typing import List, Dict, Optional

def compute_atr(candles: List[Dict], period: int = 14) -> Dict[str, Optional[float]]:
    """
    Computes Average True Range (ATR).
    
    Args:
        candles: List of OHLCV candle dictionaries.
        period: Lookback period (default 14).
        
    Returns:
        Dictionary with 'atr' key.
    """
    ...
```

### Docstrings

Use docstrings for all public functions:

```python
def my_function(param: str) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param: Description of the parameter.
        
    Returns:
        Description of return value.
    """
```

### File Structure

Each Python module should have:

1. **Module docstring** at the top explaining its purpose
2. **Imports** organized (stdlib, third-party, local)
3. **Constants** in UPPER_SNAKE_CASE
4. **Classes/Functions** with docstrings
5. **`if __name__ == "__main__":`** block for testing

### What We Value

- ✅ **Readable code** over clever code
- ✅ **Clear variable names** (`sector_heatmap` not `sh`)
- ✅ **Defensive programming** (handle edge cases)
- ✅ **Comments explaining "why"** not just "what"
- ✅ **Small, focused commits**

---

## Submitting a Pull Request

### Before You Submit

1. ✅ Your code runs without errors
2. ✅ Tests pass: `python3 tests/test_system.py`
3. ✅ Your branch is up-to-date with `main`
4. ✅ Commits are small and focused
5. ✅ Code follows the style guide

### Step 1: Push Your Branch

```bash
git push origin feature/your-feature-name
```

### Step 2: Create the Pull Request

1. Go to your fork on GitHub
2. Click **"Compare & pull request"**
3. Fill out the PR template

### PR Title Format

Use a clear, descriptive title:

```
✅ Good:
- Add sector concentration visualization
- Fix ATR calculation for empty candles
- Update API documentation

❌ Avoid:
- Fixed stuff
- Updates
- WIP
```

### PR Description Template

```markdown
## What does this PR do?

Brief description of your changes.

## Related Issue

Fixes #42 (if applicable)

## Changes Made

- Added X functionality
- Fixed Y bug
- Updated Z documentation

## Testing

- [ ] Ran `python3 tests/test_system.py`
- [ ] Tested manually in browser
- [ ] Added new tests (if applicable)

## Screenshots (if UI changes)

(Add screenshots here)
```

### Linking Issues

If your PR fixes an issue, include this in the description:

```
Fixes #42
```

This automatically closes the issue when the PR is merged.

### After Submitting

- Respond to review feedback promptly
- Make requested changes in new commits
- Don't force-push unless asked

---

## Questions?

- Check the existing documentation:
  - [`README.md`](./README.md) — Project overview
  - [`DEPLOYMENT.md`](./DEPLOYMENT.md) — Setup and deployment
  - [`ARCHITECTURE.md`](./ARCHITECTURE.md) — System design
- Open an issue on GitHub if you're stuck

We're happy to help! 🎉
