import { NUMBER_OF_UNITS, UNIT_SIZE, TILE_SIZE } from '/static/JavaScript/src/constants.js';
import { drawBorder } from '/static/JavaScript/src/border.js';
import { drawHUD } from '/static/JavaScript/src/hud.js'; // ⬅️ новий імпорт

export default class View {
  constructor(canvas, sprite) {
    this.canvas = canvas;
    this.context = canvas.getContext('2d');
    this.context.imageSmoothingEnabled = false;
    this.sprite = sprite;
    this.fieldOffsetX = 0; // Відступ для поля гри від лівої сторони
  }

  async init() {
    await this.sprite.load();
  }

  update(stage) {
    this.clearScreen();

    // Малюємо рамку
    if (
      this.sprite.frames["border-top"] &&
      this.sprite.frames["border-left"] &&
      this.sprite.frames["border-corner"]
    ) {
      drawBorder(
        this.context,
        this.sprite.image,
        this.sprite.frames,
        this.canvas.width,
        this.canvas.height
      );
    }

    // Малюємо HUD
    drawHUD(
      this.context,
      this.sprite.image,
      this.sprite.frames
    );

    this.renderStage(stage);
  }

  renderStage(stage) {
    for (const object of stage.objects) {
      const { x, y, width, height, sprite } = object;

      if (!sprite) continue;

      this.context.drawImage(
        this.sprite.image,
        ...sprite,
        x + this.fieldOffsetX, y, width, height // Зсув на X
      );

      if (object.debug) {
        this.context.strokeStyle = '#ff0000';
        this.context.lineWidth = 2;
        this.context.strokeRect(x + this.fieldOffsetX + 1, y + 1, width - 2, height - 2);
        object.debug = false;
      }
    }
  }

  renderGrid() {
    for (let y = 0; y < NUMBER_OF_UNITS; y++) {
      for (let x = 0; x < NUMBER_OF_UNITS; x++) {
        this.context.strokeStyle = '#ffffff';
        this.context.lineWidth = .2;
        this.context.strokeRect(
          x * UNIT_SIZE + this.fieldOffsetX + 1,
          y * UNIT_SIZE + 1,
          UNIT_SIZE - 2,
          UNIT_SIZE - 2
        );
      }
    }

    for (let y = 0; y < NUMBER_OF_UNITS * 2; y++) {
      for (let x = 0; x < NUMBER_OF_UNITS * 2; x++) {
        this.context.strokeStyle = '#ffffff';
        this.context.lineWidth = .1;
        this.context.strokeRect(
          x * TILE_SIZE + this.fieldOffsetX + 1,
          y * TILE_SIZE + 1,
          TILE_SIZE - 2,
          TILE_SIZE - 2
        );
      }
    }
  }

  clearScreen() {
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}
