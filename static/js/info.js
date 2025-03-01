document.addEventListener('DOMContentLoaded', function() {
    // Toggle the info box when the info button is clicked
    const infoButton = document.getElementById('info-btn');
    if (infoButton) {
      infoButton.addEventListener('click', function() {
        const infoBox = document.getElementById('info-box');
        infoBox.style.display = (infoBox.style.display === 'none' || infoBox.style.display === '') ? 'block' : 'none';
      });
    }
  });
  