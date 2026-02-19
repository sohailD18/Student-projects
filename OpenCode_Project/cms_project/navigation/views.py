from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Navigation, NavigationItem, FooterLink
from .forms import NavigationForm, NavigationItemForm, FooterLinkForm


class NavigationListView(LoginRequiredMixin, ListView):
    model = Navigation
    template_name = 'navigation/navigation_list.html'
    context_object_name = 'navigations'


class NavigationDetailView(LoginRequiredMixin, DetailView):
    model = Navigation
    template_name = 'navigation/navigation_detail.html'
    context_object_name = 'navigation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_items'] = self.object.menu_items
        return context


class NavigationCreateView(LoginRequiredMixin, CreateView):
    model = Navigation
    form_class = NavigationForm
    template_name = 'navigation/navigation_form.html'
    success_url = reverse_lazy('navigation_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class NavigationUpdateView(LoginRequiredMixin, UpdateView):
    model = Navigation
    form_class = NavigationForm
    template_name = 'navigation/navigation_form.html'
    success_url = reverse_lazy('navigation_list')


class NavigationDeleteView(LoginRequiredMixin, DeleteView):
    model = Navigation
    template_name = 'navigation/navigation_confirm_delete.html'
    success_url = reverse_lazy('navigation_list')


class NavigationItemCreateView(LoginRequiredMixin, CreateView):
    model = NavigationItem
    form_class = NavigationItemForm
    template_name = 'navigation/navigation_item_form.html'
    
    def get_success_url(self):
        return reverse_lazy('navigation_detail', kwargs={'pk': self.object.navigation.pk})


class NavigationItemUpdateView(LoginRequiredMixin, UpdateView):
    model = NavigationItem
    form_class = NavigationItemForm
    template_name = 'navigation/navigation_item_form.html'
    
    def get_success_url(self):
        return reverse_lazy('navigation_detail', kwargs={'pk': self.object.navigation.pk})


class NavigationItemDeleteView(LoginRequiredMixin, DeleteView):
    model = NavigationItem
    template_name = 'navigation/navigation_item_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('navigation_detail', kwargs={'pk': self.object.navigation.pk})


class FooterLinkListView(LoginRequiredMixin, ListView):
    model = FooterLink
    template_name = 'navigation/footer_link_list.html'
    context_object_name = 'footer_links'


class FooterLinkCreateView(LoginRequiredMixin, CreateView):
    model = FooterLink
    form_class = FooterLinkForm
    template_name = 'navigation/footer_link_form.html'
    success_url = reverse_lazy('footer_link_list')


class FooterLinkUpdateView(LoginRequiredMixin, UpdateView):
    model = FooterLink
    form_class = FooterLinkForm
    template_name = 'navigation/footer_link_form.html'
    success_url = reverse_lazy('footer_link_list')


class FooterLinkDeleteView(LoginRequiredMixin, DeleteView):
    model = FooterLink
    template_name = 'navigation/footer_link_confirm_delete.html'
    success_url = reverse_lazy('footer_link_list')
