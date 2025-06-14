document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reset-form");
  const userIdField = document.getElementById("user-id");
  const recoveryCodeField = document.getElementById("recovery-code");
  const newPassField = document.getElementById("new-password");
  const confirmPassField = document.getElementById("confirm-password");
  const errorBox = document.getElementById("error-message");

  // ✅ Підставляємо user_id і recovery_code з LocalStorage
  userIdField.value = localStorage.getItem("user_id");
  recoveryCodeField.value = localStorage.getItem("recovery_code");


  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const user_id = userIdField.value;
    const recovery_code = recoveryCodeField.value;
    const new_password = newPassField.value;
    const confirm_password = confirmPassField.value;

    // ✅ Перевіряємо чи паролі співпадають
    if (new_password !== confirm_password) {
      errorBox.textContent = "❌ Passwords do not match!";
      errorBox.style.display = "block";
      return;
    } else {
      errorBox.style.display = "none";
    }

    // ✅ Надсилаємо запит на бекенд
    try {
      const formData = new FormData();
      formData.append("user_id", user_id);
      formData.append("recovery_code", recovery_code);
      formData.append("new_password", new_password);

      const response = await fetch("/reset-password", {
        method: "POST",
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        alert("✅ Password reset successful! Redirecting to login...");
        // Очищаємо все з LocalStorage
        localStorage.removeItem("user_id");
        localStorage.removeItem("recovery_code");
        localStorage.removeItem("email");
        window.location.href = "index.html";
      } else {
        errorBox.textContent = "❌ " + result.message;
        errorBox.style.display = "block";
      }
    } catch (err) {
      console.error(err);
      errorBox.textContent = "❌ Server error. Please try again.";
      errorBox.style.display = "block";
    }
  });
});