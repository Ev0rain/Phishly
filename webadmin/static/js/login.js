/**
 * Phishly Admin Login - JavaScript
 * Handles form validation and animations (frontend only for now)
 */

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('.login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.querySelector('.login-button');

    // Form submission handler (placeholder - no backend yet)
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Basic validation
        if (!username || !password) {
            showMessage('Please fill in all fields', 'error');
            return;
        }

        // Show loading state
        loginButton.textContent = 'Signing In...';
        loginButton.disabled = true;

        // Simulate API call (remove when backend is ready)
        setTimeout(() => {
            // For now, just show a message
            // In production, this will make an actual API call
            showMessage('Backend authentication not yet implemented', 'error');
            loginButton.textContent = 'Sign In';
            loginButton.disabled = false;
        }, 1000);
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

    // Handle "Remember me" checkbox
    const rememberCheckbox = document.getElementById('remember');
    const savedUsername = localStorage.getItem('phishly_username');

    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberCheckbox.checked = true;
    }

    rememberCheckbox.addEventListener('change', function () {
        if (this.checked) {
            localStorage.setItem('phishly_username', usernameInput.value);
        } else {
            localStorage.removeItem('phishly_username');
        }
    });

    // Update saved username when input changes
    usernameInput.addEventListener('blur', function () {
        if (rememberCheckbox.checked) {
            localStorage.setItem('phishly_username', this.value);
        }
    });

    // Prevent multiple form submissions
    let isSubmitting = false;
    loginForm.addEventListener('submit', function (e) {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        isSubmitting = true;
        setTimeout(() => {
            isSubmitting = false;
        }, 2000);
    });

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
