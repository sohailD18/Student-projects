"""
Django REST Framework Serializers for the document system.
"""
from rest_framework import serializers
from .models import Category, Document, SearchQuery, DocumentAccess, SystemStats


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    document_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'document_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_color = serializers.CharField(source='category.color', read_only=True, allow_null=True)
    filename = serializers.ReadOnlyField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'file_type', 'file_size', 'file_size_formatted',
            'extracted_text', 'category', 'category_name', 'category_color',
            'confidence_score', 'upload_date', 'processed', 'view_count', 'last_accessed', 'filename'
        ]
        read_only_fields = [
            'extracted_text', 'confidence_score', 'upload_date', 'processed',
            'view_count', 'last_accessed', 'file_size'
        ]

    def get_file_size_formatted(self, obj):
        return obj.file_size_formatted


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document lists"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_color = serializers.CharField(source='category.color', read_only=True, allow_null=True)
    filename = serializers.ReadOnlyField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file_type', 'file_size_formatted', 'category', 'category_name',
            'category_color', 'confidence_score', 'upload_date', 'processed', 'view_count', 'filename'
        ]

    def get_file_size_formatted(self, obj):
        return obj.file_size_formatted


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category']

    def validate_file(self, value):
        """Validate file type and size"""
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 50MB")

        # Check file extension
        ext = value.name.split('.')[-1].lower()
        if ext not in ['pdf', 'docx', 'txt']:
            raise serializers.ValidationError("Only PDF, DOCX, and TXT files are supported")

        return value


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for SearchQuery model"""
    class Meta:
        model = SearchQuery
        fields = ['id', 'query', 'results_count', 'executed_at', 'ip_address']
        read_only_fields = ['executed_at']


class DocumentAccessSerializer(serializers.ModelSerializer):
    """Serializer for DocumentAccess model"""
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentAccess
        fields = ['id', 'document', 'document_title', 'accessed_at', 'access_type', 'ip_address']
        read_only_fields = ['accessed_at']


class SystemStatsSerializer(serializers.ModelSerializer):
    """Serializer for SystemStats model"""
    class Meta:
        model = SystemStats
        fields = ['id', 'date', 'total_documents', 'total_searches', 'total_downloads', 'total_views']
        read_only_fields = ['date']


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search results with relevance scores"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    file_type = serializers.CharField()
    file_size_formatted = serializers.CharField()
    category_name = serializers.CharField(allow_null=True)
    category_color = serializers.CharField(allow_null=True)
    confidence_score = serializers.FloatField(allow_null=True)
    upload_date = serializers.DateTimeField()
    relevance_score = serializers.FloatField()
    filename = serializers.CharField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_documents = serializers.IntegerField()
    documents_by_category = serializers.ListField()
    documents_by_type = serializers.ListField()
    recent_uploads = serializers.ListField()
    top_viewed = serializers.ListField()
    total_searches = serializers.IntegerField()
    total_categories = serializers.IntegerField()
