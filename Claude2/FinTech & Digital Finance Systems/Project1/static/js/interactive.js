/**
 * Fraud Detection System - Interactive Elements
 * Adds dynamic behavior, animations, and real-time updates
 */

// ========== Animated Counters ==========
class AnimatedCounter {
    constructor(element, target, duration = 2000) {
        this.element = element;
        this.target = parseInt(target);
        this.duration = duration;
        this.startTime = null;
        this.startValue = 0;
    }

    animate(currentTime) {
        if (!this.startTime) this.startTime = currentTime;
        const elapsed = currentTime - this.startTime;
        const progress = Math.min(elapsed / this.duration, 1);

        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = Math.floor(this.startValue + (this.target - this.startValue) * easeOutQuart);

        this.element.textContent = this.formatNumber(currentValue);

        if (progress < 1) {
            requestAnimationFrame(this.animate.bind(this));
        } else {
            this.element.classList.add('changed');
            setTimeout(() => this.element.classList.remove('changed'), 300);
        }
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    start() {
        requestAnimationFrame(this.animate.bind(this));
    }
}

// Initialize all counters on page load
function initCounters() {
    const counterElements = document.querySelectorAll('[data-count]');
    counterElements.forEach(el => {
        const target = el.getAttribute('data-count');
        new AnimatedCounter(el, target).start();
    });
}

// ========== Toast Notifications ==========
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${this.getIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.container.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            danger: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    success(message) { return this.show(message, 'success'); }
    danger(message) { return this.show(message, 'danger'); }
    warning(message) { return this.show(message, 'warning'); }
    info(message) { return this.show(message, 'info'); }
}

const toast = new ToastManager();

// ========== Theme Toggle ==========
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createToggle();
    }

    createToggle() {
        const toggle = document.createElement('div');
        toggle.className = 'theme-toggle';
        toggle.id = 'themeToggle';
        toggle.title = 'Toggle theme';
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('aria-label', 'Toggle dark/light mode');

        toggle.addEventListener('click', () => this.toggle());

        // Add to header
        const header = document.querySelector('.header-content');
        if (header) {
            const logo = document.querySelector('.logo');
            if (logo) {
                logo.insertAdjacentElement('afterend', toggle);
            }
        }
    }

    toggle() {
        const toggle = document.getElementById('themeToggle');
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        toggle.classList.toggle('active', this.currentTheme === 'light');
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme(theme) {
        const root = document.documentElement;
        if (theme === 'light') {
            root.style.setProperty('--bg-primary', '#f8fafc');
            root.style.setProperty('--bg-secondary', '#ffffff');
            root.style.setProperty('--bg-tertiary', '#e2e8f0');
            root.style.setProperty('--bg-card', '#ffffff');
            root.style.setProperty('--text-primary', '#0f172a');
            root.style.setProperty('--text-secondary', '#475569');
            root.style.setProperty('--text-muted', '#64748b');
            root.style.setProperty('--border-color', '#e2e8f0');
            document.body.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)';
        } else {
            root.style.setProperty('--bg-primary', '#0f172a');
            root.style.setProperty('--bg-secondary', '#1e293b');
            root.style.setProperty('--bg-tertiary', '#334155');
            root.style.setProperty('--bg-card', '#1e293b');
            root.style.setProperty('--text-primary', '#f1f5f9');
            root.style.setProperty('--text-secondary', '#cbd5e1');
            root.style.setProperty('--text-muted', '#94a3b8');
            root.style.setProperty('--border-color', '#334155');
            document.body.style.background = 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)';
        }
    }
}

// ========== Real-time Updates Simulator ==========
class RealTimeUpdater {
    constructor(updateInterval = 5000) {
        this.updateInterval = updateInterval;
        this.isActive = false;
    }

    start() {
        this.isActive = true;
        this.simulateUpdates();
    }

    simulateUpdates() {
        if (!this.isActive) return;

        // Simulate new transaction alerts
        if (Math.random() > 0.7) {
            const alerts = [
                { type: 'danger', message: 'High-risk transaction detected ($12,450)' },
                { type: 'warning', message: 'Unusual location pattern detected' },
                { type: 'info', message: 'New transaction batch processed' },
                { type: 'success', message: 'Model updated successfully' }
            ];

            const alert = alerts[Math.floor(Math.random() * alerts.length)];
            toast.show(alert.message, alert.type, 3000);
        }

        setTimeout(() => this.simulateUpdates(), this.updateInterval);
    }

    stop() {
        this.isActive = false;
    }
}

// ========== Skeleton Loading ==========
function showSkeleton(container, count = 4) {
    const skeletons = [];
    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'stat-card skeleton-card';
        skeleton.innerHTML = `
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text"></div>
        `;
        container.appendChild(skeleton);
        skeletons.push(skeleton);
    }
    return skeletons;
}

function removeSkeleton(skeletons) {
    skeletons.forEach(s => {
        s.style.opacity = '0';
        setTimeout(() => s.remove(), 300);
    });
}

// ========== Button Ripple Effect ==========
function initRippleEffect() {
    document.addEventListener('click', function(e) {
        const button = e.target.closest('.btn');
        if (!button) return;

        const ripple = document.createElement('span');
        ripple.className = 'ripple';

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';

        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
}

// ========== Live Indicator ==========
function addLiveIndicator() {
    const header = document.querySelector('.header-content');
    if (!header) return;

    const indicator = document.createElement('div');
    indicator.className = 'live-indicator';
    indicator.innerHTML = '● Live';
    indicator.style.marginLeft = 'auto';

    const nav = header.querySelector('nav');
    if (nav) {
        nav.insertAdjacentElement('beforebegin', indicator);
    }
}

// ========== Progress Bar Animation ==========
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(bar => {
        const target = bar.getAttribute('data-progress') || bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = target;
        }, 100);
    });
}

// ========== Notification Badge ==========
function updateNotificationBadge(count) {
    const badges = document.querySelectorAll('.notification-badge');
    badges.forEach(badge => {
        badge.setAttribute('data-count', count);
        if (count === 0) {
            badge.removeAttribute('data-count');
        }
    });
}

// ========== Initialize Everything ==========
document.addEventListener('DOMContentLoaded', function() {
    // Initialize counters
    initCounters();

    // Initialize theme toggle
    const themeManager = new ThemeManager();

    // Initialize ripple effect
    initRippleEffect();

    // Add live indicator
    addLiveIndicator();

    // Animate progress bars
    animateProgressBars();

    // Initialize real-time updates (optional - comment out if not needed)
    // const realTimeUpdater = new RealTimeUpdater();
    // realTimeUpdater.start();

    // Expose to global scope for external use
    window.toast = toast;
    window.themeManager = themeManager;
    window.AnimatedCounter = AnimatedCounter;
});

// ========== Utility Functions ==========

// Debounce function for performance
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

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard!');
        return true;
    } catch (err) {
        toast.danger('Failed to copy');
        return false;
    }
}

console.log('🛡️ Fraud Detection System - Interactive Features Loaded');
