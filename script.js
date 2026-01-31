/**
 * Phase 1 Frontend Logic
 * Simulation of data status only. No API calls.
 */

// Simulated State (Booleans)
const systemState = {
    marketDataLoaded: false,
    portfolioLoaded: false,
    newsLoaded: false
};

// DOM Elements
const marketStatusEl = document.getElementById('market-status');
const portfolioStatusEl = document.getElementById('portfolio-status');
const newsStatusEl = document.getElementById('news-status');

/**
 * Updates the UI based on the current systemState.
 * Simple text toggle based on boolean values.
 */
function updateUI() {
    // Market Data
    if (systemState.marketDataLoaded) {
        marketStatusEl.innerText = "Data Loaded";
    } else {
        marketStatusEl.innerText = "Not Loaded";
    }

    // Portfolio
    if (systemState.portfolioLoaded) {
        portfolioStatusEl.innerText = "Data Loaded";
    } else {
        portfolioStatusEl.innerText = "Not Loaded";
    }

    // News
    if (systemState.newsLoaded) {
        newsStatusEl.innerText = "Data Loaded";
    } else {
        newsStatusEl.innerText = "Not Loaded";
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log("Phase 1 Frontend Initialized");
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
