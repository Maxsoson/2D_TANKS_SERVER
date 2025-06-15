document.addEventListener("DOMContentLoaded", () => {

  // 👁 Toggle + зміна іконки
  document.querySelectorAll(".toggle-password").forEach(button => {
    button.addEventListener("click", () => {
      const input = button.closest('.password-field').querySelector('input');

      if (input.type === "password") {
        input.type = "text";
        button.textContent = "🙈"; // 👁 → 🙈
      } else {
        input.type = "password";
        button.textContent = "👁"; // 🙈 → 👁
      }
    });
  });

  // Submit логіка без змін
  const form = document.querySelector(".password-change-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const oldPass = document.getElementById("old-password").value;
    const newPass = document.getElementById("new-password").value;
    const confirmPass = document.getElementById("confirm-password").value;

    const userId = localStorage.getItem("user_id");

    if (!oldPass || !newPass || !confirmPass) {
      alert("Please fill in all fields!");
      return;
    }

    const response = await fetch("/change-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id: userId,
        old_password: oldPass,
        new_password: newPass,
        confirm_password: confirmPass
      })
    });

    const result = await response.json();
    if (response.ok) {
      alert(result.message);
      form.reset();
      // Повертаємо іконки назад у 👁 після сабміту
      document.querySelectorAll(".toggle-password").forEach(button => {
        button.textContent = "👁";
        const input = button.closest('.password-field').querySelector('input');
        input.type = "password";
      });
    } else {
      alert(result.detail);
    }
  });

});