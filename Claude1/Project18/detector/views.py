from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta
from .models import (
    Transaction, Alert, UserProfile, SpendingPattern, FraudRule,
    FraudCase, CaseNote, CaseEvidence, ComplianceReport,
    SuspiciousActivityReport, AuditLog, NotificationTemplate, NotificationLog
)
from .utils import (
    calculate_risk, AdvancedRiskScorer, SpendingPatternAnalyzer,
    AnomalyDetectionEngine, log_audit_event
)
import random
import string


# ============================================================================
# DASHBOARD & TRANSACTION VIEWS
# ============================================================================

def dashboard(request):
    """Render dashboard with all transactions and statistics"""
    transactions = Transaction.objects.all().order_by('-timestamp')[:100]

    # Calculate statistics
    stats = {
        'total_transactions': Transaction.objects.count(),
        'safe_count': Transaction.objects.filter(status='safe').count(),
        'suspicious_count': Transaction.objects.filter(status='suspicious').count(),
        'fraud_count': Transaction.objects.filter(status='fraud').count(),
        'open_alerts': Alert.objects.filter(status='open').count(),
        'open_cases': FraudCase.objects.filter(status__in=['open', 'investigating']).count(),
    }

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'stats': stats
    })


def add_transaction(request):
    """Accept POST request, save transaction, calculate risk, create alert if risk > threshold"""
    if request.method == 'POST':
        # Get data from POST request
        user = request.POST.get('user')
        amount = request.POST.get('amount')
        location = request.POST.get('location')
        merchant = request.POST.get('merchant')
        transaction_type = request.POST.get('transaction_type', 'purchase')

        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            location=location,
            merchant=merchant,
            transaction_type=transaction_type
        )

        # Calculate risk score using advanced scorer
        scorer = AdvancedRiskScorer()
        risk_score, risk_factors, severity = scorer.calculate_comprehensive_risk(transaction)
        transaction.risk_score = risk_score

        # Update transaction status based on risk
        if risk_score >= 80:
            transaction.status = 'fraud'
        elif risk_score >= 50:
            transaction.status = 'suspicious'
        else:
            transaction.status = 'safe'
        transaction.save()

        # Create alert if risk > 40
        if risk_score > 40:
            Alert.objects.create(
                transaction=transaction,
                risk_score=risk_score,
                severity=severity,
                rule_triggered=f"High risk detected: Score {risk_score} ({severity})",
                description=f"Risk factors: {risk_factors}"
            )

        # Log audit event
        log_audit_event(
            action_type='transaction_created',
            entity_type='Transaction',
            entity_id=transaction.id,
            actor=request.user.username if request.user.is_authenticated else 'system',
            changes={'risk_score': risk_score, 'status': transaction.status}
        )

        return JsonResponse({
            'success': True,
            'transaction_id': transaction.id,
            'risk_score': risk_score,
            'severity': severity,
            'status': transaction.status
        })

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


def alerts(request):
    """Render alerts page with suspicious or fraud transactions"""
    status_filter = request.GET.get('status', 'all')
    severity_filter = request.GET.get('severity', 'all')

    alerts_query = Alert.objects.all()

    if status_filter != 'all':
        alerts_query = alerts_query.filter(status=status_filter)

    if severity_filter != 'all':
        alerts_query = alerts_query.filter(severity=severity_filter)

    alerts = alerts_query.select_related('transaction').order_by('-created_at')

    stats = {
        'total': Alert.objects.count(),
        'open': Alert.objects.filter(status='open').count(),
        'critical': Alert.objects.filter(severity='critical', status='open').count(),
        'high': Alert.objects.filter(severity='high', status='open').count(),
    }

    return render(request, 'alerts.html', {
        'alerts': alerts,
        'stats': stats,
        'status_filter': status_filter,
        'severity_filter': severity_filter
    })


def alert_detail(request, alert_id):
    """View alert details"""
    alert = get_object_or_404(Alert, id=alert_id)
    return render(request, 'alert_detail.html', {'alert': alert})


def acknowledge_alert(request, alert_id):
    """Acknowledge an alert"""
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user.username if request.user.is_authenticated else 'admin'
        alert.save()

        log_audit_event(
            action_type='alert_acknowledged',
            entity_type='Alert',
            entity_id=alert.id,
            actor=alert.acknowledged_by
        )

        messages.success(request, f'Alert {alert_id} acknowledged successfully')
        return redirect('alerts')

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


# ============================================================================
# USER PROFILES & SPENDING PATTERNS
# ============================================================================

def user_profiles(request):
    """View all user profiles"""
    profiles = UserProfile.objects.all().order_by('-last_updated')
    return render(request, 'user_profiles.html', {'profiles': profiles})


def user_profile_detail(request, user):
    """View detailed user profile"""
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, f'Profile not found for user: {user}')
        return redirect('user_profiles')

    # Get user's transactions
    transactions = Transaction.objects.filter(user=user).order_by('-timestamp')[:50]

    # Generate spending report
    analyzer = SpendingPatternAnalyzer()
    spending_report = analyzer.generate_spending_report(user, days=30)

    return render(request, 'user_profile_detail.html', {
        'profile': profile,
        'transactions': transactions,
        'spending_report': spending_report
    })


def update_user_profile(request, user):
    """Manually trigger profile update for a user"""
    if request.method == 'POST':
        analyzer = SpendingPatternAnalyzer()
        profile = analyzer.analyze_and_update_profile(user)

        if profile:
            messages.success(request, f'Profile updated for {user}')
        else:
            messages.warning(request, f'No transactions found for {user}')

        return redirect('user_profile_detail', user=user)

    return redirect('user_profiles')


# ============================================================================
# FRAUD CASE MANAGEMENT
# ============================================================================

def fraud_cases(request):
    """View all fraud cases"""
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')

    cases_query = FraudCase.objects.all()

    if status_filter != 'all':
        cases_query = cases_query.filter(status=status_filter)

    if priority_filter != 'all':
        cases_query = cases_query.filter(priority=priority_filter)

    cases = cases_query.order_by('-created_at')

    stats = {
        'total': FraudCase.objects.count(),
        'open': FraudCase.objects.filter(status='open').count(),
        'investigating': FraudCase.objects.filter(status='investigating').count(),
        'closed': FraudCase.objects.filter(status='closed').count(),
    }

    return render(request, 'fraud_cases.html', {
        'cases': cases,
        'stats': stats,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })


def case_detail(request, case_id):
    """View case details"""
    case = get_object_or_404(FraudCase, case_number=case_id)
    notes = case.notes.all().order_by('-created_at')
    evidence = case.evidence.all().order_by('-uploaded_at')
    related_transactions = case.related_transactions.all()
    related_alerts = case.related_alerts.all()

    return render(request, 'case_detail.html', {
        'case': case,
        'notes': notes,
        'evidence': evidence,
        'related_transactions': related_transactions,
        'related_alerts': related_alerts
    })


def create_case(request):
    """Create a new fraud case"""
    if request.method == 'POST':
        # Generate case number
        case_number = 'FC-' + datetime.now().strftime('%Y%m%d') + '-' + \
                      ''.join(random.choices(string.digits, k=4))

        case = FraudCase.objects.create(
            case_number=case_number,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority', 'p3'),
            assigned_to=request.POST.get('assigned_to'),
        )

        # Link transaction if provided
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            case.related_transactions.add(transaction)
            case.suspected_amount = transaction.amount
            case.save()

        log_audit_event(
            action_type='case_created',
            entity_type='FraudCase',
            entity_id=case.id,
            actor=request.user.username if request.user.is_authenticated else 'admin'
        )

        messages.success(request, f'Case {case_number} created successfully')
        return redirect('case_detail', case_id=case_number)

    return render(request, 'create_case.html')


def update_case_status(request, case_id):
    """Update case status"""
    if request.method == 'POST':
        case = get_object_or_404(FraudCase, case_number=case_id)
        new_status = request.POST.get('status')

        case.status = new_status
        if new_status == 'closed':
            case.closed_at = timezone.now()
            case.closed_by = request.user.username if request.user.is_authenticated else 'admin'
            case.resolution_summary = request.POST.get('resolution_summary', '')

        case.save()

        log_audit_event(
            action_type='case_updated',
            entity_type='FraudCase',
            entity_id=case.id,
            actor=request.user.username if request.user.is_authenticated else 'admin',
            changes={'status': new_status}
        )

        messages.success(request, f'Case {case_id} updated successfully')
        return redirect('case_detail', case_id=case_id)

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


def add_case_note(request, case_id):
    """Add a note to a case"""
    if request.method == 'POST':
        case = get_object_or_404(FraudCase, case_number=case_id)

        CaseNote.objects.create(
            fraud_case=case,
            author=request.user.username if request.user.is_authenticated else 'admin',
            note=request.POST.get('note'),
            is_internal=request.POST.get('is_internal', 'true') == 'true'
        )

        messages.success(request, 'Note added successfully')
        return redirect('case_detail', case_id=case_id)

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


def create_case_from_alert(request, alert_id):
    """Create a fraud case from an alert"""
    alert = get_object_or_404(Alert, id=alert_id)

    # Generate case number
    case_number = 'FC-' + datetime.now().strftime('%Y%m%d') + '-' + \
                  ''.join(random.choices(string.digits, k=4))

    # Determine priority based on severity
    priority_map = {'critical': 'p1', 'high': 'p2', 'medium': 'p3', 'low': 'p4'}
    priority = priority_map.get(alert.severity, 'p3')

    case = FraudCase.objects.create(
        case_number=case_number,
        title=f"Case from Alert {alert.id}",
        description=f"Automatically created from alert: {alert.rule_triggered}",
        priority=priority,
        status='open',
        suspected_amount=alert.transaction.amount
    )

    case.related_transactions.add(alert.transaction)
    case.related_alerts.add(alert)

    # Update alert status
    alert.status = 'investigating'
    alert.save()

    log_audit_event(
        action_type='case_created',
        entity_type='FraudCase',
        entity_id=case.id,
        actor='system',
        changes={'source_alert': alert.id}
    )

    messages.success(request, f'Case {case_number} created from alert')
    return redirect('case_detail', case_id=case_number)


# ============================================================================
# COMPLIANCE & REPORTING
# ============================================================================

def compliance_reports(request):
    """View all compliance reports"""
    reports = ComplianceReport.objects.all().order_by('-generated_at')

    stats = {
        'total': ComplianceReport.objects.count(),
        'sar': ComplianceReport.objects.filter(report_type='sar').count(),
        'aml': ComplianceReport.objects.filter(report_type='aml').count(),
    }

    return render(request, 'compliance_reports.html', {
        'reports': reports,
        'stats': stats
    })


def generate_sar(request, case_id):
    """Generate a Suspicious Activity Report for a case"""
    case = get_object_or_404(FraudCase, case_number=case_id)

    # Check if SAR already exists
    if hasattr(case, 'sar'):
        messages.warning(request, f'SAR already exists for case {case_id}')
        return redirect('case_detail', case_id=case_id)

    if request.method == 'POST':
        # Generate SAR number
        sar_number = 'SAR-' + datetime.now().strftime('%Y%m%d') + '-' + case_id

        # Get transaction date range
        transactions = case.related_transactions.all()
        if transactions:
            date_range = {
                'start': transactions.order_by('timestamp').first().timestamp.strftime('%Y-%m-%d'),
                'end': transactions.order_by('-timestamp').first().timestamp.strftime('%Y-%m-%d')
            }
        else:
            date_range = {'start': '', 'end': ''}

        sar = SuspiciousActivityReport.objects.create(
            case=case,
            sar_number=sar_number,
            filing_date=datetime.now().date(),
            suspicious_amount=float(case.confirmed_fraud_amount or case.suspected_amount),
            activity_description=request.POST.get('activity_description', case.description),
            transaction_dates=date_range,
            involved_parties=list(case.related_transactions.values_list('user', flat=True).distinct()),
            fraud_types=['suspicious_activity'],
            filed_by=request.user.username if request.user.is_authenticated else 'admin'
        )

        # Also create a compliance report
        ComplianceReport.objects.create(
            report_type='sar',
            title=f"SAR for Case {case_id}",
            description=f" Suspicious Activity Report for case {case_id}",
            report_data={'sar_number': sar_number, 'case_id': case_id},
            date_range_start=datetime.now() - timedelta(days=30),
            date_range_end=datetime.now(),
            generated_by=request.user.username if request.user.is_authenticated else 'admin'
        )

        log_audit_event(
            action_type='report_generated',
            entity_type='SAR',
            entity_id=sar.id,
            actor=request.user.username if request.user.is_authenticated else 'admin'
        )

        messages.success(request, f'SAR {sar_number} generated successfully')
        return redirect('case_detail', case_id=case_id)

    return render(request, 'generate_sar.html', {'case': case})


def audit_log(request):
    """View audit logs"""
    log_type = request.GET.get('type', 'all')
    entity_id = request.GET.get('entity_id', '')

    logs_query = AuditLog.objects.all()

    if log_type != 'all':
        logs_query = logs_query.filter(action_type=log_type)

    if entity_id:
        logs_query = logs_query.filter(entity_id=entity_id)

    logs = logs_query.order_by('-timestamp')[:500]

    return render(request, 'audit_log.html', {
        'logs': logs,
        'log_type': log_type,
        'entity_id': entity_id
    })


def generate_fraud_summary(request):
    """Generate fraud summary report"""
    if request.method == 'POST':
        days = int(request.POST.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        # Gather statistics
        transactions = Transaction.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        alerts = Alert.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        cases = FraudCase.objects.filter(created_at__gte=start_date, created_at__lte=end_date)

        report_data = {
            'period_days': days,
            'transactions': {
                'total': transactions.count(),
                'safe': transactions.filter(status='safe').count(),
                'suspicious': transactions.filter(status='suspicious').count(),
                'fraud': transactions.filter(status='fraud').count(),
                'total_amount': sum(float(t.amount) for t in transactions),
                'fraud_amount': sum(float(t.amount) for t in transactions.filter(status='fraud')),
            },
            'alerts': {
                'total': alerts.count(),
                'critical': alerts.filter(severity='critical').count(),
                'high': alerts.filter(severity='high').count(),
                'medium': alerts.filter(severity='medium').count(),
            },
            'cases': {
                'total': cases.count(),
                'open': cases.filter(status='open').count(),
                'investigating': cases.filter(status='investigating').count(),
                'closed': cases.filter(status='closed').count(),
            }
        }

        report = ComplianceReport.objects.create(
            report_type='fraud_summary',
            title=f"Fraud Summary Report - {days} Days",
            description=f"Summary of fraud detection activity over the past {days} days",
            report_data=report_data,
            date_range_start=start_date,
            date_range_end=end_date,
            generated_by=request.user.username if request.user.is_authenticated else 'admin'
        )

        messages.success(request, f'Fraud summary report generated: {report.title}')
        return redirect('compliance_reports')

    return render(request, 'generate_report.html', {'report_type': 'fraud_summary'})


# ============================================================================
# RULES MANAGEMENT
# ============================================================================

def fraud_rules(request):
    """View all fraud detection rules"""
    rules = FraudRule.objects.all().order_by('-created_at')
    return render(request, 'fraud_rules.html', {'rules': rules})


def create_rule(request):
    """Create a new fraud rule"""
    if request.method == 'POST':
        # Build rule config based on rule type
        rule_type = request.POST.get('rule_type')
        config = {}

        if rule_type == 'amount_threshold':
            config = {
                'threshold': float(request.POST.get('threshold', 10000)),
                'risk_points': int(request.POST.get('risk_points', 50))
            }
        elif rule_type == 'time_based':
            config = {
                'start_hour': int(request.POST.get('start_hour', 1)),
                'end_hour': int(request.POST.get('end_hour', 5)),
                'risk_points': int(request.POST.get('risk_points', 30))
            }
        elif rule_type == 'location_based':
            config = {
                'suspicious_locations': request.POST.getlist('suspicious_locations'),
                'risk_points': int(request.POST.get('risk_points', 40))
            }
        elif rule_type == 'velocity_check':
            config = {
                'time_window_minutes': int(request.POST.get('time_window_minutes', 10)),
                'max_transactions': int(request.POST.get('max_transactions', 3)),
                'risk_points': int(request.POST.get('risk_points', 60))
            }
        elif rule_type == 'pattern_based':
            config = {
                'max_deviation': float(request.POST.get('max_deviation', 3.0)),
                'check_new_merchant': request.POST.get('check_new_merchant') == 'true',
                'risk_points': int(request.POST.get('risk_points', 40)),
                'merchant_risk_points': int(request.POST.get('merchant_risk_points', 20))
            }

        rule = FraudRule.objects.create(
            name=request.POST.get('name'),
            rule_type=rule_type,
            description=request.POST.get('description'),
            rule_config=config,
            weight=int(request.POST.get('weight', 50))
        )

        log_audit_event(
            action_type='rule_modified',
            entity_type='FraudRule',
            entity_id=rule.id,
            actor=request.user.username if request.user.is_authenticated else 'admin'
        )

        messages.success(request, f'Rule "{rule.name}" created successfully')
        return redirect('fraud_rules')

    return render(request, 'create_rule.html')


def toggle_rule(request, rule_id):
    """Toggle rule active/inactive"""
    if request.method == 'POST':
        rule = get_object_or_404(FraudRule, id=rule_id)
        rule.is_active = not rule.is_active
        rule.save()

        status = 'activated' if rule.is_active else 'deactivated'
        messages.success(request, f'Rule "{rule.name}" {status}')
        return redirect('fraud_rules')

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


# ============================================================================
# ANALYTICS DASHBOARD
# ============================================================================

def analytics_dashboard(request):
    """Advanced analytics dashboard"""
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)

    # Transaction statistics
    tx_stats = Transaction.objects.filter(timestamp__gte=start_date).aggregate(
        total_count=Count('id'),
        total_amount=Sum('amount'),
        avg_amount=Avg('amount'),
        fraud_count=Count('id', filter=Q(status='fraud')),
        suspicious_count=Count('id', filter=Q(status='suspicious'))
    )

    # Top risky users
    risky_users = Transaction.objects.filter(
        timestamp__gte=start_date,
        status__in=['suspicious', 'fraud']
    ).values('user').annotate(
        fraud_count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('-fraud_count')[:10]

    # Transaction trend by day
    daily_trend = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_stats = Transaction.objects.filter(
            timestamp__gte=day,
            timestamp__lt=day_end
        ).aggregate(
            count=Count('id'),
            fraud_count=Count('id', filter=Q(status__in=['suspicious', 'fraud']))
        )
        daily_trend.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': day_stats['count'] or 0,
            'fraud_count': day_stats['fraud_count'] or 0
        })

    # High risk merchants
    risky_merchants = Transaction.objects.filter(
        timestamp__gte=start_date,
        status__in=['suspicious', 'fraud']
    ).values('merchant').annotate(
        fraud_count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('-fraud_count')[:10]

    # Alerts by severity
    alert_stats = Alert.objects.filter(created_at__gte=start_date).values('severity').annotate(
        count=Count('id')
    ).order_by('-count')

    return render(request, 'analytics_dashboard.html', {
        'days': days,
        'tx_stats': tx_stats,
        'risky_users': risky_users,
        'daily_trend': daily_trend,
        'risky_merchants': risky_merchants,
        'alert_stats': alert_stats
    })
