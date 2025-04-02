document.addEventListener("DOMContentLoaded", function() {
    const leaderboardTable = document.querySelector("#leaderboard tbody");

    // Генеруємо 100 гравців із випадковими очками
    const players = [];
    for (let i = 1; i <= 100; i++) {
        players.push({ name: `Player${i}`, score: Math.floor(Math.random() * 5000) });
    }

    function updateLeaderboard() {
        leaderboardTable.innerHTML = ""; // Очищення перед оновленням

        players
            .sort((a, b) => b.score - a.score) // Сортуємо за очками
            .forEach((player, index) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${player.name}</td>
                    <td>${player.score}</td>
                `;
                leaderboardTable.appendChild(row);
            });
    }

    updateLeaderboard();
});

