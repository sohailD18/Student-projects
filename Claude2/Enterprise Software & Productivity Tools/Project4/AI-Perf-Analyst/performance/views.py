"""
Views for Employee Performance Analysis System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Employee, PerformanceRecord
from .analysis import (
    analyze_employee,
    get_dashboard_statistics,
    get_chart_data
)


def dashboard_view(request):
    """
    Main dashboard view with aggregate statistics
    """
    stats = get_dashboard_statistics()

    context = {
        'stats': stats,
        'page_title': 'Dashboard - Employee Performance Analysis'
    }
    return render(request, 'performance/dashboard.html', context)


def employee_list_view(request):
    """
    List all employees with their summary stats
    """
    employees = Employee.objects.all()

    # Add calculated metrics to each employee
    employee_data = []
    for emp in employees:
        employee_data.append({
            'id': emp.id,
            'name': emp.name,
            'department': emp.department,
            'role': emp.role,
            'join_date': emp.join_date,
            'record_count': emp.get_record_count(),
            'avg_efficiency': emp.get_average_efficiency(),
            'avg_quality': emp.get_average_quality(),
            'performance_category': emp.get_performance_category_display(),
            'category_class': get_category_class(emp.performance_category)
        })

    context = {
        'employees': employee_data,
        'page_title': 'Employees - Performance List'
    }
    return render(request, 'performance/employee_list.html', context)


def employee_detail_view(request, employee_id):
    """
    Detailed view of a single employee with AI analysis and charts
    """
    employee = get_object_or_404(Employee, id=employee_id)
    analysis = analyze_employee(employee_id)
    chart_data = get_chart_data(employee_id)

    # Get performance records for the table
    records = PerformanceRecord.objects.filter(employee=employee).order_by('-date')[:10]

    context = {
        'employee': employee,
        'analysis': analysis,
        'chart_data': chart_data,
        'records': records,
        'category_class': get_category_class(employee.performance_category),
        'page_title': f'{employee.name} - Performance Analysis'
    }
    return render(request, 'performance/employee_detail.html', context)


def add_employee_view(request):
    """
    Add a new employee
    """
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            department = request.POST.get('department')
            role = request.POST.get('role')
            join_date = request.POST.get('join_date')
            email = request.POST.get('email', '')

            if not all([name, department, role, join_date]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'performance/add_employee.html')

            employee = Employee.objects.create(
                name=name,
                department=department,
                role=role,
                join_date=datetime.strptime(join_date, '%Y-%m-%d').date(),
                email=email
            )

            messages.success(request, f'Employee "{name}" has been added successfully!')
            return redirect('employee_detail', employee_id=employee.id)

        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')

    context = {
        'page_title': 'Add New Employee'
    }
    return render(request, 'performance/add_employee.html', context)


def add_record_view(request):
    """
    Add a new performance record
    """
    if request.method == 'POST':
        try:
            employee_id = request.POST.get('employee')
            date = request.POST.get('date')
            tasks_completed = int(request.POST.get('tasks_completed', 0))
            efficiency = float(request.POST.get('efficiency', 5.0))
            quality = float(request.POST.get('quality', 5.0))
            hours_worked = float(request.POST.get('hours_worked', 8.0))
            manager_notes = request.POST.get('manager_notes', '')

            if not all([employee_id, date]):
                messages.error(request, 'Please select an employee and provide a date.')
                return render(request, 'performance/add_record.html')

            employee = get_object_or_404(Employee, id=employee_id)

            # Validate score ranges
            if not (1 <= efficiency <= 10):
                messages.error(request, 'Efficiency must be between 1 and 10.')
                return render(request, 'performance/add_record.html')

            if not (1 <= quality <= 10):
                messages.error(request, 'Quality must be between 1 and 10.')
                return render(request, 'performance/add_record.html')

            record = PerformanceRecord.objects.create(
                employee=employee,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                tasks_completed=tasks_completed,
                efficiency=efficiency,
                quality=quality,
                hours_worked=hours_worked,
                manager_notes=manager_notes
            )

            messages.success(request, f'Performance record for "{employee.name}" has been added successfully!')
            return redirect('employee_detail', employee_id=employee.id)

        except Exception as e:
            messages.error(request, f'Error adding record: {str(e)}')

    employees = Employee.objects.all()
    context = {
        'employees': employees,
        'page_title': 'Add Performance Record'
    }
    return render(request, 'performance/add_record.html', context)


def edit_record_view(request, record_id):
    """
    Edit an existing performance record
    """
    record = get_object_or_404(PerformanceRecord, id=record_id)

    if request.method == 'POST':
        try:
            date = request.POST.get('date')
            tasks_completed = int(request.POST.get('tasks_completed', 0))
            efficiency = float(request.POST.get('efficiency', 5.0))
            quality = float(request.POST.get('quality', 5.0))
            hours_worked = float(request.POST.get('hours_worked', 8.0))
            manager_notes = request.POST.get('manager_notes', '')

            if not date:
                messages.error(request, 'Please provide a date.')
                return render(request, 'performance/edit_record.html', {'record': record})

            # Validate score ranges
            if not (1 <= efficiency <= 10):
                messages.error(request, 'Efficiency must be between 1 and 10.')
                return render(request, 'performance/edit_record.html', {'record': record})

            if not (1 <= quality <= 10):
                messages.error(request, 'Quality must be between 1 and 10.')
                return render(request, 'performance/edit_record.html', {'record': record})

            record.date = datetime.strptime(date, '%Y-%m-%d').date()
            record.tasks_completed = tasks_completed
            record.efficiency = efficiency
            record.quality = quality
            record.hours_worked = hours_worked
            record.manager_notes = manager_notes
            record.save()

            messages.success(request, 'Performance record updated successfully!')
            return redirect('employee_detail', employee_id=record.employee.id)

        except Exception as e:
            messages.error(request, f'Error updating record: {str(e)}')

    context = {
        'record': record,
        'employee': record.employee,
        'page_title': f'Edit Record - {record.employee.name}'
    }
    return render(request, 'performance/edit_record.html', context)


def delete_record_view(request, record_id):
    """
    Delete a performance record
    """
    record = get_object_or_404(PerformanceRecord, id=record_id)
    employee_id = record.employee.id

    if request.method == 'POST':
        employee_name = record.employee.name
        record.delete()
        messages.success(request, f'Performance record for "{employee_name}" has been deleted.')
        return redirect('employee_detail', employee_id=employee_id)

    context = {
        'record': record,
        'page_title': 'Delete Performance Record'
    }
    return render(request, 'performance/delete_record.html', context)


def print_report_view(request, employee_id):
    """
    Generate a printable performance report
    """
    employee = get_object_or_404(Employee, id=employee_id)
    analysis = analyze_employee(employee_id)
    records = PerformanceRecord.objects.filter(employee=employee).order_by('-date')

    context = {
        'employee': employee,
        'analysis': analysis,
        'records': records,
        'generated_date': timezone.now().strftime('%Y-%m-%d %H:%M'),
        'page_title': f'Performance Report - {employee.name}'
    }
    return render(request, 'performance/print_report.html', context)


def get_category_class(category):
    """
    Get CSS class for performance category badge
    """
    category_classes = {
        'high_potential': 'badge-success',
        'needs_training': 'badge-danger',
        'stable': 'badge-info',
        'promotion_candidate': 'badge-warning'
    }
    return category_classes.get(category, 'badge-secondary')
