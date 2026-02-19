from django.contrib import admin
from .models import Template, TemplateSection, GlobalBlock, Theme, TemplateVariable


class TemplateSectionInline(admin.StackedInline):
    model = TemplateSection
    extra = 0


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'template_type', 'is_default', 'is_active', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TemplateSectionInline]


@admin.register(TemplateSection)
class TemplateSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'identifier', 'order', 'is_required', 'created_at']
    list_filter = ['template', 'is_required']
    search_fields = ['name', 'identifier', 'description']


@admin.register(GlobalBlock)
class GlobalBlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'identifier', 'block_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['block_type', 'is_active']
    search_fields = ['name', 'identifier', 'content']


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_default', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'variable_type', 'template', 'is_global']
    list_filter = ['variable_type', 'is_global', 'template']
    search_fields = ['name', 'key', 'description']
