from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f'documents/{instance.category.name if instance.category else "uncategorized"}/{filename}'


class Category(models.Model):
    """Document categories for classification"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color for UI
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def document_count(self):
        return self.documents.count()


class Document(models.Model):
    """Main document model"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=document_upload_path)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.BigIntegerField(help_text='File size in bytes')

    # Extracted text from the document
    extracted_text = models.TextField(blank=True, null=True)

    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text='ML classification confidence score (0-1)'
    )

    # Metadata
    upload_date = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False, help_text='Whether text extraction is complete')

    # Access tracking
    view_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['file_type']),
            models.Index(fields=['upload_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_size_formatted(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def increment_view_count(self):
        """Increment document view count"""
        self.view_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['view_count', 'last_accessed'])


class SearchQuery(models.Model):
    """Track search queries for analytics"""
    query = models.CharField(max_length=500)
    results_count = models.IntegerField(default=0)
    executed_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['executed_at']),
        ]

    def __str__(self):
        return f"{self.query} ({self.results_count} results)"


class DocumentAccess(models.Model):
    """Track document access patterns"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs')
    accessed_at = models.DateTimeField(default=timezone.now)
    access_type = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View'),
            ('download', 'Download'),
            ('search_result', 'Search Result'),
        ]
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['accessed_at']),
        ]

    def __str__(self):
        return f"{self.document.title} - {self.access_type}"


class SystemStats(models.Model):
    """Aggregate system statistics"""
    date = models.DateField(unique=True)
    total_documents = models.IntegerField(default=0)
    total_searches = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'System Stats'

    def __str__(self):
        return f"Stats for {self.date}"
