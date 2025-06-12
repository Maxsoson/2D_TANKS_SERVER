document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("index-login-form");
    const rememberCheckbox = document.getElementById("index-rememberMe");
    const loginMessage = document.getElementById("index-login-message");
    const usernameInput = document.getElementById("index-username");
    const passwordInput = document.getElementById("index-password");
    const loginButton = form.querySelector(".index-btn");

    // === Відновлення збереженого username ===
    const savedUsername = localStorage.getItem("rememberedUsername");
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberCheckbox.checked = true;
    }

    // === Валідація: вмикання/вимикання кнопки ===
    function checkInputs() {
        const usernameFilled = usernameInput.value.trim() !== "";
        const passwordFilled = passwordInput.value.trim() !== "";

        if (usernameFilled && passwordFilled) {
            loginButton.disabled = false;
            loginButton.classList.add("active");
        } else {
            loginButton.disabled = true;
            loginButton.classList.remove("active");
        }
    }

    usernameInput.addEventListener("input", checkInputs);
    passwordInput.addEventListener("input", checkInputs);

    checkInputs();

    // === Обробка форми ===
    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = usernameInput.value;
        const password = passwordInput.value;

        const formData = new FormData();
        formData.append("name", name);
        formData.append("password", password);

        try {
            const response = await fetch("/login", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // ✅ Зберігаємо user_id
                localStorage.setItem("user_id", result.user_id);

                // Зберігаємо ім'я та email
                localStorage.setItem("user", JSON.stringify({
                    name: result.name,
                    email: result.email
                }));

                // Remember me
                if (rememberCheckbox.checked) {
                    localStorage.setItem("rememberedUsername", name);
                } else {
                    localStorage.removeItem("rememberedUsername");
                }

                loginMessage.style.color = "green";
                loginMessage.textContent = "Login successful!";

                setTimeout(() => {
                    window.location.href = "/load_to_game_1.html";
                }, 1000);
            } else {
                loginMessage.style.color = "red";
                loginMessage.textContent = result.message || "Login failed";
            }
        } catch (error) {
            loginMessage.style.color = "red";
            loginMessage.textContent = "Network error.";
        }
    });
});
