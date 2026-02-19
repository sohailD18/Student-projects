from django.db import models
from django.contrib.auth.models import User


class Navigation(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='navigations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Navigations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def menu_items(self):
        return self.items.filter(parent=None).order_by('order')


class NavigationItem(models.Model):
    LINK_TYPE_CHOICES = [
        ('INTERNAL', 'Internal Link'),
        ('EXTERNAL', 'External Link'),
        ('PAGE', 'Page Link'),
        ('ANCHOR', 'Anchor Link'),
    ]
    
    TARGET_CHOICES = [
        ('_SELF', 'Same Window'),
        ('_BLANK', 'New Window'),
        ('_PARENT', 'Parent Window'),
        ('_TOP', 'Top Window'),
    ]

    navigation = models.ForeignKey(Navigation, on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    title = models.CharField(max_length=255)
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='INTERNAL')
    url = models.URLField(blank=True)
    page = models.ForeignKey('pages.Page', on_delete=models.CASCADE, null=True, blank=True, related_name='navigation_items')
    
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='_SELF')
    css_classes = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Navigation Items'
    
    def __str__(self):
        return self.title
    
    @property
    def has_children(self):
        return self.children.exists()
    
    @property
    def get_url(self):
        if self.link_type == 'PAGE' and self.page:
            return self.page.get_absolute_url()
        return self.url


class Breadcrumb(models.Model):
    page = models.OneToOneField('pages.Page', on_delete=models.CASCADE, related_name='breadcrumb')
    title_override = models.CharField(max_length=255, blank=True)
    
    custom_breadcrumbs = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Breadcrumbs'
    
    def __str__(self):
        return f"Breadcrumb for {self.page.title}"
    
    @property
    def get_breadcrumbs(self):
        if self.custom_breadcrumbs:
            return self.custom_breadcrumbs
        
        breadcrumbs = []
        page = self.page
        while page:
            title = self.title_override if self.title_override else page.title
            breadcrumbs.insert(0, {
                'title': title if page == self.page else page.title,
                'url': page.get_absolute_url()
            })
            page = page.parent
        return breadcrumbs


class FooterLink(models.Model):
    GROUP_CHOICES = [
        ('COMPANY', 'Company'),
        ('PRODUCTS', 'Products'),
        ('RESOURCES', 'Resources'),
        ('LEGAL', 'Legal'),
        ('SOCIAL', 'Social'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=255)
    url = models.URLField()
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, default='OTHER')
    order = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['group', 'order']
        verbose_name_plural = 'Footer Links'
    
    def __str__(self):
        return f"{self.title} ({self.group})"
