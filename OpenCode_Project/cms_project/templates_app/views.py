from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Template, TemplateSection, GlobalBlock, Theme
from .forms import TemplateForm, ThemeForm


class TemplateListView(LoginRequiredMixin, ListView):
    model = Template
    template_name = 'templates_app/template_list.html'
    context_object_name = 'templates'


class TemplateDetailView(LoginRequiredMixin, DetailView):
    model = Template
    template_name = 'templates_app/template_detail.html'
    context_object_name = 'template'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.structures.all()
        return context


class TemplateCreateView(LoginRequiredMixin, CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates_app/template_form.html'
    success_url = reverse_lazy('templates:template_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates_app/template_form.html'
    success_url = reverse_lazy('templates:template_list')


class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = Template
    template_name = 'templates_app/template_confirm_delete.html'
    success_url = reverse_lazy('templates:template_list')


class ThemeListView(LoginRequiredMixin, ListView):
    model = Theme
    template_name = 'templates_app/theme_list.html'
    context_object_name = 'themes'


class ThemeCreateView(LoginRequiredMixin, CreateView):
    model = Theme
    form_class = ThemeForm
    template_name = 'templates_app/theme_form.html'
    success_url = reverse_lazy('templates:theme_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
