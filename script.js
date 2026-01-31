/**
 * Phase 1 Frontend Logic
 * Simulation of data status only. No API calls.
 */

// Simulated State (Booleans)
// Simulated State (Booleans for Phase 1, Values for Phase 2)
const systemState = {
    // Phase 1 (Data Status)
    marketDataLoaded: false,
    portfolioLoaded: false,
    newsLoaded: false,
    
    // Phase 2 (Signals - Static Mocks)
    volatilityState: "MODERATE",
    newsScore: "NEUTRAL",
    sectorConfidence: "LOW"
};

// DOM Elements - Phase 1
const marketStatusEl = document.getElementById('market-status');
const portfolioStatusEl = document.getElementById('portfolio-status');
const newsStatusEl = document.getElementById('news-status');

// DOM Elements - Phase 2
const volatilityStateEl = document.getElementById('volatility-state');
const newsScoreEl = document.getElementById('news-score');
const sectorConfidenceEl = document.getElementById('sector-confidence');

/**
 * Updates the UI based on the current systemState.
 * Simple text toggle based on boolean values.
 */
function updateUI() {
    // Phase 1: Data Status
    marketStatusEl.innerText = systemState.marketDataLoaded ? "Data Loaded" : "Not Loaded";
    portfolioStatusEl.innerText = systemState.portfolioLoaded ? "Data Loaded" : "Not Loaded";
    newsStatusEl.innerText = systemState.newsLoaded ? "Data Loaded" : "Not Loaded";

    // Phase 2: Signals (Display Static Values)
    volatilityStateEl.innerText = systemState.volatilityState;
    newsScoreEl.innerText = systemState.newsScore;
    sectorConfidenceEl.innerText = systemState.sectorConfidence;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log("Phase 1 & 2 Frontend Initialized");
    updateUI();
});

// Expose state globally for manual testing in console if needed
window.toggleState = function(section) {
    if (section === 'market') systemState.marketDataLoaded = !systemState.marketDataLoaded;
    if (section === 'portfolio') systemState.portfolioLoaded = !systemState.portfolioLoaded;
    if (section === 'news') systemState.newsLoaded = !systemState.newsLoaded;
    updateUI();
    console.log(`State updated for ${section}`, systemState);
};
