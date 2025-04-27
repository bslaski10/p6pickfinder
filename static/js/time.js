document.addEventListener("DOMContentLoaded", function () {
    fetch('selections/time.json')  // Ensure this path is correct
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.execution_time) {
                const formattedTime = formatTime(data.execution_time);
                const timeElement = document.getElementById("last-update");
                timeElement.innerHTML = `Most Recent Stat Update: <strong>${formattedTime}</strong>`;
            } else {
                console.error("Error: 'execution_time' field not found in time.json");
            }
        })
        .catch(error => console.error("Error fetching time.json:", error));
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
