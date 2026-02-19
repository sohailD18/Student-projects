"""
Views for Core App
"""
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils import timezone
from exams.models import Exam


class HomeView(TemplateView):
    """
    Home Page - Landing page with search and recent exams
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get recent exams (latest 6)
        recent_exams = Exam.objects.filter(
            exam_date__gte=timezone.now().date()
        ).order_by('-created_at')[:6]

        # Get upcoming deadlines (applications closing soon)
        upcoming_deadlines = Exam.objects.filter(
            application_end_date__gte=timezone.now().date(),
            exam_date__gte=timezone.now().date()
        ).order_by('application_end_date')[:6]

        # Quick stats
        total_exams = Exam.objects.filter(
            exam_date__gte=timezone.now().date()
        ).count()

        context.update({
            'recent_exams': recent_exams,
            'upcoming_deadlines': upcoming_deadlines,
            'total_exams': total_exams,
        })

        return context


def search_view(request):
    """
    Search functionality for exams
    """
    query = request.GET.get('q', '')
    exams = []

    if query:
        from django.db.models import Q
        exams = Exam.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(exam_type__icontains=query)
        ).filter(exam_date__gte=timezone.now().date())[:10]

    return render(request, 'core/search.html', {
        'query': query,
        'exams': exams
    })


def about_view(request):
    """
    About page
    """
    return render(request, 'core/about.html')
