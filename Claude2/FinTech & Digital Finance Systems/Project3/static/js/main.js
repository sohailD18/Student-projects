/**
 * Finance Intelligence Platform - Main JavaScript
 */

// Global configuration
const API_ENDPOINTS = {
    insights: '/api/insights/',
    patterns: '/api/patterns/',
    forecast: '/api/forecast/',
    savings: '/api/savings/',
    summary: '/api/summary/',
};

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeAlerts();
    initializeAutoRefresh();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Initialize auto-refresh for dashboard (every 5 minutes)
 */
function initializeAutoRefresh() {
    if (document.querySelector('.dashboard-container')) {
        setInterval(() => {
            console.log('Auto-refreshing dashboard...');
            // Optional: implement silent refresh
        }, 300000); // 5 minutes
    }
}

/**
 * Fetch API data with error handling
 */
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showErrorNotification('Failed to fetch data. Please try again.');
        return null;
    }
}

/**
 * Show error notification
 */
function showErrorNotification(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const container = document.querySelector('.container-fluid');
    if (container) {
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        container.insertBefore(alertDiv.firstElementChild, container.firstElementChild);
    }
}

/**
 * Show success notification
 */
function showSuccessNotification(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const container = document.querySelector('.container-fluid');
    if (container) {
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        container.insertBefore(alertDiv.firstElementChild, container.firstElementChild);
    }
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
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

/**
 * Format date
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Debounce function for search/filter inputs
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
 * Get color based on value (for charts)
 */
function getColorForValue(value, type = 'default') {
    const colors = {
        default: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
        income: '#28a745',
        expense: '#dc3545',
        success: '#198754',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#0dcaf0'
    };

    return colors[type] || colors.default[Math.floor(Math.random() * colors.default.length)];
}

/**
 * Create a chart with common options
 */
function createChart(ctx, type, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    usePointStyle: true
                }
            }
        }
    };

    return new Chart(ctx, {
        type: type,
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

/**
 * Update insight as read
 */
async function markInsightAsRead(insightId) {
    const result = await fetchAPI(`/insights/${insightId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    });

    if (result && result.status === 'success') {
        const insightElement = document.querySelector(`[data-insight-id="${insightId}"]`);
        if (insightElement) {
            insightElement.style.opacity = '0.5';
        }
    }
}

/**
 * Get CSRF token from cookies
 */
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    return '';
}

/**
 * Export data as CSV
 */
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Convert JSON data to CSV
 */
function convertToCSV(data) {
    if (!data || data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [];

    csvRows.push(headers.join(','));

    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            const escaped = ('' + (value || '')).replace(/"/g, '\\"');
            return `"${escaped}"`;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const originalContents = document.body.innerHTML;
    const printContents = element.innerHTML;

    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;

    // Reinitialize after print
    location.reload();
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(container) {
    const spinnerHtml = `
        <div class="spinner-container">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    container.innerHTML = spinnerHtml;
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner(container) {
    const spinner = container.querySelector('.spinner-container');
    if (spinner) {
        spinner.remove();
    }
}

/**
 * Validate form before submission
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required]');
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

/**
 * Auto-format currency input
 */
function formatCurrencyInput(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    input.value = parts.join('.');
}

/**
 * Initialize currency input formatting
 */
document.addEventListener('DOMContentLoaded', function() {
    const currencyInputs = document.querySelectorAll('input[data-format="currency"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            formatCurrencyInput(this);
        });
    });
});

/**
 * Keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Quick search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Ctrl/Cmd + N: New transaction
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const newButton = document.querySelector('a[href*="add"]');
        if (newButton) {
            window.location.href = newButton.href;
        }
    }
});

/**
 * Check for unsaved changes before leaving
 */
function checkUnsavedChanges(form) {
    let originalData = new FormData(form);
    window.addEventListener('beforeunload', function(e) {
        let currentData = new FormData(form);
        let isChanged = false;

        for (let [key, value] of originalData.entries()) {
            if (currentData.get(key) !== value) {
                isChanged = true;
                break;
            }
        }

        if (isChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

/**
 * Update summary stats periodically
 */
async function updateSummaryStats() {
    const result = await fetchAPI(API_ENDPOINTS.summary);
    if (result) {
        updateSummaryCards(result);
    }
}

/**
 * Update summary cards with new data
 */
function updateSummaryCards(data) {
    const incomeCard = document.querySelector('.income-card .card-title');
    const expenseCard = document.querySelector('.expense-card .card-title');
    const savingsCard = document.querySelector('.savings-card .card-title');

    if (incomeCard) {
        incomeCard.textContent = formatCurrency(data.income);
        incomeCard.classList.add('fade-in');
    }

    if (expenseCard) {
        expenseCard.textContent = formatCurrency(data.expenses);
        expenseCard.classList.add('fade-in');
    }

    if (savingsCard) {
        savingsCard.textContent = formatCurrency(data.savings);
        savingsCard.classList.remove('text-success', 'text-danger');
        savingsCard.classList.add(data.savings >= 0 ? 'text-success' : 'text-danger');
        savingsCard.classList.add('fade-in');
    }
}

/**
 * Category suggestions based on description
 */
async function getCategorySuggestions(description) {
    if (!description || description.length < 3) return [];

    const result = await fetchAPI(`${API_ENDPOINTS.suggestions}?description=${encodeURIComponent(description)}`);
    return result?.suggestions || [];
}

/**
 * Display category suggestions
 */
async function displayCategorySuggestions(descriptionInput, categorySelect) {
    const description = descriptionInput.value;
    const suggestions = await getCategorySuggestions(description);

    if (suggestions.length > 0 && suggestions[0][1] === 100) {
        // Auto-select if high confidence
        categorySelect.value = suggestions[0][0];
    }
}

// Expose functions to global scope for inline event handlers
window.refreshDashboard = function() {
    location.reload();
};

window.printReport = function() {
    window.print();
};

window.exportData = function(data, filename) {
    exportToCSV(data, filename);
};
