document.addEventListener("DOMContentLoaded", () => {
  const countdownEl = document.getElementById("reset-password-countdown");
  if (!countdownEl) return;

  startCountdown(countdownEl);
});

function startCountdown(element) {
  const token = new URLSearchParams(window.location.search).get("sig");
  const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));

  const BUFFER_MS = 1000;
  const exp = payload.exp * 1000 + BUFFER_MS;

  const interval = setInterval(() => updateCountdown(element, exp, interval), 1000);

  updateCountdown(element, exp, interval);
}

function updateCountdown(element, exp, interval) {
  const remaining = Math.max(0, Math.floor((exp - Date.now()) / 1000));
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;

  element.textContent = `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

  if (remaining <= 0) {
    element.textContent = "00:00";
    clearInterval(interval);
    setTimeout(() => location.reload(), 50);
  }
}
