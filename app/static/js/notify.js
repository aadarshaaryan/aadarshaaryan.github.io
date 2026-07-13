// --- PASSWORD SHOW/HIDE & STRENGTH INTERACTION ---
const passwordInput = document.getElementById('password');
const meter = document.getElementById('meter');
const eye = document.getElementById('eye');
const eye_cont = document.getElementById('eye_cont');
const strengthText = document.getElementById('strength-text');

if (passwordInput) {
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
}

if (eye_cont) {
    let viewMode = true;
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
}

// --- FLOATING TOAST FLASH NOTIFICATIONS ---
const notifies = document.querySelectorAll(".notify"); //[cite: 7]

notifies.forEach((notify) => {
    // Handle entry phase triggers cleanly[cite: 7]
    notify.classList.remove("notify_go"); //[cite: 7]
    notify.classList.add("notify_come"); //[cite: 7]

    // Set auto-dismiss timing delay loops[cite: 7]
    setTimeout(() => {
        notify.classList.remove("notify_come"); //[cite: 7]
        notify.classList.add("notify_go"); //[cite: 7]
        
        // Clean up DOM structural nodes after transition hides the box completely
        notify.addEventListener('animationend', (e) => {
            if (e.animationName === 'notification_go') {
                notify.remove();
            }
        });
    }, 6000); //[cite: 7]
});