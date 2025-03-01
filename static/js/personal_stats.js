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
        
        // Check if any result is 'pending'
        const hasPending = parlay.result.includes("pend");

        // Overall parlay is considered a win only if every leg won, unless there's a pending leg
        const isParlayWin = !hasPending && parlay.result.every(r => r === "win");
        const isParlayLoss = !hasPending && parlay.result.some(r => r === "loss");

        // Set background color based on the results
        let backgroundColor;
        if (hasPending) {
            backgroundColor = "#ffff66"; // Yellow for pending
        } else if (isParlayWin) {
            backgroundColor = "#80ff63"; // Green for win
        } else if (isParlayLoss) {
            backgroundColor = "#ff7663"; // Red for loss
        } else {
            backgroundColor = "#ffffff"; // Default color for incomplete or mixed results
        }

        parlayDiv.classList.add("parlay-item");
        parlayDiv.style.backgroundColor = backgroundColor;
    
        // Build the list of legs with custom colored bullets
        let legsHtml = "<ul style='padding-left: 0;'>";
        for (let i = 0; i < parlay.legs.length; i++) {
            let leg = parlay.legs[i];
            let legResult = parlay.result[i];

            // Set bullet color based on individual leg result
            let bulletColor;
            if (legResult === "win") {
                bulletColor = "green"; // Green for winning leg
            } else if (legResult === "loss") {
                bulletColor = "red"; // Red for losing leg
            } else {
                bulletColor = "black"; // Default color
            }

            legsHtml += `<li style="list-style: none; margin-left: 0;">
                            <span style="color: ${bulletColor}; font-weight: bold; margin-right: 5px;">&#9679;</span>${leg}
                         </li>`;
        }
        legsHtml += "</ul>";
    
        parlayDiv.innerHTML = 
            `${legsHtml}
            <p>Base Pay: $${parlay.base_pay} &nbsp; Bonus: $${parlay.bonus_pay} &nbsp; Total Pay: $${parlay.total_pay}</p>
            <p>Bet Amount: $${parlay.bet_amount} &nbsp; Profit: <strong>$${parlay.profit}</strong></p>`;
        
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

    // Display Stats Below the Graph (with breakdown of winning picks)
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
        document.getElementById("total-profit").innerHTML = `<strong>Total Profit: $${totalProfit.toFixed(2)}</strong>`;
        document.getElementById("total-bets").innerText = `Total Bets: ${totalBets}`;
        document.getElementById("amount-bet").innerText = `Amount Bet: $${amountBet.toFixed(2)}`;
        document.getElementById("amount-won").innerText = `Amount Won: $${amountWon.toFixed(2)}`;

        // Clear previous breakdown stats
        let breakdownDiv = document.getElementById("breakdown-stats");
        breakdownDiv.innerHTML = "";

        // Depending on the filter, calculate breakdown stats for 2-leg and/or 3-leg parlays
        if (currentFilter === 'all') {
            const twoLegs = filteredParlays.filter(p => p.legs.length === 2);
            const threeLegs = filteredParlays.filter(p => p.legs.length === 3);
            if (twoLegs.length > 0) {
                breakdownDiv.innerHTML += `<h3>2 leggers</h3>`;
                breakdownDiv.innerHTML += getBreakdownHTML(twoLegs, 2);
            }
            if (threeLegs.length > 0) {
                breakdownDiv.innerHTML += `<h3>3 leggers</h3>`;
                breakdownDiv.innerHTML += getBreakdownHTML(threeLegs, 3);
            }
        } else if (currentFilter === '2legs') {
            breakdownDiv.innerHTML += `<h3>2 leggers</h3>`;
            breakdownDiv.innerHTML += getBreakdownHTML(filteredParlays, 2);
        } else if (currentFilter === '3legs') {
            breakdownDiv.innerHTML += `<h3>3 leggers</h3>`;
            breakdownDiv.innerHTML += getBreakdownHTML(filteredParlays, 3);
        }
    }

    // Helper function to generate breakdown HTML for a set of parlays
    // legsCount should be 2 or 3.
    function getBreakdownHTML(parlays, legsCount) {
        // Initialize counts for each outcome (e.g., "2/2", "1/2", "0/2" or "3/3", "2/3", "1/3", "0/3")
        let outcomes = {};
        for (let i = 0; i <= legsCount; i++) {
            outcomes[`${i}/${legsCount}`] = 0;
        }
        parlays.forEach(parlay => {
            let wins = parlay.result.filter(r => r === "win").length;
            let key = `${wins}/${legsCount}`;
            outcomes[key] = (outcomes[key] || 0) + 1;
        });
        let total = parlays.length;
        let html = "<ul style='list-style: none; padding-left: 0;'>";
        // Loop from highest wins to lowest wins
        for (let i = legsCount; i >= 0; i--) {
            let key = `${i}/${legsCount}`;
            let count = outcomes[key];
            let percent = total > 0 ? Math.round((count / total) * 100) : 0;
            html += `<li>${key}: ${count} - ${percent}%</li>`;
        }
        html += "</ul>";
        return html;
    }    
});
