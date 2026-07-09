const passwordInput = document.getElementById('password');
const meter = document.getElementById('meter');
const strengthText = document.getElementById('strength-text');

passwordInput.addEventListener('input', function() {
  const val = passwordInput.value;
  let score = 0;

  if (val.length >= 12) score++;          // Rule 1: Length
  if (/[A-Z]/.test(val)) score++;         // Rule 2: Uppercase
  if (/[0-9]/.test(val)) score++;         // Rule 3: Number
  if (/[^A-Za-z0-9]/.test(val)) score++;  // Rule 4: Special Char

  meter.value = score;

  // Update textual feedback
  const states = ["Very Weak Password", "Weak Password", "Medium Password", "Strong Password", "Very Strong Password"];
  strengthText.textContent = states[score];
});