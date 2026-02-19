/**
 * ProductivityMind - Utility Functions
 * Common utilities for UI components, formatting, etc.
 */

// =============================================================================
// Toast Notifications
// =============================================================================

const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toastContainer');
    },

    show(message, type = 'info', duration = 5000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                ${this.getIcon(type)}
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        `;

        this.container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                toast.remove();
            }, duration);
        }

        return toast;
    },

    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    error(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration) {
        return this.show(message, 'info', duration);
    },

    getIcon(type) {
        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>',
        };
        return icons[type] || icons.info;
    }
};

// =============================================================================
// Modal
// =============================================================================

const Modal = {
    container: null,
    overlay: null,
    modal: null,
    title: null,
    body: null,

    init() {
        this.container = document.getElementById('modalContainer');
        this.overlay = document.getElementById('modalOverlay');
        this.modal = document.getElementById('modal');
        this.title = document.getElementById('modalTitle');
        this.body = document.getElementById('modalBody');
        this.close = document.getElementById('modalClose');

        this.close.addEventListener('click', () => this.hide());
        this.overlay.addEventListener('click', () => this.hide());
    },

    show(title, content, footer = null) {
        if (!this.container) this.init();

        this.title.textContent = title;
        this.body.innerHTML = content;

        if (footer) {
            const footerEl = document.createElement('div');
            footerEl.className = 'modal-footer';
            footerEl.innerHTML = footer;
            this.body.appendChild(footerEl);
        }

        this.container.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    hide() {
        if (!this.container) return;
        this.container.classList.remove('active');
        document.body.style.overflow = '';
    }
};

// =============================================================================
// Formatting Functions
// =============================================================================

const Format = {
    /**
     * Format date to readable string
     */
    date(dateString, options = {}) {
        if (!dateString) return 'No date';

        const date = new Date(dateString);
        const defaults = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        };

        return date.toLocaleDateString('en-US', { ...defaults, ...options });
    },

    /**
     * Format date and time
     */
    dateTime(dateString) {
        return this.date(dateString, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    /**
     * Format relative time (e.g., "2 days ago")
     */
    relativeTime(dateString) {
        if (!dateString) return 'No date';

        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) return 'just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        return this.date(dateString);
    },

    /**
     * Format time until due date
     */
    timeUntil(dateString) {
        if (!dateString) return 'No due date';

        const date = new Date(dateString);
        const now = new Date();
        const diffMs = date - now;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

        if (diffMs < 0) return 'Overdue';
        if (diffDays === 0) return `Due in ${diffHours} hour${diffHours > 1 ? 's' : ''}`;
        if (diffDays === 1) return 'Due tomorrow';
        if (diffDays < 7) return `Due in ${diffDays} days`;
        return this.date(dateString);
    },

    /**
     * Format number with commas
     */
    number(num) {
        return num.toLocaleString('en-US');
    },

    /**
     * Format percentage
     */
    percentage(value, decimals = 1) {
        return `${(value * 100).toFixed(decimals)}%`;
    },

    /**
     * Format hours
     */
    hours(hours) {
        if (!hours) return '0h';
        const rounded = Math.round(hours * 10) / 10;
        return `${rounded}h`;
    },
};

// =============================================================================
// Status & Priority Helpers
// =============================================================================

const StatusHelper = {
    classes: {
        todo: 'badge-gray',
        in_progress: 'badge-primary',
        done: 'badge-success',
        cancelled: 'badge-danger',
    },

    icons: {
        todo: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><circle cx="10" cy="10" r="8"/></svg>',
        in_progress: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/></svg>',
        done: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
        cancelled: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
    },

    getBadge(status, label) {
        return `<span class="badge ${this.classes[status]}">${this.icons[status]} ${label}</span>`;
    },
};

const PriorityHelper = {
    classes: {
        low: 'text-success',
        medium: 'text-warning',
        high: 'text-danger',
        critical: 'text-danger',
    },

    getBadge(priority, label) {
        return `<span class="${this.classes[priority]}">${label}</span>`;
    },
};

const RiskHelper = {
    classes: {
        none: 'badge-gray',
        low: 'badge-primary',
        medium: 'badge-warning',
        high: 'badge-danger',
        critical: 'badge-danger',
    },

    getIndicator(riskLevel, label) {
        return `<span class="badge ${this.classes[riskLevel]}">${label}</span>`;
    },
};

// =============================================================================
// Loading States
// =============================================================================

const Loading = {
    /**
     * Show loading spinner on an element
     */
    show(element) {
        element.innerHTML = '<div class="loading"></div>';
    },

    /**
     * Show skeleton loading for cards
     */
    skeleton(element, count = 3) {
        let html = '';
        for (let i = 0; i < count; i++) {
            html += `
                <div class="skeleton" style="height: 80px; margin-bottom: 1rem;"></div>
            `;
        }
        element.innerHTML = html;
    },
};

// =============================================================================
// Chart Configuration
// =============================================================================

const ChartConfig = {
    colors: {
        primary: '#6366f1',
        success: '#22c55e',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#0ea5e9',
        gray: '#6b7280',
    },

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 16,
                    color: '#374151',
                    font: {
                        size: 12,
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#6b7280',
                    font: {
                        size: 11
                    }
                },
                grid: {
                    display: false
                }
            },
            y: {
                ticks: {
                    color: '#6b7280',
                    font: {
                        size: 11
                    }
                },
                grid: {
                    color: '#e5e7eb'
                }
            }
        }
    },

    createDoughnut(data, labels) {
        return {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        this.colors.primary,
                        this.colors.success,
                        this.colors.warning,
                        this.colors.danger,
                        this.colors.info,
                    ],
                    borderWidth: 0,
                }]
            },
            options: {
                ...this.defaultOptions,
                cutout: '70%',
            }
        };
    },

    createBar(data, labels, labelText = 'Tasks') {
        return {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: data,
                    backgroundColor: this.colors.primary,
                    borderRadius: 8,
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: false,
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            precision: 0,
                        }
                    }
                }
            }
        };
    },

    createLine(data, labels, labelText = 'Tasks Completed') {
        return {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: data,
                    borderColor: this.colors.primary,
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            precision: 0,
                        }
                    }
                }
            }
        };
    },
};

// =============================================================================
// Initialize on DOM ready
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    Toast.init();
    Modal.init();

    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 1024 &&
                !sidebar.contains(e.target) &&
                !sidebarToggle.contains(e.target) &&
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            window.location.reload();
        });
    }
});

// Export utilities
window.Toast = Toast;
window.Modal = Modal;
window.Format = Format;
window.StatusHelper = StatusHelper;
window.PriorityHelper = PriorityHelper;
window.RiskHelper = RiskHelper;
window.Loading = Loading;
window.ChartConfig = ChartConfig;
