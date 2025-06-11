import Input from '/static/JavaScript/src/input.js';
import View from '/static/JavaScript/src/view.js';
import Game from '/static/JavaScript/src/game.js';
import Sprite from '/static/JavaScript/src/sprite.js';
import stages from '/static/JavaScript/src/stages.js';
import { setupHUD } from '/static/JavaScript/hud.js';

const canvas = document.querySelector('canvas');
const sprite = new Sprite('/static/Images/assets/sprite.png');

const game = new Game({
  input: new Input(),
  view: new View(canvas, sprite),
  stages
});

game.init().then(() => {
  game.start();
  setTimeout(() => {
    setupHUD(game.stage);
  }, 100);
});

// ПоразкаAdd commentMore actions
document.getElementById('restartBtn')?.addEventListener('click', () => {
  location.reload();
});
document.getElementById('menuBtn')?.addEventListener('click', () => {
  window.location.href = 'load_to_game_1.html';
});

// Перемога
document.getElementById('nextLevelBtn')?.addEventListener('click', () => {
  window.location.href = 'tanki.html'; 
});
document.getElementById('menuBtn2')?.addEventListener('click', () => {
  window.location.href = 'load_to_game_1.html';
});