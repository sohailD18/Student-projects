"""
Views for CRM Activities app
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Activity
from contacts.models import Contact, Company
from deals.models import Deal


@login_required
def activity_list(request):
    activities = Activity.objects.all()
    
    activity_type = request.GET.get('type')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    if status:
        activities = activities.filter(status=status)
    if priority:
        activities = activities.filter(priority=priority)
    
    upcoming = activities.filter(
        due_date__gte=timezone.now().date(),
        status='PENDING'
    ).order_by('due_date')
    
    overdue = Activity.objects.filter(
        due_date__lt=timezone.now().date(),
        status='PENDING'
    )
    
    completed = activities.filter(status='COMPLETED')
    
    return render(request, 'activities/activity_list.html', {
        'activities': activities[:50],
        'upcoming': upcoming[:10],
        'overdue': overdue,
        'type_choices': Activity.TYPE_CHOICES,
        'status_choices': Activity.STATUS_CHOICES,
        'priority_choices': Activity.PRIORITY_CHOICES,
    })


@login_required
def activity_calendar(request):
    activities = Activity.objects.filter(
        activity_date__month=timezone.now().month,
        activity_date__year=timezone.now().year
    )
    
    events = []
    for activity in activities:
        events.append({
            'id': activity.id,
            'title': activity.subject,
            'start': activity.activity_date.isoformat(),
            'type': activity.activity_type,
            'status': activity.status,
        })
    
    return render(request, 'activities/activity_calendar.html', {
        'activities': activities,
        'events_json': events,
    })


class ActivityCreateView(CreateView):
    model = Activity
    template_name = 'activities/activity_form.html'
    fields = [
        'activity_type', 'contact', 'company', 'deal', 'subject', 'description',
        'activity_date', 'due_date', 'duration', 'priority', 'status',
        'is_reminder', 'reminder_date', 'outcome'
    ]
    success_url = reverse_lazy('activity_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['activity_date'] = timezone.now()
        
        contact_id = self.request.GET.get('contact')
        deal_id = self.request.GET.get('deal')
        
        if contact_id:
            initial['contact'] = contact_id
        if deal_id:
            initial['deal'] = deal_id
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['companies'] = Company.objects.all()
        context['deals'] = Deal.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ActivityUpdateView(UpdateView):
    model = Activity
    template_name = 'activities/activity_form.html'
    fields = [
        'activity_type', 'contact', 'company', 'deal', 'subject', 'description',
        'activity_date', 'due_date', 'duration', 'priority', 'status',
        'is_reminder', 'reminder_date', 'outcome'
    ]
    success_url = reverse_lazy('activity_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['companies'] = Company.objects.all()
        context['deals'] = Deal.objects.filter(is_active=True)
        return context


class ActivityDeleteView(DeleteView):
    model = Activity
    template_name = 'activities/activity_confirm_delete.html'
    success_url = reverse_lazy('activity_list')


@require_POST
@login_required
def complete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    activity.status = 'COMPLETED'
    activity.save()
    return JsonResponse({'success': True})


@require_POST
@login_required
def quick_activity(request):
    activity_type = request.POST.get('activity_type')
    subject = request.POST.get('subject')
    description = request.POST.get('description', '')
    
    contact_id = request.POST.get('contact')
    deal_id = request.POST.get('deal')
    
    contact = None
    deal = None
    
    if contact_id:
        contact = get_object_or_404(Contact, id=contact_id)
    if deal_id:
        deal = get_object_or_404(Deal, id=deal_id)
    
    Activity.objects.create(
        user=request.user,
        activity_type=activity_type,
        contact=contact,
        deal=deal,
        subject=subject,
        description=description,
        status='COMPLETED'
    )
    
    return redirect('activity_list')


@login_required
def task_list(request):
    tasks = Activity.objects.filter(activity_type='TASK').order_by('due_date', 'priority')
    
    pending_tasks = tasks.filter(status='PENDING')
    completed_tasks = tasks.filter(status='COMPLETED')
    
    return render(request, 'activities/task_list.html', {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
    })


@login_required
def activity_feed(request):
    activities = Activity.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    
    return render(request, 'activities/activity_feed.html', {
        'activities': activities,
    })
