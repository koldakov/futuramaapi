

let timerInterval = null;

function openForgotPasswordModal(event) {
  event.preventDefault();

  const modal = document.getElementById('forgotPasswordModal');
  const messageDiv = document.getElementById('forgotPasswordMessage');
  const submitButton = document.querySelector('#forgotPasswordForm button[type="submit"]');

  modal.classList.add('show');
  document.getElementById('reset-email').focus();


  messageDiv.classList.add('hidden');
  messageDiv.textContent = '';

  const { allowed, timeRemaining } = canRequestPasswordReset();

  if (!allowed) {
    messageDiv.classList.remove('hidden');
    messageDiv.className = 'auth-message error';
    startCountdown(messageDiv, timeRemaining, submitButton);
  } else {
    submitButton.disabled = false;
  }
}

function closeForgotPasswordModal() {
  const modal = document.getElementById('forgotPasswordModal');
  modal.classList.remove('show');

  const messageDiv = document.getElementById('forgotPasswordMessage');
  messageDiv.classList.add('hidden');
  messageDiv.textContent = '';

  document.getElementById('forgotPasswordForm').reset();
  clearInterval(timerInterval);
}

function canRequestPasswordReset() {
  const storedValue = localStorage.getItem('lastChanged');
  const lastChanged = storedValue ? new Date(storedValue).getTime() : null;

  const waitTime = 15 * 60 * 1000; // 15 minutes
  const now = Date.now();

  if (!lastChanged || isNaN(lastChanged)) {
    return { allowed: true, timeRemaining: null };
  }

  const nextAllowed = lastChanged + waitTime;

  if (now < nextAllowed) {
    const timeRemaining = Math.ceil((nextAllowed - now) / 1000);
    return { allowed: false, timeRemaining };
  }

  return { allowed: true, timeRemaining: null };
}

function formatTimeRemaining(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return minutes > 0 ? `${minutes}m ${secs}s` : `${secs}s`;
}

function startCountdown(messageDiv, seconds, submitButton) {
  clearInterval(timerInterval);

  let remaining = seconds;
  submitButton.disabled = true;

  messageDiv.textContent = `Please wait ${formatTimeRemaining(remaining)} before trying again.`;
  timerInterval = setInterval(() => {
    if (remaining <= 0) {
      clearInterval(timerInterval);
      messageDiv.textContent = 'You can now request a reset link.';
      submitButton.disabled = false;
      return;
    }

    messageDiv.textContent = `Please wait ${formatTimeRemaining(remaining)} before trying again.`;
    remaining--;
  }, 1000);
}

async function handleForgotPassword(event) {
  event.preventDefault();

  const messageDiv = document.getElementById('forgotPasswordMessage');
  const submitButton = document.querySelector('#forgotPasswordForm button[type="submit"]');

  const { allowed, timeRemaining } = canRequestPasswordReset();

  if (!allowed) {
    messageDiv.classList.remove('hidden');
    messageDiv.className = 'auth-message error';
    startCountdown(messageDiv, timeRemaining, submitButton);
    return;
  }

  const email = document.getElementById('reset-email').value;

  submitButton.disabled = true;
  submitButton.textContent = 'Sending...';

  console.log(BACKEND_URL)
  try {
    const response = await fetch(`${BACKEND_URL}api/users/passwords/request-change`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    messageDiv.classList.remove('hidden');

    if (response.ok) {
      messageDiv.className = 'auth-message success';
      messageDiv.textContent = '✓ Password reset link sent! Check your email.';

      // Save timestamp
      localStorage.setItem('lastChanged', new Date().toISOString());

      document.getElementById('forgotPasswordForm').reset();

      setTimeout(() => closeForgotPasswordModal(), 2000);
    } else {
      messageDiv.className = 'auth-message error';
      messageDiv.textContent = '✗ Unable to send reset link. Please try again.';
    }
  } catch (error) {
    console.error(error);
    messageDiv.className = 'auth-message error';
    messageDiv.textContent = '✗ An error occurred. Please try again.';
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Send Reset Link';
  }
}

document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') closeForgotPasswordModal();
});

window.onclick = function(event) {
  const modal = document.getElementById('forgotPasswordModal');
  if (event.target === modal) closeForgotPasswordModal();
};

// Handle URL param
const urlParams = new URLSearchParams(window.location.search);
const messageType = urlParams.get('messageType');

if (messageType === 'password_changed') {
  const submitButton = document.querySelector('.auth-button');
  if (submitButton) submitButton.disabled = false;

  localStorage.setItem('lastChanged', new Date().toISOString());

  // Clean URL after 3s
  setTimeout(() => {
    const url = new URL(window.location);
    url.searchParams.delete('messageType');
    window.history.replaceState({}, document.title, url);
  }, 2000);
}