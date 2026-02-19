from django.contrib import admin
from .models import Page, ContentBlock, PageRevision, PageView


class ContentBlockInline(admin.StackedInline):
    model = ContentBlock
    extra = 0


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'author', 'published_at', 'created_at']
    list_filter = ['status', 'created_at', 'published_at']
    search_fields = ['title', 'slug', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline]
    date_hierarchy = 'created_at'


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ['page', 'block_type', 'title', 'order', 'is_active', 'created_at']
    list_filter = ['block_type', 'is_active', 'created_at']
    search_fields = ['title', 'content']


@admin.register(PageRevision)
class PageRevisionAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['page__title', 'title']
    readonly_fields = ['page', 'title', 'content_data', 'created_by', 'created_at']


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['page__title', 'ip_address']
    readonly_fields = ['page', 'ip_address', 'user_agent', 'referrer', 'viewed_at']
