from django.contrib import admin
from .models import Category, Document, SearchQuery, DocumentAccess, SystemStats


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_count', 'color', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['color']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'category', 'confidence_score', 'processed', 'view_count', 'upload_date']
    list_filter = ['file_type', 'category', 'processed', 'upload_date']
    search_fields = ['title', 'description', 'extracted_text']
    readonly_fields = ['file_size', 'extracted_text', 'upload_date', 'view_count', 'last_accessed']
    date_hierarchy = 'upload_date'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'executed_at']
    list_filter = ['executed_at']
    search_fields = ['query']
    readonly_fields = ['executed_at']


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ['document', 'access_type', 'accessed_at']
    list_filter = ['access_type', 'accessed_at']
    readonly_fields = ['accessed_at']


@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_documents', 'total_searches', 'total_downloads', 'total_views']
    readonly_fields = ['date']
    date_hierarchy = 'date'
