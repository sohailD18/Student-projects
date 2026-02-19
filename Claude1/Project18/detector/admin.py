from django.contrib import admin
from .models import (
    Transaction, Alert, UserProfile, SpendingPattern, FraudRule, RuleExecutionLog,
    FraudCase, CaseNote, CaseEvidence, ComplianceReport, SuspiciousActivityReport,
    AuditLog, NotificationTemplate, NotificationLog, NotificationPreference
)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'merchant', 'amount', 'status', 'risk_score', 'transaction_type', 'timestamp', 'location')
    list_filter = ('status', 'transaction_type', 'timestamp')
    search_fields = ('user', 'merchant', 'location')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'risk_score')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'risk_score', 'severity', 'status', 'rule_triggered', 'created_at')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('rule_triggered', 'transaction__user')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'acknowledged_at', 'resolved_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'risk_level', 'total_transactions', 'avg_transaction_amount', 'last_updated')
    list_filter = ('risk_level', 'last_updated')
    search_fields = ('user',)
    readonly_fields = ('last_updated',)


@admin.register(SpendingPattern)
class SpendingPatternAdmin(admin.ModelAdmin):
    list_display = ('user', 'pattern_type', 'baseline_value', 'created_at')
    list_filter = ('pattern_type', 'created_at')
    search_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FraudRule)
class FraudRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'is_active', 'weight', 'created_at')
    list_filter = ('rule_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RuleExecutionLog)
class RuleExecutionLogAdmin(admin.ModelAdmin):
    list_display = ('rule', 'transaction', 'triggered', 'risk_points_added', 'executed_at')
    list_filter = ('triggered', 'executed_at')
    search_fields = ('rule__name', 'transaction__user')
    readonly_fields = ('executed_at',)


class CaseNoteInline(admin.TabularInline):
    model = CaseNote
    extra = 1
    readonly_fields = ('created_at',)


class CaseEvidenceInline(admin.TabularInline):
    model = CaseEvidence
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(FraudCase)
class FraudCaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'title', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('case_number', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'closed_at')
    inlines = [CaseNoteInline, CaseEvidenceInline]


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ('fraud_case', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('note', 'author')
    readonly_fields = ('created_at',)


@admin.register(CaseEvidence)
class CaseEvidenceAdmin(admin.ModelAdmin):
    list_display = ('fraud_case', 'evidence_type', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('evidence_type', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at',)


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'title', 'generated_by', 'generated_at', 'status')
    list_filter = ('report_type', 'status', 'generated_at')
    search_fields = ('title', 'description')
    readonly_fields = ('generated_at',)


@admin.register(SuspiciousActivityReport)
class SuspiciousActivityReportAdmin(admin.ModelAdmin):
    list_display = ('sar_number', 'case', 'filing_date', 'suspicious_amount', 'filed_by')
    list_filter = ('filing_date', 'law_enforcement_referral')
    search_fields = ('sar_number', 'case__case_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'entity_type', 'entity_id', 'actor', 'timestamp')
    list_filter = ('action_type', 'entity_type', 'timestamp')
    search_fields = ('entity_id', 'actor', 'changes')
    readonly_fields = ('timestamp',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'is_active', 'created_at')
    list_filter = ('channel', 'is_active')
    search_fields = ('name', 'subject_template')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('alert', 'channel', 'recipient', 'status', 'sent_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('recipient', 'error_message')
    readonly_fields = ('created_at', 'sent_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'sms_enabled', 'digest_mode', 'updated_at')
    list_filter = ('email_enabled', 'sms_enabled', 'digest_mode')
    search_fields = ('user', 'email_address', 'phone_number')
    readonly_fields = ('updated_at',)
