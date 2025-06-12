import stages from './stages.js';
import Stage from './stage.js';
import { drawHUD } from './hud.js';

export default class Game {
  constructor({ input, view, stages }) {
    this.input = input;
    this.view = view;
    this.stages = stages || [];
    this.stageIndex = 0;
    this.stage = null;
    this.frames = 0;
    this.lastFrame = 0;
    this.paused = false;

    this.loop = this.loop.bind(this);
    this.onGameOver = this.onGameOver.bind(this);
    this.onVictory = this.onVictory.bind(this);

    window.addEventListener('keydown', (e) => {
      if (e.code === 'KeyP') {
        this.paused = !this.paused;

        const pauseModal = document.getElementById("pauseModal");
        if (pauseModal) {
          pauseModal.style.display = this.paused ? "flex" : "none";
        }
      }
    });
  }

  async init() {
    await this.view.init();
  }

  start() {
    this.stage = new Stage(this.stages[this.stageIndex]);
    this.stage.on('gameOver', this.onGameOver);
    this.stage.on('victory', this.onVictory);
    requestAnimationFrame(this.loop);
  }

  loop(currentFrame) {
    const frameDelta = currentFrame - this.lastFrame;
    this.lastFrame = currentFrame;

    if (!this.paused) {
      this.stage.update(this.input, frameDelta);
      this.view.update(this.stage);

      const ctx = this.view.context;
      const sprite = this.view.sprite;
      const stage = this.stage;

      const totalSeconds = Math.floor(stage.time / 1000);
      const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
      const seconds = String(totalSeconds % 60).padStart(2, '0');
      const formattedTime = `${minutes}:${seconds}`;

      const remainingEnemies = stage.totalEnemyLimit - stage.spawnedEnemiesCount + stage.enemyTankCount;

      drawHUD(ctx, sprite.image, sprite.frames, stage.score, formattedTime, remainingEnemies);
    }

    requestAnimationFrame(this.loop);
  }

  onGameOver() {
    const defeatModal = document.getElementById('defeatModal');
    if (defeatModal) {
      defeatModal.classList.remove('hidden');
    }
    this.paused = true;
  }

  onVictory() {
    const stage = this.stage;
    const score = stage.score;
    const remainingTimeMs = stage.time;

    // Обчислення зірок
    const timeSpent = 60000 - remainingTimeMs;
    let stars = 1;
    if (timeSpent <= 40000) stars = 2;
    if (timeSpent <= 30000) stars = 3;

    // Відправка результатів на сервер
      const userId = window.userId;

      // Відправка результатів на сервер
      console.log("🎯 Sending progress...", {
        user_id: window.userId,
        score: score,
        stars: stars,
        level: this.stageIndex + 1
      });
      fetch("/game/victory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          score: score,
          stars: stars,
          level: this.stageIndex + 1
        })
      });



    showVictoryModal(score, remainingTimeMs);
    this.paused = true;
  }
}

function showVictoryModal(score, remainingTimeMs) {
  const starsEl = document.getElementById("victoryStars");
  const scoreEl = document.getElementById("victoryScore");
  const modalEl = document.getElementById("victoryModal");

  const timeSpent = 60000 - remainingTimeMs;

  let stars = "⭐";
  if (timeSpent <= 40000) stars = "⭐⭐";
  if (timeSpent <= 30000) stars = "⭐⭐⭐";

  if (starsEl) starsEl.textContent = stars;
  if (scoreEl) scoreEl.textContent = `Scores: ${score}`;
  if (modalEl) modalEl.classList.remove("hidden");
}
