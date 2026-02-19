from django.db import models
from django.contrib.auth.models import User
import os


def upload_to(instance, filename):
    return os.path.join('media_library', instance.uploaded_by.username, filename)


class MediaFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('DOCUMENT', 'Document'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    file = models.FileField(upload_to=upload_to)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    
    folder = models.ForeignKey('MediaFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    tags = models.CharField(max_length=500, blank=True)
    
    is_public = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files')
    
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.original_filename:
            self.original_filename = self.file.name
        if not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def extension(self):
        return os.path.splitext(self.original_filename)[1].lower()


class MediaFolder(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Media Folders'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def file_count(self):
        return self.files.count()
    
    @property
    def path(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' / '.join(path)


class MediaCollection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    files = models.ManyToManyField(MediaFile, related_name='collections')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Media Collections'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MediaUsage(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='usages')
    content_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    
    page = models.ForeignKey('pages.Page', on_delete=models.CASCADE, null=True, blank=True)
    block = models.ForeignKey('pages.ContentBlock', on_delete=models.CASCADE, null=True, blank=True)
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.media_file.title} used in {self.content_type}"
