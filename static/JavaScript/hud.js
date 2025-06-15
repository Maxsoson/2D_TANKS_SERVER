export function setupHUD(stage) {
    const enemiesSpan  = document.getElementById("enemies");
    const livesSpan    = document.getElementById("lifes");
    const scoresSpan   = document.getElementById("scores");
    const timerSpan    = document.getElementById("timer");
    const cooldownSpan = document.getElementById("cooldown");

    if (!enemiesSpan || !livesSpan || !scoresSpan || !timerSpan || !cooldownSpan) {
        console.warn("HUD: не знайдені елементи");
        return;
    }

    function updateHUD() {
        const remaining = stage.totalEnemyLimit - stage.spawnedEnemiesCount + stage.enemyTankCount;
        enemiesSpan.textContent = remaining;

        if (stage.playerTank) {
            livesSpan.textContent = stage.player.lives + 1;

            const rawCd = stage.playerTank.cooldown ?? 0;
            const cdMs  = Math.max(0, Number.isFinite(rawCd) ? rawCd : 0);
            cooldownSpan.textContent = cdMs <= 0 ? "Ready" : (cdMs / 1000).toFixed(1) + "s";
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

    setInterval(updateHUD, 100);
    setInterval(updateTimer, 1000);
}
