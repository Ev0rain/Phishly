/**
 * Settings Page JavaScript
 * Handles theme toggle and preference management
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

    // Logout confirmation
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to log out?')) {
                e.preventDefault();
            }
        });
    }

    // Toggle switches
    initToggleSwitches();
});

/**
 * Initialize toggle switches with saved preferences
 */
function initToggleSwitches() {
    const toggles = document.querySelectorAll('.toggle-switch input');

    toggles.forEach((toggle, index) => {
        // Load saved state (if any)
        const savedState = localStorage.getItem(`toggle-${index}`);
        if (savedState !== null) {
            toggle.checked = savedState === 'true';
        }

        // Save state on change
        toggle.addEventListener('change', function () {
            localStorage.setItem(`toggle-${index}`, this.checked);
        });
    });
}

/**
 * Get current theme
 * @returns {string} Current theme ('light' or 'dark')
 */
function getCurrentTheme() {
    return localStorage.getItem('phishly-theme') || 'light';
}
