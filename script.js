/**
 * script.js
 * Portfolio Intelligence System - AI Agent Visualization
 * 
 * Renders the complete AI decision pipeline step-by-step.
 * Now wired to Flask backend for real Python engine output.
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE_URL = "http://127.0.0.1:5000";
let useLiveBackend = true; // Toggle for fallback mode

// =============================================================================
// SCENARIO DATA (Fallback Mock Data)
// =============================================================================

const scenarios = {
    balanced: {
        name: "Balanced Portfolio",
        input: { positions: 3, candles: 20, headlines: 3 },
        phase2: {
            volatility: "CONTRACTING",
            volatilityExplanation: "Market volatility decreasing, risk subsiding",
            newsScore: 55,
            newsExplanation: "Mixed sentiment: AI demand positive, rate fears neutral",
            confidence: 65,
            confidenceExplanation: "Moderate confidence supports measured action"
        },
        phase3: {
            posture: "NEUTRAL",
            risk: "MEDIUM",
            reason: "Volatility stable with mixed confidence — no aggressive moves warranted",
            decisions: [
                { target: "NVDA", type: "POSITION", action: "MAINTAIN", reasons: ["Vitals Score: 84 (HEALTHY)", "Sector momentum positive"] },
                { target: "SLOW_UTIL", type: "POSITION", action: "REVIEW", reasons: ["Stagnant performance (>20 days, <2% return)"] }
            ]
        },
        phase4: {
            allowed: [{ symbol: "NVDA", action: "MONITOR", reason: "Strong position" }],
            blocked: [],
            summary: { decision: "NEUTRAL", proposed: 2, blocked: 0, mode: "STANDARD" }
        }
    }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function getVolatilityClass(state) {
    if (state === "CONTRACTING") return "green";
    if (state === "EXPANDING") return "red";
    return "yellow";
}

function getScoreClass(score) {
    if (score >= 65) return "green";
    if (score >= 40) return "yellow";
    return "red";
}

function getPostureClass(posture) {
    const p = (posture || "").toLowerCase().replace(" ", "_");
    if (["opportunity", "aggressive"].includes(p)) return "opportunity";
    if (["defensive", "risk_off"].includes(p)) return "risk_off";
    return "neutral";
}

function getRiskClass(risk) {
    return (risk || "medium").toLowerCase();
}

function getActionClass(action) {
    return (action || "").toLowerCase().replace(/\s+/g, "_");
}

function safeValue(val, fallback = "N/A") {
    return val !== undefined && val !== null ? val : fallback;
}

// =============================================================================
// BACKEND API INTEGRATION
// =============================================================================

async function fetchFromBackend() {
    try {
        const response = await fetch(`${API_BASE_URL}/run`);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Backend fetch failed:", error);
        return null;
    }
}

/**
 * Transform backend response to UI-compatible format
 */
function transformBackendData(data) {
    // Extract from backend structure
    const inputStats = data.input_stats || {};
    const phase2 = data.phase2 || {};
    const posture = data.market_posture || {};
    const decisions = data.decisions || [];
    const blocked = data.blocked_by_safety || [];
    const execPlan = data.execution_plan || [];
    const summary = data.execution_summary || {};

    // Map decisions to UI format (handle backend "reason" vs UI "reasons")
    const mappedDecisions = decisions.map(d => ({
        target: d.target,
        type: d.type,
        action: d.action,
        reasons: d.reasons || (d.reason ? [d.reason] : ["Decision based on analysis"])
    }));

    // Map allowed actions from execution plan
    const allowedActions = execPlan.map(a => ({
        symbol: a.symbol,
        action: a.action,
        reason: a.reason || "Approved by safety"
    }));

    // Map blocked actions
    const blockedActions = blocked.map(b => ({
        symbol: b.target,
        action: b.action,
        safetyReason: b.blocking_guard || b.reason_blocked || b.reason || "Safety violation"
    }));

    return {
        input: {
            positions: inputStats.positions || 0,
            candles: inputStats.candles || 0,
            headlines: inputStats.headlines || 0
        },
        phase2: {
            volatility: phase2.volatility_state || "STABLE",
            volatilityExplanation: phase2.volatility_explanation || "Volatility analysis complete",
            newsScore: phase2.news_score || 50,
            newsExplanation: phase2.news_explanation || "News sentiment analyzed",
            confidence: phase2.sector_confidence || 50,
            confidenceExplanation: phase2.confidence_explanation || "Confidence calculated"
        },
        phase3: {
            posture: posture.market_posture || "NEUTRAL",
            risk: posture.risk_level || "MEDIUM",
            reason: (posture.reasons && posture.reasons[0]) || "Decision based on analysis",
            decisions: mappedDecisions
        },
        phase4: {
            allowed: allowedActions,
            blocked: blockedActions,
            summary: {
                decision: summary.decision || posture.market_posture || "NEUTRAL",
                proposed: summary.actions_proposed || allowedActions.length,
                blocked: summary.actions_blocked || blockedActions.length,
                mode: summary.final_mode || "STANDARD"
            }
        }
    };
}

// =============================================================================
// RENDER FUNCTIONS
// =============================================================================

function renderStep1(data) {
    return `
        <div class="step">
            <div class="step-header">
                <span class="step-number blue">1</span>
                <span class="step-title">Input Data</span>
                <span class="step-label">Raw Data</span>
            </div>
            <div class="step-content">
                <div class="input-stats">
                    <div class="input-stat">
                        <span class="input-stat-icon">📊</span>
                        <span class="input-stat-label">Positions loaded:</span>
                        <span class="input-stat-value">${safeValue(data.positions)}</span>
                    </div>
                    <div class="input-stat">
                        <span class="input-stat-icon">📈</span>
                        <span class="input-stat-label">Market candles:</span>
                        <span class="input-stat-value">${safeValue(data.candles)} (15m)</span>
                    </div>
                    <div class="input-stat">
                        <span class="input-stat-icon">📰</span>
                        <span class="input-stat-label">News headlines:</span>
                        <span class="input-stat-value">${safeValue(data.headlines)}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderStep2(data) {
    const volClass = getVolatilityClass(data.volatility);
    const newsClass = getScoreClass(data.newsScore);
    const confClass = getScoreClass(data.confidence);

    return `
        <div class="step">
            <div class="step-header">
                <span class="step-number yellow">2</span>
                <span class="step-title">Market Perception</span>
                <span class="step-label">Phase 2 • Signals</span>
            </div>
            <div class="step-content">
                <div class="signal-grid">
                    <div class="signal-card">
                        <div class="signal-icon">📉</div>
                        <div class="signal-label">Volatility State</div>
                        <div class="signal-value ${volClass}">${safeValue(data.volatility)}</div>
                        <div class="signal-explanation">${safeValue(data.volatilityExplanation)}</div>
                    </div>
                    <div class="signal-card">
                        <div class="signal-icon">📰</div>
                        <div class="signal-label">News Score</div>
                        <div class="signal-value ${newsClass}">${safeValue(data.newsScore)}/100</div>
                        <div class="signal-explanation">${safeValue(data.newsExplanation)}</div>
                    </div>
                    <div class="signal-card">
                        <div class="signal-icon">🎯</div>
                        <div class="signal-label">Sector Confidence</div>
                        <div class="signal-value ${confClass}">${safeValue(data.confidence)}/100</div>
                        <div class="signal-explanation">${safeValue(data.confidenceExplanation)}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderStep3(data) {
    const postureClass = getPostureClass(data.posture);
    const riskClass = getRiskClass(data.risk);

    const decisionsHTML = (data.decisions || []).map((d, i) => {
        const actionClass = getActionClass(d.action);
        const reasonsHTML = (d.reasons || []).map(r => `<li>${r}</li>`).join("");

        return `
            <div class="decision-card" data-index="${i}">
                <div class="decision-header" onclick="toggleDecision(${i})">
                    <div class="decision-left">
                        <span class="decision-symbol">${safeValue(d.target)}</span>
                        <span class="decision-type">${safeValue(d.type)}</span>
                    </div>
                    <span class="decision-action ${actionClass}">${safeValue(d.action)}</span>
                    <span class="decision-toggle">
                        WHY? <span class="decision-toggle-icon">▼</span>
                    </span>
                </div>
                <div class="decision-reasons">
                    <div class="reasons-title">Reasoning</div>
                    <ul class="reasons-list">
                        ${reasonsHTML}
                    </ul>
                </div>
            </div>
        `;
    }).join("");

    return `
        <div class="step">
            <div class="step-header">
                <span class="step-number purple">3</span>
                <span class="step-title">Decision & Reasoning</span>
                <span class="step-label">Phase 3 • Thinking</span>
            </div>
            <div class="step-content">
                <div class="posture-banner">
                    <span class="posture-badge ${postureClass}">${safeValue(data.posture)}</span>
                    <span class="risk-indicator">
                        Risk Level: <span class="risk-tag ${riskClass}">${safeValue(data.risk)}</span>
                    </span>
                    <div class="posture-reason">"${safeValue(data.reason)}"</div>
                </div>
                <div class="decision-list">
                    ${decisionsHTML}
                </div>
            </div>
        </div>
    `;
}

function renderStep4(data) {
    const allowedHTML = (data.allowed || []).map(a => `
        <div class="safety-item allowed">
            <span class="safety-status">✓</span>
            <span class="safety-symbol">${safeValue(a.symbol)}</span>
            <span class="safety-action">→ ${safeValue(a.action)}</span>
        </div>
    `).join("");

    let blockedHTML = "";
    if (data.blocked && data.blocked.length > 0) {
        blockedHTML = data.blocked.map(b => `
            <div class="safety-item blocked">
                <span class="safety-status">✕</span>
                <span class="safety-symbol">${safeValue(b.symbol)}</span>
                <span class="safety-action">→ ${safeValue(b.action)}</span>
                <span class="safety-reason">${safeValue(b.safetyReason)}</span>
            </div>
        `).join("");
    } else {
        blockedHTML = `
            <div class="safety-success">
                <span>✓</span>
                <span>No actions were blocked by safety guardrails.</span>
            </div>
        `;
    }

    return `
        <div class="step">
            <div class="step-header">
                <span class="step-number red">4</span>
                <span class="step-title">Safety Gate</span>
                <span class="step-label">Phase 4 • Guards</span>
            </div>
            <div class="step-content">
                <div class="safety-section">
                    <div class="safety-title">
                        <span class="safety-icon">✓</span> Allowed Actions
                    </div>
                    <div class="safety-list">
                        ${allowedHTML}
                    </div>
                </div>
                <div class="safety-section">
                    <div class="safety-title">
                        <span class="safety-icon">🛡️</span> Blocked Actions
                    </div>
                    <div class="safety-list">
                        ${blockedHTML}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderStep5(data) {
    const summary = data.summary || {};

    return `
        <div class="step">
            <div class="step-header">
                <span class="step-number green">5</span>
                <span class="step-title">Execution Plan</span>
                <span class="step-label">Final Output</span>
            </div>
            <div class="step-content">
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Final Decision</div>
                        <div class="summary-value">${safeValue(summary.decision)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Actions Proposed</div>
                        <div class="summary-value">${safeValue(summary.proposed)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Actions Blocked</div>
                        <div class="summary-value">${safeValue(summary.blocked)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Final Mode</div>
                        <div class="summary-value">${safeValue(summary.mode)}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderPipeline(scenario) {
    const container = document.getElementById("pipeline");
    const emptyState = document.getElementById("empty-state");

    if (emptyState) {
        emptyState.style.display = "none";
    }

    const step1 = renderStep1(scenario.input || {});
    const step2 = renderStep2(scenario.phase2 || {});
    const step3 = renderStep3(scenario.phase3 || {});
    const step4 = renderStep4(scenario.phase4 || {});
    const step5 = renderStep5(scenario.phase4 || {});

    container.innerHTML = step1 + step2 + step3 + step4 + step5;
}

function showLoadingState() {
    const container = document.getElementById("pipeline");
    const emptyState = document.getElementById("empty-state");

    if (emptyState) {
        emptyState.style.display = "none";
    }

    container.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <div class="loading-text">Running AI Agent Pipeline...</div>
            <div class="loading-subtext">Executing Phase 2 → Phase 3 → Phase 4</div>
        </div>
    `;
}

function showErrorState(message) {
    const container = document.getElementById("pipeline");
    container.innerHTML = `
        <div class="error-state">
            <div class="error-icon">⚠️</div>
            <div class="error-title">Backend Connection Failed</div>
            <div class="error-message">${message}</div>
            <div class="error-hint">Make sure Flask backend is running: <code>python backend/app.py</code></div>
        </div>
    `;
}

// =============================================================================
// INTERACTIVITY
// =============================================================================

function toggleDecision(index) {
    const cards = document.querySelectorAll(".decision-card");
    const card = cards[index];
    if (card) {
        card.classList.toggle("expanded");
    }
}

// =============================================================================
// MAIN RUN FUNCTION (FETCHES FROM BACKEND)
// =============================================================================

async function runAgent() {
    showLoadingState();

    // Small delay for visual feedback
    await new Promise(resolve => setTimeout(resolve, 300));

    const backendData = await fetchFromBackend();

    if (backendData && !backendData.error) {
        // Transform backend data to UI format
        const uiData = transformBackendData(backendData);
        renderPipeline(uiData);

        // Update source indicator
        const sourceIndicator = document.getElementById("data-source");
        if (sourceIndicator) {
            sourceIndicator.textContent = "🔗 Live Python Backend";
            sourceIndicator.className = "data-source live";
        }
    } else {
        // Fallback to mock data
        console.warn("Using mock data fallback");
        showErrorState("Could not connect to Python backend. Is Flask running?");
    }

    // Scroll to first step
    setTimeout(function () {
        const firstStep = document.querySelector(".step");
        if (firstStep) {
            firstStep.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }, 100);
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

document.addEventListener("DOMContentLoaded", function () {
    const runBtn = document.getElementById("run-btn");

    if (runBtn) {
        runBtn.addEventListener("click", runAgent);
    }
});
