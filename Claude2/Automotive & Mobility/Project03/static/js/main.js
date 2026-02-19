/**
 * Driver Behavior Analysis System - Main JavaScript
 * Common functionality across all pages
 */

// Utility Functions
const DriverApp = {
    // Format date for display
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    },

    // Calculate percentage
    calculatePercentage: function(value, total) {
        if (total === 0) return 0;
        return ((value / total) * 100).toFixed(1);
    },

    // Get color based on risk score
    getRiskColor: function(score) {
        if (score < 30) return '#4caf50'; // Green
        if (score < 70) return '#ff9800'; // Orange
        return '#f44336'; // Red
    },

    // Get classification from score
    getClassification: function(score) {
        if (score < 30) return 'Safe';
        if (score < 70) return 'Moderate';
        return 'Risky';
    },

    // Show loading spinner
    showLoading: function(container) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        container.appendChild(spinner);
        return spinner;
    },

    // Remove loading spinner
    hideLoading: function(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    },

    // Display success message
    showSuccess: function(message) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message success';
        msgDiv.textContent = message;
        this.insertMessage(msgDiv);
    },

    // Display error message
    showError: function(message) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message error';
        msgDiv.textContent = message;
        this.insertMessage(msgDiv);
    },

    // Insert message at the top of the page
    insertMessage: function(messageElement) {
        const messagesContainer = document.querySelector('.messages') ||
                                   document.querySelector('main');
        if (messagesContainer) {
            messagesContainer.insertBefore(
                messageElement,
                messagesContainer.firstChild
            );
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 5000);
        }
    },

    // Fetch API wrapper with error handling
    fetchWithTimeout: async function(url, options = {}, timeout = 30000) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(id);
            return response;
        } catch (error) {
            clearTimeout(id);
            throw error;
        }
    },

    // Debounce function for performance
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format numbers with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Animate number counter
    animateCounter: function(element, target, duration = 1000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = this.formatNumber(Math.round(target));
                clearInterval(timer);
            } else {
                element.textContent = this.formatNumber(Math.round(current));
            }
        }, 16);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Driver Behavior Analysis System loaded');

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 5000);
    });

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Add confirmation for delete actions
    document.querySelectorAll('a[data-confirm]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DriverApp;
}
