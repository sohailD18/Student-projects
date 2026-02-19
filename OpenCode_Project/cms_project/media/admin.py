from django.contrib import admin
from .models import MediaFile, MediaFolder, MediaCollection, MediaUsage


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'folder', 'uploaded_by', 'file_size', 'is_public', 'created_at']
    list_filter = ['file_type', 'is_public', 'folder', 'created_at']
    search_fields = ['title', 'description', 'alt_text', 'original_filename']
    readonly_fields = ['file_size', 'created_at']


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MediaCollection)
class MediaCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['files']


@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ['media_file', 'content_type', 'page', 'used_at']
    list_filter = ['used_at']
    search_fields = ['media_file__title']
    readonly_fields = ['media_file', 'content_type', 'object_id', 'page', 'block', 'used_at']
