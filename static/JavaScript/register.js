document.addEventListener("DOMContentLoaded", function () {
    generateCaptcha();
    setupInputValidation();

    // Додаємо обробник форми
    document.getElementById("registerForm").addEventListener("submit", async function(event) {
        event.preventDefault(); // Запобігаємо стандартній відправці форми

        // Перевірка CAPTCHA перед відправкою
        const userAnswer = document.getElementById('captcha-input').value;
        const correctAnswer = document.getElementById('captcha-answer').value;

        if (userAnswer != correctAnswer) {
            alert("❌ Incorrect CAPTCHA. Please try again.");
            generateCaptcha();
            return;
        }

        let email = document.getElementById("email").value;
        let name = document.getElementById("name").value;
        let password = document.getElementById("password").value;

        let response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ email: email, name: name, password: password })
        });

        let result = await response.json();
        document.getElementById("message").textContent = result.message;

        // Якщо реєстрація успішна, показати модальне вікно
        if (result.message === "Користувач успішно зареєстрований") {
            showModal();
        }
    });
});

/* === Генерація CAPTCHA === */
function generateCaptcha() {
    const num1 = Math.floor(Math.random() * 10);
    const num2 = Math.floor(Math.random() * 10);
    document.getElementById('captcha-question').innerText = `What is ${num1} + ${num2}?`;
    document.getElementById('captcha-answer').value = num1 + num2;
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
        generateCaptcha(); // Генеруємо нову CAPTCHA
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
