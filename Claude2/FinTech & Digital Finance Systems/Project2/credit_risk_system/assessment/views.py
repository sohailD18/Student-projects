"""
Views for Credit Risk Assessment System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg, Count
from datetime import datetime

from .models import Applicant, FinancialData
from .forms import CombinedAssessmentForm
from .utils import (
    preprocess_applicant_data, calculate_eligibility,
    get_risk_category_details, get_dashboard_statistics
)
from .ml_model import get_predictor


def home(request):
    """
    Home page - Landing page with overview
    """
    # Get quick stats
    total_applicants = Applicant.objects.count()
    recent_applicants = Applicant.objects.select_related('financial_data')[:5]

    context = {
        'total_applicants': total_applicants,
        'recent_applicants': recent_applicants,
        'page_title': 'Home - Credit Risk Assessment System'
    }
    return render(request, 'assessment/home.html', context)


def new_assessment(request):
    """
    New Assessment Form Page
    Displays form for entering applicant information
    """
    if request.method == 'POST':
        form = CombinedAssessmentForm(request.POST)
        if form.is_valid():
            try:
                # Extract form data
                applicant_data = {
                    'name': form.cleaned_data['name'],
                    'email': form.cleaned_data['email'],
                    'phone': form.cleaned_data['phone'],
                    'annual_income': form.cleaned_data['annual_income'],
                    'employment_status': form.cleaned_data['employment_status'],
                    'years_employed': form.cleaned_data['years_employed'],
                    'debt_to_income_ratio': form.cleaned_data['debt_to_income_ratio'],
                }

                financial_data = {
                    'credit_score': form.cleaned_data['credit_score'],
                    'num_open_loans': form.cleaned_data['num_open_loans'],
                    'num_credit_lines': form.cleaned_data['num_credit_lines'],
                    'late_payments': form.cleaned_data['late_payments'],
                    'bankruptcies': form.cleaned_data['bankruptcies'],
                    'home_ownership_status': form.cleaned_data['home_ownership_status'],
                    'total_credit_limit': form.cleaned_data.get('total_credit_limit'),
                    'credit_utilization': form.cleaned_data.get('credit_utilization'),
                }

                # Get ML prediction
                predictor = get_predictor()
                processed_data = preprocess_applicant_data(applicant_data, financial_data)
                prediction_probability = predictor.predict(processed_data)

                # Calculate eligibility and risk category
                eligibility_status, risk_category = calculate_eligibility(
                    prediction_probability,
                    financial_data
                )

                # Create Applicant record
                applicant = Applicant.objects.create(
                    **applicant_data,
                    risk_probability=prediction_probability,
                    risk_category=risk_category,
                    eligibility_status=eligibility_status
                )

                # Create FinancialData record
                FinancialData.objects.create(
                    applicant=applicant,
                    **financial_data
                )

                messages.success(request, 'Assessment completed successfully!')

                # Redirect to results page
                return redirect('assessment_result', applicant_id=applicant.id)

            except Exception as e:
                messages.error(request, f'Error processing assessment: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = CombinedAssessmentForm()

    context = {
        'form': form,
        'page_title': 'New Assessment - Credit Risk Assessment'
    }
    return render(request, 'assessment/assessment_form.html', context)


def assessment_result(request, applicant_id):
    """
    Display assessment results
    Shows prediction, risk category, and recommendation
    """
    applicant = get_object_or_404(
        Applicant.objects.select_related('financial_data'),
        id=applicant_id
    )

    # Get risk category details
    risk_details = get_risk_category_details(applicant.risk_category)

    context = {
        'applicant': applicant,
        'financial_data': applicant.financial_data,
        'risk_details': risk_details,
        'page_title': f'Assessment Result - {applicant.name}'
    }
    return render(request, 'assessment/assessment_result.html', context)


def dashboard(request):
    """
    Analytics Dashboard
    Displays statistics and visualizations
    """
    applicants = Applicant.objects.select_related('financial_data').all()
    stats = get_dashboard_statistics(applicants)

    context = {
        'stats': stats,
        'page_title': 'Dashboard - Credit Risk Assessment'
    }
    return render(request, 'assessment/dashboard.html', context)


def report(request, applicant_id):
    """
    Generate printable report for an applicant
    """
    applicant = get_object_or_404(
        Applicant.objects.select_related('financial_data'),
        id=applicant_id
    )

    # Get risk category details
    risk_details = get_risk_category_details(applicant.risk_category)

    context = {
        'applicant': applicant,
        'financial_data': applicant.financial_data,
        'risk_details': risk_details,
        'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'page_title': f'Report - {applicant.name}'
    }

    # Check if PDF download is requested
    if request.GET.get('format') == 'pdf':
        # Generate PDF (lazy import to avoid startup issues on Windows)
        try:
            import weasyprint
            html_string = render_to_string('assessment/report_pdf.html', context)
            html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
            pdf_file = html.write_pdf()

            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f"credit_assessment_report_{applicant.name.replace(' ', '_')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except (ImportError, OSError) as e:
            messages.error(request, f'PDF generation is not available. Please install GTK libraries or use the HTML view. Error: {str(e)}')
            return render(request, 'assessment/report.html', context)

    return render(request, 'assessment/report.html', context)


def applicant_list(request):
    """
    List all applicants with filtering options
    """
    applicants = Applicant.objects.select_related('financial_data').all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applicants = applicants.filter(eligibility_status=status_filter)

    # Filter by risk category
    risk_filter = request.GET.get('risk')
    if risk_filter:
        applicants = applicants.filter(risk_category=risk_filter)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        applicants = applicants.filter(
            name__icontains=search_query
        ) | applicants.filter(
            email__icontains=search_query
        )

    # Order by
    order_by = request.GET.get('order_by', '-created_at')
    applicants = applicants.order_by(order_by)

    context = {
        'applicants': applicants,
        'status_filter': status_filter,
        'risk_filter': risk_filter,
        'search_query': search_query,
        'page_title': 'All Applicants - Credit Risk Assessment'
    }
    return render(request, 'assessment/applicant_list.html', context)


def applicant_detail(request, applicant_id):
    """
    Detailed view of a single applicant
    """
    applicant = get_object_or_404(
        Applicant.objects.select_related('financial_data'),
        id=applicant_id
    )

    risk_details = get_risk_category_details(applicant.risk_category)

    context = {
        'applicant': applicant,
        'financial_data': applicant.financial_data,
        'risk_details': risk_details,
        'page_title': f'Applicant Details - {applicant.name}'
    }
    return render(request, 'assessment/applicant_detail.html', context)


def api_prediction_stats(request):
    """
    API endpoint to get prediction statistics for dashboard
    Returns JSON data for charts
    """
    if request.method == 'GET':
        applicants = Applicant.objects.all()

        # Risk distribution data
        risk_distribution = {
            'low': applicants.filter(risk_category='low').count(),
            'medium': applicants.filter(risk_category='medium').count(),
            'high': applicants.filter(risk_category='high').count(),
        }

        # Status distribution
        status_distribution = {
            'approved': applicants.filter(eligibility_status='approved').count(),
            'manual_review': applicants.filter(eligibility_status='manual_review').count(),
            'rejected': applicants.filter(eligibility_status='rejected').count(),
        }

        # Average income by status
        income_by_status = {}
        for status in ['approved', 'manual_review', 'rejected']:
            avg_income = applicants.filter(
                eligibility_status=status
            ).aggregate(avg=Avg('annual_income'))['avg'] or 0
            income_by_status[status] = float(avg_income)

        # Approval rate over time (last 30 days)
        from django.utils import timezone
        from datetime import timedelta

        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_applicants = applicants.filter(created_at__gte=thirty_days_ago)

        # Group by date
        approval_timeline = {}
        for applicant in recent_applicants:
            date_str = applicant.created_at.strftime('%Y-%m-%d')
            if date_str not in approval_timeline:
                approval_timeline[date_str] = {'total': 0, 'approved': 0}
            approval_timeline[date_str]['total'] += 1
            if applicant.eligibility_status == 'approved':
                approval_timeline[date_str]['approved'] += 1

        # Convert to lists for chart
        dates = sorted(approval_timeline.keys())
        approval_rates = []
        for date in dates:
            total = approval_timeline[date]['total']
            approved = approval_timeline[date]['approved']
            rate = (approved / total * 100) if total > 0 else 0
            approval_rates.append(round(rate, 2))

        data = {
            'risk_distribution': risk_distribution,
            'status_distribution': status_distribution,
            'income_by_status': income_by_status,
            'approval_timeline': {
                'dates': dates,
                'rates': approval_rates
            }
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def delete_applicant(request, applicant_id):
    """
    Delete an applicant record
    """
    if request.method == 'POST':
        applicant = get_object_or_404(Applicant, id=applicant_id)
        applicant.delete()
        messages.success(request, 'Applicant record deleted successfully.')
        return redirect('applicant_list')

    return redirect('applicant_detail', applicant_id=applicant_id)
