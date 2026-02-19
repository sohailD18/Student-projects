/**
 * EV Trip Planner - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initChatWidget();
    initFormValidation();
    initAnimations();
});

/**
 * Mobile Navigation Toggle
 */
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
            }
        });
    }

    // Dropdown menus
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.stopPropagation();
                const content = this.querySelector('.nav-dropdown-content');
                content.style.display = content.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
}

/**
 * Floating Chat Widget
 */
function initChatWidget() {
    const chatWidget = document.getElementById('chatWidget');
    if (!chatWidget) return;

    const toggle = document.getElementById('chatWidgetToggle');
    const window = document.getElementById('chatWidgetWindow');
    const close = document.getElementById('chatWidgetClose');
    const input = document.getElementById('chatWidgetInput');
    const send = document.getElementById('chatWidgetSend');
    const messagesContainer = document.getElementById('chatWidgetMessages');

    if (!toggle || !window) return;

    // Toggle chat window
    toggle.addEventListener('click', function() {
        window.classList.toggle('active');
        if (window.classList.contains('active')) {
            input.focus();
        }
    });

    // Close chat window
    if (close) {
        close.addEventListener('click', function() {
            window.classList.remove('active');
        });
    }

    // Send message
    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, true);
        input.value = '';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/chat/api/widget/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.success) {
                addMessage(data.response, false);
            }
        } catch (error) {
            hideTypingIndicator();
            addMessage('Sorry, something went wrong. Please try again.', false);
        }
    }

    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'chat-message-user' : 'chat-message-ai'}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">${isUser ? '👤' : '⚡'}</div>
            <div class="message-content">
                <div class="message-text">${text.replace(/\n/g, '<br>')}</div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message chat-message-ai typing-indicator';
        typingDiv.id = 'widgetTypingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">⚡</div>
            <div class="message-content">
                <div class="typing-dots"><span></span><span></span><span></span></div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTypingIndicator() {
        const typing = document.getElementById('widgetTypingIndicator');
        if (typing) typing.remove();
    }

    // Send on button click
    if (send) {
        send.addEventListener('click', sendMessage);
    }

    // Send on Enter key
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validation]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    showFieldError(field, 'This field is required');
                } else {
                    field.classList.remove('error');
                    hideFieldError(field);
                }
            });

            // Email validation
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                if (field.value && !isValidEmail(field.value)) {
                    isValid = false;
                    field.classList.add('error');
                    showFieldError(field, 'Please enter a valid email address');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(field, message) {
    let errorDiv = field.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains('field-error')) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideFieldError(field) {
    let errorDiv = field.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('field-error')) {
        errorDiv.style.display = 'none';
    }
}

/**
 * Animations
 */
function initAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe animated elements
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

/**
 * Utility Functions
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

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

function formatNumber(num, decimals = 1) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

// Export functions for use in templates
window.EVTripPlanner = {
    getCookie,
    formatCurrency,
    formatNumber
};

// Global function to open chat widget from any page
window.openChatWidget = function() {
    const chatWidgetWindow = document.getElementById('chatWidgetWindow');
    if (chatWidgetWindow) {
        chatWidgetWindow.classList.add('active');
        // Focus on the input after a short delay
        setTimeout(() => {
            const chatWidgetInput = document.getElementById('chatWidgetInput');
            if (chatWidgetInput) {
                chatWidgetInput.focus();
            }
        }, 100);
    }
};
