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
Django REST Framework and DRF Spectacular settings
"""

import os
from datetime import timedelta


# --------------------------------------------------------------------------------------------------
#  Configuration
# --------------------------------------------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "False") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT")
API_ENVIRONMENT = os.getenv("API_ENVIRONMENT")


SERVER_CONFIG = (
    [
        {"url": "https://api.fyn-tech.com", "description": "Production API"},
    ]
    if ENVIRONMENT == "production" or API_ENVIRONMENT == "production"
    else [
        {"url": "http://localhost:8000", "description": "Development API"},
    ]
)

# --------------------------------------------------------------------------------------------------
#  Setting Construction
# --------------------------------------------------------------------------------------------------

# Schema Generation
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "runner_manager.authentication.RunnerTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Fyn-Tech API",
    "DESCRIPTION": "Schema for the REST API of fyn-api",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVERS": SERVER_CONFIG,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
    "TAGS": [
        {"name": "Simulation", "description": "Simulation operations"},
    ],
    "EXTENSIONS_TO_SCHEMA_FUNCTION": lambda generator, request, public: {
        "x-speakeasy-retries": {
            "strategy": "backoff",
            "backoff": {
                "initialInterval": 500,
                "maxInterval": 60000,
                "maxElapsedTime": 3600000,
                "exponent": 1.5,
            },
            "statusCodes": ["5XX"],
            "retryConnectionErrors": True,
        }
    },
}

# JWT Settings
# Note: SECRET_KEY will be set from main settings after import
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("SECRET_KEY"),  # Get directly from environment
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Export settings only.
__all__ = ["REST_FRAMEWORK", "SPECTACULAR_SETTINGS", "SIMPLE_JWT"]
