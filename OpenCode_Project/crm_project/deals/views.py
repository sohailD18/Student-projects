"""
Views for CRM Deals app
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
from .models import Deal, Pipeline, PipelineStage, DealActivity
from contacts.models import Contact, Company


@login_required
def deal_list(request):
    deals = Deal.objects.filter(is_active=True)
    
    search = request.GET.get('q')
    stage = request.GET.get('stage')
    priority = request.GET.get('priority')
    source = request.GET.get('source')
    
    if search:
        deals = deals.filter(title__icontains=search)
    if stage:
        deals = deals.filter(stage_id=stage)
    if priority:
        deals = deals.filter(priority=priority)
    if source:
        deals = deals.filter(source=source)
    
    total_value = deals.aggregate(total=Sum('value'))['total'] or Decimal('0')
    
    return render(request, 'deals/deal_list.html', {
        'deals': deals,
        'total_value': total_value,
        'stages': PipelineStage.objects.all(),
    })


@login_required
def deal_kanban(request):
    deals = Deal.objects.filter(is_active=True).select_related('contact', 'company', 'stage')
    
    stages = PipelineStage.objects.filter(pipeline__is_default=True).order_by('order')
    
    deals_by_stage = {}
    for stage in stages:
        deals_by_stage[stage.id] = deals.filter(stage_id=stage.id)
    
    return render(request, 'deals/deal_kanban.html', {
        'stages': stages,
        'deals_by_stage': deals_by_stage,
    })


@require_POST
@login_required
def update_deal_stage(request):
    deal_id = request.POST.get('deal_id')
    stage_id = request.POST.get('stage_id')
    
    deal = get_object_or_404(Deal, id=deal_id)
    stage = get_object_or_404(PipelineStage, id=stage_id)
    
    old_stage = deal.stage
    deal.stage = stage
    deal.save()
    
    if stage.is_won:
        deal.actual_close_date = timezone.now().date()
        deal.is_active = False
        deal.save()
    elif stage.is_lost:
        deal.actual_close_date = timezone.now().date()
        deal.is_active = False
        deal.save()
    
    DealActivity.objects.create(
        deal=deal,
        activity_type='STAGE_CHANGE',
        description=f"Moved from {old_stage.name} to {stage.name}",
        created_by=request.user
    )
    
    return JsonResponse({'success': True})


class DealDetailView(DetailView):
    model = Deal
    template_name = 'deals/deal_detail.html'
    context_object_name = 'deal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = self.object.deal_activities.order_by('-activity_date')
        return context


class DealCreateView(CreateView):
    model = Deal
    template_name = 'deals/deal_form.html'
    fields = [
        'contact', 'company', 'title', 'description', 'pipeline', 'stage',
        'value', 'source', 'priority', 'expected_close_date'
    ]
    success_url = reverse_lazy('deal_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['pipeline'] = Pipeline.objects.filter(is_default=True).first()
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['companies'] = Company.objects.all()
        context['pipelines'] = Pipeline.objects.all()
        context['stages'] = PipelineStage.objects.filter(pipeline__is_default=True)
        return context


class DealUpdateView(UpdateView):
    model = Deal
    template_name = 'deals/deal_form.html'
    fields = [
        'contact', 'company', 'title', 'description', 'pipeline', 'stage',
        'value', 'source', 'priority', 'expected_close_date'
    ]
    success_url = reverse_lazy('deal_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['companies'] = Company.objects.all()
        context['pipelines'] = Pipeline.objects.all()
        context['stages'] = PipelineStage.objects.filter(pipeline__is_default=True)
        return context


class DealDeleteView(DeleteView):
    model = Deal
    template_name = 'deals/deal_confirm_delete.html'
    success_url = reverse_lazy('deal_list')


@login_required
def deal_pipeline_setup(request):
    pipelines = Pipeline.objects.prefetch_related('stages').all()
    return render(request, 'deals/pipeline_setup.html', {'pipelines': pipelines})


@login_required
def reports(request):
    deals = Deal.objects.filter(is_active=True)
    
    total_value = deals.aggregate(total=Sum('value'))['total'] or Decimal('0')
    total_count = deals.count()
    avg_deal_size = (total_value / total_count) if total_count > 0 else Decimal('0')
    
    value_by_stage = Deal.objects.filter(
        is_active=True,
        stage__isnull=False
    ).values('stage__name').annotate(
        total=Sum('value'),
        count=Count('id')
    ).order_by('stage__order')
    
    value_by_priority = Deal.objects.filter(is_active=True).values('priority').annotate(
        total=Sum('value'),
        count=Count('id')
    )
    
    won_deals = Deal.objects.filter(stage__is_won=True)
    lost_deals = Deal.objects.filter(stage__is_lost=True)
    
    won_value = won_deals.aggregate(total=Sum('value'))['total'] or Decimal('0')
    lost_value = lost_deals.aggregate(total=Sum('value'))['total'] or Decimal('0')
    
    return render(request, 'deals/reports.html', {
        'total_value': total_value,
        'total_count': total_count,
        'avg_deal_size': avg_deal_size,
        'value_by_stage': value_by_stage,
        'value_by_priority': value_by_priority,
        'won_value': won_value,
        'won_count': won_deals.count(),
        'lost_value': lost_value,
        'lost_count': lost_deals.count(),
    })
