document.addEventListener("DOMContentLoaded", function() {
    const availablePicksList = document.getElementById("available-picks-list");
    const createdParlayList = document.getElementById("created-parlay-list");
    const maxSelections = 3;
    let createdParlay = [];
  
    // Fetch selections from the new route
    fetch("/get_selections")
      .then(response => response.json())
      .then(data => {
        // Assume data is an array of selection strings.
        data.forEach(selection => {
          // Create a container div for each selection
          const selectionDiv = document.createElement("div");
          selectionDiv.className = "selection-box";
  
          // Create a span to display the selection text
          const selectionText = document.createElement("span");
          selectionText.textContent = selection;
  
          // Create the add button with a plus sign
          const addButton = document.createElement("button");
          addButton.textContent = "+";
          addButton.className = "add-button";
          addButton.addEventListener("click", function() {
            addSelection(selection);
          });
  
          // Append text and button to the container, then add to the list
          selectionDiv.appendChild(selectionText);
          selectionDiv.appendChild(addButton);
          availablePicksList.appendChild(selectionDiv);
        });
      })
      .catch(error => console.error("Error loading selections:", error));
  
    function addSelection(selection) {
      // Do not add if already at the maximum or if the selection is already added.
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
  
    function renderCreatedParlay() {
      // Clear the current display
      createdParlayList.innerHTML = "";
      createdParlay.forEach(selection => {
        const selectionDiv = document.createElement("div");
        selectionDiv.className = "selection-box";
  
        const selectionText = document.createElement("span");
        selectionText.textContent = selection;
  
        // Create the remove button with an X
        const removeButton = document.createElement("button");
        removeButton.textContent = "x";
        removeButton.className = "remove-button";
        removeButton.addEventListener("click", function() {
          removeSelection(selection);
        });
  
        selectionDiv.appendChild(selectionText);
        selectionDiv.appendChild(removeButton);
        createdParlayList.appendChild(selectionDiv);
      });
    }
  });
  