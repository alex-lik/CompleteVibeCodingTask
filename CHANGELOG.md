# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure creation
- Backend folder structure with webhook, API, MCP, models, and Alembic directories
- Frontend folder structure with React/TypeScript setup
- Infrastructure configuration with Docker Compose
- Environment configuration templates
- Package configurations for both backend and frontend
- FastAPI backend implementation with basic structure
- Configuration management with environment variables
- Basic API endpoints for health check and root
- CORS middleware configuration
- Pydantic schemas for webhook data models
- Webhook route structure with authentication
- API route structure for projects and tasks
- Virtual environment setup and dependency installation
- Development environment configuration
- PostgreSQL database connection setup
- SQLAlchemy models for Project, Agent, and Task entities
- Alembic migration system configuration
- Database initialization with automatic table creation
- Database connection health check endpoint
- PostgreSQL and Redis Docker containers setup
- Redis client implementation with async support
- Redis connection endpoint with health check
- Integration of Redis into application lifecycle
- Settings model implementation for key-value configuration storage
- Alembic migration for settings table with proper indexes
- Database schema update with settings table creation
- WebhookService implementation for handling webhook data processing
- Database operations for creating/updating projects, agents, and tasks
- PostgreSQL integration with webhook start endpoint functionality
- WebSocket service implementation for real-time notifications (created)
- Complete webhook endpoint `/webhook/start` with database persistence
- API key authentication for webhook security
- Task status management with automatic timestamp tracking
- Project and agent auto-creation when receiving webhook data
- Complete webhook endpoint `/webhook/finish` with database integration
- Task completion tracking with result storage and duration calculation
- Automatic status updates from 'running' to 'completed' state
- Complete webhook endpoint `/webhook/status` with database integration
- Task status tracking with progress updates and custom messages
- Support for real-time status changes during task execution
- Enhanced error handling for non-existent task IDs

### Changed
- Updated project documentation to reflect new structure
- Modified port configuration to avoid conflicts (8001 instead of 8000)
- Simplified configuration approach using os.getenv instead of pydantic-settings

### Planned
- Database models and migrations
- WebSocket support for real-time updates
- Frontend components with shadcn/ui
- MCP integration for agent communication
- Docker production setup