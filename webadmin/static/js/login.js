/**
 * Phishly Admin Login - JavaScript
 * Handles form validation and animations (frontend only for now)
 */

document.addEventListener('DOMContentLoaded', function () {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('phishly-theme', newTheme);
        });
    }

    const loginForm = document.querySelector('.login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.querySelector('.login-button');

    // Prevent multiple form submissions
    let isSubmitting = false;

    // Form submission handler (combined validation + submit prevention)
    loginForm.addEventListener('submit', function (e) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Basic validation
        if (!username || !password) {
            e.preventDefault();
            showMessage('Please fill in all fields', 'error');
            return;
        }

        // Prevent multiple submissions
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }

        // Show loading state
        loginButton.textContent = 'Signing In...';
        loginButton.disabled = true;
        isSubmitting = true;

        // Form will submit to backend naturally
    });

    // Input validation feedback
    usernameInput.addEventListener('input', function () {
        validateInput(this);
    });

    passwordInput.addEventListener('input', function () {
        validateInput(this);
    });

    // Real-time input validation
    function validateInput(input) {
        if (input.value.trim() === '') {
            input.style.borderColor = 'var(--danger-color)';
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    }

    // Show message (error/success)
    function showMessage(text, type) {
        // Check if message element exists, if not create it
        let messageEl = document.querySelector('.message');

        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.className = 'message';
            loginForm.insertBefore(messageEl, loginForm.firstChild);
        }

        messageEl.textContent = text;
        messageEl.className = `message ${type} show`;

        // Hide after 5 seconds
        setTimeout(() => {
            messageEl.classList.remove('show');
        }, 5000);
    }

    // Add keyboard navigation enhancements
    usernameInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });

    // Password visibility toggle (optional feature)
    // Uncomment if you want to add a "show/hide password" button
    /*
    const togglePassword = document.createElement('button');
    togglePassword.type = 'button';
    togglePassword.textContent = '👁️';
    togglePassword.className = 'toggle-password';
    passwordInput.parentElement.appendChild(togglePassword);

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        this.textContent = type === 'password' ? '👁️' : '🙈';
    });
    */
});
