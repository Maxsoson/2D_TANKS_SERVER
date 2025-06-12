import { Keys, Direction, PLAYER1_TANK_POSITION, PLAYER1_TANK_SPRITES, TANK_SPEED } from '/static/JavaScript/src/constants.js';
import { getDirectionForKeys, getAxisForDirection, getValueForDirection } from '/static/JavaScript/src/utils.js';
import Tank from '/static/JavaScript/src/tank.js';

export default class PlayerTank extends Tank {
    constructor(args, stage) {
        super(args);

        this.stage = stage;
        this.type = 'playerTank';
        this.x = PLAYER1_TANK_POSITION[0];
        this.y = PLAYER1_TANK_POSITION[1];
        this.direction = Direction.UP;
        this.speed = TANK_SPEED;
        this.sprites = PLAYER1_TANK_SPRITES;

        this.lastShotTime = 0;
        this.shotCooldown = 1250; // 1.25 секунди
        this.cooldown = 0;
    }

    update({ input, frameDelta, world }) {
        // Рух
        if (input.has(Keys.UP, Keys.RIGHT, Keys.DOWN, Keys.LEFT)) {
            const direction = getDirectionForKeys(input.keys);
            const axis = getAxisForDirection(direction);
            const value = getValueForDirection(direction);

            this.turn(direction);
            this.move(axis, value);
            this.animate(frameDelta);

            if (world.isOutOfBounds(this) || world.hasCollision(this)) {
                this.move(axis, -value);
            }
        }

        // Стрільба з cooldown
        if (input.keys.has(Keys.SPACE)) {
            const now = Date.now();
            if (now - this.lastShotTime >= this.shotCooldown) {
                this.fire();
                this.lastShotTime = now;
                this.cooldown = this.shotCooldown;
            }
        }

        // Зменшення cooldown
        if (this.cooldown > 0) {
            this.cooldown -= frameDelta;
            if (this.cooldown < 0) this.cooldown = 0;
        }
    }
}
