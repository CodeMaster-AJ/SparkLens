from django.contrib import admin
from .models import IdeaSubmission, AnalysisReport


@admin.register(IdeaSubmission)
class IdeaSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'industry', 'created_at', 'session_key']
    list_filter = ['industry', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'session_key', 'created_at']


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ['submission', 'verdict', 'market_score', 'feasibility_score', 'generation_ms', 'created_at']
    list_filter = ['verdict', 'created_at']
    readonly_fields = ['id', 'model_used', 'generation_ms', 'created_at']
