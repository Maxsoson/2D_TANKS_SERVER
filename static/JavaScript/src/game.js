import stages from './stages.js';
import Stage from './stage.js';

export default class Game {
    constructor({ input, view }) {
        this.input = input;
        this.view = view;
        this.stages = stages;
        this.player1 = null;
        this.player2 = null;
        this.stage = null;
        this.stageIndex = 0;
        this.frames = 0;
        this.lastFrame = 0;
        this.paused = false; // ⏸

        this.loop = this.loop.bind(this);
        this.onGameOver = this.onGameOver.bind(this);

        // 🎮 Обробка клавіші "P" — пауза
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
        console.log('GAME OVER');
    }
}
