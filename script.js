/**
 * BuriBuri Trading - Frontend Controller
 * 
 * Handles UI updates and backend API communication.
 * Designed for clarity and maintainability.
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const CONFIG = {
    API_BASE: 'http://127.0.0.1:5001',
    MOCK_MODE: false,  // Set to false when backend is running
};

// =============================================================================
// MOCK DATA (Used when backend is not available)
// =============================================================================

const MOCK_DATA = {
    run_id: "demo-" + Date.now().toString(36),
    timestamp: new Date().toISOString(),
    data_source: "DEMO",
    profile: "OVERCONCENTRATED_TECH",

    // Phase 2: Signals
    signals: {
        volatility_state: "STABLE",
        news_score: 62,
        sector_confidence: 58,
        atr: 2.34
    },

    // Phase 3: Market Posture
    market_posture: {
        market_posture: "DEFENSIVE",
        risk_level: "MEDIUM",
        reasons: [
            "Sector concentration exceeds safe threshold",
            "Volatility regime is stable but confidence is moderate"
        ]
    },

    // Portfolio State
    portfolio: {
        total_capital: 1000000,
        cash: 35000,
        position_count: 5,
        avg_vitals: 54,
        concentration_risk: "HIGH",
        capital_lockin: "12%"
    },

    // Decisions
    decisions: [
        {
            type: "POSITION",
            target: "NVDA",
            action: "MAINTAIN",
            score: 82,
            reasons: [
                "Strong position vitals (82/100)",
                "Sector momentum remains positive",
                "No concentration breach on this position"
            ]
        },
        {
            type: "POSITION",
            target: "AMD",
            action: "TRIM_RISK",
            score: 31,
            reasons: [
                "Position vitals critically low (31/100)",
                "Contributes to sector over-concentration",
                "Better opportunities available in other sectors"
            ]
        },
        {
            type: "POSITION",
            target: "MSFT",
            action: "HOLD",
            score: 65,
            reasons: [
                "Moderate vitals score (65/100)",
                "Stable performance, no immediate action needed"
            ]
        },
        {
            type: "CANDIDATE",
            target: "XLE",
            action: "ALLOCATE",
            score: 78,
            reasons: [
                "Energy sector shows rotation opportunity",
                "Would reduce TECH concentration",
                "High projected efficiency (78/100)"
            ]
        },
        {
            type: "CANDIDATE",
            target: "MORE_TECH",
            action: "BLOCK_RISK",
            score: 85,
            blocked: true,
            blocking_guard: "Concentration Guard",
            reasons: [
                "High efficiency score (85/100) but blocked",
                "TECH sector already over-concentrated (82%)",
                "Safety guardrail prevents additional TECH exposure"
            ]
        }
    ],

    // Safety Warnings
    warnings: [
        {
            type: "danger",
            message: "TECH sector concentration at 82% (limit: 60%)"
        },
        {
            type: "warning",
            message: "Cash reserves below target (3.5% vs 10% target)"
        },
        {
            type: "info",
            message: "1 candidate blocked by concentration guard"
        }
    ]
};

// =============================================================================
// DOM ELEMENTS
// =============================================================================

const elements = {
    // Header
    statusBadge: document.getElementById('status-badge'),
    runBtn: document.getElementById('run-btn'),
    marketStatus: document.getElementById('ui-market-status'),
    dataFeed: document.getElementById('ui-data-feed'),
    dataSource: document.getElementById('ui-data-source'),
    modeDesc: document.getElementById('ui-mode-desc'),

    // Control Selectors
    symbolSelector: document.getElementById('symbol-selector'),
    rangeSelector: document.getElementById('range-selector'),
    scenarioSelector: document.getElementById('scenario-selector'),
    historicalControls: document.getElementById('historical-controls'),

    // Market Overview
    marketPosture: document.getElementById('market-posture'),
    volatilityState: document.getElementById('volatility-state'),
    newsScore: document.getElementById('news-score'),
    sectorConfidence: document.getElementById('sector-confidence'),

    // Portfolio Health
    positionCount: document.getElementById('position-count'),
    avgVitals: document.getElementById('avg-vitals'),
    capitalLockin: document.getElementById('capital-lockin'),
    concentrationRisk: document.getElementById('concentration-risk'),

    // Decisions
    decisionFeed: document.getElementById('decision-feed'),
    emptyDecisions: document.getElementById('empty-decisions'),

    // Warnings
    warningsList: document.getElementById('warnings-list'),
    emptyWarnings: document.getElementById('empty-warnings')
};

// =============================================================================
// UI UPDATE FUNCTIONS
// =============================================================================

function setStatus(status, text) {
    elements.statusBadge.className = 'status-badge ' + status;
    elements.statusBadge.textContent = text;
}

/**
 * Handle Market Transparency Updates
 */
function updateTransparency(wrapper) {
    if (!wrapper) return;

    // 1. Market Status (OPEN/CLOSED)
    const mktStatus = wrapper.market_status?.status || "UNKNOWN";
    elements.marketStatus.textContent = mktStatus;
    elements.marketStatus.className = 'status-value highlight ' + mktStatus.toLowerCase();

    // 2. Data Feed Mode
    elements.dataFeed.textContent = wrapper.data_mode || "—";
    
    // 3. Data Source
    elements.dataSource.textContent = wrapper.portfolio_source || "—";

    // 4. Description (Authoritative Wording)
    const analysis = wrapper.analysis || {};
    const posture = analysis.market_posture || {};
    elements.modeDesc.textContent = posture.description || "System operating normally.";

    // 5. Toggle Historical Controls
    if (mktStatus === "OPEN") {
        elements.historicalControls.classList.add('hidden');
    } else {
        elements.historicalControls.classList.remove('hidden');
    }
}

function updateMarketOverview(data) {
    const posture = data.market_posture?.market_posture || 'NEUTRAL';
    elements.marketPosture.textContent = posture.replace('_', ' ');
    elements.marketPosture.className = 'metric-value posture ' + posture.toLowerCase();

    elements.volatilityState.textContent = data.signals?.volatility_state || '—';
    elements.newsScore.textContent = data.signals?.news_score ? `${data.signals.news_score}/100` : '—';
    elements.sectorConfidence.textContent = data.signals?.sector_confidence ? `${data.signals.sector_confidence}/100` : '—';
}

function updatePortfolioHealth(data) {
    const portfolio = data.portfolio || {};
    elements.positionCount.textContent = portfolio.position_count || '0';

    const avgVitals = portfolio.avg_vitals;
    if (avgVitals !== undefined) {
        elements.avgVitals.textContent = `${avgVitals}/100`;
        elements.avgVitals.className = 'health-value ' + getScoreClass(avgVitals);
    }

    elements.capitalLockin.textContent = portfolio.capital_lockin || 'NONE';

    const risk = portfolio.concentration_risk;
    if (risk) {
        elements.concentrationRisk.textContent = risk;
        elements.concentrationRisk.className = 'health-value ' + getRiskClass(risk);
    }
}

function renderDecisions(decisions) {
    const feed = elements.decisionFeed;
    const empty = elements.emptyDecisions;
    
    // Clear existing
    const cards = feed.querySelectorAll('.decision-card');
    cards.forEach(c => c.remove());

    if (!decisions || decisions.length === 0) {
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    decisions.forEach(d => {
        const card = document.createElement('div');
        card.className = 'decision-card' + (d.blocked ? ' blocked-action' : '');
        
        const actionClass = (d.action || '').toLowerCase().replace(/\s+/g, '_');
        const reasons = d.reasons || [];

        card.innerHTML = `
            <div class="decision-header">
                <div class="decision-target">
                    <span class="decision-symbol">${d.target}</span>
                    <span class="decision-type">${d.type}</span>
                </div>
                <span class="decision-action ${actionClass}">${d.action.replace('_', ' ')}</span>
            </div>
            ${d.blocked ? `<div class="blocked-reason">⛔ Blocked by ${d.blocking_guard || 'Safety Guard'}</div>` : ''}
            <div class="decision-reasons">
                <div class="decision-reasons-title">Logic Justification</div>
                <ul class="decision-reasons-list">
                    ${reasons.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
            <div class="decision-score">Confidence Score: ${d.score}/100</div>
        `;
        feed.appendChild(card);
    });
}

function renderWarnings(warnings) {
    const list = elements.warningsList;
    const empty = elements.emptyWarnings;
    
    const items = list.querySelectorAll('.warning-item');
    items.forEach(i => i.remove());

    if (!warnings || warnings.length === 0) {
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    warnings.forEach(w => {
        const item = document.createElement('div');
        item.className = 'warning-item ' + (w.type || 'info');
        
        const icon = w.type === 'danger' ? '🚨' : w.type === 'warning' ? '⚠️' : 'ℹ️';
        item.innerHTML = `<span class="warning-icon">${icon}</span><span class="warning-text">${w.message}</span>`;
        list.appendChild(item);
    });
}

// =============================================================================
// HELPERS
// =============================================================================

function getScoreClass(s) { return s >= 65 ? 'positive' : s >= 40 ? 'warning' : 'danger'; }
function getRiskClass(r) { 
    r = r.toLowerCase();
    return (r === 'low' || r === 'none') ? 'positive' : (r === 'medium' || r === 'moderate') ? 'warning' : 'danger'; 
}

// =============================================================================
// API COMMUNICATION
// =============================================================================

// =============================================================================
// API COMMUNICATION
// =============================================================================

/**
 * Fetch analysis data from backend
 */
async function fetchAnalysis() {
    if (CONFIG.MOCK_MODE) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 800));
        return {
            analysis: MOCK_DATA,
            market_status: { label: "MOCK", is_open: false, timestamp: new Date().toISOString() },
            data_mode: "MOCK"
        };
    }

    const selector = document.getElementById("scenario-selector");
    const scenario = selector ? selector.value : "NORMAL";

    const symbolInput = document.getElementById("symbol-input");
    const symbol = symbolInput ? symbolInput.value : "";

    const response = await fetch(`${CONFIG.API_BASE}/run?scenario=${scenario}&symbol=${symbol}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
}

/**
 * Update Market Status Badge and Message
 */
function updateMarketStatus(wrapper) {
    if (!wrapper || !wrapper.market_status) return;

    const status = wrapper.market_status;
    const isClosed = !status.is_open;
    const badge = document.getElementById('status-badge');

    // Update Badge
    if (badge) {
        badge.textContent = status.label || (status.is_open ? "OPEN" : "CLOSED");
        badge.className = 'status-badge ' + (status.is_open ? 'success' : 'danger');
    }

    // Show Historical Data Warning if Closed AND not already a scenario
    // If it is a scenario (wrapper.data_mode == "SCENARIO"), that takes precedence.
    const mode = wrapper.data_mode || "UNKNOWN";
    const source = wrapper.portfolio_source || "UNKNOWN";

    let message = "";
    if (mode === "HISTORICAL") {
        message = `Live Market Closed. Using Historical Data for ${wrapper.symbols_used?.[0] || 'Analysis'}.`;
    } else if (mode === "LIVE") {
        message = `Live Market Data. Connected to Alpaca & Polygon.`;
    } else if (mode === "SCENARIO") {
        message = "Scenario Simulation Active.";
    }

    // Inject message into header or overview
    // We can use the existing 'scenario-badges' container if empty, or prepend to it
    // Or just set the tooltip title of the badge?
    if (badge) badge.title = message + ` \nSource: ${source}`;

    // Also log to console for demo clarity
    console.log(`[System] Mode: ${mode} | Status: ${status.label} | Source: ${source}`);
}

// =============================================================================
// MAIN RUN HANDLER
// =============================================================================

async function runAnalysis() {
    try {
        setStatus('running', 'Analyzing...');
        elements.runBtn.disabled = true;
        elements.runBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';

        // Fetch data
        const wrapper = await fetchAnalysis();
        const data = wrapper.analysis || wrapper; // Fallback for safety

        // 1. Transparency Bar
        updateTransparency(wrapper);

        // 2. Panels
        updateMarketOverview(data);
        updatePortfolioHealth(data);
        renderDecisions(data.decisions);

        // Handle Warnings
        // Analysis might have warnings, or we might add system warnings
        const warnings = data.warnings || [];
        if (wrapper.market_status && !wrapper.market_status.is_open && wrapper.data_mode === "HISTORICAL") {
            warnings.unshift({
                type: 'warning',
                message: `Market is CLOSED. Using historical data (Polygon.io).`
            });
        }
        renderWarnings(warnings);

        // Update status text (bottom controller)
        setStatus('complete', 'Complete');

    } catch (error) {
        console.error('Analysis failed:', error);
        setStatus('error', 'Error');

        // Show error in warnings
        renderWarnings([{
            type: 'danger',
            message: `Failed to connect to backend. ${CONFIG.MOCK_MODE ? 'Using mock data.' : 'Ensure Flask is running.'} (${error.message})`
        }]);

    } finally {
        elements.runBtn.disabled = false;
        elements.runBtn.textContent = 'Run Analysis';
    }
}

// =============================================================================
// CONTROL EVENT HANDLERS
// =============================================================================

/**
 * Handle symbol selection change
 */
async function handleSymbolChange(event) {
    const symbol = event.target.value;
    
    try {
        setStatus('running', 'Switching symbol...');
        await setSymbol(symbol);
        STATE.selectedSymbol = symbol;
        
        // Auto-run analysis with new symbol
        await runAnalysis();
    } catch (error) {
        console.error('Symbol change failed:', error);
        setStatus('error', 'Error');
        
        // Revert selector to previous value
        if (elements.symbolSelector) {
            elements.symbolSelector.value = STATE.selectedSymbol;
        }
        
        renderWarnings([{
            type: 'danger',
            message: `Failed to switch symbol: ${error.message}`
        }]);
    }
}

/**
 * Handle time range selection change
 */
async function handleTimeRangeChange(event) {
    const timeRange = event.target.value;
    
    try {
        setStatus('running', 'Switching time range...');
        await setTimeRange(timeRange);
        STATE.selectedTimeRange = timeRange;
        
        // Auto-run analysis with new time range
        await runAnalysis();
    } catch (error) {
        console.error('Time range change failed:', error);
        setStatus('error', 'Error');
        
        // Revert selector to previous value
        if (elements.timeRangeSelector) {
            elements.timeRangeSelector.value = STATE.selectedTimeRange;
        }
        
        renderWarnings([{
            type: 'danger',
            message: `Failed to switch time range: ${error.message}`
        }]);
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

/**
 * Initialize the application
 */
async function initializeApp() {
    console.log('[BuriBuri] Initializing Market-Aware Trading System...');
    
    // Fetch initial status to configure controls
    try {
        const status = await fetchStatus();
        if (status) {
            updateDataSourceBar({
                market_status: { label: status.market_status, is_open: status.is_open },
                data_mode: status.data_mode,
                data_source: status.data_source,
                status_message: status.status_message
            });
            updateMarketAwareControls(status);
            
            console.log(`[BuriBuri] Market: ${status.market_status} | Mode: ${status.data_mode}`);
        }
    } catch (error) {
        console.warn('[BuriBuri] Could not fetch initial status:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Bind run button
    elements.runBtn.addEventListener('click', runAnalysis);

    console.log('BuriBuri Trading UI initialized');
    console.log('Mock mode:', CONFIG.MOCK_MODE);
});
