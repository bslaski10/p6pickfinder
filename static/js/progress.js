// js/progress.js

// Declare a global variable for the polling interval so it can be accessed in scan.js.
let progressInterval;

// Function to poll the progress endpoint and update the progress bar.
async function pollProgress() {
  try {
    const res = await fetch('/progress');
    const progressData = await res.json();
    const progress = progressData.progress;
    const message = progressData.message;
    document.getElementById('progress-bar').style.width = progress + '%';
    document.getElementById('progress-bar').setAttribute('aria-valuenow', progress);
    document.getElementById('progress-message').innerText = message;
    if (progress >= 100) {
      clearInterval(progressInterval);
    }
  } catch (error) {
    console.error("Error polling progress:", error);
  }
}
