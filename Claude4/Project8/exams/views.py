"""
Views for Exams App
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Exam, ExamCategory


# StaffRequiredMixin - restricts access to staff users only
class StaffRequiredMixin(UserPassesTestMixin):
    """Only allow staff users to access management views"""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('home')


class ExamListView(ListView):
    """
    List view for all exams with filtering
    """
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 12

    def get_queryset(self):
        queryset = Exam.objects.select_related('category')

        # Get filter parameters
        category_id = self.request.GET.get('category')
        exam_type = self.request.GET.get('exam_type')
        qualification = self.request.GET.get('qualification')
        age_min = self.request.GET.get('age_min')
        age_max = self.request.GET.get('age_max')
        search = self.request.GET.get('search')

        # Filter by category (new approach)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by exam type (backward compatibility)
        if exam_type and not category_id:
            queryset = queryset.filter(exam_type=exam_type)

        # Filter by qualification (basic text matching)
        if qualification:
            queryset = queryset.filter(
                educational_qualification__icontains=qualification
            )

        # Filter by age limit
        if age_min:
            queryset = queryset.filter(age_limit_min__lte=age_min)
        if age_max:
            queryset = queryset.filter(age_limit_max__gte=age_max)

        # Search functionality
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(exam_type__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add categories to context
        context['categories'] = ExamCategory.objects.filter(is_active=True)
        context['exam_types'] = Exam.EXAM_TYPES  # Keep for backward compatibility

        # Add filter values to context for form persistence
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'exam_type': self.request.GET.get('exam_type', ''),
            'qualification': self.request.GET.get('qualification', ''),
            'age_min': self.request.GET.get('age_min', ''),
            'age_max': self.request.GET.get('age_max', ''),
            'search': self.request.GET.get('search', ''),
        }

        return context


class ExamDetailView(DetailView):
    """
    Detail view for a single exam
    """
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.get_object()

        # Add computed properties
        context['is_upcoming'] = exam.is_upcoming()
        context['is_application_open'] = exam.is_application_open()
        context['days_until_deadline'] = exam.days_until_application_deadline()
        context['days_until_exam'] = exam.days_until_exam()

        return context


# ========== Category CRUD Views ==========

class CategoryListView(StaffRequiredMixin, ListView):
    """List all exam categories for management"""
    model = ExamCategory
    template_name = 'exams/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ExamCategory.objects.all()


class CategoryCreateView(StaffRequiredMixin, CreateView):
    """Create a new exam category"""
    model = ExamCategory
    template_name = 'exams/category_form.html'
    fields = ['name', 'code', 'description', 'icon_class', 'is_active']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing exam category"""
    model = ExamCategory
    template_name = 'exams/category_form.html'
    fields = ['name', 'code', 'description', 'icon_class', 'is_active']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Delete an exam category"""
    model = ExamCategory
    template_name = 'exams/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        if category.exams.exists():
            messages.error(request, f'Cannot delete "{category.name}" - it has associated exams!')
            return redirect('category_list')
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ========== Exam CRUD Views ==========

class ExamCreateView(StaffRequiredMixin, CreateView):
    """Create a new exam"""
    model = Exam
    template_name = 'exams/exam_form.html'
    fields = [
        'title', 'category', 'official_link', 'description',
        'eligibility_criteria', 'age_limit_min', 'age_limit_max',
        'educational_qualification', 'syllabus_text',
        'application_start_date', 'application_end_date', 'exam_date'
    ]
    success_url = reverse_lazy('exam_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ExamCategory.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Exam "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class ExamUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing exam"""
    model = Exam
    template_name = 'exams/exam_form.html'
    fields = [
        'title', 'category', 'official_link', 'description',
        'eligibility_criteria', 'age_limit_min', 'age_limit_max',
        'educational_qualification', 'syllabus_text',
        'application_start_date', 'application_end_date', 'exam_date'
    ]
    success_url = reverse_lazy('exam_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ExamCategory.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Exam "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class ExamDeleteView(StaffRequiredMixin, DeleteView):
    """Delete an exam"""
    model = Exam
    template_name = 'exams/exam_confirm_delete.html'
    success_url = reverse_lazy('exam_list')

    def delete(self, request, *args, **kwargs):
        exam = self.get_object()
        messages.success(request, f'Exam "{exam.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ========== Management Dashboard ==========

class ManagementDashboardView(StaffRequiredMixin, TemplateView):
    """Management dashboard for staff users"""
    template_name = 'exams/management_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_categories = ExamCategory.objects.filter(is_active=True).count()
        total_exams = Exam.objects.count()
        upcoming_exams = Exam.objects.filter(
            exam_date__gte=timezone.now().date()
        ).count()

        recent_categories = ExamCategory.objects.order_by('-created_at')[:5]
        recent_exams = Exam.objects.order_by('-created_at')[:5]

        context.update({
            'total_categories': total_categories,
            'total_exams': total_exams,
            'upcoming_exams': upcoming_exams,
            'recent_categories': recent_categories,
            'recent_exams': recent_exams,
        })

        return context
