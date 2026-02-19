"""
Utility functions for Credit Risk Assessment System
"""
from typing import Dict, Tuple
from decimal import Decimal


def calculate_eligibility(prediction_probability: float, applicant_profile: Dict) -> Tuple[str, str]:
    """
    Calculate loan eligibility based on prediction probability and applicant profile

    Args:
        prediction_probability (float): ML model's predicted probability of default (0.0 to 1.0)
        applicant_profile (dict): Dictionary containing applicant information including credit_score

    Returns:
        tuple: (eligibility_status, risk_category)
            - eligibility_status: 'approved', 'manual_review', or 'rejected'
            - risk_category: 'low', 'medium', or 'high'

    Rules:
        - If prediction_probability < 0.3: "Approved"
        - If prediction_probability 0.3 - 0.6: "Manual Review"
        - If prediction_probability > 0.6: "Rejected"
        - Bonus: If Credit Score > 750, lower the risk probability by 10%
    """
    # Apply credit score bonus
    adjusted_probability = prediction_probability

    credit_score = applicant_profile.get('credit_score', 0)

    if credit_score > 750:
        # Lower risk probability by 10%
        adjusted_probability = max(0, prediction_probability * 0.9)

    # Determine risk category
    if adjusted_probability < 0.3:
        risk_category = 'low'
    elif adjusted_probability < 0.6:
        risk_category = 'medium'
    else:
        risk_category = 'high'

    # Determine eligibility status
    if adjusted_probability < 0.3:
        eligibility_status = 'approved'
    elif adjusted_probability < 0.6:
        eligibility_status = 'manual_review'
    else:
        eligibility_status = 'rejected'

    return eligibility_status, risk_category


def get_risk_category_details(risk_category: str) -> Dict:
    """
    Get details about a risk category for display purposes

    Args:
        risk_category (str): 'low', 'medium', or 'high'

    Returns:
        dict: Dictionary containing label, color, description
    """
    risk_details = {
        'low': {
            'label': 'Low Risk',
            'color': '#28a745',  # Green
            'bg_color': '#d4edda',
            'text_color': '#155724',
            'icon': '✓',
            'description': 'Applicant demonstrates strong financial health and low risk of default.',
            'recommendation': 'Recommended for approval with standard terms.'
        },
        'medium': {
            'label': 'Medium Risk',
            'color': '#ffc107',  # Yellow
            'bg_color': '#fff3cd',
            'text_color': '#856404',
            'icon': '⚠',
            'description': 'Applicant shows moderate risk factors that require review.',
            'recommendation': 'Requires manual review. Consider additional documentation or adjusted terms.'
        },
        'high': {
            'label': 'High Risk',
            'color': '#dc3545',  # Red
            'bg_color': '#f8d7da',
            'text_color': '#721c24',
            'icon': '✗',
            'description': 'Applicant presents significant risk factors.',
            'recommendation': 'Not recommended for approval under standard terms.'
        }
    }

    return risk_details.get(risk_category, risk_details['medium'])


def preprocess_applicant_data(applicant_data: Dict, financial_data: Dict) -> Dict:
    """
    Convert raw form data into format suitable for ML model

    Args:
        applicant_data (dict): Applicant form data
        financial_data (dict): Financial data form data

    Returns:
        dict: Processed data ready for ML prediction
    """
    processed_data = {
        'annual_income': float(applicant_data.get('annual_income', 0)),
        'employment_status': applicant_data.get('employment_status', 'employed'),
        'years_employed': int(applicant_data.get('years_employed', 0)),
        'debt_to_income_ratio': float(applicant_data.get('debt_to_income_ratio', 0)),
        'credit_score': int(financial_data.get('credit_score', 650)),
        'num_open_loans': int(financial_data.get('num_open_loans', 0)),
        'num_credit_lines': int(financial_data.get('num_credit_lines', 0)),
        'late_payments': int(financial_data.get('late_payments', 0)),
        'bankruptcies': 1 if financial_data.get('bankruptcies', False) else 0,
        'home_ownership_status': financial_data.get('home_ownership_status', 'rent')
    }

    return processed_data


def format_currency(value: float) -> str:
    """Format a number as currency string"""
    if value is None:
        return '$0.00'
    return f'${value:,.2f}'


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format a number as percentage string"""
    if value is None:
        return '0%'
    return f'{value:.{decimal_places}f}%'


def calculate_credit_score_factor(credit_score: int) -> str:
    """
    Get a description of the credit score range

    Args:
        credit_score (int): Credit score (300-850)

    Returns:
        str: Description of credit score category
    """
    if credit_score >= 800:
        return 'Exceptional (800-850)'
    elif credit_score >= 740:
        return 'Very Good (740-799)'
    elif credit_score >= 670:
        return 'Good (670-739)'
    elif credit_score >= 580:
        return 'Fair (580-669)'
    else:
        return 'Poor (300-579)'


def validate_applicant_data(data: Dict) -> Tuple[bool, list]:
    """
    Validate applicant data before processing

    Args:
        data (dict): Applicant data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []

    # Required fields check
    required_fields = [
        'name', 'email', 'phone', 'annual_income',
        'employment_status', 'years_employed', 'debt_to_income_ratio'
    ]

    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required")

    # Numeric validation
    try:
        if 'annual_income' in data:
            income = float(data['annual_income'])
            if income < 0:
                errors.append("Annual income must be positive")

        if 'debt_to_income_ratio' in data:
            dti = float(data['debt_to_income_ratio'])
            if dti < 0 or dti > 100:
                errors.append("Debt-to-income ratio must be between 0 and 100")

        if 'years_employed' in data:
            years = int(data['years_employed'])
            if years < 0 or years > 50:
                errors.append("Years employed must be between 0 and 50")

    except (ValueError, TypeError):
        errors.append("Invalid numeric value provided")

    return len(errors) == 0, errors


def validate_financial_data(data: Dict) -> Tuple[bool, list]:
    """
    Validate financial data before processing

    Args:
        data (dict): Financial data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []

    # Required fields check
    required_fields = [
        'credit_score', 'num_open_loans', 'num_credit_lines',
        'late_payments', 'home_ownership_status'
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"{field.replace('_', ' ').title()} is required")

    # Credit score validation
    try:
        if 'credit_score' in data:
            score = int(data['credit_score'])
            if score < 300 or score > 850:
                errors.append("Credit score must be between 300 and 850")

        if 'num_open_loans' in data:
            loans = int(data['num_open_loans'])
            if loans < 0:
                errors.append("Number of open loans cannot be negative")

        if 'late_payments' in data:
            late = int(data['late_payments'])
            if late < 0:
                errors.append("Number of late payments cannot be negative")

    except (ValueError, TypeError):
        errors.append("Invalid numeric value provided")

    return len(errors) == 0, errors


def get_dashboard_statistics(applicants_queryset):
    """
    Calculate statistics for the dashboard

    Args:
        applicants_queryset: QuerySet of Applicant objects

    Returns:
        dict: Dictionary containing various statistics
    """
    from .models import Applicant

    total_applicants = applicants_queryset.count()

    if total_applicants == 0:
        return {
            'total_applicants': 0,
            'approved_count': 0,
            'manual_review_count': 0,
            'rejected_count': 0,
            'low_risk_count': 0,
            'medium_risk_count': 0,
            'high_risk_count': 0,
            'low_risk_percentage': 0,
            'medium_risk_percentage': 0,
            'high_risk_percentage': 0,
            'approval_rate': 0,
            'average_income': 0,
            'average_credit_score': 0,
            'risk_distribution': [],
            'income_by_status': {}
        }

    # Status counts
    approved_count = applicants_queryset.filter(eligibility_status='approved').count()
    manual_review_count = applicants_queryset.filter(eligibility_status='manual_review').count()
    rejected_count = applicants_queryset.filter(eligibility_status='rejected').count()

    # Risk category counts
    low_risk_count = applicants_queryset.filter(risk_category='low').count()
    medium_risk_count = applicants_queryset.filter(risk_category='medium').count()
    high_risk_count = applicants_queryset.filter(risk_category='high').count()

    # Calculate averages
    avg_income = applicants_queryset.aggregate(avg_income=models.Avg('annual_income'))['avg_income'] or 0

    # Get credit scores from related financial data
    avg_credit_score = 0
    credit_scores = []
    for applicant in applicants_queryset:
        if hasattr(applicant, 'financial_data'):
            credit_scores.append(applicant.financial_data.credit_score)

    if credit_scores:
        avg_credit_score = sum(credit_scores) / len(credit_scores)

    # Risk distribution for pie chart
    risk_distribution = [
        {'category': 'Low Risk', 'count': low_risk_count, 'color': '#28a745'},
        {'category': 'Medium Risk', 'count': medium_risk_count, 'color': '#ffc107'},
        {'category': 'High Risk', 'count': high_risk_count, 'color': '#dc3545'}
    ]

    # Income by status for bar chart
    income_by_status = {
        'approved': float(applicants_queryset.filter(eligibility_status='approved')
                         .aggregate(avg=models.Avg('annual_income'))['avg'] or 0),
        'manual_review': float(applicants_queryset.filter(eligibility_status='manual_review')
                              .aggregate(avg=models.Avg('annual_income'))['avg'] or 0),
        'rejected': float(applicants_queryset.filter(eligibility_status='rejected')
                         .aggregate(avg=models.Avg('annual_income'))['avg'] or 0)
    }

    return {
        'total_applicants': total_applicants,
        'approved_count': approved_count,
        'manual_review_count': manual_review_count,
        'rejected_count': rejected_count,
        'low_risk_count': low_risk_count,
        'medium_risk_count': medium_risk_count,
        'high_risk_count': high_risk_count,
        'low_risk_percentage': round((low_risk_count / total_applicants) * 100, 2) if total_applicants > 0 else 0,
        'medium_risk_percentage': round((medium_risk_count / total_applicants) * 100, 2) if total_applicants > 0 else 0,
        'high_risk_percentage': round((high_risk_count / total_applicants) * 100, 2) if total_applicants > 0 else 0,
        'approval_rate': round((approved_count / total_applicants) * 100, 2) if total_applicants > 0 else 0,
        'average_income': float(avg_income),
        'average_credit_score': round(avg_credit_score, 2),
        'risk_distribution': risk_distribution,
        'income_by_status': income_by_status
    }


# Import at the end to avoid circular dependency
from django.db import models
