"""
Admin configuration for sessions
"""
from django.contrib import admin
from apps.sessions.models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'expert', 'student', 'start_at', 'end_at', 'status', 'created_at']
    list_filter = ['status', 'expert', 'student', 'start_at']
    search_fields = ['expert__name', 'student__name', 'expert__email', 'student__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'summary']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'expert', 'student', 'start_at', 'end_at')
        }),
        ('Status', {
            'fields': ('status', 'joined_at', 'ended_at')
        }),
        ('Summary', {
            'fields': ('summary',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )