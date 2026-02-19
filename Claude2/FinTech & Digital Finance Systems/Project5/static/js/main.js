/**
 * FinRisk AI - Main JavaScript
 * Handles all client-side functionality
 */

// ==================== UTILITY FUNCTIONS ====================

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    return `${value.toFixed(2)}%`;
}

// ==================== AJAX HELPERS ====================

/**
 * Fetch API wrapper with CSRF token
 */
async function fetchWithCSRF(url, options = {}) {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                      getCookie('csrftoken');

    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        ...options.headers
    };

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'same-origin'
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

/**
 * Get cookie value
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// ==================== FORM HANDLING ====================

/**
 * Handle AJAX form submission
 */
function handleFormSubmit(formId, successCallback) {
    const form = document.getElementById(formId);

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Convert numeric fields
        for (const key in data) {
            if (data[key] && !isNaN(data[key])) {
                const num = parseFloat(data[key]);
                if (Number.isInteger(num)) {
                    data[key] = parseInt(num);
                } else {
                    data[key] = num;
                }
            }
        }

        try {
            const response = await fetchWithCSRF(form.action, {
                method: 'POST',
                body: JSON.stringify(data)
            });

            if (response.success) {
                showToast(response.message || 'Success!', 'success');
                if (successCallback) successCallback(response);
            } else {
                showToast(response.errors || 'An error occurred', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.', 'error');
        }
    });
}

// ==================== TRANSACTION HANDLING ====================

/**
 * Add transaction via AJAX
 */
async function addTransaction(profileId) {
    const form = document.getElementById('transactionForm');

    const formData = new FormData(form);
    const data = {
        date: formData.get('date'),
        category: formData.get('category'),
        amount: parseFloat(formData.get('amount')),
        transaction_type: formData.get('transaction_type'),
        description: formData.get('description') || ''
    };

    try {
        const response = await fetchWithCSRF(`/profiles/${profileId}/transactions/add/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        if (response.success) {
            showToast('Transaction added successfully!', 'success');
            // Reload page to show updated data
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast('Error adding transaction', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    }
}

/**
 * Delete transaction
 */
async function deleteTransaction(transactionId) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }

    try {
        const response = await fetchWithCSRF(`/api/transactions/${transactionId}/delete/`, {
            method: 'DELETE'
        });

        if (response.success) {
            showToast('Transaction deleted', 'success');
            const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
            if (row) row.remove();

            // Update totals
            updateTransactionTotals();
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error deleting transaction', 'error');
    }
}

/**
 * Update transaction totals display
 */
function updateTransactionTotals() {
    // This would be called after adding/deleting transactions
    // In a real app, you'd recalculate from the visible rows
    window.location.reload();
}

// ==================== SCENARIO CALCULATOR ====================

/**
 * Calculate scenario projections
 */
async function calculateScenario() {
    const currentPortfolio = parseFloat(document.getElementById('currentPortfolio')?.value || 100000);
    const monthlyContribution = parseFloat(document.getElementById('monthlyContribution')?.value || 1000);
    const savingsIncrease = parseFloat(document.getElementById('savingsIncrease')?.value || 0);
    const marketChange = parseFloat(document.getElementById('marketChange')?.value || 0);
    const baseReturn = parseFloat(document.getElementById('baseReturn')?.value || 7);

    const data = {
        currentPortfolio,
        monthlyContribution,
        savingsIncrease,
        marketChange,
        baseReturn
    };

    try {
        const response = await fetchWithCSRF('/api/calculate-scenario/', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        if (response.success) {
            updateScenarioResults(response);
            showToast('Calculations updated', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error calculating scenario', 'error');
    }
}

/**
 * Update scenario results display
 */
function updateScenarioResults(data) {
    const resultsDiv = document.getElementById('scenarioResults');
    if (!resultsDiv) return;

    let html = '<div class="card"><div class="card-header"><h3 class="card-title">Projection Results</h3></div><div class="card-body">';

    html += `<p class="mb-2"><strong>Adjusted Annual Return:</strong> ${data.adjustedReturn}%</p>`;
    html += `<p class="mb-3"><strong>Adjusted Monthly Contribution:</strong> ${formatCurrency(data.adjustedMonthly)}</p>`;

    html += '<table class="table"><thead><tr>';
    html += '<th>Years</th><th>Portfolio Value</th><th>Total Contributions</th><th>Investment Gains</th>';
    html += '</tr></thead><tbody>';

    data.projections.forEach(proj => {
        html += `<tr>
            <td>${proj.years}</td>
            <td>${formatCurrency(proj.value)}</td>
            <td>${formatCurrency(proj.contributions)}</td>
            <td class="text-success">${formatCurrency(proj.gains)}</td>
        </tr>`;
    });

    html += '</tbody></table></div></div>';

    resultsDiv.innerHTML = html;
}

// ==================== CHART.JS HELPERS ====================

/**
 * Create a bar chart
 */
function createBarChart(canvasId, labels, data, label, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Create a scatter plot
 */
function createScatterChart(canvasId, data, xLabel, yLabel) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Asset Classes',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointRadius: 8,
                pointHoverRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.label}: Risk ${context.raw.x}%, Return ${context.raw.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xLabel,
                        font: { size: 14, weight: 'bold' }
                    },
                    beginAtZero: true
                },
                y: {
                    title: {
                        display: true,
                        text: yLabel,
                        font: { size: 14, weight: 'bold' }
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Create a doughnut chart
 */
function createDoughnutChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                }
            }
        }
    });
}

// ==================== SCROLL ANIMATIONS ====================

/**
 * Initialize scroll-triggered animations
 */
function initScrollAnimations() {
    // Create intersection observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    const animatedElements = document.querySelectorAll('[data-aos]');
    animatedElements.forEach(el => observer.observe(el));
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(targetId, offset = 80) {
    const target = document.getElementById(targetId);
    if (target) {
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Interactive mouse parallax effect for orbs
 */
function initMouseParallax() {
    const heroSection = document.querySelector('.hero-section');
    const orbs = document.querySelectorAll('.gradient-orb');

    if (!heroSection || orbs.length === 0) return;

    heroSection.addEventListener('mousemove', (e) => {
        const rect = heroSection.getBoundingClientRect();
        const x = (e.clientX - rect.left - rect.width / 2) / rect.width;
        const y = (e.clientY - rect.top - rect.height / 2) / rect.height;

        orbs.forEach((orb, index) => {
            const speed = (index + 1) * 20;
            const moveX = x * speed;
            const moveY = y * speed;
            orb.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
    });

    heroSection.addEventListener('mouseleave', () => {
        orbs.forEach(orb => {
            orb.style.transform = 'translate(0, 0)';
        });
    });
}

/**
 * Parallax effect for hero background
 */
function initParallaxEffect() {
    const heroBackground = document.querySelector('.hero-background');
    if (!heroBackground) return;

    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrolled = window.pageYOffset;
                const parallaxSpeed = 0.3;
                heroBackground.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
                ticking = false;
            });
            ticking = true;
        }
    });
}

/**
 * Initialize navbar background on scroll
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

/**
 * 3D Tilt effect for feature cards
 */
function init3DTiltEffect() {
    const cards = document.querySelectorAll('.feature-card, .stat-card-enhanced');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

/**
 * Typing animation for hero title
 */
function initTypingAnimation() {
    const titleElement = document.querySelector('.title-gradient');
    if (!titleElement) return;

    const text = titleElement.textContent;
    titleElement.textContent = '';
    titleElement.style.borderRight = '3px solid var(--color-success)';

    let index = 0;
    const typingSpeed = 100;

    function type() {
        if (index < text.length) {
            titleElement.textContent += text.charAt(index);
            index++;
            setTimeout(type, typingSpeed);
        } else {
            setTimeout(() => {
                titleElement.style.borderRight = 'none';
            }, 1000);
        }
    }

    // Start typing after a delay
    setTimeout(type, 500);
}

/**
 * Scroll progress indicator
 */
function initScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, var(--color-success), var(--color-accent));
        z-index: 10000;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = (window.scrollY / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
}

/**
 * Interactive particles in hero
 */
function initParticles() {
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;

    const particleContainer = document.createElement('div');
    particleContainer.className = 'particles-container';
    particleContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    `;
    heroSection.appendChild(particleContainer);

    // Create particles
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 2}px;
            height: ${Math.random() * 4 + 2}px;
            background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: floatParticle ${Math.random() * 10 + 10}s linear infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        particleContainer.appendChild(particle);
    }

    // Add keyframes if not exists
    if (!document.getElementById('particle-keyframes')) {
        const style = document.createElement('style');
        style.id = 'particle-keyframes';
        style.textContent = `
            @keyframes floatParticle {
                0% {
                    transform: translateY(0) translateX(0);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) translateX(${Math.random() * 100 - 50}px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Magnetic button effect
 */
function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn-primary, .btn-glass');

    buttons.forEach(button => {
        button.addEventListener('mousemove', (e) => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            button.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translate(0, 0)';
        });
    });
}

/**
 * Ripple effect on buttons
 */
function initRippleEffect() {
    document.addEventListener('click', (e) => {
        const button = e.target.closest('.btn');
        if (!button) return;

        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });

    // Add ripple keyframes
    if (!document.getElementById('ripple-keyframes')) {
        const style = document.createElement('style');
        style.id = 'ripple-keyframes';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Counter animation with easing
 */
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const startTime = performance.now();
    const startValue = 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out cubic)
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(startValue + (target - startValue) * eased);

        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target.toLocaleString();
        }
    }

    requestAnimationFrame(update);
}

/**
 * Glowing cursor trail effect
 */
function initCursorTrail() {
    const trailContainer = document.createElement('div');
    trailContainer.id = 'cursor-trail-container';
    trailContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9998;
    `;
    document.body.appendChild(trailContainer);

    const trails = [];
    const trailCount = 10;

    for (let i = 0; i < trailCount; i++) {
        const trail = document.createElement('div');
        trail.className = 'cursor-trail';
        trail.style.cssText = `
            position: absolute;
            width: ${15 - i}px;
            height: ${15 - i}px;
            background: radial-gradient(circle, rgba(0, 212, 170, ${0.5 - i * 0.05}) 0%, transparent 70%);
            border-radius: 50%;
            transition: transform 0.1s ease;
        `;
        trailContainer.appendChild(trail);
        trails.push({ element: trail, x: 0, y: 0 });
    }

    let mouseX = 0, mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrail() {
        let x = mouseX;
        let y = mouseY;

        trails.forEach((trail, index) => {
            const nextTrail = trails[index + 1] || trails[0];

            trail.x += (x - trail.x) * (0.3 - index * 0.02);
            trail.y += (y - trail.y) * (0.3 - index * 0.02);

            trail.element.style.left = trail.x + 'px';
            trail.element.style.top = trail.y + 'px';
            trail.element.style.transform = `translate(-50%, -50%)`;

            x = trail.x;
            y = trail.y;
        });

        requestAnimationFrame(animateTrail);
    }

    animateTrail();
}

/**
 * Stats hover interaction
 */
function initStatsInteraction() {
    const statCards = document.querySelectorAll('.stat-card-enhanced');

    statCards.forEach(card => {
        const icon = card.querySelector('.stat-icon');
        if (icon) {
            card.addEventListener('mouseenter', () => {
                icon.style.transform = 'scale(1.2) rotate(10deg)';
                icon.style.transition = 'transform 0.3s ease';
            });

            card.addEventListener('mouseleave', () => {
                icon.style.transform = 'scale(1) rotate(0deg)';
            });
        }
    });
}

/**
 * Wave animation for CTA section
 */
function initWaveAnimation() {
    const ctaCard = document.querySelector('.cta-card');
    if (!ctaCard) return;

    ctaCard.addEventListener('mousemove', (e) => {
        const rect = ctaCard.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        ctaCard.style.background = `
            radial-gradient(
                circle at ${x}% ${y}%,
                rgba(59, 130, 246, 0.8) 0%,
                var(--color-primary) 50%
            )
        `;
    });

    ctaCard.addEventListener('mouseleave', () => {
        ctaCard.style.background = 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%)';
    });
}

/**
 * Dynamic time-based greeting
 */
function initDynamicGreeting() {
    const badgeText = document.querySelector('.hero-badge span:last-child');
    if (!badgeText) return;

    const hour = new Date().getHours();
    let greeting;

    if (hour < 12) {
        greeting = '☀️ Good Morning - AI-Powered Financial Intelligence';
    } else if (hour < 17) {
        greeting = '🌤️ Good Afternoon - AI-Powered Financial Intelligence';
    } else if (hour < 21) {
        greeting = '🌙 Good Evening - AI-Powered Financial Intelligence';
    } else {
        greeting = '⭐ Welcome - AI-Powered Financial Intelligence';
    }

    badgeText.textContent = greeting;
}

/**
 * Sound effects on interactions (optional - commented out by default)
 */
function initSoundEffects() {
    // Uncomment to enable sound effects
    /*
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    function playSound(frequency, duration) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    }

    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => playSound(800, 0.1));
    });
    */
}

/**
 * Smooth page load animation
 */
function initPageLoadAnimation() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';

    window.addEventListener('load', () => {
        setTimeout(() => {
            document.body.style.opacity = '1';
        }, 100);
    });
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any auto-focus elements
    const firstInput = document.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        firstInput.focus();
    }

    // Initialize scenario calculator if present
    const calculateBtn = document.getElementById('calculateScenarioBtn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', calculateScenario);
    }

    // Initialize all interactive effects
    initScrollAnimations();
    initParallaxEffect();
    initNavbarScroll();
    initMouseParallax();
    init3DTiltEffect();
    initTypingAnimation();
    initScrollProgress();
    initParticles();
    initMagneticButtons();
    initRippleEffect();
    initCursorTrail();
    initStatsInteraction();
    initWaveAnimation();
    initDynamicGreeting();
    initPageLoadAnimation();
    initSoundEffects();

    // Animated counters on scroll
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counters = entry.target.querySelectorAll('.stat-value-animated');
                    counters.forEach(counter => animateCounter(counter));
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        observer.observe(statsSection);
    }

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        [data-aos] {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }

        [data-aos].animate-in {
            opacity: 1;
            transform: translateY(0);
        }

        .navbar-scrolled {
            background-color: rgba(10, 37, 64, 0.95) !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        .stat-card-enhanced,
        .feature-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            transform-style: preserve-3d;
        }

        .hero-badge {
            animation: fadeInUp 0.8s ease-out;
        }

        .hero-title .title-line {
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }

        .hero-description {
            animation: fadeInUp 0.8s ease-out 0.4s both;
        }

        .hero-actions {
            animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .hero-trust {
            animation: fadeInUp 0.8s ease-out 0.8s both;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .btn:hover {
            animation: pulse 0.6s ease-in-out;
        }

        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }

        /* Selection color */
        ::selection {
            background: var(--color-success);
            color: var(--color-primary);
        }

        /* Loading animation for stats */
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        .stat-value-animated {
            background: linear-gradient(
                90deg,
                var(--color-gray-200) 0%,
                var(--color-gray-100) 50%,
                var(--color-gray-200) 100%
            );
            background-size: 1000px 100%;
            animation: shimmer 2s infinite;
        }

        .stat-value-animated:not(:empty) {
            background: none;
            animation: none;
        }
    `;
    document.head.appendChild(style);
});

// ==================== EXPORT FUNCTIONS ====================

// Make functions available globally for inline event handlers
window.showToast = showToast;
window.formatCurrency = formatCurrency;
window.addTransaction = addTransaction;
window.deleteTransaction = deleteTransaction;
window.calculateScenario = calculateScenario;
window.createBarChart = createBarChart;
window.createScatterChart = createScatterChart;
window.createDoughnutChart = createDoughnutChart;
window.smoothScrollTo = smoothScrollTo;
window.animateCounter = animateCounter;
window.initScrollAnimations = initScrollAnimations;
window.initMouseParallax = initMouseParallax;
window.init3DTiltEffect = init3DTiltEffect;
window.initParticles = initParticles;
