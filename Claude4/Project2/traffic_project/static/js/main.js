/**
 * Traffic Prediction System - Main JavaScript
 *
 * BCA Final Year Project - AI-Based Traffic Congestion Prediction
 * Common utilities and global functionality
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Debounce function to limit the rate of function execution
 * @param {Function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @returns {Function} Debounced function
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
 * Format a number with commas
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Get the CSRF token from the page
 * @returns {string} CSRF token
 */
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, info)
 * @param {number} duration - How long to show the notification (ms)
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto remove after duration
    setTimeout(() => {
        notification.classList.add('notification-hidden');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

/**
 * Show a loading spinner
 * @param {HTMLElement} element - The element to contain the spinner
 * @param {boolean} show - Whether to show or hide the spinner
 */
function toggleLoading(element, show = true) {
    if (show) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

/**
 * Animate a number from 0 to target
 * @param {HTMLElement} element - The element containing the number
 * @param {number} target - The target number
 * @param {number} duration - Animation duration in ms
 */
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = formatNumber(Math.round(target));
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.round(current));
        }
    }, 16);
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

/**
 * Validate a form field
 * @param {HTMLElement} field - The input field to validate
 * @returns {boolean} Whether the field is valid
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';

    // Check required fields
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required';
    }

    // Check email format
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
    }

    // Check number range
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        const min = parseFloat(field.min);
        const max = parseFloat(field.max);

        if (!isNaN(min) && num < min) {
            isValid = false;
            message = `Minimum value is ${min}`;
        }
        if (!isNaN(max) && num > max) {
            isValid = false;
            message = `Maximum value is ${max}`;
        }
    }

    // Update field appearance
    if (!isValid) {
        field.classList.add('invalid');
        showError(field, message);
    } else {
        field.classList.remove('invalid');
        hideError(field);
    }

    return isValid;
}

/**
 * Show an error message for a field
 * @param {HTMLElement} field - The input field
 * @param {string} message - The error message
 */
function showError(field, message) {
    let errorElement = field.parentElement.querySelector('.error-message');

    if (!errorElement) {
        errorElement = document.createElement('span');
        errorElement.className = 'error-message';
        field.parentElement.appendChild(errorElement);
    }

    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

/**
 * Hide error message for a field
 * @param {HTMLElement} field - The input field
 */
function hideError(field) {
    const errorElement = field.parentElement.querySelector('.error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Validate an entire form
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} Whether the form is valid
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

// ============================================================================
// API HELPERS
// ============================================================================

/**
 * Make an API request
 * @param {string} url - The URL to request
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    };

    const mergedOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Make a GET request
 * @param {string} url - The URL to request
 * @returns {Promise<Object>} Response data
 */
async function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

/**
 * Make a POST request
 * @param {string} url - The URL to request
 * @param {Object} data - The data to send
 * @returns {Promise<Object>} Response data
 */
async function apiPost(url, data) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ============================================================================
// CHART HELPERS
// ============================================================================

/**
 * Default chart colors
 */
const chartColors = {
    primary: 'rgba(59, 130, 246, 0.8)',
    success: 'rgba(16, 185, 129, 0.8)',
    warning: 'rgba(245, 158, 11, 0.8)',
    danger: 'rgba(239, 68, 68, 0.8)',
    info: 'rgba(6, 182, 212, 0.8)',
};

/**
 * Create a default chart configuration
 * @param {string} type - Chart type
 * @param {Object} data - Chart data
 * @param {Object} options - Chart options
 * @returns {Object} Chart configuration
 */
function createChartConfig(type, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom',
            },
        },
    };

    return {
        type,
        data,
        options: { ...defaultOptions, ...options },
    };
}

// ============================================================================
// LOCAL STORAGE HELPERS
// ============================================================================

/**
 * Save data to local storage
 * @param {string} key - The storage key
 * @param {any} value - The value to store
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to local storage:', error);
    }
}

/**
 * Get data from local storage
 * @param {string} key - The storage key
 * @returns {any} The stored value or null
 */
function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Error reading from local storage:', error);
        return null;
    }
}

/**
 * Remove data from local storage
 * @param {string} key - The storage key
 */
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from local storage:', error);
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add form validation listeners
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        const fields = form.querySelectorAll('input, select, textarea');

        fields.forEach(field => {
            // Validate on blur
            field.addEventListener('blur', () => validateField(field));

            // Clear error on input
            field.addEventListener('input', () => {
                field.classList.remove('invalid');
                hideError(field);
            });
        });

        // Validate on submit
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Initialize any stats numbers on the page
    const statNumbers = document.querySelectorAll('.stat-value');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent.replace(/,/g, ''));
        if (!isNaN(target) && target > 0) {
            // Only animate if number is reasonably small
            if (target < 10000) {
                animateNumber(stat, target);
            }
        }
    });

    console.log('Traffic Prediction System initialized');
});

// ============================================================================
// EXPORTS (for module usage)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        debounce,
        formatNumber,
        getCSRFToken,
        showNotification,
        toggleLoading,
        animateNumber,
        validateField,
        validateForm,
        apiRequest,
        apiGet,
        apiPost,
        createChartConfig,
        saveToLocalStorage,
        getFromLocalStorage,
        removeFromLocalStorage,
    };
}
