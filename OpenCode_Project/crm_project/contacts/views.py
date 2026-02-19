"""
Views for CRM Contacts app
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Company, Contact, Tag


@login_required
def dashboard(request):
    total_contacts = Contact.objects.count()
    total_companies = Company.objects.count()
    
    recent_contacts = Contact.objects.order_by('-created_at')[:5]
    recent_companies = Company.objects.order_by('-created_at')[:5]
    
    contacts_by_status = {
        'lead': Contact.objects.filter(status='LEAD').count(),
        'prospect': Contact.objects.filter(status='PROSPECT').count(),
        'customer': Contact.objects.filter(status='CUSTOMER').count(),
    }
    
    return render(request, 'contacts/dashboard.html', {
        'total_contacts': total_contacts,
        'total_companies': total_companies,
        'recent_contacts': recent_contacts,
        'recent_companies': recent_companies,
        'contacts_by_status': contacts_by_status,
    })


class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def get_queryset(self):
        contacts = Contact.objects.all()
        
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        company = self.request.GET.get('company')
        source = self.request.GET.get('source')
        
        if search:
            contacts = contacts.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(company__name__icontains=search)
            )
        if status:
            contacts = contacts.filter(status=status)
        if company:
            contacts = contacts.filter(company_id=company)
        if source:
            contacts = contacts.filter(source=source)
        
        return contacts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        context['status_choices'] = Contact.STATUS_CHOICES
        return context


class ContactDetailView(DetailView):
    model = Contact
    template_name = 'contacts/contact_detail.html'
    context_object_name = 'contact'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = self.object.activity_set.order_by('-created_at')[:10]
        context['deals'] = self.object.deals.order_by('-created_at')[:5]
        return context


class ContactCreateView(CreateView):
    model = Contact
    template_name = 'contacts/contact_form.html'
    fields = [
        'company', 'salutation', 'first_name', 'last_name', 'email', 'phone',
        'mobile', 'job_title', 'department', 'status', 'source', 'address',
        'city', 'state', 'country', 'postal_code', 'linkedin', 'twitter', 'notes', 'tags'
    ]
    success_url = reverse_lazy('contact_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ContactUpdateView(UpdateView):
    model = Contact
    template_name = 'contacts/contact_form.html'
    fields = [
        'company', 'salutation', 'first_name', 'last_name', 'email', 'phone',
        'mobile', 'job_title', 'department', 'status', 'source', 'address',
        'city', 'state', 'country', 'postal_code', 'linkedin', 'twitter', 'notes', 'tags'
    ]
    success_url = reverse_lazy('contact_list')


class ContactDeleteView(DeleteView):
    model = Contact
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')


class CompanyListView(ListView):
    model = Company
    template_name = 'contacts/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        companies = Company.objects.all()
        
        search = self.request.GET.get('q')
        industry = self.request.GET.get('industry')
        
        if search:
            companies = companies.filter(name__icontains=search)
        if industry:
            companies = companies.filter(industry=industry)
        
        return companies
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['industry_choices'] = Company.INDUSTRY_CHOICES
        return context


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'contacts/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.object.contacts.order_by('-created_at')[:10]
        context['deals'] = self.object.deals.order_by('-created_at')[:5]
        return context


class CompanyCreateView(CreateView):
    model = Company
    template_name = 'contacts/company_form.html'
    fields = [
        'name', 'logo', 'industry', 'company_size', 'website', 'email', 'phone',
        'address', 'city', 'state', 'country', 'linkedin', 'twitter', 'description'
    ]
    success_url = reverse_lazy('company_list')


class CompanyUpdateView(UpdateView):
    model = Company
    template_name = 'contacts/company_form.html'
    fields = [
        'name', 'logo', 'industry', 'company_size', 'website', 'email', 'phone',
        'address', 'city', 'state', 'country', 'linkedin', 'twitter', 'description'
    ]
    success_url = reverse_lazy('company_list')


class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'contacts/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')


@require_POST
@login_required
def update_last_contacted(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.last_contacted_at = timezone.now()
    contact.save()
    return JsonResponse({'success': True})
