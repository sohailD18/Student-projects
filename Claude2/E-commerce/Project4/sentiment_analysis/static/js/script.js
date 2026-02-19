// ============================================
// REVIEW FORM SUBMISSION AND INTERACTIONS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initRatingInput();
    initCharacterCount();
    initReviewForm();
});

// ============================================
// RATING INPUT HANDLER
// ============================================
function initRatingInput() {
    const ratingInput = document.getElementById('ratingInput');
    const ratingField = document.getElementById('rating');
    const stars = ratingInput.querySelectorAll('.star');
    const ratingLabel = document.getElementById('ratingLabel');

    const ratingTexts = {
        1: 'Poor - Needs significant improvement',
        2: 'Fair - Below expectations',
        3: 'Good - Meets expectations',
        4: 'Very Good - Exceeds expectations',
        5: 'Excellent - Outstanding!'
    };

    stars.forEach(star => {
        // Handle click
        star.addEventListener('click', function() {
            const rating = this.getAttribute('data-rating');
            ratingField.value = rating;
            updateStars(rating);
            ratingLabel.textContent = ratingTexts[rating];
            ratingLabel.style.color = '#f59e0b';
        });

        // Handle hover
        star.addEventListener('mouseenter', function() {
            const rating = this.getAttribute('data-rating');
            highlightStars(rating);
        });

        star.addEventListener('mouseleave', function() {
            const currentRating = ratingField.value;
            if (currentRating) {
                highlightStars(currentRating);
            } else {
                resetStars();
            }
        });
    });

    function updateStars(rating) {
        stars.forEach(star => {
            const starRating = star.getAttribute('data-rating');
            if (starRating <= rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    function highlightStars(rating) {
        stars.forEach(star => {
            const starRating = star.getAttribute('data-rating');
            if (starRating <= rating) {
                star.style.color = '#f59e0b';
            } else {
                star.style.color = '#d1d5db';
            }
        });
    }

    function resetStars() {
        stars.forEach(star => {
            star.style.color = '#d1d5db';
        });
        ratingLabel.textContent = 'Select a rating';
        ratingLabel.style.color = '#6b7280';
    }
}

// ============================================
// CHARACTER COUNT FOR TEXTAREA
// ============================================
function initCharacterCount() {
    const reviewText = document.getElementById('review_text');
    const charCount = document.getElementById('charCount');
    const maxLength = 1000;

    reviewText.addEventListener('input', function() {
        const currentLength = this.value.length;
        charCount.textContent = `${currentLength} / ${maxLength}`;

        if (currentLength > maxLength * 0.9) {
            charCount.style.color = '#ef4444';
        } else if (currentLength > maxLength * 0.7) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#9ca3af';
        }

        if (currentLength >= maxLength) {
            charCount.textContent = `${maxLength} / ${maxLength} (Maximum reached)`;
        }
    });
}

// ============================================
// FORM SUBMISSION
// ============================================
function initReviewForm() {
    const form = document.getElementById('reviewForm');
    const submitBtn = document.getElementById('submitBtn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate rating
        const rating = document.getElementById('rating').value;
        if (!rating) {
            showErrorModal('Please select a rating before submitting.');
            return;
        }

        // Get form data
        const formData = {
            product_name: document.getElementById('product_name').value,
            review_text: document.getElementById('review_text').value,
            rating: parseInt(rating)
        };

        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/submit-review/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showSuccessMessage(data.review);
            } else {
                showErrorModal(data.error || 'An error occurred while submitting your review.');
            }
        } catch (error) {
            showErrorModal('Network error. Please check your connection and try again.');
            console.error('Error:', error);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });
}

// ============================================
// SUCCESS MESSAGE
// ============================================
function showSuccessMessage(review) {
    const form = document.querySelector('.review-form');
    const successMessage = document.getElementById('successMessage');
    const successDetails = document.getElementById('successDetails');

    form.style.display = 'none';
    successMessage.style.display = 'block';

    const sentimentLabels = {
        positive: '😊 Positive',
        neutral: '😐 Neutral',
        negative: '😞 Negative'
    };

    successDetails.innerHTML = `
        <strong>Product:</strong> ${review.product_name}<br>
        <strong>Rating:</strong> ${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}<br>
        <strong>Sentiment:</strong> ${sentimentLabels[review.sentiment]}
    `;
}

// ============================================
// ERROR MODAL
// ============================================
function showErrorModal(message) {
    const modal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    modal.style.display = 'flex';

    // Close on backdrop click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeErrorModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function escapeHandler(e) {
        if (e.key === 'Escape') {
            closeErrorModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    });
}

function closeErrorModal() {
    const modal = document.getElementById('errorModal');
    modal.style.display = 'none';
}
