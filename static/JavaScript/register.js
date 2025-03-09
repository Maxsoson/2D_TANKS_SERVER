document.addEventListener("DOMContentLoaded", function () {
    generateCaptcha();
    setupInputValidation();
});

/* === Генерація CAPTCHA === */
function generateCaptcha() {
    const num1 = Math.floor(Math.random() * 10);
    const num2 = Math.floor(Math.random() * 10);
    document.getElementById('captcha-question').innerText = `What is ${num1} + ${num2}?`;
    document.getElementById('captcha-answer').value = num1 + num2;
}

/* === Валідація CAPTCHA === */
function validateCaptcha(event) {
    event.preventDefault(); // Запобігаємо оновленню сторінки
    const userAnswer = document.getElementById('captcha-input').value;
    const correctAnswer = document.getElementById('captcha-answer').value;

    if (userAnswer == correctAnswer) {
        showModal(); // Викликаємо модальне вікно
    } else {
        alert("❌ Incorrect CAPTCHA. Please try again.");
        generateCaptcha();
    }
}

/* === Показати модальне вікно і накласти затемнення на всю сторінку === */
function showModal() {
    const modal = document.getElementById("success-modal");
    const overlay = document.getElementById("modal-overlay");

    overlay.style.display = "block";
    modal.style.display = "flex";

    setTimeout(() => {
        overlay.style.opacity = "1"; 
        modal.style.opacity = "1"; 
    }, 10);
}

/* === Закрити модальне вікно і прибрати затемнення === */
function closeModal() {
    const modal = document.getElementById("success-modal");
    const overlay = document.getElementById("modal-overlay");

    overlay.style.opacity = "0";
    modal.style.opacity = "0";

    setTimeout(() => {
        overlay.style.display = "none";
        modal.style.display = "none";
        document.querySelector("form").reset();
    }, 300);
}

/* === Блокування кнопки поки не заповнені всі поля === */
function setupInputValidation() {
    const emailInput = document.querySelector("input[type='email']");
    const inputs = document.querySelectorAll(".input-box input");
    const submitButton = document.querySelector(".btn");

    function isValidEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    }

    function checkInputs() {
        let allFilled = true;
        let validEmail = isValidEmail(emailInput.value);

        inputs.forEach(input => {
            if (input.value.trim() === "") {
                allFilled = false;
            }
        });

        if (allFilled && validEmail) {
            submitButton.disabled = false;
            submitButton.classList.add("active");
        } else {
            submitButton.disabled = true;
            submitButton.classList.remove("active");
        }
    }

    inputs.forEach(input => {
        input.addEventListener("input", checkInputs);
    });

    checkInputs(); // Перевіряємо на старті
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("home.js is running and DOM is ready!");
    drawTanks(); // Викликати функцію малювання танків
});
