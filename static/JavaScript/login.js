document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const rememberCheckbox = document.getElementById("rememberMe");
    const loginMessage = document.getElementById("login-message");

    // Відновлення збереженого імені
    const savedUsername = localStorage.getItem("rememberedUsername");
    if (savedUsername) {
        document.getElementById("username").value = savedUsername;
        rememberCheckbox.checked = true;
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = document.getElementById("username").value;
        const password = document.getElementById("password").value;

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
                // Зберігаємо користувача в localStorage
                localStorage.setItem("user", JSON.stringify({
                    name: result.name,
                    email: result.email
                }));

                // Зберігаємо або видаляємо username (тільки логін)
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
