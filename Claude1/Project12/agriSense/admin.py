from django.contrib import admin
from .models import Crop, Season, SoilData, YieldRecord


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'duration']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'months']
    search_fields = ['name']


@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ['type', 'ph', 'moisture', 'recorded_date']
    list_filter = ['type']
    search_fields = ['type']


@admin.register(YieldRecord)
class YieldRecordAdmin(admin.ModelAdmin):
    list_display = ['crop', 'year', 'quantity', 'recorded_date']
    list_filter = ['crop', 'year']
    search_fields = ['crop__name']
