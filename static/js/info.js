document.addEventListener("DOMContentLoaded", function () {
    const infoBtn = document.getElementById("info-btn");
    const scheduleBtn = document.getElementById("schedule-btn");
    const infoBox = document.getElementById("info-box");
    const scheduleBox = document.getElementById("schedule-box");
  
    infoBtn.addEventListener("click", function () {
      // Close scheduleBox if it's open
      if (scheduleBox && scheduleBox.style.display === "block") {
        scheduleBox.style.display = "none";
      }
  
      // Toggle infoBox
      if (infoBox.style.display === "block") {
        infoBox.style.display = "none";
      } else {
        infoBox.style.display = "block";
      }
    });
  
    scheduleBtn.addEventListener("click", function () {
      // Close infoBox if it's open
      if (infoBox && infoBox.style.display === "block") {
        infoBox.style.display = "none";
      }
  
      // Toggle scheduleBox
      if (scheduleBox.style.display === "block") {
        scheduleBox.style.display = "none";
      } else {
        scheduleBox.style.display = "block";
      }
    });
  });
  