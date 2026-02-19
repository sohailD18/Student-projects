from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction


@login_required
def wallet(request):
    """View user's wallet with transaction history"""
    user = request.user
    profile = user.profile

    # Get all transactions involving the user
    sent_transactions = Transaction.objects.filter(sender=user)
    received_transactions = Transaction.objects.filter(receiver=user)

    # Combine and sort by timestamp
    all_transactions = list(sent_transactions) + list(received_transactions)
    all_transactions.sort(key=lambda x: x.timestamp, reverse=True)

    # Calculate totals
    total_earned = received_transactions.aggregate(total=Sum('amount'))['total'] or 0
    total_spent = sent_transactions.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'profile': profile,
        'transactions': all_transactions[:50],  # Last 50 transactions
        'total_earned': total_earned,
        'total_spent': total_spent,
    }
    return render(request, 'credits/wallet.html', context)
