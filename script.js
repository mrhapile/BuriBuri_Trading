const CONFIG = {
    API_BASE: 'http://127.0.0.1:5001',
    MOCK_MODE: false,
};

// =============================================================================
// DOM ELEMENTS
// =============================================================================

const elements = {
    // Header & Global Status
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

async function runAnalysis() {
    try {
        setStatus('running', 'Analyzing...');
        elements.runBtn.disabled = true;
        elements.runBtn.innerHTML = '<span class="loading-spinner"></span> Running Pipeline...';

        const scenario = elements.scenarioSelector.value;
        const symbol = elements.symbolSelector.value;
        const range = elements.rangeSelector.value;

        const url = `${CONFIG.API_BASE}/run?scenario=${scenario}&symbol=${symbol}&time_range=${range}`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error(`Server Error: ${response.status}`);
        
        const wrapper = await response.json();
        const data = wrapper.analysis || {};

        // 1. Transparency Bar
        updateTransparency(wrapper);

        // 2. Panels
        updateMarketOverview(data);
        updatePortfolioHealth(data);
        renderDecisions(data.decisions);
        renderWarnings(data.blocked_by_safety?.map(b => ({
            type: 'warning',
            message: `Safety Block: ${b.target} → ${b.action} (${b.blocking_guard})`
        })) || []);

        setStatus('complete', 'Complete');

    } catch (err) {
        console.error(err);
        setStatus('error', 'Failed');
        renderWarnings([{ type: 'danger', message: `Pipeline Execution Failed: ${err.message}` }]);
    } finally {
        elements.runBtn.disabled = false;
        elements.runBtn.textContent = 'Run Analysis';
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    elements.runBtn.addEventListener('click', runAnalysis);
    
    // Initial silent run to detect market status
    runAnalysis();
    
    console.log('BuriBuri Trading: Market-Aware Pipeline Initialized.');
});
