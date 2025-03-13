document.addEventListener("DOMContentLoaded", function () {
  checkLoginStatus();

  document.getElementById("loginForm").addEventListener("submit", async function(event) {
      event.preventDefault(); // Запобігаємо стандартному надсиланню форми

      let name = document.getElementById("login-name").value; // Оновлено
      let password = document.getElementById("login-password").value;

      let response = await fetch("/login", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams({ name: name, password: password }) // Відправляємо name
      });

      let result = await response.json();
      document.getElementById("login-message").textContent = result.message;

      if (response.ok) {
          localStorage.setItem("token", result.token);
          localStorage.setItem("username", result.username);
          setTimeout(() => { window.location.href = "index.html"; }, 500);
      }
  });
});

// Перевірка, чи користувач залогінений
function checkLoginStatus() {
  let token = localStorage.getItem("token");
  let username = localStorage.getItem("username");

  if (token && username) {
      document.getElementById("login-container").style.display = "none";
      document.getElementById("profile-container").style.display = "block";
      document.getElementById("username").textContent = username;
  } else {
      document.getElementById("login-container").style.display = "block";
      document.getElementById("profile-container").style.display = "none";
  }
}

// Функція виходу з акаунта
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  checkLoginStatus();
}
