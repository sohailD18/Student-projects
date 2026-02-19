"""
Views for FinRisk AI - Financial Behavior and Risk Profiling System
Implements all 8 modules of the system
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import UserProfile, Transaction, RiskProfile
from .forms import UserProfileForm, TransactionForm
from .risk_engine import calculate_risk_profile, generate_financial_insights


# ==================== HOME VIEW ====================
def home(request):
    """
    Home page - Landing page for FinRisk AI
    """
    context = {
        'title': 'FinRisk AI - Financial Behavior & Risk Profiling System',
        'user_count': UserProfile.objects.count(),
        'transaction_count': Transaction.objects.count(),
        'risk_profile_count': RiskProfile.objects.count(),
    }
    return render(request, 'core/home.html', context)


# ==================== MODULE 1: Financial Behavior Data Collection ====================
def profile_list(request):
    """
    List all user profiles
    """
    profiles = UserProfile.objects.all()
    context = {
        'title': 'User Profiles',
        'profiles': profiles,
    }
    return render(request, 'core/profile_list.html', context)


def profile_create(request):
    """
    Create a new user profile
    Module 1: Financial Behavior Data Collection
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            return redirect('profile_detail', pk=profile.pk)
    else:
        form = UserProfileForm()

    context = {
        'title': 'Create User Profile',
        'form': form,
    }
    return render(request, 'core/profile_form.html', context)


def profile_detail(request, pk):
    """
    View user profile details
    """
    profile = get_object_or_404(UserProfile, pk=pk)
    transactions = profile.transactions.all()
    risk_profile = hasattr(profile, 'risk_profile')

    context = {
        'title': f'Profile - {profile.name}',
        'profile': profile,
        'transactions': transactions,
        'has_risk_profile': risk_profile,
    }
    return render(request, 'core/profile_detail.html', context)


def transaction_create(request, profile_id):
    """
    Add a transaction to a user profile
    Module 1: Financial Behavior Data Collection
    """
    profile = get_object_or_404(UserProfile, pk=profile_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user_profile = profile
            transaction.save()
            return JsonResponse({
                'success': True,
                'message': 'Transaction added successfully',
                'transaction': {
                    'id': transaction.id,
                    'date': transaction.date.strftime('%Y-%m-%d'),
                    'category': transaction.get_category_display(),
                    'amount': str(transaction.amount),
                    'type': transaction.get_transaction_type_display(),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    form = TransactionForm(initial={'date': timezone.now().date()})
    context = {
        'title': f'Add Transaction - {profile.name}',
        'form': form,
        'profile': profile,
    }
    return render(request, 'core/transaction_form.html', context)


def transaction_list(request, profile_id):
    """
    List all transactions for a profile
    Module 1: Financial Behavior Data Collection
    """
    profile = get_object_or_404(UserProfile, pk=profile_id)
    transactions = profile.transactions.all()

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    context = {
        'title': f'Transactions - {profile.name}',
        'profile': profile,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': total_income - total_expenses,
    }
    return render(request, 'core/transaction_list.html', context)


# ==================== MODULE 2, 3, 4: Analysis & Risk Profiling ====================
def analyze_profile(request, pk):
    """
    Analyze profile and create risk profile
    Module 2: Spending and Investment Pattern Analysis
    Module 3: AI-Based Risk Profiling Engine
    Module 4: Risk Tolerance Classification System
    Module 5: Personalized Financial Planning Insights
    """
    profile = get_object_or_404(UserProfile, pk=pk)

    # Check if transactions exist
    transactions = list(profile.transactions.all())
    if not transactions:
        context = {
            'title': 'Analysis Required',
            'profile': profile,
            'error': 'Please add at least one transaction before analyzing.',
        }
        return render(request, 'core/profile_detail.html', context)

    # Calculate risk profile using the risk engine
    risk_data = calculate_risk_profile(profile, transactions)

    # Create or update risk profile
    risk_profile, created = RiskProfile.objects.update_or_create(
        user_profile=profile,
        defaults=risk_data
    )

    context = {
        'title': f'Risk Analysis - {profile.name}',
        'profile': profile,
        'risk_profile': risk_profile,
        'created': created,
    }
    return render(request, 'core/risk_analysis.html', context)


# ==================== MODULE 6: Visualization Dashboard ====================
def dashboard(request, pk):
    """
    Risk vs. Return Visualization Dashboard
    Module 6: Risk vs. Return Visualization Dashboard
    """
    profile = get_object_or_404(UserProfile, pk=pk)

    # Get or create risk profile
    try:
        risk_profile = profile.risk_profile
    except RiskProfile.DoesNotExist:
        # Calculate if doesn't exist
        transactions = list(profile.transactions.all())
        if transactions:
            risk_data = calculate_risk_profile(profile, transactions)
            risk_profile = RiskProfile.objects.create(user_profile=profile, **risk_data)
        else:
            risk_profile = None

    # Prepare chart data based on risk classification
    chart_data = _prepare_chart_data(risk_profile.classification if risk_profile else 'moderate')

    context = {
        'title': f'Dashboard - {profile.name}',
        'profile': profile,
        'risk_profile': risk_profile,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'core/dashboard.html', context)


def _prepare_chart_data(classification):
    """
    Prepare chart data for different risk classifications
    Returns asset class data for risk vs. return visualization
    """
    # Define asset classes with risk and expected return percentages
    # Risk is measured as potential volatility (standard deviation)
    # Return is expected annual return

    if classification == 'conservative':
        asset_classes = [
            {'name': 'Savings Account', 'risk': 0.5, 'return': 2.0, 'allocation': 30},
            {'name': 'CDs / Fixed Deposits', 'risk': 1.0, 'return': 3.5, 'allocation': 25},
            {'name': 'Government Bonds', 'risk': 3.0, 'return': 4.0, 'allocation': 20},
            {'name': 'Blue-Chip Stocks', 'risk': 12.0, 'return': 7.0, 'allocation': 15},
            {'name': 'Corporate Bonds', 'risk': 8.0, 'return': 5.5, 'allocation': 10},
        ]
    elif classification == 'moderate':
        asset_classes = [
            {'name': 'Savings Account', 'risk': 0.5, 'return': 2.0, 'allocation': 10},
            {'name': 'Government Bonds', 'risk': 3.0, 'return': 4.0, 'allocation': 20},
            {'name': 'Corporate Bonds', 'risk': 8.0, 'return': 5.5, 'allocation': 15},
            {'name': 'Index Funds', 'risk': 15.0, 'return': 9.0, 'allocation': 25},
            {'name': 'Blue-Chip Stocks', 'risk': 12.0, 'return': 7.0, 'allocation': 15},
            {'name': 'Real Estate REITs', 'risk': 18.0, 'return': 10.0, 'allocation': 10},
            {'name': 'International Stocks', 'risk': 20.0, 'return': 11.0, 'allocation': 5},
        ]
    else:  # aggressive
        asset_classes = [
            {'name': 'Government Bonds', 'risk': 3.0, 'return': 4.0, 'allocation': 5},
            {'name': 'Index Funds', 'risk': 15.0, 'return': 9.0, 'allocation': 15},
            {'name': 'Growth Stocks', 'risk': 25.0, 'return': 14.0, 'allocation': 25},
            {'name': 'International Stocks', 'risk': 20.0, 'return': 11.0, 'allocation': 15},
            {'name': 'Emerging Markets', 'risk': 30.0, 'return': 16.0, 'allocation': 15},
            {'name': 'Cryptocurrency', 'risk': 60.0, 'return': 25.0, 'allocation': 10},
            {'name': 'Startups/VC', 'risk': 50.0, 'return': 30.0, 'allocation': 10},
            {'name': 'Commodities', 'risk': 25.0, 'return': 12.0, 'allocation': 5},
        ]

    return asset_classes


# ==================== MODULE 7: Scenario-Based Financial Analysis ====================
def scenario_calculator(request, pk):
    """
    What-If Scenario Calculator
    Module 7: Scenario-Based Financial Analysis
    """
    profile = get_object_or_404(UserProfile, pk=pk)

    # Get risk profile for baseline
    try:
        risk_profile = profile.risk_profile
        baseline_return = _get_expected_return(risk_profile.classification)
    except RiskProfile.DoesNotExist:
        baseline_return = 7.0  # Default moderate return

    context = {
        'title': f'Scenario Calculator - {profile.name}',
        'profile': profile,
        'baseline_return': baseline_return,
    }
    return render(request, 'core/scenario_calculator.html', context)


@require_http_methods(["POST"])
@csrf_exempt
def calculate_scenario(request):
    """
    API endpoint to calculate scenario projections
    Module 7: Scenario-Based Financial Analysis
    """
    try:
        data = json.loads(request.body)

        current_portfolio = Decimal(str(data.get('currentPortfolio', 100000)))
        monthly_contribution = Decimal(str(data.get('monthlyContribution', 1000)))
        savings_increase = Decimal(str(data.get('savingsIncrease', 0))) / 100
        market_change = Decimal(str(data.get('marketChange', 0))) / 100
        base_return = Decimal(str(data.get('baseReturn', 7.0)))
        years_list = [5, 10, 20, 30]

        # Calculate projections
        projections = []
        for years in years_list:
            # Adjust return based on market change
            adjusted_return = base_return + (base_return * market_change)

            # Adjust monthly contribution based on savings increase
            adjusted_monthly = monthly_contribution * (1 + savings_increase)

            # Compound interest formula with monthly contributions
            monthly_rate = adjusted_return / 100 / 12
            months = years * 12

            if monthly_rate == 0:
                future_value = current_portfolio + (adjusted_monthly * months)
            else:
                # Future Value = P(1+r)^n + PMT × [((1+r)^n - 1) / r]
                future_value = current_portfolio * ((1 + monthly_rate) ** months)
                future_value += adjusted_monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)

            projections.append({
                'years': years,
                'value': round(float(future_value), 2),
                'contributions': round(float(adjusted_monthly * months), 2),
                'gains': round(float(future_value - current_portfolio - (adjusted_monthly * months)), 2)
            })

        return JsonResponse({
            'success': True,
            'projections': projections,
            'adjustedReturn': round(float(adjusted_return), 2),
            'adjustedMonthly': round(float(adjusted_monthly), 2)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def _get_expected_return(classification):
    """
    Get expected annual return based on risk classification
    """
    returns = {
        'conservative': 5.0,
        'moderate': 8.0,
        'aggressive': 12.0
    }
    return returns.get(classification, 8.0)


# ==================== MODULE 8: Financial Risk Profiling Reports ====================
def financial_report(request, pk):
    """
    Financial Risk Profiling Report
    Module 8: Financial Risk Profiling Reports
    """
    profile = get_object_or_404(UserProfile, pk=pk)

    # Get or create risk profile
    try:
        risk_profile = profile.risk_profile
    except RiskProfile.DoesNotExist:
        transactions = list(profile.transactions.all())
        if transactions:
            risk_data = calculate_risk_profile(profile, transactions)
            risk_profile = RiskProfile.objects.create(user_profile=profile, **risk_data)
        else:
            context = {
                'title': 'Report Unavailable',
                'profile': profile,
                'error': 'No transaction data available. Add transactions and analyze profile first.',
            }
            return render(request, 'core/profile_detail.html', context)

    # Get transaction summary
    transactions = profile.transactions.all()
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    # Generate insights
    insights = generate_financial_insights(risk_profile)

    context = {
        'title': f'Financial Report - {profile.name}',
        'profile': profile,
        'risk_profile': risk_profile,
        'transactions': transactions[:10],  # Last 10 transactions
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': total_income - total_expenses,
        'insights': insights,
        'report_date': timezone.now(),
    }
    return render(request, 'core/financial_report.html', context)


# ==================== API ENDPOINTS ====================
def api_profile_stats(request, pk):
    """
    API endpoint to get profile statistics
    """
    profile = get_object_or_404(UserProfile, pk=pk)
    transactions = profile.transactions.all()

    income_by_category = {}
    expenses_by_category = {}

    for t in transactions:
        category = t.get_category_display()
        if t.transaction_type == 'income':
            income_by_category[category] = income_by_category.get(category, 0) + float(t.amount)
        else:
            expenses_by_category[category] = expenses_by_category.get(category, 0) + float(t.amount)

    return JsonResponse({
        'income': income_by_category,
        'expenses': expenses_by_category,
        'total_income': sum(income_by_category.values()),
        'total_expenses': sum(expenses_by_category.values()),
    })


@require_http_methods(["DELETE"])
def delete_transaction(request, pk):
    """
    API endpoint to delete a transaction
    """
    try:
        transaction = get_object_or_404(Transaction, pk=pk)
        profile_id = transaction.user_profile.pk
        transaction.delete()
        return JsonResponse({'success': True, 'profile_id': profile_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
