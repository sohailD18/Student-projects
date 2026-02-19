/**
 * Main JavaScript for Meeting Analyzer
 * Handles UI interactions and dynamic behavior
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // === Auto-hide messages after 5 seconds ===
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        if (message.classList.contains('alert-success') ||
            message.classList.contains('alert-info')) {
            setTimeout(function() {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 300);
            }, 5000);
        }
    });

    // === Form validation feedback ===
    const forms = document.querySelectorAll('form[data-validation]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
            }
        });
    });

    // === Smooth scroll for anchor links ===
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // === Character counter for transcript textarea ===
    const transcriptTextarea = document.getElementById('transcript');
    if (transcriptTextarea) {
        // Add character counter display if it doesn't exist
        if (!document.getElementById('transcript-counter')) {
            const counter = document.createElement('div');
            counter.id = 'transcript-counter';
            counter.className = 'form-text text-end';
            counter.style.marginTop = '0.25rem';
            transcriptTextarea.parentNode.appendChild(counter);
        }

        const updateCounter = function() {
            const text = transcriptTextarea.value;
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            const chars = text.length;
            const counter = document.getElementById('transcript-counter');
            counter.textContent = `${words} words | ${chars} characters`;
        };

        transcriptTextarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial count
    }

    // === Auto-resize textarea ===
    const textareas = document.querySelectorAll('textarea[data-autoresize]');
    textareas.forEach(function(textarea) {
        const autoResize = function() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };

        textarea.addEventListener('input', autoResize);
        autoResize(); // Initial resize
    });

    // === Table row highlight on hover ===
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.2s ease';
        });
    });

    // === Loading spinner for actions ===
    const actionButtons = document.querySelectorAll('[data-loading]');
    actionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            const loadingText = this.getAttribute('data-loading') || 'Loading...';

            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' +
                             loadingText;
        });
    });

    // === Confirm dangerous actions ===
    const dangerButtons = document.querySelectorAll('[data-confirm]');
    dangerButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // === Search form enhancement ===
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Add clear button functionality
        searchInput.addEventListener('input', function() {
            const clearBtn = document.querySelector('.search-clear');
            if (clearBtn) {
                clearBtn.style.display = this.value ? 'inline-block' : 'none';
            }
        });
    }

    // === Card hover effects enhancement ===
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // === Copy to clipboard functionality ===
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-copy'));
            if (target) {
                const text = target.textContent || target.value;

                navigator.clipboard.writeText(text).then(function() {
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-outline-secondary');

                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.classList.remove('btn-success');
                        button.classList.add('btn-outline-secondary');
                    }, 2000);
                }).catch(function() {
                    console.error('Failed to copy text');
                });
            }
        });
    });

    // === Dynamic chart refresh on window resize ===
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Charts will auto-resize due to Chart.js responsive setting
            // Add any additional resize logic here if needed
        }, 250);
    });

    // === Initialize tooltips (if Bootstrap tooltips are used) ===
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // === Initialize popovers (if Bootstrap popovers are used) ===
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// === Utility Functions ===

/**
 * Debounce function to limit execution rate
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @return {Function} Debounced function
 */
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

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @return {string} Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format date to readable string
 * @param {Date|string} date - Date to format
 * @return {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return d.toLocaleDateString('en-US', options);
}

/**
 * Show a temporary notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    setTimeout(function() {
        alertDiv.style.opacity = '0';
        setTimeout(function() {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// === Export functions for use in templates ===
window.MeetingAnalyzer = {
    showNotification: showNotification,
    formatNumber: formatNumber,
    formatDate: formatDate,
    debounce: debounce
};
