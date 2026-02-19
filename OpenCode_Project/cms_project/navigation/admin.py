from django.contrib import admin
from .models import Navigation, NavigationItem, Breadcrumb, FooterLink


class NavigationItemInline(admin.StackedInline):
    model = NavigationItem
    extra = 0


@admin.register(Navigation)
class NavigationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'navigation', 'link_type', 'page', 'order', 'is_active']
    list_filter = ['link_type', 'target', 'is_active', 'navigation']
    search_fields = ['title', 'url']


@admin.register(Breadcrumb)
class BreadcrumbAdmin(admin.ModelAdmin):
    list_display = ['page', 'title_override', 'updated_at']
    search_fields = ['page__title']


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'group', 'order', 'is_active']
    list_filter = ['group', 'is_active']
    search_fields = ['title', 'url']
