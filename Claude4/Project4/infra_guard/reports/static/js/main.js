/*
 * InfraGuard - Main JavaScript
 * Handles geolocation, form interactions, and mobile menu
 */

// ==================== Mobile Menu Toggle ====================
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const navMenu = document.querySelector('.nav-menu');
    const mobileBtn = document.querySelector('.mobile-menu-btn');

    if (!navMenu.contains(event.target) && !mobileBtn.contains(event.target)) {
        navMenu.classList.remove('active');
    }
});

// ==================== Geolocation Functions ====================

/**
 * Get the user's current location using the browser's Geolocation API
 */
function getCurrentLocation() {
    const locationStatus = document.getElementById('locationStatus');
    const latitudeField = document.getElementById('latitude');
    const longitudeField = document.getElementById('longitude');
    const locationField = document.getElementById('location');

    // Check if geolocation is supported
    if (!navigator.geolocation) {
        Swal.fire({
            icon: 'error',
            title: 'Geolocation Not Supported',
            text: 'Geolocation is not supported by your browser. Please enter your location manually.',
            confirmButtonColor: '#ef4444'
        });
        return;
    }

    showLocationStatus('info', 'Getting your location...');

    navigator.geolocation.getCurrentPosition(
        // Success callback
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            // Update hidden fields
            latitudeField.value = lat;
            longitudeField.value = lng;

            // Try to get address from coordinates
            reverseGeocode(lat, lng).then(address => {
                if (address && !locationField.value) {
                    locationField.value = address;
                }
                showLocationStatus('success', `Location captured: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
            }).catch(() => {
                showLocationStatus('success', `Location captured: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
            });
        },
        // Error callback
        function(error) {
            let message = 'Unable to get your location.';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Location access denied. Please enable location services.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    message = 'Location request timed out.';
                    break;
            }
            showLocationStatus('error', message);
        },
        // Options
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * Show location status message using SweetAlert2
 */
function showLocationStatus(type, message) {
    const locationStatus = document.getElementById('locationStatus');
    if (locationStatus) {
        locationStatus.style.display = 'block';
        locationStatus.className = 'location-status ' + type;
        locationStatus.textContent = message;

        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                locationStatus.style.display = 'none';
            }, 5000);
        }
    }

    // Also show SweetAlert2 toast
    const toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });

    if (type === 'success') {
        toast.fire({
            icon: 'success',
            title: message
        });
    } else if (type === 'error') {
        toast.fire({
            icon: 'error',
            title: message
        });
    } else if (type === 'info') {
        toast.fire({
            icon: 'info',
            title: message
        });
    }
}

/**
 * Reverse geocode coordinates to get address
 * Note: This is a simplified version. In production, use a proper geocoding service.
 */
async function reverseGeocode(lat, lng) {
    try {
        // Using OpenStreetMap Nominatim API (free, no API key required)
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
            {
                headers: {
                    'Accept-Language': 'en'
                }
            }
        );

        if (response.ok) {
            const data = await response.json();
            return data.display_name;
        }
        return null;
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

// ==================== Image Preview ====================

/**
 * Preview selected image before upload
 */
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            previewImg.src = e.target.result;
            preview.style.display = 'inline-block';
        };

        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Remove selected image
 */
function removeImage() {
    const imageInput = document.getElementById('image');
    const preview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');

    imageInput.value = '';
    previewImg.src = '';
    preview.style.display = 'none';
}

// ==================== Form Enhancements ====================

/**
 * Auto-resize textareas based on content
 */
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');

    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Add smooth scroll behavior to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
});

// ==================== AJAX Form Submission (Optional Enhancement) ====================

/**
 * Submit form via AJAX for better UX
 * Can be enabled by adding data-ajax="true" to form elements
 */
document.addEventListener('DOMContentLoaded', function() {
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');

    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Submitting...';

            fetch(this.action, {
                method: this.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message with SweetAlert2
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: data.message,
                        confirmButtonColor: '#10b981',
                        timer: 2000,
                        timerProgressBar: true
                    }).then(() => {
                        // Redirect or reload
                        if (data.redirect) {
                            window.location.href = data.redirect;
                        }
                    });
                } else {
                    // Show error message with SweetAlert2
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: data.message || 'An error occurred.',
                        confirmButtonColor: '#ef4444'
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: 'An error occurred. Please try again.',
                    confirmButtonColor: '#ef4444'
                });
                console.error('Error:', error);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    });
});

/**
 * Show notification message using SweetAlert2
 */
function showNotification(type, message) {
    const toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });

    if (type === 'success') {
        toast.fire({
            icon: 'success',
            title: message
        });
    } else if (type === 'error') {
        toast.fire({
            icon: 'error',
            title: message
        });
    } else if (type === 'info') {
        toast.fire({
            icon: 'info',
            title: message
        });
    } else if (type === 'warning') {
        toast.fire({
            icon: 'warning',
            title: message
        });
    }
}

// ==================== Statistics Updates (Optional Polling) ====================

/**
 * Poll for updates on statistics (disabled by default)
 * Enable by adding data-poll-stats="true" to body element
 */
function startStatsPolling(interval = 30000) {
    const body = document.body;
    if (!body.hasAttribute('data-poll-stats')) {
        return;
    }

    setInterval(() => {
        fetch('/api/stats/')
            .then(response => response.json())
            .then(data => {
                // Update stat cards
                updateStatCard('.stat-primary h3', data.total_incidents);
                updateStatCard('.stat-success h3', data.resolved_count);
                updateStatCard('.stat-warning h3', data.pending_count);
                updateStatCard('.stat-danger h3', data.high_severity);
            })
            .catch(error => console.error('Stats polling error:', error));
    }, interval);
}

function updateStatCard(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = value;
        // Add a brief animation
        element.style.transition = 'transform 0.3s ease';
        element.style.transform = 'scale(1.2)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 300);
    }
}

// ==================== Copy to Clipboard ====================

/**
 * Copy text to clipboard with SweetAlert2 notification
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            const toast = Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true
            });
            toast.fire({
                icon: 'success',
                title: 'Copied to clipboard!'
            });
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        const toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
        });
        toast.fire({
            icon: 'success',
            title: 'Copied to clipboard!'
        });
    }
}

// ==================== Print Function ====================

/**
 * Print current page or specific element
 */
function printElement(elementId) {
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                <head><title>Print</title></head>
                <body>${element.innerHTML}</body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        }
    } else {
        window.print();
    }
}

// ==================== Utility Functions ====================

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format time ago
 */
function timeAgo(dateString) {
    const date = new Date(dateString);
    const seconds = Math.floor((new Date() - date) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }

    return 'Just now';
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize stats polling if enabled
    startStatsPolling();

    console.log('InfraGuard initialized successfully');
});
