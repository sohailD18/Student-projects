"""
Risk Engine Module for FinRisk AI
Module 3: AI-Based Risk Profiling Engine
Module 4: Risk Tolerance Classification System
Module 5: Personalized Financial Planning Insights
"""
from decimal import Decimal


def calculate_risk_score(user_profile, transactions):
    """
    Calculate risk tolerance score using a robust rule-based algorithm

    Score Components (0-100 scale):
    1. Age Factor: Younger people have higher risk capacity
    2. Savings Rate: Higher savings rate indicates better financial health
    3. Income Stability: More stable income allows for more risk
    4. Investment Experience: More experience = higher risk tolerance

    Final Score = Weighted average of all components
    """
    from .models import Transaction

    # ===== 1. AGE FACTOR SCORE (0-100) =====
    # Age 18-25: 100 points (maximum risk capacity)
    # Age 26-35: 85 points
    # Age 36-45: 70 points
    # Age 46-55: 50 points
    # Age 56-65: 30 points
    # Age 65+: 10 points (minimum risk capacity)
    age = user_profile.age
    if age <= 25:
        age_score = 100
    elif age <= 35:
        age_score = 85
    elif age <= 45:
        age_score = 70
    elif age <= 55:
        age_score = 50
    elif age <= 65:
        age_score = 30
    else:
        age_score = 10

    # ===== 2. SAVINGS RATE SCORE (0-100) =====
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    if total_income > 0:
        savings_rate = float((total_income - total_expenses) / total_income * 100)
    else:
        savings_rate = 0

    # Savings rate scoring:
    # < 0% (negative savings): 0 points
    # 0-5%: 20 points
    # 5-10%: 40 points
    # 10-15%: 60 points
    # 15-20%: 80 points
    # 20%+: 100 points
    if savings_rate < 0:
        savings_score = 0
    elif savings_rate < 5:
        savings_score = 20
    elif savings_rate < 10:
        savings_score = 40
    elif savings_rate < 15:
        savings_score = 60
    elif savings_rate < 20:
        savings_score = 80
    else:
        savings_score = 100

    # ===== 3. INCOME STABILITY SCORE (0-100) =====
    stability_mapping = {
        'very_stable': 100,
        'stable': 85,
        'somewhat_stable': 50,
        'unstable': 25,
    }
    stability_score = stability_mapping.get(user_profile.income_stability, 50)

    # ===== 4. INVESTMENT EXPERIENCE SCORE (0-100) =====
    # 0 years: 30 points (baseline)
    # 1-2 years: 50 points
    # 3-5 years: 70 points
    # 6-10 years: 85 points
    # 10+ years: 100 points
    experience = user_profile.investment_experience_years
    if experience == 0:
        experience_score = 30
    elif experience <= 2:
        experience_score = 50
    elif experience <= 5:
        experience_score = 70
    elif experience <= 10:
        experience_score = 85
    else:
        experience_score = 100

    # ===== 5. DEPENDENTS ADJUSTMENT =====
    # More dependents = lower risk capacity
    # 0 dependents: No adjustment
    # 1-2 dependents: -5 points
    # 3-4 dependents: -10 points
    # 5+ dependents: -15 points
    dependents = user_profile.dependents
    if dependents == 0:
        dependents_adjustment = 0
    elif dependents <= 2:
        dependents_adjustment = -5
    elif dependents <= 4:
        dependents_adjustment = -10
    else:
        dependents_adjustment = -15

    # ===== CALCULATE FINAL SCORE =====
    # Weighted average:
    # Age: 30% weight
    # Savings Rate: 30% weight
    # Income Stability: 25% weight
    # Experience: 15% weight
    final_score = (
        (age_score * 0.30) +
        (savings_score * 0.30) +
        (stability_score * 0.25) +
        (experience_score * 0.15)
    ) + dependents_adjustment

    # Ensure score is within 0-100 range
    final_score = max(0, min(100, int(final_score)))

    return {
        'risk_score': final_score,
        'age_factor_score': age_score,
        'savings_rate_score': savings_score,
        'income_stability_score': stability_score,
        'experience_score': experience_score,
        'savings_rate': round(savings_rate, 2),
        'total_income': total_income,
        'total_expenses': total_expenses,
    }


def classify_risk_profile(risk_score):
    """
    Classify user into risk categories based on score

    Conservative: 0-40
    Moderate: 41-70
    Aggressive: 71-100
    """
    if risk_score <= 40:
        return 'conservative'
    elif risk_score <= 70:
        return 'moderate'
    else:
        return 'aggressive'


def analyze_spending_pattern(transactions):
    """
    Analyze spending patterns and categorize
    """
    essential_categories = ['housing', 'food', 'utilities', 'healthcare', 'transportation', 'education']
    discretionary_categories = ['dining', 'entertainment', 'shopping', 'travel', 'subscriptions']

    essential_expenses = sum(
        t.amount for t in transactions
        if t.transaction_type == 'expense' and t.category in essential_categories
    )
    discretionary_expenses = sum(
        t.amount for t in transactions
        if t.transaction_type == 'expense' and t.category in discretionary_categories
    )

    total_expenses = essential_expenses + discretionary_expenses

    if total_expenses == 0:
        return 'No expense data'

    essential_ratio = float(essential_expenses / total_expenses * 100)

    # Categorize spending pattern
    if essential_ratio >= 80:
        pattern = 'Essential Heavy'
    elif essential_ratio >= 60:
        pattern = 'Balanced Essential'
    elif essential_ratio >= 40:
        pattern = 'Balanced Discretionary'
    else:
        pattern = 'Discretionary Heavy'

    return pattern


def calculate_risk_profile(user_profile, transactions):
    """
    Main function to calculate complete risk profile
    Module 3: AI-Based Risk Profiling Engine
    Module 4: Risk Tolerance Classification System
    Module 5: Personalized Financial Planning Insights
    """
    from .models import Transaction

    # Calculate risk score
    risk_data = calculate_risk_score(user_profile, transactions)

    # Add classification
    classification = classify_risk_profile(risk_data['risk_score'])
    risk_data['classification'] = classification

    # Analyze spending pattern
    essential_categories = ['housing', 'food', 'utilities', 'healthcare', 'transportation', 'education']
    discretionary_categories = ['dining', 'entertainment', 'shopping', 'travel', 'subscriptions']

    essential_expenses = sum(
        t.amount for t in transactions
        if t.transaction_type == 'expense' and t.category in essential_categories
    )
    discretionary_expenses = sum(
        t.amount for t in transactions
        if t.transaction_type == 'expense' and t.category in discretionary_categories
    )

    risk_data['essential_expenses'] = float(essential_expenses)
    risk_data['discretionary_expenses'] = float(discretionary_expenses)

    # Add spending pattern
    spending_pattern = analyze_spending_pattern(transactions)
    risk_data['spending_pattern'] = spending_pattern

    # Generate personalized insights
    insights = generate_financial_insights_risk(classification, risk_data['savings_rate'], spending_pattern)
    risk_data['insights'] = insights

    return risk_data


def generate_financial_insights_risk(classification, savings_rate, spending_pattern):
    """
    Generate personalized financial insights based on risk profile
    Module 5: Personalized Financial Planning Insights
    """
    insights = []

    # Risk classification insights
    if classification == 'conservative':
        insights.extend([
            "Your risk tolerance is LOW. You prioritize capital preservation over high returns.",
            "Recommended portfolio allocation: 60-70% in fixed income, 20-30% in bonds, 10-20% in blue-chip stocks.",
            "Focus on: Government bonds, fixed deposits, high-quality corporate bonds, dividend stocks.",
            "Avoid: Highly volatile stocks, cryptocurrencies, speculative investments, leveraged products.",
            "Your investment horizon should be 3-5 years for optimal results.",
        ])
    elif classification == 'moderate':
        insights.extend([
            "Your risk tolerance is MODERATE. You seek a balance between growth and stability.",
            "Recommended portfolio allocation: 40-50% in stocks, 30-40% in bonds, 10-20% in alternatives.",
            "Focus on: Index funds, balanced mutual funds, blue-chip stocks, investment-grade bonds.",
            "Consider: International diversification, real estate investment trusts (REITs).",
            "Your investment horizon should be 5-10 years for optimal growth.",
        ])
    else:  # aggressive
        insights.extend([
            "Your risk tolerance is HIGH. You prioritize maximum growth and can handle significant volatility.",
            "Recommended portfolio allocation: 70-80% in equities, 10-20% in alternatives, 5-10% in cash.",
            "Focus on: Growth stocks, emerging markets, sector-specific funds, small-cap stocks.",
            "Consider: Cryptocurrency (5-10% max), startups, venture capital, commodities.",
            "Your investment horizon should be 10+ years to ride out market cycles.",
        ])

    # Savings rate insights
    if savings_rate < 5:
        insights.append(
            "⚠️ CRITICAL: Your savings rate is below 5%. Focus on building an emergency fund first, "
            "then gradually increase savings to at least 10-15% of your income."
        )
    elif savings_rate < 15:
        insights.append(
            "Your savings rate is moderate. Aim to increase it to 20% for faster wealth accumulation "
            "and better financial security."
        )
    else:
        insights.append(
            "Excellent! Your savings rate is strong. Consider investing surplus in tax-advantaged "
            "accounts for maximum wealth growth."
        )

    # Spending pattern insights
    if spending_pattern == 'Essential Heavy':
        insights.append(
            "Your spending is focused on essentials. Consider reviewing your fixed expenses for "
            "potential savings opportunities."
        )
    elif spending_pattern == 'Discretionary Heavy':
        insights.append(
            "Your discretionary spending is high. Review and prioritize non-essential expenses to "
            "boost your savings rate."
        )
    else:
        insights.append(
            "Your spending pattern is well-balanced between essential and discretionary expenses."
        )

    return "\n\n".join(insights)


def generate_financial_insights(risk_profile):
    """
    Wrapper function to generate insights from risk profile object
    """
    return generate_financial_insights_risk(
        risk_profile.classification,
        float(risk_profile.savings_rate),
        risk_profile.spending_pattern
    )
