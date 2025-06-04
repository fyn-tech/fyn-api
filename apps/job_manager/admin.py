from django.contrib import admin
from .models import JobStatus, JobInfo


@admin.register(JobInfo)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "status",
        "assigned_runner",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "assigned_runner",
        "created_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "id", "assigned_runner", "created_by__username")
    readonly_fields = (
        "id",
        "created_by",
        "created_at",
        "updated_at",
        "working_directory")

    fieldsets = (
        ("Basic Information", {"fields": ("id", "name", "status", "assigned_runner")}),
        ("Execution Information", {"fields": ("executable", "application_id", "command_line_args", 
                                              "working_directory")}),
        ("Input Files", {"fields": ("yaml_file",)}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
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
