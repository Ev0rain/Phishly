// Phishly Admin Dashboard - JavaScript

document.addEventListener('DOMContentLoaded', function () {
    console.log('Phishly Admin Dashboard loaded');

    // Add click handlers for action buttons
    const actionButtons = document.querySelectorAll('.btn-icon');
    actionButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const action = this.getAttribute('title');
            console.log(`Action: ${action}`);
            // TODO: Implement actual actions when backend is ready
        });
    });

    // Highlight active navigation
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
});
