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


# --------------------------------------------------------------------------------------------------
#  Configuration
# --------------------------------------------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "False") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT")

SERVER_CONFIG = [
        {
            "url": "http://api.fyn-tech.com:8000", 
            "description": "Production API"
        } ,
    ] if ENVIRONMENT == "production" else [
        {
            "url": "http://localhost:8000", 
            "description": "Development API"
        } ,
    ]

# --------------------------------------------------------------------------------------------------
#  Setting Construction
# --------------------------------------------------------------------------------------------------

# Schema Generation
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "runner_manager.authentication.RunnerTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
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

# Export settings only.
__all__ = ['REST_FRAMEWORK', 'SPECTACULAR_SETTINGS']