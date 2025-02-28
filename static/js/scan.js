// Global variable to track odds mode (false = implied, true = vig)
let showingVigOdds = false;

// Function to trigger the scan process.
async function scanLocks() {
    // Reset progress UI.
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-bar').setAttribute('aria-valuenow', 0);
    document.getElementById('progress-message').innerText = 'Starting scan...';
    // Note: We do NOT clear the parlays display here, so the current picks remain visible.
  
    // Start polling progress every 2000ms using the pollProgress function from progress.js.
    progressInterval = setInterval(pollProgress, 2000);
  
    try {
      const response = await fetch('/get_locks');
      const data = await response.json();
      // Once the process is done, force the progress to 100%.
      document.getElementById('progress-bar').style.width = '100%';
      document.getElementById('progress-bar').setAttribute('aria-valuenow', 100);
      document.getElementById('progress-message').innerText = 'Done!';
  
      // Update the global parlaysData with the new picks and refresh the display.
      window.parlaysData = data.parlays;
      updateParlaysDisplay();
    } catch (error) {
      console.error("Error during scan:", error);
      clearInterval(progressInterval);
      document.getElementById('progress-message').innerText = 'Error during scan';
    }
}

// Function to update the parlays display based on the current odds mode.
function updateParlaysDisplay() {
    let twoLeggersHTML = "";
    let threeLeggersHTML = "";

    window.parlaysData.forEach(parlay => {
        // Use the same labels regardless of odds mode for now.
        // (Adjust as needed if you want different labels for vig vs. implied.)
        let oddsLabel = showingVigOdds ? "Implied Odds" : "Implied Odds";
        let edgeLabel = showingVigOdds ? "Edge" : "Edge";
        let oddsValue = showingVigOdds ? parlay.vig_odds : parlay.implied_odds;
        let edgeValue = showingVigOdds ? parlay.vig_edge : parlay.edge;

        let parlayHTML = `<div class="parlay-box">
            ${parlay.parlay.map(pick => `<p>${pick}</p>`).join('')}
            <p>${oddsLabel}:<strong>${oddsValue}</strong></p>
            <p>${edgeLabel}:<strong>${edgeValue}</strong></p>
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

// Function to toggle between Implied and Vig Odds.
function toggleOdds() {
    showingVigOdds = !showingVigOdds;
    document.getElementById('toggleOddsBtn').innerText = showingVigOdds ? "Show Implied Odds" : "Show Vig Odds";
    updateParlaysDisplay();
}
