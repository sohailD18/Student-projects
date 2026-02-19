// ============================================
// DASHBOARD CHARTS AND DATA LOADING
// ============================================

let sentimentChart = null;
let ratingChart = null;

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// ============================================
// LOAD DASHBOARD DATA
// ============================================
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data/');
        const data = await response.json();

        if (response.ok) {
            updateStatsCards(data);
            updateSentimentChart(data.sentiment_counts);
            updateRatingChart(data.rating_distribution);
            updateReviewsList(data.recent_reviews);
        } else {
            console.error('Error loading dashboard data:', data);
        }
    } catch (error) {
        console.error('Network error:', error);
        showErrorState();
    }
}

// ============================================
// UPDATE STATS CARDS
// ============================================
function updateStatsCards(data) {
    document.getElementById('totalReviews').textContent = data.total_reviews;
    document.getElementById('avgRating').textContent = data.average_rating + ' ★';
    document.getElementById('positiveCount').textContent = data.sentiment_counts.positive;
    document.getElementById('neutralCount').textContent = data.sentiment_counts.neutral;
    document.getElementById('negativeCount').textContent = data.sentiment_counts.negative;
}

// ============================================
// UPDATE SENTIMENT PIE CHART
// ============================================
function updateSentimentChart(sentimentCounts) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');

    // Destroy existing chart if it exists
    if (sentimentChart) {
        sentimentChart.destroy();
    }

    const total = sentimentCounts.positive + sentimentCounts.neutral + sentimentCounts.negative;

    // If no data, show empty state
    if (total === 0) {
        ctx.fillStyle = '#9ca3af';
        ctx.font = '16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No reviews yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [sentimentCounts.positive, sentimentCounts.neutral, sentimentCounts.negative],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',   // Green for positive
                    'rgba(245, 158, 11, 0.8)',   // Yellow for neutral
                    'rgba(239, 68, 68, 0.8)'     // Red for negative
                ],
                borderColor: [
                    'rgb(16, 185, 129)',
                    'rgb(245, 158, 11)',
                    'rgb(239, 68, 68)'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14,
                            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.95)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%',
            animation: {
                animateRotate: true,
                animateScale: true
            }
        }
    });
}

// ============================================
// UPDATE RATING BAR CHART
// ============================================
function updateRatingChart(ratingDistribution) {
    const ctx = document.getElementById('ratingChart').getContext('2d');

    // Destroy existing chart if it exists
    if (ratingChart) {
        ratingChart.destroy();
    }

    const labels = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'];
    const data = [
        ratingDistribution['1'] || 0,
        ratingDistribution['2'] || 0,
        ratingDistribution['3'] || 0,
        ratingDistribution['4'] || 0,
        ratingDistribution['5'] || 0
    ];

    const maxCount = Math.max(...data, 1);

    ratingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Reviews',
                data: data,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',   // Red for 1 star
                    'rgba(245, 158, 11, 0.8)',  // Orange for 2 stars
                    'rgba(251, 191, 36, 0.8)',  // Yellow for 3 stars
                    'rgba(132, 204, 22, 0.8)',  // Light green for 4 stars
                    'rgba(16, 185, 129, 0.8)'   // Green for 5 stars
                ],
                borderColor: [
                    'rgb(239, 68, 68)',
                    'rgb(245, 158, 11)',
                    'rgb(251, 191, 36)',
                    'rgb(132, 204, 22)',
                    'rgb(16, 185, 129)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.95)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return `${context.raw} review${context.raw !== 1 ? 's' : ''}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: Math.ceil(maxCount * 1.2),
                    ticks: {
                        stepSize: Math.max(1, Math.floor(maxCount / 5)),
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(209, 213, 219, 0.5)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ============================================
// UPDATE REVIEWS LIST
// ============================================
function updateReviewsList(reviews) {
    const reviewsList = document.getElementById('reviewsList');
    const reviewCount = document.getElementById('reviewCount');

    reviewCount.textContent = `${reviews.length} review${reviews.length !== 1 ? 's' : ''}`;

    if (reviews.length === 0) {
        reviewsList.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <p>No reviews yet. Submit your first review to get started!</p>
            </div>
        `;
        return;
    }

    const reviewsHTML = reviews.map(review => createReviewItem(review)).join('');
    reviewsList.innerHTML = reviewsHTML;
}

// ============================================
// CREATE REVIEW ITEM HTML
// ============================================
function createReviewItem(review) {
    const date = new Date(review.created_at);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    const sentimentLabels = {
        positive: 'Positive',
        neutral: 'Neutral',
        negative: 'Negative'
    };

    const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);

    return `
        <div class="review-item ${review.sentiment}">
            <div class="review-header">
                <span class="review-product">${escapeHtml(review.product_name)}</span>
                <span class="review-rating">${stars}</span>
            </div>
            <p class="review-text">${escapeHtml(review.review_text)}</p>
            <div class="review-meta">
                <span class="badge badge-${review.sentiment}">${sentimentLabels[review.sentiment]}</span>
                <span class="review-date">${formattedDate}</span>
            </div>
        </div>
    `;
}

// ============================================
// REFRESH DASHBOARD
// ============================================
function refreshDashboard() {
    loadDashboardData();
}

// ============================================
// ERROR STATE
// ============================================
function showErrorState() {
    const reviewsList = document.getElementById('reviewsList');
    reviewsList.innerHTML = `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>Error loading data. Please try again.</p>
        </div>
    `;
}

// ============================================
// UTILITY: ESCAPE HTML
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
