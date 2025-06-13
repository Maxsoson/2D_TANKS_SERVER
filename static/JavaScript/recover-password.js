document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("index-modal");
  const forgotLink = document.querySelector(".index-remember-forgot a") || document.getElementById("forgot-password-link");
  const closeBtn = document.querySelector(".index-modal .index-close");

  const stepLogin = document.getElementById("step-login");
  const stepVerify = document.getElementById("step-verify");

  const loginInput = document.getElementById("recovery-login");
  const emailInput = document.getElementById("recovery-email");
  const verifyKeyInput = document.getElementById("verify-key");

  const sendButton = document.getElementById("sendBtn");
  const verifyButton = document.getElementById("verify-button");

  const sendMessage = document.getElementById("sendMessage");
  const title = document.getElementById("modal-title");

  // Перевірка email
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Валідація логіна та email
  function updateSendButtonState() {
    sendButton.disabled = !(loginInput.value.trim() && validateEmail(emailInput.value.trim()));
  }

  loginInput.addEventListener("input", updateSendButtonState);
  emailInput.addEventListener("input", updateSendButtonState);

  // Відкрити модальне вікно
  if (forgotLink) {
    forgotLink.addEventListener("click", (e) => {
      e.preventDefault();
      modal.style.display = "flex";
      resetModal();
    });
  }

  // Закрити модальне вікно
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  // Етап 1: Надіслати логін + email
  sendButton.addEventListener("click", async () => {
    const login = loginInput.value.trim();
    const email = emailInput.value.trim();

    sendMessage.style.display = "none";

    if (!login || !email) {
      sendMessage.textContent = "Будь ласка, заповніть обидва поля.";
      sendMessage.style.color = "red";
      sendMessage.style.display = "block";
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

      sendMessage.textContent = result.message;
      sendMessage.style.color = response.ok ? "#00ff99" : "red";
      sendMessage.style.display = "block";

      if (response.ok) {
        // Переходити на етап 2
        stepLogin.style.display = "none";
        stepVerify.style.display = "block";
        title.textContent = "Enter Verification Key";
      }
    } catch (error) {
      sendMessage.textContent = "🚫 Server error. Try again.";
      sendMessage.style.color = "red";
      sendMessage.style.display = "block";
    }
  });

  // Етап 2: Перевірити ключ
  verifyButton.addEventListener("click", async () => {
    const key = verifyKeyInput.value.trim();
    const login = loginInput.value.trim();

    if (!key) {
      sendMessage.textContent = "❌ Please enter the verification key.";
      sendMessage.style.color = "red";
      sendMessage.style.display = "block";
      return;
    }

    const formData = new FormData();
    formData.append("name", login);
    formData.append("code", key);

    try {
      const response = await fetch("/verify-code", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      sendMessage.textContent = result.message;
      sendMessage.style.color = response.ok ? "#00ff99" : "red";
      sendMessage.style.display = "block";

      if (response.ok) {
        setTimeout(() => {
          window.location.href = "reset_password.html";
        }, 3000);
      }
    } catch (error) {
      sendMessage.textContent = "🚫 Server error. Try again.";
      sendMessage.style.color = "red";
      sendMessage.style.display = "block";
    }
  });

  // Початковий стан модального вікна
  function resetModal() {
    stepLogin.style.display = "block";
    stepVerify.style.display = "none";
    loginInput.value = "";
    emailInput.value = "";
    verifyKeyInput.value = "";
    sendButton.disabled = true;
    sendMessage.textContent = "";
    sendMessage.style.display = "none";
    title.textContent = "Password Recovery";
  }
});
