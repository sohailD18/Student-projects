"""
Views for the Meeting Analyzer application.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import month_name
import json

from .models import Meeting, ActionItem, AnalysisResult, MeetingReport
from .utils import MeetingAnalyzer


def dashboard_view(request):
    """
    Dashboard view showing analytics and charts.
    """
    # Get all meetings
    meetings = Meeting.objects.all()

    # Calculate basic stats
    total_meetings = meetings.count()
    total_action_items = ActionItem.objects.count()
    completed_action_items = ActionItem.objects.filter(status='Done').count()
    pending_action_items = total_action_items - completed_action_items

    # Average productivity score
    avg_productivity = AnalysisResult.objects.aggregate(
        avg_score=Avg('productivity_score')
    )['avg_score'] or 0

    # Recent meetings (last 5)
    recent_meetings = meetings[:5]

    # Monthly meeting data for chart (last 6 months)
    monthly_data = []
    month_labels = []
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30*i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        count = meetings.filter(date__range=[month_start, month_end]).count()
        monthly_data.append(count)
        month_labels.append(month_start.strftime('%b %Y'))

    # Productivity trend (last 7 meetings with analysis)
    productivity_trend = []
    productivity_labels = []
    recent_analyzed = meetings.filter(
        analysis_result__isnull=False
    ).order_by('-date')[:7][::-1]

    for meeting in recent_analyzed:
        productivity_trend.append(meeting.analysis_result.productivity_score)
        productivity_labels.append(meeting.date.strftime('%b %d'))

    # Action item status distribution
    action_status_data = [
        ActionItem.objects.filter(status='Pending').count(),
        ActionItem.objects.filter(status='Done').count(),
    ]

    # Sentiment distribution
    sentiment_data = [
        AnalysisResult.objects.filter(sentiment='Positive').count(),
        AnalysisResult.objects.filter(sentiment='Neutral').count(),
        AnalysisResult.objects.filter(sentiment='Negative').count(),
    ]

    context = {
        'total_meetings': total_meetings,
        'total_action_items': total_action_items,
        'completed_action_items': completed_action_items,
        'pending_action_items': pending_action_items,
        'avg_productivity': round(avg_productivity, 1),
        'recent_meetings': recent_meetings,
        'monthly_data': json.dumps(monthly_data),
        'month_labels': json.dumps(month_labels),
        'productivity_trend': json.dumps(productivity_trend),
        'productivity_labels': json.dumps(productivity_labels),
        'action_status_data': json.dumps(action_status_data),
        'sentiment_data': json.dumps(sentiment_data),
    }

    return render(request, 'meetings/dashboard.html', context)


def meeting_list_view(request):
    """
    List all meetings with filtering and search.
    """
    meetings = Meeting.objects.all()
    query = request.GET.get('q')

    if query:
        meetings = meetings.filter(
            Q(title__icontains=query) |
            Q(participants__icontains=query)
        )

    context = {
        'meetings': meetings,
        'query': query or '',
    }

    return render(request, 'meetings/meeting_list.html', context)


def meeting_detail_view(request, pk):
    """
    Show meeting details and run AI analysis if needed.
    """
    meeting = get_object_or_404(Meeting, pk=pk)

    # Check if analysis exists, if not, run it
    analysis = None
    if not hasattr(meeting, 'analysis_result') and meeting.transcript:
        # Run the AI analysis
        analyzer = MeetingAnalyzer(meeting.transcript, meeting.duration)
        results = analyzer.analyze_complete()

        # Create analysis result
        analysis = AnalysisResult.objects.create(
            meeting=meeting,
            summary=results['summary'],
            sentiment=results['sentiment'],
            sentiment_score=results['sentiment_score'],
            productivity_score=results['productivity_score'],
            word_count=results['word_count'],
            action_items_extracted=results['action_items_count'],
            keywords=', '.join(results['keywords']),
            follow_up_recommendations=results['follow_up_recommendations']
        )

        # Create action items
        for item in results['action_items']:
            ActionItem.objects.create(
                meeting=meeting,
                description=item['description'],
                assignee=item['assignee']
            )
    elif hasattr(meeting, 'analysis_result'):
        analysis = meeting.analysis_result

    action_items = meeting.action_items.all()

    # Handle action item status update
    if request.method == 'POST' and 'action_item_id' in request.POST:
        action_item = get_object_or_404(ActionItem, pk=request.POST['action_item_id'])
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Done']:
            action_item.status = new_status
            action_item.save()
            messages.success(request, f'Action item updated to {new_status}.')
        return redirect('meeting_detail', pk=pk)

    context = {
        'meeting': meeting,
        'analysis': analysis,
        'action_items': action_items,
        'sentiment_class': 'success' if analysis and analysis.sentiment == 'Positive' else
                          'danger' if analysis and analysis.sentiment == 'Negative' else
                          'secondary',
    }

    return render(request, 'meetings/meeting_detail.html', context)


def create_meeting_view(request):
    """
    Create a new meeting.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        duration = request.POST.get('duration')
        participants = request.POST.get('participants')
        transcript = request.POST.get('transcript', '')

        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not date_str:
            errors.append('Date is required.')
        if not time_str:
            errors.append('Time is required.')
        if not duration:
            errors.append('Duration is required.')
        if not participants:
            errors.append('At least one participant is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'meetings/create_meeting.html', {
                'title': title,
                'date': date_str,
                'time': time_str,
                'duration': duration,
                'participants': participants,
                'transcript': transcript,
            })

        # Parse date and time
        try:
            datetime_obj = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
            duration = int(duration)
        except ValueError:
            messages.error(request, 'Invalid date/time format.')
            return render(request, 'meetings/create_meeting.html', {
                'title': title,
                'date': date_str,
                'time': time_str,
                'duration': duration,
                'participants': participants,
                'transcript': transcript,
            })

        # Create meeting
        meeting = Meeting.objects.create(
            title=title,
            date=datetime_obj,
            duration=duration,
            participants=participants,
            transcript=transcript
        )

        messages.success(request, f'Meeting "{title}" created successfully!')

        # If transcript provided, run analysis immediately
        if transcript.strip():
            return redirect('meeting_detail', pk=meeting.pk)
        else:
            return redirect('meeting_list')

    return render(request, 'meetings/create_meeting.html')


def delete_meeting_view(request, pk):
    """
    Delete a meeting.
    """
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        title = meeting.title
        meeting.delete()
        messages.success(request, f'Meeting "{title}" deleted successfully.')
        return redirect('meeting_list')

    return render(request, 'meetings/delete_meeting.html', {'meeting': meeting})


def analytics_view(request):
    """
    Detailed analytics view with reports.
    """
    meetings = Meeting.objects.all()

    # Meeting statistics
    total_duration = meetings.aggregate(total=Sum('duration'))['total'] or 0
    avg_duration = meetings.aggregate(avg=Avg('duration'))['avg'] or 0

    # Top productive meetings
    top_productive = AnalysisResult.objects.order_by('-productivity_score')[:5]

    # Meetings by sentiment
    positive_meetings = meetings.filter(analysis_result__sentiment='Positive').count()
    neutral_meetings = meetings.filter(analysis_result__sentiment='Neutral').count()
    negative_meetings = meetings.filter(analysis_result__sentiment='Negative').count()

    # Recent activity
    recent_meetings = meetings.order_by('-created_at')[:10]

    context = {
        'meetings': meetings,
        'total_duration': total_duration,
        'avg_duration': round(avg_duration, 1),
        'top_productive': top_productive,
        'positive_meetings': positive_meetings,
        'neutral_meetings': neutral_meetings,
        'negative_meetings': negative_meetings,
        'recent_meetings': recent_meetings,
    }

    return render(request, 'meetings/analytics.html', context)


def rerun_analysis_view(request, pk):
    """
    Re-run AI analysis for a meeting.
    """
    meeting = get_object_or_404(Meeting, pk=pk)

    if not meeting.transcript:
        messages.warning(request, 'Cannot analyze: No transcript available.')
        return redirect('meeting_detail', pk=pk)

    # Delete existing analysis and action items
    if hasattr(meeting, 'analysis_result'):
        meeting.analysis_result.delete()
    meeting.action_items.all().delete()

    # Run new analysis
    analyzer = MeetingAnalyzer(meeting.transcript, meeting.duration)
    results = analyzer.analyze_complete()

    # Create new analysis result
    AnalysisResult.objects.create(
        meeting=meeting,
        summary=results['summary'],
        sentiment=results['sentiment'],
        sentiment_score=results['sentiment_score'],
        productivity_score=results['productivity_score'],
        word_count=results['word_count'],
        action_items_extracted=results['action_items_count'],
        keywords=', '.join(results['keywords']),
        follow_up_recommendations=results['follow_up_recommendations']
    )

    # Create action items
    for item in results['action_items']:
        ActionItem.objects.create(
            meeting=meeting,
            description=item['description'],
            assignee=item['assignee']
        )

    messages.success(request, 'Analysis re-run successfully!')

    return redirect('meeting_detail', pk=pk)


from django.db.models import Sum, Avg
