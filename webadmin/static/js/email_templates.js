/**
 * Email templates Page JavaScript
 * Handles template preview, import modal, and file upload
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

    // Modal elements
    const importModal = document.getElementById('importTemplateModal');
    const previewModal = document.getElementById('previewModal');
    const importBtn = document.getElementById('importTemplateBtn');
    const closeImportBtn = document.getElementById('closeImportModal');
    const cancelImportBtn = document.getElementById('cancelImportBtn');
    const closePreviewBtn = document.getElementById('closePreviewModal');
    const importForm = document.getElementById('importTemplateForm');

    // File upload elements
    const fileInput = document.getElementById('templateFile');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileSelected = document.getElementById('fileSelected');

    // Preview elements
    const previewFrame = document.getElementById('previewFrame');
    const previewTemplateName = document.getElementById('previewTemplateName');
    const previewSubject = document.getElementById('previewSubject');

    // === Auto-open import modal if hash is #import ===
    if (window.location.hash === '#import') {
        importModal.classList.add('show');
        // Remove hash from URL without triggering page reload
        history.replaceState(null, null, ' ');
    }

    // === Import Modal Handling ===

    if (importBtn && importModal) {
        importBtn.addEventListener('click', function () {
            importModal.classList.add('show');
            loadAvailableTemplateFiles();
        });
    }

    // Load available template files from filesystem
    function loadAvailableTemplateFiles() {
        const templateSelect = document.getElementById('templateFile');

        fetch('/templates/available-files')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    templateSelect.innerHTML = '<option value="">-- Select a template file --</option>';
                    data.templates.forEach(template => {
                        const option = document.createElement('option');
                        option.value = template.filename;
                        option.textContent = `${template.name} (${template.size_kb} KB)`;
                        templateSelect.appendChild(option);
                    });
                } else {
                    templateSelect.innerHTML = '<option value="">-- No templates available --</option>';
                }
            })
            .catch(error => {
                console.error('Error loading template files:', error);
                templateSelect.innerHTML = '<option value="">-- Error loading templates --</option>';
            });
    }

    // Template file selection - load preview
    const templateFileSelect = document.getElementById('templateFile');
    if (templateFileSelect) {
        templateFileSelect.addEventListener('change', function () {
            const filename = this.value;
            const previewDiv = document.getElementById('templatePreview');
            const previewContent = document.getElementById('templatePreviewContent');

            if (filename) {
                // Load template content for preview
                fetch(`/templates/file/${encodeURIComponent(filename)}/content`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            previewDiv.style.display = 'block';
                            // Show rendered HTML in iframe
                            previewContent.innerHTML = `<iframe style="width:100%;height:400px;border:1px solid #ccc;border-radius:4px;"></iframe>`;
                            const iframe = previewContent.querySelector('iframe');
                            iframe.contentDocument.write(data.content);
                            iframe.contentDocument.close();
                        }
                    })
                    .catch(error => {
                        console.error('Error loading template content:', error);
                    });
            } else {
                previewDiv.style.display = 'none';
            }
        });
    }

    function closeImportModal() {
        if (importModal) importModal.classList.remove('show');
        if (importForm) importForm.reset();
    }

    if (closeImportBtn) {
        closeImportBtn.addEventListener('click', closeImportModal);
    }
    if (cancelImportBtn) {
        cancelImportBtn.addEventListener('click', closeImportModal);
    }

    // Close on outside click
    if (importModal) {
        importModal.addEventListener('click', function (e) {
            if (e.target === importModal) {
                closeImportModal();
            }
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            if (importModal.classList.contains('show')) {
                closeImportModal();
            }
            if (previewModal.classList.contains('show')) {
                closePreviewModal();
            }
        }
    });

    // === File Upload Handling ===

    // Only set up file upload handlers if elements exist (for drag-and-drop file upload)
    // Current template uses dropdown selector, so these may not exist
    if (fileInput && fileUploadArea && fileSelected) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                showFileSelected(file.name);
            }
        });

        // Drag and drop support
        fileUploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            fileUploadArea.style.borderColor = 'var(--primary-color)';
            fileUploadArea.style.background = 'var(--bg-secondary)';
        });

        fileUploadArea.addEventListener('dragleave', function (e) {
            e.preventDefault();
            fileUploadArea.style.borderColor = '';
            fileUploadArea.style.background = '';
        });

        fileUploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            fileUploadArea.style.borderColor = '';
            fileUploadArea.style.background = '';

            const file = e.dataTransfer.files[0];
            const validExtensions = ['.html', '.html.j2', '.j2'];
            const isValid = validExtensions.some(ext => file && file.name.endsWith(ext));
            if (isValid) {
                fileInput.files = e.dataTransfer.files;
                showFileSelected(file.name);
            } else {
                showNotification('Only HTML and Jinja2 template files are allowed (.html, .html.j2)', 'error');
            }
        });

        function showFileSelected(filename) {
            document.querySelector('.file-upload-label').style.display = 'none';
            fileSelected.style.display = 'flex';
            fileSelected.querySelector('.file-name').textContent = filename;
        }

        function hideFileSelected() {
            document.querySelector('.file-upload-label').style.display = 'block';
            fileSelected.style.display = 'none';
        }
    }

    // === Form Submission ===

    if (importForm) {
        importForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(importForm);

        // Show loading state
        const submitBtn = importForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Importing...';
        submitBtn.disabled = true;

        fetch('/templates/import', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    closeImportModal();
                    // Reload page after 1.5 seconds to show new template
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to import template. Please try again.', 'error');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    // === Preview Modal Handling ===

    const previewButtons = document.querySelectorAll('.preview-btn');

    previewButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Prevent card click
            const templateId = this.getAttribute('data-template-id');
            loadPreview(templateId);
        });
    });

    function loadPreview(templateId) {
        if (!previewFrame) {
            console.error('Preview frame element not found');
            showNotification('Preview not available', 'error');
            return;
        }

        // Show loading state
        previewModal.classList.add('show');
        previewTemplateName.textContent = 'Loading...';
        previewSubject.textContent = '';
        previewFrame.srcdoc = '<div style="padding: 40px; text-align: center; color: #666;">Loading preview...</div>';

        fetch(`/templates/${templateId}/preview`)
            .then(response => response.json())
            .then(data => {
                console.log('Preview data:', data);
                if (data.success) {
                    previewTemplateName.textContent = data.name;
                    previewSubject.textContent = `Subject: ${data.subject}`;

                    // Check if HTML content exists
                    if (data.html && data.html.trim().length > 0) {
                        console.log('Setting iframe content, length:', data.html.length);
                        previewFrame.srcdoc = data.html;
                    } else {
                        console.error('No HTML content received');
                        previewFrame.srcdoc = '<div style="padding: 40px; text-align: center; color: #666;">No preview available</div>';
                    }
                } else {
                    showNotification('Failed to load preview', 'error');
                    closePreviewModal();
                }
            })
            .catch(error => {
                console.error('Error loading preview:', error);
                showNotification('Failed to load preview', 'error');
                closePreviewModal();
            });
    }

    function closePreviewModal() {
        if (previewModal) previewModal.classList.remove('show');
        if (previewFrame) previewFrame.srcdoc = '';
    }

    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', closePreviewModal);
    }

    if (previewModal) {
        previewModal.addEventListener('click', function (e) {
            if (e.target === previewModal) {
                closePreviewModal();
            }
        });
    }

    // === Delete Template Handling ===

    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Prevent card click
            const templateId = this.getAttribute('data-template-id');
            const card = this.closest('.template-card');
            const templateName = card.querySelector('h3').textContent;

            if (confirm(`Are you sure you want to delete the template "${templateName}"?\n\nThis action cannot be undone.`)) {
                deleteTemplate(templateId, card);
            }
        });
    });

    function deleteTemplate(templateId, cardElement) {
        fetch(`/templates/${templateId}/delete`, {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    // Animate removal
                    cardElement.style.opacity = '0';
                    cardElement.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        cardElement.remove();
                    }, 300);
                } else {
                    showNotification(data.message || 'Failed to delete template', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to delete template. Please try again.', 'error');
            });
    }

    // === Edit Template Handling ===

    const editModal = document.getElementById('editModal');
    const editForm = document.getElementById('editTemplateForm');
    const closeEditBtn = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEdit');

    const editButtons = document.querySelectorAll('.edit-btn');

    editButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation();
            const templateId = this.getAttribute('data-template-id');
            openEditModal(templateId);
        });
    });

    function openEditModal(templateId) {
        // Fetch template details
        fetch(`/templates/${templateId}/details`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Populate form
                    document.getElementById('editTemplateId').value = data.template.id;
                    document.getElementById('editName').value = data.template.name;
                    document.getElementById('editSubject').value = data.template.subject;
                    document.getElementById('editFromEmail').value = data.template.from_email || '';
                    document.getElementById('editFromName').value = data.template.from_name || '';

                    // Show modal
                    editModal.classList.add('show');
                } else {
                    showNotification('Failed to load template details', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to load template', 'error');
            });
    }

    function closeEditModal() {
        editModal.classList.remove('show');
        editForm.reset();
    }

    closeEditBtn.addEventListener('click', closeEditModal);
    cancelEditBtn.addEventListener('click', closeEditModal);

    editModal.addEventListener('click', function (e) {
        if (e.target === editModal) {
            closeEditModal();
        }
    });

    // Handle edit form submission
    editForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(editForm);
        const templateId = formData.get('template_id');

        fetch(`/templates/${templateId}/edit`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    closeEditModal();
                    // Reload page to show updated template
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showNotification(data.message || 'Failed to update template', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to update template', 'error');
            });
    });

    // === Notification System ===

    function showNotification(message, type = 'success') {
        const container = document.getElementById('notificationContainer');

        if (!container) {
            console.error('Notification container not found');
            alert(message);  // Fallback to alert if container missing
            return;
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        const icon = type === 'success' ? '✓' : '✕';

        notification.innerHTML = `
            <span class="notification-icon">${icon}</span>
            <span class="notification-message">${message}</span>
        `;

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
});
