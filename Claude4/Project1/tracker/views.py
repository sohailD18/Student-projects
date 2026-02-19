from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from decimal import Decimal
from .models import Transaction, Category
from .forms import TransactionForm, SignupForm, LoginForm


def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Create default categories for the user
            default_categories = [
                # Income categories
                {'name': 'Salary', 'type': 'INCOME'},
                {'name': 'Freelance', 'type': 'INCOME'},
                {'name': 'Investments', 'type': 'INCOME'},
                {'name': 'Other Income', 'type': 'INCOME'},
                # Expense categories
                {'name': 'Food & Dining', 'type': 'EXPENSE'},
                {'name': 'Transportation', 'type': 'EXPENSE'},
                {'name': 'Shopping', 'type': 'EXPENSE'},
                {'name': 'Entertainment', 'type': 'EXPENSE'},
                {'name': 'Bills & Utilities', 'type': 'EXPENSE'},
                {'name': 'Healthcare', 'type': 'EXPENSE'},
                {'name': 'Education', 'type': 'EXPENSE'},
                {'name': 'Other Expense', 'type': 'EXPENSE'},
            ]

            for cat_data in default_categories:
                Category.objects.create(
                    name=cat_data['name'],
                    type=cat_data['type']
                )

            from django.urls import reverse
            login_url = reverse('tracker:login')
            return redirect(f'{login_url}?signup=success')
    else:
        form = SignupForm()

    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            from django.contrib.auth import authenticate
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                from django.urls import reverse
                dashboard_url = reverse('tracker:dashboard')
                return redirect(f'{dashboard_url}?login=success&username={username}')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'tracker/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    from django.urls import reverse
    login_url = reverse('tracker:login')
    return redirect(f'{login_url}?logout=success')


@login_required
def dashboard_view(request):
    """Dashboard with financial overview and charts"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    # Calculate totals
    total_income = transactions.filter(category__type='INCOME').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    total_expense = transactions.filter(category__type='EXPENSE').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    current_balance = total_income - total_expense

    # Get recent transactions (last 10)
    recent_transactions = transactions[:10]

    # Prepare data for expense by category chart
    expense_by_category = list(
        transactions
        .filter(category__type='EXPENSE')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    category_labels = [item['category__name'] for item in expense_by_category]
    category_amounts = [float(item['total']) for item in expense_by_category]

    # Generate colors for categories
    category_colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
    ]

    # Prepare data for monthly income vs expense chart (last 6 months)
    months_data = []
    month_names = []

    for i in range(5, -1, -1):
        current_date = date.today()
        target_month = (current_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        next_month = (target_month + timedelta(days=32)).replace(day=1)

        month_name = target_month.strftime('%b %Y')
        month_names.append(month_name)

        monthly_income = transactions.filter(
            category__type='INCOME',
            date__gte=target_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        monthly_expense = transactions.filter(
            category__type='EXPENSE',
            date__gte=target_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        months_data.append({
            'month': month_name,
            'income': float(monthly_income),
            'expense': float(monthly_expense)
        })

    monthly_income = [m['income'] for m in months_data]
    monthly_expense = [m['expense'] for m in months_data]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'current_balance': current_balance,
        'recent_transactions': recent_transactions,
        'transaction_count': transactions.count(),
        # Category chart data
        'category_labels': category_labels,
        'category_amounts': category_amounts,
        'category_colors': category_colors,
        # Monthly chart data
        'month_names': month_names,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
    }

    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_transaction_view(request):
    """Add new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            from django.urls import reverse
            dashboard_url = reverse('tracker:dashboard')
            return redirect(f'{dashboard_url}?added=success')
    else:
        form = TransactionForm()

    return render(request, 'tracker/add_transaction.html', {'form': form})


@login_required
def delete_transaction_view(request, transaction_id):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        from django.urls import reverse
        dashboard_url = reverse('tracker:dashboard')
        return redirect(f'{dashboard_url}?deleted=success')

    return render(request, 'tracker/delete_transaction.html', {'transaction': transaction})
