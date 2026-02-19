/**
 * AI-Powered Market Trend Analysis Dashboard
 * Frontend JavaScript for API interaction and chart rendering
 */

// ============ Global State ============
let currentStockId = null;
let charts = {};

// ============ DOM Elements ============
const elements = {
    stockSelect: document.getElementById('stockSelect'),
    addStockBtn: document.getElementById('addStockBtn'),
    addStockForm: document.getElementById('addStockForm'),
    newStockSymbol: document.getElementById('newStockSymbol'),
    fetchDataBtn: document.getElementById('fetchDataBtn'),
    cancelAddBtn: document.getElementById('cancelAddBtn'),
    dashboardContent: document.getElementById('dashboardContent'),
    stockSymbol: document.getElementById('stockSymbol'),
    stockName: document.getElementById('stockName'),
    currentPrice: document.getElementById('currentPrice'),
    priceChange: document.getElementById('priceChange'),
    trainPredictBtn: document.getElementById('trainPredictBtn'),
    analyzeVolatilityBtn: document.getElementById('analyzeVolatilityBtn'),
    generateReportBtn: document.getElementById('generateReportBtn'),
    modelSelect: document.getElementById('modelSelect'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    notification: document.getElementById('notification')
};

// ============ Utility Functions ============

/**
 * Show loading overlay
 */
function showLoading(text = 'Processing...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.classList.remove('hidden');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    elements.loadingOverlay.classList.add('hidden');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    elements.notification.textContent = message;
    elements.notification.className = `notification ${type}`;
    elements.notification.classList.remove('hidden');

    setTimeout(() => {
        elements.notification.classList.add('hidden');
    }, 5000);
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}

// ============ API Functions ============

/**
 * Fetch stock data from API
 */
async function fetchStockData(symbol) {
    try {
        showLoading('Fetching stock data...');

        const response = await fetch('/api/fetch-data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');

            // Refresh stock list
            await loadStocks();

            // Select the newly added stock
            elements.stockSelect.value = data.stock_id;
            await handleStockChange();

            // Hide form
            elements.addStockForm.classList.add('hidden');
            elements.newStockSymbol.value = '';
        } else {
            showNotification(data.error || 'Failed to fetch data', 'error');
        }
    } catch (error) {
        console.error('Error fetching stock data:', error);
        showNotification('Error fetching stock data', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load stocks list
 */
async function loadStocks() {
    try {
        const response = await fetch('/api/stocks/');
        const data = await response.json();

        if (data.success) {
            // Clear existing options
            elements.stockSelect.innerHTML = '<option value="">-- Select a Stock --</option>';

            // Add stock options
            data.stocks.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.id;
                option.textContent = `${stock.symbol} - ${stock.company_name || 'N/A'}`;
                elements.stockSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading stocks:', error);
    }
}

/**
 * Handle stock selection change
 */
async function handleStockChange() {
    const stockId = elements.stockSelect.value;

    if (!stockId) {
        elements.dashboardContent.classList.add('hidden');
        currentStockId = null;
        return;
    }

    currentStockId = parseInt(stockId);
    await loadDashboardData();
}

/**
 * Load dashboard data for selected stock
 */
async function loadDashboardData() {
    try {
        showLoading('Loading dashboard data...');

        const response = await fetch(`/api/dashboard/${currentStockId}/`);
        const data = await response.json();

        if (data.success) {
            updateStockInfo(data.stock);
            renderCharts(data.chart_data);
            updatePredictionMetrics(data.prediction);
            updatePredictionChart(data.chart_data, data.prediction);
            updateVolatilityMetrics(data.volatility);

            elements.dashboardContent.classList.remove('hidden');
        } else {
            showNotification(data.error || 'Failed to load dashboard data', 'error');
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Update stock information display
 */
function updateStockInfo(stock) {
    elements.stockSymbol.textContent = stock.symbol;
    elements.stockName.textContent = stock.company_name || 'N/A';
    elements.currentPrice.textContent = formatCurrency(stock.latest_price || 0);
}

/**
 * Train model and generate prediction
 */
async function trainAndPredict() {
    if (!currentStockId) {
        showNotification('Please select a stock first', 'warning');
        return;
    }

    try {
        showLoading('Training model and generating prediction...');

        const modelType = elements.modelSelect.value;
        const response = await fetch('/api/train-predict/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_id: currentStockId,
                model_type: modelType
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Prediction generated successfully!', 'success');
            updatePredictionMetrics(data.prediction);

            // Fetch chart data and update prediction chart
            const dashboardResponse = await fetch(`/api/dashboard/${currentStockId}/`);
            const dashboardData = await dashboardResponse.json();

            if (dashboardData.success) {
                updatePredictionChart(dashboardData.chart_data, data.prediction);
            }
        } else {
            showNotification(data.error || 'Failed to generate prediction', 'error');
        }
    } catch (error) {
        console.error('Error training model:', error);
        showNotification('Error training model', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Analyze volatility
 */
async function analyzeVolatility() {
    if (!currentStockId) {
        showNotification('Please select a stock first', 'warning');
        return;
    }

    try {
        showLoading('Analyzing volatility and risk...');

        const response = await fetch('/api/analyze-volatility/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_id: currentStockId,
                period_days: 30
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Volatility analysis complete!', 'success');
            updateVolatilityMetrics(data.analysis);
        } else {
            showNotification(data.error || 'Failed to analyze volatility', 'error');
        }
    } catch (error) {
        console.error('Error analyzing volatility:', error);
        showNotification('Error analyzing volatility', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Generate market report
 */
async function generateReport() {
    if (!currentStockId) {
        showNotification('Please select a stock first', 'warning');
        return;
    }

    try {
        showLoading('Generating market analysis report...');

        const response = await fetch('/api/generate-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_id: currentStockId
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Report generated successfully!', 'success');
            displayReport(data.report);
        } else {
            showNotification(data.error || 'Failed to generate report', 'error');
        }
    } catch (error) {
        console.error('Error generating report:', error);
        showNotification('Error generating report', 'error');
    } finally {
        hideLoading();
    }
}

// ============ Chart Functions ============

/**
 * Render all charts
 */
function renderCharts(chartData) {
    if (!chartData || chartData.length === 0) return;

    const dates = chartData.map(d => d.date);
    const prices = chartData.map(d => d.close);
    const volumes = chartData.map(d => d.volume);
    const ma5 = chartData.map(d => d.ma_5);
    const ma20 = chartData.map(d => d.ma_20);

    // Destroy existing charts
    Object.values(charts).forEach(chart => chart?.destroy());

    // Price Chart
    renderPriceChart(dates, prices, ma5, ma20);

    // Volume Chart
    renderVolumeChart(dates, volumes);

    // Volatility Chart (dummy data for now)
    renderVolatilityChart(dates, prices);
}

/**
 * Render price chart
 */
function renderPriceChart(dates, prices, ma5, ma20) {
    const ctx = document.getElementById('priceChart').getContext('2d');

    charts.price = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Close Price',
                    data: prices,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'MA 5',
                    data: ma5,
                    borderColor: '#8b5cf6',
                    borderWidth: 1.5,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    hidden: ma5.every(v => v === null)
                },
                {
                    label: 'MA 20',
                    data: ma20,
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    hidden: ma20.every(v => v === null)
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#6b7280', maxTicksLimit: 10 },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                }
            }
        }
    });
}

/**
 * Render volume chart
 */
function renderVolumeChart(dates, volumes) {
    const ctx = document.getElementById('volumeChart').getContext('2d');

    charts.volume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Volume',
                data: volumes,
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: '#3b82f6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#6b7280', maxTicksLimit: 10 },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                }
            }
        }
    });
}

/**
 * Render volatility chart
 */
function renderVolatilityChart(dates, prices) {
    const ctx = document.getElementById('volatilityChart').getContext('2d');

    // Calculate rolling volatility
    const volatility = [];
    const window = 10;

    for (let i = 0; i < prices.length; i++) {
        if (i < window - 1) {
            volatility.push(null);
        } else {
            const slice = prices.slice(i - window + 1, i + 1);
            const mean = slice.reduce((a, b) => a + b, 0) / window;
            const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / window;
            volatility.push(Math.sqrt(variance));
        }
    }

    charts.volatility = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Volatility (10-day)',
                data: volatility,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#6b7280', maxTicksLimit: 10 },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                }
            }
        }
    });
}

/**
 * Render prediction chart (empty placeholder)
 */
function renderPredictionChart() {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    charts.prediction = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                },
                title: {
                    display: true,
                    text: 'Run prediction to see results',
                    color: '#6b7280'
                }
            },
            scales: {
                x: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                }
            }
        }
    });
}

// ============ Update Functions ============

/**
 * Update prediction metrics display
 */
function updatePredictionMetrics(prediction) {
    const container = document.getElementById('predictionMetrics');

    if (!prediction) {
        container.innerHTML = '<p class="no-data">Train model to see metrics</p>';
        updateSignal(null);
        return;
    }

    container.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">Predicted Price</span>
            <span class="metric-value">${formatCurrency(prediction.predicted_price)}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Model Type</span>
            <span class="metric-value">${prediction.model_type}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">R² Score</span>
            <span class="metric-value">${prediction.r2_score?.toFixed(4) || 'N/A'}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">RMSE</span>
            <span class="metric-value">${prediction.rmse?.toFixed(4) || 'N/A'}</span>
        </div>
    `;

    updateSignal(prediction);

    // Update accuracy metrics
    const accuracyContainer = document.getElementById('accuracyMetrics');
    accuracyContainer.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">R² Score</span>
            <span class="metric-value">${prediction.r2_score?.toFixed(4) || 'N/A'}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">RMSE</span>
            <span class="metric-value">${prediction.rmse?.toFixed(4) || 'N/A'}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">MAE</span>
            <span class="metric-value">${prediction.mae?.toFixed(4) || 'N/A'}</span>
        </div>
    `;
}

/**
 * Update signal display
 */
function updateSignal(prediction) {
    const container = document.getElementById('signalContent');

    if (!prediction || !prediction.signal) {
        container.innerHTML = '<span class="no-signal">No signal generated</span>';
        return;
    }

    const signalClass = prediction.signal.toLowerCase();
    container.innerHTML = `
        <div class="signal ${signalClass}">${prediction.signal}</div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${prediction.confidence || 0}%"></div>
        </div>
        <div class="confidence-text">Confidence: ${prediction.confidence?.toFixed(1) || 0}%</div>
    `;
}

/**
 * Update prediction chart with actual vs predicted prices
 */
function updatePredictionChart(chartData, prediction) {
    if (!chartData || chartData.length === 0) return;

    const ctx = document.getElementById('predictionChart').getContext('2d');

    // Destroy existing prediction chart if it exists
    if (charts.prediction) {
        charts.prediction.destroy();
    }

    // Take last 30 data points for clearer visualization
    const recentData = chartData.slice(-30);
    const dates = recentData.map(d => d.date);
    const actualPrices = recentData.map(d => d.close);

    // Create datasets
    const datasets = [
        {
            label: 'Actual Price',
            data: actualPrices,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 2
        }
    ];

    // Add prediction line if available
    let titleText = 'Train & Predict to see predictions';
    if (prediction && prediction.predicted_price) {
        const predictedPrices = [...actualPrices.slice(0, -1), prediction.predicted_price];
        datasets.push({
            label: 'Predicted Price',
            data: predictedPrices,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
            pointRadius: 2
        });
        titleText = `Predicted: ${formatCurrency(prediction.predicted_price)} (${prediction.signal || 'HOLD'})`;
    }

    charts.prediction = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                },
                title: {
                    display: true,
                    text: titleText,
                    color: '#9ca3af',
                    font: { size: 14 }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#374151' }
                }
            }
        }
    });
}

/**
 * Update volatility metrics display
 */
function updateVolatilityMetrics(volatility) {
    const container = document.getElementById('volatilityMetrics');

    if (!volatility) {
        container.innerHTML = '<p class="no-data">Analyze volatility to see metrics</p>';
        return;
    }

    const riskClass = volatility.risk_level?.toLowerCase() || 'medium';

    container.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">Risk Level</span>
            <span class="metric-value" style="color: ${getRiskColor(volatility.risk_level)}">${volatility.risk_level}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Daily Volatility</span>
            <span class="metric-value">${(volatility.daily_volatility * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Annualized Volatility</span>
            <span class="metric-value">${(volatility.annualized_volatility * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">VaR (95%)</span>
            <span class="metric-value">${(volatility.var_95 * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Sharpe Ratio</span>
            <span class="metric-value">${volatility.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
        </div>
    `;
}

/**
 * Get risk level color
 */
function getRiskColor(riskLevel) {
    const colors = {
        'Low': '#10b981',
        'Medium': '#f59e0b',
        'High': '#ef4444',
        'Very High': '#dc2626'
    };
    return colors[riskLevel] || '#9ca3af';
}

/**
 * Display market report
 */
function displayReport(report) {
    const container = document.getElementById('reportContent');

    const trendClass = report.trend?.toLowerCase() || 'sideways';

    container.innerHTML = `
        <h4>Summary</h4>
        <p>${report.summary || 'No summary available'}</p>

        <h4>Market Trend <span class="trend-badge ${trendClass}">${report.trend || 'N/A'}</span></h4>

        <h4>Key Findings</h4>
        <ul>
            ${(report.key_findings || []).map(finding => `<li>${finding}</li>`).join('')}
        </ul>

        <h4>Recommendation</h4>
        <p>${report.recommendation || 'No recommendation available'}</p>
    `;
}

// ============ Event Listeners ============

document.addEventListener('DOMContentLoaded', () => {
    // Stock selection
    elements.stockSelect.addEventListener('change', handleStockChange);

    // Add stock form
    elements.addStockBtn.addEventListener('click', () => {
        elements.addStockForm.classList.toggle('hidden');
    });

    elements.cancelAddBtn.addEventListener('click', () => {
        elements.addStockForm.classList.add('hidden');
        elements.newStockSymbol.value = '';
    });

    elements.fetchDataBtn.addEventListener('click', () => {
        const symbol = elements.newStockSymbol.value.trim();
        if (symbol) {
            fetchStockData(symbol);
        } else {
            showNotification('Please enter a stock symbol', 'warning');
        }
    });

    // Action buttons
    elements.trainPredictBtn.addEventListener('click', trainAndPredict);
    elements.analyzeVolatilityBtn.addEventListener('click', analyzeVolatility);
    elements.generateReportBtn.addEventListener('click', generateReport);

    // Initialize empty prediction chart
    renderPredictionChart();
});

// Allow Enter key to submit stock symbol
elements.newStockSymbol?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const symbol = elements.newStockSymbol.value.trim();
        if (symbol) {
            fetchStockData(symbol);
        }
    }
});
