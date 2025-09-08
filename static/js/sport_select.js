// static/js/sport_select.js

// Set default sport
window.currentSport = "nfl";

// Function to update the active button style
function updateActiveButton(selectedSport) {
  document.querySelectorAll('.sport-btn').forEach(btn => {
    btn.classList.remove('active-sport');
  });
  const activeBtn = document.querySelector(`.sport-btn[data-sport="${selectedSport}"]`);
  if (activeBtn) {
    activeBtn.classList.add('active-sport');
  }
}

// Add event listeners to sport buttons
document.querySelectorAll('.sport-btn').forEach(button => {
  button.addEventListener('click', function () {
    const sport = this.getAttribute('data-sport');
    window.currentSport = sport;
    updateActiveButton(sport);

    if (typeof loadInitialParlays === "function") {
      loadInitialParlays();
    }
  });
});

// On page load, simulate a click on the NFL button
document.addEventListener("DOMContentLoaded", function () {
  const defaultSport = "nfl";
  const defaultBtn = document.querySelector(`.sport-btn[data-sport="${defaultSport}"]`);
  if (defaultBtn) {
    defaultBtn.click(); // This triggers the event listener and loads the data
  }
});
