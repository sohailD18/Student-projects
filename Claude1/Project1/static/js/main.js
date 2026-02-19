/**
 * JobPortal - Main JavaScript File
 * Handles common functionality across the application
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initNavbar();
    initAlerts();
    initTooltips();
    initModals();
    initFormValidation();
    initFileUpload();
    initSearchSuggestions();
    initLazyLoading();
    initNotifications();
});

/**
 * Navbar functionality
 */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Add shadow on scroll
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-lg');
            } else {
                navbar.classList.remove('shadow-lg');
            }
        });
    }

    // Close mobile menu on link click
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                navbarCollapse.classList.remove('show');
            }
        });
    });
}

/**
 * Alert/Message handling
 */
function initAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // Add close button functionality
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }

        // Auto-dismiss success messages
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Modal handling
 */
function initModals() {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            // Pause any videos or animations
            const videos = this.querySelectorAll('video, iframe');
            videos.forEach(video => {
                video.pause();
            });
        });

        modal.addEventListener('hidden.bs.modal', function() {
            // Reset forms in modals
            const forms = this.querySelectorAll('form');
            forms.forEach(form => {
                form.reset();
                form.classList.remove('was-validated');
            });
        });
    });
}

/**
 * Form validation enhancement
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);

        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value) {
                    this.classList.add('was-validated');
                }
            });
        });
    });
}

/**
 * File upload handling
 */
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const maxSize = 5 * 1024 * 1024; // 5MB

            if (file) {
                // Check file size
                if (file.size > maxSize) {
                    alert('File size exceeds 5MB limit. Please choose a smaller file.');
                    this.value = '';
                    return;
                }

                // Display file info
                const fileInfo = this.parentElement.querySelector('.file-info');
                if (fileInfo) {
                    fileInfo.innerHTML = `
                        <div class="alert alert-info mt-2">
                            <i class="fas fa-file me-2"></i>
                            <strong>${file.name}</strong> (${formatFileSize(file.size)})
                        </div>
                    `;
                }
            }
        });
    });
}

/**
 * Search suggestions
 */
function initSearchSuggestions() {
    const searchInputs = document.querySelectorAll('input[name="search"]');

    searchInputs.forEach(input => {
        let debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                return;
            }

            debounceTimer = setTimeout(() => {
                // Here you could implement AJAX search suggestions
                console.log('Searching for:', query);
            }, 300);
        });
    });
}

/**
 * Lazy loading for images
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Utility Functions
 */

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Get CSRF token
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(cookie => cookie.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || '';
}

// Make AJAX requests with CSRF token
function fetchWithCSRF(url, options = {}) {
    const defaults = {
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    };

    const mergedOptions = { ...defaults, ...options };

    // If body is FormData, remove Content-Type to let browser set it
    if (mergedOptions.body instanceof FormData) {
        delete mergedOptions.headers['Content-Type'];
    }

    return fetch(url, mergedOptions);
}

// Show loading spinner
function showLoading(element) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm ms-2';
    spinner.setAttribute('role', 'status');
    element.appendChild(spinner);
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element) {
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
    element.disabled = false;
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substr(0, maxLength) + '...';
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        document.body.appendChild(container);
    }

    container.appendChild(notification);

    // Auto-dismiss
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success');
    }
}

// Smooth scroll to element
function smoothScrollTo(element, offset = 0) {
    const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

// Validate email format
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone number
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// Export functions for use in other scripts
window.JobPortal = {
    fetchWithCSRF,
    showLoading,
    hideLoading,
    formatDate,
    truncateText,
    showNotification,
    copyToClipboard,
    smoothScrollTo,
    isValidEmail,
    isValidPhone,
    formatFileSize,
    debounce,
    getCSRFToken
};

/**
 * Notifications module
 */
function initNotifications() {
    const notificationBadge = document.querySelector('.notification-badge');
    const notificationDropdown = document.getElementById('notificationDropdown');

    if (!notificationBadge) return;

    // Load notifications on page load
    loadNotifications();

    // Load notifications when dropdown is opened
    if (notificationDropdown) {
        notificationDropdown.addEventListener('click', function() {
            loadNotifications();
        });
    }

    // Auto-refresh notifications every 60 seconds
    setInterval(updateNotificationCount, 60000);
}

async function loadNotifications() {
    try {
        const response = await fetch('/notifications/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            // Parse HTML response
            const text = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');
            const notificationItems = doc.querySelectorAll('.notification-item');

            const container = document.getElementById('notificationItems');
            if (container && notificationItems.length > 0) {
                container.innerHTML = '';
                let count = 0;
                notificationItems.forEach((item, index) => {
                    if (index < 5) { // Show only 5 most recent
                        const clone = item.cloneNode(true);
                        container.appendChild(clone);
                    }
                    if (item.getAttribute('data-read') === 'false') {
                        count++;
                    }
                });

                // Update badge
                updateBadge(count);

                // Add event listeners to new items
                attachNotificationEventListeners();
            }
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

async function updateNotificationCount() {
    try {
        const response = await fetch('/notifications/unread-count/');
        const data = await response.json();
        updateBadge(data.count);
    } catch (error) {
        console.error('Error updating notification count:', error);
    }
}

function updateBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 9 ? '9+' : count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}

function attachNotificationEventListeners() {
    // Mark as read buttons
    document.querySelectorAll('#notificationItems .mark-read-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const notificationId = this.getAttribute('data-id');
            const item = this.closest('.notification-item');

            try {
                const response = await fetch(`/notifications/${notificationId}/read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    }
                });

                const data = await response.json();
                if (data.success) {
                    item.remove();
                    updateNotificationCount();
                }
            } catch (error) {
                console.error('Error marking notification as read:', error);
            }
        });
    });
}
