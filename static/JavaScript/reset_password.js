document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reset-form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userIdField = document.getElementById("user-id");
    const recoveryCodeField = document.getElementById("recovery-code");
    const newPassField = document.getElementById("new-password");
    const confirmPassField = document.getElementById("confirm-password");
    const errorBox = document.getElementById("error-message");

    // ✅ 1) Підставляємо user_id з localStorage
    userIdField.value = localStorage.getItem("user_id");

    // ✅ 2) Якщо у тебе поле вводу коду (наприклад у Verify кроці) збережи його у localStorage або іншим способом передай сюди.
    // Для прикладу:
    const enteredCode = localStorage.getItem("recovery_code");
    recoveryCodeField.value = enteredCode;

    // ✅ 3) Перевіряємо паролі збігаються
    if (newPassField.value !== confirmPassField.value) {
      errorBox.textContent = "Passwords do not match!";
      errorBox.style.display = "block";
      return;
    } else {
      errorBox.style.display = "none";
    }

    // ✅ 4) Відправка запиту
    try {
      const response = await fetch("/reset-password", {
        method: "POST",
        body: new URLSearchParams({
          user_id: userIdField.value,
          recovery_code: recoveryCodeField.value,
          new_password: newPassField.value
        })
      });

      const result = await response.json();
      if (response.ok) {
        alert("Password reset successful! Redirecting...");
        window.location.href = "index.html";
      } else {
        errorBox.textContent = result.message;
        errorBox.style.display = "block";
      }
    } catch (err) {
      console.error(err);
      errorBox.textContent = "Server error.";
      errorBox.style.display = "block";
    }
  });
});