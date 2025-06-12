document.addEventListener("DOMContentLoaded", async function () {
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

    // 👁 Показ/приховування паролю
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            btn.textContent = isHidden ? '🙈' : '👁';
        });
    });

    // 🔄 Завантаження даних профілю
    const userId = localStorage.getItem("user_id");
    if (userId) {
        try {
            const res = await fetch(`/profile/${userId}`);
            const data = await res.json();
            console.log("📦 Profile data:", data);

            const elEmail = document.getElementById("profile-email");
            const elName = document.getElementById("profile-name");
            const elScore = document.getElementById("profile-score");
            const elPlace = document.getElementById("profile-place");

            if (elEmail) elEmail.textContent = data.email;
            if (elName) elName.textContent = data.name;
            if (elScore) elScore.textContent = data.score && data.score > 0 ? data.score : "No data yet";
            if (elPlace) elPlace.textContent = data.place && typeof data.place === "number" ? data.place : "No data yet";

        } catch (e) {
            console.error("❌ Failed to load profile data:", e);
        }
    }
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
    localStorage.removeItem("profileOpen");
    localStorage.removeItem("user_id");
    alert("You have been logged out!");
    window.location.href = "index.html";
}
