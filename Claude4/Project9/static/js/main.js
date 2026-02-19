/*
 * AgriSense - Premium Interactive JavaScript
 * Smooth Animations • Scroll Effects • Interactive UI
 */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // ==========================================
    // Navigation Enhancements
    // ==========================================
    initNavigation();

    // ==========================================
    // Scroll Effects
    // ==========================================
    initScrollEffects();

    // ==========================================
    // Smooth Scroll for Anchor Links
    // ==========================================
    initSmoothScroll();

    // ==========================================
    // Auto-hide Messages
    // ==========================================
    initAutoHideMessages();

    // ==========================================
    // Scroll Animations
    // ==========================================
    initScrollAnimations();

    // ==========================================
    // Number Input Enhancement
    // ==========================================
    initNumberInputValidation();

    // ==========================================
    // Textarea Character Counter
    // ==========================================
    initCharacterCounters();

    // ==========================================
    // Parallax Effects
    // ==========================================
    initParallaxEffects();

    // ==========================================
    // Button Ripple Effect
    // ==========================================
    initRippleEffect();

    // ==========================================
    // Stats Counter Animation
    // ==========================================
    initCounterAnimation();

    // ==========================================
    // Magnetic Buttons Effect
    // ==========================================
    initMagneticButtons();
});

// ==========================================
// Navigation Functions
// ==========================================
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navbar = document.querySelector('.navbar');

    // Toggle mobile menu
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');

            // Accessibility
            const expanded = this.classList.contains('active');
            this.setAttribute('aria-expanded', expanded);
        });

        // Close menu on link click
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeMobileMenu();
            });
        });

        // Close menu on outside click
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navMenu.contains(event.target);
            const isClickOnToggle = navToggle.contains(event.target);

            if (!isClickInsideNav && !isClickOnToggle && navMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        });
    }

    // Add scroll effect to navbar
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    function closeMobileMenu() {
        if (navMenu) navMenu.classList.remove('active');
        if (navToggle) {
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    }
}

// ==========================================
// Scroll Effects
// ==========================================
function initScrollEffects() {
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                handleScroll();
                ticking = false;
            });
            ticking = true;
        }
    });
}

function handleScroll() {
    const scrollY = window.pageYOffset;
    const heroElements = document.querySelectorAll('.hero-illustration > div');

    heroElements.forEach((el, index) => {
        const speed = 0.05 * (index + 1);
        const yPos = -(scrollY * speed);
        el.style.transform = `translateY(${yPos}px)`;
    });
}

// ==========================================
// Smooth Scroll
// ==========================================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;

            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ==========================================
// Auto-hide Messages
// ==========================================
function initAutoHideMessages() {
    const messages = document.querySelectorAll('.alert');

    messages.forEach((message, index) => {
        setTimeout(() => {
            message.style.transition = 'all 0.5s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000 + (index * 500));
    });
}

// ==========================================
// Scroll Animations
// ==========================================
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';

                // Add staggered animation to children
                const children = entry.target.querySelectorAll('.feature-card, .info-card, .history-item');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.style.opacity = '1';
                        child.style.transform = 'translateY(0)';
                    }, index * 100);
                });

                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements
    const animatedElements = document.querySelectorAll(
        '.feature-card, .info-card, .result-card, .history-item, .stat-card, .sidebar-card'
    );

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

// ==========================================
// Number Input Validation
// ==========================================
function initNumberInputValidation() {
    const numberInputs = document.querySelectorAll('input[type="number"]');

    numberInputs.forEach(input => {
        // Prevent non-numeric input
        input.addEventListener('keypress', function(e) {
            const allowedKeys = [8, 9, 27, 13, 46, 110, 190]; // backspace, tab, escape, enter, delete, decimal point
            const isModifierKey = e.ctrlKey || e.metaKey || e.altKey;
            const isNumeric = (e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105);

            if (!isNumeric && !isModifierKey && !allowedKeys.includes(e.keyCode)) {
                e.preventDefault();
            }
        });

        // Format value on blur
        input.addEventListener('blur', function() {
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);

            if (this.value && !isNaN(min) && !isNaN(max)) {
                let value = parseFloat(this.value);
                if (value < min) this.value = min;
                if (value > max) this.value = max;
            }
        });

        // Add focus animation
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

// ==========================================
// Character Counters
// ==========================================
function initCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[minlength]');

    textareas.forEach(textarea => {
        const minLength = parseInt(textarea.getAttribute('minlength'));
        const maxLength = textarea.getAttribute('maxlength');

        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.cssText = `
            font-size: 0.875rem;
            margin-top: 0.5rem;
            text-align: right;
            transition: color 0.3s ease;
            font-weight: 500;
        `;

        textarea.parentNode.insertBefore(counter, textarea.nextSibling);

        // Update counter
        function updateCounter() {
            const currentLength = textarea.value.length;
            const remaining = minLength - currentLength;

            if (remaining > 0) {
                counter.textContent = `⚠️ ${remaining} more characters needed (min: ${minLength})`;
                counter.style.color = '#f44336';
            } else if (maxLength) {
                const maxRemaining = maxLength - currentLength;
                counter.textContent = `✓ ${currentLength}/${maxLength} characters`;
                counter.style.color = maxRemaining < 10 ? '#ff9800' : '#4caf50';
            } else {
                counter.textContent = `✓ Minimum length met (${currentLength}/${minLength})`;
                counter.style.color = '#4caf50';
            }
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });
}

// ==========================================
// Parallax Effects
// ==========================================
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.crop-circle, .stats-circle, .ai-circle');

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;

        parallaxElements.forEach((element, index) => {
            const speed = 0.05 * (index + 1);
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

// ==========================================
// Ripple Effect for Buttons
// ==========================================
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.5) 0%, transparent 70%);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;

            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add ripple animation to stylesheet
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// ==========================================
// Counter Animation
// ==========================================
function initCounterAnimation() {
    const counters = document.querySelectorAll('.stats-number, .stat-number');

    const observerOptions = {
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.textContent);
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;

                const updateCounter = () => {
                    current += step;
                    if (current < target) {
                        counter.textContent = Math.floor(current) + '%';
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target + '%';
                    }
                };

                updateCounter();
                observer.unobserve(counter);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
}

// ==========================================
// Magnetic Buttons Effect
// ==========================================
function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn-large');

    buttons.forEach(button => {
        button.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            this.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px) translateY(-3px)`;
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// ==========================================
// Utility Functions
// ==========================================

// Set button loading state
function setButtonLoading(button, loading) {
    if (!button) return;

    if (loading) {
        button.setAttribute('data-original-content', button.innerHTML);
        button.innerHTML = '<span class="btn-spinner"></span> Loading...';
        button.disabled = true;

        // Add spinner styles
        if (!document.getElementById('spinner-style')) {
            const style = document.createElement('style');
            style.id = 'spinner-style';
            style.textContent = `
                .btn-spinner {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top-color: #ffffff;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    } else {
        const original = button.getAttribute('data-original-content');
        if (original) {
            button.innerHTML = original;
            button.removeAttribute('data-original-content');
        }
        button.disabled = false;
    }
}

// Validate form
function validateForm(form) {
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            showInputError(input, 'This field is required');
            isValid = false;
        } else {
            clearInputError(input);
        }
    });

    // Email validation
    const emailInput = form.querySelector('input[type="email"]');
    if (emailInput && emailInput.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value)) {
            showInputError(emailInput, 'Please enter a valid email address');
            isValid = false;
        }
    }

    return isValid;
}

function showInputError(input, message) {
    input.style.borderColor = '#f44336';

    let error = input.parentNode.querySelector('.input-error');
    if (!error) {
        error = document.createElement('span');
        error.className = 'input-error';
        error.style.cssText = `
            display: block;
            color: #f44336;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        `;
        input.parentNode.appendChild(error);
    }
    error.textContent = message;
}

function clearInputError(input) {
    input.style.borderColor = '';

    const error = input.parentNode.querySelector('.input-error');
    if (error) {
        error.remove();
    }
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Debounce function
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

// Throttle function
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

// ==========================================
// Export for global use
// ==========================================
window.Agrisense = {
    setButtonLoading,
    validateForm,
    formatNumber,
    debounce,
    throttle
};

// ==========================================
// Console Welcome Message
// ==========================================
console.log('%c🌱 AgriSense Premium', 'font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #2E7D32, #43A047); -webkit-background-clip: text; -webkit-text-fill-color: transparent;');
console.log('%cAI-Powered Soil Health Analysis', 'font-size: 16px; color: #4CAF50; font-weight: 500;');
console.log('%c✨ Glassmorphism • Animations • Modern UI', 'font-size: 12px; color: #81C784;');
console.log('');
console.log('%cReady for Smart Agriculture 🚀', 'font-size: 14px; color: #1B5E20; font-weight: 600;');
