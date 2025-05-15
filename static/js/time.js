document.addEventListener("DOMContentLoaded", function () {
    const lastUpdateElement = document.getElementById("last-update");
    const sportButtons = document.querySelectorAll(".sport-btn");
    let currentSport = "nba"; // default
  
    function formatLocalTime(dateString) {
      try {
        const [datePart, timePart] = dateString.split(" ");
        const [year, month, day] = datePart.split("-").map(Number);
        const [hour, minute] = timePart.split(":").map(Number);
  
        const ampm = hour >= 12 ? "PM" : "AM";
        const hour12 = hour % 12 === 0 ? 12 : hour % 12;
        return `${month}-${day} ${hour12}:${minute.toString().padStart(2, "0")} ${ampm}`;
      } catch (err) {
        console.error("Error formatting date:", dateString, err);
        return "Invalid";
      }
    }
  
    function loadTimeForSport(sport) {
      const url = sport === "nba" ? "time.json" : `${sport}/time.json`;
  
      fetch(url)
        .then(response => {
          if (!response.ok) throw new Error(`Failed to fetch ${url}`);
          return response.json();
        })
        .then(data => {
          if (data.execution_time) {
            const formatted = formatLocalTime(data.execution_time);
            lastUpdateElement.innerHTML = `Most Recent Stat Update (${sport.toUpperCase()}): <strong>${formatted} ET</strong>`;
          } else {
            lastUpdateElement.innerHTML = `Most Recent Stat Update (${sport.toUpperCase()}): <strong>Unknown</strong>`;
          }
        })
        .catch(error => {
          console.error("Error loading time file:", error);
          lastUpdateElement.innerHTML = `Most Recent Stat Update (${sport.toUpperCase()}): <strong>Unavailable</strong>`;
        });
    }
  
    // Sport button click handling
    sportButtons.forEach(button => {
      button.addEventListener("click", function () {
        currentSport = this.getAttribute("data-sport");
        loadTimeForSport(currentSport);
      });
    });
  
    // Initial load
    loadTimeForSport(currentSport);
  });
  