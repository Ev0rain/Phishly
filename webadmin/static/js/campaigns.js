/**
 * Campaigns Page JavaScript
 * Handles campaign creation modal and form submission
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

    const modal = document.getElementById('createCampaignModal');
    const createBtn = document.getElementById('createCampaignBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('createCampaignForm');

    // Auto-open modal if hash is #create (navigating from dashboard)
    if (window.location.hash === '#create') {
        modal.classList.add('show');
        // Remove hash from URL without triggering page reload
        history.replaceState(null, null, ' ');
    }

    // Open modal
    createBtn.addEventListener('click', function () {
        modal.classList.add('show');
    });

    // Close modal functions
    function closeModal() {
        modal.classList.remove('show');
        form.reset();
    }

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Close on outside click
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModal();
        }
    });

    // Handle form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating...';
        submitBtn.disabled = true;

        // Simulate API call (replace with actual fetch when backend is ready)
        fetch('/campaigns/create', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showNotification('Campaign created successfully!', 'success');
                    closeModal();

                    // In a real implementation, reload the campaigns list
                    // For now, just show a message
                    setTimeout(() => {
                        showNotification('Note: Page refresh needed to see new campaign (database not connected)', 'info');
                    }, 1000);
                } else {
                    showNotification('Failed to create campaign', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error creating campaign', 'error');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
    });

    // Notification system
    function showNotification(message, type = 'info') {
        // Check if notification container exists
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Add to container
        container.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
                if (container.children.length === 0) {
                    container.remove();
                }
            }, 300);
        }, 5000);
    }

    // Add notification styles dynamically
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 2rem;
                right: 2rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .notification {
                padding: 1rem 1.5rem;
                border-radius: 6px;
                font-size: 0.9375rem;
                font-weight: 500;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
                max-width: 400px;
            }

            .notification.show {
                opacity: 1;
                transform: translateX(0);
            }

            .notification-success {
                background-color: #10b981;
                color: white;
            }

            .notification-error {
                background-color: #ef4444;
                color: white;
            }

            .notification-info {
                background-color: #2563eb;
                color: white;
            }
        `;
        document.head.appendChild(style);
    }

    // Action button handlers (view, edit, delete)
    document.querySelectorAll('.btn-icon').forEach(button => {
        button.addEventListener('click', function (e) {
            const action = this.title.toLowerCase();
            const row = this.closest('tr');
            const campaignName = row.querySelector('.campaign-name strong').textContent;

            // Placeholder functionality
            if (action.includes('view')) {
                showNotification(`View details for: ${campaignName}`, 'info');
            } else if (action.includes('edit')) {
                showNotification(`Edit functionality coming soon for: ${campaignName}`, 'info');
            } else if (action.includes('delete')) {
                if (confirm(`Are you sure you want to delete "${campaignName}"?`)) {
                    showNotification(`Delete functionality coming soon`, 'info');
                }
            }
        });
    });
});
