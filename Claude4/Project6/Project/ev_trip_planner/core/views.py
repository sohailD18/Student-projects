from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import UserProfile, Vehicle, ChargingStation
from .forms import CustomUserCreationForm, UserProfileForm, VehicleForm, ChargingStationSearchForm


def home(request):
    """Home page with hero section and features"""
    context = {
        'total_stations': ChargingStation.objects.count(),
        'available_stations': ChargingStation.objects.filter(is_available=True).count(),
        'fast_charging': ChargingStation.objects.filter(fast_charging=True).count(),
    }
    return render(request, 'core/home.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to EV Trip Planner.')
            return redirect('core:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def user_login(request):
    """User login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard"""
    profile = request.user.profile
    vehicles = request.user.vehicles.all()
    recent_trips = request.user.trips.order_by('-created_at')[:5] if hasattr(request.user, 'trips') else []

    context = {
        'profile': profile,
        'vehicles': vehicles,
        'recent_trips': recent_trips,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    """User profile management"""
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)


@login_required
def vehicle_list(request):
    """List user's vehicles"""
    vehicles = request.user.vehicles.all()
    return render(request, 'core/vehicle_list.html', {'vehicles': vehicles})


@login_required
def vehicle_add(request):
    """Add a new vehicle"""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, f'{vehicle} added successfully!')
            return redirect('core:vehicle_list')
    else:
        form = VehicleForm()

    return render(request, 'core/vehicle_form.html', {'form': form, 'action': 'Add'})


@login_required
def vehicle_edit(request, pk):
    """Edit existing vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'{vehicle} updated successfully!')
            return redirect('core:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'core/vehicle_form.html', {'form': form, 'action': 'Edit', 'vehicle': vehicle})


@login_required
def vehicle_delete(request, pk):
    """Delete a vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, f'{vehicle} deleted successfully!')
        return redirect('core:vehicle_list')

    return render(request, 'core/vehicle_confirm_delete.html', {'vehicle': vehicle})


def charging_stations_map(request):
    """Map view of all charging stations"""
    stations = ChargingStation.objects.all()
    form = ChargingStationSearchForm(request.GET or None)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        connector_type = form.cleaned_data.get('connector_type')
        fast_charging = form.cleaned_data.get('fast_charging')
        max_price = form.cleaned_data.get('max_price')

        if search_query:
            stations = stations.filter(
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(address__icontains=search_query)
            )

        if connector_type:
            stations = stations.filter(connector_type=connector_type)

        if fast_charging == 'fast':
            stations = stations.filter(fast_charging=True)
        elif fast_charging == 'available':
            stations = stations.filter(is_available=True)

        if max_price:
            stations = stations.filter(price_per_kwh__lte=max_price)

    # Prepare station data for JSON response
    import json

    def serialize_station(station):
        return {
            'id': station.id,
            'name': station.name,
            'location': station.location,
            'lat': station.latitude,
            'lng': station.longitude,
            'connector_type': station.get_connector_type_display(),
            'power_kw': station.power_kw,
            'price_per_kwh': str(station.price_per_kwh),
            'is_available': bool(station.is_available),
            'fast_charging': bool(station.fast_charging),
            'total_ports': station.total_ports,
            'available_ports': station.available_ports,
            'address': station.address,
            'amenities': station.amenities,
        }

    stations_data = [serialize_station(s) for s in stations]

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'stations': stations_data})

    context = {
        'stations': stations,
        'stations_json': json.dumps(stations_data),
        'form': form,
    }
    return render(request, 'core/stations_map.html', context)


def charging_stations_list(request):
    """List view of charging stations"""
    stations = ChargingStation.objects.all()
    form = ChargingStationSearchForm(request.GET or None)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        connector_type = form.cleaned_data.get('connector_type')
        fast_charging = form.cleaned_data.get('fast_charging')
        max_price = form.cleaned_data.get('max_price')

        if search_query:
            stations = stations.filter(
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(address__icontains=search_query)
            )

        if connector_type:
            stations = stations.filter(connector_type=connector_type)

        if fast_charging == 'fast':
            stations = stations.filter(fast_charging=True)
        elif fast_charging == 'available':
            stations = stations.filter(is_available=True)

        if max_price:
            stations = stations.filter(price_per_kwh__lte=max_price)

    context = {
        'stations': stations,
        'form': form,
    }
    return render(request, 'core/stations_list.html', context)


def station_detail(request, pk):
    """Detailed view of a charging station"""
    station = get_object_or_404(ChargingStation, pk=pk)
    context = {
        'station': station,
    }
    return render(request, 'core/station_detail.html', context)
