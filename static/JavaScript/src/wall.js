import { TILE_SIZE } from '/static/JavaScript/src/constants.js';

import GameObject from '/static/JavaScript/src/game-object.js';

export default class Wall extends GameObject {
    constructor({ type, ...rest }) {
        super(rest);

        this.width = TILE_SIZE;
        this.height = TILE_SIZE;
        this.spriteIndex = 0;
        this.damage = 0;
    }

    get sprite() {
        return this.sprites[this.spriteIndex];
    }
}