document.addEventListener("DOMContentLoaded", function() {
    let parlaysData = [];
    let currentFilter = 'all'; // 2 legs/3 legs/all legs
    let currentSport = 'all';  // all/nba/mlb/nhl

    // Fetch JSON data
    function fetchParlays() {
        fetch('/selections/profit.json')
            .then(response => response.json())
            .then(data => {
                parlaysData = data.parlays;
                renderParlays();
                renderChart();
                displayStats();
            })
            .catch(error => console.error("Error fetching profit.json:", error));
    }
    fetchParlays();

    // Event Listeners for leg filters
    document.getElementById("filter-all").addEventListener("click", () => updateView('all'));
    document.getElementById("filter-2").addEventListener("click", () => updateView('2legs'));
    document.getElementById("filter-3").addEventListener("click", () => updateView('3legs'));

    // Event Listeners for sport filters
    document.getElementById("filter-sport-all").addEventListener("click", () => updateSport('all'));
    document.getElementById("filter-nba").addEventListener("click", () => updateSport('nba'));
    document.getElementById("filter-mlb").addEventListener("click", () => updateSport('mlb'));
    document.getElementById("filter-nhl").addEventListener("click", () => updateSport('nhl'));
    document.getElementById("filter-wnba").addEventListener("click", () => updateSport('wnba'));

    function updateView(filter) {
        currentFilter = filter;
        renderParlays();
        updateChart();
        displayStats();
    }

    function updateSport(sport) {
        currentSport = sport;
        renderParlays();
        updateChart();
        displayStats();
    }

    // Add Parlay Button
    document.getElementById("add-parlay-btn").addEventListener("click", function() {
        showModal("add");
    });

    // Render parlays
    function renderParlays() {
        const container = document.getElementById("parlays-list");
        container.innerHTML = "";
    
        let filteredParlays = parlaysData.filter(parlay => {
            let legMatch = true;
            let sportMatch = true;
    
            if (currentFilter === '2legs') {
                legMatch = parlay.legs.length === 2;
            } else if (currentFilter === '3legs') {
                legMatch = parlay.legs.length === 3;
            }
    
            if (currentSport !== 'all') {
                sportMatch = parlay.sport === currentSport;
            }
    
            return legMatch && sportMatch;
        });
    
        filteredParlays.forEach((parlay, index) => {
            const parlayDiv = document.createElement("div");
            parlayDiv.classList.add("parlay-item");
            parlayDiv.style.position = "relative";  // <-- make sure relative positioning is set
    
            const hasPending = parlay.result.includes("pend");
            const isParlayWin = !hasPending && parlay.result.every(r => r === "win");
            const isParlayLoss = !hasPending && parlay.result.some(r => r === "loss");
    
            let backgroundColor;
            if (hasPending) {
                backgroundColor = "#ffff66"; 
            } else if (isParlayWin) {
                backgroundColor = "#80ff63"; 
            } else if (isParlayLoss) {
                backgroundColor = "#ff7663"; 
            } else {
                backgroundColor = "#ffffff";
            }
            parlayDiv.style.backgroundColor = backgroundColor;
            parlayDiv.style.paddingTop = "30px"; // <-- Extra space at top for the sport icon
    
            // Create the tiny sport icon (top-left)
            let sportIcon = "";
            if (parlay.sport === "nba") {
                sportIcon = "🏀";
            } else if (parlay.sport === "mlb") {
                sportIcon = "⚾";
            } else if (parlay.sport === "nhl") {
                sportIcon = "🏒";
            } else if (parlay.sport === "wnba") {
                sportIcon = "👟";
            }
    
            let sportLabel = "";
            if (sportIcon) {
                sportLabel = `<div title="${parlay.sport.toUpperCase()}" style="position: absolute; top: 5px; left: 5px; font-size: 20px;">${sportIcon}</div>`;
            }
    
            // Build legs HTML
            let legsHtml = "<ul style='padding-left: 0;'>";
            parlay.legs.forEach((leg, i) => {
                let legResult = parlay.result[i];
                let bulletColor = (legResult === "win") ? "green" : (legResult === "loss") ? "red" : "black";
                legsHtml += `<li style="list-style: none; margin-left: 0;">
                                <span style="color: ${bulletColor}; font-weight: bold; margin-right: 5px;">&#9679;</span>${leg}
                             </li>`;
            });
            legsHtml += "</ul>";
    
            // Inner HTML
            parlayDiv.innerHTML = 
                `${sportLabel}
                 ${legsHtml}
                 <p>Base Pay: $${parlay.base_pay} &nbsp; Bonus: $${parlay.bonus_pay} &nbsp; Total Pay: $${parlay.total_pay}</p>
                 <p>Bet Amount: $${parlay.bet_amount} &nbsp; Profit: <strong>$${parlay.profit}</strong></p>`;
    
            // Create Edit button
            const editBtn = document.createElement("button");
            editBtn.innerText = "Edit";
            editBtn.classList.add("edit-btn");
            editBtn.style.position = "absolute";
            editBtn.style.bottom = "5px";
            editBtn.style.right = "5px";
            editBtn.addEventListener("click", function() {
                showModal("edit", parlay, index);
            });
            parlayDiv.appendChild(editBtn);
    
            // Create Delete button
            const deleteBtn = document.createElement("button");
            deleteBtn.innerText = "X";
            deleteBtn.classList.add("delete-btn");
            deleteBtn.style.position = "absolute";
            deleteBtn.style.bottom = "5px";
            deleteBtn.style.left = "5px";
            deleteBtn.addEventListener("click", function() {
                if (confirm("Are you sure you want to delete this parlay?")) {
                    deleteParlay(index);
                }
            });
            parlayDiv.appendChild(deleteBtn);
    
            container.appendChild(parlayDiv);
        });
    }
    

    // Chart
    let chartInstance;
    function renderChart() {
        const ctx = document.getElementById('profitChart').getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '',
                    data: [],
                    borderColor: 'blue',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Bet Number' } },
                    y: { title: { display: true, text: 'Cumulative Profit' } }
                },
                plugins: { legend: { display: false } }
            }
        });
        updateChart();
    }

    function updateChart() {
        let filteredParlays = parlaysData.filter(parlay => {
            let legMatch = true;
            let sportMatch = true;
            if (currentFilter === '2legs') {
                legMatch = parlay.legs.length === 2;
            } else if (currentFilter === '3legs') {
                legMatch = parlay.legs.length === 3;
            }
            if (currentSport !== 'all') {
                sportMatch = parlay.sport === currentSport;
            }
            return legMatch && sportMatch;
        });

        const reversedParlays = [...filteredParlays].reverse();
        let labels = [0];
        let cumulativeProfit = 0;
        let cumulativeProfits = [0];
        reversedParlays.forEach((parlay, index) => {
            labels.push(index + 1);
            cumulativeProfit += parlay.profit;
            cumulativeProfits.push(cumulativeProfit);
        });
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = cumulativeProfits;
        chartInstance.update();
    }

    function displayStats() {
        let filteredParlays = parlaysData.filter(parlay => {
            let legMatch = true;
            let sportMatch = true;
            if (currentFilter === '2legs') {
                legMatch = parlay.legs.length === 2;
            } else if (currentFilter === '3legs') {
                legMatch = parlay.legs.length === 3;
            }
            if (currentSport !== 'all') {
                sportMatch = parlay.sport === currentSport;
            }
            return legMatch && sportMatch;
        });
    
        const totalProfit = filteredParlays.reduce((sum, parlay) => sum + parlay.profit, 0);
        const totalBets = filteredParlays.length;
        const amountBet = filteredParlays.reduce((sum, parlay) => sum + parlay.bet_amount, 0);
        const amountWon = filteredParlays.reduce((sum, parlay) => sum + parlay.total_pay, 0);
    
        // --- New: Calculate Leg Win% ---
        let totalLegs = 0;
        let totalLegWins = 0;
        filteredParlays.forEach(parlay => {
            parlay.result.forEach(result => {
                if (result === "win" || result === "loss" || result === "pending") {
                    totalLegs += 1;
                    if (result === "win") {
                        totalLegWins += 1;
                    }
                }
            });
        });
    
        let legWinPercentage = (totalLegs > 0) ? (totalLegWins / totalLegs) * 100 : 0;
    
        // Update DOM
        document.getElementById("total-profit").innerHTML = `<strong>Total Profit: $${totalProfit.toFixed(2)}</strong>`;
        document.getElementById("total-bets").innerText = `Total Bets: ${totalBets}`;
        document.getElementById("amount-bet").innerText = `Amount Bet: $${amountBet.toFixed(2)}`;
        document.getElementById("amount-won").innerText = `Amount Won: $${amountWon.toFixed(2)}`;
    
        // --- New: Insert Leg Win% stat after amount-won ---
        let legWinStat = document.getElementById("leg-win-stat");
        if (!legWinStat) {
            legWinStat = document.createElement("p");
            legWinStat.id = "leg-win-stat";
            document.getElementById("stats").insertBefore(legWinStat, document.getElementById("breakdown-stats"));
        }
        legWinStat.innerHTML = `<strong>Leg Win % = ${legWinPercentage.toFixed(2)}%</strong>`;
    
        // --- Breakdown ---
        let breakdownDiv = document.getElementById("breakdown-stats");
        breakdownDiv.innerHTML = "";
    
        if (currentFilter === 'all') {
            const twoLegs = filteredParlays.filter(p => p.legs.length === 2);
            const threeLegs = filteredParlays.filter(p => p.legs.length === 3);
            if (twoLegs.length > 0) {
                breakdownDiv.innerHTML += `<h3>2 leggers</h3>` + getBreakdownHTML(twoLegs, 2);
            }
            if (threeLegs.length > 0) {
                breakdownDiv.innerHTML += `<h3>3 leggers</h3>` + getBreakdownHTML(threeLegs, 3);
            }
        } else if (currentFilter === '2legs') {
            breakdownDiv.innerHTML += `<h3>2 leggers</h3>` + getBreakdownHTML(filteredParlays, 2);
        } else if (currentFilter === '3legs') {
            breakdownDiv.innerHTML += `<h3>3 leggers</h3>` + getBreakdownHTML(filteredParlays, 3);
        }
    }
    

    function getBreakdownHTML(parlays, legsCount) {
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
        for (let i = legsCount; i >= 0; i--) {
            let key = `${i}/${legsCount}`;
            let count = outcomes[key];
            let percent = total > 0 ? Math.round((count / total) * 100) : 0;
            html += `<li>${key}: ${count} - ${percent}%</li>`;
        }
        html += "</ul>";
        return html;
    }

    // --- Modal functionality (add/edit parlays) ---

    function showModal(mode, parlayData, index) {
        const modal = document.getElementById("parlay-modal");
        const form = document.getElementById("parlay-form");
        modal.dataset.mode = mode;

        if (mode === "edit" && parlayData) {
            modal.dataset.editIndex = index;
            form.elements["selection1"].value = parlayData.legs[0] || "";
            form.elements["selection2"].value = parlayData.legs[1] || "";
            form.elements["selection3"].value = parlayData.legs[2] || "";
            document.getElementsByName("result1").forEach(radio => {
                radio.checked = (radio.value === parlayData.result[0]);
            });
            document.getElementsByName("result2").forEach(radio => {
                radio.checked = (radio.value === parlayData.result[1]);
            });
            document.getElementsByName("result3").forEach(radio => {
                radio.checked = (radio.value === parlayData.result[2]);
            });
            form.elements["bet_amount"].value = parlayData.bet_amount;
            form.elements["base_pay"].value = parlayData.base_pay;
            form.elements["bonus_pay"].value = parlayData.bonus_pay;
            form.elements["sport"].value = parlayData.sport || "nba";
        } else {
            form.reset();
            delete modal.dataset.editIndex;
        }
        modal.style.display = "block";
    }

    document.querySelector("#parlay-modal .close").addEventListener("click", function() {
        document.getElementById("parlay-modal").style.display = "none";
    });

    document.getElementById("parlay-form").addEventListener("submit", function(e) {
        e.preventDefault();
        const modal = document.getElementById("parlay-modal");
        const mode = modal.dataset.mode;
        const formData = new FormData(e.target);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        if (mode === "add") {
            fetch('/add_parlay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === "success") {
                    parlaysData.push(result.parlay);
                    renderParlays();
                    updateChart();
                    displayStats();
                }
                modal.style.display = "none";
            })
            .catch(error => {
                console.error("Error adding parlay:", error);
                modal.style.display = "none";
            });
        } else if (mode === "edit") {
            data.index = modal.dataset.editIndex;
            fetch('/edit_parlay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === "success") {
                    parlaysData[parseInt(data.index)] = result.parlay;
                    renderParlays();
                    updateChart();
                    displayStats();
                }
                modal.style.display = "none";
            })
            .catch(error => {
                console.error("Error editing parlay:", error);
                modal.style.display = "none";
            });
        }
    });

    function deleteParlay(index) {
        fetch('/delete_parlay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index: index })
        })
        .then(response => response.json())
        .then(data => {
            parlaysData.splice(index, 1);
            renderParlays();
            updateChart();
            displayStats();
        })
        .catch(error => console.error("Error deleting parlay:", error));
    }
});
