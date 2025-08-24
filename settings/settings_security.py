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
Security-related Django settings including CORS, CSRF, Sessions, and Host configuration
"""

import os

# --------------------------------------------------------------------------------------------------
#  Configuration
# --------------------------------------------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "False") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT")

# --------------------------------------------------------------------------------------------------
#  Setting Construction
# --------------------------------------------------------------------------------------------------

# Host settings
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")
if os.getenv("EC2_IP"):
    ALLOWED_HOSTS.append(os.getenv("EC2_IP"))

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS").split(",") if ENVIRONMENT == "production" else ["http://localhost:3000", "http://127.0.0.1:3000"]

# CSRF settings
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_DOMAIN = None if DEBUG else ".fyn-tech.com"
CSRF_COOKIE_PATH = "/"
CSRF_USE_SESSIONS = False
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(",") if ENVIRONMENT == "production" else ["http://localhost:3000", "http://127.0.0.1:3000"]

# Session settings
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_DOMAIN = None if DEBUG else ".fyn-tech.com"
SESSION_COOKIE_PATH = "/"
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Export settings only
__all__ = [
    'ALLOWED_HOSTS',
    'CORS_ALLOW_ALL_ORIGINS',
    'CORS_ALLOW_CREDENTIALS', 
    'CORS_ALLOWED_ORIGINS',
    'CSRF_COOKIE_SAMESITE',
    'CSRF_COOKIE_SECURE',
    'CSRF_COOKIE_DOMAIN',
    'CSRF_COOKIE_PATH',
    'CSRF_USE_SESSIONS',
    'CSRF_TRUSTED_ORIGINS',
    'SESSION_COOKIE_SAMESITE',
    'SESSION_COOKIE_SECURE',
    'SESSION_COOKIE_DOMAIN',
    'SESSION_COOKIE_PATH',
    'SESSION_ENGINE',
    'AUTH_PASSWORD_VALIDATORS',
]