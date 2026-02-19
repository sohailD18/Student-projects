from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    TYPE_CHOICES = [
        ('PAGE', 'Page Template'),
        ('HOME', 'Home Page'),
        ('BLOG', 'Blog Post'),
        ('PRODUCT', 'Product Page'),
        ('CATEGORY', 'Category Page'),
        ('LANDING', 'Landing Page'),
        ('CUSTOM', 'Custom'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    template_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PAGE')
    
    thumbnail = models.ImageField(upload_to='templates/', blank=True, null=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def structure_count(self):
        return self.structures.count()


class TemplateSection(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='structures')
    name = models.CharField(max_length=255)
    identifier = models.SlugField(max_length=255)
    
    description = models.TextField(blank=True)
    default_content = models.TextField(blank=True)
    
    allowed_block_types = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=False)
    max_blocks = models.PositiveIntegerField(null=True, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    css_classes = models.CharField(max_length=255, blank=True)
    custom_css = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Template Sections'
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class GlobalBlock(models.Model):
    BLOCK_TYPE_CHOICES = [
        ('HEADER', 'Header'),
        ('FOOTER', 'Footer'),
        ('SIDEBAR', 'Sidebar'),
        ('BANNER', 'Banner'),
        ('PROMO', 'Promo'),
        ('WIDGET', 'Widget'),
        ('CUSTOM', 'Custom'),
    ]

    name = models.CharField(max_length=255)
    identifier = models.SlugField(max_length=255, unique=True)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, default='CUSTOM')
    
    content = models.TextField()
    css_classes = models.CharField(max_length=255, blank=True)
    custom_css = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    display_on = models.JSONField(default=dict, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='global_blocks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Global Blocks'
    
    def __str__(self):
        return self.name


class Theme(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    accent_color = models.CharField(max_length=7, default='#28a745')
    
    background_color = models.CharField(max_length=7, default='#ffffff')
    text_color = models.CharField(max_length=7, default='#333333')
    
    font_family = models.CharField(max_length=100, default='sans-serif')
    font_size_base = models.PositiveIntegerField(default=16)
    
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='themes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TemplateVariable(models.Model):
    VARIABLE_TYPE_CHOICES = [
        ('TEXT', 'Text'),
        ('NUMBER', 'Number'),
        ('BOOLEAN', 'Boolean'),
        ('COLOR', 'Color'),
        ('URL', 'URL'),
        ('IMAGE', 'Image'),
        ('TEXTAREA', 'Textarea'),
        ('SELECT', 'Select'),
    ]

    name = models.CharField(max_length=255)
    key = models.SlugField(max_length=255)
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPE_CHOICES, default='TEXT')
    
    default_value = models.TextField(blank=True)
    choices = models.JSONField(default=list, blank=True)
    
    description = models.TextField(blank=True)
    
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='variables', null=True, blank=True)
    is_global = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Template Variables'
    
    def __str__(self):
        return f"{self.name} ({self.key})"
