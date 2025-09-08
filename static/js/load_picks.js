// load_picks.js

// Function to load initial parlays from picks.json when the page loads
async function loadInitialParlays() {
    try {
        // Use the global currentSport (defaults to "nfl")
        const sport = window.currentSport || "nfl";
        const response = await fetch(`/get_picks?sport=${sport}`); // Append sport as query parameter
        const data = await response.json();

        // Store parlays globally so they persist until the scan updates them
        window.parlaysData = data.parlays;

        // Display the parlays using the same function used after a scan
        updateParlaysDisplay();
    } catch (error) {
        console.error("Error loading initial picks:", error);
    }
}

// Function to update the parlays display based on the current odds mode remains unchanged...
function updateParlaysDisplay() {
    let twoLeggersHTML = "";
    let threeLeggersHTML = "";

    window.parlaysData.forEach(parlay => {
        let oddsLabel = showingVigOdds ? "Implied Odds" : "Implied Odds";
        let edgeLabel = showingVigOdds ? "Standard Edge" : "Edge";
        let oddsValue = showingVigOdds ? parlay.vig_odds : parlay.implied_odds;
        let edgeValue = showingVigOdds ? parlay.vig_edge : parlay.edge;

        let parlayHTML = `<div class="parlay-box">
            ${parlay.parlay.map(pick => `<p>${pick}</p>`).join('')}
            <p><strong>${oddsLabel}:</strong> ${oddsValue}</p>
            <p><strong>${edgeLabel}:</strong> ${edgeValue}</p>
        </div>`;

        if (parlay.parlay.length === 2) {
            twoLeggersHTML += parlayHTML;
        } else if (parlay.parlay.length === 3) {
            threeLeggersHTML += parlayHTML;
        }
    });

    document.getElementById('two-leggers').innerHTML = twoLeggersHTML;
    document.getElementById('three-leggers').innerHTML = threeLeggersHTML;
}

// Ensure the parlays are loaded when the page loads
document.addEventListener("DOMContentLoaded", loadInitialParlays);
