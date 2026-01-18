/**
 * Targets Page JavaScript
 * Handles modals, form submissions, and group member viewing
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
    const createGroupModal = document.getElementById('createGroupModal');
    const importGroupModal = document.getElementById('importGroupModal');
    const viewMembersModal = document.getElementById('viewMembersModal');
    const editGroupModal = document.getElementById('editGroupModal');

    // Button elements
    const createGroupBtn = document.getElementById('createGroupBtn');
    const importGroupBtn = document.getElementById('importGroupBtn');

    // Close buttons
    const closeCreateModal = document.getElementById('closeCreateModal');
    const closeImportModal = document.getElementById('closeImportModal');
    const closeViewModal = document.getElementById('closeViewModal');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelCreateBtn = document.getElementById('cancelCreateBtn');
    const cancelImportBtn = document.getElementById('cancelImportBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    // File upload
    const csvFileInput = document.getElementById('csvFile');
    const fileUploadArea = csvFileInput?.parentElement;

    // Check URL hash for opening modals on page load
    const hash = window.location.hash;
    if (hash === '#create') {
        openModal(createGroupModal);
    } else if (hash === '#import') {
        openModal(importGroupModal);
    }

    // Event Listeners - Create Group
    createGroupBtn?.addEventListener('click', () => {
        openModal(createGroupModal);
        window.location.hash = 'create';
    });

    closeCreateModal?.addEventListener('click', () => {
        closeModal(createGroupModal);
        window.location.hash = '';
    });

    cancelCreateBtn?.addEventListener('click', () => {
        closeModal(createGroupModal);
        window.location.hash = '';
    });

    // Event Listeners - Import Group
    importGroupBtn?.addEventListener('click', () => {
        openModal(importGroupModal);
        window.location.hash = 'import';
    });

    closeImportModal?.addEventListener('click', () => {
        closeModal(importGroupModal);
        window.location.hash = '';
    });

    cancelImportBtn?.addEventListener('click', () => {
        closeModal(importGroupModal);
        window.location.hash = '';
    });

    // Event Listeners - View Members Modal
    closeViewModal?.addEventListener('click', () => {
        closeModal(viewMembersModal);
    });

    // Event Listeners - Edit Group Modal
    closeEditModal?.addEventListener('click', () => {
        closeModal(editGroupModal);
    });

    cancelEditBtn?.addEventListener('click', () => {
        closeModal(editGroupModal);
    });

    // File upload visual feedback
    csvFileInput?.addEventListener('change', function (e) {
        const fileName = e.target.files[0]?.name;
        if (fileName) {
            const uploadText = fileUploadArea.querySelector('.upload-text');
            uploadText.textContent = `✓ ${fileName}`;
            fileUploadArea.classList.add('has-file');
        }
    });

    // Download CSV template
    const downloadTemplateLink = document.getElementById('downloadTemplate');
    downloadTemplateLink?.addEventListener('click', function (e) {
        e.preventDefault();
        downloadCSVTemplate();
    });

    // Close modals when clicking outside
    window.addEventListener('click', function (e) {
        if (e.target === createGroupModal) {
            closeModal(createGroupModal);
            window.location.hash = '';
        }
        if (e.target === importGroupModal) {
            closeModal(importGroupModal);
            window.location.hash = '';
        }
        if (e.target === viewMembersModal) {
            closeModal(viewMembersModal);
        }
        if (e.target === editGroupModal) {
            closeModal(editGroupModal);
        }
    });

    // View group members buttons
    const viewButtons = document.querySelectorAll('.view-btn');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const groupId = this.getAttribute('data-group-id');
            viewGroupMembers(groupId);
        });
    });

    // Edit group buttons
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const groupId = this.getAttribute('data-group-id');
            openEditModal(groupId);
        });
    });

    // Delete group buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const groupId = this.getAttribute('data-group-id');
            const groupName = this.closest('tr').querySelector('.group-name strong').textContent;
            confirmDeleteGroup(groupId, groupName);
        });
    });

    // Form validation for create group
    const createGroupForm = document.getElementById('createGroupForm');
    createGroupForm?.addEventListener('submit', function (e) {
        const targets = document.getElementById('groupTargets').value.trim();
        const emails = targets.split('\n').filter(e => e.trim());

        if (emails.length === 0) {
            e.preventDefault();
            alert('Please enter at least one email address.');
            return false;
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const invalidEmails = emails.filter(email => !emailRegex.test(email.trim()));

        if (invalidEmails.length > 0) {
            e.preventDefault();
            alert(`Invalid email format found:\n${invalidEmails.slice(0, 3).join('\n')}${invalidEmails.length > 3 ? '\n...' : ''}`);
            return false;
        }
    });
});

/**
 * Open a modal
 */
function openModal(modal) {
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

/**
 * Close a modal
 */
function closeModal(modal) {
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
}

/**
 * View group members via AJAX
 */
function viewGroupMembers(groupId) {
    const modal = document.getElementById('viewMembersModal');
    const title = document.getElementById('viewMembersTitle');
    const content = document.getElementById('membersContent');

    // Get group name from table
    const row = document.querySelector(`tr[data-group-id="${groupId}"]`);
    const groupName = row?.querySelector('.group-name strong')?.textContent || 'Unknown Group';

    title.textContent = `Members of ${groupName}`;
    content.innerHTML = '<div class="loading-spinner">Loading members...</div>';
    openModal(modal);

    // Fetch members via AJAX
    fetch(`/api/targets/${groupId}/members`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.members.length > 0) {
                displayMembers(data.members, content);
            } else {
                content.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No members found in this group.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching members:', error);
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>Error loading members. Please try again.</p>
                </div>
            `;
        });
}

/**
 * Display members list in modal
 */
function displayMembers(members, container) {
    const html = `
        <div class="members-list">
            ${members.map(member => `
                <div class="member-item">
                    <div>
                        <div class="member-email">${member.email}</div>
                        <div class="member-name">${member.first_name} ${member.last_name}</div>
                    </div>
                    <div class="member-position">${member.position || 'N/A'}</div>
                    <div class="member-department">${member.department || 'N/A'}</div>
                </div>
            `).join('')}
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
            <strong>Total Members:</strong> ${members.length}
        </div>
    `;
    container.innerHTML = html;
}

/**
 * Open edit modal and populate with group data
 */
function openEditModal(groupId) {
    const modal = document.getElementById('editGroupModal');
    const form = document.getElementById('editGroupForm');
    const groupIdInput = document.getElementById('editGroupId');
    const nameInput = document.getElementById('editGroupName');
    const descriptionInput = document.getElementById('editGroupDescription');
    const targetsInput = document.getElementById('editGroupTargets');

    // Get group data from table row
    const row = document.querySelector(`tr[data-group-id="${groupId}"]`);
    if (!row) {
        alert('Error: Group not found');
        return;
    }

    const groupName = row.querySelector('.group-name strong')?.textContent || '';
    const groupDescription = row.querySelector('.group-name small')?.textContent || '';

    // Populate basic form fields
    groupIdInput.value = groupId;
    nameInput.value = groupName;
    descriptionInput.value = groupDescription;
    targetsInput.value = 'Loading members...';
    targetsInput.disabled = true;

    // Fetch members from API
    fetch(`/api/targets/${groupId}/members`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.members.length > 0) {
                // Populate textarea with email addresses (one per line)
                const emails = data.members.map(member => member.email).join('\n');
                targetsInput.value = emails;
                targetsInput.disabled = false;
            } else {
                targetsInput.value = '';
                targetsInput.placeholder = 'No members found. Add email addresses (one per line)';
                targetsInput.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error fetching members:', error);
            targetsInput.value = '';
            targetsInput.placeholder = 'Error loading members. Add email addresses (one per line)';
            targetsInput.disabled = false;
        });

    // Handle form submission
    form.onsubmit = function (e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('name', nameInput.value.trim());
        formData.append('description', descriptionInput.value.trim());
        formData.append('targets', targetsInput.value.trim());

        // Submit via AJAX
        fetch(`/targets/${groupId}/edit`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    closeModal(modal);
                    location.reload(); // Reload to show updated data
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error updating group:', error);
                alert('Error updating group. Please try again.');
            });
    };

    openModal(modal);
}

/**
 * Confirm group deletion
 */
function confirmDeleteGroup(groupId, groupName) {
    if (confirm(`Are you sure you want to delete the group "${groupName}"?\n\nThis action cannot be undone.`)) {
        // Create and submit delete form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/targets/${groupId}/delete`;

        // Add CSRF token if available (for Flask-WTF)
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfToken;
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit();
    }
}

/**
 * Download CSV template file
 */
function downloadCSVTemplate() {
    const csvContent = `email,first_name,last_name,position,department
john.doe@company.com,John,Doe,Senior Engineer,Engineering
jane.smith@company.com,Jane,Smith,Marketing Manager,Marketing
mike.johnson@company.com,Mike,Johnson,Sales Representative,Sales
sarah.williams@company.com,Sarah,Williams,CFO,Finance`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'target_group_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Count emails in textarea (helper for UI)
 */
function updateEmailCount() {
    const textarea = document.getElementById('groupTargets');
    const counter = document.getElementById('emailCount');

    if (textarea && counter) {
        const emails = textarea.value.split('\n').filter(e => e.trim()).length;
        counter.textContent = `${emails} email${emails !== 1 ? 's' : ''}`;
    }
}
