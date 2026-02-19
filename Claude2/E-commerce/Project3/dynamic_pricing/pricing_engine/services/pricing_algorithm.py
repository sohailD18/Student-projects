from django.db.models import Avg, Sum, F, DecimalField
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Tuple, Dict, Any
import statistics


class DynamicPricingEngine:
    """
    AI-Enabled Dynamic Pricing Engine that analyzes sales trends,
    competitor prices, and stock levels to suggest optimal pricing.
    """

    def __init__(self):
        self.lookback_days = 30

    def calculate_optimal_price(self, product) -> Tuple[Decimal, str]:
        """
        Calculate the optimal price for a product based on various factors.

        Args:
            product: Product instance

        Returns:
            Tuple of (suggested_price, explanation)
        """
        # Fetch historical data
        sales_data = self._get_sales_data(product)
        competitor_prices = self._get_competitor_prices(product)

        # Analyze factors
        sales_trend = self._analyze_sales_trend(sales_data)
        stock_status = self._analyze_stock(product)
        competitor_analysis = self._analyze_competitors(product, competitor_prices)
        elasticity_score = self._calculate_elasticity(product, sales_data)

        # Determine price action
        suggested_price, reason = self._determine_price_action(
            product,
            sales_trend,
            stock_status,
            competitor_analysis,
            elasticity_score
        )

        return suggested_price, reason

    def _get_sales_data(self, product):
        """Fetch sales data for the lookback period."""
        cutoff_date = timezone.now() - timedelta(days=self.lookback_days)
        return product.sales_history.filter(date__gte=cutoff_date).order_by('date')

    def _get_competitor_prices(self, product):
        """Fetch current competitor prices."""
        cutoff_date = timezone.now() - timedelta(days=7)  # Prices from last 7 days
        return list(product.competitor_prices.filter(recorded_at__gte=cutoff_date).values_list('price', flat=True))

    def _analyze_sales_trend(self, sales_data):
        """Analyze sales trend over time."""
        if sales_data.count() < 2:
            return 'stable'

        # Group sales by day and calculate trend
        from django.db.models import Count
        from datetime import timedelta

        # Get daily sales quantities
        daily_sales = []
        for i in range(self.lookback_days):
            day_start = timezone.now() - timedelta(days=i+1)
            day_end = timezone.now() - timedelta(days=i)
            day_total = sales_data.filter(date__gte=day_start, date__lt=day_end).aggregate(
                total=Sum('quantity_sold')
            )['total'] or 0
            daily_sales.append(day_total)

        # Simple trend analysis: compare recent week to previous week
        if len(daily_sales) >= 14:
            recent_week = sum(daily_sales[:7])
            previous_week = sum(daily_sales[7:14])

            if previous_week == 0:
                return 'stable'

            change_percent = ((recent_week - previous_week) / previous_week) * 100

            if change_percent < -15:
                return 'decreasing'
            elif change_percent > 15:
                return 'increasing'

        return 'stable'

    def _analyze_stock(self, product):
        """Analyze stock levels."""
        if product.stock_quantity < 10:
            return 'low'
        elif product.stock_quantity > 100:
            return 'high'
        else:
            return 'normal'

    def _analyze_competitors(self, product, competitor_prices):
        """Analyze competitor pricing."""
        if not competitor_prices:
            return {
                'avg_price': None,
                'min_price': None,
                'max_price': None,
                'position': 'unknown'
            }

        avg_price = statistics.mean(competitor_prices)
        min_price = min(competitor_prices)
        max_price = max(competitor_prices)

        if float(product.current_price) < float(min_price):
            position = 'below_all'
        elif float(product.current_price) > float(max_price):
            position = 'above_all'
        elif float(product.current_price) < float(avg_price):
            position = 'below_average'
        else:
            position = 'above_average'

        return {
            'avg_price': Decimal(str(avg_price)),
            'min_price': Decimal(str(min_price)),
            'max_price': Decimal(str(max_price)),
            'position': position
        }

    def _calculate_elasticity(self, product, sales_data):
        """
        Calculate price elasticity score based on historical data.
        Higher score = more elastic (demand is more sensitive to price changes).
        """
        price_changes = list(product.price_history.all().order_by('-timestamp')[:10])

        if len(price_changes) < 2 or sales_data.count() < 2:
            return 1.0  # Neutral elasticity

        # Simplified elasticity calculation
        # Compare sales volume before and after price changes
        elasticity_scores = []

        for price_change in price_changes:
            # Get sales before price change (7 days)
            before_date = price_change.timestamp - timedelta(days=7)
            before_sales = product.sales_history.filter(
                date__gte=before_date,
                date__lt=price_change.timestamp
            ).aggregate(total=Sum('quantity_sold'))['total'] or 0

            # Get sales after price change (7 days)
            after_date = price_change.timestamp + timedelta(days=7)
            after_sales = product.sales_history.filter(
                date__gte=price_change.timestamp,
                date__lt=after_date
            ).aggregate(total=Sum('quantity_sold'))['total'] or 0

            if before_sales > 0 and price_change.old_price > 0:
                # Calculate percentage change in quantity and price
                qty_change_percent = ((after_sales - before_sales) / before_sales) * 100
                # Convert to float to avoid Decimal/float division issues
                price_change_percent = float(((price_change.new_price - price_change.old_price) / price_change.old_price) * 100)

                if price_change_percent != 0:
                    elasticity = abs(qty_change_percent / price_change_percent)
                    elasticity_scores.append(elasticity)

        if elasticity_scores:
            return statistics.mean(elasticity_scores)

        return 1.0

    def _determine_price_action(self, product, sales_trend, stock_status,
                               competitor_analysis, elasticity_score):
        """
        Determine the appropriate price action based on all factors.
        """
        current_price = product.current_price
        base_cost = product.base_cost
        suggested_price = current_price
        reasons = []

        # Rule 1: If sales are decreasing AND stock is high -> Decrease price
        if sales_trend == 'decreasing' and stock_status == 'high':
            decrease_percent = min(10, 20 / elasticity_score)  # More elastic = smaller decrease
            suggested_price = current_price * (Decimal('1') - Decimal(decrease_percent) / Decimal('100'))
            reasons.append(f"Sales trending down and stock is high. Decreasing price by {decrease_percent:.1f}% to stimulate demand.")

        # Rule 2: If competitor prices are significantly higher -> Increase price (but cap at competitor min - 5%)
        elif competitor_analysis['position'] in ['below_all', 'below_average'] and competitor_analysis['min_price']:
            max_allowed_price = competitor_analysis['min_price'] * Decimal('0.95')  # Competitor min - 5%
            if current_price < max_allowed_price:
                # Increase gradually based on elasticity
                increase_percent = min(5, 10 / elasticity_score)
                suggested_price = min(current_price * (Decimal('1') + Decimal(increase_percent) / Decimal('100')), max_allowed_price)
                if suggested_price > current_price:
                    reasons.append(f"Competitor prices are higher. Increasing price to capture more margin while remaining competitive.")

        # Rule 3: If stock is low (< 10 items) -> Increase price (Scarcity principle)
        elif stock_status == 'low':
            increase_percent = min(15, 25 / elasticity_score)  # More elastic = smaller increase
            suggested_price = current_price * (Decimal('1') + Decimal(increase_percent) / Decimal('100'))
            reasons.append(f"Low stock ({product.stock_quantity} units). Increasing price by {increase_percent:.1f}% to maximize profit on remaining inventory.")

        # Rule 4: If sales are increasing -> Gradual price increase
        elif sales_trend == 'increasing':
            increase_percent = min(3, 8 / elasticity_score)
            suggested_price = current_price * (Decimal('1') + Decimal(increase_percent) / Decimal('100'))
            reasons.append(f"Strong sales trend. Gradually increasing price by {increase_percent:.1f}% to optimize profit margins.")

        # Ensure price never goes below base cost
        if suggested_price < base_cost:
            suggested_price = base_cost * Decimal('1.05')  # Minimum 5% margin
            reasons.append("Adjusted to ensure minimum 5% profit margin.")

        # Ensure minimum viable price (at least 10% above cost)
        min_price = base_cost * Decimal('1.10')
        if suggested_price < min_price:
            suggested_price = min_price
            if not any("minimum" in r.lower() for r in reasons):
                reasons.append("Price adjusted to maintain minimum 10% margin.")

        # If no changes needed
        if not reasons:
            reasons.append("Current price is optimal based on market conditions.")

        # Round to 2 decimal places
        suggested_price = suggested_price.quantize(Decimal('0.01'))

        return suggested_price, " | ".join(reasons)

    def simulate_profit(self, product, hypothetical_price, hypothetical_demand) -> Dict[str, Any]:
        """
        Simulate profit for a hypothetical scenario.

        Args:
            product: Product instance
            hypothetical_price: Decimal - hypothetical price point
            hypothetical_demand: int - hypothetical quantity sold

        Returns:
            Dictionary with simulation results
        """
        current_profit = (product.current_price - product.base_cost) * hypothetical_demand
        hypothetical_profit = (hypothetical_price - product.base_cost) * hypothetical_demand
        profit_difference = hypothetical_profit - current_profit

        margin_current = ((product.current_price - product.base_cost) / product.current_price) * 100
        margin_hypothetical = ((hypothetical_price - product.base_cost) / hypothetical_price) * 100

        return {
            'current_revenue': float(product.current_price * hypothetical_demand),
            'hypothetical_revenue': float(hypothetical_price * hypothetical_demand),
            'current_profit': float(current_profit),
            'hypothetical_profit': float(hypothetical_profit),
            'profit_difference': float(profit_difference),
            'profit_improvement_percent': float((profit_difference / current_profit * 100) if current_profit > 0 else 0),
            'current_margin': float(margin_current),
            'hypothetical_margin': float(margin_hypothetical),
            'recommendation': 'Increase' if hypothetical_profit > current_profit else 'Decrease' if hypothetical_profit < current_profit else 'Maintain'
        }
