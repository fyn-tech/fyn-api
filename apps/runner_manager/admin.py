from django.contrib import admin
from runner_manager.models import RunnerInfo, SystemInfo


@admin.register(RunnerInfo)
class RunnerInfoAdmin(admin.ModelAdmin):
    print("WIP: empty - Runner admin")


@admin.register(SystemInfo)
class SystemInfoAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'runner',
                    'system_name',
                    'system_release',
                    'system_version',
                    'system_architecture',
                    'cpu_model',
                    'cpu_clock_speed_advertised',
                    'cpu_clock_speed_actual',
                    'cpu_logical_cores',
                    'cpu_physical_cores',
                    'cpu_cache_l1_size',
                    'cpu_cache_l2_size',
                    'cpu_cache_l3_size',
                    'ram_size_total',
                    'disk_size_total',
                    'disk_size_available',
                    'gpu_vendor',
                    'gpu_model',
                    'gpu_memory_size',
                    'gpu_clock_speed',
                    'gpu_compute_units',
                    'gpu_core_count',
                    'gpu_driver_version')
    list_filter = ('id',)
    ordering = ('id',)
    fieldsets = (
        ('ID', {
            'fields': ('id', 'runner')
        }),
        ('Operating System', {
            'fields': ('system_name', 'system_release', 'system_version',
                       'system_architecture')
        }),
        ('CPU System', {
            'fields': ('cpu_model',
                       'cpu_clock_speed_advertised',
                       'cpu_clock_speed_actual',
                       'cpu_logical_cores',
                       'cpu_physical_cores',
                       'cpu_cache_l1_size',
                       'cpu_cache_l2_size',
                       'cpu_cache_l3_size')
        }),
        ('Memory', {
            'fields': ('ram_size_total',)
        }),
        ('Disk', {
            'fields': ('disk_size_total', 'disk_size_available')
        }),
        ('GPU', {
            'fields': ('gpu_vendor',
                       'gpu_model',
                       'gpu_memory_size',
                       'gpu_clock_speed',
                       'gpu_compute_units',
                       'gpu_core_count',
                       'gpu_driver_version')
        })
    )
    readonly_fields = ('id', 'runner',)
