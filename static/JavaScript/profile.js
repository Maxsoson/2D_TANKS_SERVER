document.addEventListener("DOMContentLoaded", function () {
    const profileModal = document.getElementById("profileModal");
    const profileButton = document.querySelector(".profile-button");
    const closeButton = document.querySelector(".close");

    // Ховаємо модалку на початку
    profileModal.style.display = "none";

    // Відкрити модальне вікно
    profileButton.addEventListener("click", () => {
        profileModal.style.display = "flex";
        localStorage.setItem("profileOpen", "true");
    });

    // Закрити по хрестику
    closeButton.addEventListener("click", () => {
        profileModal.style.display = "none";
        localStorage.removeItem("profileOpen");
    });

    // Закрити при кліку поза вікном
    window.addEventListener("click", function (event) {
        if (event.target === profileModal) {
            profileModal.style.display = "none";
            localStorage.removeItem("profileOpen");
        }
    });

    // Повернути стан після перезавантаження
    if (localStorage.getItem("profileOpen") === "true") {
        profileModal.style.display = "flex";
    }

    // Показ / приховування паролю 👁
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            btn.textContent = isHidden ? '🙈' : '👁';
        });
    });
});

// Перемикання між інформацією і формою зміни пароля
function togglePasswordForm(show) {
    const info = document.getElementById("player-info-block");
    const form = document.getElementById("password-form-block");

    if (show) {
        info.classList.add("hidden");
        form.classList.remove("hidden");
    } else {
        form.classList.add("hidden");
        info.classList.remove("hidden");
    }
}

// Обробник Log Out
function handleLogout() {
    localStorage.removeItem("profileOpen");  // ОЧИСТКА localStorage
    alert("You have been logged out!");
    window.location.href = "/templates/index.html";
}
