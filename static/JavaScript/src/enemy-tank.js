import { Direction, ENEMY_TANK_START_POSITIONS, ENEMY_TANK_SPRITES, ENEMY_TANK_SPEED, ENEMY_TANK_TURN_TIMER_THRESHOLD } from './constants.js';
import { getAxisForDirection, getValueForDirection } from './utils.js';
import Tank from './tank.js';

export default class EnemyTank extends Tank {
    static createRandom() {
        const random = Math.floor(Math.random() * 3);
        const [x, y] = ENEMY_TANK_START_POSITIONS[random];
        const sprites = ENEMY_TANK_SPRITES[0];

        return new EnemyTank({ x, y, sprites });
    }

    constructor(args) {
        super(args);

        this.type = 'enemyTank';
        this.direction = Direction.DOWN;
        this.x = 0;
        this.y = 0;
        this.speed = ENEMY_TANK_SPEED;
        this.sprites = ENEMY_TANK_SPRITES[0];

        this.turnTimer = 0;

        // Стрільба
        this.fireCooldown = 0;
        this.FIRE_RATE = 1500; // 1.5 секунди
    }

    setPosition(positionIndex) {
        this.x = ENEMY_TANK_START_POSITIONS[positionIndex][0];
        this.y = ENEMY_TANK_START_POSITIONS[positionIndex][1];
    }

    update({ world, frameDelta }) {
        if (this.isDestroyed) {
            this.explode();
            this.destroy();
            return;
        }

        const direction = this.direction;
        const axis = getAxisForDirection(direction);
        const value = getValueForDirection(direction);

        this.move(axis, value);

        // Затримка перед наступним пострілом
        this.fireCooldown -= frameDelta;
        if (this.fireCooldown <= 0) {
            this.fire(); // викликається успадкований метод fire() з Tank
            this.fireCooldown = this.FIRE_RATE;
        }

        this.animate(frameDelta);

        const isOutOfBounds = world.isOutOfBounds(this);
        const hasCollision = world.hasCollision(this);

        if (isOutOfBounds || hasCollision) {
            this.move(axis, -value);

            if (this.shouldTurn(frameDelta)) {
                this.turnRandomly();
            }
        }
    }

    hit(bullet) {
        if (bullet.isFromEnemyTank) return;
        super.hit();
    }

    shouldTurn(frameDelta) {
        this.turnTimer += frameDelta;
        return this.turnTimer > ENEMY_TANK_TURN_TIMER_THRESHOLD;
    }

    turnRandomly() {
        const randomDirection = Math.floor(Math.random() * 4);
        this.turnTimer = 0;
        this.turn(randomDirection);
    }
}
