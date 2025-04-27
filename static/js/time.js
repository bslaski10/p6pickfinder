document.addEventListener("DOMContentLoaded", function () {
    let currentSport = 'nba';  // Default sport
    let executionTimes = {};

    // Load the time.json file
    fetch('selections/time.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            executionTimes = data;
            updateTime(currentSport); // Show default sport time on page load
        })
        .catch(error => console.error("Error fetching time.json:", error));

    // Helper function to format time as mm-dd-time(am/pm): 02-28 7:14 pm
    function formatTime(executionTime) {
        const date = new Date(executionTime);

        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        let hours = date.getHours();
        const minutes = String(date.getMinutes()).padStart(2, '0');

        const ampm = hours >= 12 ? 'pm' : 'am';
        hours = hours % 12;
        hours = hours ? hours : 12;

        return `${month}-${day} ${hours}:${minutes} ${ampm}`;
    }

    // Update the last update time display
    function updateTime(sport) {
        const timeElement = document.getElementById("last-update");

        if (executionTimes[sport]) {
            const formattedTime = formatTime(executionTimes[sport]);
            timeElement.innerHTML = `Most Recent Stat Update (${sport.toUpperCase()}): <strong>${formattedTime}</strong>`;
        } else {
            timeElement.innerHTML = `Most Recent Stat Update (${sport.toUpperCase()}): <strong>Unknown</strong>`;
        }
    }

    // Add event listeners to sport selection buttons
    document.getElementById("nbaBtn").addEventListener("click", function() {
        currentSport = 'nba';
        updateTime(currentSport);
    });

    document.getElementById("mlbBtn").addEventListener("click", function() {
        currentSport = 'mlb';
        updateTime(currentSport);
    });

    document.getElementById("nhlBtn").addEventListener("click", function() {
        currentSport = 'nhl';
        updateTime(currentSport);
    });
});


// Helper function to format time as mm-dd-time(am/pm): 02-28 7:14 pm
function formatTime(executionTime) {
    const date = new Date(executionTime);  // Convert the string into a Date object

    const month = String(date.getMonth() + 1).padStart(2, '0');  // Get month (0-based, so add 1)
    const day = String(date.getDate()).padStart(2, '0');  // Get day
    let hours = date.getHours();  // Get hours in 24-hour format
    const minutes = String(date.getMinutes()).padStart(2, '0');  // Get minutes

    // Determine am/pm
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;  // Convert to 12-hour format
    hours = hours ? hours : 12;  // Handle 12 as 12pm, not 0
    const formattedTime = `${month}-${day} ${hours}:${minutes} ${ampm}`;

    return formattedTime;
}
