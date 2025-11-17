# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Frontend implementation with React and shadcn/ui
- Authentication system enhancements
- Production Docker configuration
- CI/CD pipeline setup

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