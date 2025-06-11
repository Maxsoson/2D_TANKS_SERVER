import stages from './stages.js';
import Stage from './stage.js';

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
    showVictoryModal(this.stage.score, this.stage.time);
    this.paused = true;
  }
}

// Функція для показу зірок і очок
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


