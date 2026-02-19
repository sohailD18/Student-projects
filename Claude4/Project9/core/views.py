"""
Views for AgriSense application.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import SoilData, ContactMessage
from .ml_logic import recommend_crop, suggest_fertilizer


def home(request):
    """
    Render the home/landing page.
    """
    return render(request, 'home.html')


def analyze(request):
    """
    Handle soil analysis form submission.
    """
    if request.method == 'POST':
        try:
            # Get form data
            nitrogen = int(request.POST.get('nitrogen'))
            phosphorus = int(request.POST.get('phosphorus'))
            potassium = int(request.POST.get('potassium'))
            ph = float(request.POST.get('ph_level'))
            moisture = float(request.POST.get('moisture'))

            # Validate ranges
            if not (0 <= nitrogen <= 200):
                messages.error(request, 'Nitrogen must be between 0 and 200 mg/kg')
                return render(request, 'analyze.html')

            if not (0 <= phosphorus <= 150):
                messages.error(request, 'Phosphorus must be between 0 and 150 mg/kg')
                return render(request, 'analyze.html')

            if not (0 <= potassium <= 200):
                messages.error(request, 'Potassium must be between 0 and 200 mg/kg')
                return render(request, 'analyze.html')

            if not (0 <= ph <= 14):
                messages.error(request, 'pH must be between 0 and 14')
                return render(request, 'analyze.html')

            if not (0 <= moisture <= 100):
                messages.error(request, 'Moisture must be between 0 and 100%')
                return render(request, 'analyze.html')

            # Get AI recommendations
            recommended_crop = recommend_crop(nitrogen, phosphorus, potassium, ph, moisture)
            fertilizer_suggestion = suggest_fertilizer(nitrogen, phosphorus, potassium, recommended_crop)

            # Save to database
            soil_data = SoilData.objects.create(
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ph_level=ph,
                moisture=moisture,
                recommended_crop=recommended_crop,
                fertilizer_suggestion=fertilizer_suggestion
            )

            # Redirect to result page
            return redirect('result', analysis_id=soil_data.id)

        except (ValueError, TypeError) as e:
            messages.error(request, 'Please enter valid numeric values')
            return render(request, 'analyze.html')

    return render(request, 'analyze.html')


def result(request, analysis_id):
    """
    Display the analysis result.
    """
    try:
        soil_data = SoilData.objects.get(id=analysis_id)

        # Format fertilizer suggestion with line breaks
        formatted_suggestion = soil_data.fertilizer_suggestion

        context = {
            'soil_data': soil_data,
            'formatted_suggestion': formatted_suggestion,
            'saved_to_history': True
        }

        return render(request, 'result.html', context)

    except SoilData.DoesNotExist:
        messages.error(request, 'Analysis not found. Please try again.')
        return redirect('analyze')


def history(request):
    """
    Display the last 10 soil analyses.
    """
    # Get last 10 analyses
    analyses_list = SoilData.objects.all()[:10]

    # Pagination (show 5 per page)
    paginator = Paginator(analyses_list, 5)
    page_number = request.GET.get('page')
    analyses = paginator.get_page(page_number)

    context = {
        'analyses': analyses,
        'total_count': SoilData.objects.count()
    }

    return render(request, 'history.html', context)


def contact(request):
    """
    Handle contact form submission.
    """
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')

            # Basic validation
            if not name or not email or not message:
                messages.error(request, 'Please fill in all fields')
                return render(request, 'contact.html')

            if len(name) < 2:
                messages.error(request, 'Name must be at least 2 characters')
                return render(request, 'contact.html')

            if len(message) < 10:
                messages.error(request, 'Message must be at least 10 characters')
                return render(request, 'contact.html')

            # Save message to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )

            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return render(request, 'contact.html')

        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return render(request, 'contact.html')

    return render(request, 'contact.html')
