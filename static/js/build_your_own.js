document.addEventListener("DOMContentLoaded", function () {
    const availablePicksList = document.getElementById("available-picks-list");
    const createdParlayList = document.getElementById("created-parlay-list");
    const boostBar = document.getElementById("boost-bar");
    const boostEdgeInfo = document.getElementById("boost-edge-info");
    const searchBar = document.getElementById("search-bar");
    const maxSelections = 3;
    let createdParlay = [];
    let availablePicks = [];
  
    // Fetch selections from the new route and store them globally
    fetch("/get_selections")
      .then(response => response.json())
      .then(data => {
        availablePicks = data;
        renderAvailablePicks();
      })
      .catch(error => console.error("Error loading selections:", error));
  
    // Filter available picks as user types in the available picks search bar
    searchBar.addEventListener("input", function () {
      renderAvailablePicks();
    });
  
    function renderAvailablePicks() {
      availablePicksList.innerHTML = "";
      const query = searchBar.value.toLowerCase();
      availablePicks.forEach(selection => {
        if (selection.toLowerCase().includes(query)) {
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
  
    // Listen for boost changes
    boostBar.addEventListener("input", function () {
      updateBoostEdgeInfo();
    });
  
    function addSelection(selection) {
      if (createdParlay.length >= maxSelections || createdParlay.includes(selection)) {
        return;
      }
      createdParlay.push(selection);
      renderCreatedParlay();
    }
  
    function removeSelection(selection) {
      createdParlay = createdParlay.filter(item => item !== selection);
      renderCreatedParlay();
    }
  
    // Assumes the odds are the third comma-separated value
    function extractOdds(selection) {
      const parts = selection.split(", ");
      return parseInt(parts[2]); // e.g., -145
    }
  
    // Convert American odds to implied probability (as a decimal)
    function calculateImpliedProbability(odds) {
      if (odds < 0) {
        return Math.abs(odds) / (Math.abs(odds) + 100);
      } else {
        return 100 / (odds + 100);
      }
    }
  
    // Calculate the combined implied odds for the created parlay
    function calculateParlayImpliedOdds() {
      if (createdParlay.length === 0) return null;
      let combinedProbability = createdParlay
        .map(extractOdds)
        .map(calculateImpliedProbability)
        .reduce((acc, prob) => acc * prob, 1);
      return { impliedProbability: combinedProbability };
    }
  
    // Render the created parlay list and update the boost edge info
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
  
    // Update the implied odds and edge display based on boost input
    function updateBoostEdgeInfo() {
      boostEdgeInfo.innerHTML = "";
      const oddsData = calculateParlayImpliedOdds();
      if (oddsData) {
        // Convert implied probability to percentage
        const impliedPercentage = oddsData.impliedProbability * 100;
        let innerHTML = `<p><strong>Implied Odds:</strong> ${impliedPercentage.toFixed(2)}%</p>`;
        const boost = parseFloat(boostBar.value) || 0;
        // Use new formulas only when 2 or 3 selections are made.
        if (createdParlay.length === 2) {
          // For 2 leggers: ((implied odds% x (3 + (3 x boost/100))) - 100)
          let edge = (impliedPercentage * (3 + (3 * boost / 100))) - 100;
          innerHTML += `<p><strong>Edge:</strong> ${edge.toFixed(2)}%</p>`;
        } else if (createdParlay.length === 3) {
          // For 3 leggers: ((implied odds% x (5 + (5 x boost/100))) - 100)
          let edge = (impliedPercentage * (5 + (5 * boost / 100))) - 100;
          innerHTML += `<p><strong>Edge:</strong> ${edge.toFixed(2)}%</p>`;
        }
        boostEdgeInfo.innerHTML = innerHTML;
      }
    }
  });
  