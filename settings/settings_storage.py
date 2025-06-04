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

"""
Storage-related Django settings for general file storage
"""

import os
from pathlib import Path

# --------------------------------------------------------------------------------------------------
#  Configuration
# --------------------------------------------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "False") == "True"
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------------------------
#  Setting Construction
# --------------------------------------------------------------------------------------------------

# Path Setup
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Storage backends
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# File upload settings (increase default sizes)
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024 
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024 

# Export settings only
__all__ = [
    'MEDIA_ROOT',
    'MEDIA_URL', 
    'STORAGES',
    'FILE_UPLOAD_MAX_MEMORY_SIZE',
    'DATA_UPLOAD_MAX_MEMORY_SIZE',
]