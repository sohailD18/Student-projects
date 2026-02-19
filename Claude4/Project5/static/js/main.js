/**
 * AI Trip Planner - Main JavaScript File
 * Final Year BCA Project
 */

(function() {
    'use strict';

    // ============================
    // Application State
    // ============================
    const App = {
        version: '1.0.0',
        map: null,
        routes: [],
        currentRoute: null
    };

    // ============================
    // Utility Functions
    // ============================

    /**
     * Debounce function to limit execution rate
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
     * Format time in hours and minutes
     */
    function formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);

        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins} mins`;
    }

    /**
     * Format distance with appropriate units
     */
    function formatDistance(km) {
        if (km >= 100) {
            return `${km.toFixed(1)} km`;
        } else if (km >= 10) {
            return `${km.toFixed(1)} km`;
        } else {
            return `${km.toFixed(2)} km`;
        }
    }

    /**
     * Show toast notification
     */
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') ||
            createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Create toast container if it doesn't exist
     */
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }

    // ============================
    // Location Search
    // ============================

    /**
     * Initialize location search functionality
     */
    function initLocationSearch() {
        const searchInputs = document.querySelectorAll('[data-search-locations]');

        searchInputs.forEach(input => {
            let searchTimeout;

            input.addEventListener('input', debounce(function(e) {
                const query = e.target.value.trim();

                if (query.length < 2) {
                    hideSuggestions(input);
                    return;
                }

                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    searchLocations(query, input);
                }, 300);
            }, 300));

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !input.nextElementSibling?.contains(e.target)) {
                    hideSuggestions(input);
                }
            });
        });
    }

    /**
     * Search for locations via API
     */
    async function searchLocations(query, inputElement) {
        try {
            const response = await fetch(`/api/search-locations/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.locations && data.locations.length > 0) {
                showSuggestions(inputElement, data.locations);
            } else {
                hideSuggestions(inputElement);
            }
        } catch (error) {
            console.error('Location search error:', error);
        }
    }

    /**
     * Show location suggestions dropdown
     */
    function showSuggestions(inputElement, locations) {
        hideSuggestions(inputElement);

        const dropdown = document.createElement('div');
        dropdown.className = 'suggestions-dropdown list-group position-absolute';
        dropdown.style.zIndex = '1000';
        dropdown.style.maxHeight = '200px';
        dropdown.style.overflowY = 'auto';
        dropdown.style.width = inputElement.offsetWidth + 'px';

        locations.forEach(loc => {
            const item = document.createElement('button');
            item.className = 'list-group-item list-group-item-action';
            item.textContent = loc.full_address;
            item.addEventListener('click', () => {
                inputElement.value = loc.full_address;
                inputElement.dataset.locationId = loc.id;
                hideSuggestions(inputElement);
            });
            dropdown.appendChild(item);
        });

        inputElement.parentNode.style.position = 'relative';
        inputElement.parentNode.appendChild(dropdown);
    }

    /**
     * Hide location suggestions
     */
    function hideSuggestions(inputElement) {
        const dropdown = inputElement.parentNode.querySelector('.suggestions-dropdown');
        if (dropdown) {
            dropdown.remove();
        }
    }

    // ============================
    // Map Functions
    // ============================

    /**
     * Initialize Leaflet map
     */
    function initMap(elementId, center, zoom = 7) {
        if (typeof L === 'undefined') {
            console.error('Leaflet library not loaded');
            return null;
        }

        const map = L.map(elementId).setView([center.lat, center.lng], zoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(map);

        return map;
    }

    /**
     * Add marker to map
     */
    function addMarker(map, lat, lng, title, icon = null) {
        const options = {
            title: title
        };

        if (icon) {
            options.icon = icon;
        }

        return L.marker([lat, lng], options).addTo(map);
    }

    /**
     * Draw route polyline on map
     */
    function drawRoute(map, coordinates, color = '#0d6efd', weight = 4) {
        return L.polyline(coordinates, {
            color: color,
            weight: weight,
            opacity: 0.8
        }).addTo(map);
    }

    // ============================
    // Form Validation
    // ============================

    /**
     * Initialize form validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('[data-validate]');

        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!this.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    showToast('Please fill in all required fields correctly', 'danger');
                }

                this.classList.add('was-validated');
            });
        });
    }

    // ============================
    // Loading States
    // ============================

    /**
     * Show loading state on button
     */
    function showLoading(button, originalText) {
        button.disabled = true;
        button.dataset.originalText = originalText;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Loading...
        `;
    }

    /**
     * Hide loading state on button
     */
    function hideLoading(button) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.textContent;
    }

    // ============================
    // Analytics (Optional)
    // ============================

    /**
     * Track user interaction (for improvement)
     */
    function trackEvent(action, category = 'user_interaction') {
        console.log(`Event: ${category} - ${action}`);
        // This can be extended with actual analytics
    }

    // ============================
    // Initialize Application
    // ============================

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize features based on current page
        initLocationSearch();
        initFormValidation();

        // Track page view
        trackEvent('page_load', 'navigation');

        console.log('AI Trip Planner initialized successfully');
    });

    // ============================
    // Export Public API
    // ============================

    window.AI_Trip_Planner = {
        formatTime,
        formatDistance,
        showToast,
        initMap,
        addMarker,
        drawRoute,
        showLoading,
        hideLoading,
        trackEvent
    };

})();
