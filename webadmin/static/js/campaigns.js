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

    // Delay type handling
    const delayType = document.getElementById('delayType');
    const delaySettings = document.getElementById('delaySettings');
    const minDelayInput = document.getElementById('minDelay');
    const maxDelayInput = document.getElementById('maxDelay');
    const minDelayUnit = document.getElementById('minDelayUnit');
    const maxDelayUnit = document.getElementById('maxDelayUnit');
    const delayHint = document.getElementById('delayHint');

    // Format seconds to human readable
    function formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds} second${seconds !== 1 ? 's' : ''}`;
        } else if (seconds < 3600) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            if (secs === 0) {
                return `${mins} minute${mins !== 1 ? 's' : ''}`;
            }
            return `${mins}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            if (mins === 0) {
                return `${hours} hour${hours !== 1 ? 's' : ''}`;
            }
            return `${hours}h ${mins}m`;
        }
    }

    // Get delay value in seconds
    function getDelayInSeconds(input, unitSelect) {
        const value = parseInt(input.value) || 0;
        const multiplier = parseInt(unitSelect.value) || 1;
        return value * multiplier;
    }

    function updateDelayUI() {
        const type = delayType.value;
        const minSeconds = getDelayInSeconds(minDelayInput, minDelayUnit);
        const maxSeconds = getDelayInSeconds(maxDelayInput, maxDelayUnit);

        if (type === 'none') {
            delaySettings.style.display = 'none';
            delayHint.textContent = 'All emails will be sent immediately (no delay).';
        } else if (type === 'fixed') {
            delaySettings.style.display = 'flex';
            maxDelayInput.closest('.form-group-half').style.display = 'none';
            delayHint.textContent = `Each email will be sent with a fixed ${formatDuration(minSeconds)} delay.`;
        } else {
            delaySettings.style.display = 'flex';
            maxDelayInput.closest('.form-group-half').style.display = 'block';
            delayHint.textContent = `Emails will be sent with a random delay between ${formatDuration(minSeconds)} and ${formatDuration(maxSeconds)}.`;
        }
    }

    if (delayType) {
        delayType.addEventListener('change', updateDelayUI);
        minDelayInput.addEventListener('input', updateDelayUI);
        maxDelayInput.addEventListener('input', updateDelayUI);
        minDelayUnit.addEventListener('change', updateDelayUI);
        maxDelayUnit.addEventListener('change', updateDelayUI);
        updateDelayUI(); // Initialize
    }

    // Schedule later handling
    const scheduleLater = document.getElementById('scheduleLater');
    const scheduleDateTimeGroup = document.getElementById('scheduleDateTimeGroup');
    const scheduledLaunchInput = document.getElementById('scheduledLaunch');

    function updateScheduleUI() {
        if (scheduleLater.checked) {
            scheduleDateTimeGroup.style.display = 'block';
            // Set minimum datetime to now (prevents selecting past dates)
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            scheduledLaunchInput.min = now.toISOString().slice(0, 16);
        } else {
            scheduleDateTimeGroup.style.display = 'none';
            scheduledLaunchInput.value = ''; // Clear when unchecked
        }
    }

    if (scheduleLater) {
        scheduleLater.addEventListener('change', updateScheduleUI);
        updateScheduleUI(); // Initialize
    }

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

        // Validate scheduled launch date
        if (scheduleLater && scheduleLater.checked) {
            const scheduledDate = new Date(scheduledLaunchInput.value);
            const now = new Date();

            if (!scheduledLaunchInput.value) {
                showNotification('Please select a launch date and time', 'error');
                scheduledLaunchInput.focus();
                return;
            }

            if (scheduledDate <= now) {
                showNotification('Scheduled launch time must be in the future', 'error');
                scheduledLaunchInput.focus();
                return;
            }
        }

        // Validate delay values
        if (delayType && delayType.value !== 'none') {
            const minSeconds = getDelayInSeconds(minDelayInput, minDelayUnit);
            const maxSeconds = getDelayInSeconds(maxDelayInput, maxDelayUnit);

            if (delayType.value === 'random' && minSeconds > maxSeconds) {
                showNotification('Minimum delay cannot be greater than maximum delay', 'error');
                return;
            }
        }

        const formData = new FormData(form);

        // Convert delays to seconds before sending
        if (minDelayInput && minDelayUnit) {
            const minSeconds = getDelayInSeconds(minDelayInput, minDelayUnit);
            formData.set('min_delay', minSeconds);
        }
        if (maxDelayInput && maxDelayUnit) {
            const maxSeconds = getDelayInSeconds(maxDelayInput, maxDelayUnit);
            formData.set('max_delay', maxSeconds);
        }

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

                    // Reload page to show new campaign
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showNotification(data.message || 'Failed to create campaign', 'error');
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

    // Launch button handlers
    document.querySelectorAll('.btn-launch').forEach(button => {
        button.addEventListener('click', function (e) {
            const campaignId = this.dataset.campaignId;
            const row = this.closest('tr');
            const campaignName = row.querySelector('.campaign-name strong').textContent;

            if (confirm(`Are you sure you want to launch "${campaignName}"? This will start sending emails to all targets.`)) {
                fetch(`/campaigns/${campaignId}/launch`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showNotification(data.message || 'Campaign launched successfully!', 'success');
                            setTimeout(() => window.location.reload(), 1500);
                        } else {
                            showNotification(data.message || 'Failed to launch campaign', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showNotification('Error launching campaign', 'error');
                    });
            }
        });
    });

    // Pause button handlers
    document.querySelectorAll('.btn-pause').forEach(button => {
        button.addEventListener('click', function (e) {
            const campaignId = this.dataset.campaignId;
            const row = this.closest('tr');
            const campaignName = row.querySelector('.campaign-name strong').textContent;

            if (confirm(`Are you sure you want to pause "${campaignName}"?`)) {
                fetch(`/campaigns/${campaignId}/pause`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showNotification('Campaign paused successfully!', 'success');
                            setTimeout(() => window.location.reload(), 1500);
                        } else {
                            showNotification(data.message || 'Failed to pause campaign', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showNotification('Error pausing campaign', 'error');
                    });
            }
        });
    });

    // Delete button handlers
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function (e) {
            const campaignId = this.dataset.campaignId;
            const row = this.closest('tr');
            const campaignName = row.querySelector('.campaign-name strong').textContent;

            if (confirm(`Are you sure you want to delete "${campaignName}"? This cannot be undone.`)) {
                fetch(`/campaigns/${campaignId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showNotification('Campaign deleted successfully!', 'success');
                            setTimeout(() => window.location.reload(), 1500);
                        } else {
                            showNotification(data.message || 'Failed to delete campaign', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showNotification('Error deleting campaign', 'error');
                    });
            }
        });
    });

    // View details modal elements
    const detailsModal = document.getElementById('campaignDetailsModal');
    const closeDetailsModal = document.getElementById('closeDetailsModal');
    const closeDetailsBtn = document.getElementById('closeDetailsBtn');
    const detailsModalBody = document.getElementById('detailsModalBody');
    const detailsModalTitle = document.getElementById('detailsModalTitle');

    function closeDetailsModalFn() {
        detailsModal.classList.remove('show');
    }

    if (closeDetailsModal) {
        closeDetailsModal.addEventListener('click', closeDetailsModalFn);
    }
    if (closeDetailsBtn) {
        closeDetailsBtn.addEventListener('click', closeDetailsModalFn);
    }

    // Close on outside click
    if (detailsModal) {
        detailsModal.addEventListener('click', function (e) {
            if (e.target === detailsModal) {
                closeDetailsModalFn();
            }
        });
    }

    // View details button handlers
    document.querySelectorAll('.btn-view-details').forEach(button => {
        button.addEventListener('click', function (e) {
            const campaignId = this.dataset.campaignId;

            // Show modal with loading state
            detailsModal.classList.add('show');
            detailsModalBody.innerHTML = '<div class="loading-spinner">Loading campaign details...</div>';

            // Fetch campaign details
            fetch(`/campaigns/${campaignId}/details`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderCampaignDetails(data);
                    } else {
                        detailsModalBody.innerHTML = `<div class="error-message">Error: ${data.message}</div>`;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    detailsModalBody.innerHTML = '<div class="error-message">Failed to load campaign details</div>';
                });
        });
    });

    function renderCampaignDetails(data) {
        const campaign = data.campaign;
        const template = data.template;
        const targets = data.targets;

        // Helper function to format delay
        function formatDelay(seconds) {
            if (!seconds || seconds === 0) return 'No delay';
            if (seconds < 60) return `${seconds} seconds`;
            if (seconds < 3600) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return secs > 0 ? `${mins}m ${secs}s` : `${mins} minutes`;
            }
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return mins > 0 ? `${hours}h ${mins}m` : `${hours} hours`;
        }

        // Determine delay type description
        let delayDescription = 'No delay';
        const minDelay = campaign.min_email_delay;
        const maxDelay = campaign.max_email_delay;
        if (minDelay === 0 && maxDelay === 0) {
            delayDescription = 'No delay (all at once)';
        } else if (minDelay === maxDelay) {
            delayDescription = `Fixed: ${formatDelay(minDelay)}`;
        } else {
            delayDescription = `Random: ${formatDelay(minDelay)} - ${formatDelay(maxDelay)}`;
        }

        // Format scheduled launch
        let scheduledLaunchDisplay = 'Not scheduled';
        if (campaign.scheduled_launch) {
            const scheduled = new Date(campaign.scheduled_launch);
            scheduledLaunchDisplay = scheduled.toLocaleString();
        }

        let html = `
            <div class="details-section">
                <h3>Campaign Information</h3>
                <div class="details-grid">
                    <div class="detail-item">
                        <span class="detail-label">Name:</span>
                        <span class="detail-value">${campaign.name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Status:</span>
                        <span class="status-badge status-${campaign.status}">${campaign.status}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Description:</span>
                        <span class="detail-value">${campaign.description || 'No description'}</span>
                    </div>
                </div>
            </div>

            <div class="details-section">
                <h3>Sending Settings</h3>
                <div class="details-grid">
                    <div class="detail-item">
                        <span class="detail-label">Email Delay:</span>
                        <span class="detail-value">${delayDescription}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Scheduled Launch:</span>
                        <span class="detail-value">${scheduledLaunchDisplay}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Progress:</span>
                        <span class="detail-value">${data.emails_sent} / ${data.total_targets} emails sent</span>
                    </div>
                </div>
            </div>
        `;

        // Template section
        if (template) {
            html += `
                <div class="details-section">
                    <h3>Email Template</h3>
                    <div class="details-grid">
                        <div class="detail-item">
                            <span class="detail-label">Template:</span>
                            <span class="detail-value">${template.name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Subject:</span>
                            <span class="detail-value">${template.subject}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">From:</span>
                            <span class="detail-value">${template.from_name || 'N/A'} &lt;${template.from_email || 'N/A'}&gt;</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="details-section">
                    <h3>Email Template</h3>
                    <p class="no-data">No template assigned</p>
                </div>
            `;
        }

        // Targets section
        html += `
            <div class="details-section">
                <h3>Targets (${data.total_targets} total, ${data.emails_sent} sent)</h3>
                <div class="targets-table-container">
                    <table class="targets-detail-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Position</th>
                                <th>Email Status</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        if (targets.length === 0) {
            html += `<tr><td colspan="5" class="no-data">No targets assigned to this campaign</td></tr>`;
        } else {
            targets.forEach(target => {
                const isSent = target.email_status === 'sent';
                const statusIcon = isSent ? '✓' : (target.email_status === 'failed' ? '✗' : '○');
                const statusClass = isSent ? 'status-sent' : (target.email_status === 'failed' ? 'status-failed' : 'status-pending');

                html += `
                    <tr>
                        <td class="status-cell ${statusClass}">
                            <span class="status-icon">${statusIcon}</span>
                        </td>
                        <td>${target.first_name || ''} ${target.last_name || ''}</td>
                        <td>${target.email}</td>
                        <td>${target.position || '-'}</td>
                        <td><span class="email-status-badge ${statusClass}">${target.email_status}</span></td>
                    </tr>
                `;
            });
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        detailsModalTitle.textContent = `Campaign: ${campaign.name}`;
        detailsModalBody.innerHTML = html;
    }
});
