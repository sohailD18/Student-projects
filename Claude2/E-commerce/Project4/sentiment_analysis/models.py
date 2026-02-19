from django.db import models
from django.contrib.auth.models import User
from textblob import TextBlob


class Review(models.Model):
    PRODUCT_NAME_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Home & Kitchen', 'Home & Kitchen'),
        ('Books', 'Books'),
        ('Sports', 'Sports'),
        ('Other', 'Other'),
    ]

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    product_name = models.CharField(max_length=100, choices=PRODUCT_NAME_CHOICES)
    review_text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    sentiment_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product_name} - {self.rating}★ - {self.sentiment}"

    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate sentiment before saving.
        """
        # Analyze sentiment using TextBlob
        blob = TextBlob(self.review_text)
        polarity = blob.sentiment.polarity

        # Store the sentiment score
        self.sentiment_score = polarity

        # Classify sentiment based on polarity score
        if polarity > 0.1:
            self.sentiment = 'positive'
        elif polarity < -0.1:
            self.sentiment = 'negative'
        else:
            self.sentiment = 'neutral'

        super().save(*args, **kwargs)

    @classmethod
    def get_dashboard_stats(cls):
        """
        Get aggregated statistics for the dashboard.
        """
        total_reviews = cls.objects.count()

        if total_reviews == 0:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'sentiment_counts': {'positive': 0, 'neutral': 0, 'negative': 0},
                'rating_distribution': {str(i): 0 for i in range(1, 6)},
                'recent_reviews': []
            }

        # Calculate average rating
        reviews = cls.objects.all()
        avg_rating = sum(review.rating for review in reviews) / total_reviews

        # Count sentiments
        sentiment_counts = {
            'positive': cls.objects.filter(sentiment='positive').count(),
            'neutral': cls.objects.filter(sentiment='neutral').count(),
            'negative': cls.objects.filter(sentiment='negative').count(),
        }

        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = cls.objects.filter(rating=i).count()

        # Recent reviews (last 10)
        recent_reviews = list(cls.objects.all()[:10].values(
            'id', 'product_name', 'review_text', 'rating',
            'sentiment', 'created_at'
        ))

        return {
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'sentiment_counts': sentiment_counts,
            'rating_distribution': rating_distribution,
            'recent_reviews': recent_reviews
        }
