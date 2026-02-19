from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Complaint, Ticket, Feedback
from .forms import ComplaintForm, TicketUpdateForm, FeedbackForm


def home(request):
    """Home page with welcome message and ticket search."""
    return render(request, 'tickets/home.html')


def submit_complaint(request):
    """Handle complaint submission form."""
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            # Save the complaint
            complaint = form.save()

            # Automatically create a ticket for this complaint
            ticket = Ticket.objects.create(
                complaint=complaint,
                status='open'
            )

            # Success message with ticket ID
            messages.success(
                request,
                f'Your complaint has been submitted successfully! '
                f'Your ticket ID is: <strong>{ticket.unique_ticket_id}</strong>'
            )

            # Redirect to success page
            return redirect('tickets:success', ticket_id=ticket.unique_ticket_id)
    else:
        form = ComplaintForm()

    return render(request, 'tickets/submit.html', {'form': form})


def success(request, ticket_id):
    """Success page after complaint submission."""
    try:
        ticket = Ticket.objects.get(unique_ticket_id=ticket_id)
        return render(request, 'tickets/success.html', {'ticket': ticket})
    except Ticket.DoesNotExist:
        messages.error(request, 'Ticket not found.')
        return redirect('tickets:home')


def dashboard(request):
    """Staff dashboard to view and manage tickets.

    Queries all Ticket objects from the database, sorted by creation date
    (newest first). Supports filtering by status and priority.
    """
    # Query all tickets with related complaint data, sorted by newest first
    tickets = Ticket.objects.select_related('complaint').order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(complaint__priority=priority_filter)

    # Calculate statistics
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='open').count()
    in_progress_tickets = tickets.filter(status='in_progress').count()
    escalated_tickets = tickets.filter(status='escalated').count()
    closed_tickets = tickets.filter(status='closed').count()

    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'escalated_tickets': escalated_tickets,
        'closed_tickets': closed_tickets,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    }
    return render(request, 'tickets/dashboard.html', context)


def update_ticket(request, ticket_id):
    """Update ticket status and assigned staff member.

    Args:
        ticket_id: Unique ticket identifier (e.g., HDP-001)

    Allows staff to:
    - Change ticket status (Open, In Progress, Closed)
    - Assign the ticket to a staff member
    """
    ticket = get_object_or_404(Ticket, unique_ticket_id=ticket_id)

    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            messages.success(
                request,
                f'Ticket <strong>{updated_ticket.unique_ticket_id}</strong> has been updated successfully!'
            )
            return redirect('tickets:dashboard')
    else:
        form = TicketUpdateForm(instance=ticket)

    context = {
        'form': form,
        'ticket': ticket,
    }
    return render(request, 'tickets/ticket_update.html', context)


def escalate_ticket(request, ticket_id):
    """Escalate a ticket to higher priority handling.

    Args:
        ticket_id: Unique ticket identifier (e.g., HDP-001)

    Marks the ticket as escalated, tracks when and by whom,
    and redirects back to dashboard.
    """
    ticket = get_object_or_404(Ticket, unique_ticket_id=ticket_id)

    if ticket.status == 'closed':
        messages.error(
            request,
            f'Cannot escalate closed ticket <strong>{ticket.unique_ticket_id}</strong>.'
        )
        return redirect('tickets:dashboard')

    # Escalate the ticket
    ticket.escalate(escalated_by='Admin')

    messages.success(
        request,
        f'Ticket <strong>{ticket.unique_ticket_id}</strong> has been escalated successfully! '
        f'Escalated at: {ticket.escalated_at|date:"H:i on M d, Y"}'
    )
    return redirect('tickets:dashboard')


def feedback(request, ticket_id=None):
    """Handle feedback submission for a ticket.

    Args:
        ticket_id: Optional ticket ID. If provided, pre-fills the ticket.

    Users can:
    - Enter a ticket ID manually
    - Submit rating (1-5 stars) and comments
    - Only closed tickets can receive feedback
    """
    ticket = None
    if ticket_id:
        ticket = get_object_or_404(Ticket, unique_ticket_id=ticket_id)

    if request.method == 'POST':
        # Get ticket from form data
        ticket_id_from_form = request.POST.get('ticket_id')
        if not ticket_id_from_form:
            messages.error(request, 'Please enter a Ticket ID.')
            return redirect('tickets:feedback')

        ticket = get_object_or_404(Ticket, unique_ticket_id=ticket_id_from_form)

        # Check if feedback already exists
        if hasattr(ticket, 'feedback'):
            messages.error(
                request,
                f'Feedback has already been submitted for ticket <strong>{ticket.unique_ticket_id}</strong>.'
            )
            return redirect('tickets:feedback', ticket_id=ticket.unique_ticket_id)

        # Check if ticket is closed
        if ticket.status != 'closed':
            messages.error(
                request,
                f'Feedback can only be submitted for closed tickets. '
                f'Ticket <strong>{ticket.unique_ticket_id}</strong> is currently {ticket.get_status_display()}.'
            )
            return redirect('tickets:feedback', ticket_id=ticket.unique_ticket_id)

        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.ticket = ticket
            feedback.save()

            messages.success(
                request,
                f'Thank you for your feedback on ticket <strong>{ticket.unique_ticket_id}</strong>! '
                f'Your rating: {feedback.get_stars()}'
            )
            return redirect('tickets:home')

    else:
        form = FeedbackForm()

    context = {
        'form': form,
        'ticket': ticket,
    }
    return render(request, 'tickets/feedback.html', context)


def analytics(request):
    """Display ticket analytics and statistics.

    Shows:
    - Total number of tickets
    - Resolved (closed) tickets
    - Open tickets
    - In progress tickets
    - Escalated tickets
    - Average customer rating from feedback
    """
    from django.db.models import Avg, Count

    # Get all tickets
    all_tickets = Ticket.objects.all()

    # Calculate ticket statistics
    total_tickets = all_tickets.count()
    open_tickets = all_tickets.filter(status='open').count()
    in_progress_tickets = all_tickets.filter(status='in_progress').count()
    escalated_tickets = all_tickets.filter(status='escalated').count()
    resolved_tickets = all_tickets.filter(status='closed').count()

    # Calculate percentages
    if total_tickets > 0:
        open_percentage = round((open_tickets / total_tickets) * 100, 1)
        resolved_percentage = round((resolved_tickets / total_tickets) * 100, 1)
        in_progress_percentage = round((in_progress_tickets / total_tickets) * 100, 1)
        escalated_percentage = round((escalated_tickets / total_tickets) * 100, 1)
    else:
        open_percentage = resolved_percentage = in_progress_percentage = escalated_percentage = 0

    # Feedback statistics
    feedback_count = Feedback.objects.count()
    avg_rating = Feedback.objects.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0

    # Category breakdown
    category_stats = (
        Complaint.objects.values('category')
        .annotate(count=Count('tickets'))
        .order_by('-count')
    )

    # Priority breakdown
    priority_stats = (
        Complaint.objects.values('priority')
        .annotate(count=Count('tickets'))
        .order_by('-count')
    )

    # Recent activity (last 5 tickets)
    recent_tickets = Ticket.objects.select_related('complaint').order_by('-updated_at')[:5]

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'escalated_tickets': escalated_tickets,
        'resolved_tickets': resolved_tickets,
        'open_percentage': open_percentage,
        'resolved_percentage': resolved_percentage,
        'in_progress_percentage': in_progress_percentage,
        'escalated_percentage': escalated_percentage,
        'feedback_count': feedback_count,
        'avg_rating': avg_rating,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'tickets/analytics.html', context)
