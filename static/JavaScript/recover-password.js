document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("index-modal");
  const forgotLink = document.querySelector(".index-remember-forgot a"); // не забудь змінити в HTML
  const closeBtn = document.querySelector(".index-modal .index-close");
  const recoverBtn = document.querySelector("#index-modal .index-btn");
  const messageBox = document.getElementById("index-recover-message");

  if (forgotLink && modal && closeBtn && recoverBtn) {
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

    recoverBtn.addEventListener("click", async function () {
      const name = document.getElementById("index-recover-username").value.trim();
      const email = document.getElementById("index-recover-email").value.trim();
      messageBox.textContent = "";

      if (!name || !email) {
        messageBox.textContent = "Будь ласка, заповніть обидва поля.";
        messageBox.style.color = "red";
        return;
      }

      const formData = new FormData();
      formData.append("name", name);
      formData.append("email", email);

      try {
        const response = await fetch("/recover-password", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        messageBox.textContent = result.message;
        messageBox.style.color = response.ok ? "green" : "red";

        if (response.ok) {
          setTimeout(() => {
            modal.style.display = "none";
            clearInputs();
          }, 3000);
        }
      } catch (error) {
        messageBox.textContent = "Помилка запиту. Спробуйте ще раз.";
        messageBox.style.color = "red";
      }
    });

    function clearInputs() {
      document.getElementById("index-recover-username").value = "";
      document.getElementById("index-recover-email").value = "";
      messageBox.textContent = "";
    }
  }
});
