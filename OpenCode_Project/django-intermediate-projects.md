# 50 Intermediate Django Projects for Internship Students

A comprehensive guide to building real-world Django applications for learning and skill development.

---

## Table of Contents

1. [Hospital Management System](#1-hospital-management-system)
2. [Real-Time Chat Application](#2-real-time-chat-application)
3. [E-Commerce Platform](#3-e-commerce-platform)
4. [Task/Project Management System](#4-taskproject-management-system)
5. [Blog Platform with CMS Features](#5-blog-platform-with-cms-features)
6. [Social Media Clone](#6-social-media-clone)
7. [Online Learning Management System](#7-online-learning-management-system)
8. [Restaurant Reservation System](#8-restaurant-reservation-system)
9. [Job Portal](#9-job-portal)
10. [Real Estate Listing Platform](#10-real-estate-listing-platform)
11. [Library Management System](#11-library-management-system)
12. [Event Management System](#12-event-management-system)
13. [Inventory Management System](#13-inventory-management-system)
14. [Hotel Booking System](#14-hotel-booking-system)
15. [Fitness Tracking Application](#15-fitness-tracking-application)
16. [Recipe Sharing Platform](#16-recipe-sharing-platform)
17. [Auction Platform](#17-auction-platform)
18. [News Aggregator](#18-news-aggregator)
19. [Online Code Editor](#19-online-code-editor)
20. [File Sharing Application](#20-file-sharing-application)
21. [Poll/Voting System](#21-pollvoting-system)
22. [Note-Taking Application](#22-note-taking-application)
23. [Forum/Discussion Board](#23-forumdiscussion-board)
24. [Photo Gallery Application](#24-photo-gallery-application)
25. [Music Streaming Service](#25-music-streaming-service)
26. [Video Streaming Platform](#26-video-streaming-platform)
27. [Appointment Scheduling System](#27-appointment-scheduling-system)
28. [Multi-Vendor Marketplace](#28-multi-vendor-marketplace)
29. [Customer Relationship Management (CRM)](#29-customer-relationship-management-crm)
30. [Content Management System (CMS)](#30-content-management-system-cms)
31. [Email Marketing Platform](#31-email-marketing-platform)
32. [Analytics Dashboard](#32-analytics-dashboard)
33. [Bug Tracking System](#33-bug-tracking-system)
34. [Document Management System](#34-document-management-system)
35. [Online Examination System](#35-online-examination-system)
36. [Subscription Management System](#36-subscription-management-system)
37. [Support Ticket System](#37-support-ticket-system)
38. [URL Shortener Service](#38-url-shortener-service)
39. [Weather Application](#39-weather-application)
40. [Currency Converter](#40-currency-converter)
41. [Flashcard Application](#41-flashcard-application)
42. [Budget Tracker](#42-budget-tracker)
43. [Travel Planning Application](#43-travel-planning-application)
44. [Pet Adoption Platform](#44-pet-adoption-platform)
45. [Parking Reservation System](#45-parking-reservation-system)
46. [Delivery Tracking System](#46-delivery-tracking-system)
47. [Recipe Restaurant Management](#47-recipe-restaurant-management)
48. [Gym Membership Management](#48-gym-membership-management)
49. [Blood Donation Management](#49-blood-donation-management)
50. [Alumni Network Platform](#50-alumni-network-platform)

---

## Prerequisites

Before starting these projects, students should have:

- **Python Knowledge**: Basic to intermediate Python programming
- **Django Basics**: Understanding of Django project structure, URLs, views, templates
- **HTML/CSS**: Basic frontend knowledge
- **Database**: Understanding of relational databases and SQL
- **Git**: Basic version control operations

**Recommended Django Version**: Django 5.x

**Installation**:
```bash
pip install django
django-admin startproject projectname
python manage.py startapp appname
```

---

## 1. Hospital Management System

### Overview

Build a comprehensive hospital management system that handles patient registration, appointment scheduling, doctor management, medical records, and prescription generation. This project teaches complex database relationships and Django's authentication system.

### Learning Objectives

- Complex ForeignKey and ManyToMany relationships
- Custom user model extension
- Django Signals for automated tasks
- File uploads and media handling
- Role-based access control
- Custom template tags and filters

### Tech Stack & Dependencies

```
django>=5.0
pillow>=10.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
```

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    profile_picture = models.ImageField(upload_to='doctors/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='patients/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.get_full_name()
    
    @property
    def age(self):
        from datetime import date
        return date.today().year - self.date_of_birth.year

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'), ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.appointment_date}"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    symptoms = models.TextField()
    treatment_plan = models.TextField()
    vital_signs = models.JSONField(default=dict, blank=True)
    attachments = models.FileField(upload_to='medical_records/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Record for {self.patient} on {self.created_at.date()}"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medications = models.JSONField()
    instructions = models.TextField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription for {self.patient}"

class Billing(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Bill #{self.id} - {self.patient}"
```

### Key Features

**Patient Management**
- Patient registration and profile management
- Medical history tracking
- Emergency contact information
- Profile picture upload

**Doctor Management**
- Doctor registration with qualifications
- Department assignment
- Availability scheduling
- Consultation fee management

**Appointment System**
- Online appointment booking
- Real-time availability checking
- Appointment status tracking

**Medical Records**
- Digital medical record creation
- Vital signs tracking
- Attachments support
- Prescription generation

**Billing System**
- Invoice generation
- Payment tracking

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject hospital_project
cd hospital_project
python manage.py startapp hospital
```

**Step 2: Configure Settings**
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'hospital',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Step 3: Create Models**
```python
# hospital/models.py
# (Paste all model code from above)
```

**Step 4: Create Views**
```python
# hospital/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Patient, Doctor, Appointment

@login_required
def dashboard(request):
    if hasattr(request.user, 'patient'):
        appointments = Appointment.objects.filter(patient__user=request.user)
        return render(request, 'hospital/patient_dashboard.html', {'appointments': appointments})
    elif hasattr(request.user, 'doctor'):
        appointments = Appointment.objects.filter(doctor__user=request.user)
        return render(request, 'hospital/doctor_dashboard.html', {'appointments': appointments})
    return redirect('home')

class AppointmentListView(login_required, ListView):
    model = Appointment
    template_name = 'hospital/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'patient'):
            return Appointment.objects.filter(patient__user=self.request.user)
        elif hasattr(self.request.user, 'doctor'):
            return Appointment.objects.filter(doctor__user=self.request.user)
        return Appointment.objects.all()
```

**Step 5: Create URLs**
```python
# hospital/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='appointment_create'),
]
```

**Step 6: Configure Admin**
```python
# hospital/admin.py
from django.contrib import admin
from .models import Department, Doctor, Patient, Appointment, MedicalRecord, Prescription, Billing

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'specialization', 'consultation_fee', 'is_available']
    list_filter = ['department', 'is_available']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'blood_group', 'phone_number']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'doctor']

admin.site.register(MedicalRecord)
admin.site.register(Prescription)
admin.site.register(Billing)
```

**Step 7: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Challenges & Solutions

**Challenge: Complex form handling for patient registration**
- Solution: Use Django formsets and create custom form wizard for multi-step registration

**Challenge: Time slot availability logic**
- Solution: Create a custom manager method and use database queries to check availability

**Challenge: Medical record security**
- Solution: Implement custom permissions and use Django's @permission_required decorator

### Extensions for Advanced Students

1. **SMS Notifications**: Integrate Twilio for appointment reminders
2. **Video Consultation**: Add Django Channels for video calls
3. **Pharmacy Module**: Add medication inventory and dispensing
4. **Lab Reports**: Add laboratory test results management
5. **Analytics Dashboard**: Create charts using Chart.js
6. **Mobile API**: Build REST API using Django REST Framework

---

## 2. Real-Time Chat Application

### Overview

Build a real-time chat application with multiple chat rooms, direct messaging, user authentication, and message persistence. This project teaches Django Channels, WebSockets, and asynchronous communication.

### Learning Objectives

- Django Channels and WebSockets
- Asynchronous views and consumers
- Redis as channel layer
- Real-time UI updates with JavaScript
- Message persistence and history
- User presence indicators

### Tech Stack & Dependencies

```
django>=5.0
channels>=4.0
channels-redis>=4.1
redis>=4.5
daphne>=4.0
pillow>=10.0
```

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    is_private = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name='allowed_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, default='text')
    file_attachment = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"DM from {self.sender} to {self.recipient}"

class UserPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    current_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
```

### Key Features

**Chat Rooms**
- Create public and private chat rooms
- Set room descriptions
- Invite users to private rooms
- Room member management

**Messaging**
- Real-time text messages
- File and image sharing
- Message editing and deletion
- Message history with pagination

**Direct Messages**
- One-on-one private messaging
- Online/offline indicators
- Unread message count

**User Presence**
- Real-time online status
- Current room tracking
- Last seen timestamps

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject chat_project
cd chat_project
python manage.py startapp chat
```

**Step 2: Configure Channels**
```python
# settings.py
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'chat',
]

ASGI_APPLICATION = 'chat_project.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

**Step 3: Create ASGI Configuration**
```python
# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
```

**Step 4: Create Consumers**
```python
# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message, UserPresence

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        await self.update_presence(True, self.room_name)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'user_joined', 'user': self.user.username}
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.update_presence(False, None)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'user_left', 'user': self.user.username}
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.save_message(message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat_message', 'message': message, 'user': self.user.username}
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user': event['user']
        }))
    
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': f"{event['user']} joined the chat"
        }))
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(name=self.room_name)
        Message.objects.create(room=room, user=self.user, content=content)
    
    @database_sync_to_async
    def update_presence(self, is_online, room_name):
        room = ChatRoom.objects.get(name=room_name) if room_name else None
        UserPresence.objects.update_or_create(
            user=self.user,
            defaults={'is_online': is_online, 'current_room': room}
        )
```

**Step 5: Create Routing**
```python
# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
```

**Step 6: Create Views**
```python
# chat/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

@login_required
def chat_index(request):
    rooms = ChatRoom.objects.filter(
        models.Q(is_private=False) | models.Q(allowed_users=request.user)
    ).distinct()
    return render(request, 'chat/index.html', {'rooms': rooms})

@login_required
def chat_room(request, room_name):
    room = ChatRoom.objects.get(name=room_name)
    messages = Message.objects.filter(room=room)[:50]
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages
    })
```

**Step 7: Configure URLs**
```python
# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('room/create/', views.ChatRoomCreateView.as_view(), name='create_room'),
]
```

**Step 8: Create Templates**
```html
<!-- chat/templates/chat/room.html -->
{% extends 'base.html' %}
{% block content %}
<div class="chat-container">
    <div class="messages-container" id="messages">
        {% for message in messages %}
        <div class="message">
            <strong>{{ message.user.username }}:</strong>
            {{ message.content }}
        </div>
        {% endfor %}
    </div>
    <div class="chat-input">
        <input type="text" id="chat-message-input" placeholder="Type a message...">
        <button id="chat-message-submit">Send</button>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    const roomName = "{{ room_name }}";
    const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + room_name + '/');
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.innerHTML = `<strong>${data.user}:</strong> ${data.message}`;
        messagesDiv.appendChild(messageDiv);
    };
    
    document.getElementById('chat-message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            chatSocket.send(JSON.stringify({'message': this.value}));
            this.value = '';
        }
    });
</script>
{% endblock %}
```

**Step 9: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Extensions for Advanced Students

1. **Voice Messages**: Add audio recording and sending
2. **Message Reactions**: Add emoji reactions to messages
3. **Message Search**: Full-text search in chat history
4. **Read Receipts**: Show when messages are read
5. **End-to-End Encryption**: Implement encryption

---

## 3. E-Commerce Platform

### Overview

Build a full-featured e-commerce platform with product catalog, shopping cart, checkout process, payment integration, and order management. This project teaches Django sessions, complex forms, payment processing, and order workflows.

### Learning Objectives

- Django sessions and cart management
- Complex forms and formsets
- Django ORM queries and aggregations
- Payment integration (Stripe)
- Order processing workflow
- Product search and filtering
- Inventory management

### Tech Stack & Dependencies

```
django>=5.0
stripe>=7.0
pillow>=10.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
```

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.product.current_price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'), ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'), ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
```

### Key Features

**Product Management**
- Product catalog with categories
- Product search and filtering
- Product reviews and ratings
- Stock management

**Shopping Cart**
- Add/remove items
- Quantity updates
- Price calculations
- Persistent cart with sessions

**Checkout Process**
- Multi-step checkout
- Payment integration
- Order summary

**User Features**
- User registration and login
- Order history
- Order tracking
- Wishlist

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject ecommerce_project
cd ecommerce_project
python manage.py startapp store
```

**Step 2: Create Cart Context Processor**
```python
# store/context_processors.py
from .models import Cart

def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart': cart}
    return {'cart': None}
```

**Step 3: Create Views**
```python
# store/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem
from decimal import Decimal

def product_list(request):
    products = Product.objects.filter(status='ACTIVE')
    categories = Category.objects.filter(is_active=True)
    
    search = request.GET.get('q')
    if search:
        products = products.filter(name__icontains=search)
    
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='ACTIVE')
    reviews = product.reviews.filter(is_approved=True)
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews
    })

@login_required
def cart_detail(request):
    cart = request.user.cart
    return render(request, 'store/cart.html', {'cart': cart})

@require_POST
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'cart_total_items': cart.total_items
    })

@require_POST
@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'cart_total_price': float(cart.total_price)
    })

@login_required
def checkout(request):
    cart = request.user.cart
    if not cart.items.exists():
        return redirect('cart_detail')
    
    subtotal = cart.total_price
    shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0')
    tax = subtotal * Decimal('0.08')
    total = subtotal + shipping_cost + tax
    
    from django.utils import timezone
    order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"
    
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax=tax,
        total=total,
        payment_method='stripe'
    )
    
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.current_price,
            subtotal=item.subtotal
        )
        item.product.stock_quantity -= item.quantity
        item.product.save()
    
    cart.items.all().delete()
    
    return redirect('order_success', order_id=order.id)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_list.html', {'orders': orders})
```

**Step 4: Configure URLs**
```python
# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
]
```

**Step 5: Configure Admin**
```python
# store/admin.py
from django.contrib import admin
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'status']
    list_filter = ['category', 'status']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['order_number', 'user__username']

admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
```

**Step 6: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Coupon System**: Add discount coupons
2. **Payment Gateway**: Integrate PayPal or Stripe
3. **Order Tracking**: Real-time shipment tracking
4. **Seller Dashboard**: Multi-vendor marketplace
5. **Product Comparison**: Compare products side by side
6. **Mobile App API**: Django REST Framework API

---

## 4. Task/Project Management System

### Overview

Build a comprehensive project management system with task tracking, team collaboration, file attachments, comments, tags, and progress monitoring. This project teaches Django permissions, signals, email notifications, and custom managers.

### Learning Objectives

- Django permissions and groups
- Custom model managers and querysets
- Email notifications
- Django signals for automation
- File handling and attachments
- REST API development

### Tech Stack & Dependencies

```
django>=5.0
django-extensions>=3.2
celery>=5.3
redis>=4.5
djangorestframework>=3.14
```

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'), ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'), ('COMPLETED', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    key = models.CharField(max_length=10)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['key', 'owner']
    
    def __str__(self):
        return f"{self.key}: {self.name}"
    
    @property
    def progress(self):
        tasks = self.tasks.all()
        if not tasks:
            return 0
        completed = tasks.filter(status='DONE').count()
        return int((completed / tasks.count()) * 100)

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'In Review'), ('DONE', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'), ('MEDIUM', 'Medium'),
        ('HIGH', 'High'), ('URGENT', 'Urgent'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_key = models.CharField(max_length=20)
    summary = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, default='TASK')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_tasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    story_points = models.PositiveIntegerField(default=0)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.key}-{self.task_key}: {self.summary}"
    
    def save(self, *args, **kwargs):
        if not self.task_key:
            last_task = Task.objects.filter(project=self.project).order_by('-task_key').first()
            if last_task:
                num = int(last_task.task_key.split('-')[-1]) + 1
            else:
                num = 1
            self.task_key = f"{self.project.key}-{num:04d}"
        super().save(*args, **kwargs)

class Sprint(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.name} ({self.project.key})"
    
    @property
    def velocity(self):
        completed_tasks = self.tasks.filter(status='DONE')
        return sum(task.story_points for task in completed_tasks)

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.task}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')
    tasks = models.ManyToManyField(Task, related_name='tags', blank=True)
    
    def __str__(self):
        return self.name

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file_name

class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelogs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    logged_at = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Key Features

**Project Management**
- Create and manage projects
- Team member management
- Project roles and permissions
- Public/private visibility

**Task Management**
- Create tasks, bugs, features
- Task hierarchy (parent/subtask)
- Task assignments
- Priority and status management
- Due dates and reminders

**Sprint Management**
- Sprint planning and execution
- Sprint backlog
- Velocity tracking

**Collaboration**
- Comments and discussions
- File attachments
- Activity tracking

**Dashboard & Reports**
- Project overview dashboard
- Task statistics
- Progress tracking

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject project_manager
cd project_manager
python manage.py startapp projects
```

**Step 2: Create Custom Manager**
```python
# projects/managers.py
from django.db import models

class TaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def by_status(self, status):
        return self.filter(status=status)
    
    def by_assignee(self, user):
        return self.filter(assignee=user)
    
    def overdue(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.filter(
            due_date__lt=timezone.now().date(),
            status__in=['TODO', 'IN_PROGRESS']
        )
```

**Step 3: Create Models**
```python
# projects/models.py
# (Paste all model code from above)
```

**Step 4: Create Views**
```python
# projects/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Project, Task, Comment
from .forms import TaskForm

@login_required
def dashboard(request):
    projects = Project.objects.filter(
        models.Q(owner=request.user) | models.Q(members=request.user)
    ).distinct()
    
    my_tasks = Task.objects.filter(assignee=request.user)
    overdue_tasks = my_tasks.overdue()
    
    stats = {
        'total_projects': projects.count(),
        'active_projects': projects.filter(status='ACTIVE').count(),
        'total_tasks': my_tasks.count(),
        'completed_tasks': my_tasks.filter(status='DONE').count(),
        'overdue_tasks': overdue_tasks.count(),
    }
    
    return render(request, 'projects/dashboard.html', {
        'projects': projects,
        'stats': stats,
        'my_tasks': my_tasks.order_by('-updated_at')[:5],
        'overdue_tasks': overdue_tasks,
    })

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    
    def get_queryset(self):
        return Project.objects.filter(
            models.Q(owner=self.request.user) |
            models.Q(members=self.request.user) |
            models.Q(is_public=True)
        ).distinct()

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.select_related('assignee', 'reporter').all()
        context['sprints'] = self.object.sprints.all()
        return context

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'
    
    def form_valid(self, form):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.project = project
        form.instance.reporter = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['project_id']})

@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(task=task, author=request.user, content=content)
    return redirect('task_detail', pk=task_id)
```

**Step 5: Configure URLs**
```python
# projects/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:project_id>/tasks/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:task_id>/comment/', views.add_comment, name='add_comment'),
]
```

**Step 6: Configure Admin**
```python
# projects/admin.py
from django.contrib import admin
from .models import Project, Task, Sprint, Comment, Tag, Attachment, TimeLog

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'owner', 'status', 'start_date']
    list_filter = ['status', 'is_public']
    search_fields = ['name', 'key', 'owner__username']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_key', 'summary', 'project', 'assignee', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['summary', 'task_key', 'assignee__username']

admin.site.register(Sprint)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Attachment)
admin.site.register(TimeLog)
```

**Step 7: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Kanban Board**: Drag-and-drop task management
2. **Gantt Chart**: Visual project timeline
3. **Wiki/Documentation**: Project documentation
4. **Time Tracking Reports**: Detailed time analytics
5. **Slack Integration**: Team communication
6. **GitHub Integration**: Link commits to tasks

---

## 5. Blog Platform with CMS Features

### Overview

Build a full-featured blog platform with article management, categories, tags, comments, user profiles, rich text editing, and an admin CMS. This project teaches Django forms, template inheritance, file handling, and content management.

### Learning Objectives

- Rich text editing with CKEditor
- Image processing with Pillow
- User profile management
- Comment system with threading
- Tagging system
- Search functionality
- RSS/Atom feeds
- Sitemap generation

### Tech Stack & Dependencies

```
django>=5.0
django-ckeditor>=6.5
pillow>=10.0
django-taggit>=3.1
django-hitcount>=3.0
django-sitemaps>=2.6
```

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('ARCHIVED', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = RichTextField()
    excerpt = models.TextField(max_length=500, blank=True)
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if self.status == 'PUBLISHED' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = RichTextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    github = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class PostRevision(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='revisions')
    title = models.CharField(max_length=200)
    content = RichTextField()
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Key Features

**Article Management**
- Rich text editing with images
- Featured posts
- Post scheduling
- Draft/publish workflow
- Post revisions

**Categorization**
- Hierarchical categories
- Tags for posts
- Category pages
- Tag cloud

**Comments**
- Threaded comments
- Comment moderation
- Reply notifications

**User Features**
- User registration
- Profile management
- Author profiles

**SEO Features**
- Meta descriptions
- Sitemap
- RSS feeds

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject blog_project
cd blog_project
python manage.py startapp blog
```

**Step 2: Configure Settings**
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'taggit',
    'hitcount',
    'blog',
]

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 300,
    },
}
```

**Step 3: Create Views**
```python
# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from hitcount.views import HitCountDetailView
from .models import Post, Category, Comment, Profile
from .forms import PostForm, CommentForm

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(status='PUBLISHED')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent__isnull=True)
        return context

class PostDetailView(HitCountDetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    count_hit = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            parent__isnull=True, is_approved=True
        ).select_related('author')
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=post.slug)
    return redirect('post_detail', slug=post.slug)

def search(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()
    else:
        posts = Post.objects.none()
    return render(request, 'blog/search.html', {'posts': posts, 'query': query})
```

**Step 4: Configure URLs**
```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('search/', views.search, name='search'),
]
```

**Step 5: Configure Admin**
```python
# blog/admin.py
from django.contrib import admin
from .models import Post, Category, Page, Comment, Profile, Subscriber, PostRevision

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'view_count']
    list_filter = ['status', 'category', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content', 'author__username']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Page)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Subscriber)
admin.site.register(PostRevision)
```

**Step 6: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Dark Mode**: Theme switching
2. **Code Highlighting**: Syntax highlighting
3. **Related Posts**: ML-based recommendations
4. **Newsletter**: Email campaigns
5. **API**: REST API for mobile app
6. **Multi-language**: Internationalization

---

## 6. Social Media Clone

### Overview

Build a social media platform similar to Twitter with posts, likes, comments, follows, direct messages, notifications, and user profiles. This project teaches Django's authentication system, complex relationships, and real-time features.

### Learning Objectives

- User following/follower system
- Like and reaction system
- Real-time notifications
- Direct messaging
- Feed generation
- Activity streams
- Media handling

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=160, blank=True)
    location = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    @property
    def followers_count(self):
        return self.user.followers.count()
    
    @property
    def following_count(self):
        return self.user.following.count()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=280)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()

class Like(models.Model):
    REACTION_CHOICES = [
        ('LIKE', 'Like'), ('LOVE', 'Love'), ('HAHA', 'Haha'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES, default='LIKE')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']

class Notification(models.Model):
    TYPE_CHOICES = [
        ('LIKE', 'Like'), ('COMMENT', 'Comment'), ('FOLLOW', 'Follow'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name='hashtags', blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
```

### Key Features

**Posts**
- Create text posts with images
- Like and react to posts
- Comment on posts
- Hashtag support

**User Profiles**
- Profile customization
- Follower/following system
- Profile verification

**Feed**
- Personalized feed
- Trending hashtags
- Search functionality

**Notifications**
- Real-time notifications
- Activity tracking

**Direct Messages**
- Private messaging
- Conversation threads

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject social_project
cd social_project
python manage.py startapp social
```

**Step 2: Create Signals**
```python
# social/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, Like, Comment, Follow

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='LIKE',
            post=instance.post
        )

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='FOLLOW'
        )
```

**Step 3: Create Views**
```python
# social/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, User, Profile, Follow, Like, Comment, Notification, Hashtag

@login_required
def feed(request):
    following = request.user.following.all().values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(user__in=following) | Q(user=request.user)
    ).select_related('user').order_by('-created_at')
    return render(request, 'social/feed.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        post = Post.objects.create(user=request.user, content=content, image=image)
        
        import re
        hashtags = re.findall(r'#(\w+)', content)
        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name)
            tag.posts.add(post)
            tag.usage_count = tag.posts.count()
            tag.save()
        
        return JsonResponse({'success': True, 'post_id': post.id})
    return JsonResponse({'success': False})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        return JsonResponse({'liked': False, 'count': post.likes_count})
    return JsonResponse({'liked': True, 'count': post.likes_count})

@login_required
def follow_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        return JsonResponse({'success': False, 'error': 'Cannot follow yourself'})
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user)
    if not created:
        follow.delete()
        return JsonResponse({'following': False})
    return JsonResponse({'following': True})

@login_required
def notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'social/notifications.html', {'notifications': notifications})

def hashtag_detail(request, tag_name):
    hashtag = get_object_or_404(Hashtag, name=tag_name)
    posts = hashtag.posts.order_by('-created_at')
    return render(request, 'social/hashtag.html', {'hashtag': hashtag, 'posts': posts})
```

**Step 4: Configure URLs**
```python
# social/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('user/<str:username>/', views.profile_detail, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('hashtag/<str:tag_name>/', views.hashtag_detail, name='hashtag'),
]
```

**Step 5: Configure Admin**
```python
# social/admin.py
from django.contrib import admin
from .models import Profile, Post, Like, Comment, Follow, Notification, Message, Hashtag

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'joined_at', 'is_verified']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read']

admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Message)
admin.site.register(Hashtag)
```

**Step 6: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Direct Messages**: Real-time chat with Channels
2. **Media Optimization**: Image compression
3. **Analytics**: User engagement metrics
4. **Content Moderation**: AI-based filtering
5. **API**: Mobile app support
6. **Push Notifications**: Mobile push

---

## 7. Online Learning Management System

### Overview

Build a comprehensive LMS with course creation, video lessons, quizzes, progress tracking, certificates, and student management.

### Learning Objectives

- Course and curriculum management
- Video streaming integration
- Quiz and assessment system
- Progress tracking
- Certificate generation
- Payment integration for paid courses

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'), ('INTERMEDIATE', 'Intermediate'), ('ADVANCED', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('PUBLISHED', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='BEGINNER')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    requirements = models.TextField()
    what_you_will_learn = models.TextField()
    is_featured = models.BooleanField(default=False)
    enrollment_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('VIDEO', 'Video'), ('TEXT', 'Text'), ('QUIZ', 'Quiz'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='VIDEO')
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField()
    passing_score = models.PositiveIntegerField(default=70)
    time_limit = models.PositiveIntegerField(default=30)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MULTIPLE_CHOICE', 'Multiple Choice'), ('TRUE_FALSE', 'True/False'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student} - {self.course}"

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']

class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField()

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'student']

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/')
    
    def __str__(self):
        return f"Certificate for {self.student} - {self.course}"
```

### Key Features

**Course Management**
- Course creation with modules and lessons
- Rich content support
- Video integration

**Learning Features**
- Video lessons with progress tracking
- Text lessons
- Quizzes and assessments

**Progress Tracking**
- Lesson completion tracking
- Quiz scores and attempts
- Course progress percentage

**Reviews and Ratings**
- Course reviews
- Star ratings

**Certificates**
- Auto-generated certificates
- Certificate verification

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject lms_project
cd lms_project
python manage.py startapp courses
```

**Step 2: Create Views**
```python
# courses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from .models import Course, Module, Lesson, Enrollment, LessonProgress, Quiz, QuizAttempt

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(status='PUBLISHED').select_related('instructor', 'category')

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related('lessons')
        context['reviews'] = self.object.reviews.all()
        return context

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )
    if created:
        course.enrollment_count += 1
        course.save()
    return redirect('course_content', course_id=course.id, lesson_id=course.modules.first().lessons.first().id)

@login_required
def course_content(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.get(student=request.user, course=course)
    
    if request.method == 'POST':
        is_completed = request.POST.get('is_completed') == 'true'
        progress, created = LessonProgress.objects.update_or_create(
            enrollment=enrollment, lesson=lesson,
            defaults={'is_completed': is_completed}
        )
        
        if is_completed:
            total_lessons = course.modules.aggregate(
                total=models.Sound('lessons')
            )['total'] or 0
            completed_lessons = enrollment.lesson_progress.filter(is_completed=True).count()
            enrollment.progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            enrollment.save()
        
        return JsonResponse({'success': True})
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'modules': course.modules.prefetch_related('lessons'),
    }
    return render(request, 'courses/content.html', context)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    enrollment = Enrollment.objects.get(student=request.user, course=quiz.lesson.module.course)
    
    if request.method == 'POST':
        answers = {}
        correct_count = 0
        total_questions = quiz.questions.count()
        
        for question in quiz.questions.all():
            selected_answer = request.POST.get(f'question_{question.id}')
            answers[question.id] = selected_answer
            
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer and str(correct_answer.id) == selected_answer:
                correct_count += 1
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        passed = score >= quiz.passing_score
        
        QuizAttempt.objects.create(
            enrollment=enrollment,
            quiz=quiz,
            score=score,
            passed=passed,
            started_at=timezone.now(),
            answers=answers
        )
        
        if passed:
            return redirect('quiz_result', attempt_id=QuizAttempt.objects.last().id)
        else:
            return render(request, 'courses/quiz_failed.html', {'quiz': quiz, 'score': score})
    
    return render(request, 'courses/quiz.html', {'quiz': quiz})
```

**Step 3: Configure URLs**
```python
# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/<int:lesson_id>/', views.course_content, name='course_content'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
]
```

**Step 4: Configure Admin**
```python
# courses/admin.py
from django.contrib import admin
from .models import Category, Course, Module, Lesson, Quiz, Question, Answer, Enrollment, LessonProgress, QuizAttempt, Review, Certificate

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'status', 'price', 'enrollment_count']
    list_filter = ['status', 'level', 'category']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'order', 'is_published']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'progress', 'enrolled_at']

admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(LessonProgress)
admin.site.register(QuizAttempt)
admin.site.register(Review)
admin.site.register(Certificate)
```

**Step 5: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Video Hosting**: AWS S3 and CloudFront
2. **Live Sessions**: Django Channels for live classes
3. **Discussion Forums**: Course-specific discussions
4. **Assignment System**: File uploads and grading
5. **Certificates**: PDF generation with ReportLab
6. **Payment Integration**: Stripe for paid courses

---

## 8. Restaurant Reservation System

### Overview

Build a restaurant reservation system with table management, online booking, menu display, and customer management.

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=50, choices=[
        ('WINDOW', 'Window'), ('MAIN', 'Main Hall'),
        ('PATIO', 'Patio'), ('PRIVATE', 'Private Room')
    ])
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Table {self.table_number}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    party_size = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['table', 'date', 'time']
    
    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.date}"

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    allergens = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('PREPARING', 'Preparing'),
        ('READY', 'Ready'), ('SERVED', 'Served'), ('COMPLETED', 'Completed'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.table}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    
    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    total_visits = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferences = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
```

### Key Features

- Online table reservations
- Table management and availability
- Menu display with categories
- Order management
- Customer loyalty tracking
- Analytics dashboard

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject restaurant_project
cd restaurant_project
python manage.py startapp reservations
```

**Step 2: Create Views**
```python
# reservations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Table, Reservation, MenuCategory, MenuItem, Order, OrderItem
from datetime import date, datetime, timedelta

def home(request):
    categories = MenuCategory.objects.all()
    return render(request, 'reservations/home.html', {'categories': categories})

def menu(request):
    categories = MenuCategory.objects.prefetch_related('items').all()
    return render(request, 'reservations/menu.html', {'categories': categories})

def check_availability(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        party_size = int(request.GET.get('party_size', 2))
        
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        selected_time = datetime.strptime(time_str, '%H:%M').time()
        
        reserved_tables = Reservation.objects.filter(
            date=selected_date,
            time=selected_time,
            status__in=['PENDING', 'CONFIRMED']
        ).values_list('table_id', flat=True)
        
        available_tables = Table.objects.filter(
            capacity__gte=party_size,
            is_available=True
        ).exclude(id__in=reserved_tables)
        
        return JsonResponse({
            'available': list(available_tables.values('id', 'table_number', 'capacity', 'location'))
        })

@require_POST
def make_reservation(request):
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')
    table_id = request.POST.get('table')
    date_str = request.POST.get('date')
    time_str = request.POST.get('time')
    party_size = int(request.POST.get('party_size'))
    special_requests = request.POST.get('special_requests', '')
    
    table = get_object_or_404(Table, id=table_id)
    reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    reservation_time = datetime.strptime(time_str, '%H:%M').time()
    
    reservation = Reservation.objects.create(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        table=table,
        date=reservation_date,
        time=reservation_time,
        party_size=party_size,
        special_requests=special_requests
    )
    
    return redirect('reservation_confirmation', reservation_id=reservation.id)

@login_required
def table_management(request):
    tables = Table.objects.all()
    today = date.today()
    reservations = Reservation.objects.filter(date=today).order_by('time')
    return render(request, 'reservations/table_management.html', {
        'tables': tables,
        'reservations': reservations
    })

@login_required
def update_reservation_status(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.status = request.POST.get('status')
        reservation.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
```

**Step 3: Configure URLs**
```python
# reservations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('reservation-confirmation/<int:reservation_id>/', views.reservation_confirmation, name='reservation_confirmation'),
    path('tables/', views.table_management, name='table_management'),
    path('reservation/<int:reservation_id>/update/', views.update_reservation_status, name='update_reservation'),
]
```

**Step 4: Configure Admin**
```python
# reservations/admin.py
from django.contrib import admin
from .models import Table, Reservation, MenuCategory, MenuItem, Order, OrderItem, Customer

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'capacity', 'location', 'is_available']
    list_filter = ['location', 'is_available']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'table', 'date', 'time', 'status', 'party_size']
    list_filter = ['status', 'date', 'table']
    date_hierarchy = 'date'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_vegetarian']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_vegan']

admin.site.register(MenuCategory)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Customer)
```

**Step 5: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Online Ordering**: Order food for delivery/takeaway
2. **Kitchen Display**: Real-time order display for kitchen
3. **Payment Integration**: Online payment for deposits
4. **SMS Notifications**: Twilio integration for reminders
5. **Analytics**: Sales and reservation reports
6. **Multi-restaurant**: Support for multiple locations

---

## 9. Job Portal

### Overview

Build a job portal where employers can post jobs and job seekers can search and apply for positions.

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    company_size = models.CharField(max_length=50, choices=[
        ('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'),
        ('201-500', '201-500'), ('500+', '500+')
    ])
    location = models.CharField(max_length=200)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'), ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'), ('INTERNSHIP', 'Internship'), ('REMOTE', 'Remote')
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('CLOSED', 'Closed'), ('FILLED', 'Filled')
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    remote_type = models.CharField(max_length=20, choices=[
        ('ONSITE', 'On-site'), ('REMOTE', 'Remote'), ('HYBRID', 'Hybrid')
    ], default='ONSITE')
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    experience_required = models.CharField(max_length=50)
    education_required = models.CharField(max_length=100)
    skills_required = models.TextField()
    benefits = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    application_deadline = models.DateField()
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"

class Applicant(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'), ('REVIEWING', 'Reviewing'),
        ('SHORTLISTED', 'Shortlisted'), ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'), ('REJECTED', 'Rejected'), ('WITHDRAWN', 'Withdrawn')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'job']
    
    def __str__(self):
        return f"{self.user} applied for {self.job}"

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='resumes/')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letters')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='cover_letters')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'job']

class JobAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    keywords = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Alert for {self.keywords} by {self.user}"

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'job']
```

### Key Features

- Company profiles and verification
- Job posting and management
- Job search with filters
- Resume and cover letter management
- Application tracking
- Job alerts
- Saved jobs

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject jobportal_project
cd jobportal_project
python manage.py startapp jobs
```

**Step 2: Create Views**
```python
# jobs/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Q
from .models import Job, Company, Applicant, Resume, SavedJob, JobAlert

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        jobs = Job.objects.filter(status='ACTIVE')
        
        search = self.request.GET.get('q')
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(skills_required__icontains=search)
            )
        
        location = self.request.GET.get('location')
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        job_type = self.request.GET.get('type')
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        remote = self.request.GET.get('remote')
        if remote:
            jobs = jobs.filter(remote_type=remote)
        
        return jobs.select_related('company')

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_jobs'] = Job.objects.filter(
            status='ACTIVE',
            title__icontains=self.object.title.split()[0]
        ).exclude(id=self.object.id)[:5]
        return context

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        resume_id = request.POST.get('resume')
        cover_letter = request.POST.get('cover_letter', '')
        
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        applicant, created = Applicant.objects.get_or_create(
            user=request.user, job=job,
            defaults={'status': 'APPLIED'}
        )
        
        if not created:
            return JsonResponse({'success': False, 'message': 'Already applied'})
        
        job.views_count += 1
        job.save()
        
        return JsonResponse({'success': True, 'message': 'Application submitted successfully'})
    
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'jobs/apply.html', {'job': job, 'resumes': resumes})

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        saved.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})

@login_required
def my_applications(request):
    applications = Applicant.objects.filter(
        user=request.user
    ).select_related('job', 'job__company').order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def employer_dashboard(request):
    company = get_object_or_404(Company, user=request.user)
    jobs = Job.objects.filter(company=company)
    total_applicants = Applicant.objects.filter(job__company=company).count()
    recent_applicants = Applicant.objects.filter(
        job__company=company
    ).select_related('user', 'job').order_by('-applied_at')[:10]
    return render(request, 'jobs/employer_dashboard.html', {
        'company': company,
        'jobs': jobs,
        'total_applicants': total_applicants,
        'recent_applicants': recent_applicants
    })

@login_required
def create_job(request):
    company = get_object_or_404(Company, user=request.user)
    if request.method == 'POST':
        job = Job.objects.create(
            company=company,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities'),
            job_type=request.POST.get('job_type'),
            location=request.POST.get('location'),
            remote_type=request.POST.get('remote_type'),
            salary_min=request.POST.get('salary_min'),
            salary_max=request.POST.get('salary_max'),
            experience_required=request.POST.get('experience_required'),
            education_required=request.POST.get('education_required'),
            skills_required=request.POST.get('skills_required'),
            benefits=request.POST.get('benefits', ''),
            application_deadline=request.POST.get('application_deadline'),
            status='ACTIVE'
        )
        return redirect('employer_dashboard')
    return render(request, 'jobs/create_job.html', {'company': company})
```

**Step 3: Configure URLs**
```python
# jobs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/save/', views.save_job, name='save_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/create-job/', views.create_job, name='create_job'),
]
```

**Step 4: Configure Admin**
```python
# jobs/admin.py
from django.contrib import admin
from .models import Job, Company, Applicant, Resume, CoverLetter, JobAlert, SavedJob

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'company_size', 'location', 'is_verified']
    search_fields = ['name', 'industry']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'location', 'status', 'application_deadline']
    list_filter = ['status', 'job_type', 'remote_type', 'company']
    search_fields = ['title', 'company__name']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['user__username', 'job__title']

admin.site.register(Resume)
admin.site.register(CoverLetter)
admin.site.register(JobAlert)
admin.site.register(SavedJob)
```

**Step 5: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Resume Builder**: Interactive resume creation
2. **Interview Scheduling**: Calendar integration
3. **Video Interviews**: Django Channels for interviews
4. **Analytics**: Application statistics
5. **Premium Jobs**: Paid job listings
6. **Candidate Matching**: ML-based job recommendations

---

## 10. Real Estate Listing Platform

### Overview

Build a real estate platform with property listings, search filters, agent management, and inquiry forms.

### Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class PropertyType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Property(models.Model):
    STATUS_CHOICES = [
        ('FOR_SALE', 'For Sale'), ('FOR_RENT', 'For Rent'), ('SOLD', 'Sold'), ('RENTED', 'Rented')
    ]
    
    LISTING_TYPE_CHOICES = [
        ('FEATURED', 'Featured'), ('PREMIUM', 'Premium'), ('REGULAR', 'Regular')
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FOR_SALE')
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='REGULAR')
    
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    
    price = models.DecimalField(max_digits=14, decimal_places=2)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    square_feet = models.PositiveIntegerField()
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    year_built = models.PositiveIntegerField(blank=True, null=True)
    
    features = models.TextField()
    amenities = models.TextField()
    
    images = models.ImageField(upload_to='properties/', blank=True, null=True)
    additional_images = models.JSONField(default=list)
    
    has_garage = models.BooleanField(default=False)
    garage_spaces = models.PositiveIntegerField(default=0)
    has_pool = models.BooleanField(default=False)
    has_basement = models.BooleanField(default=False)
    cooling_system = models.CharField(max_length=100, blank=True)
    heating_system = models.CharField(max_length=100, blank=True)
    
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    agency = models.ForeignKey('Agency', on_delete=models.SET_NULL, null=True, blank=True)
    
    views_count = models.PositiveIntegerField(default=0)
    inquiry_count = models.PositiveIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Agency(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='agencies/', blank=True, null=True)
    description = models.TextField()
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    license_number = models.CharField(max_length=50)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    agents_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PropertyInquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=20, choices=[
        ('SCHEDULE_VIEWING', 'Schedule Viewing'), ('MORE_INFO', 'More Information'),
        ('OFFER', 'Make an Offer'), ('GENERAL', 'General Inquiry')
    ], default='MORE_INFO')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inquiry from {self.name} for {self.property}"

class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'property']

class PropertySearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    keywords = models.CharField(max_length=200, blank=True)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    min_price = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    max_price = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    min_sqft = models.PositiveIntegerField(blank=True, null=True)
    max_sqft = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Search by {self.user}"

class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    description = models.TextField()
    median_home_price = models.DecimalField(max_digits=14, decimal_places=2)
    crime_rate = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')
    ], default='MEDIUM')
    school_rating = models.PositiveIntegerField(default=0)
    walk_score = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name}, {self.city}"
```

### Key Features

- Property listings with photos
- Advanced search and filters
- Agent and agency profiles
- Inquiry management
- Saved properties
- Neighborhood information
- Price history tracking

### Step-by-Step Implementation

**Step 1: Project Setup**
```bash
django-admin startproject realestate_project
cd realestate_project
python manage.py startapp properties
```

**Step 2: Create Views**
```python
# properties/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q, Avg
from .models import Property, PropertyType, PropertyInquiry, SavedProperty, Neighborhood

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 20
    
    def get_queryset(self):
        properties = Property.objects.filter(is_active=True)
        
        search = self.request.GET.get('q')
        if search:
            properties = properties.filter(
                Q(title__icontains=search) |
                Q(address__icontains=search) |
                Q(city__icontains=search)
            )
        
        property_type = self.request.GET.get('type')
        if property_type:
            properties = properties.filter(property_type_id=property_type)
        
        status = self.request.GET.get('status')
        if status:
            properties = properties.filter(status=status)
        
        city = self.request.GET.get('city')
        if city:
            properties = properties.filter(city__icontains=city)
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        bedrooms = self.request.GET.get('bedrooms')
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
        
        return properties.select_related('property_type', 'agent')

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.views_count += 1
        self.object.save()
        
        context['similar_properties'] = Property.objects.filter(
            is_active=True,
            property_type=self.object.property_type,
            city=self.object.city
        ).exclude(id=self.object.id)[:6]
        
        return context

@login_required
def save_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    saved, created = SavedProperty.objects.get_or_create(user=request.user, property=property)
    
    if not created:
        saved.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})

def inquiry(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        PropertyInquiry.objects.create(
            property=property,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            message=request.POST.get('message'),
            inquiry_type=request.POST.get('inquiry_type', 'MORE_INFO')
        )
        property.inquiry_count += 1
        property.save()
        return redirect('inquiry_thank_you')
    
    return render(request, 'properties/inquiry.html', {'property': property})

@login_required
def saved_properties(request):
    saved = SavedProperty.objects.filter(user=request.user).select_related('property')
    return render(request, 'properties/saved_properties.html', {'saved': saved})

def neighborhood_info(request, city, state):
    neighborhood = get_object_or_404(
        Neighborhood, city__iexact=city, state__iexact=state
    )
    properties = Property.objects.filter(
        city__iexact=city,
        is_active=True
    ).aggregate(
        avg_price=Avg('price'),
        count=models.Count('id')
    )
    
    return render(request, 'properties/neighborhood.html', {
        'neighborhood': neighborhood,
        'stats': properties
    })
```

**Step 3: Configure URLs**
```python
# properties/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('property/<slug:slug>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('property/<int:property_id>/save/', views.save_property, name='save_property'),
    path('property/<int:property_id>/inquiry/', views.inquiry, name='inquiry'),
    path('saved-properties/', views.saved_properties, name='saved_properties'),
    path('neighborhood/<str:city>/<str:state>/', views.neighborhood_info, name='neighborhood'),
]
```

**Step 4: Configure Admin**
```python
# properties/admin.py
from django.contrib import admin
from .models import Property, PropertyType, Agency, PropertyInquiry, SavedProperty, Neighborhood

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'city', 'price', 'status', 'agent', 'is_active']
    list_filter = ['status', 'property_type', 'city', 'is_verified']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'address', 'city']

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Agency)
admin.site.register(PropertyInquiry)
admin.site.register(SavedProperty)
admin.site.register(Neighborhood)
```

**Step 5: Migrate and Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Extensions for Advanced Students

1. **Mortgage Calculator**: Payment calculations
2. **Virtual Tours**: 360° property tours
3. **Map Integration**: Google Maps API
4. **Price Alerts**: Price change notifications
5. **Agent Dashboard**: CRM for agents
6. **Premium Listings**: Featured properties

---

## 11-50. Remaining Projects (Condensed)

Due to the extensive nature of 50 full detailed projects, I'll provide condensed versions for projects 11-50.

### 11. Library Management System

**Overview**: Build a library system with book catalog, member management, borrowing/returning, and fines.

**Models**:
- Book, Author, Category, Member, Borrowing, Fine, Reservation, Shelf

**Features**:
- Book catalog with search
- Member registration
- Book borrowing/returning
- Overdue tracking and fines
- Book reservations
- ISBN barcode scanning

**Core Concepts**: File uploads, date handling, complex queries

---

### 12. Event Management System

**Overview**: Create an event platform for creating, managing, and attending events.

**Models**:
- Event, Venue, Speaker, Ticket, Registration, Schedule, Sponsor

**Features**:
- Event creation and management
- Ticket sales
- Attendee registration
- Schedule planning
- Speaker management
- Analytics dashboard

**Core Concepts**: Payment integration, QR codes, email notifications

---

### 13. Inventory Management System

**Overview**: Build an inventory system for tracking products, stock levels, and suppliers.

**Models**:
- Product, Category, Warehouse, Stock, Supplier, PurchaseOrder, SalesOrder, StockMovement

**Features**:
- Product catalog
- Stock level tracking
- Warehouse management
- Purchase orders
- Sales tracking
- Low stock alerts
- Barcode scanning

**Core Concepts**: Complex queries, reports, dashboard

---

### 14. Hotel Booking System

**Overview**: Create a hotel booking platform with room management and reservation system.

**Models**:
- Hotel, Room, RoomType, Reservation, Guest, RoomService, Payment, Review

**Features**:
- Room availability
- Online booking
- Payment processing
- Guest management
- Room service orders
- Review system

**Core Concepts**: Availability checking, calendar integration, payments

---

### 15. Fitness Tracking Application

**Overview**: Build a fitness tracking app for workouts, nutrition, and progress monitoring.

**Models**:
- UserProfile, Workout, Exercise, NutritionLog, Goal, Achievement, WorkoutPlan

**Features**:
- Workout logging
- Exercise library
- Nutrition tracking
- Goal setting
- Progress charts
- Social features

**Core Concepts**: Charts, mobile-responsive design, user engagement

---

### 16. Recipe Sharing Platform

**Overview**: Create a recipe sharing platform with categories,搜索, and user interactions.

**Models**:
- Recipe, Category, Ingredient, Instruction, Review, Cookbook, UserCollection

**Features**:
- Recipe catalog
- Advanced search
- Ingredient scaling
- Meal planning
- Shopping lists
- User collections

**Core Concepts**: Image handling, complex filtering, social features

---

### 17. Auction Platform

**Overview**: Build an online auction system for bidding on items.

**Models**:
- Auction, Bid, Category, Seller, Winner, Payment, Shipping

**Features**:
- Auction creation
- Real-time bidding
- Auction scheduling
- Winner notification
- Payment processing
- Shipping management

**Core Concepts**: Real-time updates, time-based logic, payments

---

### 18. News Aggregator

**Overview**: Create a news aggregation platform with RSS feeds and personalization.

**Models**:
- Article, Source, Category, UserFeed, Bookmark, ReadingHistory, Newsletter

**Features**:
- RSS feed aggregation
- Article categorization
- Personalized feed
- Bookmarking
- Reading history
- Newsletter subscription

**Core Concepts**: RSS parsing, personalization, caching

---

### 19. Online Code Editor

**Overview**: Build a web-based code editor with syntax highlighting and execution.

**Models**:
- Snippet, Language, ExecutionResult, UserCode, SavedCode

**Features**:
- Code editor
- Syntax highlighting
- Code execution
- Snippet sharing
- Version history
- Collaboration

**Core Concepts**: CodeMirror integration, sandbox execution, WebSocket

---

### 20. File Sharing Application

**Overview**: Create a file sharing platform with secure uploads and downloads.

**Models**:
- File, Folder, SharedLink, UserStorage, FileVersion, DownloadLog

**Features**:
- File upload/download
- Folder organization
- Share links
- Expiration dates
- Version control
- Storage tracking

**Core Concepts**: File handling, security, sharing logic

---

### 21. Poll/Voting System

**Overview**: Build a polling system for creating and participating in surveys.

**Models**:
- Poll, Question, Option, Vote, Voter, PollResult, PollShare

**Features**:
- Poll creation
- Multiple question types
- Voting system
- Results visualization
- Poll sharing
- Analytics

**Core Concepts**: Voting logic, charts, sharing

---

### 22. Note-Taking Application

**Overview**: Create a note-taking app with organization and collaboration features.

**Models**:
- Note, Notebook, Tag, Checklist, Collaboration, NoteVersion

**Features**:
- Rich text notes
- Notebooks and tags
- Checklists
- Collaboration
- Search
- Export

**Core Concepts**: Rich text, organization, real-time collaboration

---

### 23. Forum/Discussion Board

**Overview**: Build a discussion forum with categories, threads, and moderation.

**Models**:
- Forum, Thread, Post, Category, Moderator, Report, Badge

**Features**:
- Category management
- Thread creation
- Post replies
- Moderation tools
- User badges
- Search

**Core Concepts**: Hierarchical data, moderation, user reputation

---

### 24. Photo Gallery Application

**Overview**: Create a photo gallery with albums, sharing, and basic editing.

**Models**:
- Photo, Album, Tag, Comment, Like, Gallery, PhotoEdit

**Features**:
- Photo upload
- Album organization
- Tagging
- Comments and likes
- Basic editing
- Sharing

**Core Concepts**: Image processing, albums, social features

---

### 25. Music Streaming Service

**Overview**: Build a music streaming platform with playlists and library management.

**Models**:
- Song, Album, Artist, Playlist, PlaylistSong, PlayHistory, Like

**Features**:
- Song upload
- Album/artist pages
- Playlist creation
- Play history
- Shuffle/repeat
- Radio mode

**Core Concepts**: Audio streaming, large file handling, playlists

---

### 26. Video Streaming Platform

**Overview**: Create a video streaming platform like YouTube with upload and playback.

**Models**:
- Video, Channel, Playlist, Comment, Like, Subscription, ViewHistory

**Features**:
- Video upload
- Video playback
- Channel pages
- Playlists
- Comments
- Subscriptions

**Core Concepts**: Video processing, streaming, thumbnails

---

### 27. Appointment Scheduling System

**Overview**: Build an appointment booking system with calendar integration.

**Models**:
- Service, Provider, Appointment, TimeSlot, Booking, Reminder

**Features**:
- Service selection
- Provider selection
- Calendar view
- Booking confirmation
- Reminders
- Cancellation

**Core Concepts**: Calendar integration, time slots, notifications

---

### 28. Multi-Vendor Marketplace

**Overview**: Create an e-commerce platform with multiple sellers.

**Models**:
- Vendor, Product, Order, OrderItem, Commission, Review, Payout

**Features**:
- Vendor registration
- Product management
- Order processing
- Commission tracking
- Vendor dashboard
- Payouts

**Core Concepts**: Multi-tenancy, payments, vendor management

---

### 29. Customer Relationship Management (CRM)

**Overview**: Build a CRM system for managing customer relationships.

**Models**:
- Contact, Company, Deal, Activity, Task, Note, Pipeline, Lead

**Features**:
- Contact management
- Deal tracking
- Activity logging
- Task management
- Pipeline visualization
- Reporting

**Core Concepts**: Pipeline logic, activities, reporting

---

### 30. Content Management System (CMS)

**Overview**: Create a flexible CMS for managing various content types.

**Models**:
- Page, ContentBlock, Template, Media, Navigation, UserPermission

**Features**:
- Page builder
- Content blocks
- Template system
- Media library
- Navigation management
- User roles

**Core Concepts**: Dynamic content, templates, media handling

---

### 31. Email Marketing Platform

**Overview**: Build an email marketing system with campaign management.

**Models**:
- Campaign, EmailTemplate, Subscriber, EmailList, EmailLog, Analytics

**Features**:
- Campaign creation
- Template builder
- Subscriber management
- Email scheduling
- Analytics
- A/B testing

**Core Concepts**: Email sending, templates, analytics

---

### 32. Analytics Dashboard

**Overview**: Create an analytics dashboard with data visualization.

**Models**:
- DataSource, Metric, Dashboard, Widget, Report, Alert

**Features**:
- Data connections
- Metric definition
- Dashboard creation
- Widget types
- Report generation
- Alert system

**Core Concepts**: Data visualization, charting, real-time updates

---

### 33. Bug Tracking System

**Overview**: Build a bug tracking system for software development teams.

**Models**:
- Issue, Project, Version, Component, Attachment, Comment, Workflow

**Features**:
- Issue creation
- Issue tracking
- Workflow management
- File attachments
- Comments
- Reports

**Core Concepts**: Workflow, permissions, notifications

---

### 34. Document Management System

**Overview**: Create a document management system with version control.

**Models**:
- Document, Folder, Version, Permission, Tag, Comment, Workflow

**Features**:
- Document upload
- Folder organization
- Version control
- Access permissions
- Search
- Workflow

**Core Concepts**: File handling, versioning, permissions

---

### 35. Online Examination System

**Overview**: Build an online examination platform with various question types.

**Models**:
- Exam, Question, Option, ExamSession, Result, Proctoring

**Features**:
- Exam creation
- Question bank
- Timed exams
- Results
- Proctoring
- Analytics

**Core Concepts**: Timed sessions, grading, security

---

### 36. Subscription Management System

**Overview**: Create a subscription management platform with billing.

**Models**:
- Plan, Subscription, Invoice, Payment, Usage, Feature

**Features**:
- Plan management
- Subscription handling
- Invoice generation
- Payment processing
- Usage tracking
- Feature access

**Core Concepts**: Subscriptions, billing, usage tracking

---

### 37. Support Ticket System

**Overview**: Build a support ticket system for customer service.

**Models**:
- Ticket, Category, Priority, Comment, Attachment, KnowledgeBase, SLA

**Features**:
- Ticket creation
- Ticket routing
- Comments
- File attachments
- Knowledge base
- SLA tracking

**Core Concepts**: Ticket workflow, prioritization, knowledge base

---

### 38. URL Shortener Service

**Overview**: Create a URL shortening service with analytics.

**Models**:
- ShortURL, Click, CustomAlias, User, Tag, Analytics

**Features**:
- URL shortening
- Custom aliases
- Click tracking
- Analytics
- QR codes
- API

**Core Concepts**: URL routing, analytics, caching

---

### 39. Weather Application

**Overview**: Build a weather application with forecasts and historical data.

**Models**:
- Location, CurrentWeather, Forecast, HistoricalData, Alert, UserPreference

**Features**:
- Current weather
- Forecast
- Historical data
- Weather alerts
- Location search
- API integration

**Core Concepts**: API integration, caching, data visualization

---

### 40. Currency Converter

**Overview**: Create a currency converter with exchange rates and historical data.

**Models**:
- Currency, ExchangeRate, ConversionHistory, Alert, UserPreference

**Features**:
- Currency conversion
- Exchange rates
- Historical rates
- Rate alerts
- API integration
- Charts

**Core Concepts**: API integration, caching, historical data

---

### 41. Flashcard Application

**Overview**: Build a flashcard app for learning with spaced repetition.

**Models**:
- Deck, Flashcard, StudySession, Progress, Achievement, Share

**Features**:
- Deck creation
- Flashcard management
- Spaced repetition
- Progress tracking
- Achievements
- Sharing

**Core Concepts**: Algorithm implementation, progress tracking

---

### 42. Budget Tracker

**Overview**: Create a personal budget tracking application.

**Models**:
- Account, Transaction, Category, Budget, Goal, Recurring

**Features**:
- Transaction logging
- Category management
- Budget setting
- Goal tracking
- Reports
- Export

**Core Concepts**: Charts, recurring transactions, reports

---

### 43. Travel Planning Application

**Overview**: Build a travel planning platform with itinerary management.

**Models**:
- Trip, Destination, Itinerary, Accommodation, Activity, Expense, PackingList

**Features**:
- Trip creation
- Itinerary planning
- Accommodation booking
- Activity planning
- Expense tracking
- Sharing

**Core Concepts**: Calendar integration, maps, sharing

---

### 44. Pet Adoption Platform

**Overview**: Create a pet adoption platform connecting shelters with adopters.

**Models**:
- Pet, Shelter, AdoptionApplication, Foster, MedicalRecord, Donation

**Features**:
- Pet listings
- Adoption applications
- Foster management
- Donation system
- Search/filter
- Success stories

**Core Concepts**: Application workflow, donations, CMS

---

### 45. Parking Reservation System

**Overview**: Build a parking reservation system with spot management.

**Models**:
- ParkingLot, Spot, Reservation, Vehicle, Payment, PricingRule

**Features**:
- Lot management
- Spot availability
- Online reservation
- Payment processing
- Real-time updates
- Analytics

**Core Concepts**: Availability logic, payments, maps

---

### 46. Delivery Tracking System

**Overview**: Create a delivery tracking platform with real-time updates.

**Models**:
- Package, Shipment, TrackingEvent, Carrier, Route, DeliveryProof

**Features**:
- Package tracking
- Status updates
- Carrier integration
- Route optimization
- Proof of delivery
- Notifications

**Core Concepts**: Real-time updates, carrier APIs, maps

---

### 47. Restaurant Management

**Overview**: Build a comprehensive restaurant management system.

**Models**:
- Menu, Order, Table, Reservation, Staff, Inventory, Report

**Features**:
- Order management
- Table management
- Kitchen display
- Inventory tracking
- Staff management
- Reports

**Core Concepts**: POS integration, kitchen workflow, inventory

---

### 48. Gym Membership Management

**Overview**: Create a gym management system with member tracking.

**Models**:
- Member, MembershipPlan, Attendance, Trainer, Class, Equipment, Payment

**Features**:
- Membership management
- Class scheduling
- Attendance tracking
- Trainer management
- Equipment maintenance
- Reports

**Core Concepts**: Scheduling, payments, attendance

---

### 49. Blood Donation Management

**Overview**: Build a blood donation platform connecting donors with recipients.

**Models**:
- Donor, Recipient, BloodRequest, DonationCamp, DonationRecord, Eligibility

**Features**:
- Donor registration
- Blood requests
- Donation camps
- Eligibility tracking
- Request matching
- Alerts

**Core Concepts**: Matching algorithm, eligibility, notifications

---

### 50. Alumni Network Platform

**Overview**: Create an alumni network platform for educational institutions.

**Models**:
- Alumnus, Batch, GraduationYear, Event, JobPosting, Donation, Mentorship

**Features**:
- Alumni directory
- Batch management
- Event management
- Job postings
- Donation tracking
- Mentorship program

**Core Concepts**: Directory, networking, events, donations

---

## General Implementation Tips for All Projects

### Setting Up Each Project

```bash
# Create new project
django-admin startproject projectname
cd projectname

# Create app
python manage.py startapp appname

# Configure settings
# Add app to INSTALLED_APPS

# Create models
# Define your models

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Common Django Commands

```bash
# Create model changes
python manage.py makemigrations appname

# View SQL for migrations
python manage.py sqlmigrate appname migration_name

# Run tests
python manage.py test

# Create fixtures
python manage.py dumpdata appname > fixtures/data.json

# Load fixtures
python manage.py loaddata fixtures/data.json

# Check for issues
python manage.py check

# Clear cache
python manage.py cache_clear
```

### Best Practices

1. **Use Class-Based Views** for CRUD operations
2. **Implement Custom Managers** for complex queries
3. **Use Signals** for decoupled operations
4. **Add Unit Tests** for all models and views
5. **Use Django Debug Toolbar** during development
6. **Implement Pagination** for list views
7. **Add Proper Error Handling** for all views
8. **Use Django's Built-in Auth** for user management
9. **Implement Caching** for frequently accessed data
10. **Use Environment Variables** for sensitive settings

### Deployment Considerations

1. **Use Whitenoise** for static files
2. **Configure Proper Database** for production
3. **Set Up Logging** for monitoring
4. **Implement Security Headers** (CSRF, XSS)
5. **Use HTTPS** in production
6. **Configure Celery** for background tasks
7. **Set Up S3** for media storage
8. **Implement CI/CD** pipeline
9. **Add Error Tracking** (Sentry)
10. **Set Up Monitoring** (Prometheus/Grafana)

---

## Conclusion

This comprehensive guide provides 50 intermediate-level Django projects suitable for internship training. Each project is designed to teach specific Django concepts while building real-world applications.

**Recommended Learning Path**:

1. **Beginner**: Start with Blog Platform, then Job Portal
2. **Intermediate**: Move to E-Commerce, then Real Estate
3. **Advanced**: Complete LMS, then Chat Application

**Key Skills Gained**:

- Database design and modeling
- User authentication and authorization
- File handling and media
- Payment integration
- Real-time features
- REST API development
- Performance optimization
- Deployment and DevOps

Students should complete these projects sequentially, building on skills learned in each one. Each project includes extensions for advanced students who want to go beyond the basics.

Good luck with your internship training program!
