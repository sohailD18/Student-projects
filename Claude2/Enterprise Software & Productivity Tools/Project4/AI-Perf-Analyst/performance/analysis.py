"""
AI Analysis and Prediction Engine for Employee Performance
This module contains logic to analyze employee data and predict future performance
"""
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Avg, Sum
from .models import Employee, PerformanceRecord


def analyze_employee(employee_id):
    """
    Comprehensive analysis of an employee's performance data.

    Args:
        employee_id (int): The ID of the employee to analyze

    Returns:
        dict: Analysis results including predictions, trends, and recommendations
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return None

    # Fetch all performance records ordered by date
    records = PerformanceRecord.objects.filter(employee=employee).order_by('date')

    if not records.exists():
        return {
            'employee': employee,
            'has_data': False,
            'message': 'No performance records found for this employee.'
        }

    # Convert to pandas DataFrame for analysis
    data = [{
        'date': record.date,
        'tasks_completed': record.tasks_completed,
        'efficiency': record.efficiency,
        'quality': record.quality,
        'hours_worked': record.hours_worked,
        'overall_score': record.get_overall_score(),
        'productivity': record.get_productivity_score()
    } for record in records]

    df = pd.DataFrame(data)

    # Calculate basic statistics
    analysis = {
        'employee': employee,
        'has_data': True,
        'record_count': len(df),
        'date_range': {
            'start': records.first().date.strftime('%Y-%m-%d'),
            'end': records.last().date.strftime('%Y-%m-%d')
        }
    }

    # Average metrics
    analysis['averages'] = {
        'efficiency': round(df['efficiency'].mean(), 2),
        'quality': round(df['quality'].mean(), 2),
        'overall_score': round(df['overall_score'].mean(), 2),
        'tasks_per_day': round(df['tasks_completed'].mean(), 2),
        'hours_per_day': round(df['hours_worked'].mean(), 2),
        'productivity': round(df['productivity'].mean(), 2)
    }

    # Trend analysis
    if len(df) >= 2:
        # Calculate trends using linear regression slope
        df['day_number'] = range(len(df))

        # Simple linear regression for each metric
        def calculate_trend(series):
            x = df['day_number'].values
            y = series.values
            n = len(x)

            # Calculate slope (trend)
            x_mean = x.mean()
            y_mean = y.mean()
            numerator = ((x - x_mean) * (y - y_mean)).sum()
            denominator = ((x - x_mean) ** 2).sum()

            if denominator == 0:
                return 0
            slope = numerator / denominator
            return round(slope, 4)

        analysis['trends'] = {
            'efficiency_trend': calculate_trend(df['efficiency']),
            'quality_trend': calculate_trend(df['quality']),
            'productivity_trend': calculate_trend(df['productivity']),
            'overall_trend': calculate_trend(df['overall_score'])
        }

        # Trend interpretation
        analysis['trend_interpretation'] = {
            'efficiency': interpret_trend(analysis['trends']['efficiency_trend'], 'efficiency'),
            'quality': interpret_trend(analysis['trends']['quality_trend'], 'quality'),
            'productivity': interpret_trend(analysis['trends']['productivity_trend'], 'productivity')
        }

    # AI Prediction Engine
    analysis['prediction'] = predict_next_month_performance(df)

    # Strengths and Weaknesses identification
    analysis['strengths_weaknesses'] = identify_strengths_weaknesses(analysis['averages'])

    # Recommendation
    analysis['recommendation'] = generate_recommendation(analysis)

    # Performance category update
    category = determine_performance_category(analysis['averages'], analysis['trends'] if 'trends' in analysis else None)
    analysis['performance_category'] = category

    # Update employee's performance category
    employee.performance_category = category
    employee.save()

    return analysis


def predict_next_month_performance(df):
    """
    Predict next month's performance using weighted average and trend analysis.

    Args:
        df (pd.DataFrame): Historical performance data

    Returns:
        dict: Predicted metrics for next month
    """
    prediction = {}

    if len(df) >= 3:
        # Use last 3 records for prediction
        recent = df.tail(3)

        # Weighted average (more recent data gets higher weight)
        weights = [1, 2, 3][-len(recent):]

        def weighted_average(series):
            return (series * weights).sum() / sum(weights)

        prediction['predicted_efficiency'] = round(weighted_average(recent['efficiency']), 2)
        prediction['predicted_quality'] = round(weighted_average(recent['quality']), 2)
        prediction['predicted_overall_score'] = round((prediction['predicted_efficiency'] + prediction['predicted_quality']) / 2, 2)
        prediction['predicted_productivity'] = round(weighted_average(recent['productivity']), 2)

        # Confidence level based on data consistency
        efficiency_std = recent['efficiency'].std()
        quality_std = recent['quality'].std()

        # Lower standard deviation = higher confidence
        confidence = 100 - min((efficiency_std + quality_std) * 10, 50)
        prediction['confidence_level'] = round(confidence, 2)

    else:
        # Not enough data for accurate prediction
        prediction['predicted_efficiency'] = round(df['efficiency'].mean(), 2)
        prediction['predicted_quality'] = round(df['quality'].mean(), 2)
        prediction['predicted_overall_score'] = round(df['overall_score'].mean(), 2)
        prediction['predicted_productivity'] = round(df['productivity'].mean(), 2)
        prediction['confidence_level'] = round(len(df) * 20, 2)  # Lower confidence with less data

    return prediction


def identify_strengths_weaknesses(averages):
    """
    Identify employee strengths and areas for improvement based on metrics.

    Args:
        averages (dict): Average performance metrics

    Returns:
        dict: Lists of strengths and weaknesses
    """
    strengths = []
    weaknesses = []

    # Efficiency assessment
    if averages['efficiency'] >= 8.0:
        strengths.append({
            'area': 'Efficiency',
            'value': averages['efficiency'],
            'description': 'Consistently high efficiency in task completion'
        })
    elif averages['efficiency'] <= 5.0:
        weaknesses.append({
            'area': 'Efficiency',
            'value': averages['efficiency'],
            'description': 'Efficiency needs improvement - consider workflow optimization'
        })

    # Quality assessment
    if averages['quality'] >= 8.0:
        strengths.append({
            'area': 'Quality of Work',
            'value': averages['quality'],
            'description': 'Delivers high-quality work consistently'
        })
    elif averages['quality'] <= 5.0:
        weaknesses.append({
            'area': 'Quality of Work',
            'value': averages['quality'],
            'description': 'Quality issues detected - additional training recommended'
        })

    # Productivity assessment
    if averages['productivity'] >= 5.0:
        strengths.append({
            'area': 'Productivity',
            'value': averages['productivity'],
            'description': 'Excellent task completion rate per hour'
        })
    elif averages['productivity'] <= 2.0:
        weaknesses.append({
            'area': 'Productivity',
            'value': averages['productivity'],
            'description': 'Low task completion rate - needs focus improvement'
        })

    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'overall_assessment': 'Strong performer' if len(strengths) >= 2 else 'Needs development' if len(weaknesses) >= 2 else 'Balanced performance'
    }


def determine_performance_category(averages, trends=None):
    """
    Determine the performance category for an employee.

    Args:
        averages (dict): Average performance metrics
        trends (dict): Trend analysis (optional)

    Returns:
        str: Performance category
    """
    avg_efficiency = averages['efficiency']
    avg_quality = averages['quality']
    avg_score = averages['overall_score']

    # Check for promotion candidate
    if avg_efficiency >= 8.5 and avg_quality >= 8.5 and avg_score >= 8.5:
        return 'promotion_candidate'

    # Check for high potential
    if avg_score >= 7.5:
        if trends and trends.get('overall_trend', 0) > 0.1:
            return 'high_potential'
        return 'high_potential'

    # Check for needs training
    if avg_efficiency <= 5.0 or avg_quality <= 5.0:
        return 'needs_training'

    # Check for declining performance
    if trends and trends.get('overall_trend', 0) < -0.2:
        return 'needs_training'

    # Default to stable
    return 'stable'


def generate_recommendation(analysis):
    """
    Generate actionable recommendations based on analysis.

    Args:
        analysis (dict): Complete analysis results

    Returns:
        dict: Recommendations including action items and priority
    """
    averages = analysis['averages']
    prediction = analysis.get('prediction', {})
    strengths_weaknesses = analysis.get('strengths_weaknesses', {})

    recommendations = {
        'actions': [],
        'priority': 'medium',
        'summary': ''
    }

    # High performer recommendations
    if averages['overall_score'] >= 8.5:
        recommendations['actions'].append({
            'action': 'Consider for leadership or mentorship role',
            'priority': 'high',
            'category': 'recognition'
        })
        recommendations['actions'].append({
            'action': 'Assign more complex projects to leverage strengths',
            'priority': 'medium',
            'category': 'development'
        })
        recommendations['summary'] = 'Exceptional performer ready for advancement opportunities'

    # Needs training recommendations
    elif averages['quality'] <= 5.0:
        recommendations['actions'].append({
            'action': 'Schedule quality-focused training sessions',
            'priority': 'high',
            'category': 'training'
        })
        recommendations['actions'].append({
            'action': 'Implement peer review process for work output',
            'priority': 'high',
            'category': 'process'
        })
        recommendations['priority'] = 'high'
        recommendations['summary'] = 'Quality improvement needed - immediate action recommended'

    elif averages['efficiency'] <= 5.0:
        recommendations['actions'].append({
            'action': 'Review workload and task allocation',
            'priority': 'high',
            'category': 'management'
        })
        recommendations['actions'].append({
            'action': 'Provide time management training',
            'priority': 'medium',
            'category': 'training'
        })
        recommendations['priority'] = 'high'
        recommendations['summary'] = 'Efficiency improvements required - workflow assessment needed'

    # Stable performer recommendations
    else:
        recommendations['actions'].append({
            'action': 'Continue current development path',
            'priority': 'low',
            'category': 'maintenance'
        })

        if prediction.get('predicted_overall_score', 0) > averages['overall_score']:
            recommendations['actions'].append({
                'action': 'Positive trajectory - prepare for increased responsibility',
                'priority': 'medium',
                'category': 'development'
            })
            recommendations['summary'] = 'Solid performance with upward potential'
        else:
            recommendations['actions'].append({
                'action': 'Set specific performance goals for next quarter',
                'priority': 'medium',
                'category': 'planning'
            })
            recommendations['summary'] = 'Consistent performer - goal-setting recommended'

    return recommendations


def interpret_trend(trend_value, metric_name):
    """
    Interpret a trend value into human-readable text.

    Args:
        trend_value (float): Trend slope value
        metric_name (str): Name of the metric

    Returns:
        str: Interpretation of the trend
    """
    if trend_value > 0.3:
        return f"Strong positive improvement in {metric_name}"
    elif trend_value > 0.1:
        return f"Gradual improvement in {metric_name}"
    elif trend_value > -0.1:
        return f"Stable {metric_name} with minimal change"
    elif trend_value > -0.3:
        return f"Slight decline in {metric_name}"
    else:
        return f"Significant decline in {metric_name} - attention needed"


def get_dashboard_statistics():
    """
    Calculate overall statistics for the dashboard.

    Returns:
        dict: Dashboard statistics including key metrics and top performers
    """
    employees = Employee.objects.all()
    records = PerformanceRecord.objects.all()

    if not employees.exists():
        return {
            'total_employees': 0,
            'total_records': 0,
            'avg_efficiency': 0,
            'avg_quality': 0,
            'top_performers': [],
            'department_stats': {}
        }

    # Overall statistics
    stats = {
        'total_employees': employees.count(),
        'total_records': records.count(),
        'avg_efficiency': 0,
        'avg_quality': 0,
        'top_performers': [],
        'department_stats': {},
        'category_distribution': {}
    }

    if records.exists():
        stats['avg_efficiency'] = round(records.aggregate(avg=models.Avg('efficiency'))['avg'] or 0, 2)
        stats['avg_quality'] = round(records.aggregate(avg=models.Avg('quality'))['avg'] or 0, 2)

    # Category distribution
    for category, label in Employee.PERFORMANCE_CATEGORIES:
        count = employees.filter(performance_category=category).count()
        stats['category_distribution'][label] = count

    # Top performers (top 5 by overall score)
    employee_scores = []
    for emp in employees:
        if emp.get_record_count() > 0:
            avg_score = (emp.get_average_efficiency() + emp.get_average_quality()) / 2
            employee_scores.append({
                'id': emp.id,
                'name': emp.name,
                'role': emp.role,
                'department': emp.department,
                'overall_score': round(avg_score, 2),
                'record_count': emp.get_record_count()
            })

    stats['top_performers'] = sorted(employee_scores, key=lambda x: x['overall_score'], reverse=True)[:5]

    # Department statistics
    departments = employees.values_list('department', flat=True).distinct()
    for dept in departments:
        dept_employees = employees.filter(department=dept)
        dept_records = PerformanceRecord.objects.filter(employee__in=dept_employees)

        stats['department_stats'][dept] = {
            'employee_count': dept_employees.count(),
            'avg_efficiency': round(dept_records.aggregate(avg=models.Avg('efficiency'))['avg'] or 0, 2),
            'avg_quality': round(dept_records.aggregate(avg=models.Avg('quality'))['avg'] or 0, 2)
        }

    return stats


def get_chart_data(employee_id):
    """
    Prepare data for Chart.js visualizations.

    Args:
        employee_id (int): Employee ID

    Returns:
        dict: Chart-ready data
    """
    records = PerformanceRecord.objects.filter(employee_id=employee_id).order_by('date')

    if not records.exists():
        return {
            'dates': [],
            'efficiency': [],
            'quality': [],
            'tasks_completed': [],
            'productivity': []
        }

    chart_data = {
        'dates': [record.date.strftime('%Y-%m-%d') for record in records],
        'efficiency': [float(record.efficiency) for record in records],
        'quality': [float(record.quality) for record in records],
        'tasks_completed': [record.tasks_completed for record in records],
        'productivity': [float(record.get_productivity_score()) for record in records]
    }

    return chart_data
