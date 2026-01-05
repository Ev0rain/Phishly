/**
 * Settings Page JavaScript
 * Handles theme switching and preference persistence
 */

document.addEventListener('DOMContentLoaded', function () {
    // Theme Management
    initTheme();

    // Toggle switches
    initToggleSwitches();
});

/**
 * Initialize theme based on saved preference or system default
 */
function initTheme() {
    // Get saved theme or default to light
    const savedTheme = localStorage.getItem('phishly-theme') || 'light';

    // Apply theme
    applyTheme(savedTheme);

    // Set up theme toggle buttons
    const themeButtons = document.querySelectorAll('.theme-option');
    themeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const theme = this.dataset.theme;
            applyTheme(theme);
            localStorage.setItem('phishly-theme', theme);
        });
    });
}

/**
 * Apply theme to the document
 * @param {string} theme - 'light' or 'dark'
 */
function applyTheme(theme) {
    // Set theme attribute on document
    document.documentElement.setAttribute('data-theme', theme);

    // Update active button
    const themeButtons = document.querySelectorAll('.theme-option');
    themeButtons.forEach(button => {
        if (button.dataset.theme === theme) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Store preference
    localStorage.setItem('phishly-theme', theme);
}

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
