export function setupHUD(stage) {
    const enemiesSpan = document.getElementById("enemies");
    const livesSpan = document.getElementById("lifes");
    const scoresSpan = document.getElementById("scores");
    const timerSpan = document.getElementById("timer");

    if (!enemiesSpan || !livesSpan || !scoresSpan || !timerSpan) {
        console.warn("HUD: не знайдені елементи");
        return;
    }

    function updateHUD() {
        const remaining = stage.totalEnemyLimit - stage.spawnedEnemiesCount + stage.enemyTankCount;
        enemiesSpan.textContent = remaining;

        if (stage.player) {
            livesSpan.textContent = stage.player.lives + 1;
        }

        scoresSpan.textContent = stage.score;
    }

    function updateTimer() {
        if (stage.time !== undefined) {
            const totalSeconds = Math.floor(stage.time / 1000);
            const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
            const seconds = String(totalSeconds % 60).padStart(2, '0');
            timerSpan.textContent = `${minutes}:${seconds}`;
        }
    }

    // Оновлення HUD та таймера
    setInterval(updateHUD, 100);
    setInterval(updateTimer, 1000);
}

