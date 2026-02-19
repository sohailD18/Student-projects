from django.contrib import admin
from .models import LegalDocument, AnalysisReport


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'file_size')
    list_filter = ('created_at',)
    search_fields = ('title',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def file_size(self, obj):
        """Display file size in KB."""
        if obj.uploaded_file:
            size = obj.uploaded_file.size
            return f"{size / 1024:.2f} KB"
        return "N/A"
    file_size.short_description = 'File Size'


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ('document_title', 'risk_level', 'is_compliant', 'summary_preview')
    list_filter = ('risk_level', 'is_compliant')
    search_fields = ('document__title', 'summary')
    readonly_fields = ('document', 'risk_level', 'summary', 'is_compliant')

    def document_title(self, obj):
        """Display the related document title."""
        return obj.document.title
    document_title.short_description = 'Document'
    document_title.admin_order_field = 'document__title'

    def summary_preview(self, obj):
        """Display a preview of the summary."""
        return obj.summary[:100] + '...' if len(obj.summary) > 100 else obj.summary
    summary_preview.short_description = 'Summary'
