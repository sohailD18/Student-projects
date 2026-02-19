/**
 * Fleet Management System - Main JavaScript
 *
 * Handles:
 * - CSRF token management
 * - AJAX requests
 * - UI interactions
 * - Chart initialization helpers
 * - Alert management
 */

// ============================================
// CSRF Token Management
// ============================================

/**
 * Get CSRF token from cookies
 * Required for Django POST requests
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set CSRF token for all AJAX requests
const csrftoken = getCookie('csrftoken');

// ============================================
// Utility Functions
// ============================================

/**
 * Format number with specified decimal places
 */
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format percentage
 */
function formatPercentage(value, decimals = 0) {
    return (value * 100).toFixed(decimals) + '%';
}

/**
 * Show alert message
 * @param {string} type - alert type (success, danger, warning, info)
 * @param {string} message - alert message
 */
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Insert at the top of the container
    const container = document.querySelector('main > .container-fluid, main');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.id = 'loading-spinner';
    overlay.innerHTML = `
        <div class="spinner-border text-light" style="width: 3rem; height: 3rem;" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loading-spinner');
    if (overlay) {
        overlay.remove();
    }
}

// ============================================
// AJAX Request Helpers
// ============================================

/**
 * Make AJAX request with error handling
 * @param {string} url - Request URL
 * @param {object} options - Fetch options
 * @returns {Promise} - Fetch promise
 */
async function makeRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, finalOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Request failed:', error);
        showAlert('danger', 'Request failed. Please try again.');
        throw error;
    }
}

/**
 * POST request helper
 */
async function postRequest(url, data = {}) {
    return makeRequest(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * GET request helper
 */
async function getRequest(url) {
    return makeRequest(url, {
        method: 'GET'
    });
}

// ============================================
// Alert Management
// ============================================

/**
 * Refresh alerts using AI prediction
 */
async function refreshAlerts() {
    showLoading();
    try {
        const response = await postRequest('/api/alerts/refresh/');
        if (response.success) {
            showAlert('success', response.message);
            // Reload page after short delay to show updated alerts
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showAlert('danger', response.message || 'Failed to refresh alerts');
        }
    } catch (error) {
        showAlert('danger', 'Error refreshing alerts');
    } finally {
        hideLoading();
    }
}

/**
 * Dismiss an alert
 * @param {number} alertId - Alert ID to dismiss
 */
async function dismissAlert(alertId) {
    if (!confirm('Are you sure you want to dismiss this alert?')) {
        return;
    }

    showLoading();
    try {
        const response = await postRequest(`/api/alerts/${alertId}/dismiss/`);
        if (response.success) {
            showAlert('success', response.message);
            // Remove the alert from the DOM
            const alertRow = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertRow) {
                alertRow.remove();
            }
            // Reload page after short delay
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('danger', response.message || 'Failed to dismiss alert');
        }
    } catch (error) {
        showAlert('danger', 'Error dismissing alert');
    } finally {
        hideLoading();
    }
}

// ============================================
// Vehicle Stats
// ============================================

/**
 * Get real-time vehicle statistics
 * @param {number} vehicleId - Vehicle ID
 */
async function getVehicleStats(vehicleId) {
    try {
        const stats = await getRequest(`/api/vehicles/${vehicleId}/stats/`);
        return stats;
    } catch (error) {
        console.error('Error fetching vehicle stats:', error);
        return null;
    }
}

/**
 * Update vehicle statistics on page
 * @param {number} vehicleId - Vehicle ID
 */
async function updateVehicleStats(vehicleId) {
    const stats = await getVehicleStats(vehicleId);
    if (stats) {
        // Update stats on page if elements exist
        const mileageEl = document.getElementById('current-mileage');
        const efficiencyEl = document.getElementById('fuel-efficiency');
        const costEl = document.getElementById('cost-per-mile');

        if (mileageEl) mileageEl.textContent = formatNumber(stats.current_mileage) + ' mi';
        if (efficiencyEl) efficiencyEl.textContent = formatNumber(stats.fuel_efficiency) + ' MPG';
        if (costEl) costEl.textContent = formatCurrency(stats.cost_per_mile);
    }
}

// ============================================
// Chart Helpers
// ============================================

/**
 * Get random color for charts
 * @returns {string} RGBA color string
 */
function getRandomColor() {
    const colors = [
        'rgba(13, 110, 253, 1)',
        'rgba(25, 135, 84, 1)',
        'rgba(255, 193, 7, 1)',
        'rgba(220, 53, 69, 1)',
        'rgba(13, 202, 240, 1)',
        'rgba(102, 16, 242, 1)',
        'rgba(253, 126, 20, 1)',
        'rgba(32, 201, 151, 1)'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Get random color with transparency
 * @param {number} alpha - Alpha value (0-1)
 * @returns {string} RGBA color string
 */
function getRandomColorAlpha(alpha = 0.6) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Create default chart options
 * @param {object} customOptions - Custom options to merge
 * @returns {object} Chart options
 */
function getDefaultChartOptions(customOptions = {}) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    font: {
                        size: 12
                    },
                    padding: 15
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 13
                },
                cornerRadius: 4
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 11
                    }
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    font: {
                        size: 11
                    }
                }
            }
        },
        ...customOptions
    };
}

// ============================================
// Auto-refresh functionality
// ============================================

/**
 * Setup auto-refresh for dashboard
 * @param {number} interval - Refresh interval in milliseconds
 */
function setupAutoRefresh(interval = 30000) {
    setInterval(() => {
        // Refresh alerts silently
        fetch('/api/alerts/refresh/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.new_alerts > 0) {
                showAlert('info', `${data.new_alerts} new alert(s) generated`);
                // Reload page to show new alerts
                setTimeout(() => location.reload(), 2000);
            }
        })
        .catch(error => {
            console.error('Auto-refresh failed:', error);
        });
    }, interval);
}

// ============================================
// Page Load Initialization
// ============================================

/**
 * Initialize page when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
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

    // Setup auto-refresh on dashboard
    if (window.location.pathname === '/dashboard/' || window.location.pathname === '/') {
        setupAutoRefresh(60000); // Refresh every minute
    }

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        card.classList.add('fade-in');
    });

    // Handle dismiss buttons for alerts
    const dismissButtons = document.querySelectorAll('[data-dismiss="alert"]');
    dismissButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        });
    });
});

// ============================================
// Export functions for global use
// ============================================

// Expose functions to global scope
window.FleetManager = {
    getCookie,
    showAlert,
    showLoading,
    hideLoading,
    refreshAlerts,
    dismissAlert,
    getVehicleStats,
    updateVehicleStats,
    getRandomColor,
    getRandomColorAlpha,
    getDefaultChartOptions,
    formatNumber,
    formatCurrency,
    formatPercentage,
    makeRequest,
    postRequest,
    getRequest
};

console.log('Fleet Management System initialized');
