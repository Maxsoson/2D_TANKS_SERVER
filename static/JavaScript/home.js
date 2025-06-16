document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("tankCanvas");

    if (!canvas) {
        console.error("⚠️ Canvas #tankCanvas not found!");
        return;
    }

    const context = canvas.getContext("2d");

    class Tank {
        constructor(x, y, context, images, direction = 'up') {
            this.x = x;
            this.y = y;
            this.size = 37.5;
            this.context = context;
            this.images = images;
            this.direction = direction;
            this.speed = 3;
            this.animationFrame = 0;
        }

        draw() {
            const image = this.images[this.animationFrame % this.images.length];
            if (image.complete) {
                this.context.save();
                switch (this.direction) {
                    case 'up':
                        this.context.translate(this.x, this.y);
                        break;
                    case 'down':
                        this.context.translate(this.x + this.size, this.y + this.size);
                        this.context.rotate(Math.PI);
                        break;
                    case 'right':
                        this.context.translate(this.x, this.y + this.size);
                        this.context.rotate(Math.PI / 2);
                        break;
                    case 'left':
                        this.context.translate(this.x + this.size, this.y);
                        this.context.rotate(-Math.PI / 2);
                        break;
                }
                this.context.drawImage(image, 0, 0, this.size, this.size);
                this.context.restore();
            }
            this.animationFrame++;
        }

        move() {
            switch (this.direction) {
                case 'up':
                    this.y -= this.speed;
                    if (this.y < -this.size) this.y = window.innerHeight;
                    break;
                case 'down':
                    this.y += this.speed;
                    if (this.y > window.innerHeight) this.y = -this.size;
                    break;
                case 'right':
                    this.x += this.speed;
                    if (this.x > window.innerWidth) this.x = -this.size;
                    break;
                case 'left':
                    this.x -= this.speed;
                    if (this.x < -this.size) this.x = window.innerWidth;
                    break;
            }
        }
    }

    function getDistance(x1, y1, x2, y2) {
        return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    }

    function animateTanks() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const tankImages = [new Image(), new Image()];
        tankImages[0].src = '/static/Images/skin1.png';
        tankImages[1].src = '/static/Images/skin2.png';

        tankImages.forEach(img => {
            img.onload = () => console.log("🟢 Tank image uploaded:", img.src);
            img.onerror = () => console.error("🔴 Image upload error:", img.src);
        });

        const directions = ['up', 'down', 'right', 'left'];
        const tanks = [];
        const minDistance = 80;

        for (let i = 0; i < 9; i++) {
            let x, y, isTooClose;
            do {
                x = Math.random() * (window.innerWidth - 40);
                y = Math.random() * (window.innerHeight - 40);
                isTooClose = false;
                for (let j = 0; j < tanks.length; j++) {
                    const otherTank = tanks[j];
                    const distance = getDistance(x, y, otherTank.x, otherTank.y);
                    if (distance < minDistance) {
                        isTooClose = true;
                        break;
                    }
                }
            } while (isTooClose);

            const direction = directions[i % directions.length];
            tanks.push(new Tank(x, y, context, tankImages, direction));
        }

        function animate() {
            context.clearRect(0, 0, canvas.width, canvas.height);
            tanks.forEach(tank => {
                tank.move();
                tank.draw();
            });
            requestAnimationFrame(animate);
        }

        animate();
    }

    animateTanks();

    window.addEventListener("resize", () => {
        animateTanks();
    });

// 🔐 Активація кнопки "Login", коли всі поля заповнені (тільки якщо елементи існують)
    const loginInputs = document.querySelectorAll(".index-login-box input");
    const loginButton = document.querySelector(".index-login-box .index-btn");

    if (loginInputs.length > 0 && loginButton) {
        function checkLoginInputs() {
            let allFilled = true;
            loginInputs.forEach(input => {
                if (input.value.trim() === "") {
                    allFilled = false;
                }
            });

            if (allFilled) {
                loginButton.classList.add("active");
                loginButton.disabled = false;
            } else {
                loginButton.classList.remove("active");
                loginButton.disabled = true;
            }
        }

        loginInputs.forEach(input => {
            input.addEventListener("input", checkLoginInputs);
        });

        checkLoginInputs();
    } else {
        console.log("ℹ️ Логін-форма не знайдена — login скрипт пропущено.");
    }

});