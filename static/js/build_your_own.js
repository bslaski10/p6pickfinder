document.addEventListener("DOMContentLoaded", function () {
  const availablePicksList = document.getElementById("available-picks-list");
  const searchBar = document.getElementById("search-bar");
  const createdParlayList = document.getElementById("created-parlay-list");
  const maxSelections = 3;
  let createdParlay = [];
  let availablePicks = [];

  // Fetch selections from the new route and store them globally
  fetch("/get_selections")
      .then(response => response.json())
      .then(data => {
          availablePicks = data; // Store the full list of selections
          renderAvailablePicks(); // Render initially (all picks)
      })
      .catch(error => console.error("Error loading selections:", error));

  // Listen for changes on the search bar and re-render available picks
  searchBar.addEventListener("input", function () {
      renderAvailablePicks();
  });

  // Function to render available picks filtered by search input
  function renderAvailablePicks() {
      availablePicksList.innerHTML = "";
      const query = searchBar.value.toLowerCase();
      availablePicks.forEach(selection => {
          // Check if the selection contains the search query (case-insensitive)
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

  // Adds a selection to the created parlay if not already added and within limit
  function addSelection(selection) {
      if (createdParlay.length >= maxSelections || createdParlay.includes(selection)) {
          return;
      }
      createdParlay.push(selection);
      renderCreatedParlay();
  }

  // Removes a selection from the created parlay
  function removeSelection(selection) {
      createdParlay = createdParlay.filter(item => item !== selection);
      renderCreatedParlay();
  }

  // Extract the odds from the selection string (assumes odds is the third comma-separated value)
  function extractOdds(selection) {
      const parts = selection.split(", ");
      const odds = parseInt(parts[2]); // e.g., -145
      return odds;
  }

  // Convert American odds to an implied probability (as a decimal)
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

  // Render the created parlay and display implied odds and edge if applicable
  function renderCreatedParlay() {
      createdParlayList.innerHTML = "";

      // Render each selected pick
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

      // Display the combined implied odds and edge (if applicable)
const oddsData = calculateParlayImpliedOdds();
if (oddsData) {
    const oddsDiv = document.createElement("div");
    oddsDiv.className = "parlay-odds";
    let innerHTML = `<p><strong>Implied Odds:</strong> ${(oddsData.impliedProbability * 100).toFixed(2)}%</p>`;
    
    // Show the edge only for 2 or 3 selections using the new formula
    if (createdParlay.length === 2) {
        let edge = (oddsData.impliedProbability * 3) - 1;
        innerHTML += `<p><strong>Edge:</strong> ${(edge * 100).toFixed(2)}%</p>`;
    } else if (createdParlay.length === 3) {
        let edge = (oddsData.impliedProbability * 5) - 1;
        innerHTML += `<p><strong>Edge:</strong> ${(edge * 100).toFixed(2)}%</p>`;
    }
    oddsDiv.innerHTML = innerHTML;
    createdParlayList.appendChild(oddsDiv);
}
  }
});
