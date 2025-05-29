from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "created_by", "yaml_file")
    list_filter = ("created_at", "created_by")
    search_fields = ("name", "created_by__username")
    readonly_fields = ("id", "created_at", "updated_at")
