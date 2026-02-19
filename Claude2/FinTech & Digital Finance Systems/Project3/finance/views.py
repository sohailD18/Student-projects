"""
Views for the Finance Intelligence Platform.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import calendar

from .models import Transaction, Budget, FinancialInsight, Category
from .forms import TransactionForm, BudgetForm, ReportFilterForm
from .services import (
    CategoryClassifier,
    ExpensePatternAnalyzer,
    BudgetForecaster,
    InsightGenerator,
    SavingsOptimizer,
    MonthlyReportGenerator,
    get_dashboard_data
)


# ============================================================================
# Dashboard View
# ============================================================================

def dashboard(request):
    """
    Main dashboard view with analytics and insights.
    """
    # Get dashboard data
    data = get_dashboard_data()

    # Calculate summary statistics
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # This month's income and expenses
    this_month_transactions = Transaction.objects.filter(
        date__month=current_month,
        date__year=current_year
    )

    total_income_month = this_month_transactions.filter(
        transaction_type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expense_month = this_month_transactions.filter(
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    net_savings_month = total_income_month - total_expense_month

    # Get recent transactions
    recent_transactions = Transaction.objects.all()[:10]

    # Get unread insights
    unread_insights = FinancialInsight.objects.filter(is_read=False)[:5]

    context = {
        'page_title': 'Dashboard',
        'total_income': float(total_income_month),
        'total_expense': float(total_expense_month),
        'net_savings': float(net_savings_month),
        'savings_rate': float((net_savings_month / total_income_month * 100) if total_income_month > 0 else 0),
        'recent_transactions': recent_transactions,
        'insights': unread_insights,
        'category_breakdown': json.dumps(data['category_breakdown']),
        'spending_trend': json.dumps(data['spending_trend']),
        'budget_vs_actual': json.dumps(data['budget_vs_actual']),
        'savings_opportunities': data['savings_opportunities'],
        'total_potential_savings': data['total_potential_savings'],
    }

    return render(request, 'dashboard.html', context)


# ============================================================================
# Transaction Views
# ============================================================================

def transaction_list(request):
    """
    List all transactions with filtering options.
    """
    transactions = Transaction.objects.all()

    # Filter by type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Filter by category
    category = request.GET.get('category')
    if category:
        transactions = transactions.filter(category=category)

    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    context = {
        'page_title': 'Transactions',
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': total_income - total_expense,
        'categories': Category.choices,
    }

    return render(request, 'transactions.html', context)


def transaction_add(request):
    """
    Add a new transaction.
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()

            # Show category suggestion message
            if transaction.description:
                suggested = CategoryClassifier.suggest_category(transaction.description)
                if suggested != Category.OTHER and transaction.category == Category.OTHER:
                    messages.info(
                        request,
                        f'Transaction added! Based on the description, consider using category: {suggested}'
                    )
                else:
                    messages.success(request, 'Transaction added successfully!')
            else:
                messages.success(request, 'Transaction added successfully!')

            return redirect('transaction_list')
    else:
        form = TransactionForm()

    context = {
        'page_title': 'Add Transaction',
        'form': form,
        'action': 'Add',
    }

    return render(request, 'transaction_form.html', context)


def transaction_edit(request, pk):
    """
    Edit an existing transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)

    context = {
        'page_title': 'Edit Transaction',
        'form': form,
        'action': 'Edit',
        'transaction': transaction,
    }

    return render(request, 'transaction_form.html', context)


def transaction_delete(request, pk):
    """
    Delete a transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')

    context = {
        'page_title': 'Delete Transaction',
        'transaction': transaction,
    }

    return render(request, 'transaction_confirm_delete.html', context)


# ============================================================================
# Budget Views
# ============================================================================

def budget_list(request):
    """
    List all budgets with their status.
    """
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Get current month budgets
    budgets = Budget.objects.filter(month=current_month, year=current_year)

    # Calculate total budget and spent
    total_budget = sum(b.limit_amount for b in budgets)
    total_spent = sum(b.spent_amount for b in budgets)

    context = {
        'page_title': 'Budgets',
        'budgets': budgets,
        'total_budget': float(total_budget),
        'total_spent': float(total_spent),
        'total_remaining': float(total_budget - total_spent),
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
    }

    return render(request, 'budgets.html', context)


def budget_add(request):
    """
    Add a new budget.
    """
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm()

    context = {
        'page_title': 'Add Budget',
        'form': form,
        'action': 'Add',
    }

    return render(request, 'budget_form.html', context)


def budget_edit(request, pk):
    """
    Edit an existing budget.
    """
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)

    context = {
        'page_title': 'Edit Budget',
        'form': form,
        'action': 'Edit',
        'budget': budget,
    }

    return render(request, 'budget_form.html', context)


def budget_delete(request, pk):
    """
    Delete a budget.
    """
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')

    context = {
        'page_title': 'Delete Budget',
        'budget': budget,
    }

    return render(request, 'budget_confirm_delete.html', context)


# ============================================================================
# Reports Views
# ============================================================================

def reports(request):
    """
    Monthly financial reports and summaries.
    """
    report = None

    if request.method == 'GET' and 'month' in request.GET:
        form = ReportFilterForm(request.GET)
        if form.is_valid():
            month = int(form.cleaned_data['month'])
            year = int(form.cleaned_data['year'])
            report = MonthlyReportGenerator.generate_monthly_report(year, month)
    else:
        form = ReportFilterForm()
        # Generate report for current month by default
        today = timezone.now().date()
        report = MonthlyReportGenerator.generate_monthly_report(today.year, today.month)

    context = {
        'page_title': 'Reports',
        'form': form,
        'report': report,
    }

    return render(request, 'reports.html', context)


# ============================================================================
# Analytics API Views
# ============================================================================

def api_category_suggestions(request):
    """
    API endpoint to get category suggestions based on description.
    """
    description = request.GET.get('description', '')
    suggestions = CategoryClassifier.get_category_suggestions(description)

    return JsonResponse({
        'suggestions': suggestions
    })


def api_spending_patterns(request):
    """
    API endpoint to get spending pattern analysis.
    """
    day_of_week = ExpensePatternAnalyzer.analyze_spending_by_day_of_week()
    top_categories = ExpensePatternAnalyzer.get_highest_spending_categories()
    recurring = ExpensePatternAnalyzer.detect_recurring_expenses()

    return JsonResponse({
        'day_of_week': day_of_week,
        'top_categories': top_categories,
        'recurring_expenses': recurring
    })


def api_budget_forecast(request):
    """
    API endpoint to get budget forecast.
    """
    forecast = BudgetForecaster.forecast_next_month_spending()
    alerts = BudgetForecaster.generate_budget_alerts()

    return JsonResponse({
        'next_month_forecast': forecast,
        'alerts': alerts
    })


def api_savings_opportunities(request):
    """
    API endpoint to get savings optimization opportunities.
    """
    report = SavingsOptimizer.generate_savings_report()

    return JsonResponse(report)


def api_insights(request):
    """
    API endpoint to get financial insights.
    """
    insights = InsightGenerator.generate_insights()

    # Mark insights as read
    insight_ids = [i.id for i in FinancialInsight.objects.filter(is_read=False)]
    FinancialInsight.objects.filter(id__in=insight_ids).update(is_read=True)

    return JsonResponse({
        'insights': insights
    })


# ============================================================================
# Helper Views
# ============================================================================

def mark_insight_read(request, pk):
    """
    Mark an insight as read.
    """
    if request.method == 'POST':
        insight = get_object_or_404(FinancialInsight, pk=pk)
        insight.is_read = True
        insight.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


def get_summary_stats(request):
    """
    Get summary statistics for quick display.
    """
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # This month
    this_month = Transaction.objects.filter(
        date__month=current_month,
        date__year=current_year
    )

    income = this_month.filter(transaction_type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0

    expenses = this_month.filter(transaction_type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Last month for comparison
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1

    last_month_expenses = Transaction.objects.filter(
        date__month=last_month,
        date__year=last_month_year,
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate change
    if last_month_expenses > 0:
        expense_change = ((expenses - last_month_expenses) / last_month_expenses) * 100
    else:
        expense_change = 0

    return JsonResponse({
        'income': float(income),
        'expenses': float(expenses),
        'savings': float(income - expenses),
        'expense_change': round(expense_change, 1),
    })
