const passwordInput = document.getElementById('password');
const meter = document.getElementById('meter');
const eye = document.getElementById('eye');
const eye_cont = document.getElementById('eye_cont');
const strengthText = document.getElementById('strength-text');

passwordInput.addEventListener('input', function() {
  const val = passwordInput.value;
  let score = 0;

  if (val.length >= 12) score++;
  if (/[A-Z]/.test(val)) score++;
  if (/[0-9]/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  meter.value = score;

  const states = ["Very Weak Password", "Weak Password", "Medium Password", "Strong Password", "Very Strong Password"];
  strengthText.textContent = states[score];
});

let viewMode = true
eye_cont.addEventListener("click", () => {
    if (viewMode) {
      passwordInput.type = "text";
      eye.classList.replace("fa-eye", "fa-eye-slash");
    } else {
      passwordInput.type = "password";
      eye.classList.replace("fa-eye-slash", "fa-eye");
    }
    viewMode = !viewMode;
  });