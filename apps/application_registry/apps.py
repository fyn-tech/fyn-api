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

from django.apps import AppConfig
from django.conf import settings

class ApplicationRegistryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application_registry"

    def ready(self):
        self.bootstrap_default_programs()
    
    def bootstrap_default_programs(self):
        """Check (and add if required) the standard test program. """
        from django.db import connection
        from .models import AppInfo, AppType

        print("\033[93m" + "="*80)
        print("FIXME: This need to be added to boot-strapping and migration, is a quick fix.")
        
        
        # Return if we entre before table creation.
        table_names = connection.introspection.table_names()        
        if 'application_registry_appinfo' not in table_names:
            print("AppInfo table doesn't exist yet - skipping bootstrap")
            return
    
        # Check programs exist
        app_path = settings.BASE_DIR / (
                "apps/application_registry/static/application_registry/default_packages/"
                "test_program.py"
                )
        schema_path = settings.BASE_DIR / (
                "apps/application_registry/static/application_registry/default_packages/"
                "test_program_schema.json"
                )
        if not AppInfo.objects.filter(name="test_program").exists():
            if app_path.exists() and schema_path.exists():
                AppInfo.objects.create(name="test_program", type=AppType.PYTHON_SCRIPT,
                                       file_path=str(app_path), schema_path=str(schema_path))
                print("Found test_program and test_program_schema, adding to application registry.")
            else:
                print("Warning: cannot find test_program.py or test_program_schema.json, "
                        "skipping default database injection.")
        else: 
            if not app_path.exists():
                test_program_app = AppInfo.objects.filter(name="test_program")
                test_program_app.delete()
                print("Found test_program but not the file test_program.py, removed test_program.")

            if not schema_path.exists():
                test_program_app = AppInfo.objects.filter(name="test_program")
                test_program_app.delete()
                print("Found test_program but not the file test_program_schema.json, "
                      "removed test_program.")

        print("="*80 + "\033[0m")