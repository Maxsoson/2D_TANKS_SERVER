document.addEventListener("DOMContentLoaded", function () {
    generateCaptcha();
    setupInputValidation();

    const form = document.getElementById("registerForm");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const userAnswer = document.getElementById('captcha-input').value;
        const correctAnswer = document.getElementById('captcha-answer').value;

        if (userAnswer != correctAnswer) {
            alert("❌ Incorrect CAPTCHA. Please try again.");
            generateCaptcha();
            return;
        }

        const email = document.getElementById("email").value;
        const name = document.getElementById("name").value;
        const password = document.getElementById("password").value;

        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ email, name, password })
        });

        const result = await response.json();
        document.getElementById("message").textContent = result.message;

        if (result.message === "Користувач успішно зареєстрований" || result.message === "Registered") {
            // Зберігаємо user_id у localStorage
            localStorage.setItem("user_id", result.user_id);

            // ✅ Очищаємо форму
            form.reset();

            // ✅ Генеруємо нову CAPTCHA
            generateCaptcha();

            // ✅ Перевіряємо поля для правильного стану кнопки
            checkInputs();

            // ✅ Показуємо модальне вікно успіху
            showModal();
        }
    });
});

/* === CAPTCHA === */
function generateCaptcha() {
    const num1 = Math.floor(Math.random() * 10);
    const num2 = Math.floor(Math.random() * 10);
    document.getElementById('captcha-question').innerText = `What is ${num1} + ${num2}?`;
    document.getElementById('captcha-answer').value = num1 + num2;
}

/* === MODAL === */
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

function closeModal() {
    const modal = document.getElementById("success-modal");
    const overlay = document.getElementById("modal-overlay");

    overlay.style.opacity = "0";
    modal.style.opacity = "0";

    setTimeout(() => {
        overlay.style.display = "none";
        modal.style.display = "none";
        document.querySelector("form").reset();
        generateCaptcha();
        checkInputs();
    }, 300);
}

/* === VALIDATION === */
function setupInputValidation() {
    const emailInput = document.querySelector("input[type='email']");
    const inputs = document.querySelectorAll("#registerForm input");
    const submitButton = document.querySelector(".index-btn");

    function isValidEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    }

    window.checkInputs = function checkInputs() {
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

    checkInputs(); // Перевірка одразу при завантаженні
}
