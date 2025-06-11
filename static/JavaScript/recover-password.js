document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("index-modal");
  const forgotLink = document.querySelector(".index-remember-forgot a"); // не забудь перевірити, чи існує цей елемент
  const closeBtn = document.querySelector(".index-modal .index-close");
  const sendBtn = document.getElementById("sendBtn");
  const messageBox = document.getElementById("sendMessage");
  const loginInput = document.getElementById("recovery-login");
  const emailInput = document.getElementById("recovery-email");

  // Валідація для кнопки
  function validateInputs() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (loginInput.value.trim() !== "" && emailRegex.test(emailInput.value.trim())) {
      sendBtn.disabled = false;
    } else {
      sendBtn.disabled = true;
    }
  }

  loginInput.addEventListener("input", validateInputs);
  emailInput.addEventListener("input", validateInputs);

  if (forgotLink && modal && closeBtn && sendBtn) {
    forgotLink.addEventListener("click", function (e) {
      e.preventDefault();
      modal.style.display = "block";
    });

    closeBtn.addEventListener("click", function () {
      modal.style.display = "none";
      clearInputs();
    });

    window.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.style.display = "none";
        clearInputs();
      }
    });

    sendBtn.addEventListener("click", async function () {
      const login = loginInput.value.trim();
      const email = emailInput.value.trim();

      // Очистка старого повідомлення
      messageBox.style.display = "none";

      if (!login || !email) {
        messageBox.textContent = "Будь ласка, заповніть обидва поля.";
        messageBox.style.color = "red";
        messageBox.style.display = "block";
        return;
      }

      const formData = new FormData();
      formData.append("name", login);
      formData.append("email", email);

      try {
        const response = await fetch("/recover-password", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();

        messageBox.textContent = result.message;
        messageBox.style.color = response.ok ? "#00ff99" : "red";
        messageBox.style.display = "block";

        if (response.ok) {
          setTimeout(() => {
            modal.style.display = "none";
            clearInputs();
          }, 3000);
        }
      } catch (error) {
        messageBox.textContent = "Помилка запиту. Спробуйте ще раз.";
        messageBox.style.color = "red";
        messageBox.style.display = "block";
      }
    });

    function clearInputs() {
      loginInput.value = "";
      emailInput.value = "";
      sendBtn.disabled = true;
      messageBox.style.display = "none";
    }
  }
});
