/**
 * Dashboard JavaScript
 * Handles Chart.js visualizations, API calls, and interactivity
 */

// Global variables
let salesChart = null;
let statusChart = null;
let modalChart = null;
let productsData = [];
let currentProductId = null;

// Chart colors
const CHART_COLORS = {
    primary: 'rgb(52, 152, 219)',
    primaryTransparent: 'rgba(52, 152, 219, 0.2)',
    secondary: 'rgb(46, 204, 113)',
    secondaryTransparent: 'rgba(46, 204, 113, 0.2)',
    danger: 'rgb(231, 76, 60)',
    warning: 'rgb(243, 156, 18)',
    info: 'rgb(22, 160, 129)',
    gray: 'rgb(149, 165, 166)'
};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Initialize dashboard components
 */
async function initializeDashboard() {
    showLoading();

    try {
        // Load products list
        await loadProductsList();

        // Initialize status distribution chart
        await initializeStatusChart();

        // Load first product's chart data
        if (productsData.length > 0) {
            currentProductId = productsData[0].id;
            document.getElementById('productSelect').value = currentProductId;
            await updateProductChart();
        }

        updateLastUpdatedTime();
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showErrorMessage('Failed to load dashboard data. Please refresh the page.');
    } finally {
        hideLoading();
    }
}

/**
 * Load products list for dropdown
 */
async function loadProductsList() {
    try {
        const response = await fetch('/api/products/');
        const data = await response.json();

        if (data.success) {
            productsData = data.products;

            // Populate select dropdown
            const select = document.getElementById('productSelect');
            select.innerHTML = '<option value="">Select a product...</option>';

            productsData.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = `${product.name} (${product.category})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

/**
 * Initialize status distribution chart
 */
async function initializeStatusChart() {
    try {
        const response = await fetch('/api/inventory/summary/');
        const data = await response.json();

        if (data.success) {
            const statusCounts = data.summary.status_counts;

            const ctx = document.getElementById('statusChart').getContext('2d');

            statusChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Good', 'Low Stock', 'Critical', 'Over-stock'],
                    datasets: [{
                        data: [
                            statusCounts.good || 0,
                            statusCounts.low || 0,
                            statusCounts.critical || 0,
                            statusCounts.overstock || 0
                        ],
                        backgroundColor: [
                            CHART_COLORS.secondary,
                            CHART_COLORS.danger,
                            '#c0392b',
                            CHART_COLORS.warning
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true
                            }
                        },
                        title: {
                            display: false
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading status chart:', error);
    }
}

/**
 * Update product sales vs forecast chart
 */
async function updateProductChart() {
    const productId = document.getElementById('productSelect').value;

    if (!productId) {
        if (salesChart) {
            salesChart.destroy();
            salesChart = null;
        }
        return;
    }

    showLoading();

    try {
        const response = await fetch(`/api/chart/${productId}/`);
        const data = await response.json();

        if (data.success) {
            renderSalesChart(data);
            currentProductId = productId;
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        showErrorMessage('Failed to load chart data');
    } finally {
        hideLoading();
    }
}

/**
 * Render sales vs forecast chart
 */
function renderSalesChart(data) {
    const ctx = document.getElementById('salesChart').getContext('2d');

    // Destroy existing chart if it exists
    if (salesChart) {
        salesChart.destroy();
    }

    // Prepare data
    const historicalLabels = data.historical.labels;
    const historicalValues = data.historical.values;

    const forecastLabels = data.forecast.daily_forecast.map(d => d.date);
    const forecastValues = data.forecast.daily_forecast.map(d => d.predicted_quantity);

    // Combine data for continuous display
    const allLabels = [...historicalLabels.slice(-30), ...forecastLabels];
    const allHistorical = [...historicalValues.slice(-30), ...Array(forecastValues.length).fill(null)];
    const allForecast = [...Array(historicalValues.slice(-30).length).fill(null), ...forecastValues];

    salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Actual Sales',
                    data: allHistorical,
                    borderColor: CHART_COLORS.primary,
                    backgroundColor: CHART_COLORS.primaryTransparent,
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    fill: true
                },
                {
                    label: 'AI Forecast',
                    data: allForecast,
                    borderColor: CHART_COLORS.secondary,
                    backgroundColor: CHART_COLORS.secondaryTransparent,
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        title: function(context) {
                            return 'Date: ' + context[0].label;
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y) + ' units';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        maxTicksLimit: 10,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Quantity',
                        font: {
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return Math.round(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * View product details in modal
 */
async function viewProductDetails(productId) {
    showLoading();

    try {
        const response = await fetch(`/api/forecast/${productId}/`);
        const data = await response.json();

        if (data.success) {
            const chartResponse = await fetch(`/api/chart/${productId}/`);
            const chartData = await chartResponse.json();

            if (chartData.success) {
                showProductModal(data.forecast, chartData);
            }
        }
    } catch (error) {
        console.error('Error loading product details:', error);
        showErrorMessage('Failed to load product details');
    } finally {
        hideLoading();
    }
}

/**
 * Show product details modal
 */
function showProductModal(forecast, chartData) {
    const modal = document.getElementById('productModal');
    const productName = document.getElementById('modalProductName');
    const modalInfo = document.getElementById('modalInfo');

    productName.textContent = forecast.product_name;

    // Update modal info
    modalInfo.innerHTML = `
        <div class="info-item">
            <div class="info-label">Current Stock</div>
            <div class="info-value">${forecast.current_stock}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Predicted Demand (30 days)</div>
            <div class="info-value">${forecast.total_predicted_demand}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Average Daily Demand</div>
            <div class="info-value">${forecast.average_daily_demand}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Safety Stock</div>
            <div class="info-value">${forecast.safety_stock}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Status</div>
            <div class="info-value">${forecast.status_display}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Suggested Order Quantity</div>
            <div class="info-value">${forecast.suggested_order_quantity}</div>
        </div>
    `;

    // Render modal chart
    renderModalChart(chartData);

    // Show modal
    modal.classList.add('active');
}

/**
 * Render modal chart
 */
function renderModalChart(data) {
    const ctx = document.getElementById('modalChart').getContext('2d');

    // Destroy existing chart
    if (modalChart) {
        modalChart.destroy();
    }

    const historicalLabels = data.historical.labels;
    const historicalValues = data.historical.values;
    const forecastLabels = data.forecast.daily_forecast.map(d => d.date);
    const forecastValues = data.forecast.daily_forecast.map(d => d.predicted_quantity);

    modalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...historicalLabels.slice(-60), ...forecastLabels],
            datasets: [
                {
                    label: 'Actual Sales',
                    data: [...historicalValues.slice(-60), ...Array(forecastValues.length).fill(null)],
                    borderColor: CHART_COLORS.primary,
                    backgroundColor: CHART_COLORS.primaryTransparent,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'AI Forecast',
                    data: [...Array(historicalValues.slice(-60).length).fill(null), ...forecastValues],
                    borderColor: CHART_COLORS.secondary,
                    backgroundColor: CHART_COLORS.secondaryTransparent,
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
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
 * Close modal
 */
function closeModal() {
    const modal = document.getElementById('productModal');
    modal.classList.remove('active');
}

/**
 * Filter table by search and status
 */
function filterTable() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const table = document.getElementById('inventoryTable');
    const rows = table.getElementsByTagName('tr');

    // Skip header row
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const productName = row.getElementsByTagName('td')[0].textContent.toLowerCase();
        const status = row.getAttribute('data-status');

        const matchesSearch = productName.includes(searchInput);
        const matchesStatus = !statusFilter || status === statusFilter;

        if (matchesSearch && matchesStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

/**
 * Refresh dashboard data
 */
async function refreshDashboard() {
    showLoading();

    try {
        // Reload all charts and data
        await initializeDashboard();
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        showErrorMessage('Failed to refresh dashboard');
    } finally {
        hideLoading();
    }
}

/**
 * Update last updated time
 */
function updateLastUpdatedTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('lastUpdated').textContent = 'Updated: ' + timeString;
}

/**
 * Show loading overlay
 */
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    alert(message); // Simple alert for now, could be replaced with a toast notification
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('productModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // ESC to close modal
    if (event.key === 'Escape') {
        closeModal();
    }

    // Ctrl+R or F5 to refresh
    if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
        event.preventDefault();
        refreshDashboard();
    }
});
