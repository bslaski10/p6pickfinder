document.addEventListener("DOMContentLoaded", function() {
    let parlaysData = [];
    let currentFilter = 'all';

    // Fetch JSON data
    fetch('/selections/profit.json')
        .then(response => response.json())
        .then(data => {
            parlaysData = data.parlays;
            renderParlays();
            renderChart();
            displayStats();  // Display stats below the graph
        })
        .catch(error => console.error("Error fetching profit.json:", error));

    // Event Listeners for filter buttons
    document.getElementById("filter-all").addEventListener("click", () => updateView('all'));
    document.getElementById("filter-2").addEventListener("click", () => updateView('2legs'));
    document.getElementById("filter-3").addEventListener("click", () => updateView('3legs'));

    function updateView(filter) {
        currentFilter = filter;
        renderParlays();
        updateChart();
        displayStats();  // Update stats after filter change
    }

    // Render parlays list (top to bottom)
    function renderParlays() {
        const container = document.getElementById("parlays-list");
        container.innerHTML = "";
        let filteredParlays = parlaysData;

        if (currentFilter === '2legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 2);
        } else if (currentFilter === '3legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 3);
        }

        filteredParlays.forEach(parlay => {
            const parlayDiv = document.createElement("div");
            parlayDiv.classList.add("parlay-item");
            parlayDiv.style.backgroundColor = parlay.result === "win" ? "#d4edda" : "#f8d7da"; // Green for win, red for loss

            let legsHtml = "<ul>";
            parlay.legs.forEach(leg => legsHtml += `<li>${leg}</li>`);
            legsHtml += "</ul>";

            parlayDiv.innerHTML = `
                ${legsHtml}
                <p>Base Pay: $${parlay.base_pay} &nbsp; Bonus: $${parlay.bonus_pay} &nbsp; Total Pay: $${parlay.total_pay}</p>
                <p>Bet Amount: $${parlay.bet_amount} &nbsp; Profit: <strong>$${parlay.profit}</strong></p>
            `;

            container.appendChild(parlayDiv);
        });
    }

    // Initialize Chart
    let chartInstance;
    function renderChart() {
        const ctx = document.getElementById('profitChart').getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '',  // Removed title for dataset
                    data: [],
                    borderColor: 'blue',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: {
                        title: { display: true, text: 'Bet Number' }
                    },
                    y: {
                        title: { display: true, text: 'Cumulative Profit' }
                    }
                },
                plugins: {
                    legend: { display: false }  // Disable legend
                }
            }
        });
        updateChart();
    }

    // Update Chart Data (Cumulative Profit)
    function updateChart() {
        let filteredParlays = parlaysData;
        if (currentFilter === '2legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 2);
        } else if (currentFilter === '3legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 3);
        }

        // Reverse the array only for the chart (bottom to top for graph)
        const reversedParlays = [...filteredParlays].reverse();  // Create a copy to avoid modifying the original data

        // Calculate cumulative profits
        let labels = [0];  // Start the graph at 0
        let cumulativeProfit = 0;
        let cumulativeProfits = [0];  // Start the graph at (0, 0)

        reversedParlays.forEach((parlay, index) => {
            labels.push(index + 1); // Sequential Bet number: 0, 1, 2, 3, ...
            cumulativeProfit += parlay.profit; // Add profit to cumulative total
            cumulativeProfits.push(cumulativeProfit); // Store cumulative profit at each bet
        });

        // Update chart with new labels and cumulative profit data
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = cumulativeProfits;
        chartInstance.update();
    }

    // Display Stats Below the Graph
    function displayStats() {
        let filteredParlays = parlaysData;

        if (currentFilter === '2legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 2);
        } else if (currentFilter === '3legs') {
            filteredParlays = parlaysData.filter(p => p.legs.length === 3);
        }

        const totalProfit = filteredParlays.reduce((sum, parlay) => sum + parlay.profit, 0);
        const totalBets = filteredParlays.length;
        const amountBet = filteredParlays.reduce((sum, parlay) => sum + parlay.bet_amount, 0);
        const amountWon = filteredParlays.reduce((sum, parlay) => sum + parlay.total_pay, 0);

        // Update the stats below the chart
        document.getElementById("total-profit").innerText = `Total Profit: $${totalProfit.toFixed(2)}`;
        document.getElementById("total-bets").innerText = `Total Bets: ${totalBets}`;
        document.getElementById("amount-bet").innerText = `Amount Bet: $${amountBet.toFixed(2)}`;
        document.getElementById("amount-won").innerText = `Amount Won: $${amountWon.toFixed(2)}`;
    }
});
