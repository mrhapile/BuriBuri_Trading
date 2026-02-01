/**
 * BuriBuri Trading - Frontend Controller
 * 
 * Market-Aware Data Routing with Historical Validation Support.
 * Handles UI updates and backend API communication.
 * 
 * Data Source Rules (STRICT):
 * - Market OPEN  → LIVE DATA ONLY (Alpaca + Polygon)
 * - Market CLOSED → HISTORICAL DATA ONLY (from cache)
 * - NO demo data. NO silent fallbacks.
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

/**
 * Detect API base URL:
 * 1. Check for global BACKEND_URL (set by deployment)
 * 2. Check window.location for production hints
 * 3. Fallback to localhost for development
 */
function getApiBase() {
    // Allow override via global variable (set in index.html for deployment)
    if (typeof BACKEND_URL !== 'undefined' && BACKEND_URL) {
        return BACKEND_URL;
    }
    
    // Check if we're on a production domain (not localhost/127.0.0.1)
    const isProduction = window.location.hostname !== 'localhost' && 
                         window.location.hostname !== '127.0.0.1';
    
    if (isProduction) {
        // For production, assume backend is at same origin or use env-injected URL
        // This will be overridden by BACKEND_URL if set
        console.warn('⚠️ Production detected but no BACKEND_URL set. API calls may fail.');
        return '';  // Same origin
    }
    
    // Development: use localhost
    return 'http://127.0.0.1:10000';
}

const CONFIG = {
    API_BASE: getApiBase(),
    MOCK_MODE: false,  // Set to false when backend is running
};

// =============================================================================
// STATE MANAGEMENT
// =============================================================================

const STATE = {
    marketStatus: 'UNKNOWN',
    isMarketOpen: false,
    dataMode: 'UNKNOWN',
    dataSource: 'UNKNOWN',
    selectedSymbol: 'SPY',
    selectedTimeRange: '6M',
    availableSymbols: [],
    availableTimeRanges: {},
    controlsEnabled: {
        symbolSelector: false,
        timeRangeSelector: false
    }
};

// =============================================================================
// MOCK DATA (Used when backend is not available)
// =============================================================================

const MOCK_DATA = {
    run_id: "historical-" + Date.now().toString(36),
    timestamp: new Date().toISOString(),
    data_source: "HISTORICAL",
    profile: "HISTORICAL_VALIDATION",

    signals: {
        volatility_state: "STABLE",
        news_score: 50,
        sector_confidence: 55,
        atr: 2.34
    },

    market_posture: {
        market_posture: "NEUTRAL",
        risk_level: "MEDIUM",
        reasons: [
            "Historical validation mode active",
            "Decision logic being validated over extended periods"
        ]
    },

    portfolio: {
        total_capital: 100000,
        cash: 25000,
        position_count: 1,
        avg_vitals: 65,
        concentration_risk: "LOW",
        capital_lockin: "NONE"
    },

    decisions: [
        {
            type: "POSITION",
            target: "SPY",
            action: "MAINTAIN",
            score: 72,
            reasons: [
                "Position vitals stable (72/100)",
                "Historical data shows consistent behavior",
                "No concentration breach detected"
            ]
        }
    ],

    warnings: []
};

// =============================================================================
// DOM ELEMENTS
// =============================================================================

const elements = {
    // Data Source Bar
    dsMarketStatus: document.getElementById('ds-market-status'),
    dsDataMode: document.getElementById('ds-data-mode'),
    dsDataSource: document.getElementById('ds-data-source'),
    dsMessage: document.getElementById('ds-message'),
    
    // Market-Aware Controls
    symbolSelector: document.getElementById('symbol-selector'),
    timeRangeSelector: document.getElementById('time-range-selector'),
    symbolControlGroup: document.getElementById('symbol-control-group'),
    timeRangeControlGroup: document.getElementById('time-range-control-group'),
    
    // Data Info Panel
    infoSymbol: document.getElementById('info-symbol'),
    infoTimeRange: document.getElementById('info-time-range'),
    infoCandleCount: document.getElementById('info-candle-count'),
    infoDateRange: document.getElementById('info-date-range'),
    
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
    emptyWarnings: document.getElementById('empty-warnings'),
    
    // UPGRADE 2: Crash Toggle
    crashToggle: document.getElementById('crash-toggle'),
    
    // UPGRADE 1: Agent Memory
    memPrevPosture: document.getElementById('mem-prev-posture'),
    memPrevRisk: document.getElementById('mem-prev-risk'),
    memCurrRisk: document.getElementById('mem-curr-risk'),
    memTrend: document.getElementById('mem-trend'),
    memoryMessage: document.getElementById('memory-message'),
    
    // UPGRADE 3: Brain Log
    brainLog: document.getElementById('brain-log'),
    brainThinking: document.getElementById('brain-thinking')
};

// =============================================================================
// UI UPDATE FUNCTIONS
// =============================================================================

/**
 * Update the status badge in the header
 */
function setStatus(status, text) {
    if (elements.statusBadge) {
        elements.statusBadge.className = 'status-badge ' + status;
        elements.statusBadge.textContent = text;
    }
}

/**
 * Update the data source status bar
 */
function updateDataSourceBar(wrapper) {
    if (!wrapper) return;

    const marketStatus = wrapper.market_status?.label || wrapper.market_status || 'UNKNOWN';
    const isOpen = wrapper.market_status?.is_open || false;
    const dataMode = wrapper.data_mode || 'UNKNOWN';
    const dataSource = wrapper.data_source || 'UNKNOWN';
    const statusMessage = wrapper.status_message || '';

    // Update state
    STATE.marketStatus = marketStatus;
    STATE.isMarketOpen = isOpen;
    STATE.dataMode = dataMode;
    STATE.dataSource = dataSource;

    // Update Market Status
    if (elements.dsMarketStatus) {
        elements.dsMarketStatus.textContent = marketStatus;
        elements.dsMarketStatus.classList.remove('open', 'closed');
        elements.dsMarketStatus.classList.add(isOpen ? 'open' : 'closed');
    }

    // Update Data Mode
    if (elements.dsDataMode) {
        elements.dsDataMode.textContent = dataMode;
        elements.dsDataMode.classList.remove('live', 'historical');
        elements.dsDataMode.classList.add(dataMode.toLowerCase());
    }

    // Update Data Source
    if (elements.dsDataSource) {
        elements.dsDataSource.textContent = dataSource;
    }

    // Update Status Message
    if (elements.dsMessage) {
        elements.dsMessage.textContent = statusMessage;
    }
}

/**
 * Update the market-aware control selectors
 */
function updateMarketAwareControls(routingConfig) {
    if (!routingConfig) return;

    const { 
        selected_symbol, 
        selected_time_range, 
        available_symbols, 
        available_time_ranges,
        controls_enabled 
    } = routingConfig;

    // Update state
    STATE.selectedSymbol = selected_symbol || 'SPY';
    STATE.selectedTimeRange = selected_time_range || '6M';
    STATE.availableSymbols = available_symbols || [];
    STATE.availableTimeRanges = available_time_ranges || {};
    STATE.controlsEnabled = controls_enabled || {};

    // Update Symbol Selector
    if (elements.symbolSelector) {
        // Populate options
        elements.symbolSelector.innerHTML = '';
        STATE.availableSymbols.forEach(sym => {
            const option = document.createElement('option');
            option.value = sym;
            option.textContent = sym;
            if (sym === STATE.selectedSymbol) option.selected = true;
            elements.symbolSelector.appendChild(option);
        });

        // Enable/disable based on market status
        const symbolEnabled = STATE.controlsEnabled.symbol_selector !== false;
        elements.symbolSelector.disabled = !symbolEnabled;
        
        if (elements.symbolControlGroup) {
            elements.symbolControlGroup.classList.toggle('disabled', !symbolEnabled);
        }
    }

    // Update Time Range Selector
    if (elements.timeRangeSelector) {
        // Populate options
        elements.timeRangeSelector.innerHTML = '';
        Object.entries(STATE.availableTimeRanges).forEach(([key, info]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = info.label || key;
            if (key === STATE.selectedTimeRange) option.selected = true;
            elements.timeRangeSelector.appendChild(option);
        });

        // Enable/disable based on market status
        const timeRangeEnabled = STATE.controlsEnabled.time_range_selector !== false;
        elements.timeRangeSelector.disabled = !timeRangeEnabled;
        
        if (elements.timeRangeControlGroup) {
            elements.timeRangeControlGroup.classList.toggle('disabled', !timeRangeEnabled);
        }
    }
}

/**
 * Update the data info panel
 */
function updateDataInfoPanel(wrapper) {
    if (!wrapper) return;

    const routingConfig = wrapper.routing_config || {};
    const metadata = wrapper.data_metadata || {};

    // Selected Symbol
    if (elements.infoSymbol) {
        elements.infoSymbol.textContent = routingConfig.selected_symbol || STATE.selectedSymbol || '—';
    }

    // Time Range
    if (elements.infoTimeRange) {
        const timeRange = routingConfig.selected_time_range || STATE.selectedTimeRange;
        const label = STATE.availableTimeRanges[timeRange]?.label || timeRange || '—';
        elements.infoTimeRange.textContent = STATE.isMarketOpen ? 'Live' : label;
    }

    // Candle Count
    if (elements.infoCandleCount) {
        elements.infoCandleCount.textContent = metadata.candle_count || '—';
    }

    // Date Range
    if (elements.infoDateRange) {
        if (metadata.data_start && metadata.data_end) {
            elements.infoDateRange.textContent = `${metadata.data_start} → ${metadata.data_end}`;
        } else if (STATE.isMarketOpen) {
            elements.infoDateRange.textContent = 'Real-time';
        } else {
            elements.infoDateRange.textContent = '—';
        }
    }
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
    if (elements.marketPosture) {
        elements.marketPosture.textContent = posture.replace('_', ' ');
        elements.marketPosture.className = 'metric-value posture ' + posture.toLowerCase();
    }

    // Signals
    if (elements.volatilityState) {
        elements.volatilityState.textContent = data.signals?.volatility_state || '—';
    }
    if (elements.newsScore) {
        elements.newsScore.textContent = data.signals?.news_score ?
            `${data.signals.news_score}/100` : '—';
    }
    if (elements.sectorConfidence) {
        elements.sectorConfidence.textContent = data.signals?.sector_confidence ?
            `${data.signals.sector_confidence}/100` : '—';
    }
}

/**
 * Update portfolio health panel
 */
function updatePortfolioHealth(data) {
    const portfolio = data.portfolio || {};

    if (elements.positionCount) {
        elements.positionCount.textContent = portfolio.position_count || '—';
    }

    // Avg Vitals with color coding
    const avgVitals = portfolio.avg_vitals;
    if (elements.avgVitals) {
        if (avgVitals !== undefined) {
            elements.avgVitals.textContent = `${avgVitals}/100`;
            elements.avgVitals.className = 'health-value ' + getScoreClass(avgVitals);
        } else {
            elements.avgVitals.textContent = '—';
        }
    }

    if (elements.capitalLockin) {
        elements.capitalLockin.textContent = portfolio.capital_lockin || '—';
    }

    // Concentration Risk with color coding
    const risk = portfolio.concentration_risk;
    if (elements.concentrationRisk) {
        if (risk) {
            elements.concentrationRisk.textContent = risk;
            elements.concentrationRisk.className = 'health-value ' + getRiskClass(risk);
        } else {
            elements.concentrationRisk.textContent = '—';
        }
    }
}

/**
 * Render decision cards
 */
function renderDecisions(decisions) {
    if (!elements.decisionFeed) return;
    
    if (!decisions || decisions.length === 0) {
        if (elements.emptyDecisions) elements.emptyDecisions.classList.remove('hidden');
        return;
    }

    if (elements.emptyDecisions) elements.emptyDecisions.classList.add('hidden');

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
    if (!elements.warningsList) return;
    
    if (!warnings || warnings.length === 0) {
        if (elements.emptyWarnings) elements.emptyWarnings.classList.remove('hidden');
        return;
    }

    if (elements.emptyWarnings) elements.emptyWarnings.classList.add('hidden');

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

// =============================================================================
// UPGRADE 1: AGENT MEMORY
// =============================================================================

/**
 * Update the agent memory panel with trend insights
 */
function updateMemoryPanel(memory) {
    if (!memory) return;
    
    const { previous_posture, previous_risk, current_risk, trend } = memory;
    
    // Update values
    if (elements.memPrevPosture) {
        elements.memPrevPosture.textContent = previous_posture || 'First Run';
    }
    if (elements.memPrevRisk) {
        elements.memPrevRisk.textContent = previous_risk || '—';
    }
    if (elements.memCurrRisk) {
        elements.memCurrRisk.textContent = current_risk || '—';
    }
    
    // Update trend badge
    if (elements.memTrend) {
        elements.memTrend.textContent = formatTrend(trend);
        elements.memTrend.className = 'memory-value trend-badge ' + getTrendClass(trend);
    }
    
    // Update message
    if (elements.memoryMessage) {
        const message = getTrendMessage(trend, previous_risk, current_risk);
        elements.memoryMessage.textContent = message;
        elements.memoryMessage.className = 'memory-message ' + getTrendMessageClass(trend);
    }
}

function formatTrend(trend) {
    switch (trend) {
        case 'RISK_INCREASING': return '📈 INCREASING';
        case 'RISK_DECREASING': return '📉 DECREASING';
        case 'STABLE': return '➡️ STABLE';
        case 'FIRST_RUN': return '🆕 FIRST RUN';
        default: return trend || '—';
    }
}

function getTrendClass(trend) {
    switch (trend) {
        case 'RISK_INCREASING': return 'increasing';
        case 'RISK_DECREASING': return 'decreasing';
        case 'STABLE': return 'stable';
        case 'FIRST_RUN': return 'first-run';
        default: return '';
    }
}

function getTrendMessage(trend, prevRisk, currRisk) {
    switch (trend) {
        case 'RISK_INCREASING':
            return `⚠️ Risk has INCREASED since last analysis (${prevRisk} → ${currRisk}). Agent is more cautious.`;
        case 'RISK_DECREASING':
            return `✅ Risk has DECREASED since last analysis (${prevRisk} → ${currRisk}). Conditions improving.`;
        case 'STABLE':
            return `➡️ Risk level remains STABLE at ${currRisk}. No significant change detected.`;
        case 'FIRST_RUN':
            return `🆕 This is the agent's first analysis. Memory baseline established.`;
        default:
            return '';
    }
}

function getTrendMessageClass(trend) {
    switch (trend) {
        case 'RISK_INCREASING': return 'risk-increasing';
        case 'RISK_DECREASING': return 'risk-decreasing';
        default: return '';
    }
}

// =============================================================================
// UPGRADE 3: BRAIN LOG
// =============================================================================

/**
 * Render the brain log with animated entries
 */
function renderBrainLog(thoughtLog) {
    if (!elements.brainLog) return;
    
    // Clear existing entries except thinking indicator
    const existingEntries = elements.brainLog.querySelectorAll('.brain-log-entry');
    existingEntries.forEach(entry => entry.remove());
    
    // Hide thinking indicator
    if (elements.brainThinking) {
        elements.brainThinking.style.display = 'none';
    }
    
    if (!thoughtLog || thoughtLog.length === 0) {
        if (elements.brainThinking) {
            elements.brainThinking.style.display = 'flex';
        }
        return;
    }
    
    // Add entries with staggered animation
    thoughtLog.forEach((thought, index) => {
        const entry = document.createElement('div');
        entry.className = 'brain-log-entry ' + getThoughtClass(thought);
        entry.textContent = thought;
        entry.style.animationDelay = `${index * 50}ms`;
        elements.brainLog.appendChild(entry);
    });
    
    // Auto-scroll to bottom
    elements.brainLog.scrollTop = elements.brainLog.scrollHeight;
}

function getThoughtClass(thought) {
    if (thought.includes('BLOCKED') || thought.includes('🚫')) return 'blocked';
    if (thought.includes('⚠️') || thought.includes('WARNING')) return 'warning';
    if (thought.includes('✅') || thought.includes('approved')) return 'decision';
    if (thought.includes('📊') || thought.includes('📈') || thought.includes('📉')) return 'signal';
    return 'info';
}

/**
 * Show thinking animation before analysis
 */
function showThinking() {
    if (!elements.brainLog) return;
    
    // Clear existing entries
    const existingEntries = elements.brainLog.querySelectorAll('.brain-log-entry');
    existingEntries.forEach(entry => entry.remove());
    
    // Show thinking indicator
    if (elements.brainThinking) {
        elements.brainThinking.style.display = 'flex';
        const thinkingText = elements.brainThinking.querySelector('.thinking-text');
        if (thinkingText) {
            thinkingText.textContent = 'Agent is thinking...';
        }
    }
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

/**
 * Fetch the current market status and routing configuration
 */
async function fetchStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/status`);
        if (!response.ok) throw new Error(`Status API Error: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch status:', error);
        return null;
    }
}

/**
 * Set the selected symbol (historical mode only)
 */
async function setSymbol(symbol) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/set-symbol`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to set symbol');
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to set symbol:', error);
        throw error;
    }
}

/**
 * Set the selected time range (historical mode only)
 */
async function setTimeRange(timeRange) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/set-time-range`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time_range: timeRange })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to set time range');
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to set time range:', error);
        throw error;
    }
}

/**
 * Fetch analysis data from backend
 */
async function fetchAnalysis() {
    if (CONFIG.MOCK_MODE) {
        await new Promise(resolve => setTimeout(resolve, 800));
        return {
            analysis: MOCK_DATA,
            market_status: { label: "CLOSED", is_open: false, timestamp: new Date().toISOString() },
            data_mode: "HISTORICAL",
            data_source: "Alpaca Historical Cache",
            routing_config: {
                selected_symbol: "SPY",
                selected_time_range: "6M",
                available_symbols: ["SPY", "QQQ", "IWM"],
                available_time_ranges: { "1M": {label: "1 Month"}, "4M": {label: "4 Months"}, "6M": {label: "6 Months"}, "1Y": {label: "1 Year"} },
                controls_enabled: { symbol_selector: true, time_range_selector: true }
            },
            memory: { previous_posture: null, previous_risk: null, current_risk: "MEDIUM", trend: "FIRST_RUN" },
            thought_log: ["🧠 Mock mode active", "📊 Using simulated data"],
            status_message: "Market is closed. System is operating on Alpaca historical market data to validate decision logic over extended periods."
        };
    }

    const scenario = document.getElementById("scenario-selector")?.value || "NORMAL";
    const symbol = STATE.selectedSymbol;
    const timeRange = STATE.selectedTimeRange;
    
    // UPGRADE 2: Get crash toggle state
    const simulateCrash = elements.crashToggle?.checked || false;

    // Use POST to send crash simulation flag
    const response = await fetch(`${CONFIG.API_BASE}/run`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
        },
        body: JSON.stringify({
            scenario: scenario,
            symbol: symbol,
            time_range: timeRange,
            simulate_crash: simulateCrash
        })
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
}

// =============================================================================
// MAIN RUN HANDLER
// =============================================================================

async function runAnalysis() {
    try {
        // Update UI to running state
        setStatus('running', 'Running...');
        if (elements.runBtn) {
            elements.runBtn.disabled = true;
            elements.runBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
        }
        
        // UPGRADE 3: Show thinking animation
        showThinking();

        // Fetch data
        const wrapper = await fetchAnalysis();
        const data = wrapper.analysis || wrapper;

        // Update Data Source Bar (ALWAYS VISIBLE)
        updateDataSourceBar(wrapper);

        // Update Market-Aware Controls
        updateMarketAwareControls(wrapper.routing_config);

        // Update Data Info Panel
        updateDataInfoPanel(wrapper);

        // Update all panels
        updateScenarioBadges(data);
        updateMarketOverview(data);
        updatePortfolioHealth(data);
        renderDecisions(data.decisions);
        
        // UPGRADE 1: Update Memory Panel
        updateMemoryPanel(wrapper.memory);
        
        // UPGRADE 3: Update Brain Log
        renderBrainLog(wrapper.thought_log);

        // Handle Warnings
        const warnings = data.warnings || [];
        
        // Add crash simulation warning if active
        if (wrapper.crash_simulation_active) {
            warnings.unshift({
                type: 'danger',
                message: '🚨 Market Crash Simulation Active — All aggressive allocations are blocked.'
            });
        }
        
        // Add system info for historical mode
        if (wrapper.market_status && !wrapper.market_status.is_open && wrapper.data_mode === "HISTORICAL") {
            warnings.unshift({
                type: 'info',
                message: `Validation Mode: Analyzing ${wrapper.routing_config?.selected_symbol || 'symbol'} with ${wrapper.routing_config?.selected_time_range || ''} of historical data from Alpaca.`
            });
        }
        renderWarnings(warnings);

        // Update status
        setStatus('complete', 'Complete');

    } catch (error) {
        console.error('Analysis failed:', error);
        setStatus('error', 'Error');

        renderWarnings([{
            type: 'danger',
            message: `Failed to connect to backend at ${CONFIG.API_BASE || 'origin'}. (${error.message})`
        }]);

    } finally {
        if (elements.runBtn) {
            elements.runBtn.disabled = false;
            elements.runBtn.textContent = 'Run Analysis';
        }
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
        await runAnalysis();
    } catch (error) {
        console.error('Symbol change failed:', error);
        setStatus('error', 'Error');
        
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
        await runAnalysis();
    } catch (error) {
        console.error('Time range change failed:', error);
        setStatus('error', 'Error');
        
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
    // Initialize the app
    initializeApp();
    
    // Bind run button
    if (elements.runBtn) {
        elements.runBtn.addEventListener('click', runAnalysis);
    }
    
    // Bind symbol selector
    if (elements.symbolSelector) {
        elements.symbolSelector.addEventListener('change', handleSymbolChange);
    }
    
    // Bind time range selector
    if (elements.timeRangeSelector) {
        elements.timeRangeSelector.addEventListener('change', handleTimeRangeChange);
    }
    
    console.log('[BuriBuri] UI initialized. Mock mode:', CONFIG.MOCK_MODE);
});
