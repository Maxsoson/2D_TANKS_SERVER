document.addEventListener("DOMContentLoaded", () => {
  const user = JSON.parse(localStorage.getItem("user"));

  if (user) {
      document.getElementById("player-name").textContent = user.name;
      document.getElementById("player-email").textContent = user.email;
  } else {
      window.location.href = "/index.html"; // якщо не авторизований
  }
});
