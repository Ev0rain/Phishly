/**
 * Landing Pages Management JavaScript
 * Template-based landing pages with folder selector
 */

document.addEventListener('DOMContentLoaded', function () {
    // Modal elements
    const modal = document.getElementById('createModal');
    const form = document.getElementById('createLandingPageForm');
    const templateSelect = document.getElementById('template_path');
    const templateInfo = document.getElementById('templateInfo');
    const templateDetails = document.getElementById('templateDetails');
    const entryPages = document.getElementById('entryPages');

    // Open modal
    document.getElementById('createLandingPageBtn').addEventListener('click', function () {
        modal.classList.add('show');
        loadTemplates();
    });

    // Close modal
    document.querySelector('.close').addEventListener('click', closeModal);
    document.getElementById('cancelCreate').addEventListener('click', closeModal);

    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    function closeModal() {
        modal.classList.remove('show');
        form.reset();
        templateInfo.style.display = 'none';
    }

    // Load available templates
    function loadTemplates() {
        fetch('/landing-pages/templates')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    templateSelect.innerHTML = '<option value="">-- Select a template --</option>';
                    data.templates.forEach(template => {
                        const option = document.createElement('option');
                        option.value = template.name;
                        option.textContent = `${template.name} (${template.size_mb} MB, ${template.file_count} files)`;
                        templateSelect.appendChild(option);
                    });
                } else {
                    templateSelect.innerHTML = '<option value="">-- No templates available --</option>';
                }
            })
            .catch(error => {
                console.error('Error loading templates:', error);
                templateSelect.innerHTML = '<option value="">-- Error loading templates --</option>';
            });
    }

    // Template selection change
    templateSelect.addEventListener('change', function () {
        const templateName = this.value;

        if (templateName) {
            // Show loading
            templateInfo.style.display = 'block';
            templateDetails.innerHTML = '<p>Loading template information...</p>';
            entryPages.innerHTML = '';

            // Load template pages
            fetch(`/landing-pages/templates/${templateName}/pages`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const selectedOption = templateSelect.options[templateSelect.selectedIndex];
                        const optionText = selectedOption.textContent;

                        // Extract size and file count from option text
                        const match = optionText.match(/\(([\d.]+) MB, (\d+) files\)/);
                        const size = match ? match[1] : 'Unknown';
                        const fileCount = match ? match[2] : 'Unknown';

                        templateDetails.innerHTML = `
                            <p><strong>Template:</strong> ${templateName}</p>
                            <p><strong>Size:</strong> ${size} MB</p>
                            <p><strong>Files:</strong> ${fileCount}</p>
                            <p><strong>Entry Pages:</strong> ${data.count}</p>
                        `;

                        // Display entry pages
                        if (data.entry_pages.length > 0) {
                            entryPages.innerHTML = data.entry_pages.map(page =>
                                `<div class="entry-page-item">${page}</div>`
                            ).join('');
                        } else {
                            entryPages.innerHTML = '<p>No HTML files found</p>';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading template pages:', error);
                    templateDetails.innerHTML = '<p class="error">Error loading template information</p>';
                });
        } else {
            templateInfo.style.display = 'none';
        }
    });

    // Form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating...';
        submitBtn.disabled = true;

        fetch('/landing-pages/create', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    window.location.reload();
                } else {
                    alert('Error: ' + data.message);
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to create landing page');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
    });

    // Preview button handlers
    document.querySelectorAll('.btn-preview').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const row = this.closest('tr');
            const name = row.querySelector('strong').textContent;

            // Show loading state
            const originalText = this.textContent;
            this.textContent = 'Deploying...';
            this.disabled = true;

            // Deploy preview
            fetch(`/landing-pages/${id}/preview`, {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Open preview in new window
                        const previewWindow = window.open(data.preview_url, 'landingPagePreview', 'width=1200,height=800');

                        if (previewWindow) {
                            // Show cleanup modal
                            showPreviewModal(name, data.preview_url);
                        } else {
                            alert('Preview deployed! Please allow popups and visit:\n\n' + data.preview_url);
                            showPreviewModal(name, data.preview_url);
                        }
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to deploy preview');
                })
                .finally(() => {
                    this.textContent = originalText;
                    this.disabled = false;
                });
        });
    });

    // Show preview control modal
    function showPreviewModal(name, previewUrl) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>Preview: ${name}</h2>
                </div>
                <div style="padding: 20px;">
                    <p><strong>Preview URL:</strong></p>
                    <p style="background: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
                        <a href="${previewUrl}" target="_blank">${previewUrl}</a>
                    </p>
                    <p style="margin-top: 20px; color: #666;">
                        The preview instance is now running. You can explore the landing page with all its resources.
                        When you're done testing, click "Stop Preview" to clean up the instance.
                    </p>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-danger" id="stopPreviewBtn">Stop Preview</button>
                    <button type="button" class="btn btn-secondary" id="closePreviewModalBtn">Keep Running</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Stop preview button
        modal.querySelector('#stopPreviewBtn').addEventListener('click', function () {
            this.textContent = 'Stopping...';
            this.disabled = true;

            fetch('/landing-pages/preview/cleanup', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Preview instance stopped successfully');
                        document.body.removeChild(modal);
                    } else {
                        alert('Error stopping preview: ' + data.message);
                        this.textContent = 'Stop Preview';
                        this.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to stop preview');
                    this.textContent = 'Stop Preview';
                    this.disabled = false;
                });
        });

        // Close modal button
        modal.querySelector('#closePreviewModalBtn').addEventListener('click', function () {
            document.body.removeChild(modal);
        });

        // Close on outside click
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    // Edit button handlers
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            alert('Edit functionality coming soon for landing page ' + id);
        });
    });

    // Activate button handlers
    document.querySelectorAll('.btn-activate').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const row = this.closest('tr');
            const name = row.querySelector('strong').textContent;

            if (confirm(`Activate "${name}" as the active landing page?\n\nThis will be used for all new campaigns.`)) {
                fetch(`/landing-pages/${id}/activate`, {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            window.location.reload();
                        } else {
                            alert('Error: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to activate landing page');
                    });
            }
        });
    });

    // Delete button handlers
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const row = this.closest('tr');
            const name = row.querySelector('strong').textContent;

            if (confirm(`Are you sure you want to delete "${name}"?\n\nThis action cannot be undone.`)) {
                fetch(`/landing-pages/${id}/delete`, {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            row.remove();
                        } else {
                            alert('Error: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to delete landing page');
                    });
            }
        });
    });
});
