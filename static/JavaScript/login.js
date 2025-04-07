document.getElementById("login-form").addEventListener("submit", async function(e) {
    e.preventDefault();

    const name = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const messageDiv = document.getElementById("login-message");

    const formData = new FormData();
    formData.append("name", name);
    formData.append("password", password);

    const response = await fetch("/login", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        const result = await response.json();

        // Зберігаємо name + email у localStorage
        localStorage.setItem("user", JSON.stringify({
            name: result.name,
            email: result.email
        }));

        // Переходимо до гри
        window.location.href = "/load_to_game_1.html";
    } else {
        const result = await response.json();
        messageDiv.textContent = result.message || "Login failed";
    }
});
