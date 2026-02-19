from django.contrib import admin
from .models import Stock, HistoricalData, Prediction, VolatilityAnalysis, MarketReport


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'company_name', 'exchange', 'sector', 'is_active', 'data_points_count', 'latest_price']
    list_filter = ['is_active', 'exchange', 'sector']
    search_fields = ['symbol', 'company_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('symbol', 'company_name', 'is_active')
        }),
        ('Classification', {
            'fields': ('exchange', 'sector', 'industry')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'open_price', 'high', 'low', 'close', 'volume', 'price_change_percent']
    list_filter = ['stock', 'date']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at', 'price_change', 'price_change_percent']
    date_hierarchy = 'date'

    fieldsets = (
        ('Stock Information', {
            'fields': ('stock', 'date')
        }),
        ('Price Data', {
            'fields': ('open_price', 'high', 'low', 'close', 'adjusted_close')
        }),
        ('Volume', {
            'fields': ('volume',)
        }),
        ('Technical Indicators', {
            'fields': ('moving_average_5', 'moving_average_10', 'moving_average_20', 'moving_average_50', 'rsi'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('price_change', 'price_change_percent'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['stock', 'prediction_date', 'target_date', 'predicted_price', 'actual_price', 'signal', 'confidence', 'prediction_accuracy']
    list_filter = ['stock', 'prediction_date', 'signal', 'model_type']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at', 'prediction_accuracy']

    fieldsets = (
        ('Basic Information', {
            'fields': ('stock', 'prediction_date', 'target_date')
        }),
        ('Prediction', {
            'fields': ('predicted_price', 'actual_price', 'prediction_accuracy')
        }),
        ('Model Metrics', {
            'fields': ('model_type', 'mse', 'rmse', 'r2_score', 'mae')
        }),
        ('Signal', {
            'fields': ('signal', 'confidence')
        }),
        ('Advanced', {
            'fields': ('feature_importance',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(VolatilityAnalysis)
class VolatilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ['stock', 'analysis_date', 'daily_volatility', 'annualized_volatility', 'risk_level', 'var_95', 'sharpe_ratio']
    list_filter = ['stock', 'analysis_date', 'risk_level']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('stock', 'analysis_date', 'period_days')
        }),
        ('Volatility Metrics', {
            'fields': ('daily_volatility', 'annualized_volatility')
        }),
        ('Risk Metrics', {
            'fields': ('var_95', 'var_99', 'risk_level')
        }),
        ('Additional Metrics', {
            'fields': ('sharpe_ratio', 'max_drawdown', 'beta'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketReport)
class MarketReportAdmin(admin.ModelAdmin):
    list_display = ['stock', 'report_date', 'title', 'trend']
    list_filter = ['stock', 'report_date', 'trend']
    search_fields = ['stock__symbol', 'title', 'summary']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('stock', 'report_date', 'title', 'trend')
        }),
        ('Report Content', {
            'fields': ('summary', 'recommendation')
        }),
        ('Findings', {
            'fields': ('key_findings', 'data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
