export default class Sprite {
  constructor(src) {
    this.src = src;
    this.image = new Image();
    this.frames = {}; // створюємо frames тут
  }

  async load() {
    return new Promise((resolve, reject) => {
      this.image.src = this.src;
      this.image.addEventListener('load', () => {
        // додаємо координати рамки після завантаження
        this.frames["border-top"] = { x: 768, y: 0, w: 32, h: 8 };
        this.frames["border-left"] = { x: 768, y: 8, w: 8, h: 32 };
        this.frames["border-corner"] = { x: 800, y: 0, w: 8, h: 8 };
        this.frames["hud-ip"] = { x: 880, y: 368, w: 24, h: 8 };
        this.frames["hud-game"] = { x: 880, y: 384, w: 32, h: 8 };
        this.frames["hud-stage"] = { x: 880, y: 400, w: 32, h: 8 };
        this.frames["hud-flag"] = { x: 896, y: 464, w: 16, h: 16 };




        resolve(this);
      });
    });
  }
}
