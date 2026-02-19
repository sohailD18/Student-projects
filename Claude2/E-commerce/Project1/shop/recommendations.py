"""
AI Recommendation Engine for E-commerce
Content-Based Filtering using TF-IDF and Cosine Similarity
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Product


class ContentBasedRecommender:
    """
    Content-based recommendation system using TF-IDF and Cosine Similarity.
    Recommends products based on product descriptions and categories.
    """

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.product_ids = []

    def build_model(self):
        """
        Build the TF-IDF model from all products in the database.
        Call this after adding/updating products.
        """
        products = Product.objects.all()
        product_count = products.count()

        if product_count == 0:
            return

        # Combine product name, category, and description for better recommendations
        self.product_ids = list(products.values_list('id', flat=True))
        corpus = []

        for product in products:
            # Create a combined text feature
            combined_text = f"{product.name} {product.category.name} {product.description}"
            corpus.append(combined_text)

        # Fit and transform the corpus
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)

    def get_recommendations(self, product_id, n_recommendations=5):
        """
        Get product recommendations based on a given product.

        Args:
            product_id: ID of the product to base recommendations on
            n_recommendations: Number of recommendations to return (default: 5)

        Returns:
            List of recommended Product objects
        """
        # Build model if not already built or empty
        if self.tfidf_matrix is None:
            self.build_model()

        if self.tfidf_matrix is None or len(self.product_ids) == 0:
            return []

        # Check if product_id exists in our list
        if product_id not in self.product_ids:
            return []

        # Get the index of the product
        product_index = self.product_ids.index(product_id)

        # Calculate cosine similarity
        similarity_scores = cosine_similarity(
            self.tfidf_matrix[product_index:product_index + 1],
            self.tfidf_matrix
        )

        # Get similarity scores for all products
        similarity_scores = similarity_scores.flatten()

        # Get indices of top similar products (excluding the product itself)
        similar_indices = similarity_scores.argsort()[::-1][1:n_recommendations + 1]

        # Get recommended product IDs
        recommended_ids = [self.product_ids[i] for i in similar_indices]

        # Fetch and return the products
        recommended_products = Product.objects.filter(id__in=recommended_ids)

        # Order by similarity score
        product_order = {pid: i for i, pid in enumerate(recommended_ids)}
        recommended_products = sorted(
            recommended_products,
            key=lambda p: product_order[p.id]
        )

        return recommended_products

    def get_recommendations_for_user(self, user_id, n_recommendations=5):
        """
        Get personalized recommendations based on user's past interactions.
        Combines multiple product preferences for better recommendations.

        Args:
            user_id: ID of the user
            n_recommendations: Number of recommendations to return (default: 5)

        Returns:
            List of recommended Product objects
        """
        from .models import UserInteraction

        # Build model if not already built
        if self.tfidf_matrix is None:
            self.build_model()

        if self.tfidf_matrix is None or len(self.product_ids) == 0:
            return []

        # Get user's viewed and purchased products
        user_interactions = UserInteraction.objects.filter(
            user_id=user_id,
            interaction_type__in=['view', 'purchase', 'wishlist']
        )

        if user_interactions.count() == 0:
            # If no interactions, return popular products
            return Product.objects.all()[:n_recommendations]

        # Get unique product IDs the user interacted with
        interacted_product_ids = list(
            user_interactions
            .values_list('product_id', flat=True)
            .distinct()
        )

        # Calculate aggregate similarity scores
        aggregate_scores = np.zeros(len(self.product_ids))

        for prod_id in interacted_product_ids:
            if prod_id in self.product_ids:
                product_index = self.product_ids.index(prod_id)
                similarity_scores = cosine_similarity(
                    self.tfidf_matrix[product_index:product_index + 1],
                    self.tfidf_matrix
                ).flatten()
                aggregate_scores += similarity_scores

        # Remove already interacted products from recommendations
        for prod_id in interacted_product_ids:
            if prod_id in self.product_ids:
                idx = self.product_ids.index(prod_id)
                aggregate_scores[idx] = -1

        # Get top recommendations
        top_indices = aggregate_scores.argsort()[::-1][:n_recommendations]
        recommended_ids = [self.product_ids[i] for i in top_indices if aggregate_scores[i] > 0]

        if not recommended_ids:
            return Product.objects.all()[:n_recommendations]

        return Product.objects.filter(id__in=recommended_ids)


def get_frequently_bought_together(product_id, n=5):
    """
    Find products that are frequently bought together with the given product.
    Uses collaborative filtering based on user purchase patterns.

    Algorithm:
    1. Find all users who purchased the given product
    2. Find all other products those users purchased
    3. Rank by frequency of co-purchase

    Args:
        product_id: ID of the product to find recommendations for
        n: Number of recommendations to return (default: 5)

    Returns:
        List of tuples (Product, frequency_score) sorted by frequency
    """
    from .models import UserInteraction
    from django.db.models import Count, Q

    # Find all users who purchased this product
    user_ids = UserInteraction.objects.filter(
        product_id=product_id,
        interaction_type='purchase'
    ).values_list('user_id', flat=True).distinct()

    if not user_ids:
        # No purchase history, fall back to content-based recommendations
        return [(p, 0) for p in get_similar_products(product_id, n)]

    # Find all other products purchased by these users
    frequently_bought = UserInteraction.objects.filter(
        user_id__in=user_ids,
        interaction_type='purchase'
    ).exclude(
        product_id=product_id
    ).values(
        'product_id'
    ).annotate(
        purchase_count=Count('product_id')
    ).order_by('-purchase_count')[:n]

    # Get the product IDs and their frequencies
    product_freq_map = {
        item['product_id']: item['purchase_count']
        for item in frequently_bought
    }

    if not product_freq_map:
        # No co-purchases found, fall back to content-based
        return [(p, 0) for p in get_similar_products(product_id, n)]

    # Fetch the actual products
    recommended_products = Product.objects.filter(id__in=product_freq_map.keys())

    # Create list of (product, frequency_score) tuples
    results = [
        (product, product_freq_map[product.id])
        for product in recommended_products
    ]

    # Sort by frequency (highest first)
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def get_frequently_bought_together_for_cart(product_ids, n=5):
    """
    Find products frequently bought together with ANY product in the cart.
    Aggregates recommendations across all cart items.

    Args:
        product_ids: List of product IDs in the cart
        n: Number of recommendations to return (default: 5)

    Returns:
        List of tuples (Product, frequency_score) sorted by aggregated frequency
    """
    from .models import UserInteraction
    from django.db.models import Count, Q
    from collections import defaultdict

    if not product_ids:
        return []

    # Find all users who purchased any product in the cart
    user_ids = UserInteraction.objects.filter(
        product_id__in=product_ids,
        interaction_type='purchase'
    ).values_list('user_id', flat=True).distinct()

    if not user_ids:
        return []

    # Find all other products purchased by these users
    frequently_bought = UserInteraction.objects.filter(
        user_id__in=user_ids,
        interaction_type='purchase'
    ).exclude(
        product_id__in=product_ids
    ).values(
        'product_id'
    ).annotate(
        purchase_count=Count('product_id')
    ).order_by('-purchase_count')[:n * 2]  # Get more to filter better

    # Aggregate frequencies
    product_scores = defaultdict(int)
    for item in frequently_bought:
        product_scores[item['product_id']] += item['purchase_count']

    if not product_scores:
        return []

    # Sort by score and get top N
    sorted_products = sorted(
        product_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:n]

    # Fetch the actual products
    recommended_ids = [pid for pid, _ in sorted_products]
    recommended_products = Product.objects.filter(id__in=recommended_ids)

    # Create ordered results
    product_map = {p.id: p for p in recommended_products}
    results = [(product_map[pid], score) for pid, score in sorted_products]

    return results


# Singleton instance for reuse
recommender = ContentBasedRecommender()


def refresh_recommendation_model():
    """
    Refresh the recommendation model.
    Call this after bulk updates to products.
    """
    recommender.build_model()


def get_similar_products(product_id, n=5):
    """
    Convenience function to get similar products.

    Args:
        product_id: ID of the product
        n: Number of recommendations

    Returns:
        List of recommended Product objects
    """
    return recommender.get_recommendations(product_id, n)


def get_personalized_recommendations(user_id, n=5):
    """
    Convenience function to get personalized recommendations.

    Args:
        user_id: ID of the user
        n: Number of recommendations

    Returns:
        List of recommended Product objects
    """
    return recommender.get_recommendations_for_user(user_id, n)
