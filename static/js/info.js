document.addEventListener("DOMContentLoaded", function() {
  const infoBtn = document.getElementById("info-btn");
  const infoBox = document.getElementById("info-box");
  const scheduleBtn = document.getElementById("schedule-btn");
  const scheduleBox = document.getElementById("schedule-box");

  if (infoBtn && infoBox) {
      infoBtn.addEventListener("click", function() {
          if (infoBox.style.display === "none") {
              infoBox.style.display = "block";
              scheduleBox.style.display = "none"; // Hide schedule if open
          } else {
              infoBox.style.display = "none";
          }
      });
  }

  if (scheduleBtn && scheduleBox) {
      scheduleBtn.addEventListener("click", function() {
          if (scheduleBox.style.display === "none") {
              scheduleBox.style.display = "block";
              infoBox.style.display = "none"; // Hide info if open
          } else {
              scheduleBox.style.display = "none";
          }
      });
  }
});
