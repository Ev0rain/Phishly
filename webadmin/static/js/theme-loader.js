/**
 * Global Theme Loader
 * This script must be loaded in the <head> of every page
 * to prevent flash of wrong theme on page load
 */

(function() {
    // Get saved theme immediately (before page renders)
    const savedTheme = localStorage.getItem('phishly-theme') || 'light';
    
    // Apply theme attribute to html element
    document.documentElement.setAttribute('data-theme', savedTheme);
})();
