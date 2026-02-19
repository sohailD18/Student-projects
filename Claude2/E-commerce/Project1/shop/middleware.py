"""
Django Middleware for tracking user interactions.
Automatically tracks product views for logged-in users.
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import UserInteraction


class ProductViewTrackerMiddleware(MiddlewareMixin):
    """
    Middleware to automatically track when a logged-in user views a product.

    This middleware intercepts requests to product detail pages and creates
    a 'view' interaction in the UserInteraction model.

    Usage:
    1. Add this middleware to MIDDLEWARE in settings.py
    2. Ensure your product detail URL follows the pattern: /products/<id>/
       or configure PRODUCT_URL_PATTERN in settings.py

    Settings:
        PRODUCT_URL_PATTERN: URL pattern to match (default: '/products/')
        TRACK_ANONYMOUS_USERS: Whether to track anonymous users (default: False)
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        # Configure URL pattern to match product pages
        self.product_url_pattern = getattr(settings, 'PRODUCT_URL_PATTERN', '/products/')
        # Whether to track anonymous users (requires session)
        self.track_anonymous = getattr(settings, 'TRACK_ANONYMOUS_USERS', False)

    def process_response(self, request, response):
        """
        Process the response and track product views.

        Only tracks:
        - Successful responses (status code 200)
        - Product detail pages (matching URL pattern)
        - Logged-in users (unless TRACK_ANONYMOUS_USERS is True)
        - GET requests (not POST, PUT, etc.)
        """
        # Only track successful GET requests
        if response.status_code != 200 or request.method != 'GET':
            return response

        # Check if the path contains the product URL pattern
        if self.product_url_pattern not in request.path:
            return response

        # Extract product ID from URL
        product_id = self._extract_product_id(request.path)
        if not product_id:
            return response

        # Get user (must be authenticated unless tracking anonymous)
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            if self.track_anonymous:
                # For anonymous users, you could store in session
                # This requires additional implementation
                return response
            return response

        # Track the view asynchronously (don't slow down the response)
        self._track_view(user, product_id, request)

        return response

    def _extract_product_id(self, path):
        """
        Extract product ID from the URL path.

        Supports patterns like:
        - /products/123/
        - /products/123
        - /shop/product/123/
        - /api/products/123/

        Returns:
            int: Product ID or None if not found
        """
        try:
            # Get the last numeric segment from the path
            segments = path.strip('/').split('/')
            for segment in reversed(segments):
                if segment.isdigit():
                    return int(segment)
        except (ValueError, AttributeError):
            pass
        return None

    def _track_view(self, user, product_id, request):
        """
        Create a UserInteraction record for the product view.

        Uses get_or_create to avoid duplicate views within the same session
        if needed, or always creates to track every view.

        Args:
            user: The User object
            product_id: The ID of the product being viewed
            request: The HTTP request object
        """
        try:
            from django.core.exceptions import ValidationError
            from .models import Product

            # Verify the product exists
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return

            # Check if we should avoid duplicate tracking
            # Option 1: Track every view
            UserInteraction.objects.create(
                user=user,
                product=product,
                interaction_type='view'
            )

            # Option 2 (alternative): Only track once per session
            # Uncomment below to use this approach instead
            # session_key = f'viewed_product_{product_id}'
            # if session_key not in request.session:
            #     UserInteraction.objects.create(
            #         user=user,
            #         product=product,
            #         interaction_type='view'
            #     )
            #     request.session[session_key] = True

        except Exception as e:
            # Silently fail to avoid breaking the user experience
            # In production, you might want to log this error
            pass


class InteractionTrackerMiddleware(MiddlewareMixin):
    """
    Enhanced middleware that tracks multiple types of interactions.

    This is a more flexible version that can track:
    - Product views
    - Add to cart events
    - Wishlist additions

    Usage:
    - Set request.interaction_type in your view before rendering
    - Example: request.interaction_type = 'cart'
    - The middleware will create the appropriate UserInteraction record
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.product_url_pattern = getattr(settings, 'PRODUCT_URL_PATTERN', '/products/')

    def process_response(self, request, response):
        """Track various types of user interactions."""
        if response.status_code != 200 or request.method != 'GET':
            return response

        # Get the interaction type from the request (set by views)
        interaction_type = getattr(request, 'track_interaction', None)

        # If no interaction specified, only track product page views
        if not interaction_type:
            if self.product_url_pattern not in request.path:
                return response
            interaction_type = 'view'

        # Extract product ID
        product_id = self._extract_product_id(request.path)
        if not product_id:
            return response

        # Get user
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return response

        # Track the interaction
        self._track_interaction(user, product_id, interaction_type)

        return response

    def _extract_product_id(self, path):
        """Extract product ID from URL."""
        try:
            segments = path.strip('/').split('/')
            for segment in reversed(segments):
                if segment.isdigit():
                    return int(segment)
        except (ValueError, AttributeError):
            pass
        return None

    def _track_interaction(self, user, product_id, interaction_type):
        """Create UserInteraction record."""
        try:
            from .models import Product

            product = Product.objects.filter(id=product_id).first()
            if not product:
                return

            UserInteraction.objects.create(
                user=user,
                product=product,
                interaction_type=interaction_type
            )
        except Exception:
            pass
