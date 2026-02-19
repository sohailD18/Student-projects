/**
 * Intelligent Route Planner - Main Application JavaScript
 */

// Global state
const state = {
    map: null,
    originMarker: null,
    destinationMarker: null,
    routeLayers: [],
    currentRoutes: null,
    selectedRoute: null,
    originCoords: null,
    destinationCoords: null
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupEventListeners();
    loadDashboardStats();
    loadAnalytics();
});

/**
 * Initialize Leaflet Map
 */
function initializeMap() {
    // Create map centered on a default location
    state.map = L.map('map').setView([40.7128, -74.0060], 10);

    // Add OpenStreetMap tiles (no API key required)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(state.map);

    // Add click handler for selecting locations
    state.map.on('click', function(e) {
        handleMapClick(e.latlng);
    });
}

/**
 * Handle map clicks for location selection
 */
function handleMapClick(latlng) {
    if (!state.originCoords) {
        setOrigin(latlng.lat, latlng.lng, 'Selected Location');
    } else if (!state.destinationCoords) {
        setDestination(latlng.lat, latlng.lng, 'Selected Location');
    }
}

/**
 * Set origin location
 */
function setOrigin(lat, lng, name) {
    state.originCoords = { lat, lng, name };

    // Remove existing marker
    if (state.originMarker) {
        state.map.removeLayer(state.originMarker);
    }

    // Add marker
    const icon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background-color: #2563eb; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    state.originMarker = L.marker([lat, lng], { icon: icon })
        .addTo(state.map)
        .bindPopup(`<strong>Origin:</strong> ${name}`);

    document.getElementById('origin-lat').value = lat;
    document.getElementById('origin-lng').value = lng;
    document.getElementById('origin-name').value = name;
}

/**
 * Set destination location
 */
function setDestination(lat, lng, name) {
    state.destinationCoords = { lat, lng, name };

    // Remove existing marker
    if (state.destinationMarker) {
        state.map.removeLayer(state.destinationMarker);
    }

    // Add marker
    const icon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background-color: #ef4444; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    state.destinationMarker = L.marker([lat, lng], { icon: icon })
        .addTo(state.map)
        .bindPopup(`<strong>Destination:</strong> ${name}`);

    document.getElementById('destination-lat').value = lat;
    document.getElementById('destination-lng').value = lng;
    document.getElementById('destination-name').value = name;

    // Fit bounds to show both markers
    if (state.originMarker && state.destinationMarker) {
        const group = L.featureGroup([state.originMarker, state.destinationMarker]);
        state.map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Calculate routes button
    document.getElementById('calculate-btn').addEventListener('click', calculateRoutes);

    // Export report button
    document.getElementById('export-btn').addEventListener('click', exportReport);

    // Location name inputs
    document.getElementById('origin-name').addEventListener('change', function() {
        if (state.originCoords) {
            state.originCoords.name = this.value;
        }
    });

    document.getElementById('destination-name').addEventListener('change', function() {
        if (state.destinationCoords) {
            state.destinationCoords.name = this.value;
        }
    });
}

/**
 * Calculate routes between origin and destination
 */
async function calculateRoutes() {
    const originLat = parseFloat(document.getElementById('origin-lat').value);
    const originLng = parseFloat(document.getElementById('origin-lng').value);
    const originName = document.getElementById('origin-name').value || 'Origin';

    const destLat = parseFloat(document.getElementById('destination-lat').value);
    const destLng = parseFloat(document.getElementById('destination-lng').value);
    const destName = document.getElementById('destination-name').value || 'Destination';

    // Validate inputs
    if (!originLat || !originLng || !destLat || !destLng) {
        showToast('Please select both origin and destination locations on the map', 'error');
        return;
    }

    // Show loading state
    const button = document.getElementById('calculate-btn');
    button.disabled = true;
    button.textContent = 'Calculating Routes...';

    try {
        // Call API
        const response = await fetch('/api/calculate-routes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                origin_name: originName,
                origin_lat: originLat,
                origin_lng: originLng,
                destination_name: destName,
                destination_lat: destLat,
                destination_lng: destLng
            })
        });

        const data = await response.json();

        if (data.success) {
            state.currentRoutes = data.routes;
            state.originCoords = { lat: originLat, lng: originLng, name: originName };
            state.destinationCoords = { lat: destLat, lng: destLng, name: destName };

            displayRoutes(data.routes);
            showToast('Routes calculated successfully!', 'success');
        } else {
            showToast(data.message || 'Failed to calculate routes', 'error');
        }
    } catch (error) {
        console.error('Error calculating routes:', error);
        showToast('Error calculating routes. Please try again.', 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Calculate Routes';
    }
}

/**
 * Display routes on map and in list
 */
function displayRoutes(routes) {
    // Clear existing route layers
    clearRouteLayers();

    const container = document.getElementById('route-options');
    container.innerHTML = '';

    let recommendedRoute = null;

    // Display each route option
    for (const [routeType, routeData] of Object.entries(routes)) {
        if (routeType === 'metadata') continue;

        // Create route line on map
        const routeLine = L.polyline(routeData.coordinates, {
            color: routeData.color,
            weight: 5,
            opacity: 0.7
        }).addTo(state.map);

        routeLine.bindPopup(`
            <strong>${routeData.name}</strong><br>
            Distance: ${routeData.distance_km} km<br>
            Time: ${routeData.estimated_time_minutes} min<br>
            Cost: $${routeData.fuel_cost}
        `);

        state.routeLayers.push(routeLine);

        // Track recommended route
        if (routeData.is_recommended) {
            recommendedRoute = routeData;
        }

        // Create route card
        const card = createRouteCard(routeType, routeData);
        container.appendChild(card);
    }

    // Fit map to show all routes
    if (state.routeLayers.length > 0) {
        const group = L.featureGroup(state.routeLayers);
        state.map.fitBounds(group.getBounds().pad(0.1));
    }

    // Highlight recommended route
    if (recommendedRoute) {
        state.selectedRoute = recommendedRoute;
    }

    // Enable export button
    document.getElementById('export-btn').disabled = false;
}

/**
 * Create route card element
 */
function createRouteCard(routeType, routeData) {
    const card = document.createElement('div');
    card.className = `route-card route-${routeType}`;
    if (routeData.is_recommended) {
        card.classList.add('recommended', 'active');
    }

    card.innerHTML = `
        <div class="route-card-header">
            <div class="route-name">
                <span class="route-badge" style="background-color: ${routeData.color}">
                    ${routeData.name}
                </span>
            </div>
        </div>
        <p style="color: #6b7280; margin-top: 0.5rem;">${routeData.description}</p>
        <div class="route-stats">
            <div class="stat">
                <div class="stat-value">${routeData.distance_km}</div>
                <div class="stat-label">km</div>
            </div>
            <div class="stat">
                <div class="stat-value">${routeData.estimated_time_minutes}</div>
                <div class="stat-label">minutes</div>
            </div>
            <div class="stat">
                <div class="stat-value">$${routeData.fuel_cost}</div>
                <div class="stat-label">fuel cost</div>
            </div>
        </div>
    `;

    card.addEventListener('click', () => selectRoute(routeType, routeData));

    return card;
}

/**
 * Select a route
 */
function selectRoute(routeType, routeData) {
    state.selectedRoute = routeData;

    // Update active card
    document.querySelectorAll('.route-card').forEach(card => {
        card.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    // Highlight route on map
    state.routeLayers.forEach((layer, index) => {
        if (layer.options.color === routeData.color) {
            layer.setStyle({ weight: 7, opacity: 1 });
        } else {
            layer.setStyle({ weight: 5, opacity: 0.4 });
        }
    });

    showToast(`Selected: ${routeData.name}`, 'success');
}

/**
 * Clear all route layers from map
 */
function clearRouteLayers() {
    state.routeLayers.forEach(layer => {
        state.map.removeLayer(layer);
    });
    state.routeLayers = [];
}

/**
 * Export route report
 */
async function exportReport() {
    if (!state.currentRoutes || !state.selectedRoute) {
        showToast('Please calculate routes first', 'error');
        return;
    }

    try {
        const response = await fetch('/api/export-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                route_data: state.currentRoutes,
                origin: state.originCoords,
                destination: state.destinationCoords,
                selected_route: state.selectedRoute.type
            })
        });

        const data = await response.json();

        if (data.success) {
            // Download file
            const blob = new Blob([data.report], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            window.URL.revokeObjectURL(url);

            showToast('Report exported successfully!', 'success');
        }
    } catch (error) {
        console.error('Error exporting report:', error);
        showToast('Error exporting report', 'error');
    }
}

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard-stats/');
        const data = await response.json();

        if (data.success) {
            updateStatsCards(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Update stats cards
 */
function updateStatsCards(stats) {
    const statCards = [
        { id: 'stat-routes', value: stats.total_routes_calculated },
        { id: 'stat-score', value: stats.avg_optimization_score, suffix: '%' },
        { id: 'stat-distance', value: stats.total_distance_km, suffix: ' km' },
        { id: 'stat-fuel', value: stats.total_fuel_saved_liters, suffix: ' L' }
    ];

    statCards.forEach(stat => {
        const element = document.getElementById(stat.id);
        if (element) {
            element.textContent = stat.value + (stat.suffix || '');
        }
    });
}

/**
 * Load and display analytics charts
 */
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics/');
        const data = await response.json();

        if (data.success) {
            createHourlyTrafficChart(data.data.hourly_traffic);
            createWeeklyComparisonChart(data.data.weekly_comparison);
            createRouteDistributionChart(data.data.route_distribution);
            createEfficiencyTrendChart(data.data.efficiency_trend);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

/**
 * Create hourly traffic chart
 */
function createHourlyTrafficChart(data) {
    const ctx = document.getElementById('hourly-traffic-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.hour),
            datasets: [{
                label: 'Traffic Level',
                data: data.map(d => d.traffic_level),
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Traffic Level' }
                }
            }
        }
    });
}

/**
 * Create weekly comparison chart
 */
function createWeeklyComparisonChart(data) {
    const ctx = document.getElementById('weekly-comparison-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.day),
            datasets: [
                {
                    label: 'Avg Time (min)',
                    data: data.map(d => d.avg_time_minutes),
                    backgroundColor: '#2563eb'
                },
                {
                    label: 'Avg Distance (km)',
                    data: data.map(d => d.avg_distance_km),
                    backgroundColor: '#10b981'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Create route distribution chart
 */
function createRouteDistributionChart(data) {
    const ctx = document.getElementById('route-distribution-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.route_type),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => d.color)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

/**
 * Create efficiency trend chart
 */
function createEfficiencyTrendChart(data) {
    const ctx = document.getElementById('efficiency-trend-chart').getContext('2d');
    const last7Days = data.slice(-7);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days.map(d => d.date),
            datasets: [
                {
                    label: 'Optimization Score',
                    data: last7Days.map(d => d.optimization_score),
                    borderColor: '#2563eb',
                    yAxisID: 'y'
                },
                {
                    label: 'Time Saved (min)',
                    data: last7Days.map(d => d.time_saved_minutes),
                    borderColor: '#10b981',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Score' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Minutes' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
