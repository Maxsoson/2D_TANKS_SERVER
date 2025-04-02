document.addEventListener("DOMContentLoaded", function () {
  checkLoginStatus();

  document.getElementById("loginForm")?.addEventListener("submit", async function(event) {
      event.preventDefault(); // Запобігаємо стандартному надсиланню форми

      let name = document.getElementById("login-name")?.value;
      let password = document.getElementById("login-password")?.value;

      if (!name || !password) {
          console.error("Відсутні поля для входу");
          //Login fields are missing
          return;
      }

      let response = await fetch("/login", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams({ name: name, password: password })
      });

      let result = await response.json();
      document.getElementById("login-message").textContent = result.message;

      if (response.ok) {
          console.log("Login success:", result); // Лог для перевірки
          localStorage.setItem("token", result.token);
          localStorage.setItem("username", result.username);
          console.log("Saved username:", localStorage.getItem("username")); // Лог для перевірки
          setTimeout(() => { window.location.href = "home.html"; }, 500);
      }
  });

  // Обробник натискання кнопки виходу
  document.addEventListener("click", function (event) {
      if (event.target.id === "logout-button") {
          logout();
      }
  });
});

// Перевірка, чи користувач залогінений
function checkLoginStatus() {
  let token = localStorage.getItem("token");
  let username = localStorage.getItem("username");
  let authLink = document.getElementById("auth-link");
  let usernameSpan = document.getElementById("username");
  let loginContainer = document.getElementById("login-container");
  let profileContainer = document.getElementById("profile-container");

  console.log("Checking login status. Token:", token, "Username:", username); // Лог

  if (token && username) {
      if (loginContainer) loginContainer.style.display = "none";
      if (profileContainer) profileContainer.style.display = "block";

      if (usernameSpan) {
          usernameSpan.textContent = username;
          console.log("Updated username:", username); // Лог для перевірки
      }

      if (authLink) authLink.innerHTML = '<a href="#" id="logout-button">Logout</a>';
  } else {
      if (loginContainer) loginContainer.style.display = "block";
      if (profileContainer) profileContainer.style.display = "none";
      if (authLink) authLink.innerHTML = '<a href="register.html">Register</a>';
      
      // Якщо немає активного користувача, примусово перенаправляємо на index.html
      if (window.location.pathname !== "/index.html") {
          window.location.href = "index.html";
      }
  }
}

// Функція виходу з акаунта
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  checkLoginStatus();
  alert("Ви вийшли з системи.");
  //You have been logged out.
}
