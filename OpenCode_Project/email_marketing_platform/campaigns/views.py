from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import EmailList, Subscriber, EmailTemplate, Campaign, EmailLog, EmailAnalytics, Link
from .forms import (EmailListForm, SubscriberForm, BulkImportSubscribersForm,
                    EmailTemplateForm, CampaignForm, ABTestCampaignForm)


# ==================== Authentication Views ====================
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'campaigns/signup.html', {'form': form})


from django.contrib.auth import logout as auth_logout


def logout(request):
    auth_logout(request)
    return redirect('login')


# ==================== Dashboard ====================
@login_required
def dashboard(request):
    total_campaigns = Campaign.objects.count()
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    total_emails_sent = EmailLog.objects.filter(status='sent').count()
    total_opens = EmailAnalytics.objects.filter(opened_at__isnull=False).count()

    recent_campaigns = Campaign.objects.all()[:5]
    recent_subscribers = Subscriber.objects.all()[:5]

    context = {
        'total_campaigns': total_campaigns,
        'total_subscribers': total_subscribers,
        'total_emails_sent': total_emails_sent,
        'total_opens': total_opens,
        'recent_campaigns': recent_campaigns,
        'recent_subscribers': recent_subscribers,
    }
    return render(request, 'campaigns/dashboard.html', context)


# ==================== Email List Views ====================
@login_required
def email_list_list(request):
    lists = EmailList.objects.all()
    paginator = Paginator(lists, 10)
    page = request.GET.get('page')
    lists_page = paginator.get_page(page)
    return render(request, 'campaigns/email_list_list.html', {'lists': lists_page})


@login_required
def email_list_create(request):
    if request.method == 'POST':
        form = EmailListForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email list created successfully!')
            return redirect('campaigns:email_list_list')
    else:
        form = EmailListForm()
    return render(request, 'campaigns/email_list_form.html', {'form': form, 'action': 'Create'})


@login_required
def email_list_detail(request, pk):
    email_list = get_object_or_404(EmailList, pk=pk)
    subscribers = email_list.subscribers.filter(is_active=True)
    context = {
        'email_list': email_list,
        'subscribers': subscribers,
    }
    return render(request, 'campaigns/email_list_detail.html', context)


@login_required
def email_list_delete(request, pk):
    email_list = get_object_or_404(EmailList, pk=pk)
    if request.method == 'POST':
        email_list.delete()
        messages.success(request, 'Email list deleted successfully!')
        return redirect('campaigns:email_list_list')
    return render(request, 'campaigns/email_list_confirm_delete.html', {'email_list': email_list})


# ==================== Subscriber Views ====================
@login_required
def subscriber_list(request):
    subscribers = Subscriber.objects.all()
    search = request.GET.get('search')
    status_filter = request.GET.get('status')

    if search:
        subscribers = subscribers.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    if status_filter:
        subscribers = subscribers.filter(status=status_filter)

    paginator = Paginator(subscribers, 20)
    page = request.GET.get('page')
    subscribers_page = paginator.get_page(page)

    context = {
        'subscribers': subscribers_page,
        'search': search or '',
        'status_filter': status_filter or '',
    }
    return render(request, 'campaigns/subscriber_list.html', context)


@login_required
def subscriber_create(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscriber added successfully!')
            return redirect('campaigns:subscriber_list')
    else:
        form = SubscriberForm()
    return render(request, 'campaigns/subscriber_form.html', {'form': form, 'action': 'Add'})


@login_required
def subscriber_import(request):
    if request.method == 'POST':
        form = BulkImportSubscribersForm(request.POST)
        if form.is_valid():
            csv_data = form.cleaned_data['csv_data']
            email_list = form.cleaned_data['email_list']

            lines = csv_data.strip().split('\n')
            imported = 0
            errors = []

            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 1 and parts[0]:
                    try:
                        email = parts[0]
                        first_name = parts[1] if len(parts) > 1 else ''
                        last_name = parts[2] if len(parts) > 2 else ''

                        subscriber, created = Subscriber.objects.update_or_create(
                            email=email,
                            defaults={
                                'first_name': first_name,
                                'last_name': last_name,
                                'status': 'active'
                            }
                        )
                        subscriber.email_list.add(email_list)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Error importing {parts[0]}: {str(e)}")

            if imported > 0:
                messages.success(request, f'{imported} subscribers imported successfully!')
            if errors:
                messages.warning(request, f'Errors: {", ".join(errors[:5])}')
            return redirect('campaigns:subscriber_list')
    else:
        form = BulkImportSubscribersForm()
    return render(request, 'campaigns/subscriber_import.html', {'form': form})


@login_required
def subscriber_delete(request, pk):
    subscriber = get_object_or_404(Subscriber, pk=pk)
    if request.method == 'POST':
        subscriber.delete()
        messages.success(request, 'Subscriber deleted successfully!')
        return redirect('campaigns:subscriber_list')
    return render(request, 'campaigns/subscriber_confirm_delete.html', {'subscriber': subscriber})


# ==================== Email Template Views ====================
@login_required
def template_list(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'campaigns/template_list.html', {'templates': templates})


@login_required
def template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template created successfully!')
            return redirect('campaigns:template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'campaigns/template_form.html', {'form': form, 'action': 'Create'})


@login_required
def template_detail(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    return render(request, 'campaigns/template_detail.html', {'template': template})


@login_required
def template_edit(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template updated successfully!')
            return redirect('campaigns:template_detail', pk=template.pk)
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'campaigns/template_form.html', {'form': form, 'action': 'Edit', 'template': template})


@login_required
def template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Template deleted successfully!')
        return redirect('campaigns:template_list')
    return render(request, 'campaigns/template_confirm_delete.html', {'template': template})


# ==================== Campaign Views ====================
@login_required
def campaign_list(request):
    campaigns = Campaign.objects.select_related('email_template', 'email_list').all()
    paginator = Paginator(campaigns, 10)
    page = request.GET.get('page')
    campaigns_page = paginator.get_page(page)
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns_page})


@login_required
def campaign_create(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.status = 'draft'
            campaign.save()
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaigns:campaign_detail', pk=campaign.pk)
    else:
        form = CampaignForm()
    return render(request, 'campaigns/campaign_form.html', {'form': form, 'action': 'Create'})


@login_required
def campaign_ab_test_create(request):
    if request.method == 'POST':
        form = ABTestCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.status = 'draft'
            campaign.is_ab_test = True
            campaign.save()
            messages.success(request, 'A/B Test Campaign created successfully!')
            return redirect('campaigns:campaign_detail', pk=campaign.pk)
    else:
        form = ABTestCampaignForm()
    return render(request, 'campaigns/campaign_ab_test_form.html', {'form': form, 'action': 'Create'})


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    email_logs = campaign.logs.select_related('subscriber').all()[:20]
    context = {
        'campaign': campaign,
        'email_logs': email_logs,
    }
    return render(request, 'campaigns/campaign_detail.html', context)


@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully!')
            return redirect('campaigns:campaign_detail', pk=campaign.pk)
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'campaigns/campaign_form.html', {'form': form, 'action': 'Edit', 'campaign': campaign})


@login_required
def campaign_send(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if campaign.status in ['sent', 'sending']:
        messages.warning(request, 'This campaign has already been sent!')
        return redirect('campaigns:campaign_detail', pk=campaign.pk)

    if request.method == 'POST':
        # Get all active subscribers from the email list
        subscribers = campaign.email_list.subscribers.filter(is_active=True)

        # Create email logs for all subscribers
        email_logs = []
        for subscriber in subscribers:
            if campaign.is_ab_test:
                # Assign variant for A/B testing
                import random
                variant = 'A' if random.random() < (campaign.ab_test_split_percentage / 100) else 'B'
            else:
                variant = None

            log = EmailLog(
                campaign=campaign,
                subscriber=subscriber,
                status='pending',
                variant=variant
            )
            email_logs.append(log)

        EmailLog.objects.bulk_create(email_logs)

        # Update campaign status
        campaign.status = 'scheduled'
        campaign.save()

        messages.success(request, f'{len(email_logs)} emails scheduled for sending!')
        return redirect('campaigns:campaign_detail', pk=campaign.pk)

    return render(request, 'campaigns/campaign_confirm_send.html', {'campaign': campaign})


@login_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        return redirect('campaigns:campaign_list')
    return render(request, 'campaigns/campaign_confirm_delete.html', {'campaign': campaign})


# ==================== Analytics Views ====================
@login_required
def campaign_analytics(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    # Get analytics data
    total_sent = campaign.total_sent
    total_opens = campaign.total_opens
    total_clicks = campaign.total_clicks
    open_rate = campaign.open_rate
    click_rate = campaign.click_rate

    # Get email logs with analytics
    email_logs = campaign.logs.select_related('subscriber', 'analytics').all()

    # Variant comparison for A/B tests
    variant_stats = None
    if campaign.is_ab_test:
        variant_a_logs = email_logs.filter(variant='A')
        variant_b_logs = email_logs.filter(variant='B')

        variant_stats = {
            'A': {
                'sent': variant_a_logs.filter(status='sent').count(),
                'opens': variant_a_logs.filter(analytics__opened_at__isnull=False).count(),
                'clicks': variant_a_logs.filter(analytics__clicked_at__isnull=False).count(),
            },
            'B': {
                'sent': variant_b_logs.filter(status='sent').count(),
                'opens': variant_b_logs.filter(analytics__opened_at__isnull=False).count(),
                'clicks': variant_b_logs.filter(analytics__clicked_at__isnull=False).count(),
            }
        }

    context = {
        'campaign': campaign,
        'total_sent': total_sent,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'open_rate': open_rate,
        'click_rate': click_rate,
        'email_logs': email_logs[:20],
        'variant_stats': variant_stats,
    }
    return render(request, 'campaigns/campaign_analytics.html', context)


@login_required
def ab_test_winner(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if not campaign.is_ab_test:
        messages.warning(request, 'This is not an A/B test campaign!')
        return redirect('campaigns:campaign_detail', pk=campaign.pk)

    if request.method == 'POST':
        variant = request.POST.get('variant')
        if variant in ['A', 'B']:
            campaign.ab_test_winner = variant
            campaign.save()
            messages.success(request, f'Variant {variant} selected as winner!')
            return redirect('campaigns:campaign_analytics', pk=campaign.pk)

    return render(request, 'campaigns/ab_test_winner.html', {'campaign': campaign})
