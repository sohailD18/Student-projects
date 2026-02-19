/**
 * Main JavaScript file for AI-Based Examination Performance Analysis System
 */

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Utility function to format time
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// Utility function to confirm actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

// Utility function to show loading state
function showLoading(buttonElement) {
    if (!buttonElement) return;

    const originalText = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';

    return function hideLoading() {
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;
    };
}

// AJAX helper function
function ajaxRequest(url, method, data, onSuccess, onError) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    const options = {
        method: method || 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (csrfToken) {
        options.headers['X-CSRFToken'] = csrfToken;
    }

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (onSuccess) onSuccess(data);
        })
        .catch(error => {
            console.error('Error:', error);
            if (onError) onError(error);
        });
}

// Print functionality
function printPage() {
    window.print();
}

// Export functionality (can be extended)
function exportData(data, filename, type) {
    const blob = new Blob([data], { type: type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Chart color palette
const chartColors = {
    primary: 'rgba(13, 110, 253, 0.7)',
    success: 'rgba(25, 135, 84, 0.7)',
    danger: 'rgba(220, 53, 69, 0.7)',
    warning: 'rgba(255, 193, 7, 0.7)',
    info: 'rgba(13, 202, 240, 0.7)',
    secondary: 'rgba(108, 117, 125, 0.7)',
    primaryBorder: 'rgba(13, 110, 253, 1)',
    successBorder: 'rgba(25, 135, 84, 1)',
    dangerBorder: 'rgba(220, 53, 69, 1)',
};

// Debounce function to prevent excessive API calls
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

// Format percentage for display
function formatPercentage(value, decimals = 1) {
    return parseFloat(value).toFixed(decimals) + '%';
}

// Generate random color for charts
function getRandomColor() {
    const colors = [
        'rgba(13, 110, 253, 0.7)',
        'rgba(25, 135, 84, 0.7)',
        'rgba(220, 53, 69, 0.7)',
        'rgba(255, 193, 7, 0.7)',
        'rgba(13, 202, 240, 0.7)',
        'rgba(102, 16, 242, 0.7)',
        'rgba(214, 51, 132, 0.7)',
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Validate form before submission
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Copy to clipboard functionality
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(function() {
            buttonElement.innerHTML = originalText;
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Smooth scroll to element
function scrollToElement(elementId, offset = 20) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

// Console welcome message
console.log('%c AI-Based Examination Performance Analysis System ',
    'background: #0d6efd; color: white; font-size: 16px; padding: 10px; border-radius: 5px;');
console.log('Built with Django, Chart.js, and Bootstrap 5');
