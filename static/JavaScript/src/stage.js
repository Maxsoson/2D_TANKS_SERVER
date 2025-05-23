import { STAGE_SIZE, TILE_SIZE, TerrainType } from '/static/JavaScript/src/constants.js';
import EventEmitter from '/static/JavaScript/src/event-emitter.js';
import Base from '/static/JavaScript/src/base.js';
import BrickWall from '/static/JavaScript/src/brick-wall.js';
import SteelWall from '/static/JavaScript/src/steel-wall.js';
import Player from '/static/JavaScript/src/player.js';
import PlayerTank from '/static/JavaScript/src/player-tank.js';
import EnemyTank from '/static/JavaScript/src/enemy-tank.js';

export default class Stage extends EventEmitter {
    static createObject(type, args) {
        switch (type) {
            case TerrainType.BRICK_WALL: return new BrickWall(args);
            case TerrainType.STEEL_WALL: return new SteelWall(args);
        }
    }

    static createTerrain(map) {
        const objects = [];
        const mapSize = map.length * TILE_SIZE;
        const offsetX = Math.floor((STAGE_SIZE - mapSize) / 2);
        const offsetY = Math.floor((STAGE_SIZE - mapSize) / 2);

        for (let i = 0; i < map.length; i++) {
            for (let j = 0; j < map.length; j++) {
                const value = map[j][i];
                if (value) {
                    const object = Stage.createObject(value, {
                        x: i * TILE_SIZE + offsetX,
                        y: j * TILE_SIZE + offsetY
                    });
                    objects.push(object);
                }
            }
        }

        return objects;
    }

    static createEnemies(types) {
        return types.map(type => new EnemyTank({ type }));
    }

    constructor(data) {
        super();

        this.base = new Base();
        this.player = new Player();
        this.playerTank = new PlayerTank();
        this.enemyTanks = Stage.createEnemies(data.enemies);
        this.terrain = Stage.createTerrain(data.map);

        this.enemyTankCount = 0;
        this.enemyTankPositionIndex = 0;
        this.totalEnemyLimit = 9;
        this.spawnedEnemiesCount = 0;
        this.score = 0;

        this.time = 60000; // ⏱️ 60 секунд на гру

        this.objects = new Set([
            this.base,
            this.playerTank,
            ...this.terrain
        ]);

        this.init();
    }

    init() {
        this.base.on('destroyed', () => {
            this.emit('gameOver');
        });

        this.initPlayerEvents();

        this.enemyTanks.forEach(enemyTank => {
            enemyTank.on('fire', bullet => {
                this.objects.add(bullet);
                bullet.on('explode', explosion => {
                    this.objects.add(explosion);
                    explosion.on('destroyed', () => {
                        this.objects.delete(explosion);
                    });
                });
                bullet.on('destroyed', () => {
                    this.objects.delete(bullet);
                });
            });

            enemyTank.on('explode', explosion => {
                this.objects.add(explosion);
                explosion.on('destroyed', () => {
                    this.objects.delete(explosion);
                });
            });

            enemyTank.on('destroyed', () => {
                this.score += 100;
                this.removeEnemyTank(enemyTank);
            });
        });
    }

    initPlayerEvents() {
        this.playerTank.on('fire', bullet => {
            this.objects.add(bullet);

            bullet.on('explode', explosion => {
                this.objects.add(explosion);
                explosion.on('destroyed', () => {
                    this.objects.delete(explosion);
                });
            });

            bullet.on('destroyed', () => {
                this.objects.delete(bullet);
            });
        });

        this.playerTank.on('destroyed', tank => {
            this.objects.delete(tank);
            this.player.lives--;
            this.score = Math.max(0, this.score - 50);

            if (this.player.lives >= 0) {
                setTimeout(() => {
                    this.playerTank = new PlayerTank();
                    this.objects.add(this.playerTank);
                    this.initPlayerEvents();
                }, 1000);
            } else {
                this.emit('gameOver');
            }
        });
    }

    get width() { return STAGE_SIZE; }
    get height() { return STAGE_SIZE; }
    get top() { return 0; }
    get right() { return this.width; }
    get bottom() { return this.height; }
    get left() { return 0; }

    update(input, frameDelta) {
        const state = {
            input,
            frameDelta,
            world: this
        };

        // ⏱️ Зменшення часу
        if (this.time > 0) {
            this.time -= frameDelta;
            if (this.time <= 0) {
                this.time = 0;
                this.emit('gameOver'); // Час вичерпано
            }
        }

        if (this.shouldAddEnemyTank()) {
            this.addEnemyTank();
        }

        this.objects.forEach(object => object.update(state));
    }

    isOutOfBounds(object) {
        return (
            object.top < this.top ||
            object.right > this.right ||
            object.bottom > this.bottom ||
            object.left < this.left
        );
    }

    hasCollision(object) {
        return Boolean(this.getCollision(object));
    }

    getCollision(object) {
        const collisionObjects = this.getCollisionObjects(object);
        if (collisionObjects.size > 0) {
            return { objects: collisionObjects };
        }
    }

    getCollisionObjects(object) {
        const objects = new Set();

        for (const other of this.objects) {
            if (other !== object && this.haveCollision(object, other)) {
                objects.add(other);
            }
        }

        return objects;
    }

    haveCollision(a, b) {
        return (
            a.left < b.right &&
            a.right > b.left &&
            a.top < b.bottom &&
            a.bottom > b.top
        );
    }

    shouldAddEnemyTank() {
        return (
            this.enemyTankCount < 3 &&
            this.spawnedEnemiesCount < this.totalEnemyLimit
        );
    }

    removeWall() {}

    addEnemyTank() {
        const tank = this.enemyTanks.shift();

        if (tank) {
            tank.setPosition(this.enemyTankPositionIndex);

            if (!this.hasCollision(tank)) {
                this.enemyTankCount += 1;
                this.spawnedEnemiesCount += 1;
                this.enemyTankPositionIndex = (this.enemyTankPositionIndex + 1) % 3;

                this.objects.add(tank);
            } else {
                console.log("Танк не додано: позиція зайнята");
                this.enemyTanks.unshift(tank);
            }
        }
    }

    removeEnemyTank(enemyTank) {
        this.objects.delete(enemyTank);
        this.enemyTankCount -= 1;
    }
}
