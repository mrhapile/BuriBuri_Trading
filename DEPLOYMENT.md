# 🚀 Deployment Guide

**BuriBuri Trading — Portfolio Intelligence System**

---

## ⚡ Quick Start (Copy-Paste)

**Run everything locally in 60 seconds:**

```bash
# Clone and setup
git clone https://github.com/mrhapile/BuriBuri_Trading.git
cd BuriBuri_Trading
pip3 install -r requirements.txt

# Start backend (keep this terminal open)
python3 backend/app.py
```

Open a **new terminal** in the same folder:

```bash
# Start frontend (from BuriBuri_Trading folder)
python3 -m http.server 8080
```

**Open in browser:** http://localhost:8080

✅ **Done!** Click "Run Analysis" to see it work.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start-copy-paste)
2. [What Gets Deployed](#what-gets-deployed)
3. [Local Development (Detailed)](#local-development-detailed)
4. [Deploy to Render (Cloud)](#deploy-to-render-cloud)
5. [Configuration Files](#configuration-files)
6. [Environment Variables](#environment-variables)
7. [API Reference](#api-reference)
8. [Running Tests](#running-tests)
9. [Troubleshooting](#troubleshooting)
10. [Limitations](#limitations)

---

## What Gets Deployed

| Component | What it is | Where it runs |
|:----------|:-----------|:--------------|
| **Backend** | Python Flask API | `http://localhost:10000` (local) or Render |
| **Frontend** | HTML/CSS/JS dashboard | `http://localhost:8080` (local) or any static host |

**No API keys required** — the system works with cached historical data out of the box.

**Live deployment:** https://buriburi-agent-backend.onrender.com

---

## Local Development (Detailed)

### Prerequisites

- Python 3.8 or higher (3.11 recommended)
- pip (comes with Python)
- A web browser

**Check Python version:**
```bash
python3 --version
```

### Step 1: Get the Code

```bash
git clone https://github.com/mrhapile/BuriBuri_Trading.git
cd BuriBuri_Trading
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Start the Backend

```bash
python3 backend/app.py
```

You should see:
```
============================================================
Portfolio Intelligence System - Backend API
============================================================
Binding to: 0.0.0.0:10000
Endpoint: /run
Health: /health
Press Ctrl+C to stop
============================================================
```

**Leave this terminal running.**

### Step 4: Start the Frontend

Open a **new terminal window**, navigate to the project folder, and run:

```bash
python3 -m http.server 8080
```

> **Note:** Make sure you're in the `BuriBuri_Trading` directory.

### Step 5: Open the App

Go to: **http://localhost:8080**

Click **"Run Analysis"** — you should see portfolio data appear.

### Optional: Run CLI Demo

Test the system without the browser:

```bash
python3 full_system_demo.py
```

---

## Deploy to Render (Cloud)

### One-Click Deploy

1. Fork this repo to your GitHub account
2. Go to [render.com](https://render.com) and sign in
3. Click **New** → **Blueprint**
4. Select your forked repository
5. Click **Apply**

Render reads `render.yaml` and sets everything up automatically.

Your API will be live at: `https://your-app-name.onrender.com`

### Manual Deploy

If one-click doesn't work:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Enter these settings:

| Field | Value |
|:------|:------|
| Name | `buriburi-trading-api` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT` |
| Health Check Path | `/health` |

5. Add environment variable: `PYTHON_VERSION` = `3.11`
6. Click **Create Web Service**

### Connect Frontend to Deployed Backend

The frontend is pre-configured to use the deployed backend at:
```
https://buriburi-agent-backend.onrender.com
```

For local development, it automatically falls back to `http://127.0.0.1:10000`.

If deploying your own backend, update `script.js` line 19:

```javascript
const BACKEND_URL = "https://your-app-name.onrender.com";
```

Then deploy the frontend to GitHub Pages, Netlify, or Render Static Site.

---

## Configuration Files

### `Procfile`

Tells Render/Heroku how to start the app:

```
web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2
```

- `cd backend` — go to backend folder
- `gunicorn app:app` — start Flask with production server
- `--workers 1 --threads 2` — optimized for free tier
- `$PORT` — Render provides this automatically

### `render.yaml`

Auto-configures Render deployment:

```yaml
services:
  - type: web
    name: portfolio-intelligence-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: ALPACA_API_KEY
        sync: false  # Set manually in Render dashboard
      - key: ALPACA_SECRET_KEY
        sync: false  # Set manually in Render dashboard
    healthCheckPath: /health
    autoDeploy: true
```

### `requirements.txt`

Python packages needed:

```
flask>=2.0.0
flask-cors>=3.0.0
requests>=2.31.0
python-dotenv>=1.0.0
pytz>=2023.3
alpaca-trade-api>=3.0.0
gunicorn>=21.0.0
```

---

## Environment Variables

### Do I Need Them?

**No.** The app works without any environment variables using cached historical data.

### Quick Setup

```bash
cp .env.example .env
```

The `.env.example` file contains all available environment variables with explanations.

### Complete Variable Reference

| Variable | Required | Default | Description |
|:---------|:---------|:--------|:------------|
| `ALPACA_API_KEY` | No | — | Alpaca paper trading API key |
| `ALPACA_SECRET_KEY` | No | — | Alpaca paper trading secret |
| `ALPACA_BASE_URL` | No | `https://paper-api.alpaca.markets` | Alpaca API URL (paper only) |
| `POLYGON_API_KEY` | No | — | Polygon.io API key for sector data |
| `PORT` | No | `10000` | Backend server port |
| `HOST` | No | `0.0.0.0` | Backend server host |

**Testing/Validation Variables:**

| Variable | Required | Default | Description |
|:---------|:---------|:--------|:------------|
| `HISTORICAL_VALIDATION` | No | `false` | Enable historical validation mode |
| `VAL_SYMBOL` | No | `SPY` | Symbol for validation mode |
| `VAL_RANGE` | No | `6M` | Time range for validation mode |

### Data Mode Behavior

The system automatically selects the data source:

| Condition | Data Mode | What Happens |
|:----------|:----------|:-------------|
| Market OPEN + Alpaca credentials | **LIVE** | Real-time data from Alpaca |
| Market OPEN + No credentials | **LIVE** | Attempts live, may fail gracefully |
| Market CLOSED | **HISTORICAL** | Uses cached data (SPY, QQQ, IWM) |
| No credentials anytime | **HISTORICAL** | Uses cached data |

### Setting Up Alpaca (Optional)

1. Create a free account at [alpaca.markets](https://alpaca.markets)
2. Go to **Paper Trading** → **API Keys**
3. Generate a new API key
4. Add to `.env`:

```ini
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### Setting Up Polygon (Optional)

Polygon provides additional market data when Alpaca data is restricted:

1. Create a free account at [polygon.io](https://polygon.io)
2. Get your API key from the dashboard
3. Add to `.env`:

```ini
POLYGON_API_KEY=your_polygon_key
```

### On Render

Add environment variables in: **Dashboard → Your Service → Environment**

Only add the ones you need — the system works without any of them.

---

## API Reference

Test these with `curl` or your browser:

### Health Check
```bash
curl http://localhost:10000/health
```

### Run Analysis
```bash
curl http://localhost:10000/run
```

### Get Market Status
```bash
curl http://localhost:10000/status
```

### All Endpoints

| URL | Method | What it does |
|:----|:-------|:-------------|
| `/health` | GET | Check if API is running |
| `/run` | GET/POST | Run portfolio analysis |
| `/status` | GET | Get market open/closed status |
| `/available-symbols` | GET | List available stocks (SPY, QQQ, IWM) |
| `/time-ranges` | GET | List available time range options |
| `/set-symbol` | POST | Change stock to analyze |
| `/set-time-range` | POST | Change historical period |
| `/reset` | POST | Reset data router state |

---

## Running Tests

Run the test suite to verify the system:

```bash
python3 tests/test_system.py
```

Individual test modules:

```bash
# Test historical data mode
python3 tests/test_historical_mode.py

# Test live data mode (requires Alpaca credentials)
python3 tests/test_live_mode.py
```

---

## Troubleshooting

### "ModuleNotFoundError" when starting backend

**Fix:** Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Frontend shows "—" everywhere

**Fix:** Make sure backend is running:
```bash
python3 backend/app.py
```

Then refresh the browser.

### "Connection refused" in browser

**Fix:** Check you're using the correct ports:
- Backend: http://localhost:**10000**
- Frontend: http://localhost:**8080**

### Backend starts but frontend can't connect

**Fix:** Both must be running in separate terminals. Check:
1. Backend terminal shows "Binding to: 0.0.0.0:10000"
2. Frontend terminal shows "Serving HTTP on 0.0.0.0 port 8080"

### CORS errors in browser console

**Fix:** The backend has CORS enabled for all origins. If you still see errors:
1. Ensure the backend is running on port 10000
2. Check `script.js` line 19 has the correct `BACKEND_URL`

### Render deployment fails

**Fix:** Check build logs. Common issues:
- Missing `requirements.txt` — must be in repo root
- Wrong Python version — set `PYTHON_VERSION` to `3.11`

---

## Limitations

⚠️ **Important: This is a hackathon prototype**

| What | Status |
|:-----|:-------|
| Executes real trades | ❌ No |
| Connects to live accounts | ❌ No |
| Predicts stock prices | ❌ No |
| Production ready | ❌ No |

This system provides **recommendations only**. No trades are ever executed.

---

## File Structure

```
BuriBuri_Trading/
├── backend/
│   ├── app.py              ← Flask entry point
│   ├── api_routes.py       ← REST endpoints
│   ├── market_status.py    ← Market hours detection
│   └── scenarios.py        ← Demo scenarios
│
├── broker/
│   ├── alpaca_adapter.py   ← Alpaca API client (READ-ONLY)
│   └── mock_adapter.py     ← Mock data generator
│
├── demo/
│   ├── demo_profiles.py    ← Portfolio profiles
│   └── trend_overlays.py   ← Signal modifiers
│
├── tests/
│   ├── test_system.py      ← Main test suite
│   ├── test_historical_mode.py
│   └── test_live_mode.py
│
├── validation/             ← Validation utilities
├── historical_cache/       ← Cached stock data (SPY, QQQ, IWM)
│
├── index.html              ← Frontend dashboard
├── script.js               ← Frontend logic
├── styles.css              ← Styling
│
├── Procfile                ← Render/Heroku config
├── render.yaml             ← Render blueprint
├── requirements.txt        ← Python dependencies
├── .env.example            ← Environment template
│
├── decision_engine.py      ← Core decision logic
├── risk_guardrails.py      ← Safety filters
├── data_router.py          ← Market-aware data routing
├── market_mode.py          ← Market status detection
└── full_system_demo.py     ← CLI demo script
```

---

## Need Help?

1. Check [README.md](./README.md) for feature documentation
2. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
3. Open an issue on GitHub

---

_Last updated: 2026-02-02_
