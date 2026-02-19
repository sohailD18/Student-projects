from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import Service, Provider, TimeSlot, Appointment, Booking, Reminder
from .forms import BookingForm, ServiceForm

def home(request):
    services = Service.objects.filter(is_active=True)
    providers = Provider.objects.filter(is_available=True)
    return render(request, 'appointments/home.html', {
        'services': services,
        'providers': providers,
    })

class ServiceListView(ListView):
    model = Service
    template_name = 'appointments/services.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)

class ProviderListView(ListView):
    model = Provider
    template_name = 'appointments/providers.html'
    context_object_name = 'providers'
    
    def get_queryset(self):
        service_id = self.request.GET.get('service')
        if service_id:
            return Provider.objects.filter(services__id=service_id, is_available=True).distinct()
        return Provider.objects.filter(is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.request.GET.get('service')
        if service_id:
            try:
                context['service'] = Service.objects.get(id=service_id)
            except Service.DoesNotExist:
                context['service'] = None
        else:
            context['service'] = None
        return context

class ProviderDetailView(DetailView):
    model = Provider
    template_name = 'appointments/provider_detail.html'
    context_object_name = 'provider'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.filter(is_active=True)
        context['time_slots'] = self.object.time_slots.filter(is_active=True)
        context['today'] = timezone.now().date()
        return context

@ensure_csrf_cookie
def get_available_slots(request, provider_id, date):
    provider = get_object_or_404(Provider, id=provider_id)
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    day_of_week = selected_date.weekday()
    now = timezone.now()
    current_date = now.date()
    current_time = now.time()
    
    time_slots = TimeSlot.objects.filter(
        provider=provider,
        day_of_week=day_of_week,
        is_active=True
    )
    
    booked_slots = Appointment.objects.filter(
        provider=provider,
        appointment_date=selected_date,
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('start_time', 'end_time')
    
    available_slots = []
    for slot in time_slots:
        slot_time = slot.start_time
        while slot_time < slot.end_time:
            is_booked = any(
                booked_start <= slot_time < booked_end
                for booked_start, booked_end in booked_slots
            )
            is_past = selected_date == current_date and slot_time < current_time
            if not is_booked and not is_past:
                available_slots.append(slot_time.strftime('%H:%M'))
            slot_time = (datetime.combine(datetime.today(), slot_time) + timedelta(minutes=30)).time()
    
    return JsonResponse({'slots': available_slots})

@login_required
def book_appointment(request):
    provider_id = request.POST.get('provider_id') or request.GET.get('provider_id')
    service_id = request.POST.get('service_id') or request.GET.get('service_id')
    
    provider = get_object_or_404(Provider, id=provider_id)
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.provider = provider
            booking.total_amount = service.price
            booking.save()
            
            Appointment.objects.create(
                client=request.user,
                provider=provider,
                service=service,
                appointment_date=booking.booking_date,
                start_time=booking.booking_time,
                end_time=(datetime.combine(datetime.today(), booking.booking_time) + timedelta(minutes=service.duration)).time(),
                total_price=service.price,
                notes=booking.special_requests
            )
            
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()
    
    return render(request, 'appointments/book.html', {
        'form': form,
        'provider': provider,
        'service': service,
    })

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        client=request.user
    ).select_related('provider', 'service').order_by('-appointment_date', '-start_time')
    
    upcoming = appointments.filter(
        appointment_date__gte=timezone.now().date(),
        status__in=['PENDING', 'CONFIRMED']
    )
    
    past = appointments.filter(
        appointment_date__lt=timezone.now().date()
    ) | appointments.filter(status__in=['COMPLETED', 'CANCELLED'])
    
    return render(request, 'appointments/my_appointments.html', {
        'upcoming': upcoming,
        'past': past,
    })

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'appointments/confirmation.html', {'booking': booking})

@login_required
def provider_dashboard(request):
    try:
        provider = request.user.provider
        appointments = Appointment.objects.filter(provider=provider)
        upcoming = appointments.filter(
            status__in=['PENDING', 'CONFIRMED'],
            appointment_date__gte=timezone.now().date()
        ).order_by('appointment_date', 'start_time')
        
        today = timezone.now().date()
        today_appointments = appointments.filter(appointment_date=today)
        
        return render(request, 'appointments/provider_dashboard.html', {
            'provider': provider,
            'upcoming': upcoming,
            'today_appointments': today_appointments,
        })
    except Provider.DoesNotExist:
        return redirect('home')

@login_required
def update_appointment_status(request, appointment_id):
    if not hasattr(request.user, 'provider'):
        return JsonResponse({'success': False, 'error': 'Not a provider'})
    
    appointment = get_object_or_404(Appointment, id=appointment_id, provider=request.user.provider)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW']:
            appointment.status = new_status
            appointment.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'appointments/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password == password2 and len(password) >= 6:
            if User.objects.filter(username=username).exists():
                return render(request, 'appointments/register.html', {'error': 'Username already exists'})
            
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'appointments/register.html', {'error': 'Passwords must match and be at least 6 characters'})
    
    return render(request, 'appointments/register.html')
