/**
 * Carbon Credit Analysis System - Main JavaScript
 * Handles chart initialization and API interactions
 */

// Global configuration
const CHART_COLORS = {
    primary: 'rgba(54, 162, 235, 1)',
    success: 'rgba(75, 192, 192, 1)',
    danger: 'rgba(255, 99, 132, 1)',
    warning: 'rgba(255, 206, 86, 1)',
    info: 'rgba(153, 102, 255, 1)'
};

const CHART_BG_COLORS = {
    primary: 'rgba(54, 162, 235, 0.2)',
    success: 'rgba(75, 192, 192, 0.2)',
    danger: 'rgba(255, 99, 132, 0.2)',
    warning: 'rgba(255, 206, 86, 0.2)',
    info: 'rgba(153, 102, 255, 0.2)'
};

// Default chart options
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            display: true,
            position: 'bottom',
            labels: {
                padding: 15,
                usePointStyle: true
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
            }
        }
    }
};

/**
 * Create a line chart
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data
 * @param {object} options - Chart options (optional)
 */
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    const mergedOptions = {
        ...defaultChartOptions,
        ...options,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: mergedOptions
    });
}

/**
 * Create a bar chart
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data
 * @param {object} options - Chart options (optional)
 */
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    const mergedOptions = {
        ...defaultChartOptions,
        ...options,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: mergedOptions
    });
}

/**
 * Create a doughnut chart
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data
 * @param {object} options - Chart options (optional)
 */
function createDoughnutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    const mergedOptions = {
        ...defaultChartOptions,
        ...options,
        cutout: '60%'
    };

    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: mergedOptions
    });
}

/**
 * Fetch data from API endpoint
 * @param {string} url - API endpoint URL
 * @param {object} params - Query parameters (optional)
 * @returns {Promise} Fetch promise
 */
async function fetchApiData(url, params = {}) {
    try {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;

        const response = await fetch(fullUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

/**
 * Display loading spinner
 * @param {string} elementId - Element ID to show spinner in
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading data...</p>
            </div>
        `;
    }
}

/**
 * Display error message
 * @param {string} elementId - Element ID to show error in
 * @param {string} message - Error message
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
}

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Get trading suggestion badge HTML
 * @param {string} suggestion - Trading suggestion (BUY/SELL/HOLD)
 * @param {string} urgency - Urgency level (low/medium/high)
 * @returns {string} HTML string for badge
 */
function getTradingBadge(suggestion, urgency = 'low') {
    const badgeClass = {
        'SELL': 'bg-success',
        'BUY': 'bg-danger',
        'HOLD': 'bg-warning'
    }[suggestion] || 'bg-secondary';

    const urgencyIcon = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }[urgency] || '';

    return `<span class="badge ${badgeClass}">${suggestion}</span> ${urgencyIcon}`;
}

/**
 * Animate number counting
 * @param {string} elementId - Element ID
 * @param {number} target - Target number
 * @param {number} duration - Animation duration in ms
 */
function animateNumber(elementId, target, duration = 1000) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = formatNumber(target);
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 16);
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize all UI components
 */
function initUI() {
    initTooltips();
    initPopovers();
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initUI();
    console.log('Carbon Credit Analysis System initialized');
});

// Export functions for global use
window.CarbonTracker = {
    createLineChart,
    createBarChart,
    createDoughnutChart,
    fetchApiData,
    showLoading,
    showError,
    formatNumber,
    formatCurrency,
    getTradingBadge,
    animateNumber,
    initUI,
    CHART_COLORS,
    CHART_BG_COLORS
};
