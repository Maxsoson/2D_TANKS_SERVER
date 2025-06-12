document.addEventListener("DOMContentLoaded", async function () {
    const leaderboardTable = document.querySelector("#leaderboard tbody");

    function renderLeaderboard(players) {
        leaderboardTable.innerHTML = "";

        players
            .sort((a, b) => b.score - a.score)
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

    try {
        const response = await fetch("/leaderboard");
        if (!response.ok) throw new Error("Сервер повернув помилку");

        const data = await response.json();
        const players = data.map(entry => ({
            name: entry.nickname,   
            score: entry.total_score
        }));

        renderLeaderboard(players);
    } catch (error) {
        console.error("❌ Помилка завантаження рейтингу:", error);
        leaderboardTable.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; color: red;">Failed to load leaderboard data</td>
            </tr>
        `;
    }
});
