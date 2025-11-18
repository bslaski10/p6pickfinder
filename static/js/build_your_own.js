document.addEventListener("DOMContentLoaded", function () {
  const availablePicksList = document.getElementById("available-picks-list");
  const createdParlayList = document.getElementById("created-parlay-list");
  const boostBar = document.getElementById("boost-bar");
  const boostEdgeInfo = document.getElementById("boost-edge-info");
  const searchBar = document.getElementById("search-bar");
  const sportButtons = document.querySelectorAll(".sport-btn");
  const maxSelections = 3;
  let createdParlay = [];
  let availablePicks = [];
  let currentSport = "nfl"; // default

  // Base payout multipliers by sport and parlay size
  // (Feel free to adjust if your book rules differ)
  const BASE_PAYOUTS = {
    2: { nfl: 3.3, nba: 3.3, mlb: 3.3, nhl: 3.3, wnba: 2.75 },
    3: { nfl: 6.6, nba: 6.6, mlb: 6.6, nhl: 6.6, wnba: 4.4 }
  };

  function fetchSelections(sport) {
    fetch(`/get_selections?sport=${sport}`)
      .then(response => response.json())
      .then(data => {
        availablePicks = data;
        renderAvailablePicks();
      })
      .catch(error => console.error("Error loading selections:", error));
  }

  // Handle sport button clicks
  sportButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      sportButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentSport = btn.getAttribute("data-sport");
      fetchSelections(currentSport);
      // Clear created parlay when switching sports
      createdParlay = [];
      renderCreatedParlay();
    });
  });

  // Initial fetch (NFL)
  fetchSelections(currentSport);

  // Search filtering
  searchBar.addEventListener("input", function () {
    renderAvailablePicks();
  });

  function renderAvailablePicks() {
    availablePicksList.innerHTML = "";
    const query = (searchBar.value || "").toLowerCase();
    availablePicks.forEach(selection => {
      if (String(selection).toLowerCase().includes(query)) {
        const selectionDiv = document.createElement("div");
        selectionDiv.className = "selection-box";

        const selectionText = document.createElement("span");
        selectionText.textContent = selection;

        const addButton = document.createElement("button");
        addButton.textContent = "+";
        addButton.className = "add-button";
        addButton.addEventListener("click", function () {
          addSelection(selection);
        });

        selectionDiv.appendChild(selectionText);
        selectionDiv.appendChild(addButton);
        availablePicksList.appendChild(selectionDiv);
      }
    });
  }

  boostBar.addEventListener("input", function () {
    updateBoostEdgeInfo();
  });

  function addSelection(selection) {
    if (createdParlay.length >= maxSelections || createdParlay.includes(selection)) return;
    createdParlay.push(selection);
    renderCreatedParlay();
  }

  function removeSelection(selection) {
    createdParlay = createdParlay.filter(item => item !== selection);
    renderCreatedParlay();
  }

  function extractOdds(selection) {
    const parts = String(selection).split(", ");
    // Expected format: "Name, over/under X Stat, -145, matchup, time"
    // Odds at index 2
    return parseInt(parts[2], 10);
  }

  function calculateImpliedProbability(odds) {
    let rawProb;
    if (odds < 0) {
      rawProb = Math.abs(odds) / (Math.abs(odds) + 100);
    } else {
      rawProb = 100 / (odds + 100);
    }
    // Apply 6.98% vig at leg level
    return rawProb / 1.0566;
  }

  function calculateParlayImpliedOdds() {
    if (createdParlay.length === 0) return null;
    const combinedProbability = createdParlay
      .map(extractOdds)
      .map(calculateImpliedProbability)
      .reduce((acc, prob) => acc * prob, 1);
    return { impliedProbability: combinedProbability };
  }

  function renderCreatedParlay() {
    createdParlayList.innerHTML = "";
    createdParlay.forEach(selection => {
      const selectionDiv = document.createElement("div");
      selectionDiv.className = "selection-box";

      const selectionText = document.createElement("span");
      selectionText.textContent = selection;

      const removeButton = document.createElement("button");
      removeButton.textContent = "x";
      removeButton.className = "remove-button";
      removeButton.addEventListener("click", function () {
        removeSelection(selection);
      });

      selectionDiv.appendChild(selectionText);
      selectionDiv.appendChild(removeButton);
      createdParlayList.appendChild(selectionDiv);
    });
    updateBoostEdgeInfo();
  }

  function updateBoostEdgeInfo() {
    boostEdgeInfo.innerHTML = "";
    const oddsData = calculateParlayImpliedOdds();
    if (!oddsData) return;

    const impliedPercentage = oddsData.impliedProbability * 100;
    let innerHTML = `<p><strong>Implied Odds:</strong> ${impliedPercentage.toFixed(2)}%</p>`;

    const boost = parseFloat(boostBar.value) || 0;
    const legs = createdParlay.length;

    // Determine base payout by sport and parlay length via table
    const sportTable = BASE_PAYOUTS[legs];
    const basePayout = sportTable ? sportTable[currentSport] : undefined;

    if (basePayout) {
      const payout = basePayout + (basePayout * boost / 100);
      const edge = (payout * oddsData.impliedProbability - 1) * 100;
      innerHTML += `<p><strong>Edge:</strong> ${edge.toFixed(2)}%</p>`;
    }

    boostEdgeInfo.innerHTML = innerHTML;
  }
});
