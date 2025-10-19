# Fyn-API Project Overview

## Project Summary

Fyn-API is a Django-based REST API server that provides a distributed computing platform for managing and executing computational jobs across multiple remote runners. The system enables users to submit jobs, manage application registries, and coordinate distributed execution through authenticated runners.

## Architecture Overview

### Core Components

The system is organized into four main Django applications:

1. **accounts** - User authentication and management
2. **application_registry** - Application/program repository management  
3. **job_manager** - Job lifecycle and resource management
4. **runner_manager** - Remote runner coordination and authentication

### Technology Stack

- **Framework**: Django 5.0.1 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Token-based authentication for runners, session auth for users
- **API Documentation**: OpenAPI 3.0 via DRF Spectacular
- **WebSockets**: Django Channels for real-time communication
- **File Storage**: Local filesystem storage
- **Deployment**: Gunicorn + Daphne for WSGI/ASGI

## Application Details

### 1. Application Registry (`application_registry`)

**Purpose**: Manages a repository of executable applications that can be deployed to runners.

**Key Models**:
- `AppInfo`: Stores application metadata (name, file path, type)
- `AppType`: Enumeration of supported application types (Python, Linux binary, etc.)

**API Endpoints**:
- `GET /application_registry/` - List available applications
- `GET /application_registry/{id}/program/` - Download application binary/source

**Features**:
- Support for multiple application types (Python scripts, binaries, shell scripts)
- Automatic content-type detection
- Secure file serving with proper headers

### 2. Job Manager (`job_manager`)

**Purpose**: Handles job lifecycle management, resource allocation, and result collection.

**Key Models**:
- `JobInfo`: Core job metadata and status tracking
- `JobResource`: File resources associated with jobs (inputs/outputs)
- `JobStatus`: Comprehensive job state enumeration

**API Endpoints**:

**User APIs**:
- `GET/POST /job_manager/users/` - Manage jobs for authenticated users
- `GET/POST /job_manager/resources/users/` - Manage job resources

**Runner APIs**:
- `GET/PATCH /job_manager/runner/` - Access assigned jobs (runners only)
- `GET/POST /job_manager/resources/runner/` - Manage job resources (runners only)
- `GET /job_manager/resources/runner/{id}/download/` - Download resource files

**Features**:
- Comprehensive job status tracking (queued → running → completed/failed)
- File upload/download for job inputs and outputs
- Runner-specific job assignment and permissions
- Detailed resource management with original file path tracking

### 3. Runner Manager (`runner_manager`)

**Purpose**: Manages remote computational runners and their authentication/authorization.

**Key Models**:
- `RunnerInfo`: Runner metadata and authentication tokens
- `SystemInfo`: Hardware/system information from runners
- `RunnerStatus`: Runner state enumeration (idle, busy, offline, etc.)

**API Endpoints**:

**User APIs**:
- `GET/POST /runner_manager/users/` - Manage owned runners
- `POST /runner_manager/add_new_runner/` - Create new runner
- `DELETE /runner_manager/delete_runner/` - Remove runner
- `GET /runner_manager/get_status/` - Check runner status

**Runner APIs**:
- `GET/PATCH /runner_manager/runner/` - Self-management for authenticated runners
- `POST /runner_manager/register/{runner_id}` - Initial runner registration
- `PUT /runner_manager/update_system/{runner_id}` - Update system information
- `PATCH /runner_manager/report_status/{runner_id}` - Status heartbeat

**Features**:
- Token-based runner authentication with automatic token rotation
- System information collection and reporting
- Runner state management and heartbeat monitoring
- Owner-based access control (users can only manage their own runners)

### 4. Accounts (`accounts`)

**Purpose**: User authentication and account management.

**Features**:
- Custom user model with UUID primary keys
- Integration with Django's authentication system
- User-owned runner relationships

## Security Features

### Authentication & Authorization

- **Users**: Session-based authentication for web interface
- **Runners**: Custom token authentication (`RunnerTokenAuthentication`)
- **Permissions**: Fine-grained permissions ensuring users/runners can only access their own resources

### Security Headers & Configuration

- CORS configuration for cross-origin requests
- CSRF protection with configurable cookie settings
- Secure session handling for production environments
- Domain-specific security settings based on environment

### Data Protection

- Runners can only access jobs assigned to them
- Users can only manage their own runners and jobs
- Automatic token rotation on runner registration
- Protected file serving with proper content-type detection

## Configuration Management

### Environment-Based Settings

The project uses a modular settings structure:

- `settings/settings.py` - Core Django settings
- `settings/settings_rest.py` - REST Framework and OpenAPI configuration
- `settings/settings_security.py` - CORS, CSRF, and security settings
- `settings/settings_storage.py` - File storage configuration

### Environment Support

- **Development**: SQLite database, debug mode, localhost CORS
- **Production**: PostgreSQL database, secure cookies, production domains

## API Documentation

The project provides comprehensive API documentation through DRF Spectacular:

- **Swagger UI**: `/schema/swagger-ui/`
- **ReDoc**: `/schema/redoc/`
- **OpenAPI Schema**: `/schema/`

Features include:
- Automatic schema generation from Django models and serializers
- Custom endpoint documentation with parameters and responses
- Authentication examples and retry configuration
- Environment-specific server configurations

## Deployment Considerations

### Development
- Uses SQLite for simplicity
- Debug mode enabled
- Local file storage
- Localhost CORS allowance

### Production
- PostgreSQL database via environment variables
- Secure cookie settings
- Production domain CORS configuration
- File upload limits (50MB)

## Future Development Areas

The codebase includes several placeholder functions marked as "WIP" (Work In Progress):
- `request_new_job()` - Additional job request functionality
- `get_jobs()` - Enhanced job querying
- `start_job()` - Job execution triggers
- `terminate_job()` - Job termination handling

These represent areas for future feature development as the platform evolves.