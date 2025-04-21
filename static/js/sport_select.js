// static/js/sport_select.js

// Set default sport to NBA.
window.currentSport = "nba";

// Function to update the active button style
function updateActiveButton(selectedSport) {
  // Remove active class from all sport buttons
  document.querySelectorAll('.sport-btn').forEach(btn => {
    btn.classList.remove('active-sport');
  });
  // Add active class to the selected sport button
  const activeBtn = document.querySelector(`.sport-btn[data-sport="${selectedSport}"]`);
  if (activeBtn) {
    activeBtn.classList.add('active-sport');
  }
}

// Add event listeners to sport buttons
document.querySelectorAll('.sport-btn').forEach(button => {
  button.addEventListener('click', function() {
    const sport = this.getAttribute('data-sport');
    window.currentSport = sport;  // Update global sport selection
    updateActiveButton(sport);
    
    // Reload the picks specific to the selected sport
    // Assumes loadInitialParlays in load_picks.js uses currentSport to fetch data.
    if (typeof loadInitialParlays === "function") {
      loadInitialParlays();
    }
  });
});

// Set initial active button on page load
document.addEventListener("DOMContentLoaded", function() {
  updateActiveButton(window.currentSport);
});
