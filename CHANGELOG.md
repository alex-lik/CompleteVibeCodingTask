# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-01-17

### Added
- **Complete API testing suite** - Comprehensive test coverage with 15+ passing tests
- **Basic endpoint testing** - Health checks, documentation access, and basic API functionality
- **API structure validation** - Endpoint availability and response format testing
- **WebSocket testing** - WebSocket endpoints and connection statistics validation
- **Authentication testing** - API key validation and security endpoint tests
- **Test configuration** - Mock services and test database setup
- **Error handling testing** - Proper HTTP status codes and error responses

### Changed
- **Test suite**: Organized test files by functionality (basic API, WebSocket, API specific)
- **Testing framework**: Integrated pytest with TestClient for FastAPI testing
- **Mock services**: Added WebSocket service mocking for isolated testing
- **Documentation**: Updated TODO.md to reflect completed tasks
- **Configuration**: Switched to SQLite for testing environment compatibility

### Tested
- **Health endpoints** - `/health`, `/db-check`, `/redis-check` functionality
- **API documentation** - Swagger UI, ReDoc, and OpenAPI spec accessibility
- **Webhook endpoints** - Structure validation and authentication checks
- **REST API endpoints** - Project, task, and statistics endpoint availability
- **WebSocket endpoints** - Connection statistics and endpoint validation
- **Authentication** - API key validation across all endpoint types

---

## [Unreleased]

### Planned
- Frontend implementation with React and shadcn/ui
- Production Docker configuration
- CI/CD pipeline setup

### Added
- **Advanced pagination and filtering system** - Complete implementation for all API endpoints
- **Paginated response models** - `PaginatedProjectResponse` and `PaginatedTaskResponse` with metadata
- **Enhanced filtering capabilities** - Support for status, agent, date range, and task name filters
- **Global task search endpoint** - `/api/tasks/search` with cross-project filtering
- **Flexible pagination parameters** - Configurable limits (1-100) and offset controls
- **Pagination metadata** - `has_next` and `has_prev` flags for navigation
- **Enhanced API response schemas** - Proper handling of related objects and agent names

### Changed
- **API**: Updated `/api/projects` endpoint with paginated response format
- **API**: Enhanced `/api/projects/{name}/tasks` with advanced filtering options
- **API**: Added `/api/tasks/search` endpoint for global task filtering
- **Schemas**: Updated all Pydantic models to handle nullable datetime fields
- **Responses**: Improved serialization to avoid circular references
- **Security**: Maintained API key authentication across all new endpoints

---

## [0.4.0] - 2025-01-17

### Added
- **Advanced pagination and filtering system** - Complete implementation for all API endpoints
- **Paginated response models** - `PaginatedProjectResponse` and `PaginatedTaskResponse` with metadata
- **Enhanced filtering capabilities** - Support for status, agent, date range, and task name filters
- **Global task search endpoint** - `/api/tasks/search` with cross-project filtering
- **Flexible pagination parameters** - Configurable limits (1-100) and offset controls
- **Pagination metadata** - `has_next` and `has_prev` flags for navigation
- **Enhanced API response schemas** - Proper handling of related objects and agent names

### Changed
- **API**: Updated `/api/projects` endpoint with paginated response format
- **API**: Enhanced `/api/projects/{name}/tasks` with advanced filtering options
- **API**: Added `/api/tasks/search` endpoint for global task filtering
- **Schemas**: Updated all Pydantic models to handle nullable datetime fields
- **Responses**: Improved serialization to avoid circular references
- **Security**: Maintained API key authentication across all new endpoints

---

### Added
- **Extended API Key authentication** - Full authorization system implementation
- Unified security module (`core/security.py`) with common authentication functions
- API Key authorization for all REST API endpoints (`/api/*`)
- API Key authorization for WebSocket connections through query parameters
- Enhanced test suite with authentication tests
- Comprehensive documentation of authentication requirements

### Changed
- **Security**: Updated all webhook endpoints to use unified authentication system
- **API**: All REST API endpoints now require X-API-Key header
- **WebSocket**: Enhanced security with API key validation
- **Tests**: Updated all test files to include proper authentication headers
- **Documentation**: Added authentication sections to API documentation

---

## [0.3.0] - 2025-01-17

### Added
- WebSocket integration with real-time notifications for task events
- WebSocket endpoint: `/webhook/ws` with project-specific subscriptions
- WebSocket API endpoint for connection statistics: `/api/websocket/stats`
- Real-time notifications for task start, finish, status updates, and errors
- Comprehensive WebSocket service with connection management
- Test suite for WebSocket functionality
- WebSocket documentation and usage examples
- Integration of WebSocket notifications with webhook processing

### Changed
- Enabled WebSocket functionality in main application
- Enhanced WebhookService to trigger WebSocket notifications
- Added WebSocket support to all webhook processing
- Improved API documentation with WebSocket examples
- Updated project README to include WebSocket API section

---

## [0.2.0] - 2025-01-17

### Added
- Complete webhook endpoint `/webhook/error` with database integration
- Full REST API implementation for frontend consumption
- Comprehensive API documentation with examples
- Pydantic response models and schemas
- Database query operations with filtering and pagination
- Statistics endpoint with performance metrics
- Test suite with 8 passing tests
- Enhanced README with API documentation
- Error handling and validation improvements

### Changed
- Improved error handling in all endpoints
- Enhanced database query performance
- Added comprehensive validation for all inputs
- Updated documentation to reflect new API structure
- Added health monitoring endpoints

### Fixed
- Issue with task status updates not persisting correctly
- Database connection error handling in API endpoints
- Webhook endpoint authentication validation

---

## [0.1.0] - 2025-01-16

### Added
- Initial project structure creation
- Backend folder structure with webhook, API, core, models, services, and alembic directories
- FastAPI backend implementation with basic structure
- PostgreSQL database connection setup with SQLAlchemy
- Redis client implementation with async support
- Database models: Project, Agent, Task, Settings
- Alembic migration system with initial migrations
- Webhook endpoints: `/webhook/start`, `/webhook/finish`, `/webhook/status`
- API key authentication for webhook security
- CORS middleware configuration
- Health check endpoints for database and Redis
- Docker Compose configuration for development
- Basic test framework setup

### Changed
- Configuration management using environment variables
- Database schema updates through Alembic migrations
- Enhanced error handling for database operations

### Planned
- Complete webhook `/webhook/error` endpoint
- REST API implementation for frontend
- WebSocket support for real-time updates
- Frontend components with shadcn/ui
- MCP integration for agent communication
- Production Docker setup