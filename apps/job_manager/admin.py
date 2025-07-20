# Copyright (C) 2025 fyn-api Authors
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
#  see <https://www.gnu.org/licenses/>.

from django.contrib import admin
from .models import JobStatus, JobInfo, JobResource


@admin.register(JobInfo)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'status', 'created_at', 'resource_count')
    list_filter = ('status', 'created_at', 'application_id')
    search_fields = ('name', 'id', 'created_by__username')
    readonly_fields = ('id', 'created_at', 'created_by', 'updated_at', 'local_working_directory', 
                       'resource_summary_display')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'name', 'priority', 'status', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Execution', {
            'fields': ('application_id', 'executable', 'command_line_args', 'working_directory', 
                       'assigned_runner')
        }),
        ('Storage', {
            'fields': ('local_working_directory', 'resource_summary_display'),
        }),
    )

    # Custom actions
    actions = ["mark_as_queued", "mark_as_failed", "mark_as_succeeded"]

    def mark_as_queued(self, request, queryset):
        updated = queryset.update(status=JobStatus.QUEUED)
        self.message_user(request, f"{updated} jobs marked as queued.")

    mark_as_queued.short_description = "Mark selected jobs as queued"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status=JobStatus.FAILED)
        self.message_user(request, f"{updated} jobs marked as failed.")

    mark_as_failed.short_description = "Mark selected jobs as failed"

    def mark_as_succeeded(self, request, queryset):
        updated = queryset.update(status=JobStatus.SUCCEEDED)
        self.message_user(request, f"{updated} jobs marked as succeeded.")

    mark_as_succeeded.short_description = "Mark selected jobs as succeeded"
    
    def resource_count(self, obj):
        return obj.resources.count()
    
    resource_count.short_description = 'Total Resources'

    def resource_summary_display(self, obj):
        summary = obj.resource_summary
        if summary:
            return ', '.join([f"{k}: {v}" for k, v in summary.items()])
        return 'No resources'
    
    resource_summary_display.short_description = 'Resources Summary'

    # Override to set created_by automatically
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by when creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Customize queryset to show only user's jobs for non-superusers
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    # Control who can delete
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.created_by == request.user:
            return True
        return False

    # Control who can change
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.created_by == request.user:
            return True
        return False
    

@admin.register(JobResource)
class JobResourceAdmin(admin.ModelAdmin):
    list_display = ('filename', 'job', 'resource_type', 'created_at', 'created_by', 'file_location', 'original_file_path')
    list_filter = ('resource_type', 'created_at', 'job__status')
    search_fields = ('job__name', 'description', 'original_file_path')
    fields = ('job', 'resource_type', 'file', 'description', 'original_file_path', 'created_by')
    readonly_fields = ('full_path_display',)
    
    def file_location(self, obj):
        """Show where the file is actually stored"""
        return obj.full_file_path
    file_location.short_description = 'File Location'
    
    def full_path_display(self, obj):
        """Display full path in the form"""
        return obj.full_file_path
    full_path_display.short_description = 'Full File Path'