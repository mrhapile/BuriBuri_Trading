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

/**
 * Update the status badge in the header
 */
function setStatus(status, text) {
    elements.statusBadge.className = 'status-badge ' + status;
    elements.statusBadge.textContent = text;
}

/**
 * Render Scenario Badges and Description
 */
function updateScenarioBadges(data) {
    const container = document.getElementById('scenario-badges');
    if (!container) return;

    const scenario = data.scenario_meta || {};

    if (scenario.badges && scenario.badges.length > 0) {
        const badgesHtml = scenario.badges.map(b =>
            `<span class="scenario-badge">✔ ${b}</span>`
        ).join('');

        let descHtml = '';
        if (scenario.description) {
            descHtml = `<div class="scenario-desc">${scenario.header_emoji || ''} ${scenario.description}</div>`;
        }

        container.innerHTML = descHtml + `<div class="badges-row">${badgesHtml}</div>`;
        container.classList.add('visible');
    } else {
        container.innerHTML = '';
        container.classList.remove('visible');
    }
}

/**
 * Update market overview panel
 */
function updateMarketOverview(data) {
    // Market Posture
    const posture = data.market_posture?.market_posture || 'NEUTRAL';
    elements.marketPosture.textContent = posture.replace('_', ' ');
    elements.marketPosture.className = 'metric-value posture ' + posture.toLowerCase();

    // Signals
    elements.volatilityState.textContent = data.signals?.volatility_state || '—';
    elements.newsScore.textContent = data.signals?.news_score ?
        `${data.signals.news_score}/100` : '—';
    elements.sectorConfidence.textContent = data.signals?.sector_confidence ?
        `${data.signals.sector_confidence}/100` : '—';
}

/**
 * Update portfolio health panel
 */
function updatePortfolioHealth(data) {
    const portfolio = data.portfolio || {};

    elements.positionCount.textContent = portfolio.position_count || '—';

    // Avg Vitals with color coding
    const avgVitals = portfolio.avg_vitals;
    if (avgVitals !== undefined) {
        elements.avgVitals.textContent = `${avgVitals}/100`;
        elements.avgVitals.className = 'health-value ' + getScoreClass(avgVitals);
    } else {
        elements.avgVitals.textContent = '—';
    }

    elements.capitalLockin.textContent = portfolio.capital_lockin || '—';

    // Concentration Risk with color coding
    const risk = portfolio.concentration_risk;
    if (risk) {
        elements.concentrationRisk.textContent = risk;
        elements.concentrationRisk.className = 'health-value ' + getRiskClass(risk);
    } else {
        elements.concentrationRisk.textContent = '—';
    }
}

/**
 * Render decision cards
 */
function renderDecisions(decisions) {
    if (!decisions || decisions.length === 0) {
        elements.emptyDecisions.classList.remove('hidden');
        return;
    }

    elements.emptyDecisions.classList.add('hidden');

    // Clear existing decisions
    const existingCards = elements.decisionFeed.querySelectorAll('.decision-card');
    existingCards.forEach(card => card.remove());

    // Render each decision
    decisions.forEach(decision => {
        const card = createDecisionCard(decision);
        elements.decisionFeed.appendChild(card);
    });
}

/**
 * Create a single decision card element
 */
function createDecisionCard(decision) {
    const card = document.createElement('div');
    card.className = 'decision-card' + (decision.blocked ? ' blocked-action' : '');

    const actionClass = getActionClass(decision.action);
    const reasons = decision.reasons || [];

    card.innerHTML = `
        <div class="decision-header">
            <div class="decision-target">
                <span class="decision-symbol">${decision.target}</span>
                <span class="decision-type">${decision.type}</span>
            </div>
            <span class="decision-action ${actionClass}">${decision.action.replace('_', ' ')}</span>
        </div>
        ${decision.blocked ? `<div class="blocked-reason">⛔ Blocked by ${decision.blocking_guard || 'Safety Guard'}</div>` : ''}
        <div class="decision-reasons">
            <div class="decision-reasons-title">Reasoning</div>
            <ul class="decision-reasons-list">
                ${reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
        </div>
        <div class="decision-score">Confidence Score: ${decision.score}/100</div>
    `;

    return card;
}

/**
 * Render warnings list
 */
function renderWarnings(warnings) {
    if (!warnings || warnings.length === 0) {
        elements.emptyWarnings.classList.remove('hidden');
        return;
    }

    elements.emptyWarnings.classList.add('hidden');

    // Clear existing warnings
    const existingItems = elements.warningsList.querySelectorAll('.warning-item');
    existingItems.forEach(item => item.remove());

    // Render each warning
    warnings.forEach(warning => {
        const item = document.createElement('div');
        item.className = 'warning-item ' + (warning.type || 'info');

        const icon = getWarningIcon(warning.type);
        item.innerHTML = `
            <span class="warning-icon">${icon}</span>
            <span class="warning-text">${warning.message}</span>
        `;

        elements.warningsList.appendChild(item);
    });
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function getScoreClass(score) {
    if (score >= 65) return 'positive';
    if (score >= 40) return 'warning';
    return 'danger';
}

function getRiskClass(risk) {
    const r = (risk || '').toLowerCase();
    if (r === 'low' || r === 'none') return 'positive';
    if (r === 'medium' || r === 'moderate') return 'warning';
    return 'danger';
}

function getActionClass(action) {
    return (action || '').toLowerCase().replace(/\s+/g, '_');
}

function getWarningIcon(type) {
    switch (type) {
        case 'danger': return '🚨';
        case 'warning': return '⚠️';
        case 'success': return '✅';
        default: return 'ℹ️';
    }
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
        // Update UI to running state
        setStatus('running', 'Running...');
        elements.runBtn.disabled = true;
        elements.runBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';

        // Fetch data
        const wrapper = await fetchAnalysis();
        const data = wrapper.analysis || wrapper; // Fallback for safety

        // Update Market Status UI
        updateMarketStatus(wrapper);

        // Update all panels using appropriate data mapping
        updateMarketOverview(data);
        updateScenarioBadges(data);
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
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Bind run button
    elements.runBtn.addEventListener('click', runAnalysis);

    console.log('BuriBuri Trading UI initialized');
    console.log('Mock mode:', CONFIG.MOCK_MODE);
});
