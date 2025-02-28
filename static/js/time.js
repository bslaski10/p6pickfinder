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
                document.getElementById("last-update").textContent = `Most Recent Stat Update: ${data.execution_time}`;
            } else {
                console.error("Error: 'execution_time' field not found in time.json");
            }
        })
        .catch(error => console.error("Error fetching time.json:", error));
});
