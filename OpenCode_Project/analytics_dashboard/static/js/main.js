// Main JavaScript file for Analytics Dashboard

// Utility function to format dates
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Show loading indicator
function showLoading(element) {
    element.innerHTML = '<div class="loading">Loading...</div>';
}

// Show error message
function showError(message) {
    console.error(message);
    // You can enhance this to show a toast notification
}

// Auto-refresh functionality
function setupAutoRefresh(intervalInSeconds) {
    setInterval(() => {
        if (document.getElementById('refreshAll')) {
            document.getElementById('refreshAll').click();
        }
    }, intervalInSeconds * 1000);
}

// Initialize tooltips and other UI elements
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Add confirmation for destructive actions
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Handle form errors
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('error')) {
        showError(urlParams.get('error'));
    }
});

// Export functions for use in other scripts
window.AnalyticsUtils = {
    formatDate,
    formatNumber,
    showLoading,
    showError,
    setupAutoRefresh
};
