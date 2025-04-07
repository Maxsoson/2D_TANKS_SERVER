document.addEventListener("DOMContentLoaded", function () {
    let profileModal = document.getElementById("profileModal");
    let profileButton = document.querySelector(".profile-button");
    let closeButton = document.querySelector(".close");

    // Спочатку ховаємо модальне вікно
    profileModal.style.display = "none";

    // Функція відкриття модального вікна
    function openProfile() {
        profileModal.style.display = "flex";
        localStorage.setItem("profileOpen", "true"); // Запам'ятовуємо стан
    }

    // Функція закриття модального вікна
    function closeProfile() {
        profileModal.style.display = "none";
        localStorage.removeItem("profileOpen"); // Видаляємо стан
    }

    // Відкриває вікно при натисканні на кнопку "Profile"
    profileButton.addEventListener("click", openProfile);

    // Закриває вікно при натисканні на "X"
    closeButton.addEventListener("click", closeProfile);

    // Закриває вікно при натисканні поза ним
    window.addEventListener("click", function (event) {
        if (event.target === profileModal) {
            closeProfile();
        }
    });

    // Перевіряємо, чи потрібно відкривати модальне вікно після перезавантаження
    if (localStorage.getItem("profileOpen") === "true") {
        profileModal.style.display = "none";
    }
});
