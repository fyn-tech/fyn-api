from django.contrib import admin
from apps.runner_manager.models import RunnerInfo


@admin.register(RunnerInfo)
class RunnerAdmin(admin.ModelAdmin):
    print("WIP: empty - Runner admin")
