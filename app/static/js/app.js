document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.nav-item');
    navLinks.forEach(link => {
        if (window.location.pathname === link.getAttribute('href')) {
            link.style.background = '#1b2d4b';
        }
    });

    const passwordField = document.querySelector('.password-field');
    const passwordInput = document.querySelector('#password');
    const passwordToggle = document.querySelector('.password-toggle');

    if (passwordField && passwordInput && passwordToggle) {
        passwordToggle.addEventListener('click', function () {
            const isHidden = passwordInput.type === 'password';
            passwordInput.type = isHidden ? 'text' : 'password';
            passwordField.classList.toggle('show-password', isHidden);
            passwordToggle.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
            passwordToggle.setAttribute('aria-pressed', String(isHidden));
        });
    }
});
