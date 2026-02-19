from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Page(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    template = models.ForeignKey('templates_app.Template', on_delete=models.SET_NULL, null=True, blank=True, related_name='pages')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if self.status == 'PUBLISHED' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def content_blocks(self):
        return self.blocks.all().order_by('order')


class ContentBlock(models.Model):
    BLOCK_TYPE_CHOICES = [
        ('TEXT', 'Text'),
        ('HTML', 'HTML'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('GALLERY', 'Gallery'),
        ('FORM', 'Form'),
        ('QUOTE', 'Quote'),
        ('DIVIDER', 'Divider'),
        ('CODE', 'Code'),
        ('TABLE', 'Table'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    css_classes = models.CharField(max_length=255, blank=True)
    custom_css = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.block_type}: {self.title or self.page.title}"


class PageRevision(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='revisions')
    title = models.CharField(max_length=255)
    content_data = models.JSONField()
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Revision of {self.page.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class PageView(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"View of {self.page.title}"
